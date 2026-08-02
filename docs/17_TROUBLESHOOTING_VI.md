# Troubleshooting theo triệu chứng

Chạy trước:

```powershell
python scripts/system_doctor.py
docker compose ps
docker compose logs --tail=200 backend
docker compose logs --tail=200 worker
```

| Triệu chứng | Nguyên nhân thường gặp | Kiểm tra | Cách sửa |
|---|---|---|---|
| `localhost:3000` không mở | frontend dừng/build lỗi | `docker compose logs frontend` | rebuild frontend |
| Swagger không mở | backend import/env/migration lỗi | log backend | sửa lỗi đầu tiên, chạy migration |
| Login 500 | DB chưa migrate hoặc connection sai | `alembic current` | `alembic upgrade head` |
| Login 401 | sai credential/inactive | seed log, user row | nhập đúng hoặc reset seed |
| PDF pending | worker/Redis dừng | `ps`, worker logs | start Redis/worker |
| PDF failed | scanned PDF/model/storage | document status + worker log | dùng PDF text hoặc bật OCR extension |
| Chat 502 | LLM provider lỗi | test LLM script | sửa URL/model/key hoặc mock |
| Chat không có nguồn | retrieval không tìm chunk | kiểm tra chunks/embedding | process lại document |
| Search trống | chưa seed/ingest | `SELECT count(*) FROM papers` | seed hoặc ingest |
| Vector error | extension/dimension/index | query pg_extension/schema | migration/re-embed đúng dimension |
| Stripe không premium | webhook/signature/metadata | Stripe CLI + events table | chạy listen, đúng `whsec` |
| OpenAlex 429 | rate limit | backend log/header | giảm tốc, retry checkpoint |
| Git push rejected | remote mới hơn | `git log --oneline --all` | pull rebase rồi push |

## Port bị chiếm

```powershell
Get-NetTCPConnection -LocalPort 3000
Get-Process -Id <PID>
```

Dừng tiến trình hoặc đổi port mapping; không kill process hệ thống không rõ chức năng.

## Migration lỗi

```powershell
docker compose exec backend alembic current
docker compose exec backend alembic history
docker compose logs postgres
```

Không xóa volume trước khi backup. Với development có thể reset chỉ khi chấp nhận mất toàn bộ dữ liệu.

## npm lỗi

```powershell
cd frontend
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
npm cache verify
npm install
npm run typecheck
```

Không xóa lockfile để “sửa nhanh” nếu team cần reproducible build; xác định dependency xung đột trước.

## Khi cần báo lỗi

Gửi phiên bản OS/Docker, command đã chạy, log đã che secret, commit SHA và bước tái hiện. Không gửi `.env` nguyên file.
