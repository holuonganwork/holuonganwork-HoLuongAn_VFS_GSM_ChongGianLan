# Ghi bù bộ phân tích nghiệp vụ và tài liệu nghiệm thu

- Thời gian đối chiếu, ghi bù: **13/09/2026 15:45:49 (UTC+7)**.
- Thời gian thực hiện ban đầu: **chưa xác định**; không dùng giờ sửa file làm giờ làm việc.
- Mã tham chiếu nội bộ: `BACKFILL-20260913-BA`.
- Căn cứ: nội dung file và trạng thái Git so với `d144d90`; bản ghi hồi cứu theo đầu ra,
  không suy đoán tác giả, số phiên chat hoặc thời lượng thực hiện.

## Mục tiêu và công việc đã có

- Xây dựng bộ BA gồm README, 17 tài liệu chuyên đề và hai bảng CSV phục vụ thẩm định.
- Mô tả bối cảnh, mục tiêu/KPI, phạm vi, stakeholder/RACI, quy trình, yêu cầu nghiệp vụ,
  chức năng/phi chức năng, use case, user story, taxonomy và yêu cầu dữ liệu.
- Có ma trận truy vết, kịch bản UAT, nghiên cứu tham chiếu, giả định/rủi ro, lộ trình MVP,
  mẫu trải nghiệm/tìm kiếm/bằng chứng và đối chiếu khoảng cách với prototype.
- CSV truy vết có 22 yêu cầu chức năng; CSV UAT có 28 kịch bản, để trống các cột kết quả
  thực thi và người nghiệm thu. Đây là biểu mẫu đã chuẩn bị, chưa phải UAT đã đạt.

## Trạng thái và giới hạn

Nội dung hiện có là **đề xuất BA 1.0 để thẩm định**. Bộ BA đề xuất phối hợp tài xế–kiểm soát;
backend hiện triển khai review nội bộ và không có luồng tài xế tham gia ứng dụng. Chính bộ BA
đã ghi nhận khác biệt này trong README và tài liệu 17; cần quyết định phạm vi trước triển khai.
Không ghi nhận phỏng vấn, phê duyệt nghiệp vụ, xác minh dữ liệu vận hành hoặc nghiệm thu đã hoàn tất.

Lần ghi bù này kiểm tra số file, nội dung mục lục, liên kết nội bộ và cấu trúc CSV;
không thẩm định lại nguồn nghiên cứu bên ngoài hoặc chuyển đề xuất thành chức năng đã chạy.

## File được ghi nhận

| File | Trạng thái so với `d144d90` | Phạm vi tại lúc đối chiếu |
| --- | --- | --- |
| [docs/BA/01-business-context-and-objectives.md](../docs/BA/01-business-context-and-objectives.md) | Thêm mới | Dòng 1–60 |
| [docs/BA/02-scope-and-boundaries.md](../docs/BA/02-scope-and-boundaries.md) | Thêm mới | Dòng 1–51 |
| [docs/BA/03-stakeholders-and-roles.md](../docs/BA/03-stakeholders-and-roles.md) | Thêm mới | Dòng 1–54 |
| [docs/BA/04-current-and-target-business-processes.md](../docs/BA/04-current-and-target-business-processes.md) | Thêm mới | Dòng 1–105 |
| [docs/BA/05-business-requirements.md](../docs/BA/05-business-requirements.md) | Thêm mới | Dòng 1–28 |
| [docs/BA/06-functional-requirements.md](../docs/BA/06-functional-requirements.md) | Thêm mới | Dòng 1–38 |
| [docs/BA/07-non-functional-requirements.md](../docs/BA/07-non-functional-requirements.md) | Thêm mới | Dòng 1–30 |
| [docs/BA/08-use-cases-and-user-stories.md](../docs/BA/08-use-cases-and-user-stories.md) | Thêm mới | Dòng 1–87 |
| [docs/BA/09-fraud-taxonomy-and-business-rules.md](../docs/BA/09-fraud-taxonomy-and-business-rules.md) | Thêm mới | Dòng 1–62 |
| [docs/BA/10-data-requirements-and-glossary.md](../docs/BA/10-data-requirements-and-glossary.md) | Thêm mới | Dòng 1–95 |
| [docs/BA/11-acceptance-criteria-and-uat.md](../docs/BA/11-acceptance-criteria-and-uat.md) | Thêm mới | Dòng 1–65 |
| [docs/BA/12-requirements-traceability-matrix.md](../docs/BA/12-requirements-traceability-matrix.md) | Thêm mới | Dòng 1–62 |
| [docs/BA/13-research-and-solution-options.md](../docs/BA/13-research-and-solution-options.md) | Thêm mới | Dòng 1–71 |
| [docs/BA/14-discovery-assumptions-and-risks.md](../docs/BA/14-discovery-assumptions-and-risks.md) | Thêm mới | Dòng 1–81 |
| [docs/BA/15-mvp-roadmap-and-business-case.md](../docs/BA/15-mvp-roadmap-and-business-case.md) | Thêm mới | Dòng 1–77 |
| [docs/BA/16-experience-search-and-evidence-templates.md](../docs/BA/16-experience-search-and-evidence-templates.md) | Thêm mới | Dòng 1–94 |
| [docs/BA/17-prototype-gap-and-transition.md](../docs/BA/17-prototype-gap-and-transition.md) | Thêm mới | Dòng 1–56 |
| [docs/BA/README.md](../docs/BA/README.md) | Thêm mới | Dòng 1–58 |
| [docs/BA/requirements-traceability.csv](../docs/BA/requirements-traceability.csv) | Thêm mới | Dòng 1–23 |
| [docs/BA/uat-scenarios.csv](../docs/BA/uat-scenarios.csv) | Thêm mới | Dòng 1–29 |
