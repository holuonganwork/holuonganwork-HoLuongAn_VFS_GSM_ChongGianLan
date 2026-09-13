# 12. Sổ quyết định kiến trúc

Tất cả ADR dưới đây có trạng thái **proposed**, ngày 14/09/2026, thuộc SA 1.0. Đây là lựa chọn cụ thể để triển khai sau thẩm định, chưa được gán người phê duyệt thực tế. Owner là vai trò chịu trách nhiệm xem xét; khi chấp nhận cần ghi tên/ngày/bằng chứng. Không sửa nghĩa ADR cũ: tạo ADR mới, liên kết `supersedes`, cập nhật trạng thái cũ `superseded`.

## ADR-001 — Baseline hợp tác hai bên

**Bối cảnh:** BA 1.0 đưa lại tài xế, giải trình, duyệt độc lập và khiếu nại; prototype/new_architecture còn theo luồng nội bộ. **Quyết định:** dùng BA làm nghiệp vụ đích; P1 có portal tài xế, publication riêng và human final decision. Liên kết BA DEC-01/02/03.

**Phương án khác:** giữ internal AI-first hoàn toàn sẽ giảm chức năng nhưng không đáp ứng BA. **Đánh đổi:** cần identity/delivery/appeal và người độc lập, thời gian triển khai lớn hơn. **Xem lại:** khi chủ sản phẩm đổi phạm vi hoặc quy chế, phải sửa FR/UAT và migration cho nghĩa vụ đã phát sinh. **Owner:** Product + Risk + Architect.

## ADR-002 — Modular monolith Python với worker độc lập

**Bối cảnh:** có FastAPI/rule/ORM/test dùng được; chưa có số đo cần dịch vụ phân tán. **Quyết định:** giữ codebase Python, module ownership và API/worker entrypoint riêng, transaction core cùng PostgreSQL.

**Phương án khác:** Java core + Python detection hoặc microservices toàn phần. **Đánh đổi:** monolith chia sẻ release/DB và có nguy cơ truy cập chéo module; enforce boundary qua code review/import/contract checks. **Xem lại:** nhóm sở hữu và release độc lập, CPU/DB contention hoặc tiêu chuẩn doanh nghiệp chứng minh lợi ích tách. **Owner:** Tech Lead/Architect. Xem [04](04-containers-and-components.md).

## ADR-003 — PostgreSQL jobs/outbox trước broker

**Bối cảnh:** cần tác vụ bền vững, retry và notification sau commit; tải pilot chưa lớn. **Quyết định:** jobs có lease/fencing, outbox/inbox và consumer delivery riêng; at-least-once có idempotency.

**Phương án khác:** managed queue ngay từ đầu nếu doanh nghiệp đã có; Kafka khi cần log replay/fan-out; RabbitMQ khi chỉ cần routing công việc và đội đã vận hành. **Đánh đổi:** tăng tải/vacuum DB; phải giới hạn poll, retention và backlog. **Xem lại:** trigger tại tài liệu 10; không vận hành nhiều broker cùng mục đích. **Owner:** Backend/Operations. Nguyên tắc tham khảo: [AWS outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html).

## ADR-004 — Detection tách khỏi quyền kết luận

**Bối cảnh:** rule score không được hiệu chỉnh thành probability; code có nhánh auto fraud. **Quyết định:** P1 chỉ triage/priority tự động; command final decision bắt buộc human identity, độc lập, checklist và version.

**Phương án khác:** dùng ngưỡng cao để tự kết luận; không phù hợp baseline hiện tại. **Đánh đổi:** tốn năng lực điều tra/duyệt, cần quản trị queue. **Xem lại:** có thay đổi nghiệp vụ và bằng chứng chất lượng/calibration/contest được thẩm định; thay model đơn thuần không đủ. **Owner:** Risk/Product/Security. Xem [06](06-detection-and-decision-pipeline.md).

## ADR-005 — Incident ID độc lập alert fingerprint

**Bối cảnh:** fingerprint hiện chứa rule/model/policy; đổi config có thể tạo case mới cùng sự việc. **Quyết định:** incident registry có source anchors, alert revisions, case links, merge proposal có audit.

