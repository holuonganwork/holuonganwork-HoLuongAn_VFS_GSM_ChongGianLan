# Tạo hook ghi nhật ký và chuyển worklog thành mục lục

- Thời gian ghi nhận kết quả: **12/09/2026 15:56:35 (UTC+7)**.
- Mã tham chiếu nội bộ: `SETUP-20260912-WORKLOG-HOOK`.
- Đây là bản ghi khởi tạo trong lượt cài hook. Giờ bắt đầu chưa được ghi nhận;
  hook chưa có snapshot đầu lượt này nên bản ghi được bổ sung thủ công.

## Mục tiêu công việc

Tự động ghi nhật ký khi Codex sửa file. Chi tiết mỗi lượt nằm trong thư mục
`logs/` tại gốc dự án; `worklog.md` chỉ lưu tóm tắt và liên kết. Không ghi các
lượt hỏi đáp thông thường và xóa các bản ghi hỏi đáp đã có trong worklog cũ.

## Công việc thực hiện

- Tạo script Python nhận sự kiện `UserPromptSubmit` và `Stop` qua JSON trên stdin.
  Chụp hash file và từng dòng trước lượt; so sánh trạng thái cuối lượt, kể cả
  file mới chưa được Git quản lý. Thay đổi chưa commit có sẵn không bị ghi lại.
- Sinh file `logs/AUTO-YYYYMMDD-xxxxxxxxxx.md` cho lượt có thay đổi và thêm một
  dòng tổng quan vào worklog. Lưu file chi tiết trước khi ghi liên kết mục lục.
- Ghi rõ thêm/sửa/xóa, đường dẫn và số dòng. Phần bị xóa dùng số dòng cũ;
  file nhị phân, liên kết, không phải UTF-8 hoặc >1 MiB không suy đoán số dòng.
- Thêm khóa ghi và marker chống trùng; ghi file theo cơ chế thay thế nguyên tử;
  thử lại sau lỗi dùng cùng file log. Bỏ qua đầu ra nhật ký, cache và dữ liệu
  được loại trừ. Lỗi hook cảnh báo nhưng không chặn lượt làm việc của agent.
- Cài `.codex/hooks.json` từ bản mẫu trong `scripts/`, sử dụng Python của `.venv`.
  Không thay đổi backend, schema database hoặc quy tắc phát hiện gian lận.
- Chuyển 10 bản ghi milestone 1 vào một file chi tiết, chuyển bản ghi khởi tạo
  worklog vào file riêng. Xóa 7 bản ghi hỏi đáp cũ (STT 11–17), không chuyển
  những bản ghi này vào thư mục logs. Đánh lại STT của mục lục.

## Đầu ra và kiểm chứng

- **20 kiểm thử đạt** bằng `pytest backend/tests/test_worklog_hook.py -q`.
  Có hai cảnh báo deprecation từ các thư viện test backend hiện có.
- Ruff lint và format đạt với hai file Python mới.
- Chạy đúng các lệnh Windows trong cấu hình đã cài với sự kiện thử nghiệm
  `UserPromptSubmit`, `Stop`, `Stop` lặp: trả JSON hợp lệ, không tạo log hoặc
  sửa mục lục khi không có file thay đổi.
- Đã đối chiếu 51 liên kết local trong hai file lịch sử và mục lục trước khi
  thêm bản ghi này; liên kết và các dòng tham chiếu đều tồn tại lúc kiểm tra.
- Giữ nguyên yêu cầu của Codex về review/trust hook mới. Cấu hình đã được cài,
  nhưng chưa xác minh được Codex tự phát sự kiện trong một lượt có hook được trust.
  Cần mở `/hooks`, review/trust hai hook của dự án và bắt đầu lượt mới.
  Đây là yêu cầu của [Codex hooks](https://learn.chatgpt.com/docs/hooks).

## Các file và dòng đã thay đổi

| Thao tác | File | Phạm vi tại thời điểm ghi log |
| --- | --- | --- |
| Thêm mới | [scripts/codex_worklog_hook.py](../scripts/codex_worklog_hook.py#L1) | Dòng 1–337: snapshot, diff, log chi tiết, mục lục và xử lý sự kiện |
| Thêm mới | [scripts/worklog-hooks.example.json](../scripts/worklog-hooks.example.json#L1) | Dòng 1–31: cấu hình mẫu hai sự kiện |
| Thêm mới | [.codex/hooks.json](../.codex/hooks.json#L1) | Dòng 1–31: cấu hình đã cài trong dự án |
| Thêm mới | [backend/tests/test_worklog_hook.py](../backend/tests/test_worklog_hook.py#L1) | Dòng 1–309: kiểm thử các trường hợp ghi log và bỏ qua |
| Thêm mới | [docs/worklog-hook.md](../docs/worklog-hook.md#L1) | Dòng 1–89: hướng dẫn sử dụng, kích hoạt và giới hạn |
| Sửa | [worklog.md](../worklog.md#L1) | Dòng 1–24: mục lục bốn cột và quy ước ngắn |
| Thêm mới | [logs/2026-09-12-milestone-1.md](2026-09-12-milestone-1.md#L1) | Dòng 1–115: chi tiết công việc milestone 1 được chuyển từ worklog |
| Thêm mới | [logs/2026-09-12-worklog-initialization.md](2026-09-12-worklog-initialization.md#L1) | Dòng 1–16: chi tiết khởi tạo nhật ký được chuyển từ worklog |
| Thêm mới | [logs/2026-09-12-codex-worklog-hook.md](2026-09-12-codex-worklog-hook.md#L1) | Từ dòng 1: bản ghi công việc hiện tại |

## Giới hạn vận hành

Một lượt là một lần xử lý yêu cầu có sự kiện bắt đầu và kết thúc. Lượt bị hủy
trước `Stop` chưa được ghi tự động. File thay đổi đồng thời bởi người dùng hoặc
agent khác trong cùng workspace không thể phân biệt tác giả chỉ bằng snapshot.
`worklog.md`, `logs/` và các đường dẫn loại trừ không kích hoạt nhật ký lặp.
