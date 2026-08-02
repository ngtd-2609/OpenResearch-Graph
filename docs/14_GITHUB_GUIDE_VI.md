# Đưa dự án lên GitHub

## Tạo repository

Tạo repository rỗng trên GitHub. Nếu local đã có README, không chọn tạo README/gitignore/license trên web để tránh commit lịch sử khác nhau.

## Kiểm tra trước commit

```powershell
git status
python scripts/check_secrets.py
git check-ignore .env
git diff --check
```

Không commit `.env`, uploads, database dump, model weights, `.venv`, `node_modules`, `.next` hoặc cache.

## Commit đầu tiên

```powershell
git init
git add .
git commit -m "chore: initialize OpenResearch Graph"
git branch -M main
git remote add origin <repository-url>
git push -u origin main
```

## Luồng feature branch

```powershell
git switch -c feat/hybrid-search
# sửa code và test
git add .
git commit -m "feat: add PostgreSQL hybrid paper search"
git push -u origin feat/hybrid-search
```

Tạo Pull Request, chờ CI xanh, review diff rồi merge.

## Những lần cập nhật main

```powershell
git switch main
git pull origin main --rebase
git push origin main
```

Nếu push rejected, không dùng `--force` ngay. Kiểm tra remote commits và rebase.

## Conventional commits

- `feat:` tính năng.
- `fix:` sửa lỗi.
- `test:` kiểm thử.
- `docs:` tài liệu.
- `refactor:` đổi cấu trúc không đổi hành vi.
- `chore:` build/config.

## GitHub Actions

Mở tab Actions để xem backend unit, PostgreSQL migration/integration, frontend lint/typecheck/test/build và Docker build. Nhấn vào step đỏ để đọc log từ lỗi đầu tiên, không chỉ dòng cuối.

## Repository secrets

Chỉ thêm secret nếu workflow deploy cần. Pull request từ fork không nên nhận production secrets. Không in secret vào CI log.
