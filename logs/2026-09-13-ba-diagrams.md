# Bổ sung sơ đồ BA và ghi nhận bàn giao

- Thời gian đối chiếu, ghi log: **13/09/2026 21:38:38 (UTC+7)**.
- Thời gian bắt đầu/kết thúc xây dựng sơ đồ: **không ghi nhận chính xác**; thời gian trên là lúc ghi log.
- Mã tham chiếu nội bộ: `BACKFILL-20260913-BA-DIAGRAMS`.
- Yêu cầu: bổ sung các sơ đồ còn thiếu, ghi log công việc đã hoàn thành và commit.
- Nhánh: `main`; mốc đối chiếu trước commit: `1a7906d`.

## Phạm vi ghi nhận

Bộ BA nền tảng gồm 20 file đã được ghi tại [nhật ký BA](2026-09-13-ba-documents-backfill.md)
và commit `2ecb886`. Nhật ký này bổ sung phần sơ đồ đã hoàn thành nhưng chưa có bản ghi,
dựa trên nội dung hiện có và chênh lệch Git; không ghi lặp phần BA nền tảng.

Phần việc gồm **44 file: 39 file mới và 5 file cập nhật** trong `docs/BA/`.
Cùng với nhật ký này và `worklog.md`, phạm vi commit là **46 file**.

## Công việc và đầu ra

- Bổ sung **14 sơ đồ**, mỗi sơ đồ có nguồn PlantUML và bản SVG:
  **2 Use Case, 3 Activity có swimlane, 4 Sequence, 2 Domain Class và 3 DFD**.
- Use Case mô tả tác nhân, điều tra, phối hợp tài xế và quản trị.
  Activity/Sequence mô tả phát hiện dấu hiệu, điều tra, giao nhận yêu cầu giải trình,
  phê duyệt độc lập, khiếu nại và khắc phục.
- Domain Class mô tả hồ sơ, dữ liệu nguồn, bằng chứng, giải trình và phiên bản quyết định.
  DFD gồm ngữ cảnh, mức 1 và mức 2 cho tìm kiếm/kiểm chứng bằng chứng;
  tài liệu giải thích quy ước hình và cân bằng luồng dữ liệu.
- Viết sáu tài liệu 18–23: danh mục, chú giải, ràng buộc nghiệp vụ và truy vết đến
  UC, FR, DR, RULE, UAT; cập nhật liên kết trong năm tài liệu BA có sẵn.
- Tạo [trang xem sơ đồ](../docs/BA/diagrams/index.html) có tìm kiếm theo mã/tên/nhóm,
  hỗ trợ tìm tiếng Việt không dấu, bố cục màn hình nhỏ, liên kết mở SVG và tải nguồn.
- Cung cấp `catalog.json`, theme dùng chung, `render.ps1` và hướng dẫn kiểm cú pháp,
  tái xuất SVG/HTML tại [README sơ đồ](../docs/BA/diagrams/README.md).
- Ghi bổ sung nhật ký này và một dòng số 11 trong [worklog](../worklog.md).

Các sơ đồ giữ các nguyên tắc của BA: điểm rủi ro dùng để ưu tiên điều tra;
kết luận cần bằng chứng và người duyệt độc lập; thời hạn giải trình chỉ bắt đầu khi có
bằng chứng giao nhận hợp lệ; không phản hồi không đồng nghĩa thừa nhận gian lận.
Giải trình, tài liệu đính kèm và quyết định có trạng thái/phiên bản riêng;
khiếu nại được phân công độc lập và lưu lịch sử quyết định.

## Kiểm chứng

| Kiểm tra | Kết quả |
| --- | --- |
| Dựng SVG trong lượt bổ sung sơ đồ | Đã xuất đủ 14 SVG và trang HTML bằng PlantUML 1.2026.1, Java 21, layout Smetana |
| Kiểm cú pháp lại trước commit bằng `render.ps1 -CheckOnly` | `Syntax valid: 14 diagrams.` |
| Trang xem trong Chromium trước commit | 14/14 hình tải được; 4 tình huống lọc đạt; kiểm tra 58 liên kết (gồm liên kết neo); không có lỗi JavaScript |
| Màn hình nhỏ | Viewport rộng 390 px không tràn ngang |
| Danh mục, nguồn và SVG | Đủ 14 cặp; XML SVG hợp lệ; ID danh mục khớp nguồn |
| Markdown và nhật ký | Kiểm tra liên kết tệp nội bộ, UTF-8, khối mã; bảng worklog liên tục và không trùng dòng ghi nhận |
| Whitespace phần commit | `git diff --cached --check` đạt trước commit |

