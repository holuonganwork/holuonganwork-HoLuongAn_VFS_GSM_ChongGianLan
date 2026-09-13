# MVP, lộ trình và mô hình lợi ích

## Mục tiêu của MVP

MVP phải chứng minh trọn một vòng: nhận dữ liệu → tạo nghi vấn → tìm và kiểm chứng nguồn → tài xế giải trình → duyệt độc lập → công bố → khiếu nại khi phát sinh. Có thể giới hạn số tài xế, nguồn và loại tệp, nhưng không gọi một dashboard chỉ đọc là MVP phối hợp hai bên.

Phạm vi Must gồm FR-01–FR-22 và NFR tương ứng. Giới hạn thực hiện ban đầu: batch thay vì streaming, một đơn vị, một ngôn ngữ, bốn nhóm quy tắc, web di động, tệp JPG/PNG/PDF, bàn giao xử lý thủ công, một vòng khiếu nại thông thường. OCR/ngữ nghĩa/ML, nhiều tầng quan hệ và tích hợp thi hành chế tài nằm ngoài đợt này.

## Lộ trình tham chiếu

**8–12 tuần là khung lập kế hoạch giả định**, không phải cam kết giao hàng. Dùng để thảo luận với đội có kinh nghiệm và có quyền tiếp cận hệ thống nguồn; cần ước lượng lại sau discovery. Không bắt đầu đồng hồ triển khai khi các phụ thuộc quan trọng chưa có owner/ngày sẵn sàng.

| Đợt | Khoảng tham chiếu | Phạm vi và đầu ra | Điều kiện kết thúc |
| --- | --- | --- | --- |
| P0 — Discovery | 1–2 tuần | As-is đã xác nhận, inventory, baseline ban đầu, quy chế, mẫu trải nghiệm, phân rã backlog | G0: thống nhất mục tiêu, phạm vi và kế hoạch dữ liệu/nhân sự |
| P1 — Nền tảng hồ sơ nội bộ | 3–4 tuần | FR-01–07, FR-15–17, nền FR-19/20; xác thực, quyền, nguồn/snapshot, tìm kiếm và thao tác điều tra | G1: quyền dữ liệu đã thẩm định; hệ thống đủ an toàn để bắt đầu thử nội bộ với nguồn được phép |
| P2 — Phối hợp và quyết định | 2–3 tuần | FR-08–14, FR-22; hoàn tất FR-18–21, SLA, upload, duyệt, khiếu nại, báo cáo và nhãn | G2: UAT Must đạt, quy tắc/SLA chốt, chất lượng shadow run và diễn tập vận hành đủ để mở pilot |
| P3 — Pilot có kiểm soát | 2–3 tuần hoặc kéo dài đủ cửa sổ nhãn | Cohort giới hạn, hỗ trợ tài xế, đo KPI, kiểm mẫu không cảnh báo, khiếu nại và khắc phục | G3: báo cáo giá trị/chất lượng, quyết định mở rộng, chỉnh hướng hoặc dừng |

Tổng thời gian pilot có thể dài hơn 12 tuần nếu cần đủ một chu kỳ thưởng hoặc chờ kết thúc khiếu nại. Không ép nhãn chưa chín để đạt ngày kết thúc kế hoạch. P1 là mốc nội bộ, chưa công bố sản phẩm phối hợp đã hoàn chỉnh.

## Backlog theo giá trị và phụ thuộc

