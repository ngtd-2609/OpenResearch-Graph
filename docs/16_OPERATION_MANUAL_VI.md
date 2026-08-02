# HĂ†Â°Ă¡Â»â€ºng dĂ¡ÂºÂ«n sĂ¡Â»Â­ dĂ¡Â»Â¥ng Ă¡Â»Â©ng dĂ¡Â»Â¥ng

## TÄ‚Â i khoĂ¡ÂºÂ£n

1. MĂ¡Â»Å¸ `/register`, nhĂ¡ÂºÂ­p email, username, hĂ¡Â»Â tÄ‚Âªn vÄ‚Â  mĂ¡ÂºÂ­t khĂ¡ÂºÂ©u hai lĂ¡ÂºÂ§n.
2. Ă„ÂĂ„Æ’ng nhĂ¡ÂºÂ­p tĂ¡ÂºÂ¡i `/login`.
3. MĂ¡Â»Å¸ `/account` Ă„â€˜Ă¡Â»Æ’ xem plan, customer portal hoĂ¡ÂºÂ·c thu hĂ¡Â»â€œi mĂ¡Â»Âi phiÄ‚Âªn.
4. Development demo cÄ‚Â³ user/admin seed; Ă„â€˜Ă¡Â»â€¢i password trĂ†Â°Ă¡Â»â€ºc khi public demo.

## TÄ‚Â¬m kiĂ¡ÂºÂ¿m paper

1. MĂ¡Â»Å¸ `/search`.
2. NhĂ¡ÂºÂ­p query Ä‚Â­t nhĂ¡ÂºÂ¥t 2 kÄ‚Â½ tĂ¡Â»Â±.
3. ChĂ¡Â»Ân nĂ„Æ’m bĂ¡ÂºÂ¯t Ă„â€˜Ă¡ÂºÂ§u/kĂ¡ÂºÂ¿t thÄ‚Âºc vÄ‚Â  Open Access nĂ¡ÂºÂ¿u cĂ¡ÂºÂ§n.
4. Submit, xem component ranking vÄ‚Â  pagination.
5. MĂ¡Â»Å¸ paper detail hoĂ¡ÂºÂ·c lĂ†Â°u vÄ‚Â o library.

Search local dÄ‚Â¹ng hybrid keyword/vector/citation/recency/rerank. NĂ¡ÂºÂ¿u OpenAlex API bĂ¡ÂºÂ­t, remote result cÄ‚Â³ thĂ¡Â»Æ’ dÄ‚Â¹ng lÄ‚Â m fallback.

## Analytics vÄ‚Â  citation graph

- `/analytics`: xu hĂ†Â°Ă¡Â»â€ºng theo nĂ„Æ’m, tÄ‚Â¡c giĂ¡ÂºÂ£/topic/source tÄ‚Â¹y dĂ¡Â»Â¯ liĂ¡Â»â€¡u.
- `/graph`: node lÄ‚Â  paper, edge lÄ‚Â  citation; zoom/click Ă„â€˜Ă¡Â»Æ’ xem chi tiĂ¡ÂºÂ¿t.
- Graph giĂ¡Â»â€ºi hĂ¡ÂºÂ¡n node Ă„â€˜Ă¡Â»Æ’ trÄ‚Â¡nh treo trÄ‚Â¬nh duyĂ¡Â»â€¡t; cĂ¡ÂºÂ£nh bÄ‚Â¡o khi kĂ¡ÂºÂ¿t quĂ¡ÂºÂ£ bĂ¡Â»â€¹ cĂ¡ÂºÂ¯t.

## Library

TĂ¡ÂºÂ¡i `/library`, user xem paper Ă„â€˜Ä‚Â£ lĂ†Â°u, sĂ¡Â»Â­a collection, tags/notes vÄ‚Â  xÄ‚Â³a khĂ¡Â»Âi thĂ†Â° viĂ¡Â»â€¡n. MĂ¡Â»â€”i thao tÄ‚Â¡c tĂ¡ÂºÂ¡o interaction phĂ¡Â»Â¥c vĂ¡Â»Â¥ recommendation.

## PDF Chat

1. MĂ¡Â»Å¸ `/chat`.
2. Upload PDF cÄ‚Â³ text vÄ‚Â  trong quota.
3. UI polling trĂ¡ÂºÂ¡ng thÄ‚Â¡i Ă„â€˜Ă¡ÂºÂ¿n completed/failed.
4. Ă„ÂĂ¡ÂºÂ·t cÄ‚Â¢u hĂ¡Â»Âi.
5. MĂ¡Â»Å¸ citation theo page/chunk vÄ‚Â  Ă„â€˜Ă¡Â»â€˜i chiĂ¡ÂºÂ¿u nguĂ¡Â»â€œn.

PDF scan Ă¡ÂºÂ£nh chĂ†Â°a OCR sĂ¡ÂºÂ½ thĂ¡ÂºÂ¥t bĂ¡ÂºÂ¡i cÄ‚Â³ thÄ‚Â´ng bÄ‚Â¡o. KhÄ‚Â´ng dÄ‚Â¹ng chatbot thay cho viĂ¡Â»â€¡c Ă„â€˜Ă¡Â»Âc paper gĂ¡Â»â€˜c.

## Recommendations

`/recommendations` hiĂ¡Â»Æ’n thĂ¡Â»â€¹ explanation vÄ‚Â  component scores. DÄ‚Â¹ng like/dislike/dismiss/save Ă„â€˜Ă¡Â»Æ’ cĂ¡ÂºÂ­p nhĂ¡ÂºÂ­t preference. Seed data chĂ¡Â»â€° cho demo; recommendation tĂ¡Â»â€˜t dĂ¡ÂºÂ§n khi cÄ‚Â³ tĂ†Â°Ă†Â¡ng tÄ‚Â¡c thĂ¡ÂºÂ­t.

## Billing test

- `/pricing`: bĂ¡ÂºÂ¯t Ă„â€˜Ă¡ÂºÂ§u checkout mock/Stripe test.
- `/account`: xem plan, portal vÄ‚Â  chu kĂ¡Â»Â³.
- KhÄ‚Â´ng dÄ‚Â¹ng thĂ¡ÂºÂ» thĂ¡ÂºÂ­t trong test mode.

## Admin

Admin seed: `admin@openresearch.dev / Admin123!` chĂ¡Â»â€° dÄ‚Â¹ng local.

- `/admin`: tĂ¡Â»â€¢ng quan integration.
- `/admin/integrations`: trĂ¡ÂºÂ¡ng thÄ‚Â¡i database, Redis, OpenAlex, LLM, Stripe, email vÄ‚Â  storage.
- Trang admin khÄ‚Â´ng hiĂ¡Â»Æ’n thĂ¡Â»â€¹ secret.

## DĂ¡Â»Â¯ liĂ¡Â»â€¡u vÄ‚Â  quyĂ¡Â»Ân riÄ‚Âªng tĂ†Â°

XÄ‚Â³a document sĂ¡ÂºÂ½ xÄ‚Â³a file/chunks theo flow. KhÄ‚Â´ng upload tÄ‚Â i liĂ¡Â»â€¡u mĂ¡ÂºÂ­t lÄ‚Âªn demo public nĂ¡ÂºÂ¿u chĂ†Â°a cÄ‚Â³ chÄ‚Â­nh sÄ‚Â¡ch retention, encryption vÄ‚Â  access review.

