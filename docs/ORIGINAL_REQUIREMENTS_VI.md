# PROMPT TẠO TOÀN BỘ DỰ ÁN OPENRESEARCH GRAPH

Bạn là một **Senior Full-stack Engineer, Machine Learning Engineer và Data Engineer**. Hãy xây dựng hoàn chỉnh một dự án cá nhân có tên:

# OpenResearch Graph

**OpenResearch Graph** là nền tảng web hỗ trợ sinh viên, giảng viên và nhà nghiên cứu:

* Tìm kiếm bài báo khoa học.
* Phân tích xu hướng nghiên cứu.
* Vẽ mạng trích dẫn.
* Đọc và trò chuyện với PDF bằng RAG.
* Đề xuất bài báo phù hợp với người dùng.
* Theo dõi tác giả, chủ đề và bài báo.
* Quản lý tài khoản người dùng.
* Quản lý gói miễn phí và gói trả phí.
* Xây dựng pipeline có khả năng mở rộng để xử lý số lượng lớn bài báo.

Dự án phải thể hiện rõ kiến thức của sinh viên đại học ngành:

* Trí tuệ nhân tạo.
* Khoa học dữ liệu.
* Machine Learning.
* Deep Learning.
* Xử lý ngôn ngữ tự nhiên.
* Hệ thống khuyến nghị.
* Cấu trúc dữ liệu và giải thuật.
* Cơ sở dữ liệu.
* Lập trình web.
* Kỹ nghệ phần mềm.
* Data Engineering.
* MLOps cơ bản.

---

# 1. MỤC TIÊU QUAN TRỌNG

Không chỉ tạo giao diện hoặc gọi API đơn giản.

Hãy tạo một repository hoàn chỉnh, có thể chạy được trên máy cá nhân, gồm:

* Frontend.
* Backend.
* Database.
* Authentication.
* Payment test mode.
* PDF processing.
* RAG.
* Deep Learning.
* Recommendation system.
* Data ingestion pipeline.
* Background jobs.
* Automated tests.
* Docker.
* GitHub Actions.
* Documentation.
* Hướng dẫn triển khai.
* Dữ liệu mẫu.
* File cấu hình môi trường mẫu.

Code phải được chia nhỏ khoa học, rõ ràng và dễ đọc.

Không được viết toàn bộ backend trong một file `main.py`.

Không được viết toàn bộ frontend trong một file `page.tsx`.

Không được chỉ tạo mã giả, TODO hoặc placeholder cho các chức năng chính.

Các chức năng chính phải có code thực tế và chạy được.

---

# 2. PHẠM VI THỰC TẾ

Đây là dự án portfolio của sinh viên nên phải thỏa mãn đồng thời hai điều:

1. Có kiến trúc đủ chuyên nghiệp để gây ấn tượng với nhà tuyển dụng.
2. Có chế độ chạy local với tài nguyên máy tính thông thường.

Không tải hàng triệu bài báo ngay trong lần chạy đầu tiên.

Hãy xây dựng hai chế độ:

## Chế độ Development

* Sử dụng khoảng 1.000–10.000 bài báo mẫu.
* Có thể chạy bằng Docker Compose.
* Chạy được trên máy có RAM khoảng 8–16 GB.
* Có thể tắt các dịch vụ nặng.
* Có mock data khi chưa có API key.

## Chế độ Scalable Ingestion

* Có pipeline có khả năng xử lý hàng triệu metadata bài báo.
* Đọc dữ liệu theo batch hoặc streaming.
* Không nạp toàn bộ dữ liệu vào RAM.
* Có checkpoint để tiếp tục khi pipeline bị dừng.
* Có logging và thống kê tiến độ.
* Có deduplication.
* Có retry.
* Có rate limiting.
* Có thể nhập dữ liệu từ OpenAlex API hoặc OpenAlex Snapshot.
* Tài liệu phải giải thích cách mở rộng hệ thống, không tuyên bố demo local đã chứa hàng triệu bài báo.

---

# 3. CÔNG NGHỆ BẮT BUỘC

## Frontend

Sử dụng:

* Next.js.
* TypeScript.
* App Router.
* Tailwind CSS.
* TanStack Query.
* React Hook Form.
* Zod.
* ECharts hoặc Recharts.
* Cytoscape.js để vẽ citation graph.
* Markdown renderer cho nội dung chatbot.
* ESLint.
* Prettier.

## Backend

Sử dụng:

* Python.
* FastAPI.
* Pydantic.
* SQLAlchemy 2.
* Alembic.
* PostgreSQL.
* pgvector.
* Redis.
* Celery hoặc RQ cho background jobs.
* HTTPX.
* Pandas hoặc Polars.
* NetworkX.
* Scikit-learn.
* PyTorch.
* Sentence Transformers.
* PyMuPDF để đọc PDF.
* Stripe ở test mode.
* JWT access token và refresh token.
* Passlib hoặc Argon2 để băm mật khẩu.

Ưu tiên code Python rõ ràng, dễ hiểu, có type hints.

Không lạm dụng framework AI nếu làm code khó hiểu.

Có thể dùng LangChain hoặc LlamaIndex ở một lớp riêng, nhưng pipeline RAG cốt lõi phải được trình bày rõ:

```text
PDF
→ Extract text
→ Clean text
→ Split chunks
→ Create embeddings
→ Store vectors
→ Retrieve
→ Rerank
→ Build prompt
→ Generate answer
→ Return citations
```

---

# 4. MÔ HÌNH AI VÀ LLM

Hệ thống phải hỗ trợ hai chế độ.

## Chế độ miễn phí local

* Sentence Transformer chạy local để tạo embedding.
* Có thể sử dụng một model nhỏ từ Hugging Face.
* Có một mock LLM hoặc extractive answer mode khi không có API key.
* Có thể kết nối Ollama nếu người dùng cài Ollama.

## Chế độ API

Hỗ trợ cấu hình một trong các nhà cung cấp LLM thông qua biến môi trường.

Tạo interface chung, ví dụ:

```python
class LLMProvider(Protocol):
    async def generate(self, messages: list[Message]) -> LLMResponse:
        ...
```

Các provider phải được đặt ở module riêng.

Không hard-code API key.

Không đưa API key thật vào repository.

---

# 5. CẤU TRÚC REPOSITORY

Hãy tạo cấu trúc tương tự dưới đây và có thể điều chỉnh khi cần:

```text
openresearch-graph/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   ├── search/
│   │   │   ├── papers/[paperId]/
│   │   │   ├── analytics/
│   │   │   ├── graph/
│   │   │   ├── library/
│   │   │   ├── chat/
│   │   │   ├── recommendations/
│   │   │   ├── pricing/
│   │   │   ├── account/
│   │   │   ├── admin/
│   │   │   └── about/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   ├── layout/
│   │   │   ├── auth/
│   │   │   ├── papers/
│   │   │   ├── charts/
│   │   │   ├── graph/
│   │   │   ├── chat/
│   │   │   └── billing/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── services/
│   │   ├── stores/
│   │   ├── types/
│   │   └── utils/
│   ├── public/
│   ├── tests/
│   ├── .env.example
│   ├── Dockerfile
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── dependencies.py
│   │   │   └── v1/
│   │   │       ├── router.py
│   │   │       ├── auth.py
│   │   │       ├── users.py
│   │   │       ├── papers.py
│   │   │       ├── search.py
│   │   │       ├── analytics.py
│   │   │       ├── graphs.py
│   │   │       ├── documents.py
│   │   │       ├── chat.py
│   │   │       ├── recommendations.py
│   │   │       ├── subscriptions.py
│   │   │       └── admin.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── logging.py
│   │   │   ├── exceptions.py
│   │   │   └── rate_limit.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── repositories/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── openalex_service.py
│   │   │   ├── paper_service.py
│   │   │   ├── pdf_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── retrieval_service.py
│   │   │   ├── reranking_service.py
│   │   │   ├── rag_service.py
│   │   │   ├── recommendation_service.py
│   │   │   ├── graph_service.py
│   │   │   ├── analytics_service.py
│   │   │   ├── payment_service.py
│   │   │   └── storage_service.py
│   │   ├── ml/
│   │   │   ├── datasets/
│   │   │   ├── features/
│   │   │   ├── models/
│   │   │   ├── training/
│   │   │   ├── evaluation/
│   │   │   └── inference/
│   │   ├── tasks/
│   │   ├── workers/
│   │   └── utils/
│   ├── alembic/
│   ├── scripts/
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── fixtures/
│   ├── uploads/
│   ├── .env.example
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── Dockerfile
│
├── data_pipeline/
│   ├── ingestion/
│   ├── processing/
│   ├── validation/
│   ├── checkpoints/
│   ├── scripts/
│   ├── tests/
│   └── README.md
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_search_baseline.ipynb
│   ├── 03_recommendation_baseline.ipynb
│   └── 04_model_evaluation.ipynb
│
├── docs/
│   ├── architecture.md
│   ├── database.md
│   ├── api.md
│   ├── rag.md
│   ├── recommendation.md
│   ├── deployment.md
│   ├── security.md
│   └── limitations.md
│
├── scripts/
├── .github/workflows/
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
├── .gitignore
├── Makefile
├── LICENSE
└── README.md
```

Mọi thư mục phải có chức năng rõ ràng.

Xóa các thư mục không cần thiết thay vì tạo cấu trúc rỗng quá nhiều.

---

# 6. CƠ SỞ DỮ LIỆU

