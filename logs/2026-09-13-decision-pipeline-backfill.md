# Ghi bù triển khai luồng cảnh báo, quyết định và review nội bộ

- Thời gian đối chiếu, ghi bù: **13/09/2026 02:48:31 (UTC+7)**.
- Thời gian thực hiện ban đầu: **chưa xác định**; không suy đoán từ giờ sửa file.
- Mã tham chiếu nội bộ: `BACKFILL-20260913-DECISION-PIPELINE`.
- Mốc đối chiếu: `d144d90` — commit cuối đã có trước các thay đổi này.
- Phạm vi: **30 file chưa commit**, gồm 19 file đã sửa và 11 file mới. Hai tài
  liệu phương án/review được ghi riêng trong [log tài liệu](2026-09-13-architecture-documents-backfill.md).
- Đây là bản ghi hồi cứu tổng hợp từ code và Git diff; không xác định tác giả,
  số phiên chat hay thứ tự thực hiện từng thay đổi khi chưa có bằng chứng.

## Mục tiêu công việc

Chuyển bộ khung FastAPI/PostgreSQL sang luồng tách Signal → Alert → Decision →
Case, có chính sách quyết định và review nội bộ, đồng thời giữ khả năng đọc dữ
liệu điều tra cũ. Những nội dung dưới đây mô tả code hiện có trong workspace.

## Công việc thực hiện và đầu ra đã có

### 1. Tách xử lý dữ liệu, phát hiện và đánh giá

- Tách loader dữ liệu thành `processing/observations.py`; engine điều phối các
  bước load observations, detect, correlation, assess và xử lý alert.
- Thêm giao diện `Detector`, `RiskAssessor` cùng adapter sử dụng bốn detector
  quy tắc hiện có. Chưa có mô hình ML hoặc ensemble thực tế trong các adapter này.
- Thêm contract `Assessment` và `AlertCandidate`. Risk score, fraud probability,
  confidence, impact và model version được lưu thành các trường riêng.
- Thêm taxonomy cho Signal, Alert và Case. Correlation gom các tín hiệu có chung
  bằng chứng chuyến/GPS; tách sự việc không liên quan của cùng tài xế và loại tín
  hiệu trùng. Chỉ chung danh tính tài xế, thiết bị hoặc khuyến mãi không đủ để gộp.
- Mở rộng kết quả batch và CLI với số alert mới/cũ, Auto Clear, Auto Fraud và
  Human Review; bộ đếm outcome chỉ tính các quyết định mới được lưu.

### 2. Thêm policy và lưu snapshot quyết định

- Có `DecisionPolicyConfig`, enum outcome/impact/actor và hàm đánh giá policy.
  Ngưỡng minh họa: confidence tối thiểu 0,90; Auto Clear cần probability ≤0,10
  và risk ≤20; Auto Fraud cần probability ≥0,95. Nhánh tự động yêu cầu impact thấp.
- Impact cao/critical/không biết, tín hiệu mâu thuẫn, thiếu probability/confidence
  hoặc confidence thấp sẽ vào Human Review.
- Adapter quy tắc chỉ cung cấp risk; probability/confidence để trống và impact
  là unknown. Vì vậy đường chạy mặc định vẫn đưa cảnh báo vào Human Review.
- Có service lưu Alert, DecisionResult và Case tùy outcome trong cùng giao dịch:
  Auto Clear giữ alert mà không tạo case; Auto Fraud tạo case kết thúc cùng quyết
  định của hệ thống; Human Review tạo case chờ review.
- Fingerprint bao gồm tín hiệu, correlation, cấu hình quy tắc, assessment và policy.
  Code giữ cơ chế khóa tài xế, chống trùng và giữ nguyên các snapshot đã có khi chạy lại.
- Model/migration bổ sung `fraud_alerts`, `decision_results`, `fraud_cases.alert_id`
  và `case_decisions.actor_type`. Model hiện định nghĩa 14 bảng ứng dụng. Có migration
  `0002_alert_decisions` với upgrade/downgrade; chưa xác minh migration đã áp dụng
  vào database đang chạy tại thời điểm ghi bù.

### 3. Cập nhật API và review nội bộ

- Thêm `GET /fraud-alerts`, `GET /fraud-alerts/{alert_id}` và `GET /review-queue`.
  Danh sách alert có lọc theo outcome/tài xế; hàng đợi ưu tiên risk cao.
- Case detail bổ sung alert và kết quả policy; schema quyết định có actor type.
- Bỏ endpoint, request schema và service ghi giải trình mới. Giải trình cũ vẫn
  đọc được; case cũ chờ giải trình có thể trở lại review nội bộ.
- Giữ kiểm tra chuyển trạng thái, khóa case, quyết định cuối và audit. Các nhánh
  quyết định không cập nhật trạng thái tài xế trong code đã đối chiếu.
- Metadata FastAPI được cập nhật lên phiên bản `0.2.0`.

