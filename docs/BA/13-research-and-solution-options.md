# Nghiên cứu tham chiếu và lựa chọn hướng đi

## Câu hỏi nghiên cứu và kết luận đề xuất

Cần giải quyết ba câu hỏi: hệ thống phải giúp quyết định điều gì; bằng chứng và trao đổi hai bên cần được tổ chức ra sao; mức tự động hóa nào phù hợp khi chưa có dữ liệu/nhãn thật. Hướng đề xuất là **quy tắc giải thích được + tìm kiếm và hồ sơ bằng chứng + giải trình/khiếu nại + quyết định độc lập**. ML và trợ lý ngôn ngữ là các bước thử nghiệm sau khi có baseline và dữ liệu đáng tin cậy.

Cơ sở nghiên cứu gồm mã/tài liệu repository và nguồn công khai của bên vận hành, cơ quan tiêu chuẩn, nhà phát triển nền tảng và Chính phủ. Phạm vi là nghiên cứu bàn, không gồm phỏng vấn, mua thử sản phẩm hay kiểm chứng thống kê gian lận của doanh nghiệp. Ngày truy cập nguồn: **13/09/2026**. Nguồn được dùng trong đúng bối cảnh, không suy chính sách của Uber/Grab thành quy định của GSM/VFS.

## Phát hiện có nguồn và hàm ý thiết kế

