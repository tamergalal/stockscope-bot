"""Scheduled jobs: alert checker and daily digest (via JobQueue)."""

from __future__ import annotations

import asyncio
import logging

from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from ..analysis.service import AnalysisService
from ..config import settings
from ..storage import repo
from .messages import rec_emoji

logger = logging.getLogger(__name__)
service = AnalysisService()


async def check_alerts(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Poll active alerts and notify users when triggered."""
    alerts = repo.get_active_alerts()
    for alert in alerts:
        try:
            quote = await asyncio.to_thread(service.data.get_quote, alert.symbol)
            price = quote["price"]
            triggered = False
            note = ""
            if alert.condition == "above" and price >= alert.value:
                triggered, note = True, f"rose above {alert.value}"
            elif alert.condition == "below" and price <= alert.value:
                triggered, note = True, f"fell below {alert.value}"
            elif alert.condition in ("rsi_oversold", "score_buy"):
                report = await service.analyze(alert.symbol)
                if alert.condition == "score_buy" and report.rec.composite >= 65:
                    triggered, note = True, f"score reached {report.rec.composite:.0f} (BUY zone)"
                elif alert.condition == "rsi_oversold":
                    from ..analysis.indicators import rsi as _rsi
                    df = await asyncio.to_thread(service.data.get_ohlcv, alert.symbol, "6mo", "1d")
                    r = float(_rsi(df["Close"]).dropna().iloc[-1])
                    if r <= alert.value:
                        triggered, note = True, f"RSI dropped to {r:.0f} (oversold)"
            if triggered:
                user = repo.get_user_by_pk(alert.user_id)
                if user:
                    await context.bot.send_message(
                        chat_id=user.telegram_id,
                        text=(f"🔔 <b>Alert</b>: <b>{alert.symbol}</b> {note}\n"
                              f"Current price: {price:.2f}"),
                        parse_mode=ParseMode.HTML)
                repo.deactivate_alert(alert.id)
        except Exception as exc:  # noqa: BLE001
            logger.warning("alert %s check failed: %s", alert.id, exc)


async def daily_digest(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Morning digest: quick scan highlights per market for subscribed users."""
    users = repo.get_digest_users()
    if not users:
        return
    lines: list[str] = ["☀️ <b>Daily Market Digest</b>", ""]
    for market, label in (("egx", "🇪🇬 EGX"), ("us", "🇺🇸 US"), ("etf", "📦 ETF")):
        try:
            top = await service.scan(market, top_n=3)
        except Exception as exc:  # noqa: BLE001
            logger.warning("digest scan %s failed: %s", market, exc)
            continue
        if top:
            lines.append(f"<b>{label}</b>")
            for r in top:
                lines.append(f"  {rec_emoji(r.rec.label)} {r.symbol} — {r.rec.composite:.0f}/100 "
                             f"({r.price:.2f} {r.currency})")
            lines.append("")
    lines.append("Use /analyze &lt;SYMBOL&gt; for details. ⚠️ Educational, not advice.")
    text = "\n".join(lines)
    for u in users:
        try:
            await context.bot.send_message(chat_id=u.telegram_id, text=text,
                                           parse_mode=ParseMode.HTML)
        except Exception as exc:  # noqa: BLE001
            logger.warning("digest send to %s failed: %s", u.telegram_id, exc)
