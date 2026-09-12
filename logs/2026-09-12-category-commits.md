# Chuẩn bị commit theo danh mục

- Thời gian ghi nhận: **12/09/2026 17:10:50 (UTC+7)**.
- Mã tham chiếu nội bộ: `PREP-20260912-COMMITS`.
- Nhánh làm việc: `main`; commit gốc trước khi phân nhóm: `a74e1f2`.
- Bản ghi bổ sung cho các chỉnh sửa file thực tế trong bước chuẩn bị commit.

## Mục tiêu công việc

Chia các file của dự án thành các commit riêng theo nhóm chức năng để dễ xem
lịch sử, review và bảo trì. Giữ cấu trúc thư mục hiện có.

## Công việc thực hiện

- Kiểm tra các file chưa commit, nội dung cấu hình và trạng thái Git.
- Phân 70 file có sẵn thành chín nhóm; bản ghi này bổ sung một file nhật ký,
  đưa tổng số file của đợt commit lên 71.
- Chạy toàn bộ kiểm thử, lint và định dạng trước khi tạo commit.
- Xóa một dòng trống dư ở cuối sáu file cấu hình do kiểm tra whitespace của
  Git phát hiện. Không thay đổi giá trị cấu hình hoặc logic ứng dụng.
- Giữ `.env`, `.venv/`, `.local/` và dữ liệu sinh ra ngoài danh sách commit.

## Các nhóm commit

| Nhóm | Số file | Nội dung |
| --- | --- | --- |
| Môi trường | 11 | Dependencies Python, Docker, cấu hình công cụ và thư mục dữ liệu |
| Database | 14 | Domain, cấu hình chung, model, session và migration |
| Phát hiện gian lận | 10 | Detector, scoring, bằng chứng và script chạy detection |
| API | 8 | API, schema và quy trình điều tra của con người |
| Dữ liệu mẫu | 2 | Sinh và nhập dữ liệu giả lập có thể tái lập |
| Kiểm thử/CI | 9 | Bộ test backend và workflow GitHub Actions |
| Tài liệu | 7 | Kiến trúc, schema, hướng dẫn, kiểm chứng và định hướng future.md |
| Hook Codex | 5 | Hook, cấu hình, tài liệu và kiểm thử ghi nhật ký |
| Nhật ký | 5 | Worklog tổng quan và bốn file log chi tiết |

Hash và thứ tự commit được tra cứu trực tiếp bằng `git log --oneline`.

## Đầu ra và kiểm chứng

- **101 kiểm thử đạt, không bỏ qua test**, gồm các kiểm thử PostgreSQL và hook.
  Có hai cảnh báo deprecation từ thư viện test hiện có.
- PostgreSQL dùng database kiểm thử riêng `fraud_investigation_tests`. Kết nối
  `localhost` bị chờ quá lâu; lần kiểm chứng hoàn tất dùng `127.0.0.1` và thời
  hạn kết nối 5 giây qua biến môi trường của tiến trình test.
- Ruff lint và format đạt cho toàn bộ `backend` và `scripts`.
- Chỉ xóa dòng trống cuối file sau kiểm thử; không thay đổi hành vi đã kiểm chứng.

## Các file và dòng đã sửa trong lượt này

| Thao tác | File | Vị trí |
| --- | --- | --- |
| Xóa dòng trống cuối | [.dockerignore](../.dockerignore#L8) | Dòng cũ 9; file còn 8 dòng |
| Xóa dòng trống cuối | [.env.example](../.env.example#L9) | Dòng cũ 10; file còn 9 dòng |
| Xóa dòng trống cuối | [.gitignore](../.gitignore#L15) | Dòng cũ 16; file còn 15 dòng |
| Xóa dòng trống cuối | [backend/Dockerfile](../backend/Dockerfile#L10) | Dòng cũ 11; file còn 10 dòng |
| Xóa dòng trống cuối | [backend/alembic.ini](../backend/alembic.ini#L31) | Dòng cũ 32; file còn 31 dòng |
| Xóa dòng trống cuối | [pyproject.toml](../pyproject.toml#L11) | Dòng cũ 12; file còn 11 dòng |
| Bổ sung tổng quan | [worklog.md](../worklog.md#L25) | Dòng 25: liên kết đến bản ghi này |
| Thêm mới | [logs/2026-09-12-category-commits.md](2026-09-12-category-commits.md#L1) | Từ dòng 1: chi tiết chuẩn bị commit |
