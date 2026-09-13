# Yêu cầu chức năng

Tất cả FR dưới đây thuộc phạm vi **Must của MVP đích**. Bảng quy định hành vi để thiết kế/QA cùng hiểu; tiêu chí Given–When–Then tại [UAT](11-acceptance-criteria-and-uat.md). Chức năng tìm kiếm và biểu mẫu được chi tiết tại [trải nghiệm](16-experience-search-and-evidence-templates.md).

| Mã | Chức năng | Đầu vào, hành vi bắt buộc và đầu ra | BR |
| --- | --- | --- | --- |
| FR-01 | Nhận và kiểm tra nguồn | Nhận bản ghi có source ID, version, thời gian sự kiện/tiếp nhận; kiểm tra định danh, kiểu dữ liệu và quan hệ; tách lỗi/quarantine; công bố số nhận, trùng, lỗi và watermark theo nguồn | BR-01, BR-03 |
| FR-02 | Tạo dấu hiệu giải thích được | Chạy quy tắc đã duyệt với tham số chụp lại; tạo đo lường, ngưỡng, nguồn và cảnh báo chất lượng; thiếu dữ liệu bắt buộc thì đánh dấu không đánh giá được | BR-02, BR-10 |
| FR-03 | Gộp dấu hiệu và chống trùng | Nhóm theo cùng sự việc, thời gian và nguồn; giữ mọi nhóm nghi vấn; retry cùng đầu vào không tạo thêm hồ sơ; tín hiệu mới làm thay đổi bản chụp phải được rà soát liên kết hồ sơ trước khi phát hành thêm | BR-02, BR-08 |
| FR-04 | Hàng đợi và phân công | Lọc loại, trạng thái, owner, đơn vị, mức ưu tiên, hạn, chất lượng; sắp ưu tiên quá hạn rồi mức tác động đã xác minh, risk, thời gian tạo; nhận/chuyển việc có kiểm tra phiên bản | BR-08 |
| FR-05 | Tìm kiếm đa nguồn | Tìm mã hồ sơ/tài xế/chuyến/thiết bị, khoảng thời gian và từ khóa trong mô tả/giải trình được phép; AND giữa bộ lọc, OR trong đa lựa chọn; phân trang, nguồn, độ mới và liên kết gốc | BR-01, BR-07 |
| FR-06 | Dòng thời gian và quan hệ | Xem sự kiện theo event time và received time, GPS có sai số nếu có, chuyến–thiết bị–chính sách–giải trình; thể hiện khoảng trống/mâu thuẫn và quan hệ chỉ là quan sát | BR-01, BR-03 |
| FR-07 | Lập gói bằng chứng | Lưu bản gốc/bản dẫn xuất, hash, xuất xứ, đơn vị đo, phương pháp tính, rule version, quality, trạng thái xác minh; phân loại ủng hộ/phản bác/chưa rõ; gắn vào giả thuyết và quyết định | BR-03 |
| FR-08 | Phát hành yêu cầu giải trình | Kiểm soát soạn mã chuyến, sự việc, câu hỏi, nội dung đã che, hạn và kênh hỗ trợ; xem trước bản tài xế; lưu phiên bản phát hành và trạng thái giao | BR-04, BR-07 |
| FR-09 | Cổng tài xế và biên nhận | Tài xế chỉ xem hồ sơ đã phát hành của mình; lưu nháp theo tài khoản, gửi nội dung, tải tệp và nhận mã/thời gian biên nhận; retry cùng yêu cầu không nhân đôi; bổ sung tạo phiên bản mới | BR-04 |
| FR-10 | Thông báo, nhắc hạn và gia hạn | Lưu riêng sent/delivered/read khi kênh hỗ trợ; retry không reset hạn; lỗi giao tạo tác vụ hỗ trợ; gia hạn ghi người, lý do, hạn cũ/mới; không chứa chi tiết nhạy cảm trong thông báo ngoài ứng dụng | BR-04, BR-08 |
| FR-11 | Đánh giá và đề xuất | Kiểm soát đánh giá từng ý giải trình, đối chiếu nguồn ủng hộ/phản bác, chỉ ra phần thiếu; chọn resolution, căn cứ quy chế và số tiền đã xác minh nếu có; checklist chặn gửi thiếu | BR-03, BR-05 |
| FR-12 | Phê duyệt kết luận | Người độc lập duyệt/trả lại với lý do, khóa theo version; thông tin mới làm vô hiệu đề xuất đang chờ; lưu quyết định và audit nguyên tử; không tác động trực tiếp tài khoản/tiền | BR-05 |
| FR-13 | Công bố kết quả và bàn giao | Tạo bản kết quả phù hợp người nhận, lý do, căn cứ được phép xem và hạn khiếu nại; theo dõi giao; bàn giao thủ công có người nhận/trạng thái; không tự chạy chế tài | BR-05, BR-06 |
| FR-14 | Khiếu nại và xem xét lại | Nhận lý do/tài liệu, kiểm tra hạn và người độc lập; giữ/sửa/hủy bằng decision version mới; giữ lịch sử, theo dõi khắc phục nếu đã bàn giao; yêu cầu trễ có luồng xem xét đặc biệt | BR-06 |
| FR-15 | Xác thực và quyền theo đối tượng | Xác thực người dùng bằng danh tính đáng tin cậy; kiểm tra vai trò, đơn vị, phân công, ownership và trường dữ liệu tại server cho mọi hành động; hạn chế người điều tra tự duyệt | BR-07 |
| FR-16 | Audit và lịch sử | Ghi actor đã xác thực, thời gian, hành động, object/version, lý do, kết quả cho đọc nhạy cảm/tìm kiếm/xuất/thay đổi; không lưu tràn lan nội dung cá nhân; không sửa/xóa qua giao diện vận hành | BR-03, BR-07 |
| FR-17 | Xuất hồ sơ có kiểm soát | Xuất bản tài xế hoặc nội bộ theo quyền, kèm manifest nguồn/phiên bản/hash, bộ lọc, người xuất, thời điểm và mức che; đóng dấu mục đích; audit yêu cầu và lượt tải | BR-03, BR-07 |
| FR-18 | Báo cáo chất lượng và vận hành | KPI OBJ, tồn/quá hạn, giao/đọc/phản hồi, nhãn chưa xác định, khiếu nại và đảo kết luận; có mẫu số, cohort, thời gian và độ mới; không suy tiền thu hồi từ số cảnh báo | BR-08, BR-09 |
| FR-19 | Quản lý phiên bản quy tắc | Tạo nháp, chạy thử trên mẫu, so với bản hiện hành, người khác duyệt, lịch hiệu lực và rollback; mỗi phát hiện giữ snapshot cũ; chưa tự áp nhãn mô hình thành kết luận | BR-02, BR-10 |
| FR-20 | Quản lý vòng đời dữ liệu | Cấu hình lịch lưu theo loại/mục đích đã duyệt, legal hold, yêu cầu truy cập/đính chính/xóa có thẩm định; áp dụng đến bản gốc, chỉ mục và bản export quản lý được; lưu biên bản xử lý | BR-07 |
| FR-21 | Phản hồi chất lượng và tạo tập đánh giá | Lấy mẫu có thiết kế, ghi nhãn bởi người độc lập, quản lý bất đồng và phiên bản sau khiếu nại; giữ split theo thời gian/sự việc; tách dữ liệu tổng hợp và thật | BR-09, BR-10 |
| FR-22 | Tiếp nhận vấn đề từ tài xế | Cho tài xế báo vấn đề của chuyến/hồ sơ mình với lý do và bằng chứng; kiểm soát sàng lọc/chuyển đúng kênh hoặc liên kết hồ sơ đã có; biên nhận không đồng nghĩa xác nhận gian lận | BR-01, BR-04 |

