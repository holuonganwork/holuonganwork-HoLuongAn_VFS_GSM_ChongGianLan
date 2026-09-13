# Yêu cầu phi chức năng

Các mức dưới đây là **mục tiêu thiết kế đề xuất**, chưa được đo trên prototype. NFR áp dụng cho MVP dùng dữ liệu thật; nhóm kiến trúc xác nhận tính khả thi và chi phí tại cổng pilot.

## Hồ sơ tải để đo

Giả định pilot: tối đa 1.000 tài xế, 10 kiểm soát viên, 10.000 chuyến/ngày và 60 điểm GPS/chuyến trung bình. Cửa sổ tìm kiếm trực tuyến 30 ngày tương ứng khoảng 300.000 chuyến và 18 triệu điểm GPS; đây là giả định tải, không phải chính sách lưu trữ. Test với 20 phiên tìm kiếm đồng thời và 50 phiên tài xế thao tác biểu mẫu; đường truyền tài xế mô phỏng 2 Mbps, trễ 200 ms. Thay số khi có đo thực tế và ghi cấu hình máy, độ lớn chỉ mục, cache nóng/lạnh trong biên bản.

| Mã | Thuộc tính | Tiêu chí có thể đo | Cách chứng minh / owner |
| --- | --- | --- | --- |
| NFR-01 | Bảo mật truy cập | 100% tình huống trái ownership/phân công bị từ chối ở server, không lộ metadata; thay quyền có hiệu lực trong ≤5 phút; MFA cho vai trò nội bộ có quyền quyết định/xuất | Kiểm thử quyền ngang/dọc và thu hồi phiên; Security |
| NFR-02 | Bảo vệ dữ liệu | Mã hóa khi truyền/lưu; không có credential, token, nội dung giải trình đầy đủ hoặc định vị chi tiết trong log vận hành; kiểm tra quyền trên snippet/export | Kiểm cấu hình, mẫu log và thử export; Security/đầu mối dữ liệu |
| NFR-03 | Tính toàn vẹn | 100% bằng chứng dùng để duyệt có source/version và kết quả kiểm hash; thay đổi một byte phát hiện được; tài khoản điều tra không sửa được bản gốc và hash kiểm chứng | Thử sửa bản sao, đối chiếu manifest; QA dữ liệu |
| NFR-04 | Tính đúng khi retry/đồng thời | Một hành động logic chỉ tạo một kết quả; hai người duyệt cùng version chỉ một người thành công; không có quyết định thiếu audit hoặc ngược lại | Thử cạnh tranh và lỗi giữa giao dịch; QA kỹ thuật |
| NFR-05 | Hiệu năng tìm kiếm | p95 ≤3 giây cho tìm mã/bộ lọc; ≤5 giây tìm văn bản trên trang đầu 50 kết quả; phản hồi gửi biểu mẫu chữ p95 ≤2 giây, không tính upload/giao thông báo ngoài hệ thống | Bài tải theo hồ sơ trên, ≥1.000 truy vấn hỗn hợp sau warm-up, báo cache lạnh riêng; Tech Lead |
| NFR-06 | Độ mới và quan sát được | Chuyến hoàn tất đến sẵn sàng tìm kiếm p95 ≤30 phút trong batch pilot; trạng thái hồ sơ đã lưu đến đọc lại ≤5 giây; mọi nguồn có watermark và cảnh báo trễ | Đối chiếu event/received/indexed time; Data Lead |
| NFR-07 | Sẵn sàng và phục hồi | Sẵn sàng tháng ≥99,5%; RPO ≤15 phút, RTO ≤4 giờ; biên nhận sau mốc phục hồi phải được đối soát/replay hoặc ghi ngoại lệ chưa khôi phục, không báo đủ khi còn thiếu | Giám sát đường đi chính, diễn tập restore gồm dữ liệu và tệp; Operations |
| NFR-08 | Khả dụng trên di động | 8/10 người thử độc lập hoàn thành xem yêu cầu–gửi phản hồi trong ≤5 phút không được hướng dẫn thao tác; bàn phím/nhãn rõ, lỗi không chỉ báo bằng màu, chữ phóng to 200% vẫn dùng được | Thử tác vụ bằng mẫu tài xế đa dạng, không ghi đây là kết quả đã đạt; UX |
| NFR-09 | Giới hạn tệp và mạng yếu | Đề xuất JPG/PNG/PDF, ≤10 MB/tệp, ≤5 tệp/lần gửi; kiểm MIME thực, cách ly/quét trước khi mở; mất mạng không mất nháp đã được xác nhận lưu; tệp bị lỗi có hướng dẫn gửi lại | Kiểm tệp sai loại, giới hạn, quét lỗi và mạng ngắt; Security/QA |
| NFR-10 | Kiểm toán và thời gian | Mọi chuyển trạng thái, quyết định, export, đọc nhạy cảm có actor và dấu thời gian UTC; UI ghi múi giờ; audit không bị sửa qua quyền vận hành; báo thiếu sự kiện | Đối soát sự kiện theo mã liên kết, kiểm đồng hồ và quyền; Audit/Operations |
| NFR-11 | Khả năng giải thích và chất lượng | 100% cảnh báo có đo lường/nguồn/phiên bản/giới hạn; không hiển thị phần trăm gian lận nếu chưa có xác suất đã kiểm định; báo tỷ lệ chưa xác định và sai số theo nhóm đủ mẫu | Review mẫu độc lập và mẫu mâu thuẫn/thiếu dữ liệu; Risk Lead |
| NFR-12 | Duy trì và vòng đời | Có rollback cấu hình, thay quy tắc không sửa lịch sử; tác vụ lưu/xóa/hold có báo cáo đối soát tới dữ liệu và chỉ mục; backup có lịch hết hạn riêng và áp lại danh sách xóa khi restore | Diễn tập rollback, hold, xóa và restore; Data/Operations |

Lưu ý NFR-07: RPO cho phép một khoảng mất dữ liệu do thảm họa; biên nhận phải nêu được mốc phục hồi và có cơ chế đối soát/replay để phục hồi các giao dịch sau mốc đó. Nếu nghiệp vụ yêu cầu tuyệt đối không mất mọi biên nhận thì phải đổi mục tiêu sang RPO=0 cho luồng gửi và đánh giá lại kiến trúc/chi phí trước pilot. Không được quảng bá “không mất dữ liệu” chỉ từ việc có backup.

Sẵn sàng = thời gian các hành trình chính sử dụng được / tổng thời gian quan sát, gồm cả gián đoạn bảo trì trong mẫu số để không che mất trải nghiệm. Pilot chưa đủ một tháng chỉ báo kết quả trên số ngày đã quan sát; không khẳng định đã đạt SLO tháng. Thời gian lưu trực tuyến 30 ngày trong hồ sơ tải cũng không tự trở thành thời hạn xóa dữ liệu tại FR-20.

## Điều kiện đo và xử lý không đạt

NFR-01–04, 09–10 là cổng chất lượng bắt buộc trước người dùng thật. Các mục tiêu hiệu năng/sẵn sàng chưa có baseline phải được xác nhận qua bài đo phù hợp quy mô pilot. Nếu không đạt, giảm phạm vi pilot hoặc khắc phục và đo lại; ghi ngoại lệ có owner/hạn xử lý, không âm thầm sửa ngưỡng sau bài đo. Không yêu cầu chạy kiểm thử tải sản xuất chỉ để nghiệm thu tài liệu BA.
