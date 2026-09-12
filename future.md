                DRIVER DATA
                    │
                    ▼
             Python Pipeline
        ┌─────────────────────┐
        │ Normalize           │
        │ Fraud Rules         │
        │ ML / Anomaly        │
        │ Risk Scoring        │
        │ Evidence generation │
        └──────────┬──────────┘
                   │
           suspicious event
                   │
                   ▼
              Queue / Kafka
                   │
                   ▼
            Java Core Backend
     ┌───────────────────────────┐
     │ Fraud Case Management     │
     │ Review Workflow           │
     │ User / Role / Permission  │
     │ Driver Dispute Workflow   │
     │ Audit Log                 │
     │ Final Decision            │
     └─────────────┬─────────────┘
                   │
                   ▼
              PostgreSQL