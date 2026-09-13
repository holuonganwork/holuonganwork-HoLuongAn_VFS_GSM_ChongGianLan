# 07. API và tích hợp

## Contract và tương thích

Đây là thiết kế API đích, chưa tồn tại trong [routes hiện tại](../../backend/app/api/routes.py). API local hiện có đường dẫn `/fraud-cases`, `/fraud-alerts`, `/review-queue`; frontend Vite proxy `/api` tới backend. Namespace `/api/v1` bên dưới cần gateway/proxy mới và OpenAPI versioned khi implementation; không tự đổi client đang chạy chỉ bằng sửa tài liệu.

Chọn REST/JSON cho application commands và query; event bất đồng bộ cho tích hợp sau commit. Một public API version giữ nghĩa ổn định; thay enum/bắt buộc trường/xóa field là breaking change cần version mới và thời gian chuyển consumer. Các trường optional mới được bổ sung với kiểm tương thích. API schemas phân biệt DTO nội bộ/tài xế, không dùng cùng ORM serialization rồi xóa vài field tại frontend.

## Danh mục endpoint đích

Tất cả đường dẫn trong bảng có tiền tố `/api/v1`. `I` là internal audience, `D` là driver, `S` là service đã xác thực. Mỗi nhóm còn phải kiểm quyền đối tượng tại [08](08-security-and-access-control.md).

| Method/path | Audience | Hành vi và đáp ứng |
| --- | --- | --- |
| `GET /internal/cases`, `/internal/alerts`, `/internal/review-queue` | I | Lọc có quyền, phân trang, độ mới; metadata tối thiểu |
| `GET /internal/cases/{id}` | I | Chi tiết, version/ETag, evidence links và timeline được cấp |
| `POST /internal/cases/{id}/assignments` | I | Nhận/chuyển owner có If-Match; 201 |
| `POST /internal/cases/{id}/evidence-links` | I | Gắn evidence version, support/refute/unclear; 201 |
| `POST /internal/cases/{id}/explanation-requests` | I | Soạn/phát hành bản đã preview và duyệt che; 201, delivery pending |
| `POST /internal/requests/{id}/extensions` | I | Gia hạn có lý do và lịch cũ/mới; 201 |
| `POST /internal/cases/{id}/proposals` | I | Checklist và information version; 201 |
| `POST /internal/proposals/{id}/approvals` | I | Duyệt/trả lại, độc lập, case/proposal version; 201 |
| `POST /internal/cases/{id}/publications` | I | Phát hành kết quả đúng decision version, projection riêng; 201 |
| `POST /internal/cases/{id}/handoffs` | I | Hồ sơ bàn giao, purpose/recipient; 201 |
| `POST /internal/appeals/{id}/decisions` | I | Giữ/sửa/hủy bằng version kế tiếp; 201 |
| `POST /internal/searches` | I | Query snapshot, trang đầu, count/nguồn/watermark; 201 |
| `GET /internal/searches/{id}/results?cursor=...` | I | Trang ổn định trong TTL, quyền kiểm lại |
| `POST /internal/exports` | I | Tạo job theo case/query snapshot và audience; 202 + job ID |
| `GET /internal/jobs/{id}` | I | Trạng thái export và link tải có quyền; không trả object key |
| `GET /internal/reports`, `/internal/audit-events` | I | Report theo cohort; audit theo quyền riêng, có pagination |
| `POST /internal/rule-releases` và `/{id}/approvals`, `/{id}/activations` | I | Tạo, duyệt độc lập, kích hoạt/lịch hiệu lực và rollback version |
| `POST /internal/data-requests`, `/internal/holds` | I | Yêu cầu lifecycle/hold có thẩm định, 202/201 |
| `POST /internal/label-reviews` | I | Nhãn độc lập và phân xử có version; 201 |
| `GET /driver/cases`, `/driver/cases/{id}` | D | Chỉ publication đã phát hành đúng chủ; không trả raw case |
| `PUT /driver/requests/{id}/draft` | D | Lưu nháp theo principal, If-Match draft; 200 + version |
| `POST /driver/requests/{id}/responses` | D | Gửi/bổ sung bất biến, request version, biên nhận; 201 |
| `GET /driver/receipts/{id}` | D | Đối soát thao tác của chính chủ sau lỗi mạng |
| `POST /driver/cases/{id}/appeals` | D | Nhận khiếu nại có biên nhận; 201, chưa đồng nghĩa hợp lệ |
| `POST /driver/issues` | D | Báo vấn đề chuyến mình, kiểm ownership nguồn; 201 |
| `POST /driver/uploads`, `POST /driver/uploads/{id}/complete` | D | Cấp upload session rồi kiểm nhận/quét; 201/202 |
| `GET /files/{artifact_id}/content` | I/D | Kiểm quyền/version/trạng thái quét mỗi lượt tải; audit |
| `POST /integrations/batches` | S | Đăng ký manifest/object đã nhận bền vững; 202 + receipt |
| `POST /integrations/notifications/{provider}/events` | S | Callback xác thực, dedup provider event, 202 |

