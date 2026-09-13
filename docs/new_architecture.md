Dưới đây là kiến trúc tôi đề xuất cho hệ thống của bạn ở mức **System Architecture**, dựa trên toàn bộ các quyết định đã thống nhất: AI là tác nhân phát hiện chính, con người chỉ review exception, tài xế không tham gia ứng dụng, Fraud Case dùng chung và phân loại bằng taxonomy, chưa cần microservices toàn phần ngay từ đầu.

# 1. System Architecture tổng quan

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                     DRIVER FRAUD DETECTION PLATFORM                          │
│                                                                              │
│             AI-FIRST + HUMAN-IN-THE-LOOP FOR EXCEPTIONS                     │
└──────────────────────────────────────────────────────────────────────────────┘


                               DATA SOURCES
                                    │
          ┌─────────────────────────┼──────────────────────────┐
          │                         │                          │
          ▼                         ▼                          ▼
 ┌─────────────────┐      ┌─────────────────┐       ┌─────────────────┐
 │ Driver Metadata │      │ Trip / GPS Data │       │ Internal Data   │
 │                 │      │                 │       │                 │
 │ • driver_id     │      │ • trip_id       │       │ • historical   │
 │ • status        │      │ • location      │       │   fraud data    │
 │ • device        │      │ • timestamps    │       │ • transactions │
 │ • attributes    │      │ • route         │       │ • other signals│
 └────────┬────────┘      └────────┬────────┘       └────────┬────────┘
          │                        │                         │
          └────────────────────────┼─────────────────────────┘
                                   ▼
                    ┌──────────────────────────┐
                    │    1. INGESTION LAYER    │
                    │                          │
                    │ • Receive data/events    │
                    │ • Validate schema        │
                    │ • Deduplicate            │
                    │ • Timestamp              │
                    │ • Source validation      │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │     MESSAGE BROKER       │
                    │                          │
                    │ RabbitMQ / Kafka later   │
                    │                         │
                    │ Buffers incoming events  │
                    │ Decouples processing     │
                    └────────────┬─────────────┘
                                 │
                                 ▼
              ┌──────────────────────────────────────┐
              │       2. DATA PROCESSING LAYER       │
              │                                      │
              │ • Cleaning                           │
              │ • Normalization                      │
              │ • Feature engineering                │
              │ • Context enrichment                 │
              │ • Historical aggregation             │
              │                                      │
              │              PYTHON                  │
              └──────────────────┬───────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         3. AI FRAUD ENGINE                                  │