Thiết kế database bằng PostgreSQL và SQLAlchemy.

Tạo Alembic migrations đầy đủ.

Các bảng chính nên gồm:

## User

* id.
* email.
* username.
* password_hash.
* full_name.
* avatar_url.
* role.
* is_active.
* is_verified.
* created_at.
* updated_at.
* last_login_at.

## RefreshToken hoặc UserSession

* id.
* user_id.
* token_hash.
* expires_at.
* revoked_at.
* device_info.
* ip_address.

## Subscription

* id.
* user_id.
* plan.
* status.
* stripe_customer_id.
* stripe_subscription_id.
* current_period_start.
* current_period_end.
* cancel_at_period_end.

## Paper

* id nội bộ.
* openalex_id.
* doi.
* title.
* abstract.
* publication_date.
* publication_year.
* language.
* cited_by_count.
* referenced_works_count.
* is_open_access.
* open_access_url.
* pdf_url.
* source_name.
* type.
* metadata JSON.
* created_at.
* updated_at.

## Author

* id.
* openalex_id.
* name.
* orcid.
* cited_by_count.
* works_count.

## Institution

* id.
* openalex_id.
* name.
* country_code.
* institution_type.

## PaperAuthor

* paper_id.
* author_id.
* author_position.
* is_corresponding.

## PaperInstitution

* paper_id.
* institution_id.

## Citation

* citing_paper_id.
* cited_paper_id.

## Topic

* id.
* name.
* description.
* embedding.

## PaperTopic

* paper_id.
* topic_id.
* score.

## UserPaperInteraction

* user_id.
* paper_id.
* interaction_type.
* interaction_value.
* created_at.

Các interaction type gồm:

* view.
* click.
* save.
* unsave.
* download.
* share.
* cite.
* like.
* dislike.
* chat.
* dismiss.

## LibraryItem

* id.
* user_id.
* paper_id.
* collection_name.
* notes.
* tags.
* created_at.

## UploadedDocument

* id.
* user_id.
* original_filename.
* stored_filename.
* mime_type.
* file_size.
* storage_path.
* checksum.
* processing_status.
* page_count.
* created_at.

## DocumentChunk

* id.
* document_id.
* page_number.
* chunk_index.
* content.
* token_count.
* embedding.
* metadata.

## ChatSession

* id.
* user_id.
* title.
* created_at.
* updated_at.

## ChatMessage

* id.
* session_id.
* role.
* content.
* citations JSON.
* token_usage.
* created_at.

## SearchHistory

* id.
* user_id.
* query.
* filters JSON.
* result_count.
* created_at.

## RecommendationLog

* id.
* user_id.
* paper_id.
* algorithm.
* score.
* explanation.
* clicked.
* saved.
* created_at.

Thêm index phù hợp cho:

* OpenAlex ID.
* DOI.
* publication_year.
* cited_by_count.
* user_id.
* document_id.
* vector search.
* full-text search.

---

# 7. AUTHENTICATION VÀ AUTHORIZATION

Xây dựng đầy đủ:

* Đăng ký.
* Đăng nhập.
* Đăng xuất.
* Refresh token.
* Thu hồi refresh token.
* Lấy thông tin người dùng hiện tại.
* Đổi mật khẩu.
* Quên mật khẩu.
* Reset mật khẩu.
* Email verification ở chế độ mock hoặc console.
* Role `user`, `premium`, `admin`.
* Route guard phía frontend.
* Dependency kiểm tra quyền phía backend.

Yêu cầu bảo mật:

* Băm mật khẩu bằng Argon2 hoặc bcrypt.
* Không lưu refresh token dạng plain text trong database.
* Access token có thời gian sống ngắn.
* Refresh token có thời gian sống dài hơn.
* Có token rotation.
* Có giới hạn số lần đăng nhập thất bại.
* Không trả password hash ra API.
* Validate dữ liệu đầu vào.
* CORS cấu hình bằng biến môi trường.
* Có security headers cơ bản.
* Không ghi API key hoặc mật khẩu vào log.

---

# 8. THANH TOÁN

Tích hợp Stripe ở test mode.

Có các gói:

## Free

* Số lượt tìm kiếm giới hạn.
* Số PDF tải lên giới hạn.
* Số câu hỏi chatbot mỗi ngày giới hạn.
* Recommendation cơ bản.

## Premium

* Giới hạn cao hơn.
* Reranking tốt hơn.
* Nhiều PDF hơn.
* Recommendation nâng cao.
* Export kết quả.
* Analytics nâng cao.

Xây dựng:

* Trang pricing.
* Tạo Stripe Checkout Session.
* Customer Portal.
* Webhook Stripe.
* Đồng bộ trạng thái subscription.
* Xử lý payment success, failed, canceled.
* Không xử lý trực tiếp thông tin thẻ.
* Có mock billing mode khi chưa có Stripe key.

Tạo hướng dẫn rõ nơi người dùng phải thêm:

```env
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
STRIPE_PRICE_PREMIUM_MONTHLY=
```

---

# 9. OPENALEX VÀ THU THẬP DỮ LIỆU

Tích hợp OpenAlex để lấy:

* Papers.
* Authors.
* Institutions.
* Topics.
* Sources.
* Citation references.
* Open access information.

Yêu cầu service OpenAlex:

* Async HTTP client.
* Timeout.
* Retry với exponential backoff.
* Rate limiting.
* Pagination.
* Cursor pagination nếu API hỗ trợ.
* Cache Redis.
* Chuẩn hóa dữ liệu.
* Xử lý thiếu trường.
* Logging.
* Không làm API crash khi OpenAlex lỗi.

Xây dựng data ingestion CLI, ví dụ:

```bash
python -m data_pipeline.ingestion.openalex \
  --query "deep learning" \
  --from-year 2020 \
  --to-year 2026 \
  --max-records 5000
```

Và pipeline nhập snapshot theo batch, ví dụ:

```bash
python -m data_pipeline.ingestion.snapshot \
  --input-path /data/openalex-snapshot \
  --batch-size 5000 \
  --checkpoint-path ./checkpoints/openalex.json
```

Pipeline phải:

* Đọc từng batch.
* Transform.
* Validate.
* Upsert.
* Commit theo batch.
* Ghi checkpoint.
* Có resume.
* Có thống kê số bản ghi thành công và lỗi.
* Không lưu toàn bộ dataset trong RAM.
* Có dead-letter file cho bản ghi lỗi.

---

# 10. TÌM KIẾM BÀI BÁO

Hệ thống tìm kiếm cần có nhiều tầng.

## Baseline 1

* PostgreSQL full-text search.
* Tìm theo title, abstract, author, topic.

## Baseline 2

* TF-IDF.
* Cosine similarity.

## Semantic Search

* Sentence Transformer embeddings.
* pgvector similarity search.

## Hybrid Search

Kết hợp:

* Keyword score.
* Semantic score.
* Citation score.
* Recency score.
* Open-access score.

Ví dụ công thức:

```text
final_score =
    w1 × keyword_score
  + w2 × semantic_score
  + w3 × normalized_citation_score
  + w4 × recency_score
  + w5 × open_access_score
```

Các trọng số phải được cấu hình.

Không chỉ hard-code một công thức không giải thích.

## Reranking

Sử dụng cross-encoder nhỏ để rerank top kết quả.

Nếu model không tải được, hệ thống phải fallback về hybrid score.

API tìm kiếm phải hỗ trợ:

* Query.
* Năm bắt đầu.
* Năm kết thúc.
* Tác giả.
* Tổ chức.
* Topic.
* Open access.
* Loại công trình.
* Sắp xếp theo relevance.
* Sắp xếp theo citation.
* Sắp xếp theo mới nhất.
* Pagination.

---

# 11. PHÂN TÍCH XU HƯỚNG

Tạo trang analytics có:

* Số bài báo theo năm.
* Tổng số citation theo năm.
* Citation trung bình.
* Top tác giả.
* Top tổ chức.
* Top nguồn xuất bản.
* Top topic.
* Tỷ lệ Open Access.
* Số bài theo quốc gia.
* Chủ đề tăng trưởng nhanh.
* Chủ đề giảm dần.
* Phân bố citation.
* Phân cụm bài báo.

Tạo endpoint backend tổng hợp dữ liệu.

Không để frontend phải tự xử lý hàng chục nghìn bản ghi.

Có cache cho truy vấn analytics.

---

# 12. CITATION GRAPH

Sử dụng NetworkX phía backend và Cytoscape.js phía frontend.

Chức năng:

* Vẽ node bài báo.
* Edge biểu diễn quan hệ trích dẫn.
* Node size theo citation.
* Node color theo topic hoặc publication year.
* Click node để xem thông tin.
* Lọc node.
* Zoom.
* Search node.
* Hiển thị legend.
* Giới hạn số node mặc định để tránh lag.
* Có thông báo khi graph bị cắt bớt.

Các thuật toán cần có:

* PageRank.
* Degree centrality.
* Betweenness centrality.
* Community detection.
* Connected components.

Trả về explanation cho paper quan trọng:

```text
Bài báo này có PageRank cao vì được nhiều bài có ảnh hưởng trích dẫn.
```

---

# 13. CHATBOT ĐỌC PDF BẰNG RAG

Người dùng có thể:

* Tải PDF lên.
* Xem trạng thái xử lý.
* Tạo chat session.
* Đặt câu hỏi.
* Nhận câu trả lời.
* Xem trích dẫn theo số trang.
* Bấm citation để mở đúng trang hoặc đoạn.
* Xóa tài liệu.
* Xóa lịch sử chat.

