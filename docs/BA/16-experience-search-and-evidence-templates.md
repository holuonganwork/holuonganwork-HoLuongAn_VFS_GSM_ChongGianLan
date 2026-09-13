# Trải nghiệm, tìm kiếm và mẫu bằng chứng

## Hành trình người dùng

| Bước | Kiểm soát cần làm | Tài xế cần biết/làm | Dấu hiệu trải nghiệm đạt |
| --- | --- | --- | --- |
| Tiếp nhận | Nhận đúng hồ sơ, biết vì sao ưu tiên | Chưa bị yêu cầu hành động khi mới có cảnh báo nội bộ | Không gửi thông báo nghi vấn thiếu sàng lọc |
| Xác minh | Tìm nguồn, đo lường, so bối cảnh | Xem sự việc khi được phát hành | Không gọi tài xế là gian lận khi chưa kết luận |
| Làm rõ | Đặt câu hỏi cụ thể và theo dõi giao | Trả lời từng ý, cung cấp thứ mình có, xin hỗ trợ/gia hạn | Có hạn, trạng thái và biên nhận rõ |
| Quyết định | Kiểm tra phản bác, đề xuất/duyệt độc lập | Nhận lý do và dữ kiện liên quan | Không chỉ thông báo một risk score |
| Xem lại | Phân công người độc lập, khắc phục nếu đổi kết quả | Gửi khiếu nại và theo dõi | Giữ lịch sử, biết kết quả nào đang hiệu lực |

## Màn hình khái niệm

Đây là cấu trúc nội dung để UX thiết kế, không phải giao diện đã được xây dựng.

| Màn hình | Thành phần chính | Hành động và trạng thái lỗi |
| --- | --- | --- |
| Hàng đợi kiểm soát | Mã hồ sơ, chủ thể, loại nghi vấn, lý do ưu tiên, owner, hạn, quality, nguồn cập nhật | Nhận/chuyển/lọc; xung đột nhận việc; nguồn chưa sẵn sàng |
| Tìm kiếm | Ô mã/từ khóa, loại thực thể, loại nguồn, thời gian và múi giờ, unit/owner/type/status | Xem nguồn, thêm vào hồ sơ được giao; rỗng, bộ lọc sai, nguồn trễ, không đủ quyền |
| Hồ sơ điều tra | Sự việc; dấu hiệu; timeline/bản đồ; bảng nguồn; giải trình; ủng hộ/phản bác; đề xuất; lịch sử | Yêu cầu bổ sung, đề xuất, duyệt; hiển thị phần chưa xác minh; khóa do version mới |
| Danh sách tài xế | Chỉ hồ sơ đã công bố của mình; trạng thái dễ hiểu, hạn, việc cần làm | Mở, phản hồi, báo vấn đề; chưa có hồ sơ hoặc lỗi tải riêng |
| Chi tiết tài xế | Mã chuyến, sự việc trung tính, căn cứ được công bố, câu hỏi, hạn/hỗ trợ, nội dung đã gửi | Lưu nháp, gửi, bổ sung, xin gia hạn; nháp đã lưu/chưa lưu; tệp chờ quét/lỗi |
| Kết quả và khiếu nại | Kết luận có hiệu lực, lý do, căn cứ liên quan, ngày giao, hạn/kênh xem lại | Khiếu nại, theo dõi, tải bản đã công bố; thông tin trễ hạn và cách đề nghị xét đặc biệt |

Điểm rủi ro và ngưỡng phát hiện chỉ hiển thị cho vai trò nghiệp vụ cần dùng. Nhận xét nội bộ tách khỏi nội dung công bố. Nếu người dùng cần xem căn cứ để giải trình, ưu tiên mô tả sự kiện cụ thể đủ hiểu thay vì thông báo “hệ thống phát hiện bất thường” không có chi tiết.

Quyền truy cập cổng giải trình/khiếu nại phải tách khỏi quyền nhận chuyến. Nếu tài khoản vận hành bị hạn chế hoặc tài xế mất thiết bị, vẫn có cách xác minh danh tính qua hỗ trợ và nhận/gửi tài liệu an toàn; không yêu cầu mở lại quyền nhận chuyến chỉ để gửi khiếu nại. Tình huống này cần có test con trong UAT-18/19.

## Đặc tả tìm kiếm phục vụ điều tra

