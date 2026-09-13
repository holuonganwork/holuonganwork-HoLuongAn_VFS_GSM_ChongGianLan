# System Architect — Nền tảng điều tra gian lận tài xế

| Thuộc tính | Baseline |
| --- | --- |
| Phiên bản | SA 1.0 — 14/09/2026 |
| Trạng thái | Thiết kế đích đề xuất, có thể thay đổi bằng ADR; chưa triển khai, chưa nghiệm thu production |
| Cơ sở nghiệp vụ | [BA 1.0](../BA/README.md), đặc biệt FR-01–FR-22 và NFR-01–NFR-12 |
| Cơ sở kỹ thuật | Working tree được rà soát ngày 14/09/2026: FastAPI, PostgreSQL, pipeline rule và frontend Vite |
| Phạm vi | Điều tra, bằng chứng, phối hợp tài xế–kiểm soát, phê duyệt và khiếu nại; mở rộng phát hiện bằng ML sau pilot |
| Chủ trì đề xuất | System Architect; Product/Risk sở hữu quy chế, Data sở hữu nguồn, Security sở hữu quyền, Operations sở hữu SLO |

**Lựa chọn chính:** phát triển từ modular monolith Python hiện có, tách API và worker thành các tiến trình độc lập; PostgreSQL giữ giao dịch nghiệp vụ, object storage giữ bản chụp/tệp bằng chứng. Dùng hợp đồng dữ liệu có phiên bản, outbox và xử lý idempotent để có thể thêm broker hoặc tách dịch vụ khi có căn cứ về tải và tổ chức.

## Cách đọc

| Tài liệu | Câu hỏi được trả lời |
| --- | --- |
| [01. Tổng quan](01-architecture-overview.md) | Chọn kiến trúc nào và khác prototype ở đâu? |
| [02. Động lực và ràng buộc](02-architecture-drivers-and-constraints.md) | Tối ưu cho mục tiêu nào, với giả định tải nào? |
| [03. Ngữ cảnh hệ thống](03-system-context.md) | Ai sử dụng, ai sở hữu dữ liệu, hệ thống nối với ai? |
| [04. Container và component](04-containers-and-components.md) | Chạy những tiến trình nào, module nào chịu trách nhiệm ghi? |
| [05. Kiến trúc dữ liệu](05-data-architecture.md) | Lưu, liên kết, tìm kiếm, bảo toàn và xóa dữ liệu thế nào? |
| [06. Phát hiện và quyết định](06-detection-and-decision-pipeline.md) | Từ dữ liệu tới hồ sơ, phê duyệt và khiếu nại ra sao? |
| [07. API và tích hợp](07-api-and-integration.md) | Contract, lỗi, retry, phân trang và sự kiện có nghĩa gì? |
| [08. Bảo mật và quyền](08-security-and-access-control.md) | Chặn truy cập chéo, giả danh, lộ tệp và tự duyệt thế nào? |
| [09. Hạ tầng và triển khai](09-deployment-and-infrastructure.md) | Pilot chạy ở đâu, phát hành và khôi phục thế nào? |
| [10. Hiệu năng và độ tin cậy](10-performance-scalability-and-reliability.md) | Tính tải, đo SLO, xử lý quá tải và mở rộng khi nào? |
| [11. Quan sát và phản hồi mô hình](11-observability-and-model-feedback.md) | Theo dõi vận hành và đánh giá phát hiện bằng bằng chứng nào? |
| [12. Sổ quyết định ADR](12-architecture-decision-records.md) | Vì sao chọn, chấp nhận đánh đổi gì, điều kiện xem lại? |
| [13. Migration và rollout](13-migration-and-rollout-plan.md) | Đi từ code hôm nay tới pilot mà bảo toàn lịch sử thế nào? |
| [14. Rủi ro và đánh đổi](14-technical-risks-and-tradeoffs.md) | Phần nào có thể thất bại và ai xử lý? |
| [Nguồn tham khảo](references.md) | Học gì từ nguồn sơ cấp, giới hạn áp dụng là gì? |
| [Ma trận truy vết](requirements-traceability.csv) | FR/NFR được giải quyết và kiểm chứng tại đâu? |