│                                                                             │
│                              PYTHON                                         │
│                                                                             │
│    ┌───────────────┐   ┌────────────────┐   ┌────────────────────┐          │
│    │ Rule Engine   │   │ ML Classifier  │   │ Anomaly Detection  │          │
│    │               │   │                │   │                    │          │
│    │ Known fraud   │   │ Known patterns │   │ Unknown patterns   │          │
│    │ patterns      │   │ XGBoost etc.   │   │ Isolation Forest   │          │
│    └───────┬───────┘   └───────┬────────┘   └─────────┬──────────┘          │
│            │                   │                      │                     │
│            └───────────────────┼──────────────────────┘                     │
│                                ▼                                            │
│                       ┌─────────────────┐                                    │
│                       │ Ensemble / Risk │                                    │
│                       │ Scoring Engine  │                                    │
│                       └────────┬────────┘                                    │
│                                │                                            │
│         OUTPUT                 ▼                                            │
│                                                                             │
│         • fraud_probability                                                 │
│         • confidence                                                        │
│         • severity                                                          │
│         • fraud_category                                                    │
│         • fraud_types[]                                                     │
│         • signals[]                                                         │
│         • evidence[]                                                        │
│         • model_version                                                     │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │    4. DECISION ENGINE    │
                    │                          │
                    │ AI output                │
                    │ + business policy        │
                    │ + impact level           │
                    └────────────┬─────────────┘
                                 │
                ┌────────────────┼──────────────────┐
                │                │                  │
                ▼                ▼                  ▼

       ┌────────────────┐ ┌────────────────┐ ┌──────────────────┐
       │   AUTO CLEAR   │ │   AUTO FRAUD   │ │  HUMAN REVIEW    │
       │                │ │                │ │                  │
       │ Low fraud risk │ │ High fraud     │ │ Uncertain AI     │
       │ High certainty │ │ probability    │ │ Low confidence   │
       │                │ │ High confidence│ │ Conflicting data │
       └───────┬────────┘ └───────┬────────┘ │ High-impact case │
               │                  │          └─────────┬────────┘
               │                  │                    │
               │                  │                    ▼
               │                  │             ┌───────────────┐
               │                  │             │ Human Reviewer │
               │                  │             │               │
               │                  │             │ Confirm       │
               │                  │             │ Reject        │
               │                  │             │ Override      │
               │                  │             └───────┬───────┘
               │                  │                     │
               └──────────────────┼─────────────────────┘
                                  ▼
                    ┌───────────────────────────┐
                    │ 5. FRAUD CASE MANAGEMENT │
                    │                           │
                    │ Unified Fraud Case system │
                    │                           │
                    │ No separate app per fraud │
                    └─────────────┬─────────────┘
                                  │
                     ┌────────────┼─────────────┐
                     │            │             │
                     ▼            ▼             ▼
              LOCATION_FRAUD  TRIP_FRAUD  ACCOUNT_FRAUD
                     │            │             │
                     ▼            ▼             ▼
                fraud_type    fraud_type    fraud_type
                + signals     + signals     + signals

                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │ 6. BUSINESS WORKFLOW      │
                    │                           │
                    │ • Case assignment         │
                    │ • Review status           │
                    │ • Escalation              │
                    │ • Business action         │
                    │ • Final decision          │
                    │ • Notification            │
                    │ • Audit                   │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                          FINAL CASE STATE
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                     │
│                                                                             │
│    PostgreSQL                    Redis                  Object Storage        │
│    ──────────                    ─────                  ──────────────        │
│    drivers                       cache                  raw evidence          │
│    trips                         sessions               large raw data        │
│    fraud_signals                 temporary state        files                 │
│    fraud_decisions               locks                  archives              │
│    fraud_cases                   hot data                                      │
│    case_evidence                                                             │
│    human_reviews                                                            │
│    audit_logs                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MONITORING & FEEDBACK LOOP                              │
│                                                                             │
│ • False Positive Rate             • Human override rate                     │
│ • False Negative Rate             • Model drift                             │
│ • Precision / Recall              • Processing latency                      │
│ • AI confidence distribution      • Queue backlog                           │
│ • Fraud distribution              • DB performance                          │
│                                                                             │
│ Human review result ───────────────────────────────► Training dataset        │
│ Training dataset ─────────────────────────────────► New model               │
│ New model ────────────────────────────────────────► Fraud Engine             │
└─────────────────────────────────────────────────────────────────────────────┘
```

# 2. Người dùng của hệ thống

**Tài xế không phải user của ứng dụng.** Tài xế chỉ là một `data subject` mà hệ thống phân tích.

```text
                    INTERNAL USERS
                          │
        ┌─────────────────┼──────────────────┐
        │                 │                  │
        ▼                 ▼                  ▼
     Reviewer        Operations          Admin /
                                        Supervisor
        │                 │                  │
        ▼                 ▼                  ▼
Review uncertain     Handle confirmed    Manage users
AI decisions         fraud cases         Monitor AI
Inspect evidence     Business actions    Audit
Override AI          Final status        Reporting
```

Frontend do đó là một **internal operations application**.

---

# 3. Fraud taxonomy

Không thiết kế một hệ thống riêng cho mỗi lỗi.

```text
Fraud Category
      │
      └── Fraud Type
              │
              └── Fraud Signal
```

Ví dụ:

```text
LOCATION_FRAUD
│
├── GPS_SPOOFING
│   ├── impossible_speed
│   ├── location_jump
│   └── route_mismatch
│
└── FAKE_LOCATION


TRIP_FRAUD
│
├── FAKE_TRIP
├── DISTANCE_MANIPULATION
└── TRIP_MANIPULATION


