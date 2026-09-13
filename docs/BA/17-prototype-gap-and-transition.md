# Khoảng cách với prototype và hướng chuyển tiếp

## Cách đọc hiện trạng

Đối chiếu này dựa trên working tree quan sát ngày 13/09/2026, không phải audit production. Có nhiều thay đổi chưa commit trong repository. Bộ BA chỉ bổ sung tài liệu trong `docs/BA/`; chưa thay đổi code, API hoặc baseline kiến trúc bên ngoài thư mục này.

Nguồn chủ yếu: [README](../../README.md), [routes](../../backend/app/api/routes.py), [case service](../../backend/app/services/cases.py), [enums](../../backend/app/core/enums.py), [config](../../backend/app/core/config.py), [data model](../data-model.md), [fraud rules](../fraud-rules.md), [frontend README](../../frontend/README.md), [kiến trúc đề xuất trước đó](../new_architecture.md).

## Ma trận khoảng cách

| Năng lực | Quan sát trong prototype | BA đích / việc cần làm | FR liên quan |
| --- | --- | --- | --- |
| Nguồn và kiểm tra | Có PostgreSQL, dữ liệu tổng hợp, ràng buộc quan hệ, manifest | Thêm nguồn thật được phép, ingest/version, received time, watermark, chất lượng và quarantine | FR-01 |
| Phát hiện | Có bốn nhóm rule, snapshot, điểm có thể giải thích | Hiệu chỉnh bằng dữ liệu đã thẩm định, bổ sung metadata chất lượng và quản trị thay đổi | FR-02, FR-19 |
| Correlation | Có gom tín hiệu theo bằng chứng/chuyến và fingerprint; retry cùng snapshot chống trùng | Thiết kế liên kết vụ việc qua các batch/version; xem lại trước phát hành hồ sơ trùng sự việc | FR-03 |
| Tìm kiếm | List/filter hồ sơ/cảnh báo/tài xế, lấy nguồn theo evidence; phân trang | Tìm theo mã chuyến/thiết bị, thời gian, nội dung và nguồn với quyền, snippet, watermark, snapshot truy vấn | FR-05 |
| Giao diện | Dashboard độc lập chủ yếu đọc dữ liệu và xem kiến trúc/nguồn | Giao diện thao tác điều tra, bản công bố, cổng tài xế, thông báo và trạng thái lỗi | FR-04, FR-06, FR-08–14, FR-22 |
| Bằng chứng | Có evidence/source FK và đo lường; giữ được tham chiếu gốc | Bản chụp nguồn bất biến, hash/chain of custody, classification/refutation, bản che và export | FR-07, FR-17 |
| Tài xế giải trình | Có bảng lịch sử; endpoint ghi mới đã bị bỏ trong kiến trúc hiện hành | Luồng request/response mới có identity, delivery, receipt, version, upload và SLA | FR-08, FR-09, FR-10 |
| Quyết định | Có `auto_clear`, `auto_fraud`, `human_review`; adapter rule để probability/confidence là unknown nên đang đưa review | Giữ khả năng giải thích; MVP BA không sử dụng tự xác nhận gian lận; thêm đề xuất–người duyệt độc lập và checklist | FR-11, FR-12 |
| Quyền | Chưa có xác thực/phân quyền; reviewer là chuỗi do caller cung cấp | Identity đáng tin cậy, ownership/phân công/đơn vị, quyền trường/tệp/export; actor lấy từ phiên đăng nhập | FR-15 |
| Trạng thái | `detected`, `under_review`, hai trạng thái giải trình lịch sử, `confirmed_fraud`, `dismissed` | Tách case_status/resolution; bổ sung chưa đủ căn cứ/ngoài phạm vi/trùng; SLA và block reason | FR-04, FR-11–14 |
| Khiếu nại | Hồ sơ terminal không mở lại; một quyết định cuối/hồ sơ | Thực thể khiếu nại, quyết định có phiên bản, người độc lập và tác vụ khắc phục | FR-14 |
| Audit | Có status events, decision actor và snapshot | Audit đọc/tìm/xuất, identity xác thực, mục đích, quyền bất biến và đối soát | FR-16 |
| KPI và nhãn | Có thống kê/dashboard và ground truth tổng hợp | KPI có mẫu số/cohort, nhãn độc lập, lấy mẫu không cảnh báo và loại chưa xác định | FR-18, FR-21 |
| Vòng đời/tệp | Chưa có upload, object storage và quy trình lưu/xóa/hold hoàn chỉnh | Tệp quét/cách ly, lịch lưu, hold, xóa chỉ mục, backup/restore theo chính sách | FR-09, FR-20 |
| Tiền và chế tài | Không có tích hợp chi trả hoặc thay đổi driver status tự động | Tiếp tục tách tác động tài khoản/tiền; xác minh chứng từ và bàn giao người có thẩm quyền | FR-11, FR-13 |