Đây là danh mục năng lực API, chưa liệt kê mọi thao tác quản trị hoặc schema field. OpenAPI đầy đủ là đầu ra bắt buộc đợt P1, đối chiếu FR và contract tests ở tài liệu 13.

## Lệnh ghi và version

Mutable resource trả ETag có namespace, ví dụ `"case-1042-v17"`. Lệnh đổi owner/proposal/approve cần `If-Match`; thiếu trả 428, version lỗi thời trả 412. Nghiệp vụ không hợp lệ trên version đúng trả 409. Body không nhận `reviewer` tùy ý; actor lấy từ session, delegated actor từ hồ sơ ủy quyền đã kiểm.

Gửi response dùng `request_version` mà tài xế đã xem cùng ID submission do client tạo; server khóa case và gắn response vào trạng thái hiện hành. Không yêu cầu tài xế biết version nội bộ để được nhận nội dung. Request đã bị thay thế hoặc case đã resolved vẫn lưu nội dung liên quan có receipt và chuyển đúng luồng xét bổ sung/khiếu nại; không tính nó là đã trả lời một cáo buộc mới chưa từng được công bố. Tác vụ quản trị có tác động nội dung tăng information version theo [06](06-detection-and-decision-pipeline.md).

Ví dụ tổng hợp:

```http
POST /api/v1/driver/requests/req-demo-17/responses
Content-Type: application/json
Idempotency-Key: submission-demo-001

{
  "client_submission_id": "submission-demo-001",
  "request_version": 2,
  "content": "Thiết bị được bàn giao theo ca; xin đối chiếu sổ cấp phát.",
  "attachment_ids": ["upload-demo-01"]
}
```

```json
{
  "receipt_id": "receipt-demo-001",
  "response_id": "response-demo-001",
  "response_version": 1,
  "received_at": "2026-09-14T03:10:00Z",
  "late": false,
  "attachments": [{"id": "upload-demo-01", "status": "pending_scan"}],
  "next_step": "awaiting_review"
}
```

ID có tiền tố `demo` minh họa, không phải UUID production. Receipt trả sau commit text/attachment references/audit/outbox. Tệp chưa quét không chặn nhận phần chữ, nhưng được hiển thị rõ chưa dùng làm căn cứ.

## Idempotency, lỗi và retry

1. Xác thực, kiểm quyền hiện hành trước cả truy vấn idempotency result.
2. Khóa duy nhất `(org_id, principal_id, operation, key)`; hash canonical payload có version. Cùng key/body nhận cùng logical result; key/body khác trả 409 `idempotency_conflict`.
3. Claim idempotency và ghi domain result/audit/outbox trong cùng transaction. Cạnh tranh chờ ngắn hoặc trả 409 `request_in_progress` có Retry-After. Crash rollback không để key thành công giả.
4. Retry result là tham chiếu resource/receipt, serialize lại theo quyền hiện hành; không trả response cache chứa dữ liệu đã mất quyền.
5. Cache kết quả đề xuất 7 ngày; khóa business lâu hơn giữ trong receipt `client_submission_id` theo vòng đời hồ sơ. Hết cache không tạo thêm một submission/approval cũ; key không được dùng lại cho thao tác mới.

