# Phân loại nghi vấn và quy tắc nghiệp vụ

## Taxonomy đề xuất

Category mô tả nhóm nghiệp vụ; type mô tả kiểu nghi vấn; signal là quan sát cụ thể. Nhãn dưới đây thể hiện đối tượng điều tra, không tự khẳng định tài xế gian lận. Bốn type đầu khớp [enum hiện có](../../backend/app/core/enums.py).

| Nhóm / type | Giả thuyết và nguồn cần xem | Giải thích hợp lệ cần kiểm tra | Ưu tiên |
| --- | --- | --- | --- |
| Vị trí / `gps_spoofing` | Di chuyển không phù hợp dữ liệu thời gian; cặp GPS, accuracy/provider, thứ tự nhận, trạng thái mạng, log chuyến | Hầm, mất sóng, GPS phục hồi, lệch đồng hồ, dữ liệu đến trễ | MVP |
| Chuyến / `repeated_trips` | Nhiều chuyến ngắn cùng tuyến; chuyến, tọa độ, thời gian, loại dịch vụ | Tuyến đưa đón hợp lệ, điểm trung chuyển, nhu cầu hành khách thật | MVP |
| Tài khoản / `shared_device` | Thiết bị liên quan nhiều tài khoản; lịch sử liên kết và cấp phát thiết bị | Thiết bị đội xe dùng luân phiên, đổi máy, sửa chữa; chưa chứng minh dùng đồng thời | MVP |
| Khuyến mại / `promotion_abuse` | Chùm chuyến có thưởng; chính sách có hiệu lực, tập chuyến mẫu số, eligibility và payout nếu có | Chương trình hợp lệ kích thích nhu cầu, khác phiên bản chính sách | MVP |
| Chuyến / tuyến đường kéo dài | Sai lệch giá cước so tuyến hợp lệ; lộ trình dự kiến, điều chỉnh điểm đến, giao thông | Tắc đường, đường cấm, hành khách yêu cầu | Sau pilot khi có nguồn bối cảnh |
| Tài khoản / giả mạo hoặc chiếm đoạt | Định danh và truy cập bất thường; nguồn xác minh được phép dùng | Đổi thiết bị, tài khoản bị bên khác chiếm đoạt, khôi phục hợp lệ | Sau pilot; không thu sinh trắc học trong MVP |
| Thanh toán / phí không hợp lệ | Phí phát sinh, chứng từ, thanh toán/hoàn tiền | Sửa giao dịch, phí được khách đồng ý, chậm đối soát | Sau pilot có sổ cái |
| Quan hệ / nghi vấn thông đồng | Quan hệ chuyến–tài xế–khách–thiết bị theo thời gian | Cùng hộ gia đình, khách quen, doanh nghiệp đặt xe | Nghiên cứu sau; không suy từ một liên kết |

