"""Entrypoint: build the Telegram Application, register handlers and jobs."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from telegram.ext import (Application, CallbackQueryHandler, CommandHandler)

from stock_bot.bot import handlers, jobs
from stock_bot.config import settings
from stock_bot.storage.db import init_db


def _setup_logging() -> None:
    level = getattr(logging, settings.log_level, logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    root.addHandler(ch)
    fh = RotatingFileHandler("bot.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    fh.setFormatter(fmt)
    root.addHandler(fh)


def main() -> None:
    _setup_logging()
    settings.validate()
    init_db()

    app = Application.builder().token(settings.telegram_bot_token).build()

    # Commands
    app.add_handler(CommandHandler("start", handlers.cmd_start))
    app.add_handler(CommandHandler("help", handlers.cmd_help))
    app.add_handler(CommandHandler("disclaimer", handlers.cmd_disclaimer))
    app.add_handler(CommandHandler("analyze", handlers.cmd_analyze))
    app.add_handler(CommandHandler("technical", handlers.cmd_technical))
    app.add_handler(CommandHandler("fundamental", handlers.cmd_fundamental))
    app.add_handler(CommandHandler("scan", handlers.cmd_scan))
    app.add_handler(CommandHandler("compare", handlers.cmd_compare))
    app.add_handler(CommandHandler("watchlist", handlers.cmd_watchlist))
    app.add_handler(CommandHandler("alert", handlers.cmd_alert))
    app.add_handler(CommandHandler("digest", handlers.cmd_digest))
    app.add_handler(CommandHandler("settings", handlers.cmd_settings))
    app.add_handler(CommandHandler("sharia", handlers.cmd_sharia))
    app.add_handler(CommandHandler("cheap", handlers.cmd_cheap))
    app.add_handler(CommandHandler("glossary", handlers.cmd_glossary))
    app.add_handler(CommandHandler("portfolio", handlers.cmd_portfolio))
    app.add_handler(CallbackQueryHandler(handlers.on_callback))

    # Jobs
    if app.job_queue is not None:
        app.job_queue.run_repeating(
            jobs.check_alerts, interval=settings.alert_check_interval, first=10)
        # Daily digest ~09:00 Cairo time (07:00 UTC); adjust as needed
        import datetime as dt
        app.job_queue.run_daily(
            jobs.daily_digest, time=dt.time(hour=7, minute=0), name="daily_digest")
    else:
        logging.getLogger(__name__).warning(
            "JobQueue unavailable - alerts/digest disabled. "
            "Install with: pip install 'python-telegram-bot[job-queue]'")

    logging.getLogger(__name__).info("Bot starting (mode=%s)...", settings.mode)
    allowed = ["message", "callback_query"]
    if settings.mode == "webhook":
        if not settings.webhook_url:
            raise RuntimeError("MODE=webhook requires WEBHOOK_URL (e.g. https://app.onrender.com)")
        url_path = settings.telegram_bot_token  # secret path = token
        app.run_webhook(
            listen="0.0.0.0", port=settings.port, url_path=url_path,
            webhook_url=f"{settings.webhook_url.rstrip('/')}/{url_path}",
            allowed_updates=allowed,
        )
    else:
        app.run_polling(allowed_updates=allowed)


if __name__ == "__main__":
    main()
