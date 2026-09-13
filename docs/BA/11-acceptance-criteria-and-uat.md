# Tiêu chí nghiệm thu và UAT

## Phạm vi nghiệm thu

Bộ kịch bản này nghiệm thu **sản phẩm đích theo BA**, không mô tả kết quả test đã chạy. Tất cả UAT hiện ở trạng thái **Chưa thực hiện**. Các test prototype đã có trong repository chỉ chứng minh phần được triển khai và cần đối chiếu lại theo [gap analysis](17-prototype-gap-and-transition.md).

Dùng [bảng UAT dạng CSV](uat-scenarios.csv) để ghi build, phiên bản dữ liệu, người thực hiện, kết quả thực tế và bằng chứng khi triển khai. Các ô kết quả trống là trường ghi nhận, không phải nội dung phân tích chưa hoàn thành.

UAT nghiệp vụ do kiểm soát, đại diện tài xế và người duyệt thực hiện; QA chuẩn bị dữ liệu và lưu bằng chứng. Với hiệu năng, an toàn, phục hồi, đội kỹ thuật cung cấp biên bản kiểm chứng làm điều kiện đầu vào cho chủ nghiệp vụ chấp nhận; không yêu cầu tài xế tự đánh giá cấu hình hạ tầng.

## Bộ dữ liệu kiểm thử đề xuất

Dùng dữ liệu tổng hợp, định danh `TX-A`, `TX-B`, `TX-C`; hai đơn vị vận hành, ba vai trò độc lập là điều tra `KS-1`, duyệt `DUYET-1`, khiếu nại `KN-1`. Không dùng dữ liệu tài xế thật nếu chưa có quyền sử dụng. Những fixture mới dưới đây cần đội phát triển/QA xây khi triển khai; chưa được thêm vào code ở đợt tài liệu này.

| Nhóm | Ca dương, ca âm và biên cần có |
| --- | --- |
| GPS | Vượt ngưỡng, đúng ngưỡng, Δt=0, Δt<0, duplicate đứng yên, accuracy thiếu/kém, điểm đến trễ, mất sóng rồi phục hồi |
| Chuyến ngắn | 7/8/9 chuyến, ngay biên bán kính và thời lượng, cửa sổ qua nửa đêm, đầu cuối cửa sổ, tuyến đưa đón hợp lệ |
| Thiết bị | 2/3/4 tài xế, dùng luân phiên được cấp phát, khoảng dùng chồng lấn, mã bị cấp lại |
| Khuyến mại | Tỷ lệ dưới/bằng/trên 0,8, chuyến không thưởng nằm trong mẫu số, hai chính sách khác version, thưởng chưa chi, khoản bị đảo |
| Phối hợp | Gửi/giao/đọc khác nhau, gửi lỗi, trễ hạn, gia hạn, tệp sạch/bị cách ly, bằng chứng mới sát lúc duyệt |
| Quyền và lịch sử | Hồ sơ chưa công bố, hồ sơ người khác/đơn vị khác, phiên bị thu hồi, audit, export đã che, nguồn sửa, hold và xóa |

## Kịch bản chấp nhận

Mỗi dòng được diễn đạt theo **Given → When → Then**. Mỗi nhóm điều kiện biên phải có test con; ID cha giữ ổn định trong RTM.

