Kết luận nhanh: file CSS đủ để trích xuất nền tảng UI số, nhưng không phải brand guideline hoàn chỉnh. CSS không chứa trực tiếp logo, favicon hay slogan. Tên “Green SM” là thông tin từ yêu cầu của bạn, không xuất hiện rõ trong CSS.

Nguồn chính: [khối design tokens](C:/Users/anho2/Downloads/8df8b0548502e6c4.css:6298), [font Montserrat](C:/Users/anho2/Downloads/8df8b0548502e6c4.css:12882).

## 1. Nhận diện cốt lõi

| Hạng mục | Kết quả |
|---|---|
| Brand Name | Green SM — do bạn cung cấp |
| Logo | Không trích xuất được. CSS chỉ có selector logo chung và ảnh banner `banner-download.png`, không có file logo |
| Slogan / Tagline | Không xuất hiện trong CSS |
| Phong cách hình ảnh | Suy ra: xanh ngọc, sạch, hiện đại, thân thiện môi trường; có gradient xanh nhạt–xanh lá |
| Font chính | Montserrat, hỗ trợ variable weight 100–900 |
| Fallback | Arial, sans-serif |

Logo tối ưu cho favicon/App Icon nên dùng riêng biểu tượng nhận diện Green SM dạng SVG, không dùng wordmark ở kích thước nhỏ. Không nên tự dựng logo chỉ từ màu CSS.

## 2. Digital Color Palette

### Màu thương hiệu

| Vai trò | HEX | RGB |
|---|---:|---:|
| Primary | `#28BDBF` | `rgb(40, 189, 191)` |
| Brand 600 | `#22B1B3` | `rgb(34, 177, 179)` |
| Brand 700 / Link | `#209799` | `rgb(32, 151, 153)` |
| Brand 800 / Dark | `#3C7475` | `rgb(60, 116, 117)` |
| Secondary gold | `#E3BB42` | `rgb(227, 187, 66)` |
| Accent background | `#D4F2F2` | `rgb(212, 242, 242)` |
| Brand tint | `#BCE8E8` | `rgb(188, 232, 232)` |
| Brand light | `#E3F8F8` | `rgb(227, 248, 248)` |

CSS cũng chứa màu nổi bật `#2DCCD3` (`rgb(45, 204, 211)`) cho một số background, border và shadow. Đây nên được xem là màu highlight/CTA phụ, không nên tự động thay thế Primary.

### Màu nền, chữ và đường viền

| Vai trò | HEX | RGB |
|---|---:|---:|
| Canvas | `#FFFFFF` | `rgb(255, 255, 255)` |
| Background phụ | `#F9FAFB` | `rgb(249, 250, 251)` |
| Heading | `#111827` | `rgb(17, 24, 39)` |
| Body text | `#4B5563` | `rgb(75, 85, 99)` |
| Placeholder | `#6B7280` | `rgb(107, 114, 128)` |
| Border chính | `#D1D5DB` | `rgb(209, 213, 219)` |
| Border phụ | `#E5E7EB` | `rgb(229, 231, 235)` |

### Màu trạng thái

| Trạng thái | Màu chính | Màu nền |
|---|---|---|
| Success | `#22C55E` / `rgb(34,197,94)` | `#F0FDF4` |
| Error | `#E60A32` / `rgb(230,10,50)` | `#FEF2F2` |
| Warning | `#B45309` / `rgb(180,83,9)` | `#FFFBEB` |
| Info | `#2F6BFF` / `rgb(47,107,255)` | `#F0F9FF` |

Gradient header được khai báo là:

```css
linear-gradient(180deg, #D5FEFF, #F0FCD5 95%)
```

## 3. UI Components đề xuất chuẩn hóa

| Component | Quy chuẩn nên dùng |
|---|---|
| Primary button | Cao 48px, padding ngang 24px, radius 12px, nền `#28BDBF`, chữ trắng |
| Hover | `#25B5BB` |
| Pressed | `#1F9B9F` |
| Disabled | Nền `#E6E6E6`, chữ `#B3B3B3` |
| Secondary button | Nền trắng, border `#209799`, chữ `#209799`; hover nền `#E3F8F8` |
| Header | Có thể dùng chiều cao 68px; CSS có cấu trúc navigation responsive |
| Bottom bar app | 4–5 mục, cao khoảng 64–72px; icon active dùng `#28BDBF` |
| Icon | Dùng một bộ SVG thống nhất, grid 24px, stroke khoảng 2px |
| Input | Cao 48px, border `#D1D5DB`, radius 8–12px, placeholder `#6B7280` |
| Input focus | Border `#28BDBF`, focus ring `#BCE8E8` |
| Checkbox/Radio | Kích thước khoảng 20px; trạng thái checked dùng màu Primary |

CSS hiện có nhiều mức bo góc như 8px, 12px, 16px và dạng pill. Vì vậy nên chốt một chuẩn riêng cho sản phẩm để tránh giao diện thiếu nhất quán. Các kích thước 36, 40, 44 và 48px cũng đã xuất hiện trong CSS.

## 4. Typography

Nên dùng:

```css
font-family: Montserrat, Arial, sans-serif;
```

Scale phù hợp với các kích thước đã xuất hiện trong file:

- Body: `16px / 24px`, weight 400
- Small text: `14px / 20px`
- Label: `12px / 18px`
- Heading nhỏ: `20px / 28px`, weight 600
- Heading lớn: `30–36px`, weight 700
- Hero heading: `48px / 60px`, weight 700–800

## 5. Quy trình triển khai

1. Wireframe: chỉ bố trí layout, navigation, button, form và luồng người dùng.
2. UI Design: áp dụng token màu, Montserrat, radius, icon và trạng thái component ở trên.
3. Prototype: kiểm tra các luồng chính như đặt xe, đăng nhập, thanh toán, thông báo lỗi/thành công và responsive mobile.

Điểm còn thiếu để hoàn thiện bộ nhận diện là file logo SVG/PNG chính thức và nguồn xác nhận slogan/tagline.