| HTTP | Ý nghĩa và client action |
| --- | --- |
| 400 / 422 | Contract hoặc dữ liệu không hợp lệ; sửa trường, không retry tự động |
| 401 / 403 | Chưa xác thực / không có quyền chức năng; refresh/login theo policy |
| 404 | Không tồn tại hoặc ngoài phạm vi object; không phân biệt để tiết lộ hồ sơ |
| 409 / 412 / 428 | Conflict nghiệp vụ / version cũ / thiếu precondition; xem lại tình trạng |
| 410 | Search session hoặc upload session hết hạn; tạo phiên mới, không mất receipt đã lưu |
| 413 / 415 | Quá giới hạn / sai loại tệp |
| 429 / 503 | Quá tải / phụ thuộc chưa sẵn sàng; Retry-After + exponential backoff có jitter |

Error body dùng `type`, `title`, `status`, `code`, `request_id`, lỗi field đã làm sạch; không SQL, stack trace, source URL riêng hoặc chi tiết quyền của người khác. Giới hạn retry đề xuất 5 lần/tác vụ nền trước quarantine/DLQ; retry lâu hơn do lịch khôi phục có owner, không loop vô hạn.

## Query và phân trang

List thông thường dùng cursor keyset với sort key + ID và version bộ lọc; `limit` mặc định 50, tối đa 200. Danh sách thay đổi trực tiếp ghi rõ có thể cập nhật giữa lần tải. Khi cần không lặp/mất trong cùng truy vấn, dùng search session tại [05](05-data-architecture.md).

Search body gồm exact IDs, `from/to`, types/statuses, text, sort, audience; AND giữa bộ lọc, OR trong multi-value. Chuỗi ID theo normalization nguồn, không fuzzy identity. Result có `search_id`, `snapshot_at`, `expires_at`, `authorized_total`, `items`, `next_cursor`, `source_statuses`, `watermarks`. Cursor ký, gắn principal/query/auth epoch, không phải quyền truy cập thay session. Query vượt scope/giới hạn phải trả yêu cầu thu hẹp, không báo zero khi nguồn lỗi.

## Event envelope và tương thích consumer

Event nội bộ ví dụ sau dùng ID dạng minh họa. Timestamp do publisher ghi, version nghiệp vụ dùng để phát hiện event trễ/trùng.

```json
{
  "event_id": "event-demo-001",
  "event_type": "case.response_received",
  "schema_version": 1,
  "org_id": "org-pilot",
  "aggregate_type": "case",
  "aggregate_id": "case-demo-1042",
  "aggregate_version": 18,
  "occurred_at": "2026-09-14T03:10:00Z",
  "producer": "collaboration",
  "correlation_id": "flow-demo-001",
  "causation_id": "command-demo-001",
  "run_mode": "live",
  "data": {"response_id": "response-demo-001", "information_version": 7}
}
```

Event chỉ mang dữ liệu tối thiểu và reference, không GPS thô/nội dung giải trình. Transport auth và ACL consumer không được thay bằng trường `producer` tự khai. Trường `org_id` luôn kiểm theo nguồn xác thực. Event schema được quản lý trong Git ở P1, kiểm backward compatibility khi phát hành; schema registry là lựa chọn khi thêm broker nhiều producer.

| Event | Producer → consumer | Tác động |
| --- | --- | --- |
| `source.revision_accepted`, `source.corrected` | Ingest → detection, search, impact analysis | Recompute đúng cửa sổ và đối chiếu evidence |
| `alert.assessed` | Detection → incident/case projection, metrics | Link/create theo policy live, dedup fingerprint |
| `case.publication_released` | Collaboration → notification, search | Gửi projection tối thiểu, không gửi raw |
| `case.response_received` | Collaboration → queue/search/report | Cập nhật hiển thị; invalidation proposal đã nằm trong transaction command |
| `case.decision_recorded` | Workflow → publication task, handoff task, quality | Tác vụ có review, không tự phát hành nội dung chưa che |
| `notification.delivery_recorded` | Integration → workflow/report | Mốc SLA được kiểm chữ ký và business contract |
| `data.access_revoked`, `data.purged` | Governance → search/export/cache | Thu hồi/xóa dẫn xuất và đối soát |

At-least-once áp dụng ở transport. Không hứa exactly-once từ broker đến database/provider. Callback trễ/trùng lưu lịch sử, không đưa trạng thái delivered trở về sent. Provider timeout không rõ đã gửi hay chưa: query trạng thái theo delivery key hoặc tạo ngoại lệ `delivery_unknown`; không lặp gửi mù. Callback replay bị kiểm ID/chữ ký/thời gian theo hợp đồng, có luồng reconciliation cho delivery thật đến muộn.
