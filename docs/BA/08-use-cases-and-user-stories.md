# Use case và user story

## Danh mục use case

| Mã | Tác nhân và mục tiêu | Kích hoạt / tiền điều kiện | Hậu điều kiện thành công |
| --- | --- | --- | --- |
| UC-01 | Tác vụ dữ liệu tạo nghi vấn | Nguồn được cấp quyền, quy tắc có hiệu lực; batch mới hoặc chạy lại | Có nguồn, kết quả chất lượng, dấu hiệu/cảnh báo không trùng |
| UC-02 | Kiểm soát nhận và tìm hồ sơ | Đã xác thực, đúng đơn vị; có hồ sơ mới hoặc mã cần tra | Có owner, kết quả tìm phù hợp quyền và truy được nguồn |
| UC-03 | Kiểm soát dựng bằng chứng | Có hồ sơ được giao và nguồn đủ truy cập | Có gói nguồn/đo lường/giả thuyết/phản bác và lịch sử truy cập |
| UC-04 | Kiểm soát yêu cầu tài xế làm rõ | Có sự kiện cụ thể cần hỏi và bản công bố phù hợp | Tài xế có yêu cầu, hạn tính đúng mốc giao, cơ chế hỗ trợ |
| UC-05 | Tài xế phản hồi | Yêu cầu thuộc tài xế, phiên xác thực hợp lệ | Nội dung và tệp hợp lệ có biên nhận, kiểm soát được báo |
| UC-06 | Kiểm soát và người duyệt kết luận | Đã kiểm nguồn, phản bác và cơ hội giải trình khi cần | Quyết định được duyệt độc lập, lưu phiên bản và công bố |
| UC-07 | Tài xế khiếu nại | Kết luận đã giao; trong hạn hoặc có lý do xem xét đặc biệt | Có kết quả độc lập và theo dõi khắc phục khi cần |
| UC-08 | Risk/QA cải tiến và báo cáo | Có dữ liệu được phép dùng và phương pháp lấy mẫu | KPI có mẫu số; nhãn đã thẩm định; quy tắc có phiên bản |
| UC-09 | Người được giao quản trị dữ liệu | Có nhiệm vụ, quyền và chính sách lưu/xuất cụ thể | Export hoặc xử lý vòng đời đúng phạm vi, có audit |
| UC-10 | Tài xế báo vấn đề chuyến của mình | Tài xế xác thực, chọn được chuyến thuộc mình | Có biên nhận; vấn đề liên kết hồ sơ hoặc chuyển đúng kênh |

## Luồng chi tiết các use case trọng tâm

### UC-02 — Nhận việc và tìm kiếm

1. Kiểm soát mở hàng đợi, xem mức ưu tiên, hạn và chất lượng dữ liệu.
2. Nhận hồ sơ trên phiên bản hiện hành; hệ thống ghi owner và thời điểm.
3. Tìm theo mã chuyến/tài xế và khoảng thời gian; kết quả chỉ gồm dữ liệu thuộc phạm vi được phép.
4. Mở bản ghi, xem nguồn/phiên bản, thêm vào danh sách cần đánh giá của hồ sơ.

Thay thế: hồ sơ vừa có người khác nhận thì báo xung đột; nguồn chưa cập nhật hiển thị watermark; tìm không thấy không suy thành không có vi phạm; mã không hợp lệ hướng dẫn cách nhập. Không chuyển bản ghi từ tài xế khác vào bản công bố cho người đang được điều tra.

### UC-03 — Từ dấu hiệu đến bằng chứng

1. Mở dấu hiệu và phép đo; kiểm tra đơn vị, thời gian, quy tắc và nguồn.
2. Ghi giả thuyết, ví dụ “tín hiệu định vị bị can thiệp”, cùng cách giải thích thay thế “GPS phục hồi sau mất sóng”.
3. Tìm các dữ kiện phân biệt hai giả thuyết; xem nguồn độc lập nếu có, ghi rõ nếu chúng cùng xuất phát từ một thiết bị.
4. Lập evidence item có nguồn, bản chụp, phương pháp tính, mức kiểm chứng; phân loại ủng hộ/phản bác/chưa rõ.
5. Kiểm tra tính toàn vẹn và nội dung cho phép công bố; lưu gói bằng chứng theo version.

Thay thế: sai hash hoặc nguồn không còn truy xuất được thì đặt trạng thái cần xác minh và chặn viện dẫn như căn cứ đã xác minh. Bản đồ chỉ minh họa, không biến đường nối qua khoảng trống thành hành trình thực tế. Một bản sao từ cùng nguồn không được tính là xác nhận độc lập.

### UC-04 và UC-05 — Yêu cầu, phản hồi, bổ sung

1. Kiểm soát chọn sự kiện/mã chuyến cần hỏi, soạn câu hỏi trung tính và xem trước bản tài xế.
2. Hệ thống phát hành phiên bản, gửi qua kênh đã đăng ký và theo dõi giao.
3. Tài xế mở yêu cầu, xem sự việc, hạn, quyền truy cập tài liệu và kênh hỗ trợ.
4. Tài xế lưu nháp, trả lời theo từng ý, thêm tài liệu sẵn có; không bắt cung cấp thứ họ không thể có.
5. Khi gửi, hệ thống lưu nội dung, cấp biên nhận; tệp đang quét được hiển thị đúng trạng thái.
6. Kiểm soát đánh giá; yêu cầu bổ sung phải nói rõ phần còn thiếu và hạn mới nếu được duyệt.

