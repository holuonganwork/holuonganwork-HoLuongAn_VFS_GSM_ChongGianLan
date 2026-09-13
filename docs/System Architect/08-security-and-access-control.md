# 08. Bảo mật và kiểm soát truy cập

## Mục tiêu và hiện trạng

Prototype chưa có auth; reviewer là chuỗi caller truyền. Mọi kiểm soát dưới đây là yêu cầu thiết kế P1, cần implementation và bằng chứng kiểm thử trước mở môi trường dùng chung. Ranh giới truy cập phải bao phủ list, count, search, snippet, detail, tệp, export, job, notification và backup vận hành.

## Identity và session

Tích hợp IdP hiện có bằng OpenID Connect, authorization code + PKCE. BFF giữ token phía server; trình duyệt nhận cookie session `HttpOnly`, `Secure`, `SameSite` phù hợp luồng đăng nhập, chống CSRF cho lệnh ghi, kiểm Origin/CORS allowlist. Token không lưu localStorage. Tách client/audience cho nội bộ và tài xế; staff có quyền quyết định/export cần MFA. Lựa chọn dựa trên hướng dẫn OAuth security hiện hành, chi tiết IdP phải kiểm lúc implementation. [RFC 9700](https://datatracker.ietf.org/doc/html/rfc9700).

Mapping `(issuer, subject)` tới principal và driver/business unit phải do nguồn được xác minh; không nhận `driver_id` hoặc vai trò từ body làm bằng chứng ownership. Staff chuyển đơn vị/driver đổi số điện thoại cần lifecycle mapping, không tự nối tài khoản theo tên hoặc số điện thoại trùng.

Session kiểm auth epoch mỗi request; đề xuất cache quyền tối đa 60 giây và invalidation từ IdP/danh sách thu hồi, để đáp ứng giới hạn 5 phút của BA. API, job và file gateway từ chối khi không xác minh được quyền mới. Service dùng workload identity/credential ngắn hạn có scope; khóa callback được xoay có khoảng chồng version và audit.

## Policy quyền

`allow = authenticated AND role_action_allowed AND org_scope AND object_scope AND field_policy AND workflow_precondition`. Deny mặc định. Service account cũng chịu role/module scope; không dùng chung DB superuser cho API/worker.

| Hành động | Tài xế | Kiểm soát | Người duyệt | Auditor | Admin kỹ thuật |
| --- | --- | --- | --- | --- | --- |
| Xem case | Publication đúng chủ đã phát hành | Case được phân công/phạm vi cấp | Case trong phạm vi duyệt | Phạm vi audit được cấp | Không mặc định |
| Tìm nguồn thô | Không | Có scope nguồn/mục đích | Khi cần xét hồ sơ được cấp | Theo scope audit riêng | Không mặc định |
| Gửi giải trình | Đúng request của mình | Chỉ nhập hộ có ủy quyền, ghi hai actor | Không giả danh | Không | Không |
| Lập proposal | Không | Người điều tra được phân công | Không tự tạo rồi tự duyệt | Không | Không |
| Duyệt | Không | Không duyệt việc mình điều tra/đề xuất | Độc lập và version đúng | Không | Không |
| Xử lý appeal | Gửi yêu cầu | Không xét vòng mình tham gia | Người được phân công, độc lập vòng trước | Không | Không |
| Xuất/tải | Bản phát hành của mình nếu được cấp | Cần quyền export riêng + purpose | Cần quyền export riêng + purpose | Theo scope export audit | Không mặc định |
| Sửa rule/retention | Không | Theo role chuyên trách | Phê duyệt độc lập nếu được cấp | Chỉ đọc lịch sử | Cài đặt kỹ thuật theo release, không tự đổi quy chế |

Người hỗ trợ có delegation phải ghi authority, scope, expiry, `acting_principal_id` và `on_behalf_of`. Quyền role không vượt điều kiện độc lập theo lịch sử case. Khi thiếu người độc lập, tạo block/escalation thay vì bỏ kiểm.

## Bảo vệ dữ liệu ở từng đường đi

- Query builder bắt buộc scope org/assignment/ownership trước filter/rank/count; join bảng nguồn cũng có scope. Unit test kiểm policy; integration test kiểm SQL và serialization thực.
- Publication là dữ liệu phát hành được lưu và duyệt riêng, chỉ chứa sự việc/căn cứ đủ để phản hồi. Không dùng response nội bộ cho driver; mặc định không có risk, model threshold, thông tin người thứ ba.
- Search session chứa principal/auth epoch; quyền đổi làm hết hiệu lực cả session/count. Projection chỉ trợ giúp tìm kiếm, quyền cuối đọc từ authoritative store.
- Export kiểm quyền khi nhận job, lúc dựng manifest và lúc tải. Tác vụ hết quyền phải hủy/thu hồi artifact. Watermark mục đích/người xuất và audit theo lượt tải.
- Download qua file gateway, kiểm quyền lại mỗi request/range và định kỳ tối đa 60 giây cho stream dài. Không phát URL raw lâu hạn vượt qua cơ chế thu hồi. Dữ liệu đã tải về thiết bị không thể thu hồi bằng cách xóa URL.
- Dùng `Cache-Control: private, no-store` cho dữ liệu nhạy cảm, không cache service worker; logout xóa state/nháp local. Nháp đã xác nhận lưu nằm server theo principal và có version.

PostgreSQL RLS là lớp bổ sung cho `org_id` và dữ liệu chủ thể phù hợp. Runtime role không là table owner/superuser và không có `BYPASSRLS`; dùng transaction-local context với connection pool để không rò scope sang request kế tiếp. RLS không thay field masking hoặc workflow authorization. [PostgreSQL row security](https://www.postgresql.org/docs/16/ddl-rowsecurity.html).

## Upload và tệp không tin cậy

1. Kiểm actor/ownership và quota; cấp upload session gắn principal/request, key ngẫu nhiên, expiry ngắn. Không chấp nhận object key do client tự chọn.
2. Nhận vào quarantine riêng; giới hạn 10 MB/tệp và 5 tệp/lần theo BA ở cả gateway/storage policy và kiểm server sau upload. URL upload không cấp quyền read/list/overwrite evidence.
3. Kiểm byte size, MIME signature, loại allowlist JPG/PNG/PDF, checksum; không tin extension/Content-Type client. Tệp nén thực thi không thuộc MVP.
4. Scanner chạy cách ly, tài nguyên/time limit và egress hạn chế; PDF render/preview được sandbox, không chạy active content. Timeout/failure giữ cách ly; không đánh dấu sạch mặc định.
5. Kết quả scan gắn đúng object version/hash. Copy/promote thành evidence version mới rồi xác minh lại trước metadata `verified`; thay bytes sau scan phải quét lại.
6. Serve bằng tên an toàn, Content-Disposition phù hợp, `nosniff`; bản gốc hạn chế download, preview từ bản dẫn xuất an toàn. Không trả tệp pending/rejected qua URL cũ.

Các lớp kiểm này được chọn theo hướng dẫn upload của OWASP; scanner riêng lẻ không bảo đảm tệp an toàn. [OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html).

## Mô hình đe dọa và kiểm chứng

| Đe dọa | Kiểm soát chính | Kiểm thử cần có |
| --- | --- | --- |
| IDOR/truy cập chéo đơn vị | Object authorization, RLS, DTO theo audience | Đổi case/receipt/upload/job IDs trên mọi endpoint |
| Giả danh reviewer / role escalation | Actor từ IdP, role server, MFA, SoD | Body reviewer giả, token sai audience, tự duyệt |
| Race duyệt và phản hồi | Lock/version, atomic audit, proposal invalidation | Hai approver, phản hồi và timeout/approve cùng lúc |
| Lộ dữ liệu qua search/export | Scope trước count/snippet; kiểm quyền khi tải | Quyền thu hồi giữa search page/export job/download |
| Sửa evidence/audit | Append permissions, version/hash, signed manifests, backup tách quyền | Sửa byte, sửa metadata, mất audit checkpoint |
| Replay callback/giả delivered | Chữ ký, provider event ID, hợp đồng trạng thái | Duplicate, callback lệch thứ tự, sent bị khai delivered |
| Tệp độc/SSRF | Quarantine, allowlist, sandbox; fetch connector theo endpoint allowlist | PDF lỗi, MIME giả, URL nội bộ trong trường nguồn |
| Rò log/secret | Log allowlist, secret manager, lọc telemetry | Scan mẫu log/artifact/trace, không ghi content/token/GPS |
| Nội gián đặc quyền | Phân quyền DB/KMS/backup, truy cập khẩn cấp có hạn, cảnh báo độc lập | Admin app không sửa raw/audit; diễn tập emergency access |
| Prompt injection nếu thêm LLM | Retrieval theo quyền, nội dung là dữ liệu, không quyền command | Tài liệu chứa lệnh không thể thay policy hoặc quyết định |

LLM, OCR, graph/semantic search chưa nằm trên luồng bắt buộc P1. Nếu bổ sung, dữ liệu evidence vẫn không có quyền điều khiển công cụ; câu trả lời phải dẫn source/version, có người xét và giữ giới hạn quyền nguồn.

## Mã hóa, audit và vòng đời

TLS cho mọi kết nối ngoài/mạng nội bộ phù hợp hạ tầng; mã hóa DB/object/backup bằng khóa quản lý tập trung, rotation và kiểm restore với key version cũ. Secret không nằm repo, image hoặc log. Dữ liệu PII chi tiết chỉ nằm vùng được cấp, mapping dùng riêng, analytics dùng trường tối thiểu.

State changes và quyết định commit cùng audit. Đọc nhạy cảm/search/export phải ghi audit bền vững trước giao nội dung; nếu audit store không ghi được thì trả lỗi cho đường đi đó. Log vận hành là kênh khác, có thể gián đoạn mà không phá nghiệp vụ khi audit DB vẫn hoạt động. Audit không chứa toàn bộ nội dung giải trình hoặc query text nhạy cảm; ghi reference và query hash, tham số cần thiết lưu vùng bảo vệ nếu có mục đích đã duyệt.

Runtime chỉ append audit; quyền bảo trì/purge tách riêng và bị giám sát. Mô hình này giảm nguy cơ sửa lịch sử, không tuyên bố chống mọi quyền quản trị cloud. Truy cập khẩn cấp có ticket, lý do, hạn, cảnh báo và hậu kiểm; không giả làm tài xế hoặc bỏ điều kiện duyệt.

Retention/hold/xóa thực thi theo [05](05-data-architecture.md), kiểm vùng lưu và căn cứ xử lý ở cổng pilot. Bộ SA mô tả cơ chế kỹ thuật, không tự xác nhận tuân thủ pháp lý khi chưa xác định nguồn, hợp đồng và chính sách áp dụng.