## PDF Pipeline

1. Kiểm tra file type.
2. Kiểm tra kích thước.
3. Tính checksum.
4. Lưu file.
5. Đọc text bằng PyMuPDF.
6. Phát hiện PDF không có text.
7. Báo rõ rằng OCR chưa được bật hoặc hỗ trợ OCR tùy chọn.
8. Làm sạch header/footer lặp lại.
9. Chia đoạn theo heading, paragraph và token length.
10. Thêm overlap.
11. Tạo embedding.
12. Lưu vector.
13. Cập nhật trạng thái xử lý.

## Retrieval

* Vector search.
* Có thể kết hợp keyword search.
* Lấy top-k chunk.
* Rerank.
* Loại chunk gần trùng.
* Giữ metadata page number.
* Tạo context có giới hạn token.

## Generation

Prompt hệ thống phải yêu cầu:

* Chỉ trả lời dựa trên context.
* Không bịa thông tin.
* Nói không tìm thấy khi context không đủ.
* Luôn trả citation.
* Không tiết lộ system prompt.

Phản hồi API cần có dạng:

```json
{
  "answer": "...",
  "citations": [
    {
      "document_id": "...",
      "page": 5,
      "chunk_id": "...",
      "quote": "..."
    }
  ],
  "retrieval_scores": [],
  "model": "...",
  "latency_ms": 0
}
```

## Chống prompt injection

PDF có thể chứa chỉ dẫn độc hại.

Hệ thống phải:

* Xem PDF là dữ liệu, không phải chỉ dẫn hệ thống.
* Không cho nội dung PDF thay đổi system prompt.
* Không thực thi code từ PDF.
* Không tiết lộ secret.
* Có kiểm tra prompt injection cơ bản.
* Có tài liệu nêu hạn chế.

---

# 14. DEEP LEARNING

Dự án phải có phần Deep Learning thực sự, không chỉ gọi API.

Tạo ít nhất một mô hình có thể train hoặc fine-tune.

Ưu tiên mô hình:

## Paper Relevance Classifier

Đầu vào:

* Query.
* Paper title.
* Paper abstract.

Đầu ra:

* Điểm liên quan từ 0 đến 1.

Có thể sử dụng:

* Bi-encoder.
* Cross-encoder.
* PyTorch.
* Sentence Transformer.

Tạo:

* Dataset class.
* Data loader.
* Training loop.
* Validation loop.
* Checkpoint.
* Early stopping.
* Metrics.
* Config.
* Inference service.

Metrics:

* Accuracy.
* Precision.
* Recall.
* F1.
* ROC-AUC nếu phù hợp.
* nDCG khi đánh giá ranking.

Có script:

```bash
python -m app.ml.training.train_relevance \
  --config configs/relevance.yaml
```

Không cần train model lớn mặc định.

Tạo dữ liệu mẫu nhỏ và hướng dẫn người dùng tạo dataset lớn hơn.

Ngoài mô hình Deep Learning, phải có baseline Logistic Regression hoặc TF-IDF để so sánh.

---

# 15. HỆ THỐNG KHUYẾN NGHỊ PHỨC TẠP

Không chỉ đề xuất bài có citation cao.

Xây dựng hybrid recommendation system gồm:

## Content-based

* Embedding của title và abstract.
* Topic similarity.
* Author similarity.
* Institution similarity.

## Collaborative Filtering

Dựa trên:

* View.
* Save.
* Click.
* Download.
* Like.
* Dislike.
* Dismiss.

Có thể sử dụng implicit feedback matrix factorization.

## Graph-based

* Citation graph.
* Author-paper graph.
* Topic-paper graph.
* Personalized PageRank.

## Popularity và Trending

* Citation.
* Lượt xem.
* Lượt lưu.
* Tốc độ tăng trưởng.
* Publication recency.

## Hybrid Ranker

Kết hợp nhiều score.

Ví dụ:

```text
recommendation_score =
    a × content_score
  + b × collaborative_score
  + c × graph_score
  + d × popularity_score
  + e × recency_score
```

Có cold-start strategy:

* Người dùng mới chọn lĩnh vực quan tâm.
* Sử dụng topic preferences.
* Đề xuất bài phổ biến có diversity.
* Không đề xuất toàn bộ bài cùng một chủ đề.

Có explanation:

```text
Được đề xuất vì bạn đã lưu các bài về reinforcement learning
và bài này có nội dung tương tự với các bài trong thư viện của bạn.
```

Có đánh giá offline:

* Precision@K.
* Recall@K.
* MAP@K.
* nDCG@K.
* Coverage.
* Diversity.
* Novelty.

Có notebook hoặc script so sánh:

* Popularity baseline.
* Content-based.
* Collaborative filtering.
* Hybrid recommendation.

---

# 16. FRONTEND

Thiết kế giao diện hiện đại nhưng không quá cầu kỳ.

Phong cách:

* Chuyên nghiệp.
* Gọn.
* Dễ đọc.
* Responsive.
* Có dark mode nếu phù hợp.
* Không lạm dụng animation.
* Không sử dụng dữ liệu giả sau khi backend đã có dữ liệu thật.

Các trang bắt buộc:

## Landing Page

* Giới thiệu vấn đề.
* Tính năng.
* Demo search.
* Kiến trúc ngắn gọn.
* Link GitHub.
* Pricing.

## Search

* Thanh tìm kiếm.
* Filter.
* Sort.
* Pagination.
* Loading skeleton.
* Error state.
* Empty state.
* Paper card.
* Save paper.
* Open access link.

## Paper Detail

* Title.
* Authors.
* Institution.
* Abstract.
* Citation.
* References.
* Topics.
* Related papers.
* Citation graph nhỏ.
* Nút lưu.
* Nút hỏi AI.

## Analytics

* Biểu đồ.
* Filter.
* Tooltips.
* Export CSV nếu là Premium.

## Citation Graph

* Interactive graph.
* Search node.
* Filter.
* Legend.
* Paper detail side panel.

## PDF Chat

* Upload PDF.
* Danh sách tài liệu.
* Processing status.
* Chat history.
* Source citation.
* Page preview hoặc link trang.
* Loading state.
* Stop generation nếu có streaming.

## Recommendations

* Danh sách đề xuất.
* Explanation.
* Like.
* Dislike.
* Dismiss.
* Save.
* Filter theo chủ đề.

## Library

* Saved papers.
* Collections.
* Tags.
* Notes.
* Search.
* Remove.
* Export.

## Pricing

* Free.
* Premium.
* Stripe checkout.

## Account

* Profile.
* Password.
* Subscription.
* Usage.
* Logout all devices.

## Admin

* User statistics.
* Paper statistics.
* Ingestion jobs.
* Failed jobs.
* System health.
* Không cho user thường truy cập.

---

# 17. API ENDPOINTS

Tạo REST API versioned dưới `/api/v1`.

Ví dụ:

```text
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
GET    /api/v1/users/me
PATCH  /api/v1/users/me

GET    /api/v1/search/papers
GET    /api/v1/papers/{paper_id}
GET    /api/v1/papers/{paper_id}/related
GET    /api/v1/papers/{paper_id}/citations

GET    /api/v1/analytics/trends
GET    /api/v1/analytics/authors
GET    /api/v1/analytics/institutions
GET    /api/v1/analytics/topics

GET    /api/v1/graphs/citations

POST   /api/v1/documents/upload
GET    /api/v1/documents
GET    /api/v1/documents/{document_id}
DELETE /api/v1/documents/{document_id}

POST   /api/v1/chat/sessions
GET    /api/v1/chat/sessions
GET    /api/v1/chat/sessions/{session_id}
POST   /api/v1/chat/sessions/{session_id}/messages
DELETE /api/v1/chat/sessions/{session_id}

GET    /api/v1/recommendations
POST   /api/v1/recommendations/{paper_id}/feedback

GET    /api/v1/library
POST   /api/v1/library
DELETE /api/v1/library/{paper_id}

POST   /api/v1/subscriptions/checkout
POST   /api/v1/subscriptions/portal
POST   /api/v1/subscriptions/webhook
GET    /api/v1/subscriptions/me

GET    /api/v1/admin/health
GET    /api/v1/admin/ingestion-jobs
POST   /api/v1/admin/ingestion-jobs
```

Tạo Swagger/OpenAPI tự động.

Thêm response schemas rõ ràng.

Sử dụng status code đúng.

---

# 18. BACKGROUND JOBS

Dùng Celery hoặc RQ với Redis.

Các task gồm:

* Xử lý PDF.
* Tạo embeddings.
* Đồng bộ OpenAlex.
* Cập nhật citation.
* Tạo topic.
* Tính PageRank.
* Tạo recommendation.
* Gửi email mock.
* Dọn file tạm.
* Cập nhật usage.
* Retry job thất bại.

Có trạng thái:

* pending.
* running.
* completed.
* failed.
* canceled.

Có endpoint hoặc admin page xem tiến độ.

---

# 19. CACHE VÀ RATE LIMIT

Dùng Redis cho:

* Cache search.
* Cache analytics.
* Rate limiting.
* Celery broker.
* Session metadata nếu cần.

Có rate limit theo:

* IP.
* User.
* Subscription plan.

Ví dụ:

* Free: 20 search/giờ.
* Premium: giới hạn cao hơn.
* Anonymous: thấp hơn.

