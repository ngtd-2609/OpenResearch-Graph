# Yêu cầu hệ thống

Tài liệu này giúp bạn kiểm tra máy trước khi chạy OpenResearch Graph. Cấu hình dưới đây dành cho môi trường development, không phải thông số production.

## Cấu hình tối thiểu

| Thành phần | Tối thiểu | Khuyến nghị |
|---|---:|---:|
| Hệ điều hành | Windows 10 64-bit | Windows 11 + WSL 2 |
| RAM | 8 GB | 16 GB trở lên |
| Dung lượng trống | 10 GB | 25 GB trở lên |
| CPU | 4 luồng | 8 luồng trở lên |
| GPU | Không bắt buộc | NVIDIA GPU nếu chạy model local lớn |

Máy 8 GB RAM nên dùng `LLM_PROVIDER=mock`, giữ embedding trên CPU và chỉ ingest vài nghìn paper. Không nên chạy đồng thời Ollama model lớn, Docker Desktop, trình duyệt nhiều tab và notebook huấn luyện.

## Phần mềm cần cài

- Git 2.40 trở lên.
- Docker Desktop có Docker Compose v2.
- VS Code và extension Python, Docker, ESLint.
- Python 3.11–3.13 khi muốn chạy backend ngoài Docker.
- Node.js 22 khi muốn chạy frontend ngoài Docker.

Docker là cách chạy mặc định. Python và Node cục bộ chỉ cần cho debug, notebook hoặc phát triển riêng từng lớp.

## Kiểm tra bằng PowerShell

```powershell
git --version
python --version
node --version
npm --version
docker --version
docker compose version
```

Mỗi lệnh phải trả về số phiên bản, không phải lỗi “is not recognized”. Sau khi cài phần mềm mới, đóng và mở lại PowerShell để cập nhật `PATH`.

## Kiểm tra Docker

```powershell
docker info
docker run --rm hello-world
```

Nếu `docker info` báo không kết nối được daemon, hãy mở Docker Desktop và đợi trạng thái Engine Running. Nếu WSL 2 lỗi, chạy `wsl --status` rồi cập nhật WSL trước khi cài lại toàn bộ dự án.

## Cổng mặc định

| Cổng | Dịch vụ |
|---:|---|
| 3000 | Next.js frontend |
| 8000 | FastAPI backend |
| 5432 | PostgreSQL |
| 6379 | Redis |
| 8025 | Mailpit UI nếu bật profile email |

Nếu cổng bị chiếm, dùng `Get-NetTCPConnection -LocalPort 3000` để tìm tiến trình hoặc đổi mapping trong `docker-compose.yml`.

## Kiểm tra cuối

```powershell
python scripts/system_doctor.py
```

Không cần cấu hình OpenAlex, Stripe hay LLM thật để vượt qua phần core. Các tích hợp tùy chọn có thể hiện `WARNING` hoặc `SKIPPED` trong development.
