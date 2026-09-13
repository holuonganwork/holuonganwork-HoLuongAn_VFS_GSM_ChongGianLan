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
| 4 | 12/09/2026 17:12:47–17:12:55 (UTC+7) — thời gian commit; đối chiếu bổ sung 13/09/2026 | Hoàn tất 9 commit theo danh mục cho 71 file; bổ sung hash và kết quả kiểm chứng. | [Chi tiết commit theo danh mục](logs/2026-09-12-category-commits.md) |
| 5 | 13/09/2026 02:48:31 (UTC+7) — ghi bù; thời gian thực hiện chưa xác định | Ghi nhận 2 tài liệu kiến trúc/review; bổ sung 14 khung tài liệu còn rỗng ngày 13/09. | [Chi tiết tài liệu kiến trúc](logs/2026-09-13-architecture-documents-backfill.md) |
| 6 | 13/09/2026 02:48:31 (UTC+7) — ghi bù; thời gian thực hiện chưa xác định | Ghi nhận 30 file Alert/Decision; bổ sung kiểm chứng: 125 test đạt, 3 PostgreSQL chưa chạy. | [Chi tiết luồng cảnh báo–quyết định](logs/2026-09-13-decision-pipeline-backfill.md) |
| 7 | 13/09/2026 15:45:49 (UTC+7) — ghi bù; giờ thực hiện chưa xác định | Ghi bù 20 file BA: yêu cầu, truy vết và 28 kịch bản UAT; chưa nghiệm thu. | [Chi tiết BA](logs/2026-09-13-ba-documents-backfill.md) |
| 8 | 13/09/2026 15:45:49 (UTC+7) — ghi bù; giờ thực hiện chưa xác định | Ghi bù frontend FraudLens và CI; build, 5 test API và 9 E2E đạt. | [Chi tiết frontend](logs/2026-09-13-frontend-backfill.md) |
| 9 | 13/09/2026 15:45:49 (UTC+7) — ghi bù; giờ thực hiện chưa xác định | Ghi nhận 3 tài nguyên giao diện backend còn dở dang, chưa tích hợp. | [Chi tiết khởi tạo web](logs/2026-09-13-backend-web-scaffold-backfill.md) |
| 10 | 13/09/2026 15:45:49 (UTC+7) — ghi nhận kết quả đối chiếu | Đối chiếu đủ 95 file công việc; chia 6 commit cho 103 file, bổ sung tracking và kết quả kiểm chứng. | [Chi tiết đối chiếu và commit](logs/2026-09-13-worklog-audit-and-commits.md) |