Các giới hạn phải cấu hình được bằng biến môi trường.

---

# 20. TESTING

Tạo test thực tế.

## Backend

* Unit tests cho services.
* Tests cho authentication.
* Tests cho password hashing.
* Tests cho JWT.
* Tests cho search scoring.
* Tests cho recommendation scoring.
* Tests cho PDF chunking.
* Tests cho citation extraction.
* Tests cho Stripe webhook verification.
* Integration tests với database test.
* Mock OpenAlex.
* Mock LLM.
* Mock Stripe.

Dùng:

* Pytest.
* Pytest-asyncio.
* HTTPX TestClient hoặc AsyncClient.

## Frontend

* Component tests.
* Form validation tests.
* Search page tests.
* Auth tests.
* API error state tests.

Dùng:

* Vitest hoặc Jest.
* React Testing Library.

## End-to-end

Tạo một số test Playwright cho:

* Đăng ký.
* Đăng nhập.
* Tìm bài.
* Lưu bài.
* Upload PDF.
* Gửi câu hỏi.
* Xem recommendation.

Không cần test mọi chi tiết nhưng các luồng chính phải có test.

---

# 21. CODE QUALITY

Backend:

* Type hints.
* Docstring cho class và hàm phức tạp.
* Ruff.
* Black nếu cần.
* MyPy.
* Pre-commit.

Frontend:

* TypeScript strict mode.
* ESLint.
* Prettier.
* Không dùng `any` nếu không thực sự cần.
* Tách API client.
* Tách types.
* Tách component.
* Có error boundary phù hợp.

Quy tắc:

* Không copy-paste logic.
* Không tạo hàm dài hàng trăm dòng.
* Không hard-code URL.
* Không hard-code key.
* Không hard-code plan limit.
* Không nuốt exception.
* Không dùng `except Exception: pass`.
* Không ghi log token hoặc password.
* Không trả stack trace cho frontend.
* Không dùng biến tên khó hiểu.

---

# 22. DOCKER

Tạo:

* Dockerfile cho frontend.
* Dockerfile cho backend.
* Docker Compose.

Các service:

```text
frontend
backend
worker
postgres
redis
```

Có thể thêm service model local hoặc object storage ở profile tùy chọn.

Docker Compose phải:

* Có healthcheck.
* Có volumes.
* Có network.
* Có dependency hợp lý.
* Có restart policy phù hợp.
* Không đưa secret trực tiếp vào file.

Lệnh khởi chạy mong muốn:

```bash
docker compose up --build
```

Sau khi chạy:

```text
Frontend: http://localhost:3000
Backend: http://localhost:8000
Swagger: http://localhost:8000/docs
```

---

# 23. GITHUB ACTIONS

Tạo workflow:

## Backend CI

* Cài Python.
* Cài dependencies.
* Ruff.
* MyPy.
* Pytest.

## Frontend CI

* Cài Node.
* npm ci.
* Lint.
* Type check.
* Test.
* Build.

## Docker Build

* Kiểm tra image build thành công.

Không cần deploy thật nếu chưa có secret.

---

# 24. FILE MÔI TRƯỜNG

Tạo `.env.example` hoàn chỉnh.

Ví dụ:

```env
APP_NAME=OpenResearch Graph
ENVIRONMENT=development
DEBUG=true

BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000

DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/openresearch
REDIS_URL=redis://redis:6379/0

JWT_SECRET_KEY=replace_with_a_long_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=14

OPENALEX_API_KEY=
OPENALEX_BASE_URL=https://api.openalex.org

EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
RERANKER_MODEL_NAME=cross-encoder/ms-marco-MiniLM-L-6-v2
EMBEDDING_DEVICE=cpu

LLM_PROVIDER=mock
OPENAI_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=

MAX_UPLOAD_SIZE_MB=25
MAX_FREE_DOCUMENTS=3
MAX_PREMIUM_DOCUMENTS=50
MAX_FREE_CHAT_MESSAGES_PER_DAY=20

STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PRICE_PREMIUM_MONTHLY=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=

SMTP_HOST=
SMTP_PORT=
SMTP_USERNAME=
SMTP_PASSWORD=
EMAIL_FROM=noreply@example.com

STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=./uploads
```

Tạo hướng dẫn tạo JWT secret, ví dụ bằng Python hoặc OpenSSL.

---

# 25. SEED DATA

Tạo script seed:

```bash
python -m app.scripts.seed
```

Script tạo:

* Một admin.
* Một user thường.
* Một premium user.
* Một số paper mẫu.
* Một số author.
* Một số topic.
* Một số interactions.
* Một số recommendations.

Thông tin tài khoản demo chỉ sử dụng trong development và phải ghi rõ trong README.

---

# 26. NOTEBOOKS VÀ ĐÁNH GIÁ KHOA HỌC DỮ LIỆU

Tạo notebook có cấu trúc rõ ràng:

## Data Exploration

* Missing values.
* Citation distribution.
* Publication trends.
* Authors.
* Topics.
* Outliers.

## Search Baseline

So sánh:

* Keyword.
* TF-IDF.
* Embedding.
* Hybrid.
* Reranker.

## Recommendation Baseline

So sánh:

* Popularity.
* Content-based.
* Collaborative filtering.
* Hybrid.

## Model Evaluation

* Metrics.
* Charts.
* Error analysis.
* Limitations.
* Kết luận.

Notebook không được chứa toàn bộ logic sản phẩm.

Logic dùng chung phải đặt trong package Python rồi import vào notebook.

---

# 27. README CHUYÊN NGHIỆP

README phải gồm:

1. Tên dự án.
2. Hình minh họa hoặc vị trí đặt screenshot.
3. Bài toán thực tế.
4. Đối tượng sử dụng.
5. Các chức năng.
6. Demo.
7. Kiến trúc hệ thống.
8. Tech stack.
9. Database schema.
10. RAG pipeline.
11. Recommendation pipeline.
12. Deep Learning model.
13. Data sources.
14. Cách cài đặt.
15. Cách chạy Docker.
16. Cách chạy không dùng Docker.
17. Cách thêm API key.
18. Cách cấu hình Stripe test mode.
19. Cách lấy dữ liệu OpenAlex.
20. Cách chạy migrations.
21. Cách seed database.
22. Cách chạy worker.
23. Cách chạy tests.
24. Kết quả đánh giá.
25. Limitations.
26. Roadmap.
27. License.
28. Lưu ý bảo mật.
29. Cấu trúc repository.
30. Conventional commits được đề xuất.

README phải có lệnh chính xác để copy và chạy.

---

# 28. HƯỚNG DẪN CHO NGƯỜI DÙNG SAU KHI CODE XONG

Sau khi hoàn thành code, tạo file:

```text
docs/SETUP_GUIDE_VI.md
```

Viết hướng dẫn bằng tiếng Việt cho người mới, bao gồm:

## Cài công cụ

* Git.
* Python.
* Node.js.
* Docker Desktop.
* VS Code.

## Clone dự án

```bash
git clone <repository-url>
cd openresearch-graph
```

## Tạo file môi trường

```bash
cp .env.example .env
```

Đối với Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

## Những key người dùng phải tự thêm

Giải thích cụ thể:

* OpenAlex API key lấy ở đâu.
* LLM API key thêm vào biến nào.
* Stripe test key lấy ở đâu.
* Stripe webhook chạy local như thế nào.
* JWT secret tạo như thế nào.
* SMTP có thể để trống trong development.

## Chạy Docker

```bash
docker compose up --build
```

## Chạy migration

```bash
docker compose exec backend alembic upgrade head
```

## Seed database

```bash
docker compose exec backend python -m app.scripts.seed
```

## Chạy frontend và backend thủ công

Hướng dẫn riêng cho Windows PowerShell.

## Chạy worker

## Chạy test

## Kiểm tra Swagger

## Các lỗi thường gặp

* Port đang được sử dụng.
* Docker chưa chạy.
* Database chưa sẵn sàng.
* Thiếu API key.
* Sai CORS.
* Model tải chậm.
* Hết RAM.
* Stripe webhook sai.
* Alembic lỗi revision.
* PowerShell chặn activate venv.
* `ModuleNotFoundError`.
* `npm install` lỗi.
* Git push bị từ chối.

## Đưa lên GitHub

Hướng dẫn:

```bash
git init
git add .
git commit -m "chore: initialize OpenResearch Graph"
git branch -M main
git remote add origin <repository-url>
git push -u origin main
```

Hướng dẫn những lần push sau:

```bash
git status
git add .
git commit -m "feat: add citation graph"
git pull origin main --rebase
git push origin main
```

---

# 29. TÀI LIỆU KIẾN TRÚC

Tạo sơ đồ Mermaid cho:

* System architecture.
* Request flow.
* Authentication flow.
* RAG flow.
* Recommendation flow.
* Data ingestion flow.
* Payment flow.
* Database ERD.

Ví dụ phải nằm trong các file Markdown để GitHub hiển thị được.
# 29A. CẨM NANG THAO TÁC ỨNG DỤNG VÀ DỊCH VỤ BÊN NGOÀI

Sau khi tạo xong source code, không chỉ viết hướng dẫn chạy dự án chung chung.

Hãy tạo một bộ tài liệu bằng tiếng Việt giúp một sinh viên chưa từng cấu hình hệ thống có thể tự:

