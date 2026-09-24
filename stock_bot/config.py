"""Central configuration: env settings, scoring weights, recommendation bands.

All secrets come from environment variables / .env file. Never hardcode tokens.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _get_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment."""

    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    fmp_api_key: str = os.getenv("FMP_API_KEY", "")
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'stock_bot.db'}")
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()

    # Caching TTLs (seconds)
    ohlcv_cache_ttl: int = 60 * 15          # 15 min for daily bars
    fundamentals_cache_ttl: int = 60 * 60 * 24  # 24 h for fundamentals
    quote_cache_ttl: int = 60 * 5           # 5 min for quotes

    # Composite scoring weights per asset type (must sum to 1.0 each)
    weights: dict = field(default_factory=lambda: {
        "stock": {"technical": 0.50, "fundamental": 0.50},
        "etf": {"technical": 0.60, "fundamental": 0.40},
    })

    # Recommendation bands (composite score thresholds)
    band_strong_buy: float = 80.0
    band_buy: float = 65.0
    band_hold: float = 45.0  # below this -> AVOID

    # Minimum fraction of fundamental fields present before score is "confident"
    fundamentals_min_coverage: float = 0.60

    # Risk model
    atr_stop_multiplier: float = 2.0
    max_portfolio_risk_pct: float = 2.0  # risk per trade hint

    # Alert checker cadence (seconds)
    alert_check_interval: int = 900  # 15 minutes

    # /cheap command: default max share price for "cheap & Sharia-compliant" scans
    cheap_max_price_egx: float = _get_float("CHEAP_MAX_PRICE_EGX", 50.0)   # EGP
    cheap_max_price_us: float = _get_float("CHEAP_MAX_PRICE_US", 10.0)     # USD

    # Deployment mode: "polling" (local/VPS) or "webhook" (Render/Koyeb/etc.)
    mode: str = os.getenv("MODE", "polling").lower()
    webhook_url: str = os.getenv("WEBHOOK_URL", "")   # e.g. https://your-app.onrender.com
    port: int = int(os.getenv("PORT", "8080"))        # Render/Koyeb inject PORT

    def validate(self) -> None:
        if not self.telegram_bot_token:
            raise RuntimeError(
                "TELEGRAM_BOT_TOKEN is not set. Copy .env.example to .env and "
                "paste your token from @BotFather."
            )


settings = Settings()

DISCLAIMER_SHORT = (
    "⚠️ <i>Educational analysis, not financial advice. Markets carry risk — "
    "do your own research or consult a licensed advisor.</i>"
)

DISCLAIMER_FULL = (
    "📜 <b>Disclaimer</b>\n\n"
    "This bot provides educational technical and fundamental analysis only. "
    "It is NOT financial, investment, or trading advice, and nothing here is a "
    "recommendation or solicitation to buy or sell any security.\n\n"
    "• Data may be delayed, incomplete, or inaccurate — verify before acting.\n"
    "• Past performance does not guarantee future results.\n"
    "• Trading stocks and ETFs involves substantial risk of loss, including in "
    "emerging markets such as the EGX (currency, liquidity, and political risk).\n"
    "• The developers accept no liability for any financial decisions made using "
    "this bot.\n\n"
    "Always do your own research or consult a licensed financial advisor."
)
