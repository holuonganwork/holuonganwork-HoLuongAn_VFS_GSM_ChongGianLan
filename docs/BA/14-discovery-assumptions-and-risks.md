# Khám phá nghiệp vụ, giả định và rủi ro

## Kế hoạch discovery từ điểm bắt đầu

Chưa thực hiện phỏng vấn hoặc thu dữ liệu thật. Kế hoạch 1–2 tuần dưới đây là đề xuất để kiểm chứng hướng đi, không phải biên bản đã làm. Chỉ dùng hồ sơ được doanh nghiệp cho phép, đã giảm dữ liệu cá nhân cần thiết.

| Hoạt động | Người tham gia / mẫu đề xuất | Đầu ra và tiêu chí đủ |
| --- | --- | --- |
| Workshop mục tiêu và quy chế | Sponsor, kiểm soát, vận hành tài xế, pháp chế, Finance | Chốt hành vi nào thuộc phạm vi; ai kết luận/duyệt/khiếu nại; thống nhất từ gian lận và lỗi vận hành |
| Quan sát xử lý hồ sơ | 4–6 kiểm soát viên, khác kinh nghiệm; 12–20 hồ sơ gồm xác nhận/bác/thiếu căn cứ/khiếu nại | As-is có thời gian thao tác/chờ, hệ thống nguồn và điểm bàn giao; không chọn chỉ hồ sơ dễ |
| Phỏng vấn tài xế | 10–12 người khác thâm niên/khu vực/thiết bị, gồm người từng giải trình và chưa từng | Hiểu thông báo, khả năng có bằng chứng, mạng/thiết bị, trở ngại khiếu nại; tránh chỉ chọn tài xế bị nghi |
| Kiểm kê dữ liệu | Chủ nguồn chuyến/GPS/thiết bị/thưởng, Security | Dictionary, mẫu đã che, độ đầy đủ/trễ, quyền truy cập, khả năng lưu snapshot; chưa có thì ghi rõ |
| Thẩm định nhãn | Hai người độc lập đọc 30–50 hồ sơ mẫu, người thứ ba xử lý bất đồng | Checklist đủ căn cứ, tỷ lệ đồng thuận, danh sách trường hợp chưa biết; mẫu này không đủ tự khẳng định tỷ lệ gian lận toàn đội |
| Thử tác vụ và bản mẫu | 5 kiểm soát + 10 tài xế, dữ liệu tổng hợp | Thời gian tìm nguồn/đọc yêu cầu/gửi phản hồi; lỗi thao tác và nội dung khó hiểu |
| Workshop chốt baseline | Chủ các BR, kiến trúc và QA | Danh sách quyết định/giả định, phạm vi pilot, ngưỡng đề xuất, backlog ước lượng và cổng tiếp theo |

## Bộ câu hỏi phỏng vấn ưu tiên

| Mã | Câu hỏi cần trả lời | Người trả lời / quyết định bị ảnh hưởng |
| --- | --- | --- |
| Q-01 | Dịch vụ nào, thị trường nào, tài xế là nhân viên hay đối tác, quy chế nào có hiệu lực? | Sponsor/pháp chế; scope và ngôn ngữ quyết định |
| Q-02 | Một hồ sơ gần nhất mất bao lâu ở từng bước, phải mở những hệ thống nào? | Kiểm soát; baseline OBJ-01 và FR-05/06 |
| Q-03 | Điều gì phân biệt đủ căn cứ, chưa đủ căn cứ, lỗi dữ liệu và vi phạm chất lượng? | Người duyệt/pháp chế; RULE-08 và checklist |
| Q-04 | Ai được phát hành yêu cầu, duyệt kết luận, xử lý khiếu nại; có đủ người độc lập không? | Trưởng kiểm soát; quyền và phân công |
| Q-05 | Tài xế hiện nhận thông báo ở đâu, làm gì khi không đăng nhập/không còn thiết bị? | Tài xế/vận hành; kênh phản hồi và hỗ trợ |
| Q-06 | Tài xế có thể cung cấp dữ kiện nào, câu hỏi nào khó hiểu, hạn nào khả thi? | Tài xế; mẫu giải trình, SLA và UX |
| Q-07 | GPS có accuracy/sequence/received time không, độ trễ và sự cố app được lưu ở đâu? | Mobile/Data; loại bỏ nhiễu và DR-02/03 |
| Q-08 | Thiết bị là thiết bị cá nhân hay được cấp, ID có bị thay/đặt lại, có lịch cấp phát không? | Đội xe/Identity; RULE-03 và phản bác |
| Q-09 | Chính sách thưởng được version thế nào, xác nhận đã chi/đảo/thu hồi từ nguồn nào? | Finance/chủ thưởng; tiền và RULE-04/13 |
| Q-10 | Căn cứ, quyền truy cập, thời hạn lưu và bên nhận dữ liệu từng nguồn là gì? | Pháp chế/đầu mối dữ liệu; FR-15/20 |
| Q-11 | Một ngày có bao nhiêu nghi vấn, bao nhiêu người xử lý, hồ sơ tồn/đảo kết luận là bao nhiêu? | Trưởng kiểm soát; ưu tiên, KPI và năng lực pilot |
| Q-12 | Điều kiện nào khiến pilot dừng, chấp nhận hoặc mở rộng; ngân sách và người trực là ai? | Sponsor/Operations; roadmap và business case |

