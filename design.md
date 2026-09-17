# Green SM — UI Design Specification

> **Trạng thái:** Bản chuẩn hoá phục vụ thiết kế UI/UX và phát triển giao diện. Đây không phải brand guideline chính thức của Green SM.
>
> **Nguồn:** Các token và quy ước được trích từ [brand.md](brand.md), dựa trên file CSS tham chiếu. Những nội dung không có trong CSS được ghi rõ là đề xuất triển khai, không được xem là nhận diện thương hiệu đã xác nhận.

## 1. Phạm vi và nguyên tắc sử dụng

- **Tên thương hiệu sử dụng trong sản phẩm:** Green SM.
- **Hướng hình ảnh:** xanh ngọc, sạch, hiện đại, thân thiện môi trường; ưu tiên không gian thoáng, nền sáng và điểm nhấn teal.
- **Không tự tạo logo hoặc tagline:** CSS không có logo gốc, favicon, app icon hay slogan. Chỉ thay thế phần logo trong thiết kế khi có file SVG/PNG chính thức và hướng dẫn sử dụng từ chủ sở hữu thương hiệu.
- **Nguồn sự thật cho giao diện:** dùng token trong tài liệu này thay cho mã màu rải rác trong mockup hoặc code.

## 2. Design tokens

### 2.1. Color tokens

```css
:root {
  /* Brand */
  --color-brand-primary: #28BDBF;
  --color-brand-600: #22B1B3;
  --color-brand-700: #209799;
  --color-brand-800: #3C7475;
  --color-brand-secondary: #E3BB42;
  --color-brand-highlight: #2DCCD3;
  --color-brand-tint: #BCE8E8;
  --color-brand-light: #E3F8F8;
  --color-brand-accent-bg: #D4F2F2;

  /* Surface and text */
  --color-bg-canvas: #FFFFFF;
  --color-bg-subtle: #F9FAFB;
  --color-text-heading: #111827;
  --color-text-body: #4B5563;
  --color-text-placeholder: #6B7280;
  --color-border-default: #D1D5DB;
  --color-border-subtle: #E5E7EB;

  /* Semantic status */
  --color-success: #22C55E;
  --color-success-bg: #F0FDF4;
  --color-error: #E60A32;
  --color-error-bg: #FEF2F2;
  --color-warning: #B45309;
  --color-warning-bg: #FFFBEB;
  --color-info: #2F6BFF;
  --color-info-bg: #F0F9FF;

  /* Interaction */
  --color-primary-hover: #25B5BB;
  --color-primary-pressed: #1F9B9F;
  --color-disabled-bg: #E6E6E6;
  --color-disabled-text: #B3B3B3;
}
```

| Nhóm | Token | HEX | RGB | Mục đích |
|---|---|---:|---:|---|
| Primary | `--color-brand-primary` | `#28BDBF` | `40, 189, 191` | CTA chính, trạng thái đang chọn, icon active |
| Brand dark | `--color-brand-700` | `#209799` | `32, 151, 153` | Link, border/hover đậm |
| Brand darkest | `--color-brand-800` | `#3C7475` | `60, 116, 117` | Chữ trên nền nhạt, trạng thái hover đậm |
| Secondary | `--color-brand-secondary` | `#E3BB42` | `227, 187, 66` | Điểm nhấn hạn chế, badge hoặc khuyến mại |
| Brand light | `--color-brand-light` | `#E3F8F8` | `227, 248, 248` | Hover của nút phụ, nền thẻ nhấn mạnh |
| Text heading | `--color-text-heading` | `#111827` | `17, 24, 39` | Tiêu đề và nội dung cần độ tương phản cao |
| Text body | `--color-text-body` | `#4B5563` | `75, 85, 99` | Nội dung thông thường |
| Border | `--color-border-default` | `#D1D5DB` | `209, 213, 219` | Input, divider, card outline |

### 2.2. Background gradient

Chỉ dùng cho hero/header trải nghiệm hoặc khu vực truyền thông; không dùng làm nền mặc định cho form, bảng dữ liệu hoặc màn hình nghiệp vụ.

```css
--gradient-brand-experience: linear-gradient(180deg, #D5FEFF 0%, #F0FCD5 95%);
```

