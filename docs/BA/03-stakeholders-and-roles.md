# Bên liên quan, vai trò và trách nhiệm

## Vai trò và nhu cầu

| Vai trò | Công việc cần hoàn thành | Quyền quyết định / giới hạn |
| --- | --- | --- |
| Sponsor / chủ sản phẩm | Chốt mục tiêu, phạm vi, nguồn lực, mức chấp nhận rủi ro | Chấp thuận pilot; không sửa bằng chứng hoặc quyết định cá biệt bằng quyền quản trị |
| Tài xế | Hiểu sự việc liên quan, cung cấp bối cảnh, theo dõi kết quả, khiếu nại | Gửi nội dung của mình; không sửa dữ liệu nguồn hay xem hồ sơ người khác |
| Kiểm soát viên | Sàng lọc, tìm dữ liệu, kiểm tra giả thuyết, trao đổi, đề xuất | Được thao tác trong phạm vi phân công; không tự duyệt đề xuất của mình |
| Trưởng kiểm soát / người duyệt | Phân công, kiểm tra tính đầy đủ, duyệt hoặc trả lại | Quyết định trên hồ sơ không do chính mình điều tra; phải nêu lý do |
| Người giải quyết khiếu nại | Kiểm tra căn cứ mới và tính đúng đắn của quy trình | Khác người điều tra và người duyệt trước; có thể giữ/sửa/hủy kết luận |
| Vận hành tài xế / hỗ trợ | Hướng dẫn truy cập, hỗ trợ người gặp khó khăn | Gửi hộ chỉ khi có xác minh và ghi nhận ủy quyền; không kết luận gian lận |
| Chủ nguồn / Data Steward | Giải thích nguồn, sửa lỗi theo phiên bản, đối chiếu chất lượng | Xác nhận dữ kiện thuộc nguồn; không quyết định kết quả hồ sơ |
| Risk Analyst / Data Scientist | Đề xuất và đánh giá quy tắc/mô hình | Không tự đưa phiên bản vào pilot khi chưa có người duyệt nghiệp vụ |
| Finance | Xác minh tiền đã chi, thất thoát, thu hồi | Xác nhận số tiền theo chứng từ; không suy số tiền từ risk score |
| Pháp chế / đầu mối bảo vệ dữ liệu | Xác định căn cứ, thông báo, quyền, thời hạn lưu và bàn giao | Thẩm định theo loại dữ liệu, hợp đồng và địa bàn |
| Quản trị / an toàn thông tin | Cấp quyền, vận hành, xử lý sự cố | Không mặc nhiên có quyền đọc nội dung hồ sơ; truy cập khẩn cấp phải ghi lý do |
| Kiểm toán / QA nghiệp vụ | Đọc mẫu hồ sơ, kiểm chứng audit và chất lượng | Chỉ đọc theo phạm vi; không ghi đè kết luận |

Các vai trò là chức năng, không giả định cơ cấu nhân sự thực tế. Một người có thể giữ nhiều chức năng ở quy mô nhỏ, nhưng các ràng buộc độc lập phải kiểm tra **trên từng hồ sơ**. Nếu thiếu người độc lập, hồ sơ chờ phân công/escalation, không tự bỏ bước kiểm tra.

## RACI

R: thực hiện; A: chịu trách nhiệm cuối cùng; C: tham vấn; I: được thông tin; “—”: không tham gia. Mỗi dòng có một A. “Dữ liệu” gồm chủ nguồn và Risk Analyst tùy công việc; “Pháp chế” gồm đầu mối bảo vệ dữ liệu.

| Hoạt động | Sponsor | Kiểm soát | Người duyệt | Tài xế | Dữ liệu | Pháp chế | Finance | Người xử lý khiếu nại |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Chốt phạm vi và KPI | A | R | C | C | C | C | C | I |
| Thông qua căn cứ xử lý dữ liệu | I | C | I | I | R | A | C | I |
| Phê duyệt phiên bản quy tắc | I | C | A | — | R | C | C | I |
| Xác nhận chất lượng nguồn | I | C | I | — | A/R | C | C | — |
| Phân công điều tra | I | R | A | I | — | — | — | — |
| Thu thập và đánh giá bằng chứng | — | R | A | C | C | C | C | — |
| Gửi giải trình | — | C | I | A/R | — | — | — | — |
| Duyệt kết luận lần đầu | I | R | A | I | C | C | C | — |
| Giải quyết khiếu nại | I | C | C | C | C | C | C | A/R |
| Xác nhận lợi ích/tiền tổn thất | I | R | C | — | C | C | A | — |

## Ma trận quyền tối thiểu

| Tài nguyên / hành động | Tài xế | Kiểm soát viên | Người duyệt | Khiếu nại | Kiểm toán | Quản trị kỹ thuật |
| --- | --- | --- | --- | --- | --- | --- |
| Hồ sơ chưa phát hành | Không | Theo phân công | Theo đơn vị | Khi được giao vụ khiếu nại | Theo nhiệm vụ | Không mặc định |
| Bản hồ sơ tài xế được xem | Của mình | Xem trước khi phát hành | Duyệt bản phát hành | Theo hồ sơ | Chỉ đọc | Không mặc định |
| Bản gốc chứa dữ liệu bên thứ ba | Không | Khi cần và có quyền nguồn | Tương tự | Tương tự | Theo nhiệm vụ | Truy cập khẩn cấp có audit |
| Giải trình đã gửi | Đọc của mình, bổ sung phiên bản | Đọc, yêu cầu bổ sung | Đọc | Đọc | Đọc theo nhiệm vụ | Không sửa |
| Đề xuất kết luận | Không | Tạo trên hồ sơ được giao | Trả lại/duyệt nếu độc lập | Không sửa quyết định cũ | Chỉ đọc | Không |
| Quyết định khiếu nại | Gửi yêu cầu | Không tự giải quyết | Không tự xử lý quyết định mình đã duyệt | Ghi phiên bản kế tiếp | Chỉ đọc | Không |
| Export | Bản đã công bố của mình | Theo quyền xuất riêng | Theo quyền xuất riêng | Theo quyền xuất riêng | Theo nhiệm vụ | Không mặc định |
| Đổi quyền / chính sách lưu | Không | Không | Đề nghị | Không | Kiểm tra | Thực thi thay đổi đã duyệt |

Quyền phải áp dụng đồng nhất cho danh sách, tìm kiếm, bộ đếm, chi tiết, tệp đính kèm, URL tải xuống và export. Kiểm tra lại khi tải tệp, không chỉ lúc tạo đường dẫn. Người nhận chuyển công tác/mất quyền phải mất khả năng truy cập phiên đang mở theo NFR-01.

Nếu phát hiện nghi vấn thông đồng với người kiểm soát, chuyển hồ sơ đến người độc lập ngoài chuỗi phân công hiện tại, bảo vệ người báo và audit thao tác. Đây là ngoại lệ vận hành, không dùng hệ thống này để tự động đánh giá nhân viên.