Đọc 01 → 02 → 12 để đánh giá quyết định; 03–08 để thiết kế/phát triển; 09–11 và 13–14 để lập kế hoạch vận hành. Mermaid nằm trực tiếp trong Markdown để sửa cùng nội dung. CSV là danh mục kiểm chứng thiết kế, không phải kết quả UAT.

## Quan hệ với các tài liệu khác

1. [README repository](../../README.md), [architecture.md](../architecture.md) và mã nguồn là căn cứ về **phần đang có**. Một vài mô tả cũ có thể chưa cập nhật frontend; ưu tiên mã nguồn khi xác minh implementation.
2. [BA 1.0](../BA/README.md) là baseline nghiệp vụ được chọn cho thiết kế này: tài xế tham gia; kết luận có người duyệt độc lập; có khiếu nại. BA vẫn là đề xuất cần thẩm định trước pilot.
3. Bộ SA này là **thiết kế đích mới**. [new_architecture.md](../new_architecture.md), [architect-review-comparison](../architect-review-comparison) và [future.md](../../future.md) là phương án trước đó; không kết hợp các phần mâu thuẫn thành một workflow.
4. ADR-001 ghi rõ việc chọn baseline. Hoàn thiện SA không tự thay code, không phê duyệt quy chế, không bật nhánh tự kết luận hay triển khai cloud.

## Cách chỉnh sửa kiến trúc về sau

| Loại thay đổi | Cách cập nhật |
| --- | --- |
| Ngưỡng rule, lịch SLA, giới hạn upload | Sửa cấu hình có version, chạy đánh giá, lưu người duyệt và ngày hiệu lực; giữ snapshot lịch sử |
| Thay framework, broker, cloud, search engine | Tạo ADR thay thế, ghi số đo/chi phí/khả năng quay lại; cập nhật 04, 07, 09, 10, 13 |
| Thay quyền tài xế, cho phép tự kết luận, thêm chế tài | Cập nhật yêu cầu BA và ADR-001/004 trước implementation; cập nhật quyền, quy trình, UAT và migration |
| Thay schema/API/event | Bổ sung version và kế hoạch tương thích; kiểm consumer, backfill, rollback, retention |
| Thay một quyết định lịch sử | Dùng quyết định kế tiếp hoặc đính chính có thẩm quyền; không sửa nội dung snapshot trước |

Mỗi ADR có trạng thái `proposed`, `accepted`, `superseded` hoặc `rejected`. SA 1.0 dùng `proposed` cho các lựa chọn mới: đây là phương án thiết kế cụ thể được đề xuất, không phải chỗ trống chờ làm. Giữ nguyên ID cũ khi thay thế; tăng baseline và cập nhật ma trận truy vết cùng một thay đổi tài liệu.

Các bất biến cần bảo vệ khi đổi công nghệ: quyền được kiểm ở server; điểm rủi ro không phải kết luận; quyết định/audit nguyên tử; bằng chứng được truy nguyên theo version; retry không nhân đôi tác động; một quyết định hiện hành; không trực tiếp đổi tài khoản hoặc tiền trong phạm vi này.

## Kiểm chứng bộ tài liệu

Đã kiểm cấu trúc 14 chương, 14 ADR, liên kết tệp nội bộ và JSON minh họa; ma trận đủ 22 FR +12 NFR, đối chiếu đúng các nhóm UAT tương ứng trong BA và bao phủ UAT-01–28. Có 9 sơ đồ Mermaid dạng nguồn trong Markdown; kiểm loại sơ đồ/fence và rà soát nội dung, chưa chạy renderer trong đợt này.

Các SLO, sizing, API đích, migration và biện pháp bảo mật là thiết kế chờ triển khai/đo. Đợt hoàn thiện tài liệu không thay mã ứng dụng, không chạy UAT hoặc benchmark hệ thống; cổng nghiệm thu và đầu ra còn phải làm được chỉ rõ tại tài liệu 13.
