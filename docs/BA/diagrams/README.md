# Nguồn và bản xuất sơ đồ BA

Thư mục chứa mã nguồn PlantUML, bản SVG đã xuất và [trang xem chung](index.html). Danh mục và truy vết nghiệp vụ tại [tài liệu 18](../18-diagram-catalog.md). Có 14 sơ đồ: 2 Use Case, 3 Activity, 4 Sequence, 2 Domain Class và 3 DFD.

- `src/*.puml`: nguồn từng sơ đồ; `src/theme.puml` là cấu hình hình thức dùng chung, không phải một sơ đồ.
- `svg/*.svg`: bản xuất vector, xem trực tiếp trong Markdown hoặc trình duyệt.
- `catalog.json`: danh sách ID, tiêu đề, nhóm và tên tệp phục vụ trang xem chung.
- `render.ps1`: kiểm cú pháp và tái xuất SVG/trang HTML; không tải thư viện hoặc gửi nội dung ra dịch vụ bên ngoài.

## Tái tạo

Cần Java chạy được và PlantUML JAR. Bản xuất hiện tại được kiểm với **PlantUML 1.2026.1, Java 21**; layout Smetana được chọn trong theme. Tải công cụ từ [bản phát hành chính thức](https://github.com/plantuml/plantuml/releases/tag/v1.2026.1). Chạy ở repository root, thay đường dẫn Java/JAR bằng bản cài trên máy:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./docs/BA/diagrams/render.ps1 `
  -JavaExecutable 'C:/path/to/jdk/bin/java.exe' `
  -PlantUmlJar '.local/ba-diagram-tools/plantuml-1.2026.1.jar'
```

Chỉ kiểm cú pháp:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./docs/BA/diagrams/render.ps1 `
  -JavaExecutable 'C:/path/to/jdk/bin/java.exe' `
  -PlantUmlJar '.local/ba-diagram-tools/plantuml-1.2026.1.jar' `
  -CheckOnly
```

Lệnh trên cho phép chạy script trong tiến trình PowerShell dựng sơ đồ, không đổi execution policy cố định của máy. Script chỉ ghi các bản xuất trong thư mục này. Không lưu JAR vào thư mục tài liệu; công cụ tải phục vụ lần xuất hiện tại nằm ở `.local/ba-diagram-tools/`, được repository bỏ qua. Nguồn dùng `!include theme.puml` cục bộ; SVG xuất với `-nometadata` để không nhúng mã nguồn nén vào hình.

Sau thay đổi: kiểm cú pháp, xuất lại, mở SVG xem tiếng Việt/bố cục, cập nhật mô tả và truy vết nếu ý nghĩa đổi. Việc render thành công không chứng minh nghiệp vụ đúng; cần đối chiếu các bất biến trong tài liệu 18 và điều kiện UAT. Hướng dẫn công cụ: [PlantUML command line](https://plantuml.com/command-line), [layout Smetana](https://plantuml.com/smetana02).
