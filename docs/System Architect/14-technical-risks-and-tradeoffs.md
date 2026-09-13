# 14. Rủi ro kỹ thuật và đánh đổi

## Sổ rủi ro

Mức độ là đánh giá thiết kế ban đầu theo tác động, chưa có xác suất đo từ vận hành. Owner là vai trò được đề xuất; cần gán người thật trước pilot. Residual risk phải được owner theo dõi, không tự coi đã xử lý chỉ vì có kiểm soát trong tài liệu.

| ID / mức | Rủi ro và tín hiệu phát hiện | Giảm thiểu / kiểm chứng | Owner / liên kết |
| --- | --- | --- | --- |
| R-01 / cao | BA và code khác phạm vi; portal thiếu nhưng bị gọi MVP hoàn chỉnh | ADR baseline; trace 22 FR; guard chống auto final; nghiệm thu toàn vòng | Product/Risk; ADR-001/004 |
| R-02 / cao | Dữ liệu sai chủ, GPS thiếu/giả, version conflict | Source contract, quality/quarantine, watermark, evidence refutation; UAT-01–05 | Data; 05–06 |
| R-03 / cao | Rule score bị hiểu là probability hoặc chứng cứ đủ kết luận | DTO/UX tách trường, unknown rõ, checklist và người độc lập; UAT-15 | Risk; ADR-004/011 |
| R-04 / cao | Lộ case người khác qua list/count/snippet/tệp/export | Scope trước query, publication riêng, auth epoch và file gateway; UAT-19/21 | Security; ADR-009 |
| R-05 / cao | Nguồn bị sửa, mất object, hash/metadata bị thay đồng thời | Snapshot/version, signed manifest, quyền tách biệt, restore inventory; UAT-10/28 | Data/Security; ADR-006 |
| R-06 / cao | Case trùng sau đổi model/rule, hoặc merge hai sự việc khác | Incident anchors, snapshot ID riêng, merge proposal; đo case/incident ratio; UAT-06 | Risk/Backend; ADR-005 |
| R-07 / cao | Phản hồi sát lúc duyệt bị bỏ hoặc có hai decision hiện hành | Case/information version, khóa ngắn, receipt và append decision/pointer nguyên tử; UAT-16 | Backend; ADR-007 |
| R-08 / cao | Job/event retry gửi lặp hay worker hết lease ghi muộn | Inbox/idempotency/unique keys, fencing, provider reconciliation; fault injection | Backend/Operations; ADR-003 |
| R-09 / cao | Nhầm sent/delivered làm hết hạn tài xế trước khi biết sự việc | Hợp đồng delivery, due null, fallback hỗ trợ và gia hạn; UAT-14 | Product/Operations; 06–07 |
| R-10 / cao | Restore DB nhưng thiếu tệp/receipt hoặc tái lộ dữ liệu đã xóa | DR ledger độc lập, PITR + object version + deletion/hold replay; UAT-24/28 | Operations/Data; ADR-010/013 |
| R-11 / cao | Không đủ người duyệt/appeal độc lập, queue vượt năng lực | Capacity người, phân công độc lập, block/escalate; không tự bỏ guard | Risk/Product; ADR-001/004 |
| R-12 / cao | Lạm dụng quyền quản trị/khẩn cấp, audit chưa tách quyền | DB/KMS/backup role separation, MFA, signed checkpoint, hậu kiểm | Security/Audit; 08 |
| R-13 / vừa | Full-memory loader hoặc query text làm DB quá tải | Window/chunk/partition/index, worker pool/connection budget; benchmark 18 triệu GPS | Backend/Data; ADR-002/008 |
| R-14 / vừa | Monolith mất boundary, nhiều module ghi lẫn nhau | Module ownership, UoW contract, CI import/contract checks, tách khi có số đo | Tech Lead; ADR-002 |
| R-15 / vừa | Search index stale, pagination lặp/mất, thu hồi quyền muộn | Snapshot session/auth epoch, current authority check, watermark/rebuild; UAT-08/19 | Backend; ADR-008/009 |
| R-16 / cao | Label leakage/selection bias, appeal đổi nhưng model học nhãn cũ | Sampling non-alert, temporal/entity split, label/dataset version, adjudication | Data/Risk; ADR-011 |
| R-17 / vừa | Drift hoặc model timeout tăng case/độ trễ | Shadow/canary, coverage/drift monitor, rule fallback, không auto activate | Data/Operations; 11 |
| R-18 / cao | Upload độc hại hoặc tệp bị đổi sau scan | Quarantine/version/hash, scanner sandbox, MIME/size, quyền tải; UAT-12 | Security; 08 |
| R-19 / vừa | Vendor lock-in hoặc TCO tăng do lưu/log/egress | Adapter, contract tính năng, retention phân lớp, cost/1.000 trips và budget | Architect/Operations; 02/09/10 |
| R-20 / cao | Migration gán dismissed thành not_fraud hoặc bịa verified actor | Giữ original/legacy/null, mapping report, backfill replay và UAT migration | Data/QA; ADR-014 |