ACCOUNT_FRAUD
│
├── ACCOUNT_SHARING
├── MULTI_ACCOUNT
└── DEVICE_MANIPULATION
```

Một case có thể chứa nhiều signal và nhiều loại lỗi:

```text
Fraud Case FC-00192
│
├── Driver: D-19382
├── Trip: T-82019
│
├── Primary Fraud Type
│      └── GPS_SPOOFING
│
├── Related Fraud Type
│      └── DEVICE_MANIPULATION
│
├── Signals
│      ├── impossible_speed
│      ├── location_jump
│      ├── route_mismatch
│      └── unexpected_device_change
│
├── Risk Score: 0.96
├── Confidence: 0.78
│
└── Status: NEED_REVIEW
```

Do đó reviewer làm việc trên **Unified Fraud Review Queue**, rồi lọc theo `category`, `type`, `severity`, `confidence`, `risk` hoặc `status`.

---

# 4. Logic AI → HITL

Không phải mọi fraud detection đều tạo ticket review.

```text
                     AI RESULT
                         │
                         ▼
                  Decision Policy
                         │
           ┌─────────────┼──────────────┐
           │             │              │
           ▼             ▼              ▼
     Low Fraud Risk    High Fraud     Uncertain
                        Confidence
           │             │              │
           ▼             ▼              ▼
       AUTO CLEAR     Check Impact    HUMAN REVIEW
                         │
                 ┌───────┴────────┐
                 ▼                ▼
             Low Impact       High Impact
                 │                │
                 ▼                ▼
             AUTO ACTION      HUMAN APPROVAL
```

Do đó Human-in-the-loop là **exception path**, không phải default path.

---

# 5. Signal, Alert và Case phải tách biệt

Đây là một trong những boundary quan trọng nhất của domain:

```text
SIGNAL
"Phát hiện một dấu hiệu bất thường"
        │
        ▼
ALERT
"Có đủ dấu hiệu để cảnh báo"
        │
        ▼
CASE
"Có một vấn đề cần quản lý / xử lý"
```

Ví dụ:

```text
GPS jump                 → Signal
Impossible speed         → Signal
Route mismatch           → Signal
Device change            → Signal

        ↓ AI correlation

Potential GPS Spoofing   → Alert

        ↓ Decision Engine

Fraud Case FC-1029       → Case
```

Không tạo bốn ticket riêng cho bốn signal.

---

# 6. Kiến trúc phần mềm hiện tại

Tôi **không khuyên bắt đầu bằng microservices**.

```text
                         FRONTEND
                             │
                             ▼
                  ┌────────────────────┐
                  │  Core Backend      │
                  │                    │
                  │ Modular Monolith   │
                  │ Python / FastAPI   │
                  └─────────┬──────────┘
                            │
       ┌────────────────────┼──────────────────────┐
       │                    │                      │
       ▼                    ▼                      ▼
     Auth               Fraud Case              Review
     User               Workflow                Audit
     Roles              Search                  Reports
       │                    │                      │
       └────────────────────┼──────────────────────┘
                            │
                 PostgreSQL + Redis


                     AI SIDE
                        │
                        ▼
                  Python Workers
                        │
                        ▼
                  Fraud Engine
                        │
                        ▼
                  Message Broker
                        │
                        ▼
                  Core Backend
```

Đây là **Modular Monolith + asynchronous AI workers**.

Nó đơn giản hơn nhiều so với xây microservices ngay từ đầu nhưng vẫn tạo boundary đủ tốt để tách sau này.

---

# 7. Boundary Python và Java trong tương lai

Một ranh giới công nghệ tự nhiên là:

```text
┌───────────────────────────┐
│          PYTHON           │
│                           │
│ "WHAT IS SUSPICIOUS?"     │
│                           │
│ Data processing           │
│ Feature engineering       │
│ Rule engine               │
│ Machine Learning          │
│ Anomaly detection         │
│ Deep Learning             │
│ Risk scoring              │
│ Confidence                │
│ Evidence generation       │
└─────────────┬─────────────┘
              │
              │ Fraud Decision/Event
              ▼
