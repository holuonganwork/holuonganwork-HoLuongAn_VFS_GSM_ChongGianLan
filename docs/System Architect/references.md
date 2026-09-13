# Nguồn tham khảo và giới hạn áp dụng

Nguồn sơ cấp được truy cập/đối chiếu ngày **14/09/2026**. Bài engineering lịch sử mô tả thiết kế tại thời điểm công bố; tài liệu sản phẩm mô tả tính năng được công khai. Không có quyền truy cập kiến trúc nội bộ hiện tại của Uber/Stripe/Google/AWS hoặc hệ thống thật của VFS/GSM. Các lựa chọn, sizing và ngưỡng vận hành trong SA là đề xuất của dự án, không phải số đo vay mượn từ các công ty này.

| ID | Nguồn | Điều học được / nơi áp dụng | Giới hạn |
| --- | --- | --- | --- |
| S-01 | [Uber — Mastermind](https://www.uber.com/gb/en/blog/mastermind/), 08/03/2017 | Rule governance, evaluate/shadow và tách xử lý feature/model; tài liệu 01/06 | Không sao chép hành động ban/chặn hoặc performance công bố; không coi là kiến trúc Uber hiện hành |
| S-02 | [Uber — Risk Entity Watch](https://www.uber.com/us/en/blog/risk-entity-watch/), 28/09/2023 | Anomaly/entity features và người review kết quả; 06/11 | Anomaly khác nhãn gian lận; không chứng minh graph/unsupervised model cần thiết cho pilot |
| S-03 | [Uber — Michelangelo](https://www.uber.com/us/en/blog/michelangelo-machine-learning-platform/), 05/09/2017 | Vòng đời ML, feature/data pipeline có thể tái lập; 11 | Áp dụng nguyên tắc và contract, không dựng toàn stack ML quy mô Uber |
| S-04 | [Stripe — Risk insights](https://docs.stripe.com/radar/reviews/risk-insights) | Trình bày tín hiệu/risk context để review; 01 | Thanh toán khác điều tra tài xế; không mang threshold hoặc retention sản phẩm sang dự án |
| S-05 | [Google SRE — Implementing SLOs](https://sre.google/workbook/implementing-slos/) | SLI theo người dùng, error budget và ưu tiên độ tin cậy; 01/10 | SLO 99,5% và budget policy của SA lấy từ BA/đề xuất, không phải cam kết của Google |
| S-06 | [AWS — Transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html) | Domain write + outbox cùng transaction, consumer idempotent; 04/07/12 | Không suy exactly-once qua DB/broker/provider; không bắt buộc dùng AWS |
| S-07 | [PostgreSQL 16 — Table partitioning](https://www.postgresql.org/docs/16/ddl-partitioning.html) | Partition/pruning và ràng buộc unique có partition key; 05/10 | Tần suất partition và sizing phải benchmark workload GPS |
| S-08 | [PostgreSQL 16 — Row security policies](https://www.postgresql.org/docs/16/ddl-rowsecurity.html) | RLS và ngoại lệ owner/superuser/BYPASSRLS; 08 | Không thay field policy, identity, object scope và kiểm quyền ứng dụng |
| S-09 | [PostgreSQL 16 — Continuous archiving/PITR](https://www.postgresql.org/docs/16/continuous-archiving.html) | Base backup, WAL và phục hồi theo thời điểm; 09 | DB PITR không tự khôi phục object, identity, receipt và deletion ledger |
| S-10 | [PostgreSQL 16 — SELECT](https://www.postgresql.org/docs/16/sql-select.html) | Row locking và `SKIP LOCKED` cho bảng công việc; 04 | Lease/fencing/idempotency là thiết kế bổ sung, không do SELECT tự bảo đảm |
| S-11 | [PostgreSQL 16 — pg_trgm](https://www.postgresql.org/docs/16/pgtrgm.html) | Index hỗ trợ các kiểu tìm chữ thích hợp; 05 | Cần dữ liệu tiếng Việt và query benchmark, không mặc định mọi query dùng index |
| S-12 | [PostgreSQL 16 — unaccent](https://www.postgresql.org/docs/16/unaccent.html) | Chuẩn hóa dấu trong pipeline tìm kiếm; 05 | Phải kiểm `đ`, Unicode, mã định danh và version normalization |
| S-13 | [OWASP — File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html) | Kiểm upload nhiều lớp, nơi lưu và xử lý tệp; 08 | Scanner không chứng nhận tuyệt đối tệp vô hại; giới hạn 10 MB/5 tệp là từ BA |
| S-14 | [Amazon S3 — Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html) | Hiểu khả năng retention/hold của kho hỗ trợ WORM; 05 | S3-compatible không tự tương đương; cần chốt policy trước bật khóa không thể rút |
| S-15 | [IETF — RFC 9700, OAuth 2.0 Security BCP](https://datatracker.ietf.org/doc/html/rfc9700), 01/2025 | Cơ sở chọn authorization code/PKCE và bảo vệ token; 08 | IdP/OIDC/session cần cấu hình, threat review và test riêng |
| S-16 | [OpenTelemetry — Signals](https://opentelemetry.io/docs/concepts/signals/) | Chuẩn hóa telemetry qua SDK/collector; 11 | Không coi telemetry sampled là audit đầy đủ hoặc tự đáp ứng SLO |

## Căn cứ trong repository

| Nguồn | Dùng để xác minh |
| --- | --- |
| [README](../../README.md), [architecture](../architecture.md) | Luồng prototype, stack và các phần chưa triển khai |
| [BA README](../BA/README.md), [phạm vi](../BA/02-scope-and-boundaries.md), [FR](../BA/06-functional-requirements.md), [NFR](../BA/07-non-functional-requirements.md) | Yêu cầu đích, tải pilot và cổng chất lượng |
| [BA workflow](../BA/04-current-and-target-business-processes.md), [gap](../BA/17-prototype-gap-and-transition.md) | Trạng thái, delivery/SLA, appeal và xung đột baseline |
| [BA UAT](../BA/11-acceptance-criteria-and-uat.md), [traceability](../BA/12-requirements-traceability-matrix.md) | Kịch bản kiểm chứng cần có, chưa phải kết quả thực thi |
| [API](../../backend/app/api/routes.py), [models](../../backend/app/models/entities.py) | Endpoint, unique/FK, enum và cấu trúc đang tồn tại |
| [Detection service](../../backend/app/services/detection.py), [case service](../../backend/app/services/cases.py) | Transaction, fingerprint, quyết định cuối và lịch sử |
| [Providers](../../backend/app/fraud/providers.py), [correlation](../../backend/app/fraud/correlation.py), [observations](../../backend/app/processing/observations.py) | Adapter rule, giới hạn batch và tương quan trong lần chạy |
| [Frontend](../../frontend/README.md), [Compose](../../docker-compose.yml), [CI](../../.github/workflows/tests.yml) | Dashboard chỉ đọc, local deployment và phạm vi regression hiện có |

Khi triển khai, kiểm lại phiên bản thư viện, tính năng dịch vụ và tài liệu bảo mật ở thời điểm phát hành. Không thay mục tiêu nghiệp vụ chỉ để khớp sản phẩm nhà cung cấp; nếu khác contract thì ghi ADR và phép kiểm tương ứng.
