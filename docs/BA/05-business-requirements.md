# Yêu cầu nghiệp vụ

Các yêu cầu là baseline đề xuất cho sản phẩm đích. “Must” là bắt buộc để gọi là MVP phối hợp tài xế–kiểm soát; không có nghĩa prototype hiện tại đã đáp ứng. Mã OBJ tham chiếu [mục tiêu](01-business-context-and-objectives.md).

| Mã | Yêu cầu và giá trị cần tạo | Điều kiện đáp ứng nghiệp vụ | Ưu tiên | Chủ sở hữu | Mục tiêu |
| --- | --- | --- | --- | --- | --- |
| BR-01 | Hợp nhất thông tin sự việc để giảm công tìm dữ liệu | Tìm từ mã tài xế/chuyến/hồ sơ đến bằng chứng gốc trong phạm vi quyền; phân biệt dữ liệu thiếu với không có kết quả | Must | Trưởng kiểm soát | OBJ-01 |
| BR-02 | Phát hiện và ưu tiên nghi vấn có thể giải thích | Mỗi cảnh báo có lý do, thời gian, nguồn và phiên bản quy tắc; xếp hàng phù hợp năng lực kiểm tra | Must | Risk Lead | OBJ-03 |
| BR-03 | Bảo đảm căn cứ có thể truy nguyên và kiểm chứng | Người duyệt tái dựng được dữ kiện đã dùng tại thời điểm quyết định; ghi thông tin ủng hộ và phản bác | Must | QA nghiệp vụ | OBJ-02 |
| BR-04 | Cho tài xế cơ hội phản hồi thực chất | Hiểu sự việc, biết cần cung cấp gì, có hạn rõ ràng, gửi được khi mạng yếu và nhận biên nhận | Must | Vận hành tài xế | OBJ-04 |
| BR-05 | Kết luận nhất quán và có trách nhiệm | Phân biệt gian lận, không gian lận, chưa đủ căn cứ; người điều tra không tự duyệt; lưu căn cứ chính sách | Must | Trưởng kiểm soát | OBJ-02 |
| BR-06 | Cho phép kiểm tra lại quyết định | Tài xế nhận lý do/kênh khiếu nại; người độc lập xử lý; lưu phiên bản và kết quả khắc phục | Must | Chủ quy trình khiếu nại | OBJ-02, OBJ-04 |
| BR-07 | Bảo vệ thông tin theo mục đích và quyền | Quyền sở hữu/phân công áp dụng tới mọi điểm truy cập; có lịch lưu và xử lý yêu cầu dữ liệu | Must | Đầu mối bảo vệ dữ liệu | OBJ-02 |
| BR-08 | Kiểm soát tải và tiến độ xử lý | Có owner, hàng đợi, đồng hồ SLA, escalation và báo cáo tồn; không reset hạn khi chuyển người | Must | Trưởng kiểm soát | OBJ-05 |
| BR-09 | Đo chất lượng và giá trị thật | Báo cáo có mẫu số, thời gian, mức thiếu dữ liệu; tách số tiền nghi vấn/xác nhận/thu hồi; có mẫu kiểm tra độc lập | Must | Sponsor và Finance | OBJ-03, OBJ-06 |
| BR-10 | Cải tiến mà giữ được lịch sử và khả năng quay lại | Quy tắc có người duyệt, thời điểm hiệu lực, thử trước; thay đổi không viết lại kết luận cũ | Must | Chủ sản phẩm | OBJ-03, OBJ-05 |

## Các nguyên tắc kinh doanh chi phối

1. **Một nghi vấn không phải một kết luận.** Cảnh báo và phản ánh từ người dùng đều cần kiểm chứng nguồn; không phản hồi cũng không tạo bằng chứng xác nhận.
2. **Quyết định dựa trên quy chế có hiệu lực tại thời điểm sự việc.** Thay đổi chương trình thưởng sau chuyến không được dùng hồi tố nếu quy chế không cho phép; người duyệt phải thấy phiên bản áp dụng.
3. **Một khoản lợi ích chỉ được đếm một lần.** Vụ việc có cả chuyến lặp và khuyến mại không làm số tiền tăng gấp đôi.
4. **Sửa kết luận phải khắc phục tác động đã bàn giao.** Hệ thống tạo tác vụ theo dõi người nhận và xác nhận khắc phục; không coi đổi nhãn là đã hoàn tất.
5. **Dữ liệu thiếu làm tăng nhu cầu xác minh.** Chất lượng dữ liệu không được quy thành lỗi tài xế một cách mặc định.

## Tiêu chí hoàn tất thẩm định BA

BR được xem là đã thống nhất khi có chủ sở hữu, phạm vi, chỉ số/kịch bản kiểm chứng, yêu cầu con truy vết được và các giả định ảnh hưởng đã được quyết định. Tài liệu 12 cung cấp liên kết; tài liệu 14 giữ các điểm cần làm rõ. Chỉ thay trạng thái thành “đã phê duyệt” khi có biên bản thực, ngày và người chấp thuận.