## Quy tắc chung cho thao tác ghi

Lệnh ghi phải nêu object/version hiện hành; actor lấy từ phiên đăng nhập. Sau khi nhận thành công, nội dung và audit có thể đọc lại. Lỗi mạng sau khi server đã lưu được giải quyết bằng mã idempotency và truy vấn biên nhận; không yêu cầu tài xế gửi lại thành nội dung mới. Cập nhật xung đột trả thông tin để tải lại, không âm thầm ghi đè.

## Tìm kiếm: ngữ nghĩa tối thiểu

Định danh chính xác được ưu tiên trước từ khóa. Khoảng thời gian dùng `[từ, đến)` và luôn hiển thị múi giờ; nếu chọn ngày địa phương thì chuyển biên ngày sang UTC. Tìm không dấu áp dụng trường văn bản tiếng Việt; mã định danh được chuẩn hóa theo hợp đồng nguồn, không ghép hai mã chỉ vì gần giống. Kết quả phải hiển thị lý do khớp, loại nguồn, chất lượng, thời gian cập nhật, tổng số trong phạm vi quyền và liên kết chi tiết.

MVP tìm nội dung chữ có cấu trúc và metadata tệp, **không cam kết tìm chữ bên trong ảnh/PDF**. OCR/ngữ nghĩa là Could sau pilot, phải dẫn đúng trang/đoạn và không mở rộng quyền truy cập. Bản xuất, snippet và bộ đếm không được để lộ dữ liệu đã bị che. Chi tiết tác vụ tại tài liệu 16.
