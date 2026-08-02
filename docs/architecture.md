# Kiến trúc hệ thống

OpenResearch Graph dùng **modular monolith**: một repository và một domain model thống nhất, nhưng frontend, API và background worker chạy thành tiến trình riêng. Cách này dễ học/debug hơn microservices, đồng thời vẫn cho phép scale worker và API độc lập.

## Sơ đồ tổng thể

```mermaid
flowchart LR
    B[Browser] --> F[Next.js frontend]
    F --> A[FastAPI /api/v1]
    A --> P[(PostgreSQL + pgvector)]
    A --> R[(Redis)]
    A --> O[OpenAlex API]
    A --> L[Mock / Ollama / OpenAI-compatible]
    A --> S[Mock / Stripe]
    A --> FS[Local / S3 storage]
    R --> W[Celery worker]
    W --> P
    W --> FS
    W --> L
```

## Backend layers

```text
API routes
  ↓ request/response schemas + authorization
Services
  ↓ domain logic, retrieval, ranking, provider adapters
SQLAlchemy models / repositories
  ↓ transaction and persistence
PostgreSQL, Redis, storage, external APIs
```

Route không nên chứa thuật toán dài hoặc provider-specific code. Service không được tin `user_id` do frontend gửi nếu đã có authenticated user từ dependency.

## Luồng authentication

```mermaid
sequenceDiagram
  participant U as User
  participant F as Frontend
  participant A as FastAPI
  participant D as PostgreSQL
  U->>F: email + password
  F->>A: POST /auth/login
  A->>D: verify user and Argon2 hash
  A->>D: store hashed refresh token + family
  A-->>F: access + refresh token
  F->>A: authorized request
  A-->>F: 401 when access expires
  F->>A: POST /auth/refresh
  A->>D: rotate token and revoke old token
  A-->>F: new token pair
```

Development frontend lưu token để minh họa flow. Production cần secure HttpOnly refresh cookie và CSRF strategy như tài liệu security.

## Luồng PDF RAG

```mermaid
sequenceDiagram
  participant U as User
  participant F as Next.js
  participant A as FastAPI
  participant Q as Redis/Worker
  participant P as PostgreSQL
  participant L as LLM
  U->>F: Upload PDF
  F->>A: multipart + access token
  A->>P: document pending metadata
  A->>Q: process_document(document_id)
  Q->>P: processing status
  Q->>Q: extract, clean, chunk, embed
  Q->>P: chunks + vectors + completed
  U->>F: Ask question
  F->>A: chat message
  A->>P: FTS/vector candidates
  A->>A: rerank + MMR + context budget
  A->>L: grounded prompt
  L-->>A: answer
  A-->>F: answer + page citations
```

## Luồng recommendation

```mermaid
flowchart LR
    I[User interactions] --> C[Content profile]
    I --> CF[Collaborative co-occurrence]
    G[Citation graph] --> PR[Personalized PageRank]
    P[Paper metadata] --> POP[Popularity/recency/OA]
    C --> H[Hybrid ranker]
    CF --> H
    PR --> H
    POP --> H
    H --> D[MMR diversity]
    D --> API[Recommendations + explanations]
```

## Luồng ingestion

API ingestion dùng cursor checkpoint. Snapshot ingestion đọc từng gzip/JSONL file, normalize, batch upsert, commit, checkpoint và dead-letter record. API server không nên tự chạy job snapshot dài; dùng worker hoặc process riêng.

## Ranh giới scale

- API/worker stateless có thể scale ngang.
- PostgreSQL và storage cần backup, monitoring và capacity planning.
- Vector dimension là schema contract.
- Analytics lớn có thể chuyển sang materialized view/warehouse.
- Không tách microservice cho từng module trước khi có bottleneck và ownership rõ.
