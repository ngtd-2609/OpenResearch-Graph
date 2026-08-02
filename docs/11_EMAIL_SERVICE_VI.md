# Email verification và reset password

## Console mode

```env
EMAIL_BACKEND=console
```

Link verify/reset được ghi vào backend log:

```powershell
docker compose logs -f backend
```

Console mode chỉ dùng development; không gửi email thật.

## Mailpit

```powershell
docker compose --profile mail up -d mailpit
```

Mở http://localhost:8025. Cấu hình SMTP trong container theo service `mailpit` nếu compose profile cung cấp.

## SMTP thật

```env
EMAIL_BACKEND=smtp
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
EMAIL_FROM=noreply@your-domain.example
```

Không dùng mật khẩu email cá nhân nếu provider hỗ trợ app password/API SMTP credential.

## Kiểm tra

```powershell
python scripts/test_email_connection.py
```

Không log SMTP password hoặc full reset token trong production. Link reset phải hết hạn, dùng một lần và thu hồi sessions cũ sau khi đổi mật khẩu.

## Deliverability production

Cấu hình SPF, DKIM và DMARC; theo dõi bounce/complaint. Email verification không thay thế authorization.
