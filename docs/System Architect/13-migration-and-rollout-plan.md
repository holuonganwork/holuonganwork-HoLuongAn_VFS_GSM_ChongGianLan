# 13. Migration và kế hoạch rollout

## Phạm vi bàn giao

SA 1.0 hoàn thành thiết kế và cơ sở chia backlog. Những bước sau là công việc implementation tương lai, chưa được thực hiện chỉ bởi việc viết tài liệu. Không coi tests prototype, dữ liệu seed hoặc sơ đồ là chứng nhận pilot.

Toàn bộ FR-01–FR-22 là Must của BA đích. Các giai đoạn nội bộ có thể phát hành để kiểm chứng nhưng không được gọi là hoàn thành MVP hợp tác hai bên khi còn thiếu portal, appeal, governance/lifecycle hoặc nhãn độc lập. ML thật, Kafka, search cluster và LLM là mở rộng sau đó theo ADR.

## Kế hoạch theo đầu ra và cổng kiểm chứng

Mã P0–P3 ở tài liệu 01 biểu diễn mức trưởng thành; các bước M0–M6 dưới đây là thứ tự thực hiện. Cổng SA dùng tên riêng để không lẫn với cổng G0/G1/G2 của [roadmap BA](../BA/15-mvp-roadmap-and-business-case.md).

| Bước | Đầu ra cụ thể | Phụ thuộc / owner | Cổng hoàn thành |
| --- | --- | --- | --- |
| M0 — chốt contract | Xác nhận BA DEC-01–06, actor/SoD, mapping appeal annul, inventory nguồn, IdP, retention/vùng dữ liệu, sizing và SLO | Product/Risk/Data/Security/Operations | `SA-G0`: các quyết định nghiệp vụ đủ cụ thể cho pilot, ADR được nhận trách nhiệm |
| M1 — nền tảng dữ liệu và quyền | Auth/session/DTO theo audience, org/public IDs, source revision/hash, object quarantine, audit/UoW/jobs/outbox, disable system final decision | Backend/Data/Security | `SA-G1`: kiểm quyền, ingest dedup, evidence integrity và transaction đạt trên PostgreSQL thật |
| M2 — điều tra nội bộ | Loader window/checkpoint, incident registry, queue/assignment, timeline/search, evidence support/refute, proposal/approval, compatibility đọc legacy | M1; Backend/Frontend/Risk | `SA-G2`: shadow đúng expected sets, race/version pass, không gửi notification live |
| M3 — hợp tác và kết quả | Portal mobile, drafts/receipt/upload, publication/delivery/SLA, response, result/handoff, appeal và xem xét đặc biệt | M1/M2; Product/Frontend/Backend | `SA-G3`: UAT hai bên/quyền tệp/độc lập/deadline race pass; chưa mở cohort thật trước G4 |
| M4 — vận hành và governance | Rule release approval/rollback, reports/label sampling, retention/hold/export, observability/runbook/backup/restore, load/UX UAT | Các nền tảng làm từ M1; Data/Operations/QA | `SA-G4`: đủ 22 FR/12 NFR, security/data gates, DR và quyết định mở pilot được ghi nhận |
| M5 — pilot có kiểm soát | Cohort được xác nhận, hỗ trợ người dùng, lịch xét hàng ngày, báo số đo/ngoại lệ và rollback | SA-G4; Product/Operations/Risk | `SA-G5`: đối chiếu kết quả với BA, quyết định mở rộng/chỉnh/dừng có owner |
| M6 — tăng trưởng có căn cứ | ML shadow hoặc broker/search/service split theo trigger | SA-G5 và ADR tương ứng | Contract parity, benchmark, canary và on-call của thành phần mới |

Không đặt deadline theo tuần khi chưa biết nhân sự/nguồn tích hợp. Mỗi bước cần người backend, frontend, data, QA và hỗ trợ security/operations theo mức độ; lập ước lượng sau phân rã đầu ra. Các kiểm soát nền tảng làm sớm xuyên suốt, không để tới M4 mới phát hiện cần audit/retention.

## Migration schema và dữ liệu hiện có