| Mã | Given — điều kiện | When — hành động | Then — kết quả bắt buộc |
| --- | --- | --- | --- |
| UAT-01 | Batch có bản đúng, trùng, thiếu khóa, GPS không đúng chủ chuyến | Nhận batch và chạy lại | Đối soát số bản đúng/trùng/lỗi; dữ liệu sai bị cách ly; không tạo quan hệ sai; watermark chính xác |
| UAT-02 | Cặp GPS trong từng ca biên, có trường quality và nguồn | Chạy quy tắc GPS bản đã duyệt | Đúng phép đo/đơn vị; không chia 0; ghi chất lượng/thứ tự; có nguồn và version; không tự kết luận gian lận |
| UAT-03 | Tập chuyến ngắn ở biên số lượng/thời gian/bán kính, có tuyến hợp lệ | Chạy quy tắc lặp | Đúng `[start,end)` và hướng tuyến; giữ đủ tập khớp; tuyến lặp hợp lệ vẫn được kiểm bối cảnh, không tự xác nhận |
| UAT-04 | Một thiết bị cấp luân phiên cho ba tài xế có sổ cấp phát | Chạy và điều tra dấu hiệu | Có liên kết lịch sử đúng; không suy dùng đồng thời; kiểm soát lưu được bằng chứng phản bác; không lộ hồ sơ chéo cho tài xế |
| UAT-05 | Chuyến thưởng và không thưởng, tỷ lệ biên, chưa có payout | Chạy/đọc nghi vấn khuyến mại | Mẫu số đủ mọi chuyến thuộc điều kiện; đúng version; hiện tiền nghi vấn riêng, không ghi tiền đã mất/thu hồi |
| UAT-06 | Batch/cảnh báo đã xử lý, có cùng đầu vào và một sự việc khác | Retry, chạy đồng thời rồi nhận dữ liệu mới | Cùng sự việc/snapshot không nhân đôi; sự việc khác không bị nuốt; dữ liệu mới liên kết/xét version, không xóa lịch sử |
| UAT-07 | Hai kiểm soát cùng nhận một hồ sơ, có hồ sơ quá hạn | Nhận/chuyển/lọc hàng đợi | Một owner hiện hành, người còn lại được báo xung đột; thứ tự ưu tiên đúng; chuyển người không reset hạn |
| UAT-08 | Bộ nguồn có mã, chữ có/không dấu, thời gian biên và nguồn trễ | Tìm mã, AND/OR bộ lọc, phân trang, tìm văn bản | Kết quả đúng ngữ nghĩa tài liệu 16; không lặp/mất giữa trang trong cùng snapshot; watermark hiện; không kết quả khác nguồn chưa khả dụng |
| UAT-09 | GPS có khoảng trống/đến trễ, thiết bị dùng luân phiên | Mở timeline/quan hệ | Tách event/received time và hiển thị timezone; không vẽ khoảng trống như hành trình chắc chắn; quan hệ có thời hạn và nguồn |
| UAT-10 | Evidence có bản gốc, bản che, hash; một bản bị thay byte | Lưu, kiểm và viện dẫn khi duyệt | Tìm được nguồn/version/phép tính; phát hiện sai hash; bản lỗi không được coi đã xác minh; phân loại được support/refute/unclear |
| UAT-11 | Hồ sơ cần hỏi tài xế và chứa dữ liệu người khác | Soạn, xem trước, phát hành | Bản công bố có sự việc/câu hỏi/hỗ trợ; dữ liệu bên thứ ba được che; giữ bản phát hành; chưa giao thì chưa tính due_at |
| UAT-12 | Tài xế đúng chủ, có nháp và tệp đúng/sai loại, quá cỡ, mã quét lỗi | Gửi và bổ sung | Nội dung chữ có biên nhận; chỉ tệp hợp lệ được dùng; tệp cách ly không preview; bản bổ sung không ghi đè; tài xế biết phần thiếu |
| UAT-13 | Mạng ngắt sau khi server lưu; 10 người thử tác vụ trên di động | Retry cùng mã, đăng nhập lại, thực hiện tác vụ | Chỉ một lần gửi; đọc lại được biên nhận/nháp đã lưu; tài khoản khác không đọc nháp; thử khả dụng đạt NFR-08 với biên bản riêng |
| UAT-14 | Gửi lỗi, giao muộn, nhắc lặp, cuối tuần và yêu cầu gia hạn | Chạy đồng hồ/nhắc/hết hạn | Tính từ mốc giao theo lịch chính sách; không reset khi retry/chuyển owner; gia hạn có lý do/hạn cũ mới; im lặng không là thừa nhận |
| UAT-15 | Có phản bác chưa xét hoặc chưa có cơ hội giải trình, chỉ có điểm rủi ro | Đề xuất xác nhận gian lận | Bị chặn kèm trường thiếu; `inconclusive` có lý do dùng được; checklist bắt buộc đánh giá từng phần giải trình |
| UAT-16 | Đề xuất đủ căn cứ; người đề xuất tự duyệt; hai người duyệt cạnh tranh; có bổ sung sát lúc duyệt | Duyệt hoặc thử gây lỗi giữa giao dịch | Chặn tự duyệt; chỉ một quyết định trên version; không có quyết định thiếu audit; thông tin mới phải được xét trước duyệt |
| UAT-17 | Kết luận được duyệt và bản nội bộ có trường nhạy cảm | Công bố và bàn giao | Tài xế nhận đúng bản/phiên bản, lý do và hạn khiếu nại; bàn giao có người nhận; không đổi driver status/tiền từ thao tác này |
| UAT-18 | Quyết định đã công bố, có khiếu nại đúng/trễ hạn và căn cứ mới | Tiếp nhận, phân công, sửa/hủy kết luận | Người xử lý độc lập; bản cũ còn đọc; một version hiệu lực; yêu cầu trễ có xem xét lý do; tác vụ khắc phục được theo dõi |
| UAT-19 | Người khác/đơn vị khác, hồ sơ chưa công bố, URL tải cũ, phiên đã mất quyền | Thử list/search/count/detail/file/export và tự nâng quyền | Server từ chối, không lộ snippet/tổng số nhạy cảm; thu hồi đạt NFR-01; nội bộ đặc quyền cần MFA; log không lộ token/nội dung cá nhân |
| UAT-20 | Có đọc nguồn nhạy cảm, tìm kiếm, đổi trạng thái, export và truy cập khẩn cấp | Xem audit và thử sửa bằng quyền vận hành | Đủ actor/thời gian/object/version/lý do/kết quả; không sửa/xóa được; timestamp có thể đối chiếu; thiếu event được phát hiện |
| UAT-21 | Hồ sơ có bản gốc và bản tài xế, người xuất có/không có quyền riêng | Export và tải bằng tài khoản khác hoặc sau thu hồi | Đúng bản che, manifest/hash/source, người nhận/mục đích; tải kiểm quyền lại; audit đủ; không đọc được bản gốc qua link dẫn xuất |
| UAT-22 | Dữ liệu gồm TP=30, FP=10, inconclusive=5, pending=5; 2/10 khiếu nại đã xử lý bị đảo | Xem báo cáo trên cohort cố định | Precision=75% trên 40 hồ sơ đã đủ nhãn; hiển thị 10/50 bị loại và lý do; đảo kết luận=20% trên 10 khiếu nại; không gọi đây là recall |
| UAT-23 | Quy tắc mới ở nháp, có tập thử và snapshot bản cũ | Thử, duyệt độc lập, kích hoạt rồi rollback | Người tạo không tự duyệt; bản mới có hiệu lực đúng lịch; cảnh báo cũ giữ tham số/điểm cũ; rollback không đổi kết luận |
| UAT-24 | Hồ sơ hết hạn, một hồ sơ có hold, dữ liệu nằm trong index/export/backup | Xử lý yêu cầu dữ liệu, chạy purge rồi diễn tập restore | Thẩm định căn cứ; hold chặn đúng phạm vi; dữ liệu/index/bản quản lý được đối soát; backup theo lịch riêng; restore áp lại yêu cầu xóa |
| UAT-25 | Nhãn có inconclusive, đang khiếu nại, tổng hợp, đã xác minh, có bất đồng hai người | Tạo tập đánh giá và sửa nhãn sau khiếu nại | Loại/đánh dấu đúng; có người phân xử; tách thời gian/sự việc; công bố mẫu không cảnh báo; version nhãn thay đổi được truy nguyên |
| UAT-26 | Tài xế chọn chuyến mình, chuyến người khác, vấn đề đã tồn tại hoặc sự cố an toàn | Gửi báo vấn đề | Ownership được kiểm; có biên nhận; liên kết hồ sơ trùng; chuyển kênh phù hợp, không tự gắn nhãn gian lận |
| UAT-27 | Môi trường và dữ liệu tải theo NFR-05/06 | Chạy truy vấn hỗn hợp và batch, đo từ event đến index | Đạt p95 tương ứng; báo độ trễ nguồn, lỗi và cache lạnh riêng; không chỉ đo API trống hoặc dữ liệu mẫu nhỏ |
| UAT-28 | Có backup/tệp/index, giao dịch sau mốc backup, cấu hình có thể rollback | Mô phỏng gián đoạn và phục hồi có kiểm soát | Biên bản chứng minh RPO/RTO, đối soát phần cần replay, hash và phiên bản sau restore; báo phạm vi mất dữ liệu nếu có; chỉ mở lại khi kiểm xong |

