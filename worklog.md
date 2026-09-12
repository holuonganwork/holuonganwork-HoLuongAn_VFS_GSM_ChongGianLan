# Tổng quan công việc — Driver Fraud Investigation System

File này chỉ lưu tóm tắt ngắn và liên kết đến nhật ký chi tiết trong `logs/`.
Không lưu các lượt hỏi đáp thông thường.

## Quy ước

- Mỗi lượt Codex có thay đổi file: tạo một file `logs/AUTO-YYYYMMDD-xxxxxxxxxx.md`
  và một dòng tóm tắt tại đây. Mã AUTO là mã nội bộ, không phải mã chat thật.
- Không ghi log khi không có thay đổi thực tế so với đầu lượt; bỏ qua thay đổi
  có sẵn từ trước, chính `worklog.md`, `logs/`, cache và dữ liệu được loại trừ.
- Chi tiết mục tiêu, công việc, đầu ra, file và số dòng được lưu trong file log.
  Thời gian dùng múi giờ Việt Nam (UTC+7). Không ghi thông tin bí mật.
- Không thêm thủ công một dòng khác cho lượt đã được hook ghi. Lượt bị hủy trước
  khi có sự kiện kết thúc cần bổ sung thủ công nếu muốn lưu phần công việc đã làm.
- Cách bật và kiểm tra hook: [docs/worklog-hook.md](docs/worklog-hook.md).

## Các công việc đã thực hiện

| STT | Thời gian thực hiện (Ngày, giờ) | Tóm tắt công việc | File log chi tiết |
| --- | --- | --- | --- |
| 1 | 12/09/2026 — giờ triển khai chưa ghi nhận đầy đủ | Xây dựng backend milestone 1, schema, phát hiện gian lận, dữ liệu mẫu và kiểm thử. | [Chi tiết milestone 1](logs/2026-09-12-milestone-1.md) |
| 2 | 12/09/2026 11:45:04 (UTC+7) — bắt đầu lập nhật ký | Tạo nhật ký và quy ước bàn giao công việc giữa các phiên. | [Chi tiết khởi tạo worklog](logs/2026-09-12-worklog-initialization.md) |
| 3 | 12/09/2026 15:56:35 (UTC+7) — ghi nhận kết quả | Tạo hook lưu chi tiết trong logs, rút gọn worklog và xóa các bản ghi hỏi đáp. | [Chi tiết thiết lập hook](logs/2026-09-12-codex-worklog-hook.md) |
| 4 | 12/09/2026 17:10:50 (UTC+7) — ghi nhận chuẩn bị commit | Phân nhóm file thành 9 danh mục, kiểm thử và chuẩn hóa dòng cuối của sáu file cấu hình. | [Chi tiết chuẩn bị commit](logs/2026-09-12-category-commits.md) |
