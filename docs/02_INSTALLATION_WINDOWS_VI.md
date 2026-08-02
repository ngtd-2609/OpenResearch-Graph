# Cài đặt trên Windows 10/11

## 1. Cài Git

Tải Git for Windows từ trang chính thức, giữ tùy chọn thêm Git vào `PATH`, sau đó mở PowerShell mới:

```powershell
git --version
git config --global user.name "Tên của bạn"
git config --global user.email "email-cua-ban@example.com"
```

Email nên trùng email GitHub nếu bạn muốn commit hiện đúng profile.

## 2. Cài Docker Desktop và WSL 2

Mở PowerShell bằng quyền Administrator:

```powershell
wsl --install
wsl --update
wsl --status
```

Khởi động lại máy nếu Windows yêu cầu. Cài Docker Desktop, chọn WSL 2 backend, mở ứng dụng và đợi Docker Engine hoạt động.

```powershell
docker --version
docker compose version
docker run --rm hello-world
```

## 3. Cài công cụ phát triển tùy chọn

Cài Node.js 22 và Python 3.11–3.13 khi muốn chạy ngoài Docker:

```powershell
node --version
npm --version
python --version
```

Cài VS Code cùng extension Python, Docker, ESLint và GitLens nếu cần.

## 4. Giải nén hoặc clone repository

```powershell
git clone <repository-url>
cd openresearch-graph
Copy-Item .env.example .env
```

Nếu nhận file ZIP, giải nén vào đường dẫn không quá dài và tránh thư mục có quyền hạn chế.

## 5. Chạy setup

```powershell
.\scripts\windows\setup.ps1
.\scripts\windows\doctor.ps1
.\scripts\windows\start.ps1
```

Nếu PowerShell chặn script:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Không dùng `Unrestricted` nếu không cần.

## 6. Kiểm tra URL

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Swagger: http://localhost:8000/docs

## Chạy không Docker

Chỉ làm khi bạn cần debug từng lớp. PostgreSQL và Redis vẫn có thể chạy bằng Docker.

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend ở PowerShell khác:

```powershell
cd frontend
npm install
npm run dev
```

Worker ở PowerShell thứ ba:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
celery -A app.workers.celery_app worker --loglevel=INFO --pool=solo
```

Trên Windows, `--pool=solo` dễ chạy hơn prefork trong development.