* Cài phần mềm cần thiết.
* Tạo tài khoản trên các dịch vụ bên ngoài.
* Lấy API key.
* Thêm API key vào đúng file.
* Khởi động từng dịch vụ.
* Kiểm tra kết nối.
* Xác định dịch vụ nào đang lỗi.
* Thay đổi nhà cung cấp mà không sửa code.
* Thu hồi hoặc thay API key.
* Chuyển từ mock mode sang real mode.
* Đưa dự án lên GitHub.
* Triển khai thử nghiệm.

Không được chỉ viết:

```text
Thêm API key vào file .env.
```

Phải chỉ rõ:

1. Mở website hoặc phần mềm nào.
2. Đăng ký hoặc đăng nhập ở đâu.
3. Mở khu vực cài đặt nào.
4. Tạo key hoặc webhook như thế nào.
5. Sao chép giá trị nào.
6. Dán vào biến môi trường nào.
7. Khởi động lại service nào.
8. Chạy lệnh gì để kiểm tra.
9. Kết quả đúng phải trông như thế nào.
10. Các lỗi thường gặp và cách khắc phục.

---

# 29B. CẤU TRÚC BỘ TÀI LIỆU HƯỚNG DẪN

Tạo các file sau:

```text
docs/
├── 00_START_HERE_VI.md
├── 01_SYSTEM_REQUIREMENTS_VI.md
├── 02_INSTALLATION_WINDOWS_VI.md
├── 03_INSTALLATION_DOCKER_VI.md
├── 04_ENVIRONMENT_VARIABLES_VI.md
├── 05_DATABASE_POSTGRESQL_VI.md
├── 06_OPENALEX_SETUP_VI.md
├── 07_LLM_SETUP_VI.md
├── 08_OLLAMA_LOCAL_VI.md
├── 09_HUGGINGFACE_MODELS_VI.md
├── 10_STRIPE_TEST_MODE_VI.md
├── 11_EMAIL_SERVICE_VI.md
├── 12_FILE_STORAGE_VI.md
├── 13_REDIS_AND_WORKER_VI.md
├── 14_GITHUB_GUIDE_VI.md
├── 15_DEPLOYMENT_VI.md
├── 16_OPERATION_MANUAL_VI.md
├── 17_TROUBLESHOOTING_VI.md
├── 18_SECURITY_CHECKLIST_VI.md
└── EXTERNAL_SERVICES_MATRIX.md
```

Tài liệu phải ưu tiên Windows 10/11 và PowerShell vì đây là môi trường chính của người dùng.

Có thể bổ sung lệnh Linux hoặc macOS, nhưng không được chỉ cung cấp lệnh Bash.

---

# 29C. FILE BẮT ĐẦU NHANH

File:

```text
docs/00_START_HERE_VI.md
```

phải đóng vai trò là cẩm nang chính.

Nội dung phải chia thành các checkpoint.

## Checkpoint 1 — Kiểm tra máy

Hướng dẫn chạy:

```powershell
git --version
python --version
node --version
npm --version
docker --version
docker compose version
```

Với mỗi lệnh, giải thích:

* Lệnh dùng để kiểm tra gì.
* Kết quả hợp lệ trông như thế nào.
* Nếu báo không tìm thấy lệnh thì phải cài gì.
* Có cần khởi động lại PowerShell hay không.

## Checkpoint 2 — Chuẩn bị source code

```powershell
git clone <repository-url>
cd openresearch-graph
Copy-Item .env.example .env
```

## Checkpoint 3 — Khởi động hạ tầng

```powershell
docker compose up -d postgres redis
```

## Checkpoint 4 — Chạy migration

```powershell
docker compose run --rm backend alembic upgrade head
```

## Checkpoint 5 — Tạo dữ liệu mẫu

```powershell
docker compose run --rm backend python -m app.scripts.seed
```

## Checkpoint 6 — Chạy toàn bộ hệ thống

```powershell
docker compose up --build
```

## Checkpoint 7 — Kiểm tra

```text
Frontend: http://localhost:3000
Backend: http://localhost:8000
Swagger: http://localhost:8000/docs
```

## Checkpoint 8 — Kiểm thử chức năng

Yêu cầu người dùng thực hiện lần lượt:

1. Đăng ký tài khoản.
2. Đăng nhập.
3. Tìm một bài báo.
4. Mở chi tiết bài báo.
5. Lưu bài báo vào thư viện.
6. Tải PDF lên.
7. Chờ worker xử lý.
8. Đặt câu hỏi cho PDF.
9. Kiểm tra citation.
10. Mở trang recommendation.
11. Kiểm tra Stripe mock hoặc test mode.

Mỗi checkpoint phải có ô đánh dấu Markdown:

```markdown
- [ ] Đã hoàn thành
```

Không chuyển sang checkpoint tiếp theo khi checkpoint hiện tại chưa đạt.

---

# 29D. MA TRẬN DỊCH VỤ BÊN NGOÀI

Tạo file:

```text
docs/EXTERNAL_SERVICES_MATRIX.md
```

Nội dung phải có bảng:

| Dịch vụ               | Mục đích            |              Bắt buộc | Có chế độ miễn phí/mock | Biến môi trường   | Cách kiểm tra          | Fallback              |
| --------------------- | ------------------- | --------------------: | ----------------------: | ----------------- | ---------------------- | --------------------- |
| PostgreSQL            | Database chính      |                    Có |            Local Docker | DATABASE_URL      | Health endpoint        | Không                 |
| pgvector              | Vector search       |                    Có |            Local Docker | Không             | SQL kiểm tra extension | Không                 |
| Redis                 | Cache và worker     |                    Có |            Local Docker | REDIS_URL         | Redis ping             | In-memory development |
| OpenAlex              | Metadata bài báo    |   Có cho dữ liệu thật |       Có quota miễn phí | OPENALEX_API_KEY  | Test endpoint          | Seed data             |
| Ollama                | LLM local           |                 Không |                      Có | OLLAMA_BASE_URL   | List models            | Mock LLM              |
| LLM API               | Chatbot tốt hơn     |                 Không |            Tùy provider | Provider-specific | Test generation        | Ollama/mock           |
| Stripe                | Thanh toán          | Không khi development |               Test mode | STRIPE_*          | Trigger webhook        | Mock billing          |
| SMTP                  | Gửi email           |                 Không |         Console/Mailpit | SMTP_*            | Send test email        | Console backend       |
| S3-compatible storage | Lưu PDF production  |       Không khi local |     Local storage/MinIO | STORAGE_*         | Upload test file       | Local storage         |
| GitHub                | Quản lý source code |      Có cho portfolio |                      Có | Không             | Git push               | Local Git             |

Không được coi tất cả dịch vụ là bắt buộc.

Phải phân biệt:

* Bắt buộc để chạy core system.
* Chỉ bắt buộc cho một chức năng.
* Tùy chọn.
* Production only.

---

# 29E. HƯỚNG DẪN DOCKER DESKTOP

Trong tài liệu Docker, giải thích bằng tiếng Việt:

1. Cách cài Docker Desktop trên Windows.
2. Cách kiểm tra WSL 2.
3. Cách mở Docker Desktop.
4. Cách biết Docker Engine đã chạy.
5. Cách kiểm tra container.
6. Cách xem log.
7. Cách restart container.
8. Cách xóa container nhưng giữ database.
9. Cách xóa cả database volume.
10. Sự khác nhau giữa hai thao tác trên.

Cung cấp các lệnh:

```powershell
docker compose ps
docker compose logs backend
docker compose logs worker
docker compose logs postgres
docker compose logs redis
docker compose restart backend
docker compose down
docker compose down -v
```

Phải cảnh báo rõ:

```powershell
docker compose down -v
```

sẽ xóa volume database local và làm mất dữ liệu development.

Giải thích sự khác nhau giữa:

```powershell
docker compose up
docker compose up -d
docker compose up --build
```

---

# 29F. HƯỚNG DẪN POSTGRESQL VÀ PGVECTOR

Dự án phải sử dụng:

```text
PostgreSQL + pgvector
```

làm database chính.

Không thay bằng MySQL trong phiên bản mặc định.

Tạo tài liệu giải thích ngắn gọn:

* PostgreSQL lưu dữ liệu quan hệ.
* `jsonb` lưu metadata linh hoạt.
* Full-text search phục vụ keyword search.
* pgvector lưu embedding.
* Redis không thay thế PostgreSQL.
* File PDF không nên lưu trực tiếp toàn bộ trong database.

Docker Compose nên sử dụng PostgreSQL image đã hỗ trợ pgvector hoặc tự cài extension rõ ràng.

Migration đầu tiên phải chạy:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Tạo script kiểm tra:

```powershell
docker compose exec postgres psql `
  -U postgres `
  -d openresearch `
  -c "SELECT extversion FROM pg_extension WHERE extname = 'vector';"
