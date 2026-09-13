# Ghi bù tài liệu kiến trúc mục tiêu và bản so sánh

- Thời gian đối chiếu, ghi bù: **13/09/2026 02:48:31 (UTC+7)**.
- Thời gian thực hiện ban đầu: **chưa xác định**; không suy đoán từ giờ sửa file.
- Mã tham chiếu nội bộ: `BACKFILL-20260913-ARCHITECTURE`.
- Căn cứ: nội dung hai file hiện có và trạng thái `git status` so với `d144d90`.
- Đây là bản ghi hồi cứu theo nhóm tài liệu; không khẳng định hai file được tạo
  trong cùng một phiên chat hoặc bởi một tác giả cụ thể.

## Mục tiêu công việc

Lưu phương án kiến trúc mục tiêu và đánh giá những phần cần chuyển đổi từ hệ
thống phát hiện bằng quy tắc sang luồng tách biệt detection, policy và quản lý hồ sơ.

## Công việc đã có trong repository

- Có tài liệu mô tả kiến trúc mục tiêu: AI là tác nhân phát hiện chính, con người
  review trường hợp ngoại lệ, tài xế là đối tượng dữ liệu, taxonomy dùng chung.
- Phân biệt Signal, Alert và Case; mô tả ba nhánh Auto Clear, Auto Fraud và Human
  Review, cùng định hướng tách xử lý dữ liệu, detection và nghiệp vụ.
- Có nội dung định hướng mở rộng ML/anomaly/ensemble, queue, lưu trữ, feedback,
  LLM/RAG hỗ trợ và ranh giới Python/Java trong tương lai.
- Có bản so sánh kiến trúc cũ với mục tiêu: thời điểm tạo case, risk score so với
  probability/confidence, vai trò con người, bằng chứng, dữ liệu và các bước chuyển tiếp.

## Đầu ra và trạng thái

Hai file tài liệu tồn tại, đang chưa được Git theo dõi tại thời điểm đối chiếu.
Đây là đầu ra thiết kế và review; các thành phần tương lai trong tài liệu không
đồng nghĩa đã được triển khai. Phần code chuyển tiếp đang có được ghi riêng trong
[log triển khai](2026-09-13-decision-pipeline-backfill.md).

Không chạy kiểm thử backend cho việc ghi bù tài liệu. Không chép các lượt hỏi đáp
thông thường vào nhật ký; chỉ ghi nhận hai file đầu ra đã tồn tại.

## File và dòng được ghi nhận

| Thao tác so với `d144d90` | File | Phạm vi |
| --- | --- | --- |
| Thêm mới | [docs/new_architecture.md](../docs/new_architecture.md#L1) | Dòng 1–591: phương án kiến trúc mục tiêu |
| Thêm mới | [docs/architect-review-comparison](../docs/architect-review-comparison#L1) | Dòng 1–930: so sánh và đề xuất bước chuyển tiếp; giữ nguyên tên file hiện có |

## Bổ sung đối chiếu lúc 13/09/2026 15:45:49 (UTC+7)

Hai tài liệu phương án/review ở trên vẫn giữ nguyên nội dung so với snapshot ghi bù trước.
Phát hiện thêm **14 file mới, toàn bộ 0 byte**, trong `docs/System Architect/`. Tên file tạo
khung các chủ đề: tổng quan, động lực/ràng buộc, context, component, dữ liệu, pipeline, API,
bảo mật, deployment, hiệu năng/độ tin cậy, quan sát/feedback, ADR, rollout và rủi ro.

Chỉ ghi nhận **đã khởi tạo khung tài liệu; chưa viết nội dung thiết kế chi tiết**. Lần này
giữ nguyên các file rỗng và đưa vào Git để theo dõi phần việc dở dang. Không dùng việc file
tồn tại làm bằng chứng hoàn thành thiết kế. Tổng phạm vi của log sau bổ sung: **16 file**.

| File | Trạng thái so với `d144d90` | Phạm vi tại lúc đối chiếu |
| --- | --- | --- |
| [docs/System Architect/01-architecture-overview.md](../docs/System%20Architect/01-architecture-overview.md) | Thêm mới | 0 byte; chưa có nội dung |
| [docs/System Architect/02-architecture-drivers-and-constraints.md](../docs/System%20Architect/02-architecture-drivers-and-constraints.md) | Thêm mới | 0 byte; chưa có nội dung |
| [docs/System Architect/03-system-context.md](../docs/System%20Architect/03-system-context.md) | Thêm mới | 0 byte; chưa có nội dung |
| [docs/System Architect/04-containers-and-components.md](../docs/System%20Architect/04-containers-and-components.md) | Thêm mới | 0 byte; chưa có nội dung |
| [docs/System Architect/05-data-architecture.md](../docs/System%20Architect/05-data-architecture.md) | Thêm mới | 0 byte; chưa có nội dung |
| [docs/System Architect/06-detection-and-decision-pipeline.md](../docs/System%20Architect/06-detection-and-decision-pipeline.md) | Thêm mới | 0 byte; chưa có nội dung |
| [docs/System Architect/07-api-and-integration.md](../docs/System%20Architect/07-api-and-integration.md) | Thêm mới | 0 byte; chưa có nội dung |
| [docs/System Architect/08-security-and-access-control.md](../docs/System%20Architect/08-security-and-access-control.md) | Thêm mới | 0 byte; chưa có nội dung |
| [docs/System Architect/09-deployment-and-infrastructure.md](../docs/System%20Architect/09-deployment-and-infrastructure.md) | Thêm mới | 0 byte; chưa có nội dung |
| [docs/System Architect/10-performance-scalability-and-reliability.md](../docs/System%20Architect/10-performance-scalability-and-reliability.md) | Thêm mới | 0 byte; chưa có nội dung |
| [docs/System Architect/11-observability-and-model-feedback.md](../docs/System%20Architect/11-observability-and-model-feedback.md) | Thêm mới | 0 byte; chưa có nội dung |
| [docs/System Architect/12-architecture-decision-records.md](../docs/System%20Architect/12-architecture-decision-records.md) | Thêm mới | 0 byte; chưa có nội dung |
| [docs/System Architect/13-migration-and-rollout-plan.md](../docs/System%20Architect/13-migration-and-rollout-plan.md) | Thêm mới | 0 byte; chưa có nội dung |
| [docs/System Architect/14-technical-risks-and-tradeoffs.md](../docs/System%20Architect/14-technical-risks-and-tradeoffs.md) | Thêm mới | 0 byte; chưa có nội dung |

Kết quả commit của các file tài liệu được đối chiếu tại [log tổng hợp đợt commit](2026-09-13-worklog-audit-and-commits.md).