| Epic | Yêu cầu | Phụ thuộc chính | Định nghĩa hoàn tất |
| --- | --- | --- | --- |
| E-01 — Dữ liệu đúng chủ thể | FR-01, FR-02, FR-03 | Chủ nguồn, khóa, metadata và quy tắc | Đối soát batch, không trùng, nguồn và chất lượng kiểm được |
| E-02 — Tìm nguồn và dựng hồ sơ | FR-04, FR-05, FR-06, FR-07 | E-01; quyền E-06 | Kiểm soát hoàn thành tác vụ tìm nguồn và lưu căn cứ/refute |
| E-03 — Tài xế tham gia | FR-08, FR-09, FR-10, FR-22 | E-02; identity, kênh giao, quyền E-06 | Thử trên di động gồm lỗi mạng/giao và hỗ trợ gửi hộ |
| E-04 — Quyết định và khiếu nại | FR-11, FR-12, FR-13, FR-14 | E-03; quy chế, người độc lập | Đủ vòng kết luận–xem lại–khắc phục với version/audit |
| E-05 — Chất lượng và cải tiến | FR-18, FR-19, FR-21 | E-01/04; phương pháp nhãn và mẫu | KPI có mẫu số, rule version, rollback, kiểm mẫu độc lập |
| E-06 — Quyền và quản trị dữ liệu | FR-15, FR-16, FR-17, FR-20 | Identity, chính sách dữ liệu, nơi lưu tệp | Quyền toàn đường đi, export che, audit, hold/xóa/restore |

E-06 phải được thiết kế ngay đầu P1 và hoàn thiện cùng các epic; không xếp bảo mật vào phần bổ sung sau khi đưa tài xế vào hệ thống. Mỗi story Ready khi có mẫu dữ liệu, quyền, trạng thái, ngoại lệ và UAT; Done khi hành vi đã chứng minh trên build xác định, có hướng dẫn vận hành và người chấp nhận.

## Cổng quyết định

- **G0 — Chốt bài toán:** Sponsor chấp nhận OBJ/BR, DEC-01–04, dự kiến nhân sự/ngân sách và người chịu trách nhiệm dữ liệu; baseline còn thiếu có kế hoạch đo rõ.
- **G1 — Sẵn sàng nguồn và nền tảng:** khóa đúng, mục đích/quyền/lưu dữ liệu được thẩm định; quyền và snapshot có kiểm chứng; quy trình sự cố/restore sẵn sàng theo phạm vi thử.
- **G2 — Mở pilot:** UAT và chất lượng kỹ thuật theo tài liệu 11 đạt; có nhóm độc lập xử lý/khiếu nại, kênh tài xế dùng được; giới hạn cohort/rule; đủ năng lực hàng đợi và có quy trình dừng.
- **G3 — Mở rộng:** đo được giảm công tìm nguồn, chất lượng quyết định/kênh phản hồi đạt ngưỡng đã thống nhất, không có lỗi nghiêm trọng còn mở; Finance xác nhận business case có lợi ích ròng phù hợp. Chưa đủ mẫu thì kéo dài hoặc giữ phạm vi, không tự suy kết quả tốt.

Điều kiện dừng/thu hẹp ngay: sai chủ thể, rò rỉ dữ liệu, sai tính toàn vẹn trọng yếu, tự động tác động tài khoản/tiền ngoài phạm vi, hoặc thiếu người xử lý khiến không còn đáp ứng quyền phản hồi. Tăng lỗi dữ liệu/cảnh báo nhiễu thì dừng quy tắc/nguồn bị ảnh hưởng, giữ các hồ sơ đã tạo và xử lý tới cùng. Không dừng cả kênh khiếu nại khi dừng phát hiện mới.

## Năng lực và nguồn lực

Nhóm tham chiếu: 1 BA/PO, 1 Tech Lead, 2–3 kỹ sư ứng dụng, 1 kỹ sư dữ liệu, 1 QA; UX, Security, pháp chế và Finance tham gia theo đợt. Phía nghiệp vụ cần nhóm kiểm soát và người duyệt/khiếu nại độc lập. Đây là giả định lập kế hoạch, không phải số người đã có hoặc dự toán nhân sự được phê duyệt.