```

Tạo tài liệu kết nối bằng pgAdmin hoặc DBeaver, bao gồm:

```text
Host: localhost
Port: 5432
Database: openresearch
Username: postgres
Password: lấy từ file .env
```

Giải thích các bảng quan trọng và cho người dùng thực hiện:

* Mở bảng users.
* Mở bảng papers.
* Mở bảng uploaded_documents.
* Mở bảng document_chunks.
* Mở bảng subscriptions.
* Xem thử một embedding nhưng không chỉnh sửa thủ công.
* Chạy một truy vấn SQL đơn giản.
* Sao lưu database development.
* Khôi phục database development.

Tạo các lệnh backup và restore phù hợp với Docker.

Không đưa mật khẩu database thật vào tài liệu.

---

# 29G. HƯỚNG DẪN OPENALEX

Tạo hướng dẫn thao tác OpenAlex từ đầu.

Bao gồm:

1. Mục đích của OpenAlex trong dự án.
2. Cách tạo tài khoản.
3. Cách lấy API key từ khu vực tài khoản.
4. Biến phải điền:

```env
OPENALEX_API_KEY=
OPENALEX_BASE_URL=https://api.openalex.org
```

5. Cách restart backend sau khi sửa `.env`.
6. Cách kiểm tra API key.
7. Cách xem quota còn lại.
8. Cách kiểm tra response headers liên quan tới quota.
9. Cách xử lý lỗi 401, 403, 429 và timeout.
10. Cách bật Redis cache để giảm số lần gọi API.
11. Cách chạy bằng seed data khi không có key.
12. Cách nhập theo query.
13. Cách nhập OpenAlex snapshot theo batch.
14. Cách dừng và tiếp tục ingestion bằng checkpoint.

Tạo lệnh kiểm tra riêng:

```powershell
python scripts/test_openalex_connection.py
```

Kết quả thành công phải hiển thị:

```text
OpenAlex connection: OK
API key configured: YES
Rate-limit status: AVAILABLE
Sample paper fetched: YES
```

Không được in toàn bộ API key ra terminal.

Chỉ được hiển thị dạng che:

```text
oa_xxxx...abcd
```

---

# 29H. HƯỚNG DẪN LLM PROVIDER

Code không được phụ thuộc cứng vào một nhà cung cấp.

Hỗ trợ:

```text
mock
ollama
openai-compatible
```

Có thể mở rộng thêm provider khác nhưng phải qua interface chung.

Biến môi trường:

```env
LLM_PROVIDER=mock
LLM_MODEL=
LLM_BASE_URL=
LLM_API_KEY=
```

Nếu có provider-specific key, các biến đó phải nằm trong `.env.example`.

Tạo hướng dẫn chuyển đổi:

## Mock mode

```env
LLM_PROVIDER=mock
```

Không cần key.

Dùng để kiểm tra luồng chat, citation và frontend.

## Ollama local

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=<model-name>
```

Giải thích khác biệt khi backend chạy:

* Trực tiếp trên Windows.
* Bên trong Docker container.

## API mode

Giải thích:

* Cách tạo key.
* Cách lưu key.
* Cách test.
* Cách giới hạn chi phí.
* Cách thu hồi key.
* Không đưa key lên GitHub.
* Không đưa key vào frontend.
* Mọi request LLM phải đi qua backend.

Tạo script:

```powershell
python scripts/test_llm_connection.py
```

Kết quả phải nêu:

```text
Provider
Base URL
Model
Connection status
Generation status
Latency
```

Không hiển thị secret.

---

# 29I. HƯỚNG DẪN OLLAMA

Tạo hướng dẫn riêng cho Ollama local:

1. Cài Ollama.
2. Mở Ollama.
3. Tải model.
4. Liệt kê model đã tải.
5. Chạy thử model.
6. Kiểm tra API local.
7. Kết nối backend.
8. Kiểm tra từ Docker container.
9. Đổi model.
10. Xóa model không còn dùng.
11. Giải thích dung lượng model.
12. Cảnh báo máy RAM thấp.

Các lệnh phải dùng placeholder model thay vì bắt buộc một model quá lớn:

```powershell
ollama list
ollama pull <model-name>
ollama run <model-name>
```

Hướng dẫn người dùng chọn model theo RAM:

* Nhóm máy yếu.
* Nhóm máy trung bình.
* Nhóm máy có GPU.

Không khẳng định model nào chạy tốt nếu chưa kiểm tra phần cứng.

Ứng dụng phải có fallback về `mock` khi Ollama chưa chạy.

---

# 29J. HƯỚNG DẪN STRIPE TEST MODE

Tích hợp Stripe phải mặc định ở test hoặc mock mode.

Tài liệu phải chỉ rõ:

1. Tạo tài khoản Stripe.
2. Bật test mode hoặc sandbox.
3. Tạo Product.
4. Tạo recurring Price.
5. Sao chép publishable key.
6. Sao chép secret key.
7. Sao chép Price ID.
8. Điền:

```env
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PRICE_PREMIUM_MONTHLY=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
```

9. Cài Stripe CLI.
10. Đăng nhập Stripe CLI.
11. Forward webhook vào backend local.
12. Sao chép webhook signing secret được CLI trả về.
13. Restart backend.
14. Dùng thẻ test.
15. Kiểm tra database subscription.
16. Kiểm tra sự kiện payment success.
17. Kiểm tra cancel subscription.
18. Kiểm tra payment failed.
19. Chuyển về mock mode.

Lệnh ví dụ:

```powershell
stripe login
stripe listen --forward-to http://localhost:8000/api/v1/subscriptions/webhook
```

Tạo lệnh test webhook:

```powershell
stripe trigger checkout.session.completed
```

Tài liệu phải nói rõ:

* Không sử dụng live key khi đang phát triển.
* Không nhập thông tin thẻ thật.
* Webhook secret khác với Stripe secret key.
* Publishable key có thể dùng ở frontend.
* Secret key chỉ được dùng ở backend.
* Không lưu trạng thái premium chỉ dựa vào redirect thành công.
* Trạng thái subscription phải được xác nhận bằng webhook.

Ứng dụng phải có:

```env
BILLING_MODE=mock
```

để toàn bộ hệ thống vẫn chạy khi người dùng chưa cấu hình Stripe.

---

# 29K. HƯỚNG DẪN EMAIL

Hỗ trợ các mode:

```text
console
smtp
mailpit
```

Mặc định development:

```env
EMAIL_BACKEND=console
```

Khi dùng console mode:

* Verification link được in vào backend log.
* Reset-password link được in vào backend log.
* Không gửi email thật.

Cung cấp lựa chọn Mailpit trong Docker Compose để người dùng xem email development trên trình duyệt.

Tạo hướng dẫn SMTP nhưng không bắt buộc người dùng phải cấu hình ngay.

Có script:

```powershell
python scripts/test_email_connection.py
```

Không log SMTP password.

---

# 29L. HƯỚNG DẪN LƯU FILE

Hỗ trợ:

```text
local
s3-compatible
```

Development mặc định:

```env
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=/app/uploads
```

Production có thể sử dụng object storage tương thích S3.

Tạo interface chung:

```python
class StorageProvider(Protocol):
    async def save(...): ...
    async def delete(...): ...
    async def get_url(...): ...
```

Tài liệu phải giải thích:

* File PDF được lưu ở đâu.
* Metadata được lưu ở đâu.
* Embedding được lưu ở đâu.
* Xóa document sẽ xóa những gì.
* Backup file upload như thế nào.
* Không commit thư mục upload lên GitHub.
* Kiểm tra MIME type và kích thước file.
* Không tin tưởng tên file người dùng tải lên.

Có script upload thử một file và kiểm tra checksum.

---

# 29M. TRANG QUẢN TRỊ KẾT NỐI

Tạo trang:

```text
/admin/integrations
```

Chỉ admin được truy cập.

Trang này chỉ hiển thị trạng thái, không hiển thị secret.

Hiển thị:

| Integration | Configured |     Connected | Last checked | Action |
| ----------- | ---------: | ------------: | ------------ | ------ |
| PostgreSQL  |     Yes/No | Healthy/Error | Time         | Test   |
| Redis       |     Yes/No | Healthy/Error | Time         | Test   |
| OpenAlex    |     Yes/No | Healthy/Error | Time         | Test   |
| LLM         |     Yes/No | Healthy/Error | Time         | Test   |
| Stripe      |     Yes/No | Healthy/Error | Time         | Test   |
| Email       |     Yes/No | Healthy/Error | Time         | Test   |
| Storage     |     Yes/No | Healthy/Error | Time         | Test   |

Nút `Test` gọi backend admin endpoint.

Không cho frontend gửi API key mới qua endpoint này.

Secret phải được cấu hình qua environment variables hoặc secret manager.

API response chỉ được trả:

```json
{
  "name": "openalex",
  "configured": true,
  "status": "healthy",
  "message": "Connection succeeded",
  "checked_at": "..."
}
```

Không trả key, connection string đầy đủ hoặc password.

---

# 29N. HEALTH CHECK VÀ SYSTEM DOCTOR

Tạo script:

```text
scripts/system_doctor.py
```

Và các lệnh:

```powershell
python scripts/system_doctor.py
```

hoặc:

```powershell
make doctor
```

Trên Windows không có `make`, phải có lệnh PowerShell tương đương.

Script phải kiểm tra:

* Python.
* Node.js.
* npm.
* Git.
* Docker.
* Docker Compose.
* File `.env`.
* Database connection.
* pgvector extension.
* Redis connection.
* Backend health endpoint.
* Frontend.
* OpenAlex.
* LLM.
* Stripe configuration.
* Email configuration.
* Storage write permission.
* Worker status.

Kết quả dùng trạng thái:

```text
[OK]
[WARNING]
[ERROR]
[SKIPPED]
```

Ví dụ:

```text
[OK] PostgreSQL connection
[OK] pgvector extension
[OK] Redis connection
[WARNING] OpenAlex key is not configured; seed data will be used
[WARNING] Stripe is in mock mode
[OK] Local storage is writable
[ERROR] Worker is not running
```

Cuối script phải đưa ra hành động cụ thể để sửa từng lỗi.