## Điều kiện vào, ra và bằng chứng nghiệm thu

Điều kiện vào UAT: baseline BA được chủ nghiệp vụ chốt, tài khoản/nguồn tổng hợp sẵn sàng, test kỹ thuật cốt lõi pass, kênh thông báo thử được kiểm soát, có lịch chính sách và vai trò độc lập. Môi trường tách dữ liệu thật; tác vụ bàn giao không thực hiện chế tài thật.

Điều kiện ra pilot: 100% kịch bản Must và test con về quyền/toàn vẹn/quyết định/giải trình/khiếu nại đạt; không còn lỗi nghiêm trọng gây lộ dữ liệu, mất bằng chứng, sai chủ thể hoặc kết luận sai luồng. Có biên bản đo tải, phục hồi và chất lượng nhãn; quy tắc/SLA/quyền nguồn được chấp thuận; có người trực xử lý sự cố và hướng dẫn tài xế. Ngưỡng chất lượng phát hiện phải được chốt từ baseline, không lấy 6 hồ sơ tổng hợp làm chứng minh.

Mẫu ghi nhận kết quả cho từng test con: `UAT ID / build / data version / người thực hiện / thời điểm / kết quả mong đợi / kết quả thực tế / bằng chứng / lỗi liên quan / người chấp nhận`. Pass/fail là kết quả thực thi, không điền sẵn khi lập kế hoạch. Mọi ngoại lệ cần nêu ảnh hưởng, người chịu trách nhiệm, hạn khắc phục và cổng triển khai bị ảnh hưởng.
