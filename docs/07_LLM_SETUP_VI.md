# Cấu hình LLM provider

Backend dùng interface chung cho `mock`, `ollama` và `openai-compatible`. Frontend không gọi provider trực tiếp và không được giữ API key.

## Mock mode

```env
LLM_PROVIDER=mock
```

Mock mode kiểm tra upload → retrieval → citation mà không tốn phí. Nó không đại diện chất lượng generation thật.

## Ollama

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=<model-name>
LLM_TIMEOUT_SECONDS=120
LLM_MAX_RETRIES=2
```

Đọc thêm [`08_OLLAMA_LOCAL_VI.md`](08_OLLAMA_LOCAL_VI.md).

## OpenAI-compatible

```env
LLM_PROVIDER=openai-compatible
LLM_BASE_URL=https://provider.example/v1
LLM_MODEL=<model-name>
LLM_API_KEY=<secret>
```

Provider phải hỗ trợ endpoint chat-completions tương thích. Nếu schema khác, tạo adapter riêng thay vì thêm `if` rải rác trong RAG service.

## Kiểm tra kết nối

```powershell
python scripts/test_llm_connection.py
```

Kết quả cần có provider, model, status, latency và một response ngắn; không in API key.

## Cơ chế lỗi

LLM service có timeout, retry/backoff và validate response schema. Endpoint chat trả lỗi 502/503 có kiểm soát thay vì stack trace. Khi provider lỗi, bạn có thể chuyển lại mock mà không sửa code.

## Quản lý chi phí

- Giới hạn context và output tokens.
- Rate limit theo plan.
- Ghi usage/latency nhưng không log nội dung nhạy cảm.
- Tạo budget/alert ở nhà cung cấp.
- Dùng test project/key riêng.

## Bảo mật

- Key chỉ ở backend env/secret manager.
- Không đặt key trong `NEXT_PUBLIC_*`.
- Không cho PDF thay đổi system prompt.
- Không gửi toàn bộ PDF nếu retrieval chỉ cần vài chunks.
- Revoke key ngay nếu bị lộ.