Không chỉ ghi:

```text
Connection failed.
```

Phải ghi:

```text
Không thể kết nối PostgreSQL tại localhost:5432.
Hãy mở Docker Desktop và chạy:
docker compose up -d postgres
```

---

# 29O. SCRIPT TỰ ĐỘNG HÓA CHO WINDOWS

Tạo các file:

```text
scripts/windows/
├── setup.ps1
├── start.ps1
├── stop.ps1
├── reset_development.ps1
├── run_tests.ps1
├── backup_database.ps1
├── restore_database.ps1
└── doctor.ps1
```

## setup.ps1

Thực hiện:

* Kiểm tra Docker.
* Kiểm tra `.env`.
* Tạo `.env` từ `.env.example` nếu chưa có.
* Khởi động PostgreSQL và Redis.
* Đợi healthcheck.
* Chạy migration.
* Seed dữ liệu.
* In URL truy cập.

Không tự tạo API key giả.

## start.ps1

Khởi động toàn bộ hệ thống.

## stop.ps1

Dừng container nhưng giữ dữ liệu.

## reset_development.ps1

Phải hỏi xác nhận trước khi xóa volume.

Hiển thị cảnh báo lớn rằng dữ liệu local sẽ bị xóa.

## doctor.ps1

Chạy system doctor.

Mỗi script phải có xử lý lỗi và mã thoát phù hợp.

---

# 29P. LỆNH QUẢN TRỊ THỐNG NHẤT

Tạo Makefile và script PowerShell tương ứng cho:

```text
setup
up
down
logs
doctor
migrate
migration
seed
test
lint
format
backup
restore
ingest-sample
train-baseline
evaluate
```

Ví dụ:

```powershell
.\scripts\windows\setup.ps1
.\scripts\windows\start.ps1
.\scripts\windows\doctor.ps1
.\scripts\windows\run_tests.ps1
```

Người dùng không được buộc phải nhớ quá nhiều câu lệnh Docker dài.

---

# 29Q. CHẾ ĐỘ CHẠY KHÔNG CÓ DỊCH VỤ NGOÀI

Toàn bộ dự án phải khởi động được ở chế độ development khi chưa có:

* OpenAlex API key.
* LLM API key.
* Stripe key.
* SMTP.
* S3.

Cấu hình mặc định:

```env
OPENALEX_MODE=seed
LLM_PROVIDER=mock
BILLING_MODE=mock
EMAIL_BACKEND=console
STORAGE_BACKEND=local
```

Trong chế độ này:

* Search sử dụng dữ liệu seed.
* Chatbot kiểm tra được toàn bộ luồng nhưng câu trả lời dùng mock hoặc extractive mode.
* Payment sử dụng mock checkout.
* Email được in vào log.
* PDF lưu local.
* PostgreSQL và Redis vẫn chạy thật.

Giao diện phải hiển thị badge:

```text
Development mode
Mock LLM
Mock billing
Seed data
```

để không làm người dùng hiểu nhầm đang dùng dịch vụ thật.

---

# 29R. QUY TRÌNH BẬT DẦN CÁC TÍCH HỢP

Trong tài liệu, hướng dẫn theo thứ tự:

## Mức 1 — Core local

```text
PostgreSQL
Redis
Backend
Frontend
Seed data
Mock LLM
Mock billing
Console email
Local storage
```

## Mức 2 — Dữ liệu thật

Bật OpenAlex.

## Mức 3 — LLM local

Bật Ollama.

## Mức 4 — LLM API

Bật provider API tùy chọn.

## Mức 5 — Thanh toán thử nghiệm

Bật Stripe test mode.

## Mức 6 — Email development

Bật Mailpit hoặc SMTP thử nghiệm.

## Mức 7 — Production-style storage

Bật S3-compatible storage.

Không yêu cầu người dùng cấu hình tất cả dịch vụ cùng lúc.

Mỗi mức phải có:

* Các biến cần chỉnh.
* Lệnh restart.
* Lệnh test.
* Kết quả mong đợi.
* Cách quay về cấu hình trước.

---

# 29S. HƯỚNG DẪN THAO TÁC ỨNG DỤNG OPENRESEARCH

Tạo file:

```text
docs/16_OPERATION_MANUAL_VI.md
```

Không chỉ hướng dẫn cài đặt; phải hướng dẫn sử dụng chính ứng dụng.

Bao gồm:

## Người dùng thông thường

* Đăng ký.
* Xác minh tài khoản.
* Đăng nhập.
* Tìm paper.
* Sử dụng filter.
* Sắp xếp kết quả.
* Xem paper detail.
* Xem citation graph.
* Lưu paper.
* Tạo collection.
* Thêm tag.
* Ghi chú.
* Upload PDF.
* Theo dõi trạng thái xử lý.
* Chat với PDF.
* Đọc citation.
* Xem recommendation.
* Gửi like/dislike.
* Xem usage.
* Đổi mật khẩu.
* Đăng xuất các thiết bị.

## Premium test

* Mở pricing.
* Chọn plan.
* Thực hiện test checkout.
* Kiểm tra plan được cập nhật.
* Mở customer portal.
* Hủy subscription test.

## Admin

* Đăng nhập admin.
* Xem system health.
* Kiểm tra integrations.
* Xem ingestion jobs.
* Chạy sample ingestion.
* Xem failed jobs.
* Retry job.
* Xem thống kê user.
* Xem thống kê PDF.
* Không chỉnh trực tiếp secret từ admin page.

Mỗi chức năng phải ghi:

* Đường dẫn trang.
* Các nút cần bấm.
* Dữ liệu cần nhập.
* Kết quả mong đợi.
* Lỗi có thể gặp.

---

# 29T. HƯỚNG DẪN GITHUB

Tài liệu GitHub phải hướng dẫn:

1. Tạo repository rỗng.
2. Không chọn tạo README khi local đã có README.
3. Kiểm tra `.gitignore`.
4. Kiểm tra secret trước commit.
5. Commit đầu tiên.
6. Kết nối remote.
7. Push.
8. Xử lý remote có commit trước.
9. Tạo branch chức năng.
10. Tạo pull request.
11. Xem GitHub Actions.
12. Đọc lỗi CI.
13. Thêm repository secrets khi deploy.
14. Không thêm `.env` vào GitHub.

Lệnh:

```powershell
git status
git add .
git commit -m "chore: initialize OpenResearch Graph"
git branch -M main
git remote add origin <repository-url>
git push -u origin main
```

Những lần sau:

```powershell
git status
git add .
git commit -m "feat: describe the completed feature"
git pull origin main --rebase
git push origin main
```

Tạo script kiểm tra secret cơ bản trước khi commit.

Có thể sử dụng pre-commit hook nhưng phải giải thích cách cài.

---

# 29U. HƯỚNG DẪN TRIỂN KHAI

Không khóa hệ thống vào một nền tảng duy nhất.

Tạo tài liệu deployment theo thành phần:

```text
Frontend
Backend
Worker
PostgreSQL
Redis
Object storage
Domain
HTTPS
Environment variables
Webhook
```

Giải thích rõ:

* Frontend không được chứa backend secret.
* Backend và worker phải dùng cùng database.
* Worker phải truy cập được Redis.
* Webhook Stripe cần public HTTPS URL.
* CORS phải đổi từ localhost sang domain thật.
* OAuth callback hoặc reset-password URL phải đổi theo domain.
* Database migration phải chạy trước phiên bản backend mới.
* Không dùng database development làm production.
* Phải backup trước migration quan trọng.

Tạo checklist deployment, không khẳng định deploy thành công khi chưa thực hiện.

---

# 29V. TROUBLESHOOTING THEO TRIỆU CHỨNG

Tạo bảng lỗi dựa trên điều người dùng nhìn thấy.

Ví dụ:

| Triệu chứng                   | Nguyên nhân có thể    | Lệnh kiểm tra               | Cách sửa                      |
| ----------------------------- | --------------------- | --------------------------- | ----------------------------- |
| localhost:3000 không mở       | Frontend chưa chạy    | docker compose ps           | Start frontend                |
| Swagger không mở              | Backend crash         | docker compose logs backend | Sửa env hoặc migration        |
| Login lỗi 500                 | Database chưa migrate | alembic current             | Chạy upgrade head             |
| PDF đứng ở pending            | Worker chưa chạy      | logs worker                 | Start worker                  |
| Chat không trả lời            | LLM chưa kết nối      | test_llm_connection.py      | Chuyển mock hoặc bật provider |
| Search không có dữ liệu       | Chưa seed/ingest      | kiểm tra bảng papers        | Seed hoặc ingestion           |
| Stripe không cập nhật Premium | Webhook chưa chạy     | Stripe CLI logs             | Start stripe listen           |
| Vector search lỗi             | Chưa có pgvector      | kiểm tra extension          | Create extension              |
| Git push rejected             | Remote mới hơn local  | git status/log              | Pull rebase rồi push          |

Hướng dẫn phải ưu tiên chẩn đoán trước khi yêu cầu xóa dữ liệu hoặc cài lại toàn bộ.

---

# 29W. YÊU CẦU KIỂM CHỨNG TÀI LIỆU

Coding agent phải thực sự kiểm tra các lệnh quan trọng khi môi trường cho phép.

Tối thiểu phải kiểm tra:

```text
docker compose config
backend import
database migration
seed script
system doctor
backend tests
frontend lint
frontend type check
frontend build
```