┌───────────────────────────┐
│    JAVA / SPRING BOOT     │
│      Future option        │
│                           │
│ "WHAT SHOULD WE DO?"      │
│                           │
│ Case management           │
│ Human workflow            │
│ Permissions               │
│ Transactions              │
│ Action execution          │
│ Audit                     │
│ Notifications             │
│ Reporting API             │
└───────────────────────────┘
```

Không có lý do để rewrite AI Python sang Java.

Nếu Spring Boot được đưa vào sau này, candidate tốt nhất là **Core Business Backend**.

---

# 8. Kiến trúc tương lai khi hệ thống thực sự lớn

Khi có nhu cầu scale độc lập, team ownership hoặc fault isolation, modular monolith có thể tách dần:

```text
                              Frontend
                                 │
                                 ▼
                            API Gateway
                                 │
          ┌──────────────────────┼──────────────────────┐
          ▼                      ▼                      ▼
     Auth Service          Case Service          Search Service
     Java/Spring           Java/Spring           Java/Spring
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                                 ▼
                               Kafka
                                 │
             ┌───────────────────┼───────────────────┐
             ▼                   ▼                   ▼
       Fraud AI Service     Audit Service     Notification Service
          Python               Java                Java
             │
             ▼
       ML / Rules / DL
```

Và có thể scale:

```text
Auth Service          ×2
Case Service          ×3
Search Service        ×6
Fraud AI Workers      ×20
```

thay vì scale toàn bộ application.

---

# 9. LLM/RAG nằm ở đâu?

LLM không phải Fraud Detection Engine chính.

```text
                    Fraud Case
                        │
                        ▼
                 Evidence Store
                        │
                        ▼
                   Retriever
                        │
                        ▼
                    LLM / RAG
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
       Explain Evidence      Reviewer Assistant
```

LLM/RAG có thể giúp reviewer:

```text
"Tại sao AI đánh dấu case này?"

"Tìm các evidence quan trọng nhất."

"Tìm các case lịch sử tương tự."

"Tóm tắt timeline của case."
```

Nhưng `fraud_probability` nên đến từ Fraud Engine chứ không phải từ LLM.

---

# 10. Kiến trúc mục tiêu cô đọng nhất

Nếu cần một diagram để đưa thẳng vào `ARCHITECTURE.md`, tôi sẽ dùng phiên bản này:

```text
                           DATA SOURCES
                                │
                                ▼
                         Data Ingestion
                                │
                                ▼
                         Message Broker
                                │
                                ▼
                       Data Processing
                            [Python]
                                │
                                ▼
                        AI Fraud Engine
                            [Python]
                Rules + ML + Anomaly + DL
                                │
                                ▼
         risk + confidence + fraud_type + evidence
                                │
                                ▼
                        Decision Engine
                                │
                ┌───────────────┼──────────────┐
                ▼               ▼              ▼
           AUTO CLEAR      AUTO FRAUD     HUMAN REVIEW
                                │              │
                                └───────┬──────┘
                                        ▼
                                Fraud Case
                                        │
                         Unified Case Management
                                        │
                     ┌──────────────────┼─────────────────┐
                     ▼                  ▼                 ▼
                   Review            Actions            Audit
                     │                  │                 │
                     └──────────────────┼─────────────────┘
                                        ▼
                                Final Case State
                                        │
                                        ▼
                   ┌────────────────────────────────┐
                   │ PostgreSQL                     │
                   │ Redis                          │
                   │ Object Storage                 │
                   └────────────────────────────────┘

                              FEEDBACK
                                 ▲
                                 │
                    Human Review / Ground Truth
                                 │
                                 └──────────► AI Training
```

**Kiến trúc tôi chọn cho giai đoạn đầu:** `Python/FastAPI modular monolith + Python AI workers + PostgreSQL + Redis + Object Storage + một message broker`, chưa cần Kubernetes và chưa cần chia toàn bộ thành microservices.

**Kiến trúc đích dài hạn:** Python giữ Fraud/AI platform; Java/Spring Boot có thể đảm nhận Core Business/Case Workflow; Kafka trở thành event backbone khi quy mô đủ lớn; từng service chỉ được tách khi thực sự cần scale, deploy hoặc vận hành độc lập.
