# 10. Hiệu năng, mở rộng và độ tin cậy

## Mô hình tải có thể tính lại

Giữ giả định BA cho P1, dùng hai kịch bản lớn hơn để kiểm điểm đổi kiến trúc. Đây là kịch bản thiết kế, không mô tả quy mô thực của VFS/GSM.

| Thông số | P1 pilot | Kịch bản ×10 | Kịch bản ×100 |
| --- | ---: | ---: | ---: |
| Tài xế | 1.000 | 10.000 | 100.000 |
| Chuyến/ngày | 10.000 | 100.000 | 1.000.000 |
| GPS/chuyến | 60 | 60 | 60 |
| GPS/ngày | 600.000 | 6.000.000 | 60.000.000 |
| GPS/giây trung bình | 6,94 | 69,44 | 694,44 |
| GPS/giây peak giả định ×10 | 69,44 | 694,44 | 6.944,44 |
| GPS/30 ngày | 18 triệu | 180 triệu | 1,8 tỷ |
| Raw GPS/ngày ở 500 byte/event | 0,30 GB | 3,00 GB | 30,00 GB |
| Raw GPS/30 ngày ở 500 byte/event | 9 GB | 90 GB | 900 GB |

500 byte là giả định payload, chưa gồm tuple/index, JSON wrapping, WAL, replication, backup hoặc artifact. Hệ số DB/index tham chiếu ×3 cho ra 27/270/2.700 GB phần GPS online; phải đo bằng `pg_total_relation_size` và manifest thực. Không lấy các con số này làm quota disk cuối cùng. Attachments tính riêng: số response/ngày ×tệp/response ×byte/tệp ×retention ×replication; worst case một lần gửi là 50 MB theo BA.

Mỗi batch 5 phút có khoảng 2.083 GPS mới ở tải trung bình P1, nhưng detection đọc cả lookback, không chỉ delta. Tối ưu bằng aggregates theo cửa sổ và incremental recompute đúng incident. Model×rule count, join context và read amplification là tham số bắt buộc của benchmark.

## Năng lực hàng đợi và ngân sách tài nguyên

Tốc độ phục vụ hữu hiệu `mu` phải lớn hơn tốc độ đến `lambda`. Thời gian rút backlog `B / (mu - lambda)` chỉ có nghĩa khi đơn vị công việc giống nhau và mu > lambda. Đo riêng job detection, notification, scan, export; số job không phản ánh chi phí nếu một batch chứa lượng dữ liệu khác nhau.

Budget DB đề xuất: 2 API ×10 connection +2 worker ×5 +10 dự phòng =40, đối chiếu giới hạn DB; autoscale không được nhân pool vượt budget. Dùng queue admission/backpressure thay vì tạo connection vô hạn. Tách CPU detection, I/O scan/export và các job workflow ưu tiên cao.

Năng lực người cũng là nút thắt. Ví dụ giả định 10 người ×6 giờ xử lý/ngày ×60 /20 phút mỗi case =180 case/ngày trước thời gian duyệt. Nếu proposal cần 10 phút duyệt thì tổng giờ điều tra + duyệt phải tính chung hoặc có nhóm người bổ sung. Tỷ lệ tạo case phải được đo, không đặt tùy ý để khớp năng lực bằng cách tự bỏ nghi vấn.

## SLI/SLO

| SLI | Cách đo và mục tiêu P1 | Cảnh báo/đáp ứng |
| --- | --- | --- |
| Availability hành trình | Probe đăng nhập/xem publication/gửi chữ/xem hàng đợi/duyệt bằng tài khoản test; good minutes / observed minutes ≥99,5% từng hành trình | Critical incident khi gửi/duyệt mất; không để trung bình API che hỏng portal |
| Search latency | p95 first page gồm query/snapshot/serialization ≤3s exact/filter, ≤5s text | Phân loại warm/cold, query shape, tenant và data size |
| Form latency | p95 API gửi chữ đến receipt commit ≤2s; đo client network riêng | Kiểm lock wait/pool/DB, ưu tiên workflow queue |
| Source freshness | Completed trip event time → searchable p95 ≤30 phút; đo source delay, ingest, processing, index riêng | Cảnh báo watermark/oldest unprocessed age, nguồn im lặng |
| Case freshness | Commit → đọc thấy đúng version ≤5s | Chi tiết/receipt đọc primary; báo lag projection |
| Authorization revocation | Thời điểm thay quyền → mọi đường đọc/ghi/tải từ chối ≤5 phút | Cảnh báo auth cache/invalidation lỗi |
| RPO/RTO | Recovery point gap ≤15 phút; phục hồi hành trình ≤4h qua diễn tập | Cảnh báo WAL/object/receipt backup lag; đối soát phần thiếu |
| Integrity | 100% decision evidence verified, 100% command bắt buộc có audit | Một vi phạm mở incident; không lấy mẫu để gọi là đủ |

Availability tính cả bảo trì và lỗi phụ thuộc mà người dùng chịu. Probe không tạo quyết định thật: tenant tổng hợp cô lập, không notification live. Error rate request là SLI bổ sung, không thay availability theo thời gian của BA. Lỗi 4xx hợp lệ tách khỏi 5xx/timeout; lỗi auth do cấu hình hệ thống vẫn tính thất bại hành trình.