| Thuộc tính | Hành vi MVP |
| --- | --- |
| Điểm vào | Mã hồ sơ, mã tài xế ngoài hệ thống, mã chuyến, mã thiết bị token hóa hoặc từ khóa |
| Phạm vi | Nguồn chuyến/GPS/thiết bị/chính sách, evidence metadata, nội dung chữ giải trình/mô tả theo quyền; metadata tệp |
| Bộ lọc | Thực thể, loại nguồn, `[từ,đến)`, đơn vị, owner, trạng thái, loại nghi vấn, quality; rõ bộ lọc nào chỉ áp dụng hồ sơ |
| Kết hợp | AND giữa trường; OR giữa lựa chọn trong cùng trường; từ khóa tiếng Việt tìm chuỗi/cụm theo chính sách được hiển thị |
| Chuẩn hóa | Chuẩn hóa dấu/case cho văn bản; mã theo hợp đồng nguồn; không fuzzy-merge danh tính |
| Sắp xếp | Tra mã ưu tiên exact match; tìm chữ theo mức liên quan, sau đó event time giảm dần, source ID tăng dần để ổn định; người dùng có thể chọn thời gian |
| Phân trang | Mặc định 50, tối đa 200; truy vấn có snapshot/watermark và thứ tự ổn định; nguồn thay đổi thì báo refresh, không lẫn hai snapshot |
| Kết quả | Loại bản ghi, mã, lý do khớp, đoạn chữ được phép, event/received time, nguồn/version, quality, đường dẫn chi tiết |
| Không kết quả | “Không tìm thấy trong phạm vi đã chọn”; hiện bộ lọc và gợi ý nới phạm vi, không khẳng định không có gian lận |
| Nguồn chưa sẵn sàng | Kết quả khả dụng kèm nguồn thiếu/độ trễ; tổng số là tổng trong phần đã lập chỉ mục và đúng quyền |
| Lưu kết quả vào hồ sơ | Lưu query/bộ lọc/snapshot/IDs/version; sau khi dữ liệu nguồn đổi vẫn mở được bản đã viện dẫn |
| Quyền | Lọc quyền trước khi trả snippet/count/ranking/extract; tệp tải lại kiểm quyền; không cho tài xế dùng tìm kiếm xuyên hồ sơ |

Ví dụ tác vụ để UX/QA dùng: tìm mã chuyến chính xác; tìm “mất sóng” trong giải trình đã được phân công; tìm các GPS của một chuyến trong khoảng 23:50 ngày D tới 00:20 ngày D+1 theo giờ Việt Nam; tìm liên kết thiết bị có khoảng dùng giao với thời gian sự việc; so các chuyến thưởng và không thưởng trong cùng cửa sổ. Bộ tìm kiếm không cung cấp chữ trong ảnh nếu chưa có OCR, và không suy dữ liệu thiếu thành kết quả âm.

Tác vụ quan hệ phải hiển thị thời gian, nguồn và tính phụ thuộc; hai tài xế cùng dùng một mã thiết bị có thể do cấp lại. Khi thêm căn cứ liên quan người khác, tạo bản diễn giải/che phù hợp trước công bố.

## Mẫu evidence item

| Trường cần điền | Nội dung cần ghi |
| --- | --- |
| Mã evidence / hồ sơ / giả thuyết | Định danh; nhận định đang kiểm tra, không ghi sẵn kết luận |
| Sự kiện quan sát | Ai/đối tượng nào, chuyến nào, thời điểm và đo lường cụ thể |
| Nguồn và bản chụp | Hệ thống, source IDs/versions, thời điểm/phương thức thu, người thu |
| Toàn vẹn | Hash thuật toán/giá trị của bản gốc và bản dẫn xuất, thời điểm/kết quả kiểm; giá trị sinh khi thu thật |
| Phép biến đổi | Công thức, đơn vị, bộ lọc, cửa sổ, tập mẫu số, rule version và tham số |
| Chất lượng và giới hạn | Dữ liệu thiếu, độ trễ, sai số, nguồn phụ thuộc, phần không thể kiểm chứng |
| Thông tin phản bác | Giải thích hợp lệ cần kiểm; căn cứ liên quan; phần đã xác minh/chưa xác minh |
| Phân loại sử dụng | Support/refute/unclear; verified/unverified/disputed/integrity_failed; ai đã kiểm |
| Công bố | Bản nội bộ/bản tài xế, dữ liệu cần che, người kiểm duyệt bản công bố |
| Viện dẫn | Quyết định hoặc đề xuất nào dùng evidence version này; lịch sử đổi/thu hồi |

Không tạo hash giả để làm ví dụ trông giống đã thu nhận thật. Mẫu này quy định trường phải điền khi có dữ liệu; giá trị hash và actor do hệ thống đã xác thực sinh/ghi lúc thực hiện.

