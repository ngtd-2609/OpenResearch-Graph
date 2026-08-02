# BĂ¡ÂºÂ¯t Ă„â€˜Ă¡ÂºÂ§u tĂ¡Â»Â« Ă„â€˜Ä‚Â¢y

## Checkpoint 1 Ă¢â‚¬â€ KiĂ¡Â»Æ’m tra mÄ‚Â¡y

```powershell
git --version
python --version
node --version
npm --version
docker --version
docker compose version
```

- [ ] CÄ‚Â¡c lĂ¡Â»â€¡nh Ă„â€˜Ă¡Â»Âu trĂ¡ÂºÂ£ vĂ¡Â»Â phiÄ‚Âªn bĂ¡ÂºÂ£n.
- NĂ¡ÂºÂ¿u Docker khÄ‚Â´ng chĂ¡ÂºÂ¡y, mĂ¡Â»Å¸ Docker Desktop vÄ‚Â  chĂ¡Â»Â trĂ¡ÂºÂ¡ng thÄ‚Â¡i Engine running.

## Checkpoint 2 Ă¢â‚¬â€ ChuĂ¡ÂºÂ©n bĂ¡Â»â€¹ source

```powershell
Copy-Item .env.example .env
```

TĂ¡ÂºÂ¡o JWT secret:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

DÄ‚Â¡n kĂ¡ÂºÂ¿t quĂ¡ÂºÂ£ vÄ‚Â o `JWT_SECRET_KEY` trong `.env`.

## Checkpoint 3 Ă¢â‚¬â€ KhĂ¡Â»Å¸i Ă„â€˜Ă¡Â»â„¢ng hĂ¡ÂºÂ¡ tĂ¡ÂºÂ§ng

```powershell
docker compose up -d postgres redis
```

- [ ] `docker compose ps` cho thĂ¡ÂºÂ¥y hai service healthy.

## Checkpoint 4 Ă¢â‚¬â€ Migration

```powershell
docker compose run --rm backend alembic upgrade head
```

## Checkpoint 5 Ă¢â‚¬â€ Seed

```powershell
docker compose run --rm backend python -m app.scripts.seed
```

## Checkpoint 6 Ă¢â‚¬â€ ChĂ¡ÂºÂ¡y hĂ¡Â»â€¡ thĂ¡Â»â€˜ng

```powershell
docker compose up --build
```

## Checkpoint 7 Ă¢â‚¬â€ KiĂ¡Â»Æ’m tra

- [ ] Frontend: http://localhost:3000
- [ ] Backend: http://localhost:8000
- [ ] Swagger: http://localhost:8000/docs

## Checkpoint 8 Ă¢â‚¬â€ ThĂ¡Â»Â­ chĂ¡Â»Â©c nĂ„Æ’ng

- [ ] Login bĂ¡ÂºÂ±ng `user@openresearch.dev / Student123!`
- [ ] Search `deep learning`
- [ ] MĂ¡Â»Å¸ citation graph
- [ ] Upload mĂ¡Â»â„¢t PDF cÄ‚Â³ text
- [ ] ChĂ¡Â»Â worker chuyĂ¡Â»Æ’n trĂ¡ÂºÂ¡ng thÄ‚Â¡i sang completed
- [ ] TĂ¡ÂºÂ¡o chat session vÄ‚Â  hĂ¡Â»Âi PDF
- [ ] Xem citation theo trang
- [ ] Xem recommendation
- [ ] DÄ‚Â¹ng mock premium trong Account

TiĂ¡ÂºÂ¿p tĂ¡Â»Â¥c Ă„â€˜Ă¡Â»Âc `04_ENVIRONMENT_VARIABLES_VI.md`, sau Ă„â€˜Ä‚Â³ bĂ¡ÂºÂ­t tĂ¡Â»Â«ng tÄ‚Â­ch hĂ¡Â»Â£p mĂ¡Â»â„¢t thay vÄ‚Â¬ bĂ¡ÂºÂ­t tĂ¡ÂºÂ¥t cĂ¡ÂºÂ£ cÄ‚Â¹ng lÄ‚Âºc.