### 2.3. Typography tokens

```css
--font-sans: Montserrat, Arial, sans-serif;
```

Montserrat là font chính và có dải weight 100–900 trong CSS tham chiếu. Dùng Arial/sans-serif làm fallback. Không thay bằng Inter, Roboto hoặc font khác nếu chưa có quyết định thiết kế riêng.

| Vai trò | Font size / line height | Weight | Quy ước |
|---|---:|---:|---|
| Hero | `48px / 60px` | 700–800 | Tối đa một tiêu đề chính mỗi màn hình |
| H1 | `36px / 44px` | 700 | Tiêu đề trang desktop |
| H2 | `30px / 38px` | 700 | Tiêu đề section |
| H3 | `20px / 28px` | 600 | Tiêu đề card/modal |
| Body | `16px / 24px` | 400 | Văn bản mặc định |
| Body small | `14px / 20px` | 400–500 | Mô tả phụ, nội dung bảng |
| Label | `12px / 18px` | 500–600 | Nhãn form, metadata, bottom navigation |

### 2.4. Layout, spacing và radius

| Token | Giá trị | Dùng cho |
|---|---:|---|
| `--space-1` | `4px` | Khoảng cách icon–text nhỏ |
| `--space-2` | `8px` | Khoảng cách nội bộ tối thiểu |
| `--space-3` | `12px` | Nhóm thông tin gần nhau |
| `--space-4` | `16px` | Padding card/form mặc định |
| `--space-6` | `24px` | Padding CTA, khoảng cách section nhỏ |
| `--space-8` | `32px` | Khoảng cách section |
| `--radius-sm` | `8px` | Input, chip, control nhỏ |
| `--radius-md` | `12px` | Button, card tiêu chuẩn |
| `--radius-lg` | `16px` | Modal, card nổi bật |
| `--radius-pill` | `9999px` | Tag, filter chip, avatar; không dùng mặc định cho mọi button |

## 3. Nhận diện trên màn hình nhỏ

### 3.1. Logo, favicon và app icon

- Dùng **biểu tượng logo chính thức dạng SVG** cho favicon và app icon; không dùng toàn bộ wordmark khi kích thước dưới 32px.
- Chuẩn bị tối thiểu ba phiên bản: full-color trên nền sáng, trắng trên nền teal đậm và đơn sắc tối cho trường hợp hạn chế màu.
- Chừa safe area xung quanh biểu tượng tối thiểu 12% cạnh icon.
- Kích thước xuất: favicon `16/32/48px`; app icon `180/192/512/1024px`.
- Không suy diễn hình dạng biểu tượng từ CSS. Cần bổ sung asset chính thức trước khi xuất bản.

### 3.2. Navigation

| Bối cảnh | Quy chuẩn |
|---|---|
| Web header | Cao mục tiêu `68px`; logo trái, điều hướng trung tâm/phải, CTA nổi bật dùng Primary |
| Mobile header | Cao tối thiểu `56px`; giữ tối đa một CTA và menu gọn |
| Bottom navigation | 4–5 mục, cao `64–72px` chưa tính safe-area; icon 24px, label 12px |
| Trạng thái active | Icon/label `#28BDBF`; inactive dùng `#6B7280` |
| Trạng thái focus | Hiển thị ring 2px hoặc outline rõ ràng, không chỉ đổi màu |

## 4. Component specification

### 4.1. Buttons

| Variant | Default | Hover | Pressed | Disabled |
|---|---|---|---|---|
| Primary | Nền `#28BDBF`, chữ trắng | `#25B5BB` | `#1F9B9F` | Nền `#E6E6E6`, chữ `#B3B3B3` |
| Secondary | Nền trắng, border/chữ `#209799` | Nền `#E3F8F8` | Nền `#D4F2F2` | Nền trắng, border `#E5E7EB`, chữ `#B3B3B3` |
| Ghost/link | Nền trong, chữ `#209799` | Nền `#E3F8F8` | Nền `#D4F2F2` | Chữ `#B3B3B3` |
| Destructive | Nền `#E60A32`, chữ trắng | Dùng sắc đỏ đậm hơn đã được phê duyệt | Giảm sáng hoặc tăng tối rõ ràng | Theo token disabled |

