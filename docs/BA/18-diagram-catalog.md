# Danh mục sơ đồ UML và luồng dữ liệu

Phụ lục bổ sung cho baseline BA 1.0, mô tả **hệ thống đích phối hợp tài xế–kiểm soát**. Các sơ đồ không khẳng định prototype đã có những chức năng này. Quy trình, quyền và thuật ngữ tham chiếu tài liệu 03–10; không bổ sung chế tài tự động hoặc mở rộng phạm vi dữ liệu.

## Xem và chỉnh sửa

- Xem trực tiếp hình trong các tài liệu 19–23; mở liên kết SVG để phóng to mà chữ không bị vỡ.
- [Trang xem toàn bộ sơ đồ](diagrams/index.html) dùng được khi mở cục bộ bằng trình duyệt, không cần dịch vụ trực tuyến.
- Mỗi SVG có mã nguồn `.puml` tương ứng trong [thư mục nguồn](diagrams/src/). Mã nguồn là bản chuẩn; sau sửa phải xuất lại SVG bằng [hướng dẫn tái tạo](diagrams/README.md).
- Use Case, Activity, Sequence và Domain Class dùng ký pháp UML. DFD là sơ đồ luồng dữ liệu riêng, có quy ước hình tại tài liệu 23; không gọi DFD hoặc ERD là UML.

## Các sơ đồ bổ sung

| Mã | Sơ đồ | Tài liệu / bản SVG | Truy vết chính |
| --- | --- | --- | --- |
| UC-D01 | Use Case điều tra và phối hợp tài xế | [19 — Use Case](19-uml-use-case-diagrams.md), [SVG](diagrams/svg/uc-01-investigation.svg) | UC-01–07, UC-10; FR-01–14, FR-22 |
| UC-D02 | Use Case quản trị và cải tiến | [19 — Use Case](19-uml-use-case-diagrams.md), [SVG](diagrams/svg/uc-02-governance.svg) | UC-08, UC-09; FR-15–21 |
| ACT-D01 | Activity điều tra và duyệt kết luận | [20 — Activity](20-uml-activity-diagrams.md), [SVG](diagrams/svg/act-01-investigation.svg) | UC-02–06; RULE-07–12; UAT-07, UAT-15–17 |
| ACT-D02 | Activity yêu cầu và giải trình | [20 — Activity](20-uml-activity-diagrams.md), [SVG](diagrams/svg/act-02-explanation.svg) | UC-04, UC-05; FR-08–10; UAT-11–14 |
| ACT-D03 | Activity khiếu nại và khắc phục | [20 — Activity](20-uml-activity-diagrams.md), [SVG](diagrams/svg/act-03-appeal.svg) | UC-07; FR-14; UAT-18 |
| SEQ-D01 | Sequence tiếp nhận, phát hiện và chống trùng | [21 — Sequence](21-uml-sequence-diagrams.md), [SVG](diagrams/svg/seq-01-detection.svg) | FR-01–03; DR-01–05; UAT-01–06 |
| SEQ-D02 | Sequence phát hành và nhận giải trình | [21 — Sequence](21-uml-sequence-diagrams.md), [SVG](diagrams/svg/seq-02-explanation.svg) | FR-08–10, FR-15–16; UAT-11–14, UAT-19–20 |
| SEQ-D03 | Sequence đề xuất và duyệt độc lập | [21 — Sequence](21-uml-sequence-diagrams.md), [SVG](diagrams/svg/seq-03-decision.svg) | FR-11–13; RULE-08–12; UAT-15–17 |
| SEQ-D04 | Sequence khiếu nại và quyết định kế tiếp | [21 — Sequence](21-uml-sequence-diagrams.md), [SVG](diagrams/svg/seq-04-appeal.svg) | FR-14; DR-08; UAT-18 |
| CLS-D01 | Domain Class sự việc và bằng chứng | [22 — Domain Class](22-uml-domain-class-diagrams.md), [SVG](diagrams/svg/class-01-evidence.svg) | FR-01–07; DR-01–05; RULE-06–07 |
| CLS-D02 | Domain Class giải trình và quyết định | [22 — Domain Class](22-uml-domain-class-diagrams.md), [SVG](diagrams/svg/class-02-workflow.svg) | FR-08–16; DR-06–08 |
| DFD-D00 | DFD ngữ cảnh | [23 — DFD](23-data-flow-diagrams.md), [SVG](diagrams/svg/dfd-00-context.svg) | Ranh giới tại tài liệu 02; FR-01, FR-08–22 |
| DFD-D01 | DFD mức 1 | [23 — DFD](23-data-flow-diagrams.md), [SVG](diagrams/svg/dfd-01-system.svg) | FR-01–22; DR-01–10; phân rã chức năng chính |
| DFD-D02 | DFD mức 2 của tìm kiếm và kiểm chứng | [23 — DFD](23-data-flow-diagrams.md), [SVG](diagrams/svg/dfd-02-evidence-search.svg) | FR-04–07, FR-11, FR-15–17; UAT-07–10, UAT-19–21 |

Các dải ID trong bảng là phạm vi truy vết, không phải mã yêu cầu mới. Quan hệ chi tiết FR–BR–UAT vẫn quản lý tại [ma trận 12](12-requirements-traceability-matrix.md).

## Các sơ đồ đã có trong baseline

| Sơ đồ | Vị trí | Cách dùng cùng phụ lục |
| --- | --- | --- |
| Cây vấn đề | [01 — Bối cảnh](01-business-context-and-objectives.md) | Giải thích vì sao cần hệ thống |
| Bối cảnh hệ thống | [02 — Phạm vi](02-scope-and-boundaries.md) | Kiểm tra ranh giới tác nhân của Use Case và DFD |
| Luồng nghiệp vụ to-be | [04 — Quy trình](04-current-and-target-business-processes.md) | Tổng quan trước khi đọc Activity chi tiết |
| State Diagram hồ sơ | [04 — Quy trình](04-current-and-target-business-processes.md) | Quy định trạng thái; Activity/Sequence phải tuân thủ |
| ERD khái niệm | [10 — Dữ liệu](10-data-requirements-and-glossary.md) | Đối chiếu dữ liệu với Domain Class, không thay thế thiết kế bảng |

## Quy tắc đọc nhất quán

`case_status` là tiến độ công việc, `resolution` là kết luận. Hồ sơ vẫn `resolved` trong khi khiếu nại riêng ở `submitted/reviewing/decided/rejected`. Một kết luận chỉ có hiệu lực sau khi lưu thành công; thông tin mới chưa xét phải làm dừng phê duyệt trên phiên bản cũ. Không phản hồi không là thừa nhận, và cảnh báo không đồng nghĩa xác nhận gian lận.

Các thành phần trên Sequence/DFD là trách nhiệm logic, không yêu cầu microservices hay cơ sở dữ liệu riêng. Tất cả tác vụ nhạy cảm kiểm quyền tại server; không vẽ lặp mọi kiểm tra trên mọi mũi tên để giữ hình đọc được. Những chỗ lược bớt được nêu dưới từng sơ đồ.