Không được hiểu dữ liệu source FK là đã có bản chụp nội dung bất biến. Tương tự, hash manifest của dataset tổng hợp không thay thế quản lý hash và lịch sử thu nhận cho từng evidence trong sản phẩm thật.

## Các xung đột cần chuyển thành quyết định thiết kế

1. **Tài xế tham gia:** kiến trúc trước đó loại vai trò này; BA hiện tại đưa lại theo đề tài. Cần bổ sung actor, quyền, integration và workflow, không chỉ mở lại hai endpoint cũ vốn chưa có xác thực.
2. **Tự động kết luận:** code có nhánh tự xác nhận theo chính sách; BA đề xuất dùng máy để ưu tiên, người độc lập quyết định trong MVP. Trước pilot phải có kiểm tra không kích hoạt nhánh tự xác nhận; thay adapter/model không được vô tình bật lại.
3. **Quyết định có phiên bản:** ràng buộc một quyết định cuối và terminal không mở lại không đủ cho khiếu nại. Thiết kế mới cần giữ quyết định cũ, đánh dấu hiệu lực và liên kết quyết định kế tiếp.
4. **Bằng chứng và quyền:** response hiện trả thông tin liên kết nguồn/thiết bị/tài xế cho môi trường local; không dùng nguyên response đó làm API cho tài xế. Phải xây projection được kiểm duyệt và kiểm quyền ở server.

## Hướng migration nghiệp vụ đề xuất

| Bước | Việc cần thiết kế/thực hiện ở đợt phát triển | Điều kiện kiểm chứng |
| --- | --- | --- |
| 1. Chốt baseline | Thẩm định DEC, trạng thái, kết luận và quyền; cập nhật tài liệu kiến trúc trong thay đổi được giao riêng | Có quy tắc chuyển đổi được Product/Data/QA hiểu thống nhất |
| 2. Ánh xạ lịch sử | `detected → new`; `under_review → investigating`; giải trình lịch sử giữ nguyên và gắn nhãn legacy; terminal giữ kết luận gốc | Không tạo ra delivery, actor xác thực hoặc phê duyệt độc lập không từng tồn tại |
| 3. Kiểm tra nhãn terminal | `confirmed_fraud` lịch sử bảo tồn như kết luận legacy; `dismissed` cần đọc lý do trước ánh xạ `not_fraud/out_of_scope/inconclusive/duplicate` | Chưa phân loại được thì giữ nhãn legacy và không đưa vào nhãn huấn luyện chuẩn |
| 4. Thêm thực thể/phiên bản | Request, response, attachment, delivery, approval, appeal, decision version, lifecycle | Hồ sơ cũ đọc được; source và giải trình không mất; một quyết định hiện hành rõ |
| 5. Xác thực và bản công bố | Liên kết tài xế với identity được xác minh, tạo projection; dữ liệu cũ chưa duyệt chưa tự xuất hiện cho tài xế | UAT-19/21 pass; không suy reviewer chuỗi cũ thành danh tính đã xác thực |
| 6. Replay/shadow | Chạy dữ liệu tổng hợp rồi dữ liệu được phép trong cohort nội bộ; so source/case/decision và lượng trùng | Không phát hành thông báo thật hoặc tự hành động tài khoản khi replay |
| 7. Mở pilot | Chuyển theo cohort/feature flag, theo dõi và rollback có kế hoạch | Rollback ngừng tính năng mới vẫn bảo toàn phản hồi/khiếu nại đã tiếp nhận; không downgrade xóa dữ liệu mới |

Ánh xạ ở bước 2 là đề xuất ban đầu. Hai trạng thái giải trình lịch sử không chứng minh có yêu cầu đã giao hợp lệ; chuyển thành hồ sơ cần kiểm lại trước khi tiếp tục. Hồ sơ `confirmed_fraud` có actor hệ thống lịch sử phải được nhận diện khi chọn mẫu đánh giá; không tự coi là nhãn đã được người độc lập kiểm.

## Gói bàn giao cho thiết kế/phát triển

Kiến trúc cần giải quyết identity, authorization toàn đường đi, workflow/version, evidence storage/search, upload, thông báo, vòng đời và phục hồi. BA cung cấp BR/FR/NFR, mô hình dữ liệu khái niệm, trạng thái, mẫu hồ sơ và UAT; kiến trúc chọn công nghệ theo tải đã xác nhận. Không cần chốt microservices, graph database hay vector database chỉ từ tên đề tài.

QA dùng tài liệu 11–12 để phân rã test và so kết quả implementation, không coi bộ test hiện tại đã bao phủ quy trình hai bên. Product dùng tài liệu 14–15 để chốt discovery/pilot. Vận hành chuẩn bị tài liệu hướng dẫn, người nhận escalation và người xử lý khiếu nại độc lập trước mời tài xế thật.