| Size | Height | Padding ngang | Text | Radius |
|---|---:|---:|---|---:|
| Small | `36px` | `12px` | 14px / 20px | 8px |
| Medium | `40px` | `16px` | 14px / 20px | 12px |
| Large | `48px` | `24px` | 16px / 24px | 12px |

- Icon button phải có vùng chạm ít nhất `44 × 44px`, tooltip hoặc `aria-label`.
- Chuyển trạng thái trong khoảng 200–300ms; không dùng animation làm chậm thao tác.
- Nút Primary chỉ nên có một hành động chính trong một khu vực nhìn thấy.

### 4.2. Inputs và selection controls

| Thành phần | Quy chuẩn |
|---|---|
| Text input/select | Cao 48px, padding ngang 16px, radius 8px hoặc 12px, border `#D1D5DB`, nền trắng |
| Placeholder | `#6B7280`; không dùng placeholder thay thế label |
| Focus | Border `#28BDBF` + outer ring 2px `#BCE8E8` |
| Error | Border và message `#E60A32`, nền cảnh báo nhẹ `#FEF2F2` khi cần |
| Disabled | Nền `#E6E6E6`, chữ `#B3B3B3`, không che mất giá trị đã nhập |
| Checkbox | 20px, radius 4px, checked dùng Primary và check trắng |
| Radio | 20px, hình tròn, selected dùng Primary |
| Switch | Track tối thiểu 40 × 24px; trạng thái bật dùng Primary |

### 4.3. Cards, modal và feedback

- Card mặc định: nền trắng, border `#E5E7EB`, radius 12px, padding 16px hoặc 24px.
- Modal: radius 16px, overlay đen 60–80%, có nút đóng và trap focus.
- Toast/alert: dùng bảng màu semantic; không dùng teal cho lỗi hoặc cảnh báo.
- Không chỉ biểu đạt trạng thái qua màu: luôn có icon, nhãn hoặc nội dung mô tả.

### 4.4. Iconography

- Ưu tiên SVG, canvas `24 × 24px`, stroke `2px`, đầu nét và góc bo đồng nhất.
- Dùng cùng một họ icon cho toàn sản phẩm; không trộn icon fill, emoji và nhiều thư viện khác nhau trong cùng một màn hình.
- Màu icon mặc định theo text; active dùng `#28BDBF`; destructive dùng `#E60A32`.

## 5. Accessibility baseline

- Kiểm tra độ tương phản chữ/nền theo WCAG AA: tối thiểu 4.5:1 cho body text và 3:1 cho text lớn/điều khiển UI.
- Không đặt chữ trắng nhỏ trên `#28BDBF` nếu chưa xác nhận tỷ lệ tương phản trong thiết kế cuối; ưu tiên chữ đậm, kích thước đủ lớn hoặc dùng `#3C7475` cho text trên nền nhạt.
- Mọi thành phần tương tác phải thao tác được bằng bàn phím, có focus state rõ ràng và nhãn truy cập được.
- Khu vực chạm trên mobile tối thiểu 44 × 44px.

## 6. Quy trình áp dụng

1. **Wireframe:** xác định luồng người dùng, hierarchy thông tin, hành động chính/phụ và trạng thái lỗi trước khi thêm màu.
2. **UI design:** dùng token từ mục 2 và component từ mục 4; không hard-code màu ngoài token nếu chưa có lý do được ghi nhận.
3. **Prototype:** kiểm tra các luồng đặt xe, đăng nhập, thanh toán, lỗi/thành công, loading, empty state và responsive mobile.
4. **Handoff:** bàn giao Figma/component specs, token mapping và trạng thái interaction cho lập trình viên.

## 7. Danh sách cần bổ sung trước khi phát hành

- File logo chính thức (SVG/PNG), favicon và app icon.
- Slogan/tagline đã được thương hiệu phê duyệt.
- Quy tắc clear space, kích thước tối thiểu và biến thể logo nền sáng/tối.
- Kiểm thử contrast trên các màn hình thực tế trước khi chốt màu chữ trên CTA.