## Đánh đổi được chấp nhận trong thiết kế đề xuất

| Lựa chọn | Lợi ích | Chi phí/giới hạn còn lại |
| --- | --- | --- |
| Modular monolith + worker | Tận dụng code, giao dịch core dễ kiểm, vận hành ít thành phần | Shared DB/release; cần kỷ luật module và capacity |
| Batch 5 phút / freshness 30 phút | Phù hợp điều tra sau chuyến, có replay rõ | Không ngăn gian lận đồng bộ trong quá trình đặt xe; yêu cầu đó cần kiến trúc khác |
| PostgreSQL jobs/outbox | Durable work và domain commit cùng DB, thay broker được | Phải xử lý vacuum/poll/leases; throughput log dài hạn có giới hạn |
| Human final decision | Căn cứ/phản hồi/độc lập rõ, phù hợp BA | Chi phí nhân sự, thời gian chờ, con người vẫn có thể sai |
| Object version + DB metadata | Tệp lớn rẻ hơn OLTP, source snapshot truy nguyên | Không có transaction nguyên tử qua hai kho; cần reconcile/backup đồng bộ về logic |
| Search PostgreSQL | Ít hạ tầng, scope SQL và query semantics dễ đối chiếu | Analyzer/ranking nâng cao hạn chế; cần benchmark tiếng Việt |
| HA một vùng + cold restore | Phù hợp SLO pilot và chi phí ban đầu | Có thể mất phần sau recovery point; thảm họa vùng cần restore nhiều giờ |
| Immutable history + governed purge | Lịch sử không bị chỉnh tùy tiện, có kiểm soát vòng đời | Retention/hold/WORM có thể xung đột; cần policy và báo trạng thái thực |

Các đánh đổi trên có thể thay đổi qua ADR. Không xem hạn chế kỹ thuật là lý do tự giảm quyền phản hồi hoặc che độ mới/độ tin cậy của kết quả.

## Quyết định còn cần xác nhận trước pilot

| Nội dung | Mặc định để tiếp tục thiết kế | Điều kiện cần biết trước vận hành |
| --- | --- | --- |
| Nguồn và định danh | Adapter batch có namespace/revision/quality | Chủ nguồn, contract ID/version/completeness, quyền sử dụng, cơ chế correction |
| Quy chế phản hồi/khiếu nại | Theo BA SLA và một vòng appeal thông thường; luồng đặc biệt có phân công | Lịch hiệu lực, delivery proof chấp nhận, người duyệt độc lập, mapping hủy quyết định |
| Cloud/IdP/kênh thông báo | Managed services đáp ứng contract, adapter thay được | Nền tảng sẵn có, region, hợp đồng, SLA provider, mapping tài xế |
| Retention/hold | Policy cấu hình; chưa purge dữ liệu thật theo số ngày tự suy | Inventory, mục đích, thời hạn từng lớp, authority cho hold/xóa/backup |
| Chất lượng và nguồn lực | Rule baseline, người đánh giá độc lập, report unknown | Sampling/cỡ mẫu, chi phí lỗi, năng lực điều tra/duyệt, mức dừng pilot |
| Khôi phục | RPO 15 phút, RTO 4 giờ theo BA | Chấp nhận recovery gap hay cần RPO=0; vùng dự phòng và khả năng replay content |

Các nội dung này không cản trở hoàn thiện tài liệu hoặc thử synthetic. Chúng là đầu vào triển khai thật, liên kết BA DEC-04/05/06 và cổng SA-G0/G4; không được suy approval từ việc người dùng chấp nhận bộ tài liệu.

## Điểm cần kiểm sau mỗi thay đổi lớn

Kiểm lại đường đi dữ liệu/quyền, danh sách authoritative writers, version compatibility, migration/rollback, retention/restore và metric chất lượng. Với đổi ML, thêm đánh giá leakage/calibration/case load; với đổi broker, thêm ordering/dedup/lease replay; với đổi storage/search, thêm hash/ACL/purge/restore parity.

Nếu số đo phủ định một giả định, cập nhật ADR và sizing công khai trong tài liệu. Không làm kiến trúc cố định theo tên công nghệ hoặc theo uy tín công ty tham khảo; căn cứ cuối cùng là nghiệp vụ, dữ liệu, kết quả đo và năng lực vận hành của dự án.