### 4. Cập nhật kiểm thử, cấu hình và tài liệu vận hành

- Thêm test cho policy, validation, correlation, các nhánh lưu quyết định/API,
  chạy lại, nhiều sự việc, rollback, đổi policy và khả năng xử lý case cũ.
- Điều chỉnh test API/workflow/PostgreSQL cho review nội bộ; thêm test migration
  giữ nguyên giải trình, quyết định và case lịch sử khi nâng cấp.
- Bổ sung ví dụ `DECISION_POLICY` trong `.env.example`; CLI nhận policy từ settings.
- Cập nhật README, tài liệu kiến trúc và data model. Implementation plan cũ được
  đánh dấu là tài liệu lịch sử và dẫn đến kiến trúc chuyển tiếp hiện hành.

## Trạng thái kiểm chứng và phần chưa triển khai

Đã kiểm tra nội dung file và diff so với `d144d90`; chưa có bằng chứng được đối
chiếu trong lượt ghi bù này về việc chạy test, lint, migration hoặc triển khai
dịch vụ cho bộ thay đổi mới. Không dùng kết quả **101 tests passed** của đợt commit
trước để gán trạng thái kiểm thử đạt cho code này. Việc có file test chỉ xác nhận
test đã được viết; không xác nhận test đã chạy thành công.

Vẫn là ứng dụng đồng bộ, xử lý dataset nhỏ trong RAM. Các phần ML thực, streaming,
broker/worker, Redis, object storage, frontend và việc tách Java/microservices
chưa được triển khai trong bộ file đối chiếu. Đây là bộ khung chuyển tiếp hiện có.

## File và dòng thay đổi so với `d144d90`

Số dòng mới được tính tại lúc đối chiếu; phần đã xóa dùng số dòng cũ trong commit
gốc. Đây là diff tổng hợp của các thay đổi chưa commit, không phải lịch sử theo
từng lượt chat. Các phạm vi dòng được đối chiếu bằng Git.

