# Giới hạn và phạm vi trung thực

OpenResearch Graph là portfolio-grade modular monolith, không phải SaaS production đã được vận hành với người dùng thật.

## Dữ liệu

- Repository không đi kèm hàng triệu paper.
- API ingestion phù hợp query có giới hạn; OpenAlex snapshot mới là đường phù hợp để ingest quy mô toàn bộ dữ liệu.
- Seed data chỉ dùng để kiểm tra luồng, không dùng kết luận khoa học.
- Citation count và metadata phụ thuộc chất lượng nguồn công khai.

## RAG

- PDF ảnh/scanned chưa có OCR mặc định.
- Prompt-injection detection là heuristic, không phải bảo đảm tuyệt đối.
- Citation chỉ cho biết chunk được truy xuất, không chứng minh câu trả lời đúng hoàn toàn.
- Model local/mock có chất lượng thấp hơn provider thật.
- Chưa có malware scanner trong package development.

## Recommendation

- Collaborative signal trong seed data quá nhỏ để đánh giá thực tế.
- Personalized PageRank và co-occurrence có trong ranker, nhưng chất lượng cần dataset tương tác thật.
- Offline metrics không thay thế A/B testing hoặc user study.
- Popularity có thể tạo bias với paper cũ/nhiều citation.

## Billing và security

- Stripe mặc định mock/test; không dùng live key khi chưa kiểm toán webhook lifecycle.
- Frontend development lưu token trong localStorage để dễ học; production nên chuyển refresh token sang secure HttpOnly cookie và có CSRF protection.
- Email console/Mailpit không phải kênh gửi production.
- Chưa có SSO, MFA, malware scanning, DLP hoặc audit log đầy đủ.

## Scale

- Pipeline có batch, checkpoint và dead-letter record nhưng chưa được benchmark với snapshot nhiều terabyte.
- HNSW index tăng tốc vector search nhưng cần tuning theo RAM, write rate và dataset.
- Analytics lớn có thể cần materialized views, warehouse hoặc columnar store.

## Điều không nên tuyên bố

Không mô tả repository là “production-ready”, “đã xử lý hàng triệu paper”, “recommendation chính xác” hoặc “RAG chống hallucination hoàn toàn” nếu chưa có bằng chứng vận hành và evaluation tương ứng.
