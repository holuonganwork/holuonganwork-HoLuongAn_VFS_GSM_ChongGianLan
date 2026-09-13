# Ma trận truy vết yêu cầu

Baseline BA 1.0. Bảng liên kết mọi FR với mục tiêu nghiệp vụ, use case/story, dữ liệu, quy tắc và UAT. **Trạng thái chung: đề xuất, chưa triển khai/nghiệm thu theo baseline này.** Mức đáp ứng thực tế của prototype nằm ở tài liệu 17, không suy từ việc đã có test trong repository.

Bảng FR có [bản CSV](requirements-traceability.csv) dùng cho công cụ bảng tính; tài liệu này là bản chuẩn cho cả FR và NFR.

## Truy vết yêu cầu chức năng

| FR | BR | UC | US | Quy tắc | Dữ liệu | UAT |
| --- | --- | --- | --- | --- | --- | --- |
| FR-01 | BR-01, BR-03 | UC-01 | US-01 | RULE-07 | DR-01, DR-02, DR-03 | UAT-01 |
| FR-02 | BR-02, BR-10 | UC-01 | US-01 | RULE-01, RULE-02, RULE-03, RULE-04, RULE-05 | DR-03, DR-04, DR-05 | UAT-02, UAT-03, UAT-04, UAT-05 |
| FR-03 | BR-02, BR-08 | UC-01 | US-01 | RULE-06 | DR-01, DR-04 | UAT-06 |
| FR-04 | BR-08 | UC-02 | US-02 | RULE-06, RULE-10 | DR-06, DR-08 | UAT-07 |
| FR-05 | BR-01, BR-07 | UC-02 | US-03 | RULE-07, RULE-11 | DR-01, DR-02, DR-03, DR-06 | UAT-08, UAT-19, UAT-27 |
| FR-06 | BR-01, BR-03 | UC-03 | US-03 | RULE-07 | DR-02, DR-04 | UAT-09 |
| FR-07 | BR-03 | UC-03 | US-04 | RULE-07, RULE-17 | DR-04, DR-06 | UAT-10 |
| FR-08 | BR-04, BR-07 | UC-04 | US-05 | RULE-10, RULE-11 | DR-06, DR-07 | UAT-11 |
| FR-09 | BR-04 | UC-05 | US-06 | RULE-10, RULE-12 | DR-06, DR-07 | UAT-12, UAT-13 |
| FR-10 | BR-04, BR-08 | UC-04, UC-05 | US-05 | RULE-10 | DR-02, DR-07 | UAT-14 |
| FR-11 | BR-03, BR-05 | UC-06 | US-04 | RULE-07, RULE-08, RULE-13, RULE-17 | DR-04, DR-07, DR-09 | UAT-15 |
| FR-12 | BR-05 | UC-06 | US-07 | RULE-08, RULE-09, RULE-11, RULE-12 | DR-08 | UAT-16 |
| FR-13 | BR-05, BR-06 | UC-06 | US-07 | RULE-09, RULE-11, RULE-12 | DR-06, DR-07, DR-08 | UAT-17 |
| FR-14 | BR-06 | UC-07 | US-08 | RULE-11, RULE-12 | DR-07, DR-08 | UAT-18 |
| FR-15 | BR-07 | UC-09 | US-09 | RULE-11 | DR-06 | UAT-19 |
| FR-16 | BR-03, BR-07 | UC-09 | US-09 | RULE-11, RULE-12 | DR-08 | UAT-20 |
| FR-17 | BR-03, BR-07 | UC-09 | US-09 | RULE-07, RULE-11 | DR-04, DR-06, DR-08 | UAT-21 |
| FR-18 | BR-08, BR-09 | UC-08 | US-10 | RULE-13, RULE-14, RULE-17 | DR-03, DR-08, DR-09 | UAT-22 |
| FR-19 | BR-02, BR-10 | UC-08 | US-11 | RULE-05, RULE-15 | DR-05, DR-08 | UAT-23 |
| FR-20 | BR-07 | UC-09 | US-09 | RULE-16 | DR-06, DR-10 | UAT-24 |
| FR-21 | BR-09, BR-10 | UC-08 | US-11 | RULE-14, RULE-15, RULE-17 | DR-05, DR-09 | UAT-25 |
| FR-22 | BR-01, BR-04 | UC-10 | US-12 | RULE-06, RULE-11, RULE-18 | DR-01, DR-06, DR-07 | UAT-26 |

## Truy vết chất lượng hệ thống

| NFR | BR | FR chịu ảnh hưởng chính | Bằng chứng nghiệm thu |
| --- | --- | --- | --- |
| NFR-01 | BR-07 | FR-15, FR-17 | UAT-19, UAT-21 |
| NFR-02 | BR-07 | FR-08, FR-15, FR-16, FR-17 | UAT-19, UAT-20, UAT-21 |
| NFR-03 | BR-03 | FR-07, FR-17 | UAT-10, UAT-21 |
| NFR-04 | BR-05, BR-08 | FR-03, FR-09, FR-12 | UAT-06, UAT-13, UAT-16 |
| NFR-05 | BR-01, BR-04 | FR-05, FR-09 | UAT-27 |
| NFR-06 | BR-01, BR-08 | FR-01, FR-05, FR-18 | UAT-01, UAT-27 |
| NFR-07 | BR-04, BR-08 | FR-09, FR-12, FR-20 | UAT-28 |
| NFR-08 | BR-04 | FR-08, FR-09, FR-14 | UAT-13 |
| NFR-09 | BR-04, BR-07 | FR-09, FR-15 | UAT-12, UAT-13 |
| NFR-10 | BR-03, BR-07 | FR-10, FR-16 | UAT-14, UAT-20 |
| NFR-11 | BR-02, BR-09 | FR-02, FR-18, FR-21 | UAT-02, UAT-03, UAT-04, UAT-05, UAT-22, UAT-25 |
| NFR-12 | BR-07, BR-10 | FR-19, FR-20 | UAT-23, UAT-24, UAT-28 |

## Nguồn hình thành và điểm cần xác nhận

| Nhóm yêu cầu | Cơ sở | Xác nhận còn cần |
| --- | --- | --- |
| BR-01–03 | Prototype có quy tắc/nguồn; nghiên cứu quy trình điều tra tại tài liệu 13 | Thao tác và dữ liệu thật; baseline công tìm nguồn |
| BR-04–06 | Đề tài phối hợp tài xế–kiểm soát; đề xuất quản trị vụ việc | Quy chế giải trình/khiếu nại và người độc lập |
| BR-07 | Nhu cầu phân quyền dữ liệu vụ việc; nguồn pháp lý trong tài liệu 13 | Căn cứ theo dữ liệu, thời hạn lưu, nghĩa vụ pháp lý áp dụng |
| BR-08–10 | Mục tiêu tải/hiệu quả/chất lượng; giả thuyết pilot | Năng lực kiểm soát, chỉ số, chi phí và mức chấp nhận sai |

## Quy tắc quản lý thay đổi

Mỗi yêu cầu thay đổi phải ghi lý do, người đề nghị, BR/FR/NFR/DR/RULE bị tác động, dữ liệu và quyền liên quan, UAT cần cập nhật, chi phí/lịch dự kiến, người quyết định và ngày hiệu lực. Nếu bỏ tính năng, cập nhật scope, backlog, RTM và UAT đồng thời; không xóa ID cũ để che lịch sử. Các quy tắc chính thức và bằng chứng thực thi phải bổ sung vào baseline sau workshop, không tự đánh dấu đã thống nhất.