**Phương án khác:** một case/driver gây gộp sai; một case/fingerprint sinh trùng nghiệp vụ. **Đánh đổi:** correlation nhập nhằng cần người xét; episode/window có version. **Xem lại:** dữ liệu thật chứng minh correlation rule không đủ, xem graph/entity resolution nhưng giữ quyền theo case. **Owner:** Data/Risk. Xem [05](05-data-architecture.md), [06](06-detection-and-decision-pipeline.md).

## ADR-006 — PostgreSQL cho metadata, object storage cho artifact

**Bối cảnh:** evidence FK chưa đóng băng nguồn; cần tệp, bản che, source revisions và retention. **Quyết định:** source/evidence version append, SHA-256, signed manifest, object version; DB giữ quan hệ/hash/classification và current decision pointer.

**Phương án khác:** tất cả JSONB/BLOB trong DB hoặc chỉ URL nguồn đều không đáp ứng chi phí/tính nguyên vẹn dài hạn. **Đánh đổi:** cần đối soát hai kho, orphan cleanup và DR cùng version. **Xem lại:** yêu cầu WORM/hold, khối lượng và vị trí dữ liệu đổi; chọn storage dựa contract tính năng thực. **Owner:** Data/Operations/Security. Xem [05](05-data-architecture.md).

## ADR-007 — Workflow state hiện hành + lịch sử append

**Bối cảnh:** cần version quyết định, appeal và transaction dễ kiểm. **Quyết định:** relational state machine, optimistic version + khóa row ngắn, audit/outbox nguyên tử; một current decision pointer. Appeal riêng, bản cũ giữ nguyên.

**Phương án khác:** event sourcing toàn phần hoặc workflow engine ngay P1. **Đánh đổi:** phải viết transition/timer/reconciliation rõ; không có replay toàn hệ thống từ audit. **Xem lại:** nhiều workflow liên dịch vụ, timer/compensation phức tạp và đội có khả năng vận hành engine. **Owner:** Backend/Product. Xem [06](06-detection-and-decision-pipeline.md).

## ADR-008 — Search PostgreSQL trước search cluster

**Bối cảnh:** MVP cần exact ID, time filters, tiếng Việt không dấu, text có quyền; chưa cần OCR/ngữ nghĩa. **Quyết định:** authorized SQL, text projection theo audience, index phù hợp và search session ổn định.

**Phương án khác:** OpenSearch/Elasticsearch sớm, vector database sớm. **Đánh đổi:** tiếng Việt và snapshot nhiều kết quả cần benchmark; query/session cap rõ. **Xem lại:** SLO hoặc analyzer/features không đạt sau tuning; phải kiểm ACL/count/snippet/delete/reindex parity trước đổi. **Owner:** Backend/Data. Xem [05](05-data-architecture.md), [07](07-api-and-integration.md).

## ADR-009 — IdP và quyền theo đối tượng, publication riêng

**Bối cảnh:** caller tự khai reviewer, source endpoint có thể trả dữ liệu người khác. **Quyết định:** OIDC/BFF, MFA staff nhạy cảm; RBAC + org/assignment/ownership + field/workflow policy; file gateway và RLS phòng vệ.

**Phương án khác:** tự xây identity, API key người dùng hoặc chỉ ẩn UI. **Đánh đổi:** tăng phụ thuộc IdP và chi phí kiểm quyền ở query/export; không dùng raw signed download URL dài hạn. **Xem lại:** tích hợp app tài xế/IdP khác, nhiều đơn vị, SLO thu hồi thay đổi. **Owner:** Security/Identity. Xem [08](08-security-and-access-control.md).

## ADR-010 — HA một vùng, restore có đối soát

**Bối cảnh:** mục tiêu BA 99,5%, RPO 15 phút/RTO 4 giờ. **Quyết định:** hai failure domain, managed PostgreSQL HA, object version/backup, PITR, receipt/deletion ledger tách quyền và cold restore có kiểm.

