# Cẩm nang thiết lập OpenResearch Graph

Đây là file chỉ mục. Người mới nên làm đúng thứ tự, không bật tất cả dịch vụ bên ngoài cùng lúc.

## Mức 1 — Core local

1. [`01_SYSTEM_REQUIREMENTS_VI.md`](01_SYSTEM_REQUIREMENTS_VI.md): kiểm tra máy.
2. [`02_INSTALLATION_WINDOWS_VI.md`](02_INSTALLATION_WINDOWS_VI.md): cài Git, Docker, VS Code.
3. [`03_INSTALLATION_DOCKER_VI.md`](03_INSTALLATION_DOCKER_VI.md): hiểu container, log và volume.
4. [`04_ENVIRONMENT_VARIABLES_VI.md`](04_ENVIRONMENT_VARIABLES_VI.md): tạo `.env`.
5. [`00_START_HERE_VI.md`](00_START_HERE_VI.md): chạy setup theo checkpoint.
6. [`05_DATABASE_POSTGRESQL_VI.md`](05_DATABASE_POSTGRESQL_VI.md): kiểm tra schema và pgvector.

Core local dùng seed data, mock LLM, mock billing, console email và local storage. Sau bước này bạn phải đăng ký, tìm paper, upload PDF và chat mock được.

## Mức 2 — Bật dữ liệu thật

- [`06_OPENALEX_SETUP_VI.md`](06_OPENALEX_SETUP_VI.md)
- [`data_pipeline/README.md`](../data_pipeline/README.md)

Bắt đầu bằng query nhỏ 100–1.000 records. Chỉ dùng snapshot khi đã hiểu checkpoint, disk, backup và index.

## Mức 3 — Bật LLM

- [`07_LLM_SETUP_VI.md`](07_LLM_SETUP_VI.md)
- [`08_OLLAMA_LOCAL_VI.md`](08_OLLAMA_LOCAL_VI.md)
- [`09_HUGGINGFACE_MODELS_VI.md`](09_HUGGINGFACE_MODELS_VI.md)

Test provider bằng script trước khi đổi UI sang real mode.

## Mức 4 — Billing và email

- [`10_STRIPE_TEST_MODE_VI.md`](10_STRIPE_TEST_MODE_VI.md)
- [`11_EMAIL_SERVICE_VI.md`](11_EMAIL_SERVICE_VI.md)

Chỉ dùng Stripe test key. Subscription phải được xác nhận bằng webhook, không chỉ redirect thành công.

## Mức 5 — Storage và deployment

- [`12_FILE_STORAGE_VI.md`](12_FILE_STORAGE_VI.md)
- [`15_DEPLOYMENT_VI.md`](15_DEPLOYMENT_VI.md)
- [`18_SECURITY_CHECKLIST_VI.md`](18_SECURITY_CHECKLIST_VI.md)

## Khi gặp lỗi

```powershell
python scripts/system_doctor.py
docker compose ps
docker compose logs --tail=200 backend
docker compose logs --tail=200 worker
```

Đọc [`17_TROUBLESHOOTING_VI.md`](17_TROUBLESHOOTING_VI.md) theo triệu chứng. Không dùng `docker compose down -v` như bước sửa lỗi đầu tiên vì lệnh đó xóa dữ liệu development.

## Hướng dẫn sử dụng sản phẩm

Sau khi cài thành công, đọc [`16_OPERATION_MANUAL_VI.md`](16_OPERATION_MANUAL_VI.md) để biết luồng user, premium test và admin.
