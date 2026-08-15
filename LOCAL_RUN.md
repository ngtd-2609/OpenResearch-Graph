## Khởi chạy ứng dụng local (không Docker)

# Chuẩn bị: Mở 2 terminal riêng biệt

### Terminal 1: Backend
```powershell
cd "D:\OpenResearch Graph\openresearch-graph-v2\backend"
$env:PYTHONPATH='D:\OpenResearch Graph\openresearch-graph-v2\backend;D:\OpenResearch Graph\openresearch-graph-v2'
& 'D:\OpenResearch Graph\openresearch-graph-v2\.venv\Scripts\uvicorn.exe' app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2: Frontend
```powershell
cd "D:\OpenResearch Graph\openresearch-graph-v2\frontend"
npm run dev
```

### Tài khoản demo
| Email | Password | Role |
|---|---|---|
| admin@openresearch.dev | Admin123! | Admin |
| user@openresearch.dev | Student123! | User |
| premium@openresearch.dev | Premium123! | Premium |

### URLs
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