Thay thế: chưa giao thì xử lý lỗi kênh; mất mạng thì kiểm tra biên nhận trước khi gửi lại; nội dung chữ vẫn gửi được khi tệp bị cách ly; hỗ trợ gửi hộ phải nêu người thực hiện và căn cứ ủy quyền. Sau khi gửi chỉ được bổ sung phiên bản, không sửa lời khai cũ.

### UC-06 — Đề xuất và duyệt

1. Kiểm soát đối chiếu từng lập luận và ghi phần đã xác minh/chưa biết.
2. Chọn kết luận đề xuất, chính sách có hiệu lực, nguồn và phản bác liên quan.
3. Hệ thống kiểm tra checklist; xác nhận gian lận phải đủ cơ hội giải trình và dữ kiện cụ thể về hành vi vi phạm.
4. Người độc lập đọc hồ sơ và duyệt hoặc trả lại với lý do.
5. Lưu quyết định/audit; gửi bản kết quả đã che và hướng dẫn khiếu nại.

Thay thế: có tài liệu mới trong lúc chờ duyệt thì trở lại điều tra; hai người duyệt chỉ một thành công; thiếu chứng từ tiền thì không ghi tổn thất xác nhận; kiểm soát chưa đủ căn cứ có thể đề xuất `inconclusive`.

### UC-07 — Khiếu nại

1. Tài xế chọn quyết định, nêu điểm không đồng ý và cung cấp thông tin nếu có.
2. Hệ thống cấp biên nhận, giữ quyết định cũ, chỉ định người chưa tham gia kết luận.
3. Người xử lý xem hồ sơ cũ, căn cứ mới, tính đúng đắn của quy trình và yêu cầu làm rõ nếu cần.
4. Ghi giữ nguyên/sửa/hủy, lý do và quyết định version kế tiếp; gửi kết quả.
5. Nếu kết quả đã được bàn giao trước đó, tạo và theo dõi tác vụ khắc phục tới khi người nhận xác nhận.

Thay thế: trễ hạn thông thường chuyển người có thẩm quyền xét lý do; gửi lặp trả lại cùng biên nhận; không có người độc lập thì escalation. Việc đang khiếu nại hiển thị riêng, không tự động xóa kết luận gốc hoặc coi là có tội.

## User stories và dấu hiệu chấp nhận

| Mã | Câu chuyện | Dấu hiệu chấp nhận chính | FR |
| --- | --- | --- | --- |
| US-01 | Là chủ nguồn, tôi muốn biết batch nhận đúng bao nhiêu bản ghi để xử lý phần lỗi | Số nhận/trùng/lỗi đối soát được, retry không nhân đôi | FR-01, FR-02, FR-03 |
| US-02 | Là kiểm soát, tôi muốn nhận việc theo ưu tiên để không bỏ hồ sơ đến hạn | Owner rõ, chống nhận đồng thời, bộ lọc và hạn nhất quán | FR-04 |
| US-03 | Là kiểm soát, tôi muốn tìm từ mã chuyến đến dữ kiện liên quan để kiểm giả thuyết | Kết quả đúng quyền, nguồn và timeline truy được | FR-05, FR-06 |
| US-04 | Là người duyệt, tôi muốn thấy cả căn cứ ủng hộ và phản bác để kiểm tra đề xuất | Gói bằng chứng có nguồn, phiên bản, hash và mức xác minh | FR-07, FR-11 |
| US-05 | Là kiểm soát, tôi muốn đặt câu hỏi rõ và biết đã giao để tính hạn đúng | Bản công bố được xem trước, hạn chỉ bắt đầu sau giao | FR-08, FR-10 |
| US-06 | Là tài xế, tôi muốn giải trình bằng điện thoại và có biên nhận để biết đã gửi thành công | Giữ nháp, chống gửi lặp, tệp có trạng thái, bổ sung giữ bản cũ | FR-09 |
| US-07 | Là người duyệt, tôi muốn kết luận độc lập có căn cứ để chịu trách nhiệm về quyết định | Chặn tự duyệt/thiếu nguồn, lưu quyết định và công bố đúng bản | FR-12, FR-13 |
| US-08 | Là tài xế, tôi muốn người khác xem xét khiếu nại để kết quả được kiểm tra lại | Người xử lý độc lập, quyết định mới không xóa cũ, có khắc phục | FR-14 |
| US-09 | Là người chịu trách nhiệm dữ liệu, tôi muốn mọi quyền và truy cập kiểm chứng được | Ownership, audit, export có che, lịch lưu/hold/xóa đối soát | FR-15, FR-16, FR-17, FR-20 |
| US-10 | Là trưởng kiểm soát, tôi muốn KPI có mẫu số để đánh giá chất lượng thực | Báo tồn, chờ, precision, khiếu nại, độ mới và mẫu bị loại | FR-18 |
| US-11 | Là Risk Analyst, tôi muốn thử phiên bản mới trên nhãn đã thẩm định để giảm nhiễu | Có người duyệt, đánh giá thời gian khác, rollback và giữ lịch sử | FR-19, FR-21 |
| US-12 | Là tài xế, tôi muốn báo lỗi dữ liệu chuyến của mình để được làm rõ sớm | Có biên nhận, chống trùng, chuyển đúng kênh với người nhận | FR-22 |

Không coi danh mục này là backlog đã được ước lượng. Phân rã kỹ thuật và ước lượng chỉ thực hiện sau khi thống nhất dữ liệu, quy trình quyền và tiêu chí UAT liên quan.