**Phương án khác:** một VM đơn, hoặc multi-region active-active. **Đánh đổi:** chi phí HA/backup lớn hơn demo; vẫn có recovery gap và thời gian DR. **Xem lại:** cần RPO=0, SLO cao hơn hoặc vùng dữ liệu thay đổi; benchmark/diễn tập là căn cứ. **Owner:** Operations/Product. Xem [09](09-deployment-and-infrastructure.md), [10](10-performance-scalability-and-reliability.md).

## ADR-011 — Nhãn độc lập trước ML production

**Bối cảnh:** dữ liệu hiện là synthetic, thiếu nhãn thật/recall/calibration. **Quyết định:** rule baseline, cohort/sampling, label version/adjudication; model registry và shadow/canary khi đủ điều kiện.

**Phương án khác:** dùng system decision làm nhãn tự động hoặc mua model rồi coi probability là đúng. **Đánh đổi:** cần công sức gán nhãn và chờ nhãn trưởng thành. **Xem lại:** có nguồn nhãn đáng tin cậy và bài đo chi phí lỗi; vẫn giữ lineage và quyền contest. **Owner:** Risk/Data. Xem [11](11-observability-and-model-feedback.md).

## ADR-012 — OCR, graph và LLM là phần mở rộng

**Bối cảnh:** nhu cầu tìm bằng chứng có thể hưởng lợi từ công cụ nâng cao nhưng MVP chỉ cam kết text/metadata. **Quyết định:** thêm sau pilot khi có tác vụ cụ thể và thí nghiệm; output dẫn nguồn/version, người xét, quyền retrieval giữ nguyên.

**Phương án khác:** AI agent tự điều tra/kết luận end-to-end hoặc xây graph/vector từ đầu. **Đánh đổi:** P1 chưa tìm chữ trong ảnh/PDF hoặc tự khám phá quan hệ nhiều tầng. **Xem lại:** benchmark tác vụ chứng minh giảm thời gian với quality/chi phí đủ tốt. **Owner:** Product/Data/Security.

## ADR-013 — Vòng đời dữ liệu và hold có đối soát

**Bối cảnh:** xóa dữ liệu ảnh hưởng evidence chung, index, export, backup và mô hình. **Quyết định:** policy theo loại/mục đích, dependency graph, hold authority, deletion ledger độc lập, áp lại khi restore.

**Phương án khác:** TTL chung 30 ngày hoặc giữ mọi thứ vô hạn. **Đánh đổi:** tăng metadata/job vận hành; WORM/backup có thể trì hoãn purge, phải báo đúng trạng thái. **Xem lại:** quy chế lưu, căn cứ sử dụng hoặc khu vực dữ liệu đổi. **Owner:** Data/Security/đầu mối có thẩm quyền. Xem [05](05-data-architecture.md).

## ADR-014 — Migration tăng dần và cutover theo cohort

**Bối cảnh:** có legacy explanations, dismissed/confirmed cases và unverified actor strings. **Quyết định:** expand/backfill/shadow/switch/contract; một writer mỗi cohort; giữ giá trị gốc và nhãn legacy, không bịa metadata còn thiếu.

**Phương án khác:** sửa enum/đè quyết định cũ hoặc rewrite Big Bang. **Đánh đổi:** phải giữ compatibility adapter một thời gian và xử lý ngoại lệ mapping. **Xem lại:** sau khi mọi client/cohort chuyển, có thể contract schema cũ qua thay đổi được đánh giá riêng. **Owner:** Backend/Data/QA. Xem [13](13-migration-and-rollout-plan.md).

## Mẫu cho quyết định tiếp theo

```text
ID / tiêu đề / ngày / trạng thái / owner / người chấp nhận
Bối cảnh và yêu cầu FR/NFR bị ảnh hưởng
Số đo, giả định và phương án đã so sánh
Quyết định, ranh giới và giao diện thay đổi
Đánh đổi, rủi ro, chi phí vận hành
Migration, tương thích, rollback, kiểm chứng
Điều kiện xem lại; supersedes / superseded_by
```

Xem lại ADR khi vượt trigger, thay baseline nghiệp vụ, xảy ra incident nghiêm trọng, hoặc tối thiểu sau pilot. Công nghệ có thể thay; invariant về quyền, evidence, audit và quyết định cần được kiểm chứng lại trên lựa chọn mới.