Uber công bố các ví dụ như thao túng GPS, kéo dài chuyến và chuyến không có thật; đây là tham chiếu phân loại trong thị trường UK, không phải quy chế áp dụng cho đơn vị này. [Nguồn](https://www.uber.com/gb/en/drive/driver-app/fraud-activities/)

## Quy tắc phát hiện hiện có để làm mốc thử nghiệm

Các giá trị dưới đây **chỉ là cấu hình demo đã đọc từ repository**, chưa là ngưỡng sản xuất. Định nghĩa chi tiết và các giới hạn hiện hành ở [fraud-rules.md](../fraud-rules.md) và [config.py](../../backend/app/core/config.py).

| Mã | Logic demo | Bằng chứng phải thể hiện | Điểm và hạn chế |
| --- | --- | --- | --- |
| RULE-01 | Trong cùng chuyến, hai GPS kế tiếp theo ingestion ID; quãng dịch chuyển ≥0,1 km, Δt>0 và tốc độ >180 km/h; nhảy ≥5 km trong ≤60 giây có tên riêng; Δt≤0 xử lý bằng quy tắc thứ tự | Hai bản ghi gốc, thời gian, khoảng cách, đơn vị, cách tính, thứ tự nhận; không chia cho 0 | Nhóm GPS 30 điểm một lần; sai thứ tự có thể do hệ thống |
| RULE-02 | ≥8 chuyến dài ≤1 km, thời lượng >0 và ≤300 giây trong cửa sổ 24 giờ; điểm đón/trả trong 0,2 km so anchor tương ứng | Toàn bộ chuyến khớp, cửa sổ `[start,end)`, hướng tuyến, anchor và độ lệch | 25 điểm; tuyến hợp lệ có thể lặp; demo chỉ giữ nhóm lớn nhất |
| RULE-03 | Thiết bị từng liên kết ≥3 tài xế khác nhau | Các liên kết, first/last seen, lịch sử cấp phát nếu có | 25 điểm; demo không yêu cầu thời gian dùng trùng nhau |
| RULE-04 | Cửa sổ 24 giờ trong kỳ khuyến mại, số chuyến được thưởng ≥max(10, ngưỡng chương trình); tỷ lệ chuyến được thưởng/tất cả chuyến ≥0,8 và chuyến thưởng ngắn/chuyến thưởng ≥0,8 | Tất cả chuyến thuộc mẫu số và các tập con, điều kiện thưởng, số tiền gắn chuyến, phiên bản chính sách | 20 điểm; không chứng minh thưởng đã được chi trả |

Khoảng cách demo là đường chim bay haversine, không phải độ dài đường bộ. Thứ tự ID là giả định của dữ liệu mẫu; mục tiêu dữ liệu thật phải có sequence và thời điểm nhận riêng. Dữ liệu GPS âm thời gian/đến trễ ưu tiên đánh dấu chất lượng trước khi xem là dấu hiệu hành vi.

## Quy tắc xử lý và quyết định đích

| Mã | Quy định nghiệp vụ đề xuất | Ví dụ / hệ quả |
| --- | --- | --- |
| RULE-05 | Điểm tổng = min(100, tổng trọng số của từng nhóm có dấu hiệu, mỗi nhóm tính một lần); tách probability, confidence, impact và quality | Hai evidence GPS vẫn đóng góp 30; 45 điểm không có nghĩa 45% khả năng gian lận |
| RULE-06 | Một hồ sơ theo một tài xế/sự việc; cùng nguồn/snapshot không tạo trùng; sự việc khác không gộp chỉ vì cùng tài xế | Liên kết cross-case nội bộ khi dùng chung thiết bị; không trộn quyền xem |
| RULE-07 | Nguồn thiếu, mâu thuẫn, sai hash hoặc suy luận từ dữ liệu phụ thuộc phải được ghi rõ; cảnh báo chất lượng không là xác nhận hành vi | Hai bản xuất từ cùng điện thoại không là hai nguồn độc lập |
| RULE-08 | Xác nhận gian lận phải thỏa đồng thời: xác định hành vi và căn cứ về yếu tố cố ý/trục lợi không hợp lệ theo tiêu chuẩn quy chế có hiệu lực; có nguồn gốc/toàn vẹn kiểm được; kiểm tra cách giải thích thay thế; đã cho cơ hội giải trình hợp lệ; người khác duyệt | Vi phạm chất lượng hoặc lỗi kỹ thuật không tự là gian lận; một điểm GPS, dùng chung máy hoặc im lặng đơn lẻ không đủ; thiếu điều kiện thì tiếp tục xác minh hoặc `inconclusive` |
| RULE-09 | MVP tự động hóa tổng hợp, ưu tiên và nhắc việc; kết luận có người chịu trách nhiệm; không tự chế tài | Nhánh `auto_fraud` của prototype không được coi là phê duyệt nghiệp vụ cho pilot này |
| RULE-10 | Hạn phản hồi bắt đầu từ giao hợp lệ, không từ gửi; hết hạn không là nhận lỗi; gia hạn/nhắc lặp có audit | Gửi lại thông báo không tự reset hạn |
| RULE-11 | Phân quyền theo danh tính, ownership, phân công, trường dữ liệu và mục đích; tách người đề xuất/duyệt/khiếu nại trên cùng hồ sơ | Bản tài xế được xem không chứa danh tính người khác hoặc ghi chú nội bộ |
| RULE-12 | Bản đã gửi/duyệt không ghi đè; thông tin mới và khiếu nại tạo phiên bản, chỉ rõ bản đang hiệu lực | Khiếu nại sửa kết luận không xóa quyết định cũ |
| RULE-13 | Tiền nghi vấn, xác nhận thiệt hại và thu hồi là ba đại lượng khác; cùng khoản giao dịch không đếm hai lần | Nhiều type trên cùng khoản thưởng chỉ một khoản lợi ích/tổn thất |
| RULE-14 | Chỉ đưa vào tập nhãn dương/âm sau thẩm định độc lập và thời gian hoàn thiện nhãn; loại pending/inconclusive, giữ lý do loại và theo dõi đảo kết luận | Không gán mọi hồ sơ chưa bị phạt thành “không gian lận” |
| RULE-15 | Quy tắc mới cần người duyệt, dữ liệu đánh giá tách biệt và lịch hiệu lực; rollback không viết lại lịch sử | Giữ được vì sao một cảnh báo xuất hiện dưới `demo-v1` |
| RULE-16 | Lưu/giữ/xóa theo mục đích và lịch đã duyệt; hold có căn cứ, owner và ngày rà soát, không lưu vô thời hạn mặc định | Xóa chỉ mục và bản dẫn xuất tương ứng; backup hết hạn theo chính sách |
| RULE-17 | Mọi kết luận phải xét thông tin phản bác; mẫu kiểm tra chất lượng không chỉ lấy hồ sơ đã xác nhận gian lận | Phân tầng theo loại/khu vực/thiết bị; mẫu quá nhỏ chỉ báo thiếu căn cứ đánh giá |
| RULE-18 | Phản ánh của tài xế là nguồn yêu cầu xác minh; chuyển kênh an toàn/chất lượng phù hợp; bảo vệ danh tính người báo khi liên quan bên khác | Biên nhận báo vấn đề không trở thành bằng chứng buộc lỗi |

## Bảng quyết định rút gọn

| Tình huống | Hành động hợp lệ | Hành động bị chặn |
| --- | --- | --- |
| GPS nhảy, thiếu accuracy và có khoảng mất sóng | Xác minh nguồn kỹ thuật, yêu cầu bối cảnh khi cần | Xác nhận gian lận chỉ từ tốc độ |
| Thiết bị cấp lại cho ba tài xế ở ba giai đoạn | Đối chiếu cấp phát và thời gian; đề xuất bác nghi vấn nếu phù hợp | Đồng nhất liên kết lịch sử với thông đồng |
| Dấu hiệu thưởng + chứng từ chi + vi phạm chính sách đã được kiểm + đã xét phản bác | Đề xuất và duyệt độc lập theo RULE-08 | Tự trừ tiền từ giá trị nghi vấn |
| Tài xế chưa trả lời, thông báo lỗi giao | Sửa kênh, hỗ trợ truy cập | Cho hết hạn hoặc ghi nhận thừa nhận |
| Nguồn trọng yếu mâu thuẫn không giải quyết được | `inconclusive`, ghi phần thiếu và điều kiện xem lại | Ép vào một trong hai nhãn dương/âm |

Ngưỡng sản xuất phải được chọn theo dữ liệu đã thẩm định, năng lực hàng đợi và chi phí kết luận sai. Không dùng tỷ lệ điểm demo hoặc lời giải thích do LLM tạo làm tiêu chuẩn chứng minh.