Với tháng giả định 30 ngày, error budget của 99,5% là 216 phút. Chính sách đề xuất: cháy >25% budget trong 24 giờ hoặc >50% trong 7 ngày thì ưu tiên ổn định và dừng thay đổi không cấp thiết trên luồng bị ảnh hưởng; outage gửi phản hồi/duyệt cần xử lý ngay bất kể budget. Tháng thực dùng số phút thực tế; pilot ngắn báo đúng khoảng quan sát. Cách dùng SLO làm quyết định lấy cảm hứng từ [Google SRE](https://sre.google/workbook/implementing-slos/), còn ngưỡng này là đề xuất của dự án.

## Tối ưu theo thứ tự

1. Query theo ID/window, projection nhỏ, index theo kế hoạch truy vấn; bỏ full scan và N+1. Không nạp toàn bộ trips/GPS bằng loader prototype.
2. Partition/pruning, cursor, batch checkpoint, feature aggregates được đối soát với phép tính gốc.
3. Worker process riêng, limit concurrency và connection budget, tăng tài nguyên DB khi số đo cho thấy cần.
4. Cache dữ liệu ít nhạy cảm/versioned, replica cho report/read cho phép stale; không dùng replica lag cho duyệt, quyền, receipt.
5. Tách search/analytics và thêm broker/stream khi lợi ích vượt chi phí vận hành.

## Trigger mở rộng cụ thể

| Bổ sung | Trigger đề xuất để mở ADR | Điều kiện hoàn thành |
| --- | --- | --- |
| Broker quản lý, ưu tiên Kafka nếu cần event log replay nhiều consumer | Outbox/jobs chiếm >20% DB I/O hoặc lag vi phạm freshness kéo dài sau tuning; hoặc ≥3 consumer độc lập cần replay dài | Benchmark, retention/partition key, inbox/dedup, schema compatibility, DLQ, owner trực |
| Stream processor | Batch không đạt freshness mới do nghiệp vụ yêu cầu tính cửa sổ liên tục dưới phút | Event time/watermark/state recovery, late correction và đối soát batch |
| Search engine riêng | Text search vượt p95 trên dữ liệu/đồng thời đã chốt sau index/query tuning, hoặc cần analyzer tính năng PostgreSQL không đáp ứng | ACL trước count/snippet, PIT/snapshot, deletion, reindex, query parity |
| Analytical store | Report/training làm ảnh hưởng OLTP hoặc dữ liệu dài hạn vượt online | Export/CDC theo cutoff, access control và label lineage |
| Tách detection service | CPU/scale/release/owner khác core gây contention hoặc deploy coupling rõ | Contract ổn định, không ghi bảng case trực tiếp, shadow/canary |
| Kubernetes / nhiều vùng chủ động | Đã có platform team/chuẩn doanh nghiệp hoặc SLO/DR được nâng và chứng minh runtime hiện tại không đáp ứng | TCO, on-call, failover/fencing, data residency; ADR riêng |

Các tỷ lệ/consumer count là tín hiệu xem xét, không lệnh tự động mua hạ tầng. 18 triệu GPS tự nó không chứng minh cần Kafka; cần đo event rate, replay và workload truy vấn.

## Chế độ suy giảm

| Sự cố | Hành vi thiết kế |
| --- | --- |
| DB primary mất | API ghi trả 503, không cấp receipt giả; client retry cùng key khi hồi; failover theo runbook |
| Ingest nguồn trễ | Hiển thị watermark/quality; công việc dựa nguồn thiếu bị block; vẫn nhận phản hồi |
| Worker chết sau commit trước ACK | Lease expiry/retry, inbox/unique key ngăn tác động lặp |
| Object/scanner lỗi | Nhận phần chữ, giữ tệp pending; chặn duyệt cần tệp trọng yếu; tải thiếu báo unavailable |
| Notification lỗi | Request đã lưu, delivery pending/unknown; chưa tính hạn phản hồi; tạo task hỗ trợ |
| Search lỗi/trễ | Detail theo ID từ primary nếu có quyền; trang tìm kiếm báo chưa khả dụng, không zero giả |
| IdP/quyền không kiểm được | Chặn thao tác bảo vệ; session còn hợp lệ chỉ dùng khi policy thu hồi vẫn được kiểm trong giới hạn |
| Model lỗi/drift | Rule-only assessment với capability thiếu; vẫn review; không tự tăng quyền policy |
| Audit DB ghi lỗi | Rollback command; đọc nhạy cảm từ chối nếu không ghi audit được |
| Telemetry exporter lỗi | Business tiếp tục khi audit bền vững; buffer có giới hạn và báo mất telemetry |

## Kế hoạch benchmark và fault injection

Dữ liệu P1: 300.000 trips/18 triệu GPS, phân phối lệch có hot driver/device, source gaps/late/correction và hồ sơ có tệp. 20 phiên tìm +50 phiên tài xế, 2 Mbps/200 ms cho mobile. Ít nhất 1.000 query hỗn hợp sau warm-up; báo cold cache riêng. So kết quả với expected query sets trước so tốc độ.

Chạy tải steady đề xuất 60 phút, burst ×10 ở ingestion, soak 8 giờ để phát hiện memory/lease/backlog. Đo histogram p50/p95/p99, error rate, CPU/RSS/IOPS/DB size/lock, source-to-search và drain time. Các thời lượng là kế hoạch implementation, chưa thực thi trong đợt tài liệu này.

Fault tests tập trung mất mạng sau commit, kill worker sau publish, hai approver, response sát deadline, mất scanner/IdP, DB restore với object thiếu, quyền thu hồi giữa export. Cổng pass dựa trên invariant + SLO, không chỉ HTTP 200. Không benchmark production thật nếu chưa có môi trường/phạm vi được phép.
