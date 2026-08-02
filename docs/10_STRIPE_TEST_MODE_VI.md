# Stripe test mode

Billing mặc định là `BILLING_MODE=mock`. Chỉ bật Stripe sau khi core system đã chạy.

## Tạo sandbox

1. Tạo Stripe account và bật test mode/sandbox.
2. Tạo Product `OpenResearch Premium`.
3. Tạo recurring monthly Price.
4. Sao chép test secret key và Price ID.

```env
BILLING_MODE=stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_PREMIUM_MONTHLY=price_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

Secret key/webhook secret chỉ ở backend. Publishable key mới được dùng frontend.

## Stripe CLI

```powershell
stripe login
stripe listen --forward-to http://localhost:8000/api/v1/subscriptions/webhook
```

CLI in `whsec_...`; dán vào `.env`, rồi recreate backend:

```powershell
docker compose up -d --force-recreate backend
```

## Kiểm thử

1. Đăng nhập user.
2. Mở `/pricing` và chọn Premium.
3. Dùng thẻ test do Stripe cung cấp, không dùng thẻ thật.
4. Quan sát Stripe CLI và backend logs.
5. Kiểm tra `subscriptions` và `payment_webhook_events`.

Trigger mẫu:

```powershell
stripe trigger checkout.session.completed
stripe trigger invoice.payment_failed
```

Event giả từ CLI có thể thiếu metadata user của checkout do ứng dụng tạo; kiểm thử đầy đủ nên đi qua checkout UI.

## Idempotency và lifecycle

Backend lưu event ID để webhook gửi lặp không nâng cấp nhiều lần. Lifecycle xử lý checkout completed, subscription updated/deleted/paused và invoice failed. Trạng thái premium phải dựa vào webhook đã xác minh signature, không dựa vào query `?checkout=success`.

## Quay về mock

```env
BILLING_MODE=mock
```

Mock upgrade chỉ hoạt động khi billing mode là mock.

## Trước production

- Dùng live product/price riêng.
- Public HTTPS webhook.
- Rotate key và dùng secret manager.
- Kiểm thử retry/out-of-order events.
- Đối soát trạng thái định kỳ với Stripe API.