| Thao tác | File | Dòng thay đổi |
| --- | --- | --- |
| Sửa | [.env.example](../.env.example#L1) | Thêm/sửa dòng 10 |
| Sửa | [README.md](../README.md#L1) | Thêm/sửa dòng 3–4; 6–7; 12–16; 19–23; 25–32; 72–73; 116–119; 129–131; 141; 147–151; 155–156; 159; 173–180; 195; 210–211; 243–244. Xóa dòng cũ 115–116 |
| Sửa | [backend/app/api/routes.py](../backend/app/api/routes.py#L1) | Thêm/sửa dòng 8; 11–12; 22; 97–99; 102–121. Xóa dòng cũ 17–18 |
| Sửa | [backend/app/core/config.py](../backend/app/core/config.py#L1) | Thêm/sửa dòng 44–60; 66 |
| Sửa | [backend/app/core/enums.py](../backend/app/core/enums.py#L1) | Thêm/sửa dòng 11–43; 45 |
| Sửa | [backend/app/fraud/engine.py](../backend/app/fraud/engine.py#L1) | Thêm/sửa dòng 1–2; 8–11; 13–15; 22–30; 34; 40–45; 47–55; 57; 60–68; 70–93. Xóa dòng cũ 4; 7; 28–33 |
| Sửa | [backend/app/fraud/types.py](../backend/app/fraud/types.py#L1) | Thêm/sửa dòng 3; 5; 26–30 |
| Sửa | [backend/app/main.py](../backend/app/main.py#L1) | Thêm/sửa dòng 21–22 |
| Sửa | [backend/app/models/entities.py](../backend/app/models/entities.py#L1) | Thêm/sửa dòng 21–31; 144–189; 197–199; 217–220; 276–277; 296–300 |
| Sửa | [backend/app/schemas/api.py](../backend/app/schemas/api.py#L1) | Thêm/sửa dòng 6–17; 76; 89–122; 126–127; 138; 141. Xóa dòng cũ 8–10; 100–104 |
| Sửa | [backend/app/services/cases.py](../backend/app/services/cases.py#L1) | Thêm/sửa dòng 10; 32–34; 49; 103–121. Xóa dòng cũ 29–35; 121–124 |
| Sửa | [backend/tests/test_api.py](../backend/tests/test_api.py#L1) | Thêm/sửa dòng 32; 34–40; 99; 113 |
| Sửa | [backend/tests/test_migrations.py](../backend/tests/test_migrations.py#L1) | Thêm/sửa dòng 8; 10–13; 45–114 |
| Sửa | [backend/tests/test_postgres.py](../backend/tests/test_postgres.py#L1) | Xóa dòng cũ 109–121 |
| Sửa | [backend/tests/test_workflow.py](../backend/tests/test_workflow.py#L1) | Thêm/sửa dòng 67; 87. Xóa dòng cũ 11; 13; 61–62; 67; 76–77; 92; 97–98 |
| Sửa | [docs/architecture.md](../docs/architecture.md#L1) | Thêm/sửa dòng 1; 3–6; 9–26; 29; 31; 33–103; 107–110; 115–126; 128–133; 135–139; 141–144; 146–159 |
| Sửa | [docs/data-model.md](../docs/data-model.md#L1) | Thêm/sửa dòng 3–4; 15–17; 21; 50–52; 55–56; 71–86; 102 |
| Sửa | [docs/implementation-plan.md](../docs/implementation-plan.md#L1) | Thêm/sửa dòng 3–6 |
| Sửa | [scripts/run_fraud_detection.py](../scripts/run_fraud_detection.py#L1) | Thêm/sửa dòng 1; 21 |
| Thêm mới | [backend/alembic/versions/0002_alert_decisions.py](../backend/alembic/versions/0002_alert_decisions.py#L1) | Toàn file, dòng 1–170 |
| Thêm mới | [backend/app/decision/__init__.py](../backend/app/decision/__init__.py#L1) | Toàn file, dòng 1 |
| Thêm mới | [backend/app/decision/policy.py](../backend/app/decision/policy.py#L1) | Toàn file, dòng 1–32 |
| Thêm mới | [backend/app/fraud/contracts.py](../backend/app/fraud/contracts.py#L1) | Toàn file, dòng 1–25 |
| Thêm mới | [backend/app/fraud/correlation.py](../backend/app/fraud/correlation.py#L1) | Toàn file, dòng 1–62 |
| Thêm mới | [backend/app/fraud/providers.py](../backend/app/fraud/providers.py#L1) | Toàn file, dòng 1–37 |
| Thêm mới | [backend/app/processing/__init__.py](../backend/app/processing/__init__.py#L1) | Toàn file, dòng 1 |
| Thêm mới | [backend/app/processing/observations.py](../backend/app/processing/observations.py#L1) | Toàn file, dòng 1–39 |
| Thêm mới | [backend/app/services/alerts.py](../backend/app/services/alerts.py#L1) | Toàn file, dòng 1–33 |
| Thêm mới | [backend/app/services/detection.py](../backend/app/services/detection.py#L1) | Toàn file, dòng 1–156 |
| Thêm mới | [backend/tests/test_decision_pipeline.py](../backend/tests/test_decision_pipeline.py#L1) | Toàn file, dòng 1–228 |

## Kiểm tra nhật ký trong lần ghi bù này

- Bổ sung hash, thời gian và kết quả hoàn tất vào log commit cũ, cập nhật dòng
  tổng quan tương ứng thay vì tạo dòng trùng cho cùng công việc.
- Tạo hai log hồi cứu, ghi nhận đủ 32 file có thay đổi trước lúc bắt đầu bổ sung:
  hai tài liệu phương án/review và 30 file triển khai chuyển tiếp.
- Giữ nguyên nội dung 32 file nguồn; chỉ cập nhật worklog và các file nhật ký.
- Phạm vi xác minh của lần ghi bù là lịch sử Git, cấu trúc bảng, tham chiếu file
  và số dòng. Không chạy lại backend hoặc áp dụng migration khi ghi nhật ký.

## Bổ sung kiểm chứng lúc 13/09/2026 15:45:49 (UTC+7)

- Đối chiếu snapshot lưu từ lần ghi bù trước: **30/32 file nguồn giữ nguyên hash**.
  `README.md` bổ sung 18 dòng ròng cho frontend và phạm vi hiện hành, được ghi riêng tại
  [log frontend](2026-09-13-frontend-backfill.md). `backend/app/main.py` chỉ khác kiểu xuống dòng so với snapshot cũ.
- `.venv/Scripts/python.exe -m pytest -q -ra`: **125 đạt, 3 bỏ qua, 2 cảnh báo deprecation**.
  Ba test bỏ qua thuộc PostgreSQL vì chưa đặt `TEST_DATABASE_URL`; thử kết nối database
  kiểm thử riêng `fraud_investigation_tests` tại `127.0.0.1`, timeout 5 giây, không thành công.
  Không áp dụng migration lên database ứng dụng. Các test migration dùng SQLite đã chạy trong suite.
- `.venv/Scripts/python.exe -m ruff check backend scripts`: **đạt**.
- `.venv/Scripts/python.exe -m ruff format --check backend scripts`: **54 file đạt**.
- API thật còn được dùng trong **9 test E2E frontend đạt** với SQLite cô lập; không thay thế
  kiểm chứng PostgreSQL/concurrency. Chi tiết tại [log frontend](2026-09-13-frontend-backfill.md).

Nhận định frontend chưa triển khai trong phần hồi cứu phía trên chỉ áp dụng cho bộ 30 file
ở thời điểm ghi bù cũ. Hiện có frontend độc lập; ML/streaming/broker và các hạ tầng mở rộng
vẫn chưa được xác nhận triển khai. Kết quả commit xem [log tổng hợp](2026-09-13-worklog-audit-and-commits.md).