Năng lực xử lý/ngày = `số người × giờ làm hồ sơ/ngày × hệ số dành cho xử lý × 60 / phút công trung bình mỗi hồ sơ`. Phút công phải gồm triage, thu thập, đánh giá, duyệt và phần khiếu nại phân bổ; không gồm thời gian chờ tài xế. Ví dụ tổng hợp: 3 người × 4 giờ × 75% × 60 / 30 phút = **18 hồ sơ/ngày**. Nếu nhận 25 hồ sơ/ngày thì backlog tăng 7/ngày; cần giảm cohort/cảnh báo hoặc tăng năng lực. Với cùng giả định, 5 người xử lý được 30 hồ sơ/ngày. Công thức này không thay cho yêu cầu vai trò độc lập và độ phức tạp thực tế.

## Business case có thể thay số

Đơn vị tiền: VND. Công thức theo tháng:

`Tiết kiệm công = Q × (T_trước − T_sau) / 60 × C_giờ`

`Lợi ích ròng = tiết kiệm công + L_xác_nhận − chi phí vận hành tăng thêm − chi phí xây dựng phân bổ`

`L_xác_nhận` là lợi ích tổn thất tránh được/thu hồi được Finance chấp thuận phương pháp quy kết, không là tổng tiền bị gắn cờ. Một khoản không được vừa tính “tránh mất” vừa tính “thu hồi”. Tiết kiệm thời gian có thể chỉ tạo thêm năng lực, chưa trở thành dòng tiền tiết kiệm; báo riêng hai góc nhìn.

**Ví dụ hoàn toàn giả định, không phải báo giá hay dữ liệu doanh nghiệp:** T_trước=45 phút, T_sau=30 phút, C_giờ=120.000; chi phí vận hành tăng thêm=30 triệu/tháng; xây dựng phân bổ=15 triệu/tháng. Các giá trị phải được thay bằng dữ liệu đã xác nhận.

| Đầu vào/kết quả tháng | Thận trọng | Cơ sở giả định | Thuận lợi |
| --- | ---: | ---: | ---: |
| Hồ sơ đủ điều kiện Q | 200 | 500 | 1.000 |
| Giờ công tiết kiệm | 50 | 125 | 250 |
| Giá trị công tiết kiệm | 6 triệu | 15 triệu | 30 triệu |
| Lợi ích tổn thất xác nhận giả định | 0 | 20 triệu | 60 triệu |
| Tổng chi phí tăng thêm + phân bổ | 45 triệu | 45 triệu | 45 triệu |
| Lợi ích ròng | −39 triệu | −10 triệu | +45 triệu |

Với Q=500, cần lợi ích tổn thất xác nhận **ít nhất 30 triệu/tháng** để hòa vốn theo mô hình này; cao hơn mức đó mới có lợi ích ròng dương. Kịch bản cơ sở minh họa chưa hòa vốn, nên chưa có căn cứ kinh tế để chấp thuận mở rộng. Discovery/pilot phải làm rõ năng lực tiết kiệm thật, chi phí và phần lợi ích quy kết được.

Trước quyết định đầu tư, Finance cần bổ sung CAPEX ban đầu, số tháng phân bổ, chi phí lưu trữ/GPS/tệp/thông báo, nhân sự review/khiếu nại, vận hành, đào tạo, sai quyết định và khắc phục. Nếu báo thời gian hoàn vốn, dùng dòng tiền tăng thêm thực nhận và vốn ban đầu; không lấy con số lợi ích ròng đã trừ phân bổ rồi tiếp tục trừ vốn lần nữa.

## Vận hành và chuyển giao

Ban hành hướng dẫn triage, đọc nguồn/phản bác, viết yêu cầu, duyệt, khiếu nại, sự cố và export. Đào tạo kiểm soát bằng cả hồ sơ dương/âm/chưa biết; tài xế bằng ví dụ yêu cầu trung tính và thao tác phản hồi. Hằng ngày xem tồn/quá hạn/giao lỗi; hằng tuần review chất lượng theo mẫu và nhãn đảo. Mỗi đợt quy tắc có owner, lịch hiệu lực và rollback; mỗi nguồn có người trực khi lỗi.