Không đặt câu hỏi dẫn dắt như “tài xế dùng GPS giả vì lý do gì” khi hành vi chưa xác minh. Nên yêu cầu mô tả một sự việc cụ thể và dữ kiện đã xem; phân biệt lời kể với tài liệu đối chiếu.

## Sổ giả định

| Mã | Giả định đang dùng | Rủi ro nếu sai | Cách xác minh / owner / thời hạn |
| --- | --- | --- | --- |
| A-01 | Vận tải hành khách tại Việt Nam, một đơn vị pilot | Sai loại dữ liệu và quy chế | Q-01; Sponsor; G0 |
| A-02 | Phối hợp có cổng tài xế và kênh hỗ trợ là phạm vi đích | Khác hướng prototype/kiến trúc cũ | Chốt DEC-01 theo đề tài hiện tại; Product; G0 |
| A-03 | Liên kết định danh chuyến–GPS–tài xế đáng tin cậy | Gắn nhầm người/hồ sơ | Profiling và DR-01; Data; G1 |
| A-04 | Có quyền dùng dữ liệu thật cho mục đích pilot | Không đủ điều kiện xử lý | Ma trận mục đích/căn cứ/nguồn; pháp chế; G1 |
| A-05 | Có kênh thông báo và hỗ trợ khi tài xế không vào được | Không có cơ hội giải trình thực chất | Thử gửi/giao và tác vụ hỗ trợ; Operations; G1 |
| A-06 | Có tối thiểu ba người phù hợp để tách điều tra/duyệt/khiếu nại | Tự duyệt hoặc tắc hàng đợi | Chốt phân công và thay thế khi vắng; trưởng kiểm soát; G1 |
| A-07 | Bốn nhóm quy tắc đủ có ích để thử giá trị | Nhiễu cao, không có tác động kinh tế | Nhãn mẫu, shadow run và baseline; Risk; G2 |
| A-08 | SLA 48 giờ phản hồi, 7 ngày khiếu nại khả thi | Tài xế khó đáp ứng/quá tải | Q-06, thử tác vụ, quy chế; Operations/pháp chế; G0 |
| A-09 | Chưa thể xác nhận payout qua tích hợp hiện có | Sai kỳ vọng số tiền thu hồi | Q-09; Finance; G1; cho phép xác minh thủ công có chứng từ |
| A-10 | Tải pilot/NFR và lịch 8–12 tuần là khả thi | Thiếu nguồn lực hoặc chậm tích hợp | Ước lượng sau inventory; Tech Lead/Sponsor; G0 rồi rà lại G1 |

G0–G3 là cổng của [lộ trình](15-mvp-roadmap-and-business-case.md). Mọi giả định hiện ở trạng thái **Chưa xác nhận**; không tự chuyển thành fact chỉ vì đã được dùng trong thiết kế.

## Rủi ro ưu tiên

Mức khả năng/ảnh hưởng là đánh giá BA ban đầu, cần điều chỉnh sau discovery.

