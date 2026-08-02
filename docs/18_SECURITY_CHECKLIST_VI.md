# Security checklist

## Trước mỗi commit

- [ ] `.env` bị Git ignore.
- [ ] `python scripts/check_secrets.py` đạt.
- [ ] Không có credential trong screenshot/notebook/test fixture.
- [ ] Không log access/refresh token, password hoặc PDF content nhạy cảm.

## Authentication

- [ ] Argon2 hash, không lưu plain password.
- [ ] Access token sống ngắn.
- [ ] Refresh token hash, rotation và reuse detection.
- [ ] Password reset token dùng một lần và hết hạn.
- [ ] Đổi/reset password thu hồi sessions.
- [ ] Admin authorization được kiểm tra ở backend.

## API

- [ ] Validate Pydantic/Zod.
- [ ] Rate limit theo user/IP/plan.
- [ ] CORS chỉ domain cần thiết.
- [ ] Không trả stack trace production.
- [ ] Resource query luôn scope theo owner.
- [ ] Pagination và upload limits có giới hạn cứng.

## PDF/RAG

- [ ] Kiểm tra MIME, size, checksum và random stored name.
- [ ] PDF được xem là untrusted data.
- [ ] Không thực thi code/tool instruction từ PDF.
- [ ] Context có budget.
- [ ] Citation cho phép user kiểm tra nguồn.
- [ ] Production có malware scanning và retention.

## Billing

- [ ] Stripe secret chỉ backend.
- [ ] Webhook verify signature.
- [ ] Event ID idempotency.
- [ ] Premium thay đổi theo webhook, không theo redirect.
- [ ] Test out-of-order/retry/payment failed/cancel.

## Production

- [ ] `DEBUG=false`.
- [ ] JWT/database/API secrets được rotate và lưu secret manager.
- [ ] HTTPS, HSTS, CSP và trusted proxy đúng.
- [ ] Refresh token dùng secure HttpOnly cookie + CSRF strategy.
- [ ] Backup đã thử restore.
- [ ] Monitoring, alert và audit log.
- [ ] Demo accounts bị tắt hoặc đổi credential.

Security checklist không thay thế penetration test hoặc code review độc lập.
