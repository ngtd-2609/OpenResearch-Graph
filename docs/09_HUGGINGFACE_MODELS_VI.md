# Hugging Face và mô hình local

OpenResearch Graph dùng mô hình embedding và reranker theo cơ chế tùy chọn. Hệ thống vẫn chạy khi không tải được model nhờ deterministic hash embedding và lexical reranker, nhưng chất lượng tìm kiếm sẽ thấp hơn.

## Mô hình mặc định

```env
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
RERANKER_MODEL_NAME=cross-encoder/ms-marco-MiniLM-L-6-v2
EMBEDDING_DEVICE=cpu
```

`all-MiniLM-L6-v2` tạo vector 384 chiều, khớp với cột `Vector(384)` trong migration. Không được đổi sang model có số chiều khác mà không tạo migration tương ứng.

## Lần chạy đầu

Lần đầu worker tạo embedding, thư viện có thể tải model từ Hugging Face. Hãy xem log:

```powershell
docker compose logs -f worker
```

Nếu mạng bị chặn hoặc tải thất bại, log sẽ báo fallback. Luồng PDF vẫn hoàn tất nhưng semantic retrieval chỉ mang tính development.

## Cache model

Có thể tạo volume cache để tránh tải lại model sau mỗi lần build. Không commit thư mục cache hoặc file trọng số lớn vào GitHub.

```env
HF_HOME=/app/.cache/huggingface
TRANSFORMERS_CACHE=/app/.cache/huggingface
```

## Kiểm tra embedding

```powershell
docker compose exec backend python -c "from app.services.embedding_service import EmbeddingService; s=EmbeddingService(); print(len(s.encode_one('research graph')))"
```

Kết quả mong đợi là `384`. Nếu khác, không chạy ingestion hoặc migration tiếp cho đến khi đồng bộ lại vector dimension.

## Chọn CPU hoặc GPU

- `EMBEDDING_DEVICE=cpu`: ổn định, phù hợp đa số máy sinh viên.
- `EMBEDDING_DEVICE=cuda`: chỉ dùng khi PyTorch nhận GPU và image có CUDA tương thích.
- Không đặt `cuda` chỉ vì máy có GPU; hãy kiểm tra `torch.cuda.is_available()`.

```powershell
docker compose exec backend python -c "import torch; print(torch.cuda.is_available())"
```

## Đổi model an toàn

1. Ghi lại số chiều output của model mới.
2. Tạo migration đổi các cột vector và index HNSW.
3. Xóa hoặc tái tạo embeddings cũ.
4. Chạy evaluation notebook trước khi đưa vào demo.
5. Ghi model name, version và metrics vào model card.

Không so sánh model chỉ dựa vào cảm giác chatbot trả lời hay; hãy đo Recall@K, nDCG@K, latency và RAM.