| Hiện có | Đích / cách chuyển | Kiểm tra bắt buộc |
| --- | --- | --- |
| `drivers.id` bigint, `external_driver_id` | Giữ PK; thêm org/public ID, source namespace; identity binding qua nguồn xác minh | FK không đổi; không tự gắn người dùng theo chuỗi tên |
| `trips`, `gps_events`, `devices`, `driver_devices`, `promotions` | Thêm revision registry/capture; partition GPS qua bảng mới/copy chunk có đối soát | Count/hash/ownership/time/key đúng; phiên bản thu nhận mới không giả là lịch sử nguồn từng có |
| `fraud_alerts`, `decision_results` | Giữ read legacy, thêm run/incident/revision links | Không thay probability unknown hoặc đổi kết quả auto legacy |
| `fraud_cases.alert_id` unique | Bổ sung `case_alerts` và incident links; backfill một link từ dữ liệu có thật | Cho phép nhiều alert revisions/case; không tạo incident chắc chắn từ chỉ driver ID |
| `fraud_evidences`, `evidence_sources` | Tạo evidence version từ nội dung hiện có, ghi thời điểm capture hiện tại, `legacy_unverified` khi thiếu căn cứ | FK/source không mất; hash mới chứng minh bản mới thu nhận, không chứng minh nguyên bản quá khứ |
| `driver_explanations` | Giữ read history, liên kết legacy response với provenance | Không tạo request/delivered_at/identity verification không từng tồn tại |
| `case_decisions` unique case | Giữ nguyên bảng lịch sử, thêm `decision_versions`/current pointer và mapping provenance | Không bỏ unique cũ rồi sửa tại chỗ; pointer thuộc case, một bản hiện hành |
| `case_status_events` | Giữ event cũ, gắn legacy actor representation | Actor type `human` từ default migration không chứng minh user đã xác thực |

Giá trị mới thêm qua expand migration; migration không import application model động. Backfill chia chunk, checkpoint, idempotent và checksum trước/sau. Ghi `migration_batch_id`, nguồn mapping và ngoại lệ; chạy lại không tạo bản capture/decision lặp.

## Mapping trạng thái và kết luận

| Giá trị cũ | Mapping đề xuất | Ghi chú bảo toàn sự thật |
| --- | --- | --- |
| `detected` | `case_status=new`, `resolution=null` | Triage lại, không tự có owner |
| `under_review` | `investigating`, `resolution=null` | Reviewer chuỗi cũ chỉ là provenance; phân công người đã xác thực |
| `awaiting_driver_explanation` | `investigating`, `block_reason=legacy_delivery_unverified` | Không suy hạn đã chạy; xét phát hành request mới |
| `driver_responded` | `investigating`, response lịch sử đính kèm | Không gán authenticated receipt mới cho lịch sử |
| `confirmed_fraud` | `resolved`, `resolution=confirmed_fraud`, decision legacy | Gắn `legacy_unverified` hoặc `legacy_system`; không làm nhãn vàng và không tự phát hành ra portal |
| `dismissed` | `resolved`, `resolution=null`, `legacy_resolution=dismissed`, mapping status pending | Xét lý do để phân loại; không mặc định `not_fraud` |

Ngoại lệ null resolution chỉ cho bản migration legacy có provenance, không cho quyết định mới. Sau thẩm định, nếu cần kết luận theo quy trình mới thì tạo decision version mới với actor/căn cứ thật, giữ bản cũ. Case resolved legacy chưa mapping vẫn đọc được ở giao diện nội bộ và báo cáo phân nhóm riêng.

## Cutover và một writer