| Nguồn | Sự kiện đã kiểm tra | Hàm ý BA đề xuất và giới hạn áp dụng |
| --- | --- | --- |
| S-01 | Uber mô tả Risk Entity Watch dùng phát hiện bất thường ở cấp thực thể, giải thích dấu hiệu và đưa kết quả cho người xem xét | Tách dấu hiệu, đánh giá và kết luận; so bối cảnh/thời gian trước khi quy kết. Bài kỹ thuật năm 2023, không cung cấp tỷ lệ phát hiện cho dữ liệu của dự án. [Uber Engineering](https://www.uber.com/us/en/blog/risk-entity-watch/) |
| S-02 | Trang Uber UK mô tả phần mềm phát hiện, đội chuyên trách xem xét, thông báo và kênh đề nghị xem lại | Thiết kế thông báo có lý do và khả năng phản hồi. Đây là thực hành theo trang thị trường UK, không là thời hạn/pháp luật Việt Nam. [Uber Driver App — Fraud activities](https://www.uber.com/gb/en/drive/driver-app/fraud-activities/) |
| S-03 | Grab Việt Nam công bố cập nhật FairPlay 2024: tiếp nhận phản hồi từ đối tác/người dùng, xác minh và phân định loại vấn đề thuộc chương trình | Tài xế có thể là nguồn thông tin; cần sàng lọc vấn đề đúng kênh và bảo vệ người báo. Bài về chương trình 2024, không khẳng định mức thưởng hoặc điều kiện còn áp dụng năm 2026. [Grab FairPlay 2024](https://www.grab.com/vn/blog/driver/bike/grabfairplay2024/) |
| S-04 | NIST IR 8387, mục 3.2, trình bày bảo quản bằng chứng số, ghi xuất xứ và bảo vệ giá trị hash | Cần bản gốc, lịch sử thu nhận/chuyển giao và kiểm tra toàn vẹn; hash không tự chứng minh sự thật trước lúc thu. Tài liệu thiên về bảo quản trong điều tra pháp lý; thiết kế ở đây là vận dụng nghiệp vụ, không là chứng nhận giá trị tố tụng. [NIST IR 8387](https://nvlpubs.nist.gov/nistpubs/ir/2022/NIST.IR.8387.pdf) |
| S-05 | Cổng văn bản Chính phủ ghi Luật 91/2025/QH15 ban hành 26/06/2025, hiệu lực 01/01/2026 | Baseline pháp lý cho rà soát dữ liệu cá nhân phải xét văn bản đã có hiệu lực năm 2026. Chưa kết luận căn cứ xử lý cụ thể của doanh nghiệp. [Luật Bảo vệ dữ liệu cá nhân](https://vanban.chinhphu.vn/?docid=214590&pageid=27160) |
| S-06 | Cổng văn bản Chính phủ ghi Nghị định 356/2025/NĐ-CP ban hành 31/12/2025, hiệu lực 01/01/2026, hướng dẫn thi hành Luật Bảo vệ dữ liệu cá nhân | Pháp chế cần đọc cùng luật và kiểm văn bản liên quan/chuyển tiếp khi phê duyệt triển khai; không chỉ dùng tài liệu pháp lý cũ. [Nghị định 356/2025/NĐ-CP](https://vanban.chinhphu.vn/?classid=1&docid=216387&pageid=27160) |
| S-07 | NIST AI RMF 1.0 tổ chức quản trị rủi ro theo Govern, Map, Measure, Manage; trang hiện ghi bản 1.0 đang được cập nhật | Nếu dùng AI, phải có người chịu trách nhiệm, đo chất lượng, theo dõi rủi ro và khả năng dừng/điều chỉnh. Đây là khung tự nguyện tham khảo; cập nhật lại trước triển khai AI. [AI RMF Core](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/) |
| S-08 | Android Location cung cấp accuracy theo bán kính ước lượng và thời gian/nguồn vị trí; tài liệu nêu các nguồn có thể dùng đồng hồ khác nhau | Cần giữ metadata và phân biệt thời gian sự kiện/tiếp nhận; đường nối tọa độ không tự chứng minh thao túng. Không suy độ tin cậy của OS này cho mọi thiết bị. [Android Location](https://developer.android.com/reference/android/location/Location#getAccuracy()) |

Không có nguồn nào ở trên cung cấp mức thất thoát, tỷ lệ dương tính giả hoặc mức giảm chi phí của doanh nghiệp đang nghiên cứu. Vì vậy, KPI và business case của bộ BA là kế hoạch đo và mô hình giả định.

## So sánh các hướng giải quyết

| Phương án | Giá trị có thể tạo | Đánh đổi và điều kiện |
| --- | --- | --- |
| A. Báo cáo/quy tắc, xử lý trên công cụ rời | Ra báo cáo nhanh, hỗ trợ rà soát ban đầu | Khó giữ liên kết nguồn–giải trình–quyết định; cần kỷ luật vận hành mạnh để không thất lạc |
| B. Hồ sơ bằng chứng và phối hợp hai bên, dùng quy tắc trước | Bao phủ đề tài; kiểm chứng hiệu quả tìm nguồn, phản hồi, duyệt và khiếu nại | Cần đầu tư phân quyền, dữ liệu và workflow trước pilot; chưa tối ưu mọi kiểu gian lận |
| C. ML/AI tự quyết định làm trung tâm ngay từ đầu | Có thể mở rộng phát hiện khi dữ liệu/nhãn trưởng thành | Chưa có nhãn/hiệu chỉnh; chi phí kết luận sai chưa biết; không giải quyết đủ kênh trao đổi/bằng chứng nếu chỉ tập trung mô hình |
| D. Cấu hình một nền tảng quản lý vụ việc bên ngoài | Có thể giảm thời gian làm workflow/audit cơ bản | Cần đánh giá kết nối GPS/chuyến, quyền theo đối tượng, vị trí dữ liệu, xuất/di chuyển và chi phí; chưa đánh giá nhà cung cấp cụ thể |

Ma trận dưới đây là **đánh giá BA giả định**, thang 1–5, điểm cao thuận lợi hơn. Không phải benchmark sản phẩm hoặc kết quả khảo sát. Trọng số cần Sponsor chốt tại discovery.

| Tiêu chí | Trọng số | A | B | C | D |
| --- | ---: | ---: | ---: | ---: | ---: |
| Thời gian kiểm chứng giá trị ban đầu | 20% | 5 | 4 | 2 | 3 |
| Khả năng truy nguyên/quản lý căn cứ | 25% | 2 | 5 | 3 | 4 |
| Đáp ứng phối hợp tài xế–kiểm soát | 25% | 1 | 5 | 2 | 3 |
| Phù hợp khi dữ liệu/nhãn còn thiếu | 15% | 4 | 4 | 1 | 3 |
| Công tích hợp/vận hành dự kiến thấp | 15% | 4 | 3 | 2 | 2 |
| Tổng có trọng số, tối đa 5 | 100% | 2,95 | 4,35 | 2,10 | 3,10 |

Chọn B làm **hướng sản phẩm**. Quyết định tự xây hay mua thành phần vẫn mở: có thể thực hiện B trên công nghệ hiện có hoặc nền tảng phù hợp. Cần demo cùng tác vụ tìm nguồn, phân quyền tài xế, lịch sử phiên bản và khiếu nại để so phương án D; chưa có cơ sở chốt mua một dịch vụ cụ thể.

## AI nên xuất hiện ở đâu

Giai đoạn đầu dùng quy tắc để tạo dữ kiện có thể đọc lại; ưu tiên hoàn thiện chất lượng nguồn và nhãn. Sau pilot có thể thử anomaly detection để mở rộng hàng nghi vấn và tìm kiếm ngữ nghĩa/OCR để giảm công đọc. Thử nghiệm phải đo trên thời gian khác tập phát triển, so cùng ngân sách điều tra và đánh giá cả nhóm không bị cảnh báo.

Nếu có trợ lý tóm tắt: chỉ dùng dữ liệu đúng quyền; mọi nhận định có liên kết evidence/source; chỉ rõ phần thiếu, không tự điền căn cứ; nội dung tệp là dữ liệu chứ không phải lệnh điều khiển; người dùng phải mở được đoạn gốc. Bản tóm tắt là dẫn xuất, không thay thế bằng chứng hoặc tự ban hành quyết định. Đây là đề xuất thiết kế cho giai đoạn sau, không thuộc Must MVP.

## Phạm vi rà soát pháp lý cần bàn giao

Nguồn S-05/S-06 đã kiểm tra tên, số, ngày ban hành và hiệu lực trên cổng chính thức; bản đính kèm là PDF quét. Bộ BA không thực hiện thẩm định toàn bộ điều khoản, tình trạng sửa đổi của mọi luật liên quan hoặc căn cứ áp dụng vào hợp đồng cụ thể. Danh sách việc pháp chế cần xác nhận gồm: mục đích và căn cứ cho từng loại dữ liệu; vai trò bên kiểm soát/xử lý; thông báo và quyền chủ thể; phân loại dữ liệu vị trí/tài chính/sinh trắc nếu phát sinh; thời hạn lưu/hold; chia sẻ bên thứ ba/chuyển dữ liệu; quy trình sự cố; giá trị bằng chứng điện tử; quy chế giải trình/chế tài phù hợp quan hệ lao động hoặc hợp tác.

Đây là các câu hỏi thẩm định, không phải khẳng định mọi cơ chế đều cần sự đồng ý, mọi dữ liệu phải lưu trong nước hoặc mọi hồ sơ phải giữ cùng một số năm. Trước sử dụng dữ liệu thật, cần danh mục nghĩa vụ có điều khoản, owner, bằng chứng tuân thủ và các yêu cầu phần mềm bị ảnh hưởng.

## Danh mục nguồn

| Mã | Tác giả/cơ quan, tên, ngày/phiên bản | Liên kết gốc và phần sử dụng |
| --- | --- | --- |
| S-01 | Christopher Settles và cộng sự, Uber, “Risk Entity Watch – Using Anomaly Detection to Fight Fraud”, 28/09/2023 | [Bài gốc](https://www.uber.com/us/en/blog/risk-entity-watch/), phần Background, Events and Entities, Anomaly Explanation |
| S-02 | Uber UK, “Fraud activities”; trang không nêu ngày xuất bản | [Trang gốc](https://www.uber.com/gb/en/drive/driver-app/fraud-activities/), quy trình review/thông báo và ví dụ hành vi |
| S-03 | Grab Việt Nam, “Cập nhật mới về chương trình Phản hồi gian lận – Grab Fairplay”, 30/01/2024 | [Trang gốc](https://www.grab.com/vn/blog/driver/bike/grabfairplay2024/), phạm vi phản hồi và xác minh |
| S-04 | Barbara Guttman, Douglas R. White, Shannan Williams, Tracy Walraven; NIST IR 8387, 09/2022 | [PDF](https://nvlpubs.nist.gov/nistpubs/ir/2022/NIST.IR.8387.pdf), mục 3.2, trang in 7–11 |
| S-05 | Quốc hội, Luật số 91/2025/QH15, 26/06/2025 | [Hồ sơ văn bản](https://vanban.chinhphu.vn/?docid=214590&pageid=27160), metadata; [bản ký](https://datafiles.chinhphu.vn/cpp/files/vbpq/2025/7/91qh.signed.pdf) để pháp chế đọc toàn văn |
| S-06 | Chính phủ, Nghị định số 356/2025/NĐ-CP, 31/12/2025 | [Hồ sơ văn bản](https://vanban.chinhphu.vn/?classid=1&docid=216387&pageid=27160), metadata; [bản ký](https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/01/356-nd.signed.pdf) để pháp chế đọc toàn văn |
| S-07 | NIST, AI RMF 1.0 (2023), AI RMF Core trên AI Resource Center | [Trang Core](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/), bốn chức năng và thông báo cập nhật |
| S-08 | Google, Android Developers, Location API reference, tài liệu cập nhật liên tục | [Location](https://developer.android.com/reference/android/location/Location), getAccuracy, getTime và metadata |

Nguồn nội bộ: [README](../../README.md), [fraud-rules](../fraud-rules.md), [data model](../data-model.md), [routes](../../backend/app/api/routes.py), [workflow service](../../backend/app/services/cases.py), [config](../../backend/app/core/config.py), [kiến trúc đề xuất trước đó](../new_architecture.md). Đây là trạng thái working tree đã quan sát ngày 13/09/2026, có thay đổi chưa commit; không coi là bản production.
