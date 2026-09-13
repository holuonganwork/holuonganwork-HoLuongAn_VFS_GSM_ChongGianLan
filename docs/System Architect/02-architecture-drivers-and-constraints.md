# 02. Động lực kiến trúc và ràng buộc

## Thứ tự ưu tiên

1. Đúng quyền, đúng bằng chứng và đúng trình tự kết luận.
2. Tiếp nhận phản hồi bền vững, giải quyết retry/đồng thời, bảo toàn lịch sử.
3. Tìm kiếm và điều tra hiệu quả trên dữ liệu đủ mới.
4. Vận hành, phục hồi, thay đổi và hiệu chỉnh được với nguồn lực hữu hạn.
5. Tăng tải và thêm ML dựa trên số đo.

Không hy sinh ba mục đầu để tăng throughput. Hết năng lực xử lý thì giữ đầu vào, báo backlog, phân ưu tiên và bổ sung người/năng lực; không tự đóng hồ sơ hoặc kết luận để giảm hàng đợi.

## Giả định thiết kế có thể thay đổi

| ID | Giả định SA 1.0 | Tác động nếu sai | Người xác minh |
| --- | --- | --- | --- |
| A-01 | Một đơn vị vận hành trong pilot; có `org_id` từ đầu | Nhiều đơn vị cần isolation, identity mapping và kiểm thử tenant trước onboarding | Product/Security |
| A-02 | 1.000 tài xế, 10.000 chuyến/ngày, 60 GPS/chuyến | Điều chỉnh partition, ingest window, worker và chi phí | Data |
| A-03 | 20 phiên tìm kiếm + 50 phiên tài xế theo BA | Điều chỉnh connection budget, tài nguyên API và UX mạng yếu | Tech Lead |
| A-04 | Tìm trực tuyến 30 ngày; lưu thực tế cấu hình riêng | Cửa sổ dài tăng DB/index; retention chưa chốt chặn purge thật | Data/Product |
| A-05 | Có IdP và ánh xạ tài khoản–tài xế đáng tin cậy | Xây adapter onboarding/verification trước mở portal | Identity owner |
| A-06 | Có ít nhất hai người đủ quyền điều tra/duyệt; người xử lý khiếu nại độc lập với vòng trước | Không thể hoàn tất luồng có phân tách trách nhiệm; cần phân công nhân sự | Risk |
| A-07 | Batch p95 ≤30 phút đủ cho pilot | Yêu cầu quyết định trực tuyến cần contract latency mới và ADR khác | Product/Data |
| A-08 | Có dịch vụ PostgreSQL HA, object storage và kênh thông báo đáp ứng yêu cầu triển khai | Nếu on-prem, phải cộng chi phí backup, vận hành, scanner, HA vào phương án | Operations |

Các giả định này cụ thể hóa [BA discovery](../BA/14-discovery-assumptions-and-risks.md); không thay những quyết định nghiệp vụ DEC đang mở ở đó.

## Kịch bản chất lượng quyết định cấu trúc

| ASR | Tình huống → đáp ứng cần thiết | Cơ chế | NFR |
| --- | --- | --- | --- |
| ASR-01 | Tài xế thay ID hoặc mở link tải cũ → không thấy hồ sơ/metadata trái quyền | Policy ở query và command; publication projection; download qua gateway kiểm quyền lại | NFR-01, 02 |
| ASR-02 | Mạng mất sau commit phản hồi → retry nhận lại cùng biên nhận | Idempotency record + response + audit trong một transaction | NFR-04, 09 |
| ASR-03 | Phản hồi đến lúc người duyệt bấm xác nhận → chỉ duyệt tập thông tin đã kiểm | Case version, khóa ngắn, invalidation proposal, luồng xem xét lại sau commit | NFR-04, 10 |
| ASR-04 | Nguồn bị sửa sau kết luận → vẫn mở được nội dung từng dùng và thấy đính chính | Source/evidence version bất biến, manifest, impact task | NFR-03, 11 |
| ASR-05 | Batch quá tải hoặc thiếu GPS → hiển thị nguồn trễ/không đánh giá được | Watermark từng nguồn, quality status, bounded worker và backpressure | NFR-06, 11 |
| ASR-06 | PostgreSQL hỏng → phục hồi dữ liệu/tệp và đối soát biên nhận | PITR, backup tách quyền, inventory object, receipt ledger | NFR-07, 12 |
| ASR-07 | Người dùng hết quyền trong lúc search/export → dữ liệu chưa giao phải bị chặn | Auth epoch, kiểm lại job và download, invalidate search session | NFR-01, 02 |
| ASR-08 | Thay rule/model → lịch sử không thay, thử nghiệm không gửi thông báo thật | Version registry, snapshot, shadow namespace, consumer allowlist | NFR-11, 12 |

