# FraudLens frontend

Dashboard tiếng Việt, chạy độc lập với FastAPI. Dùng JavaScript ES modules, CSS và
[Vite](https://vite.dev/guide/), không có dependency runtime. Sơ đồ là HTML/SVG nên có thể
chỉnh sửa từng thành phần trong mã nguồn, không cần công cụ thiết kế riêng.

## Chạy local

Cần Node.js 20.19+ hoặc 22.12+; khuyến nghị Node.js 22.12 trở lên.
Từ thư mục gốc, khởi động backend đã cài dependencies và migrate:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

Hoặc sử dụng backend qua Docker theo README gốc. Mở terminal khác:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Mở **http://127.0.0.1:5173**. Trên Linux/macOS dùng `npm` thay cho `npm.cmd`.
`npm.cmd` cũng tránh lỗi PowerShell chặn thực thi `npm.ps1` trên Windows.

Frontend mặc định gửi `/api/*` qua Vite proxy đến `http://127.0.0.1:8000/*`.
Không cần thêm CORS hoặc sửa backend. Nếu API ở địa chỉ khác, sao chép
`.env.example` thành `.env` **bên trong frontend**, thay `BACKEND_URL`, rồi khởi động lại Vite.
Không chép `.env` backend sang frontend. Xem [cấu hình proxy Vite](https://vite.dev/config/server-options.html#server-proxy).

## Chức năng

- Dashboard kiến trúc: xem chi tiết module, đầu vào/đầu ra; phóng to, thu nhỏ, vừa khung;
  bật/tắt các thành phần dự kiến mở rộng.
- Chỉ số tài xế, cảnh báo, hồ sơ và hàng chờ; phân luồng Auto Clear / Auto Fraud / Human Review.
- Các trang cảnh báo, hàng chờ review, hồ sơ điều tra và tài xế; phân trang và bộ lọc API.
- Chi tiết cảnh báo, bằng chứng, bản ghi nguồn, lịch sử xử lý và quyết định.
- Bố cục responsive; điều hướng bằng bàn phím và hộp thoại hỗ trợ Escape.
- Trạng thái tải, rỗng, lỗi từng nguồn dữ liệu và thử lại; không dùng số liệu mẫu trong giao diện.

Các trang dữ liệu hiện chỉ đọc. Thao tác bắt đầu review / ghi quyết định vẫn dùng API hiện có.
Sơ đồ vẫn hoạt động khi backend chưa chạy. “Đã triển khai” trên sơ đồ là phạm vi code hiện có,
không phải health check từng module. Chỉ báo kết nối trên thanh đầu trang gọi `/health`.
Kiến trúc tham chiếu `../docs/architecture.md` và `../docs/new_architecture.md`.

API hiện chưa có endpoint thống kê: dashboard lấy từng trang 200 bản ghi, tối đa 10 trang
cho mỗi nguồn. Khi chạm ngưỡng, số lượng hiển thị `≥ 2.000`; phân luồng ghi rõ chỉ tính
trên các cảnh báo đã tải. Dữ liệu cập nhật khi vào trang hoặc bấm Làm mới; không phải realtime.
Khi dữ liệu lớn hơn, nên bổ sung API tổng hợp riêng. Hai giá trị probability/confidence
null luôn hiển thị “Chưa ước lượng”, không suy ra từ risk score.

## Các vị trí chỉnh sửa

```text
frontend/
  index.html                    # Entry HTML
  vite.config.js                # Cổng chạy và API proxy
  src/
    main.js                     # Khung giao diện và điều hướng hash
    config/architecture.js      # Nội dung, vị trí node, liên kết và lộ trình
    components/
      architecture-map.js       # Vẽ sơ đồ và tương tác
      record-detail.js          # Chi tiết bản ghi / bằng chứng
    pages/
      dashboard.js              # Chỉ số, sơ đồ, hàng chờ, phân luồng
      records.js                # Danh sách, bộ lọc, phân trang
    lib/
      api.js                    # API client, hủy yêu cầu, timeout, giới hạn phân trang
      ui.js                     # Icon SVG, định dạng, nhãn và thành phần dùng chung
    styles.css                  # Màu sắc, typography, giao diện desktop
    styles-responsive.css       # Giao diện tablet/mobile, giảm chuyển động
  tests/                        # API client và kiểm thử trình duyệt
```

Để thêm một thành phần kiến trúc, sửa `nodes` và `edges` trong `architecture.js`.
Mỗi node có ID duy nhất, vị trí `x/y`, kích thước `w/h`, mô tả, đầu vào/đầu ra và module.
Đặt `planned: true` cho thành phần chưa triển khai. Sơ đồ dùng canvas tọa độ 1140px;
nếu đổi bố cục tổng thể, cập nhật kích thước và nhãn giai đoạn ở component tương ứng.
Để thêm trang, đăng ký route trong `main.js` và tạo module trong `pages/`.

## Build và kiểm tra

```powershell
npm.cmd run build
npm.cmd run preview
npm.cmd test
npm.cmd run format:check
# Cần dependencies Python của backend để chạy API kiểm thử cô lập:
npx.cmd playwright install chromium
npm.cmd run test:e2e
```

Bản build nằm ở `dist/`; preview tại **http://127.0.0.1:4173**.
Kiểm thử trình duyệt tự chạy frontend tại 5175 và backend thật tại 8751 với SQLite
trong bộ nhớ cùng dataset tổng hợp seed 42. Không dùng PostgreSQL hoặc dữ liệu local đang làm việc.
Cần Python đã cài `backend/requirements-dev.txt`; config ưu tiên `.venv` của dự án.
Nếu dùng Chrome đã cài trên máy thay Chromium của Playwright, đặt
`$env:PLAYWRIGHT_CHANNEL = 'chrome'` trước khi chạy test.
Các screenshot và trace kiểm thử nằm trong `test-results/` (Git bỏ qua).
Chạy `npm.cmd run format` để định dạng mã JavaScript, CSS, JSON và Markdown khi chỉnh sửa.

Khi triển khai static build, web server cần proxy `/api/*` đến backend và bỏ tiền tố `/api`.
Vite proxy chỉ phục vụ dev/preview. Không dùng `vite preview` làm production server.
Frontend này sử dụng API local chưa có xác thực; phần tài khoản và phân quyền là hạng mục nâng cấp.