Nếu không thể kiểm tra thao tác cần tài khoản bên ngoài, phải ghi:

```text
Chưa được kiểm tra trực tiếp vì cần tài khoản hoặc API key của người dùng.
```

Không được ghi rằng Stripe, OpenAlex, email hoặc deployment hoạt động hoàn chỉnh nếu chỉ mới viết code mà chưa test với credential thật.

---

# 29X. NGUYÊN TẮC QUẢN LÝ SECRET

Tất cả hướng dẫn phải nhấn mạnh:

* `.env` không được commit.
* `.env.example` chỉ chứa placeholder.
* Secret chỉ được đọc ở backend.
* Frontend chỉ sử dụng biến được phép public.
* Không in secret vào log.
* Không chụp ảnh màn hình có key thật.
* Không gửi key trong README hoặc issue GitHub.
* Khi key bị lộ, phải thu hồi và tạo key mới.
* Không lưu Stripe secret key trong frontend.
* Không lưu JWT secret trong source code.
* Không trả database URL cho client.
* Production nên dùng secret manager của nền tảng triển khai.

Tạo script:

```powershell
python scripts/check_secrets.py
```

để kiểm tra sơ bộ:

* `.env` có bị Git track không.
* Source có chuỗi giống API key không.
* Docker Compose có hard-code secret không.
* Frontend có biến bí mật không phù hợp không.

---

# 29Y. ACCEPTANCE CRITERIA CHO PHẦN HƯỚNG DẪN

Phần hướng dẫn chỉ được coi là hoàn thành khi người mới có thể:

* Cài Docker Desktop.
* Clone repository.
* Tạo `.env`.
* Chạy PostgreSQL và Redis.
* Chạy migration.
* Seed dữ liệu.
* Mở frontend.
* Mở Swagger.
* Đăng ký và đăng nhập.
* Tìm kiếm dữ liệu mẫu.
* Upload PDF.
* Kiểm tra worker.
* Chat ở mock mode.
* Thêm OpenAlex key.
* Kiểm tra OpenAlex.
* Kết nối Ollama hoặc LLM API.
* Chạy Stripe test webhook.
* Xem dữ liệu bằng pgAdmin hoặc DBeaver.
* Chạy system doctor.
* Đọc log khi có lỗi.
* Backup database.
* Push code lên GitHub.

Không được yêu cầu người dùng tự đoán bước còn thiếu.

Mỗi tích hợp phải có:

```text
Purpose
Prerequisites
Account setup
Installation
Environment variables
Startup command
Connection test
Expected result
Common errors
Security notes
How to disable
```

---

# 29Z. KẾT QUẢ CUỐI CÙNG CỦA CODING AGENT

Sau khi hoàn thiện code, coding agent phải trả về một bản tổng kết gồm:

## Phần đã chạy được không cần key

* Database.
* Authentication.
* Seed search.
* PDF upload.
* PDF processing.
* Mock/extractive chat.
* Library.
* Recommendation baseline.
* Analytics.
* Citation graph từ seed data.
* Mock billing.

## Phần người dùng cần tự cấu hình

* OpenAlex.
* Ollama hoặc LLM API.
* Stripe test mode.
* SMTP tùy chọn.
* S3-compatible storage tùy chọn.
* Deployment.

## Danh sách thao tác người dùng cần làm

Phải tạo checklist theo đúng thứ tự, không chỉ liệt kê biến môi trường.

## Danh sách file hướng dẫn

Liệt kê và mô tả từng file trong `docs`.

## Những phần chưa được kiểm tra

Ghi rõ các tích hợp chưa được kiểm chứng bằng credential thật.

Không được nói “dự án hoàn chỉnh 100%” khi vẫn còn bước cấu hình thủ công hoặc tích hợp chưa được kiểm tra.

---

# 30. ACCEPTANCE CRITERIA

Dự án chỉ được coi là hoàn thành khi:

* `docker compose up --build` chạy được.
* Frontend mở được.
* Backend mở được.
* Swagger mở được.
* Database migrations chạy được.
* Có thể đăng ký.
* Có thể đăng nhập.
* Có thể refresh token.
* Có thể tìm kiếm bài báo.
* Có thể xem paper detail.
* Có thể lưu paper.
* Có thể xem analytics.
* Có thể mở citation graph.
* Có thể upload một PDF có text.
* PDF được background worker xử lý.
* Có thể hỏi PDF.
* Câu trả lời có citation theo trang.
* Có thể xem recommendations.
* Có thể gửi feedback recommendation.
* Stripe test hoặc mock billing chạy được.
* Admin route được bảo vệ.
* Test chính chạy được.
* Không có API key thật trong repository.
* README có đầy đủ hướng dẫn.
* `.env.example` đầy đủ.
* Code được chia module rõ ràng.

---

# 31. CÁCH THỰC HIỆN NHIỆM VỤ

Hãy làm theo thứ tự sau:

## Bước 1: Phân tích và thiết kế

* Chốt kiến trúc.
* Chốt database schema.
* Chốt luồng dữ liệu.
* Chốt các interface quan trọng.

## Bước 2: Tạo repository và cấu trúc file

* Tạo toàn bộ thư mục cần thiết.
* Không tạo thư mục thừa.

## Bước 3: Backend nền tảng

* Config.
* Database.
* Models.
* Migrations.
* Authentication.
* Error handling.
* Logging.

## Bước 4: OpenAlex và tìm kiếm

* OpenAlex service.
* Paper repository.
* Search.
* Analytics.
* Graph.

## Bước 5: PDF và RAG

* Upload.
* Background processing.
* Chunk.
* Embedding.
* Retrieval.
* Reranking.
* Chat.
* Citation.

## Bước 6: Recommendation và Deep Learning

* Baselines.
* Hybrid recommender.
* Training code.
* Evaluation.
* Inference.

## Bước 7: Subscription

* Stripe test mode.
* Mock mode.
* Usage limits.

## Bước 8: Frontend

* Auth.
* Search.
* Paper detail.
* Analytics.
* Graph.
* Chat.
* Recommendations.
* Library.
* Pricing.
* Account.
* Admin.

## Bước 9: Testing

* Backend.
* Frontend.
* End-to-end.

## Bước 10: Docker, CI và tài liệu

* Docker Compose.
* GitHub Actions.
* README.
* Setup guide.

## Bước 11: Kiểm tra

Chạy:

```bash
docker compose config
docker compose build
docker compose up
```

Chạy lint, type check và tests.

Sửa lỗi trước khi kết luận.

---

# 32. YÊU CẦU ĐẦU RA

Không chỉ trả lời bằng hướng dẫn hoặc các đoạn code rời rạc.

Hãy thực sự tạo các file trong workspace.

Sau khi hoàn thành:

1. Liệt kê cấu trúc repository cuối cùng.
2. Cho biết những chức năng đã chạy thật.
3. Cho biết những chức năng sử dụng mock khi thiếu API key.
4. Liệt kê các biến môi trường người dùng phải điền.
5. Ghi rõ các giới hạn còn lại.
6. Tạo một file ZIP chứa toàn bộ source code nếu môi trường cho phép.
7. Không đưa `.env`, API key, file model lớn, `node_modules` hoặc `.venv` vào ZIP.
8. Kiểm tra trong source code không có secret.
9. Không tuyên bố đã chạy thành công nếu chưa thực sự chạy.
10. Nếu một phần chưa hoàn chỉnh, phải nói rõ chính xác phần nào.

Nếu lượng code vượt quá giới hạn phản hồi, không được dồn tất cả vào một câu trả lời dài.

Hãy tạo file trực tiếp trong workspace theo từng module, sau đó kiểm tra và cung cấp repository hoàn chỉnh.

---

# 33. QUY TẮC VỀ ĐỘ PHỨC TẠP

Mặc dù dự án có nhiều chức năng, code phải phù hợp với khả năng đọc hiểu của sinh viên đại học.

Với mỗi module phức tạp:

* Có docstring.
* Có tên biến rõ ràng.
* Có chú thích ở đoạn thuật toán quan trọng.
* Có giải thích ngắn trong tài liệu.
* Không dùng design pattern phức tạp khi không cần thiết.
* Không tạo quá nhiều abstraction vô ích.
* Không tạo microservices nếu monolith module hóa đã đủ.
* Ưu tiên modular monolith.
* Background worker có thể chạy riêng nhưng dùng chung code backend.
* Ưu tiên code dễ debug hơn code quá “ảo”.

---

# 34. YÊU CẦU CUỐI CÙNG

Hãy tạo một dự án thực tế, trung thực và có thể trình bày với nhà tuyển dụng.

Dự án không được chỉ là:

* CRUD gắn chatbot.
* Giao diện gọi OpenAlex.
* Chatbot gọi thẳng LLM.
* Notebook machine learning.
* Code sinh tự động không có cấu trúc.
* Demo chỉ chạy với dữ liệu hard-code.

Dự án phải thể hiện được toàn bộ luồng:

```text
Public research data
→ Data ingestion
→ Data validation
→ Database
→ Search and analytics
→ Machine learning
→ Deep learning
→ Recommendation
→ PDF RAG
→ Backend API
→ Frontend product
→ Authentication
→ Subscription
→ Testing
→ Deployment
```

Bắt đầu bằng việc kiểm tra workspace, tạo cấu trúc repository và triển khai code theo từng giai đoạn. Không hỏi lại các câu hỏi không cần thiết; hãy đưa ra giả định hợp lý và ghi rõ giả định trong tài liệu.
