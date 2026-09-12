# Tự động ghi worklog cho Codex

Khi kết thúc một lượt Codex có thay đổi file, hook tạo **một file chi tiết trong
`logs/` và một dòng tóm tắt kèm liên kết trong `worklog.md`**. Lượt hỏi đáp không
sửa file không tạo file log hoặc dòng tóm tắt. Mã `AUTO-YYYYMMDD-xxxxxxxxxx` do hook
sinh, không phải mã chat thật. Thư mục `logs/` nằm tại gốc repository này.

## Cài đặt và kích hoạt

- Script: `scripts/codex_worklog_hook.py`, Python 3.11+, chỉ dùng thư viện chuẩn.
- Cấu hình đang dùng: `.codex/hooks.json`. Bản mẫu: `scripts/worklog-hooks.example.json`.
- Windows dùng Python trong `.venv` của dự án và đường dẫn tuyệt đối hiện tại.
  Nếu chuyển thư mục dự án, sửa hai giá trị `commandWindows`; đường dẫn có khoảng
  trắng cần đặt trong dấu nháy theo shell đang dùng. macOS/Linux dùng `python3` và Git.
- Mở lại phiên Codex tại repository để nạp cấu hình. Trong Codex CLI, chạy `/hooks`,
  xem và trust hai hook `UserPromptSubmit` và `Stop` của dự án. Chỉ tin cậy thư mục
  dự án chưa đủ: Codex yêu cầu duyệt riêng định nghĩa hook mới hoặc đã thay đổi.
  IDE/app cần bản hỗ trợ hooks và thao tác review hooks tương ứng; nếu chưa có giao
  diện review, có thể dùng Codex CLI trong cùng thư mục và cùng tài khoản local.
- Sau khi kích hoạt, bắt đầu **lượt mới** để có snapshot ban đầu. Việc chép cấu hình
  vào giữa lượt không tạo được trạng thái trước khi sửa file của lượt đó.

Đây là cơ chế lifecycle hook của Codex, không phải Git commit hook và không phụ
thuộc agent nhớ tự viết nhật ký. Tham khảo [tài liệu hooks chính thức của OpenAI](https://learn.chatgpt.com/docs/hooks).

## Nội dung được ghi

`worklog.md` là mục lục bốn cột: **STT | Thời gian thực hiện (Ngày, giờ) | Tóm tắt
công việc | File log chi tiết**. Tóm tắt lấy tối đa 160 ký tự từ yêu cầu và số file
thay đổi. Nội dung chi tiết không đưa vào mục lục.

Mỗi file `logs/AUTO-YYYYMMDD-xxxxxxxxxx.md` chứa:

| Cột | Cách lấy dữ liệu |
| --- | --- |
| Thời gian | Bắt đầu và kết thúc theo đồng hồ máy, UTC+7 |
| Mã log đoạn chat | Mã nội bộ `AUTO-...` |
| Mục tiêu công việc | Tối đa 600 ký tự từ yêu cầu người dùng |
| Công việc thực hiện | Số file có thay đổi so với đầu lượt |
| Đầu ra công việc | Tối đa 3.000 ký tự từ câu trả lời cuối, ghi rõ “Agent báo cáo” |
| Các đoạn code đã sửa | Tên file, thêm/sửa/xóa và phạm vi dòng; dòng đã xóa dùng tọa độ cũ |

Hook ghi nhận chênh lệch file; không tự kết luận test đã đạt hay mục tiêu đã hoàn
thành. Kết quả kiểm thử chỉ xuất hiện nếu có trong báo cáo cuối của agent.

## Phạm vi và cách hoạt động

`UserPromptSubmit` lưu hash file và hash từng dòng vào `.local/worklog-hook/`.
`Stop` so sánh với file cuối lượt, lưu file log rồi thêm dòng vào cuối bảng mục lục.
Không lưu bản sao code hoặc đọc lịch sử chat. Trạng thái đầu lượt bị rút gọn sau
khi xử lý xong; `.local/` đã được Git bỏ qua.

- Theo dõi file đã được Git quản lý và file mới chưa bị `.gitignore` loại trừ.
  Thay đổi có sẵn từ trước lượt không bị tính lại. Đổi tên được ghi là xóa và thêm.
- Bao gồm code, tài liệu và cấu hình. Bỏ qua chính `worklog.md`, `logs/`, thư mục môi trường,
  cache, `.local/`, dữ liệu `data/raw/`, `data/generated/` và file bí mật thông dụng
  (`.env`, khóa riêng...). `.env.example` vẫn được theo dõi.
- Sửa file rồi khôi phục đúng trạng thái ban đầu không tạo log. Tạo rồi xóa trong
  cùng lượt cũng không tạo log. Chỉ sửa `worklog.md` hoặc `logs/` không kích hoạt log lặp.
- File nhị phân, liên kết, file không phải UTF-8 và file lớn hơn 1 MiB vẫn được ghi
  nhận thay đổi, nhưng không có số dòng. Snapshot không chứa nội dung những file này.
- Khóa hệ điều hành bảo vệ STT khi nhiều tiến trình hook cùng ghi. Khóa được giải
  phóng khi tiến trình dừng. Marker ẩn trong dòng giúp chống ghi trùng khi `Stop`
  được gọi lại, kể cả sau sự cố giữa lúc ghi worklog và lưu trạng thái hoàn tất.
  File chi tiết được lưu trước mục lục; nếu ghi mục lục thất bại, lần thử lại dùng
  cùng file chi tiết đã có để không tạo file log trùng.
- Hook không có snapshot đầu lượt sẽ cảnh báo và bỏ qua; không lấy toàn bộ thay
  đổi chưa commit làm lịch sử giả. Lỗi hook không chặn agent tiếp tục làm việc.
- Hook dựa trên file trong workspace nên không phân biệt được thay đổi do người
  dùng hoặc agent khác đồng thời sửa. Dùng workspace/worktree riêng nếu chạy nhiều
  tác vụ đồng thời. Lượt bị hủy hoặc ứng dụng đóng trước `Stop` chưa được ghi tự động.

## Kiểm chứng và khắc phục

Chạy kiểm thử độc lập, không cần database:

```powershell
.venv/Scripts/python.exe -m pytest backend/tests/test_worklog_hook.py -q
```

Nếu không có log, kiểm tra `/hooks` đã trust cả hai sự kiện, cấu hình không tắt
`features.hooks`, đường dẫn Python còn đúng, và đã bắt đầu lượt mới sau khi bật.
Hook cần Git có trên PATH và quyền ghi `worklog.md`, `logs/`, `.local/worklog-hook/`.
Cảnh báo `ValueError` thường là thiếu snapshot hoặc bảng worklog bị đổi cấu trúc;
`CalledProcessError` là Git không chạy được; `TimeoutError` là đang chờ khóa quá lâu.
Giữ nguyên tiêu đề bốn cột và hàng phân cách của bảng mục lục.

Lịch sử cũ đã được chuyển thành hai file hồi cứu trong `logs/`: milestone 1 và
khởi tạo worklog. Bảy bản ghi hỏi đáp thông thường đã được xóa khỏi nhật ký.