1. Chụp baseline dữ liệu/schema/config, backup và danh sách client/worker đang ghi. Xác định cohort routing trong DB, không chỉ frontend flag.
2. Expand schema và deploy code đọc cả hai; client hiện hành tiếp tục local/internal theo scope, chặn truy cập chia sẻ khi chưa auth.
3. Backfill/dual-read kiểm parity; shadow detection ghi riêng, không tạo publication/notification/decision live.
4. Dừng scheduler/old writers cho cohort, đợi transaction/lease hết, ghi source cutoff và quyền sở hữu writer. Phần đuôi sau cutoff được ingest/replay theo contract, không bỏ khoảng trống.
5. Bật writer mới và đối soát source→alert→case→decision/receipt. Adapter API cũ chỉ được đọc legacy hoặc chuyển qua command mới có đầy đủ quyền; endpoint `/decision` cũ không được vượt guard phê duyệt mới.
6. Mở cohort theo cấu hình, theo dõi sample hồ sơ/notification/receipt. Có thể bắt đầu 5%, 25%, 100% khi cohort đủ lớn; tỷ lệ là gợi ý, số thực và thời gian quan sát do Product/Risk quyết định.
7. Contract schema cũ chỉ sau mọi client/worker đã chuyển, lịch sử đọc được, backup/restore kiểm xong. Không xóa dữ liệu chỉ vì migration đã thành công.

Không chạy hai authoritative writers trên cùng case. Nếu cần dual write để chuyển kho, thực hiện qua transaction/outbox hoặc CDC có đối soát và đúng một nguồn sự thật; không ghép hai HTTP calls rồi hy vọng cả hai thành công.

## Bộ kiểm chứng bắt buộc

| Nhóm | Ca kiểm có ý nghĩa | Đầu ra |
| --- | --- | --- |
| Migration | DB rỗng + lịch sử `0001/0002`; đủ enum/actor/legacy/null; backfill retry/interruption | Báo count/FK/hash/mapping exceptions và khả năng đọc sau nâng cấp |
| Auth | Sai chủ/đơn vị/role/audience, thu hồi giữa search/export/download, tự duyệt | UAT-19/21 + NFR-01/02; không leak metadata |
| Ingest/detection | Duplicate/version conflict/late/correction, đủ lookback, hai incident cùng driver, policy đổi | UAT-01–06/23, run coverage và expected evidence sets |
| Atomicity | Mất mạng sau commit, hai approver, stale lease, replay outbox, response sát deadline/approve | UAT-06/13/16, không mất audit hoặc nhân đôi tác động |
| Evidence/files | Thay byte, MIME giả, scan timeout, object unavailable, redaction/export | UAT-10/12/21, không preview bản cách ly |
| Collaboration | Delivery sent/delivered/read, retry/gia hạn, late response, appeal độc lập/handoff correction | UAT-11–18/26 |
| Search/UX | Không dấu, query AND/OR, stable pages, quyền đổi; mobile 2 Mbps/200 ms, bàn phím/200% zoom | UAT-08/09/13/27; 8/10 người dùng hoàn thành tác vụ ≤5 phút theo NFR-08 |
| Quality/governance | KPI mẫu số, pending/legacy labels, independent sampling, rule rollback, hold/delete | UAT-20/22–25 |
| Reliability | Tải P1, backup/object missing, receipt replay, deletion ledger sau restore | UAT-27/28 + SLO thực đo |

Tất cả UAT-01–28 cần có build/data version/executor/evidence/accepted by khi triển khai. Backend tests hiện có tiếp tục regression; frontend cần thêm test thao tác ghi/quyền vì hiện chủ yếu đọc. Không dùng SQLite để chứng minh row locking, RLS, JSONB, partition hoặc concurrency PostgreSQL.

## Tiêu chí dừng và rollback

Dừng mở cohort khi có leak quyền, hash/audit sai, tự kết luận ngoài policy, nhận phản hồi không bền vững, duplicate decision, mapping mất lịch sử hoặc restore chưa đạt. Vi phạm latency/backlog được đánh giá theo SLO và capacity; không dùng thay ngưỡng sau bài đo để tuyên bố pass.

Rollback dừng producer mới/notification mới theo cohort, giữ API nhận/xem phản hồi và luồng case đã phát sinh bằng release tương thích. Replay inbox/outbox giữ khóa; kiểm provider status để không gửi lặp. Rule/model rollback đổi release cho run mới; quyết định/publication đã phát hành chỉ thay bằng quy trình correction/version, không sửa DB trực tiếp.

Kết thúc mỗi đợt cập nhật [ma trận truy vết](requirements-traceability.csv), runbook, ADR trạng thái, baseline config và bằng chứng UAT. Trong SA 1.0 cột trạng thái vẫn là thiết kế đề xuất/chưa thực thi.