| Mã | Rủi ro | Khả năng / ảnh hưởng | Giảm thiểu và dấu hiệu cần hành động | Owner |
| --- | --- | --- | --- | --- |
| RISK-01 | Gắn nhầm tài xế do khóa/nguồn lỗi | Trung bình / rất cao | Kiểm quan hệ, quarantine; phát hiện sai chủ thể thì dừng phát hành nhóm ảnh hưởng | Data Lead |
| RISK-02 | Kết luận nhầm vì GPS/thiết bị/chuyến hợp lệ | Cao / cao | Checklist phản bác, mẫu độc lập, chặn tự kết luận; theo dõi đảo và nhãn chưa biết | Risk Lead |
| RISK-03 | Lộ dữ liệu người khác qua tìm kiếm/tệp/export | Trung bình / rất cao | Kiểm quyền đồng nhất, bản che và UAT-19/21; có lỗi thì dừng đường truy cập ảnh hưởng | Security |
| RISK-04 | Tài xế không nhận hoặc không hiểu yêu cầu | Cao / cao | Mốc giao, hỗ trợ và thử tác vụ; không tính hết hạn khi lỗi giao | Operations |
| RISK-05 | Cảnh báo vượt năng lực xử lý | Cao / cao | Giới hạn cohort, theo dõi backlog, giảm tỷ lệ lấy vào có ghi nhận; không tự đóng để đạt SLA | Trưởng kiểm soát |
| RISK-06 | Nhãn huấn luyện nhiễm quyết định cũ/sai lệch chọn mẫu | Cao / cao | Nhãn độc lập, version, dữ liệu không cảnh báo, tách thời gian; chưa đủ thì không mở ML | Data Science |
| RISK-07 | Chế tài dựa trực tiếp vào risk score | Trung bình / rất cao | Tách quyết định và bàn giao, vô hiệu nhánh tự xác nhận trong pilot, diễn tập UAT-17 | Product/Risk |
| RISK-08 | Bằng chứng bị sửa hoặc mất sau nguồn thay đổi | Trung bình / cao | Snapshot/hash/audit và restore; lỗi toàn vẹn thì chặn dùng nguồn liên quan để duyệt | Data/Operations |
| RISK-09 | Thiếu căn cứ/lịch lưu hoặc thay đổi quy định | Trung bình / cao | Danh mục nghĩa vụ được thẩm định, rà lại trước dùng dữ liệu thật và trước mở rộng | Pháp chế |
| RISK-10 | Không đủ người độc lập hoặc có xung đột lợi ích | Trung bình / cao | Điều phối ngoài chuỗi hiện tại, quyền theo hồ sơ, audit và escalation | Sponsor |

## Sổ quyết định cần chốt

| Mã | Khuyến nghị BA | Ai quyết định / khi nào | Trạng thái |
| --- | --- | --- | --- |
| DEC-01 | Lấy phối hợp hai bên làm phạm vi đích; cập nhật kiến trúc sau khi baseline thống nhất | Product + kiến trúc; G0 | Đề xuất theo yêu cầu hiện tại |
| DEC-02 | MVP dùng quy tắc và phê duyệt độc lập; chưa tự xác nhận gian lận | Risk Lead + Sponsor; G0 | Đề xuất |
| DEC-03 | Dùng một hồ sơ/tài xế/sự việc, liên kết các hồ sơ nhóm ở nội bộ | Trưởng kiểm soát + Data; G0 | Đề xuất |
| DEC-04 | Thông qua SLA, lịch, cơ hội phản hồi, khiếu nại và ngoại lệ | Operations + pháp chế; G0 | Chờ quy chế thật |
| DEC-05 | Thông qua căn cứ dữ liệu, lịch lưu, quyền theo nguồn và tệp | Đầu mối dữ liệu + pháp chế; G1 | Chờ inventory |
| DEC-06 | Chốt quy mô, mức chất lượng, nguồn lực, tiêu chí dừng/mở rộng | Sponsor + Finance + Risk; G0/G2 | Chờ baseline và ước lượng |

Các quyết định trên dành cho vòng thẩm định sản phẩm sau BA; không phải yêu cầu người đọc cấp phép cho việc viết bộ tài liệu này.
