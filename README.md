# Production Telegram Bot (Render + Webhook)

## Quick start (local)
1. `python -m venv .venv && . .venv/bin/activate`
2. `pip install -r requirements.txt`
3. Create `.env` from `.env.example` and fill `BOT_TOKEN`, `BASE_URL` (ngrok URL), `WEBHOOK_SECRET`
4. `python -m app`

## Deploy to Render
- Push this repo to GitHub
- Create **Web Service** from repo
- Set secrets: BOT_TOKEN, BASE_URL, WEBHOOK_SECRET (auto), ENV=prod, SENTRY_DSN?, DATABASE_URL?
- Health check path: `/healthz`

## Admin features
- `/stats` and `/broadcast` for `ADMIN_IDS` (comma-separated).

## Database
- Optional PostgreSQL. Without it, bot works but stats/broadcast won’t.
