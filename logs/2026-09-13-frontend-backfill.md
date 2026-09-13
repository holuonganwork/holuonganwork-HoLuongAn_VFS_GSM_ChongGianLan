# Ghi bù frontend FraudLens, tích hợp API và kiểm thử trình duyệt

- Thời gian đối chiếu, ghi bù: **13/09/2026 15:45:49 (UTC+7)**.
- Thời gian thực hiện ban đầu: **chưa xác định**; không dùng giờ sửa file làm giờ làm việc.
- Mã tham chiếu nội bộ: `BACKFILL-20260913-FRONTEND`.
- Căn cứ: nội dung file và trạng thái Git so với `d144d90`; bản ghi hồi cứu theo đầu ra,
  không suy đoán tác giả, số phiên chat hoặc thời lượng thực hiện.

## Mục tiêu và công việc đã có

- Tạo frontend độc lập bằng JavaScript ES modules, CSS và Vite: entry HTML, favicon,
  cấu hình proxy, package/lockfile, quy ước định dạng và hướng dẫn chạy/build/kiểm thử.
- Dashboard tiếng Việt có sơ đồ kiến trúc tương tác, chi tiết module, zoom/vừa khung,
  bật/tắt thành phần dự kiến và phân biệt code đã có với phần mở rộng.
- Đọc API thật cho chỉ số, cảnh báo, hàng chờ review, hồ sơ và tài xế; có lọc, phân trang,
  xem bằng chứng/bản ghi nguồn, lịch sử và quyết định.
- Có timeout, hủy request, tải/rỗng/lỗi từng nguồn/thử lại; giới hạn đếm tối đa 2.000 bản ghi
  mỗi nguồn và hiển thị cận dưới khi chạm ngưỡng. Probability/confidence null được giữ là chưa biết.
- Có responsive, điều hướng bàn phím, hộp thoại Escape và xử lý dữ liệu API dưới dạng text.
- Bổ sung test API client, Playwright và API kiểm thử SQLite cô lập; workflow GitHub Actions
  thực hiện build, format, unit test và E2E. README gốc thêm hướng dẫn frontend; Docker ignore
  loại frontend khỏi build context backend.

## Kiểm chứng tại lần ghi bù

- `npm.cmd test`: **5/5 test đạt**.
- `npm.cmd run build`: **đạt**, Vite 7.3.6. Lần đầu sandbox chặn ghi file tạm; chạy lại với
  quyền thực thi được duyệt thành công, không sửa cấu hình build.
- `npm.cmd run format:check`: **đạt**.
- `$env:PLAYWRIGHT_CHANNEL = 'chrome'; npm.cmd run test:e2e`: **9/9 test đạt**, dùng Chrome
  có sẵn, frontend cổng 5175 và backend SQLite trong bộ nhớ cổng 8751. Lần chạy mặc định
  không khởi động được trình duyệt vì máy thiếu Chromium của Playwright; chưa kiểm chứng
  lần chạy Linux CI dùng Chromium riêng.

Các trang dữ liệu hiện chỉ đọc; số liệu cập nhật khi vào trang/làm mới, chưa có realtime
hoặc API thống kê tổng hợp. Test dùng dữ liệu tổng hợp, không xác nhận vận hành production.
Build, node_modules, screenshot và trace được Git bỏ qua.

## File được ghi nhận

README gốc cũng có phần backend được ghi ở log Decision Pipeline trước đó. Bảng dưới bao gồm
phần frontend bổ sung; không tính README thành hai file khi tổng hợp toàn đợt.

| File | Trạng thái so với `d144d90` | Phạm vi tại lúc đối chiếu |
| --- | --- | --- |
| [.dockerignore](../.dockerignore) | Sửa | Dòng 1–9 |
| [.github/workflows/frontend.yml](../.github/workflows/frontend.yml) | Thêm mới | Dòng 1–32 |
| [README.md](../README.md) | Sửa | Dòng 1–265 |
| [frontend/.env.example](../frontend/.env.example) | Thêm mới | Dòng 1–2 |
| [frontend/.gitignore](../frontend/.gitignore) | Thêm mới | Dòng 1–6 |
| [frontend/.prettierignore](../frontend/.prettierignore) | Thêm mới | Dòng 1–5 |
| [frontend/.prettierrc.json](../frontend/.prettierrc.json) | Thêm mới | Dòng 1–5 |
| [frontend/README.md](../frontend/README.md) | Thêm mới | Dòng 1–105 |
| [frontend/index.html](../frontend/index.html) | Thêm mới | Dòng 1–22 |
| [frontend/package-lock.json](../frontend/package-lock.json) | Thêm mới | Dòng 1–1188 |
| [frontend/package.json](../frontend/package.json) | Thêm mới | Dòng 1–23 |
| [frontend/playwright.config.js](../frontend/playwright.config.js) | Thêm mới | Dòng 1–41 |
| [frontend/public/favicon.svg](../frontend/public/favicon.svg) | Thêm mới | Dòng 1–1 |
| [frontend/src/components/architecture-map.js](../frontend/src/components/architecture-map.js) | Thêm mới | Dòng 1–77 |
| [frontend/src/components/record-detail.js](../frontend/src/components/record-detail.js) | Thêm mới | Dòng 1–77 |
| [frontend/src/config/architecture.js](../frontend/src/config/architecture.js) | Thêm mới | Dòng 1–268 |
| [frontend/src/lib/api.js](../frontend/src/lib/api.js) | Thêm mới | Dòng 1–64 |
| [frontend/src/lib/ui.js](../frontend/src/lib/ui.js) | Thêm mới | Dòng 1–131 |
| [frontend/src/main.js](../frontend/src/main.js) | Thêm mới | Dòng 1–96 |
| [frontend/src/pages/dashboard.js](../frontend/src/pages/dashboard.js) | Thêm mới | Dòng 1–134 |
| [frontend/src/pages/records.js](../frontend/src/pages/records.js) | Thêm mới | Dòng 1–84 |
| [frontend/src/styles-responsive.css](../frontend/src/styles-responsive.css) | Thêm mới | Dòng 1–401 |
| [frontend/src/styles.css](../frontend/src/styles.css) | Thêm mới | Dòng 1–1483 |
| [frontend/tests/api.test.js](../frontend/tests/api.test.js) | Thêm mới | Dòng 1–64 |
| [frontend/tests/dashboard.spec.js](../frontend/tests/dashboard.spec.js) | Thêm mới | Dòng 1–161 |
| [frontend/tests/serve_backend.py](../frontend/tests/serve_backend.py) | Thêm mới | Dòng 1–31 |
| [frontend/vite.config.js](../frontend/vite.config.js) | Thêm mới | Dòng 1–19 |
