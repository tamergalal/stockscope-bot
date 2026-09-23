---
title: StockScope Bot
emoji: 📈
sdk: docker
app_port: 7860
pinned: false
---

# 📈 StockScope Bot — EGX + US Stocks + ETF Analysis Telegram Bot

A production-ready Telegram bot that performs **technical + fundamental analysis**
and generates **BUY / HOLD / AVOID recommendations** with complete trade plans for:

- 🇪🇬 **EGX** stocks (Egyptian Exchange, `.CA` tickers — COMI.CA, ETEL.CA, SWDY.CA…)
- 🇺🇸 **US stocks** (NYSE/NASDAQ — AAPL, MSFT, NVDA…)
- 📦 **ETFs** (SPY, QQQ, SCHD, GLD, TLT…)

## ✨ Features

- `/analyze SYMBOL` — full report: summary card, technical section, fundamental
  section, recommendation with **entry zone, ATR stop-loss, T1/T2 targets, R:R**
- `/scan egx|us|etf` — top BUY candidates ranked by composite score
- `/compare A B` — side-by-side scoring
- `/watchlist add/remove/list` — personal watchlist with one-tap re-analysis
- `/alert add SYMBOL above|below PRICE` — price/RSI/score alerts (checked every 15 min)
- `/digest on` — morning digest with market highlights
- `/settings` — English/العربية + risk profile
- `/sharia egx|us|etf` — ☪️ scan **Sharia-compliant** candidates only
  (AAOIFI-inspired: no prohibited activities + debt & cash < 33% of market cap;
  Islamic ETFs HLAL, SPUS, UMMA, SPSK recognized automatically)
- `/glossary RSI` — 📖 plain-language explanation of any term (EN/العربية);
  every report also auto-includes a **"Terms explained"** block for the
  abbreviations it used
- Candlestick **charts** with MA20/50, Bollinger Bands, volume & RSI
- Bilingual 🇬🇧/🇪🇬 interface

## 🧠 Analysis engine

**Technical (0–100):** trend (SMA 20/50/200, golden/death cross, ADX, Ichimoku),
momentum (RSI + divergence, MACD, Stochastic), volatility (Bollinger %B, squeeze,
ATR), volume (OBV, spikes), price action (8+ candlestick patterns, support/resistance
clusters, breakouts, Fibonacci levels), multi-timeframe consensus (daily + weekly).

**Fundamental (0–100):** US stocks scored vs sector benchmarks (P/E, PEG-proxy,
ROE, margins, D/E, growth, FCF, dividends); **EGX stocks scored against EGX
benchmarks** with graceful handling of sparse free data (low-confidence flag);
**ETFs** scored on expense ratio, AUM, yield, returns, max drawdown.

**Composite** = weighted mix (stocks 50/50, ETFs 60/40 technical tilt) →
`STRONG BUY ≥ 80 · BUY 65–79 · HOLD/WATCH 45–64 · AVOID < 45`

## 🚀 Quick start

```bash
# 1. Get a bot token from @BotFather on Telegram
# 2. Install deps
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# edit .env -> paste TELEGRAM_BOT_TOKEN (FMP_API_KEY optional, free at
# site.financialmodelingprep.com for richer US fundamentals)

# 4. Run
python main.py
```

Then in Telegram: `/start` → `/analyze AAPL` → `/analyze COMI.CA`

## ☁️ Free online deployment (run 24/7 without your PC)

**Why not Vercel?** Vercel runs *serverless functions* that spin up per request and
die — this bot needs a **persistent process** (polling) or a stable HTTPS endpoint
(webhook) plus background jobs, so use one of these instead:

### Option A — Oracle Cloud "Always Free" VM (recommended, true 24/7)
Free forever: 4 ARM CPUs + 24 GB RAM — plenty for this bot.
1. Create account at cloud.oracle.com → launch an **Ubuntu 22.04 ARM (Ampere) VM**
2. Upload the project (git clone or `scp`), then:
   ```bash
   sudo apt update && sudo apt install -y docker.io
   cd stock_bot_project
   # put your .env (with TELEGRAM_BOT_TOKEN) here, MODE stays "polling"
   sudo docker build -t stock-bot .
   sudo docker run -d --name stock-bot --restart unless-stopped --env-file .env stock-bot
   ```
✅ Alerts + daily digest run 24/7 · SQLite persists in a Docker volume.

### Option B — Render free tier (webhook mode, no server admin)
1. Push this repo to GitHub
2. Render.com → **New > Web Service** → connect the repo
   (`render.yaml` blueprint is included and pre-fills everything)
3. Set env vars in the dashboard: `TELEGRAM_BOT_TOKEN`, `FMP_API_KEY`,
   `MODE=webhook`
4. After first deploy, copy your URL (e.g. `https://stockscope-bot.onrender.com`)
   into the `WEBHOOK_URL` env var and redeploy — the bot registers the webhook
   with Telegram automatically.

⚠️ Free-tier caveats: the service **sleeps after ~15 min idle** (Telegram messages
wake it — first reply takes ~30 s), and the SQLite file **resets on redeploys**
(watchlists/alerts are lost — use a free Neon/Render Postgres via `DATABASE_URL`
to persist).

## 🐳 Docker (VPS deployment)

```bash
docker build -t stock-bot .
docker run -d --name stock-bot --restart unless-stopped --env-file .env stock-bot
# or: docker compose up -d
```

## 🧪 Tests

```bash
python -m pytest tests -q   # 34 tests: indicators, scoring, market detection, i18n
```

## 📁 Architecture

```
stock_bot/
├── main.py                # entrypoint (polling + JobQueue)
├── stock_bot/
│   ├── config.py          # env settings, weights, bands, disclaimers
│   ├── data/              # providers (yfinance + optional FMP), symbol universe
│   ├── analysis/          # indicators, technical, fundamental, scoring, charts, service
│   ├── bot/               # handlers, keyboards, messages (EN/AR), jobs, formatting
│   └── storage/           # SQLAlchemy models + repository (SQLite default)
└── tests/                 # pytest suite
```

## ⚙️ Configuration

| Env var | Required | Purpose |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | ✅ | Token from @BotFather |
| `FMP_API_KEY` | optional | Enriches US fundamentals (free tier OK) |
| `DATABASE_URL` | optional | Default: local SQLite file |
| `LOG_LEVEL` | optional | INFO/DEBUG/… |

## ⚠️ Disclaimer

This bot provides **educational analysis, not financial advice**. Market data may
be delayed or inaccurate. Trading involves substantial risk of loss — always do
your own research or consult a licensed advisor.

## Notes & limitations

- EGX fundamentals via free APIs are sparse for many tickers; the bot flags
  low-confidence scores instead of fabricating numbers.
- yfinance is subject to Yahoo rate limits; the bot caches aggressively
  (15 min OHLCV / 24 h fundamentals) to stay friendly.
- To add symbols: edit `stock_bot/data/symbols.py` (EGX/US/ETF dicts).