## Các mục tiêu đo

| Thuộc tính | Mục tiêu P1 theo BA |
| --- | --- |
| Sẵn sàng | ≥99,5% theo tháng, tính cả bảo trì trong thời gian quan sát |
| Phục hồi | RPO ≤15 phút; RTO ≤4 giờ; đối soát giao dịch sau mốc khôi phục |
| Tìm kiếm | p95 ≤3 giây mã/bộ lọc; ≤5 giây văn bản, trang đầu 50 kết quả |
| Biểu mẫu chữ | p95 ≤2 giây, không tính upload hoặc nhà cung cấp thông báo |
| Độ mới nguồn | Chuyến hoàn tất → sẵn sàng tìm p95 ≤30 phút |
| Độ mới hồ sơ | Lưu → đọc lại ≤5 giây; API chi tiết ưu tiên primary |
| Thu hồi quyền | Có hiệu lực ≤5 phút trên API, search, export, tệp |
| Tệp | JPG/PNG/PDF ≤10 MB/tệp, ≤5 tệp/lần; cách ly và quét |
| Audit/integrity | 100% thao tác bắt buộc có audit; 100% evidence viện dẫn khi duyệt có nguồn/version/hash hợp lệ |

Cách lấy mẫu, SLI và tải chi tiết ở [10](10-performance-scalability-and-reliability.md); nguồn yêu cầu là [NFR BA](../BA/07-non-functional-requirements.md). Đây là mục tiêu chưa benchmark, không phải thông số đã chứng minh của stack.

## Tối ưu tổng chi phí

TCO tháng = compute API/worker + PostgreSQL/HA/IOPS + object/backup/egress + IdP/thông báo + monitoring + chi phí trực vận hành. Chi phí trên 1.000 chuyến = chi phí phân bổ kỳ / số chuyến hợp lệ kỳ ×1.000. Chi phí trên hồ sơ đã giải quyết bao gồm giờ điều tra/duyệt, tách khỏi chi phí máy chủ.

Không gán giá cloud khi chưa có nhà cung cấp, vùng dữ liệu, hợp đồng và retention. Dùng ba kịch bản tải ở tài liệu 10, đo byte thực tế và thời gian worker, rồi lập dự toán. Ưu tiên dịch vụ doanh nghiệp sẵn có nếu thỏa contract; tránh vận hành hai broker hoặc hai kho tìm kiếm cùng mục đích trong P1.

## Ràng buộc đối với lựa chọn công nghệ

- Giữ Python cho rule/data và API hiện tại; phiên bản triển khai phải được khóa, cập nhật bảo mật và kiểm tương thích theo CI.
- PostgreSQL giữ nguồn sự thật về workflow; kho search/cache chỉ là bản dẫn xuất, có thể dựng lại.
- Không gọi IdP, scanner, object store hay kênh thông báo trong transaction đang khóa case. Chuẩn bị bên ngoài rồi kiểm version và commit ngắn.
- Trạng thái model unknown phải biểu diễn được; dữ liệu không có khác với đánh giá không có dấu hiệu.
- Khu vực dữ liệu, căn cứ xử lý và lịch lưu do đầu mối có thẩm quyền xác nhận trước pilot; SA không tự ấn định nghĩa vụ pháp lý hoặc thời hạn lưu.

Mọi quyết định hạ tầng mới phải trả lời: giải quyết nút thắt nào, đo trước/sau ra sao, ai vận hành, phục hồi bằng gì và cách rút lại. Xem [ADR-002/003/008/010](12-architecture-decision-records.md).