## Ba hồ sơ tổng hợp để thảo luận

### Ví dụ A — GPS bất thường nhưng chưa chứng minh hành vi

Hồ sơ `DEMO-CASE-A`, tài xế `DEMO-TX-A`, chuyến `DEMO-TRIP-A`. Dữ liệu minh họa giả định có một đoạn đo được **6 km trong 30 giây**, tương ứng `6 / 30 × 3600 = 720 km/h`; đây là số liệu minh họa phép tính, chưa có cặp tọa độ gốc để nghiệm thu. Bản dùng UAT phải cung cấp cặp GPS đầy đủ để tái tính, thay vì chỉ chép các số này.

Giả thuyết 1: tín hiệu bị can thiệp. Giả thuyết 2: thiết bị khôi phục vị trí sau mất sóng hoặc đồng hồ sai. Kiểm soát cần tìm accuracy/provider, received time, khoảng mất dữ liệu, log sự cố và giải trình. Nếu các nguồn kỹ thuật xác nhận lỗi và không có căn cứ hành vi vi phạm, đề xuất `not_fraud`; nếu không đủ phân biệt, `inconclusive`. Điểm GPS đơn lẻ không vượt qua RULE-08.

### Ví dụ B — Thiết bị dùng luân phiên hợp lệ

`DEMO-DEVICE-B` từng liên kết `DEMO-TX-B1/B2/B3`. Các khoảng cấp phát theo sổ đội xe không chồng lấn, phù hợp lịch liên kết. Dấu hiệu RULE-03 vẫn xuất hiện dưới cấu hình demo nhưng sổ cấp phát là căn cứ phản bác cần xác minh. Sau kiểm, đề xuất `not_fraud`; tài xế chỉ thấy thông tin liên quan giai đoạn mình sử dụng, không thấy danh tính/lời giải trình người khác.

### Ví dụ C — Chuyến lặp và nghi vấn thưởng

Trong cửa sổ minh họa có 12 chuyến, 10 chuyến nhận ưu đãi và 9 trong số 10 chuyến đó đủ điều kiện ngắn: tỷ lệ lần lượt `10/12 ≈ 83,33%` và `9/10 = 90%`. Giả định 9 chuyến ngắn cùng tuyến trong bán kính quy định và ngưỡng chương trình là 10; khi đó cả nhóm lặp và khuyến mại có thể kích hoạt, điểm demo `25 + 20 = 45`.

Đây mới là dấu hiệu. Hồ sơ phải đối chiếu điều kiện hưởng, nhu cầu chuyến thực, phản hồi tài xế và sổ chi nếu có. Không cộng hai lần khoản ưu đãi vì có hai nhóm cảnh báo. Chưa có payout thì ghi tiền nghi vấn và trạng thái chưa xác nhận chi; chưa đủ RULE-08 thì chưa xác nhận gian lận.

## Mẫu nội dung giao tiếp

**Yêu cầu làm rõ:** “Chúng tôi cần đối chiếu dữ liệu chuyến [mã] vào [thời gian và múi giờ]. Dữ liệu đang có [mô tả sự kiện]. Anh/chị vui lòng cho biết [câu hỏi cụ thể]. Anh/chị có thể bổ sung tài liệu sẵn có hoặc cho biết không có tài liệu. Hạn phản hồi: [hạn tính từ giao hợp lệ]. Đây là yêu cầu xác minh. Anh/chị có thể xin hỗ trợ/gia hạn tại [kênh].”

**Biên nhận:** “Đã nhận phản hồi [mã] lúc [giờ]. Nội dung đã được lưu. Tệp [tên] đang kiểm tra/chưa tải thành công. Anh/chị có thể theo dõi hoặc gửi bổ sung tại hồ sơ.”

**Kết quả:** “Hồ sơ [mã] có kết quả [diễn đạt kết luận]. Các căn cứ chính: [sự kiện và nguồn được công bố]. Giải trình của anh/chị đã được xem xét như sau: [đánh giá]. Nếu chưa đồng ý, anh/chị có thể yêu cầu xem lại tại [kênh] trước [hạn].”

Thông báo ngoài ứng dụng chỉ nêu có cập nhật và cách vào hệ thống, không chứa tọa độ, tài liệu cá nhân hoặc nội dung cáo buộc. Các phần trong ngoặc vuông là trường của mẫu thông báo, được điền bằng dữ liệu đã kiểm khi vận hành.