Kiểm tra trình duyệt sử dụng script hỗ trợ tại `.local/ba-diagram-tools/check-gallery.cjs`.
Công cụ JAR, script kiểm tra tạm và ảnh chụp phục vụ kiểm chứng nằm trong `.local/`,
được Git bỏ qua. Công cụ dựng tài liệu không gửi nội dung sơ đồ tới dịch vụ bên ngoài.

Đây là thay đổi tài liệu và trang xem sơ đồ; không có thay đổi backend/frontend ứng dụng
và không chạy lại bộ kiểm thử ứng dụng trong đợt ghi log/commit này.
Kiểm cú pháp và hiển thị không thay thế thẩm định nghiệp vụ. Bộ BA vẫn là đề xuất:
chưa ghi nhận phỏng vấn, phê duyệt chính sách hoặc thực thi UAT mới.

## Danh sách file công việc

Số dòng là tổng số dòng hiện có tại lúc đối chiếu, không phải số dòng thêm/sửa.
Các SVG được xuất trên một dòng. Năm file cập nhật chỉ thêm liên kết điều hướng:
tài liệu 04, 08, 10, 12 mỗi file thêm 2 dòng; README thêm 8 dòng.

| File | Thay đổi so với `1a7906d` | Tổng số dòng |
| --- | --- | --- |
| [docs/BA/04-current-and-target-business-processes.md](../docs/BA/04-current-and-target-business-processes.md) | Cập nhật | 107 |
| [docs/BA/08-use-cases-and-user-stories.md](../docs/BA/08-use-cases-and-user-stories.md) | Cập nhật | 89 |
| [docs/BA/10-data-requirements-and-glossary.md](../docs/BA/10-data-requirements-and-glossary.md) | Cập nhật | 97 |
| [docs/BA/12-requirements-traceability-matrix.md](../docs/BA/12-requirements-traceability-matrix.md) | Cập nhật | 64 |
| [docs/BA/18-diagram-catalog.md](../docs/BA/18-diagram-catalog.md) | Thêm mới | 47 |
| [docs/BA/19-uml-use-case-diagrams.md](../docs/BA/19-uml-use-case-diagrams.md) | Thêm mới | 28 |
| [docs/BA/20-uml-activity-diagrams.md](../docs/BA/20-uml-activity-diagrams.md) | Thêm mới | 33 |
| [docs/BA/21-uml-sequence-diagrams.md](../docs/BA/21-uml-sequence-diagrams.md) | Thêm mới | 41 |
| [docs/BA/22-uml-domain-class-diagrams.md](../docs/BA/22-uml-domain-class-diagrams.md) | Thêm mới | 43 |
| [docs/BA/23-data-flow-diagrams.md](../docs/BA/23-data-flow-diagrams.md) | Thêm mới | 84 |
| [docs/BA/diagrams/catalog.json](../docs/BA/diagrams/catalog.json) | Thêm mới | 16 |
| [docs/BA/diagrams/index.html](../docs/BA/diagrams/index.html) | Thêm mới | 100 |
| [docs/BA/diagrams/README.md](../docs/BA/diagrams/README.md) | Thêm mới | 31 |
| [docs/BA/diagrams/render.ps1](../docs/BA/diagrams/render.ps1) | Thêm mới | 64 |
| [docs/BA/diagrams/src/act-01-investigation.puml](../docs/BA/diagrams/src/act-01-investigation.puml) | Thêm mới | 54 |
| [docs/BA/diagrams/src/act-02-explanation.puml](../docs/BA/diagrams/src/act-02-explanation.puml) | Thêm mới | 40 |
| [docs/BA/diagrams/src/act-03-appeal.puml](../docs/BA/diagrams/src/act-03-appeal.puml) | Thêm mới | 48 |
| [docs/BA/diagrams/src/class-01-evidence.puml](../docs/BA/diagrams/src/class-01-evidence.puml) | Thêm mới | 89 |
| [docs/BA/diagrams/src/class-02-workflow.puml](../docs/BA/diagrams/src/class-02-workflow.puml) | Thêm mới | 89 |
| [docs/BA/diagrams/src/dfd-00-context.puml](../docs/BA/diagrams/src/dfd-00-context.puml) | Thêm mới | 32 |
| [docs/BA/diagrams/src/dfd-01-system.puml](../docs/BA/diagrams/src/dfd-01-system.puml) | Thêm mới | 69 |
| [docs/BA/diagrams/src/dfd-02-evidence-search.puml](../docs/BA/diagrams/src/dfd-02-evidence-search.puml) | Thêm mới | 44 |
| [docs/BA/diagrams/src/seq-01-detection.puml](../docs/BA/diagrams/src/seq-01-detection.puml) | Thêm mới | 48 |
| [docs/BA/diagrams/src/seq-02-explanation.puml](../docs/BA/diagrams/src/seq-02-explanation.puml) | Thêm mới | 51 |
| [docs/BA/diagrams/src/seq-03-decision.puml](../docs/BA/diagrams/src/seq-03-decision.puml) | Thêm mới | 51 |
| [docs/BA/diagrams/src/seq-04-appeal.puml](../docs/BA/diagrams/src/seq-04-appeal.puml) | Thêm mới | 49 |
| [docs/BA/diagrams/src/theme.puml](../docs/BA/diagrams/src/theme.puml) | Thêm mới | 35 |
| [docs/BA/diagrams/src/uc-01-investigation.puml](../docs/BA/diagrams/src/uc-01-investigation.puml) | Thêm mới | 44 |
| [docs/BA/diagrams/src/uc-02-governance.puml](../docs/BA/diagrams/src/uc-02-governance.puml) | Thêm mới | 41 |
| [docs/BA/diagrams/svg/act-01-investigation.svg](../docs/BA/diagrams/svg/act-01-investigation.svg) | Thêm mới | 1 |
| [docs/BA/diagrams/svg/act-02-explanation.svg](../docs/BA/diagrams/svg/act-02-explanation.svg) | Thêm mới | 1 |
| [docs/BA/diagrams/svg/act-03-appeal.svg](../docs/BA/diagrams/svg/act-03-appeal.svg) | Thêm mới | 1 |
| [docs/BA/diagrams/svg/class-01-evidence.svg](../docs/BA/diagrams/svg/class-01-evidence.svg) | Thêm mới | 1 |
| [docs/BA/diagrams/svg/class-02-workflow.svg](../docs/BA/diagrams/svg/class-02-workflow.svg) | Thêm mới | 1 |
| [docs/BA/diagrams/svg/dfd-00-context.svg](../docs/BA/diagrams/svg/dfd-00-context.svg) | Thêm mới | 1 |
| [docs/BA/diagrams/svg/dfd-01-system.svg](../docs/BA/diagrams/svg/dfd-01-system.svg) | Thêm mới | 1 |
| [docs/BA/diagrams/svg/dfd-02-evidence-search.svg](../docs/BA/diagrams/svg/dfd-02-evidence-search.svg) | Thêm mới | 1 |
| [docs/BA/diagrams/svg/seq-01-detection.svg](../docs/BA/diagrams/svg/seq-01-detection.svg) | Thêm mới | 1 |
| [docs/BA/diagrams/svg/seq-02-explanation.svg](../docs/BA/diagrams/svg/seq-02-explanation.svg) | Thêm mới | 1 |
| [docs/BA/diagrams/svg/seq-03-decision.svg](../docs/BA/diagrams/svg/seq-03-decision.svg) | Thêm mới | 1 |
| [docs/BA/diagrams/svg/seq-04-appeal.svg](../docs/BA/diagrams/svg/seq-04-appeal.svg) | Thêm mới | 1 |
| [docs/BA/diagrams/svg/uc-01-investigation.svg](../docs/BA/diagrams/svg/uc-01-investigation.svg) | Thêm mới | 1 |
| [docs/BA/diagrams/svg/uc-02-governance.svg](../docs/BA/diagrams/svg/uc-02-governance.svg) | Thêm mới | 1 |
| [docs/BA/README.md](../docs/BA/README.md) | Cập nhật | 66 |

Hai file nhật ký đi cùng: [worklog.md](../worklog.md) và bản ghi này.

## Tra cứu commit

Tra commit theo tiêu đề **`docs(ba): add UML and DFD diagrams with worklog`**.
Nhật ký và toàn bộ 44 file công việc được đưa vào cùng commit local trên `main`;
không ghi hash của chính commit vào nội dung của nó. Yêu cầu hiện tại chỉ bao gồm commit,
không thực hiện push.
