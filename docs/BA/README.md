# Phân tích nghiệp vụ hệ thống điều tra gian lận tài xế

Bộ tài liệu xây dựng hướng đi từ bài toán nghiệp vụ đến phạm vi sản phẩm, yêu cầu và nghiệm thu cho hệ thống phân tích, tìm kiếm bằng chứng và phối hợp giữa **tài xế – kiểm soát**.

| Thuộc tính | Giá trị |
| --- | --- |
| Phiên bản | BA 1.0, ngày 13/09/2026 |
| Trạng thái | Đề xuất để thẩm định nghiệp vụ; chưa phải quy chế vận hành đã phê duyệt |
| Bối cảnh giả định | Doanh nghiệp vận tải hành khách/đặt xe tại Việt Nam; một đơn vị vận hành trong pilot |
| Đối tượng sử dụng | Chủ sản phẩm, kiểm soát, đại diện tài xế, vận hành, dữ liệu, kiến trúc, phát triển và QA |
| Cơ sở | Rà soát repository và nghiên cứu nguồn công khai; chưa phỏng vấn người dùng hoặc phân tích dữ liệu vận hành thật |

## Định hướng đề xuất

Xây dựng **không gian điều tra dùng chung theo hồ sơ, với quyền xem khác nhau**. Hệ thống tổng hợp dấu hiệu và xếp hàng ưu tiên; kiểm soát tìm dữ liệu nguồn, kiểm tra giả thuyết và thông tin phản bác; tài xế nhận thông tin liên quan đến mình, giải trình, bổ sung tài liệu và khiếu nại kết luận. Kết luận phải có người chịu trách nhiệm, căn cứ và lịch sử phiên bản.

MVP tập trung vào bốn nhóm dấu hiệu đã có dữ liệu mẫu trong repository: bất thường GPS, chuyến ngắn lặp lại, dùng chung thiết bị và nghi vấn lạm dụng khuyến mại. Giá trị cần kiểm chứng là giảm thời gian thu thập bằng chứng và tăng chất lượng quyết định. Điểm rủi ro dùng để ưu tiên điều tra; việc xác nhận gian lận và tác động đến thu nhập/tài khoản là các quyết định khác nhau.

**Khác biệt phạm vi cần lưu ý:** [README hiện tại](../../README.md) và [kiến trúc đề xuất trước đó](../new_architecture.md) mô tả luồng kiểm soát nội bộ, tài xế không tham gia ứng dụng. Bộ BA này đáp ứng đề tài phối hợp hai bên theo yêu cầu hiện tại. Các chức năng mới dưới đây là yêu cầu đích, không phải tuyên bố đã được triển khai. Xem [đối chiếu prototype](17-prototype-gap-and-transition.md).

## Cách đọc và sử dụng

| Tài liệu | Nội dung và mục đích |
| --- | --- |
| [01. Bối cảnh và mục tiêu](01-business-context-and-objectives.md) | Vấn đề, giả thuyết giá trị, cây nguyên nhân, KPI |
| [02. Phạm vi](02-scope-and-boundaries.md) | MVP, ngoài phạm vi, phụ thuộc và ranh giới trách nhiệm |
| [03. Bên liên quan](03-stakeholders-and-roles.md) | Vai trò, RACI, quyền và phân tách trách nhiệm |
| [04. Quy trình nghiệp vụ](04-current-and-target-business-processes.md) | As-is giả định, to-be, trạng thái, SLA và ngoại lệ |
| [05. Yêu cầu nghiệp vụ](05-business-requirements.md) | BR-01–BR-10, giá trị và điều kiện thành công |
| [06. Yêu cầu chức năng](06-functional-requirements.md) | FR-01–FR-22, đầu vào, hành vi, đầu ra |
| [07. Yêu cầu phi chức năng](07-non-functional-requirements.md) | NFR-01–NFR-12, mục tiêu đo được |
| [08. Use case và user story](08-use-cases-and-user-stories.md) | UC-01–UC-10, US-01–US-12 và các luồng thay thế |
| [09. Taxonomy và quy tắc](09-fraud-taxonomy-and-business-rules.md) | Phân loại nghi vấn, ngưỡng demo, quy tắc quyết định |
| [10. Dữ liệu và thuật ngữ](10-data-requirements-and-glossary.md) | Mô hình khái niệm, từ điển, chất lượng và vòng đời dữ liệu |
| [11. Tiêu chí nghiệm thu](11-acceptance-criteria-and-uat.md) | UAT-01–UAT-28, dữ liệu kiểm thử, điều kiện pilot |
| [12. Truy vết yêu cầu](12-requirements-traceability-matrix.md) | Liên kết mục tiêu → yêu cầu → câu chuyện → nghiệm thu |
| [13. Nghiên cứu và lựa chọn hướng đi](13-research-and-solution-options.md) | Nguồn gốc, giới hạn áp dụng, so sánh phương án |
| [14. Kế hoạch khám phá](14-discovery-assumptions-and-risks.md) | Phỏng vấn, giả định, câu hỏi, rủi ro và quyết định mở |
| [15. MVP và lộ trình](15-mvp-roadmap-and-business-case.md) | Backlog theo đợt, cổng quyết định, năng lực và mô hình lợi ích |
| [16. Trải nghiệm và mẫu hồ sơ](16-experience-search-and-evidence-templates.md) | Màn hình khái niệm, đặc tả tìm kiếm, mẫu bằng chứng/giải trình |
| [17. Khoảng cách với prototype](17-prototype-gap-and-transition.md) | Phần tái sử dụng, phần còn thiếu, bàn giao kiến trúc |

Bản bảng tính để sử dụng trong workshop và nghiệm thu:

- [requirements-traceability.csv](requirements-traceability.csv): 22 yêu cầu chức năng và các liên kết truy vết; ma trận phi chức năng xem tài liệu 12.
- [uat-scenarios.csv](uat-scenarios.csv): 28 nhóm kịch bản, có cột điền build, dữ liệu, kết quả thực tế, bằng chứng, lỗi và người chấp nhận. Các cột này để trống có chủ đích vì chưa thực thi UAT.

CSV dùng UTF-8, phân cách bằng dấu phẩy. Nội dung gốc của bảng nằm tại tài liệu 11–12; khi đổi baseline, cập nhật và xuất lại CSV tương ứng để tránh lệch phiên bản.

## Quy ước chung

- **Đã quan sát:** có căn cứ trong tệp repository hoặc nguồn công khai được dẫn trực tiếp.
- **Giả định:** chưa xác minh với doanh nghiệp; quản lý tại tài liệu 14.
- **Đề xuất:** lựa chọn BA để thẩm định, gồm mọi ngưỡng, SLA, chi phí, quy mô pilot và ưu tiên.
- **Ví dụ tổng hợp:** chỉ phục vụ thiết kế/kiểm thử, không mô tả hành vi của tài xế thật.
- Must = điều kiện bắt buộc của MVP hợp tác hai bên; Should = xem xét sau khi Must hoàn thành; Could = thử nghiệm sau pilot. Các mã yêu cầu là định danh ổn định, không tái sử dụng cho nghĩa khác.

Sponsor cần chốt phạm vi vận tải, quy chế kết luận/khiếu nại, quyền sử dụng dữ liệu và nguồn lực pilot tại các cổng của tài liệu 15. Việc hoàn thành bộ BA không đồng nghĩa các cổng này đã được thông qua.
