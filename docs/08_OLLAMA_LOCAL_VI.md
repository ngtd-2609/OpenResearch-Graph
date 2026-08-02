# Ollama local

Ollama là lựa chọn LLM chạy trên máy, không bắt buộc cho core development.

## Cài và kiểm tra

```powershell
ollama --version
ollama list
ollama pull <model-name>
ollama run <model-name>
```

Chọn model theo RAM/VRAM thực tế. Bắt đầu bằng model nhỏ; không tải nhiều model lớn nếu ổ đĩa hạn chế.

## Kiểm tra API

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

Backend trực tiếp trên Windows:

```env
OLLAMA_BASE_URL=http://localhost:11434
```

Backend trong Docker:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

## Bật trong dự án

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=<model-name>
```

```powershell
docker compose up -d --force-recreate backend worker
python scripts/test_llm_connection.py
```

## Chẩn đoán

- Connection refused: Ollama chưa chạy hoặc URL sai.
- Model not found: `ollama pull` đúng tên.
- Out of memory: chọn model nhỏ hơn hoặc giảm context.
- Phản hồi chậm: kiểm tra CPU/GPU, không chạy nhiều request song song.
- Docker không thấy host: dùng `host.docker.internal`, kiểm tra firewall.

## Gỡ model

```powershell
ollama rm <model-name>
```

Chuyển về fallback:

```env
LLM_PROVIDER=mock
```
