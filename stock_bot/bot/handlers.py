"""Telegram command & callback handlers."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes

from ..analysis.charts import render_chart
from ..analysis.service import AnalysisService
from ..config import DISCLAIMER_FULL
from ..data.providers import DataProviderError
from ..data.symbols import detect_market, normalize_symbol
from ..storage import repo
from ..storage.db import init_db
from . import formatting as fmt
from .keyboards import (analysis_actions, market_picker, settings_keyboard,
                        watchlist_quick)
from .messages import rec_emoji, t

logger = logging.getLogger(__name__)
service = AnalysisService()


def _lang(telegram_id: int) -> str:
    user = repo.get_user(telegram_id)
    return user.language if user else "en"


async def _send_long(update: Update, text: str, reply_markup=None) -> None:
    chunks = [text[i:i + 4000] for i in range(0, len(text), 4000)] or [""]
    for i, chunk in enumerate(chunks):
        await update.message.reply_text(
            chunk, parse_mode=ParseMode.HTML,
            reply_markup=reply_markup if i == len(chunks) - 1 else None,
            disable_web_page_preview=True)


async def _chat_action(update: Update, action) -> None:
    try:
        await update.message.chat.send_action(action)
    except Exception:
        pass


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    init_db()
    user = update.effective_user
    repo.get_or_create_user(user.id, user.username)
    await update.message.reply_text(t("welcome", _lang(user.id)),
                                    parse_mode=ParseMode.HTML,
                                    reply_markup=market_picker("scan"))


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(t("help", _lang(update.effective_user.id)),
                                    parse_mode=ParseMode.HTML)


async def cmd_disclaimer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(DISCLAIMER_FULL, parse_mode=ParseMode.HTML)


async def _run_full_analysis(update: Update, raw_symbol: str) -> None:
    user_id = update.effective_user.id
    lang = _lang(user_id)
    repo.get_or_create_user(user_id, update.effective_user.username)
    status = await update.message.reply_text(
        t("analyzing", lang, symbol=raw_symbol.upper()), parse_mode=ParseMode.HTML)
    await _chat_action(update, ChatAction.TYPING)
    try:
        report = await service.analyze(raw_symbol)
    except DataProviderError:
        await status.edit_text(t("error_no_data", lang, symbol=raw_symbol.upper()),
                               parse_mode=ParseMode.HTML)
        return
    except Exception:  # noqa: BLE001
        logger.exception("analysis failed for %s", raw_symbol)
        await status.edit_text(t("error_generic", lang), parse_mode=ParseMode.HTML)
        return
    await status.delete()
    text = (fmt.summary_card(report, lang) + "\n\n" + fmt.technical_section(report, lang)
            + "\n\n" + fmt.fundamental_section(report, lang) + "\n\n"
            + fmt.sharia_section(report, lang) + "\n\n"
            + fmt.recommendation_card(report))
    await _send_long(update, text, reply_markup=analysis_actions(report.symbol))


async def cmd_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /analyze AAPL  |  /analyze COMI.CA")
        return
    await _run_full_analysis(update, context.args[0])


async def cmd_technical(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /technical AAPL")
        return
    try:
        report = await service.analyze(context.args[0])
        await _send_long(update, fmt.technical_section(report, _lang(update.effective_user.id)))
    except DataProviderError:
        await update.message.reply_text(
            t("error_no_data", _lang(update.effective_user.id), symbol=context.args[0]),
            parse_mode=ParseMode.HTML)


async def cmd_fundamental(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /fundamental AAPL")
        return
    try:
        report = await service.analyze(context.args[0])
        await _send_long(update, fmt.fundamental_section(report, _lang(update.effective_user.id)))
    except DataProviderError:
        await update.message.reply_text(
            t("error_no_data", _lang(update.effective_user.id), symbol=context.args[0]),
            parse_mode=ParseMode.HTML)


async def cmd_scan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = _lang(update.effective_user.id)
    market = context.args[0].lower() if context.args else None
    if market not in ("egx", "us", "etf"):
        await update.message.reply_text(t("pick_market", lang),
                                        reply_markup=market_picker("scan"))
        return
    await _do_scan(update, market, lang)


async def _do_scan(update: Update, market: str, lang: str) -> None:
    status = await update.message.reply_text(
        t("analyzing", lang, symbol=market.upper()), parse_mode=ParseMode.HTML)
    await _chat_action(update, ChatAction.TYPING)
    reports = await service.scan(market, top_n=5)
    await status.delete()
    if not reports:
        await update.message.reply_text(t("no_results", lang), parse_mode=ParseMode.HTML)
        return
    lines = [t("scan_title", lang, market=market.upper()), ""]
    for i, r in enumerate(reports, 1):
        lines.append(
            f"{i}. {rec_emoji(r.rec.label)} <b>{r.symbol}</b> — {r.rec.composite:.0f}/100 "
            f"({r.price:.2f} {r.currency}) — {r.rec.label}")
    lines += ["", "Use /analyze &lt;SYMBOL&gt; for the full report."]
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)



async def cmd_compare(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /compare AAPL MSFT")
        return
    lang = _lang(update.effective_user.id)
    reports = []
    for sym in context.args[:2]:
        try:
            reports.append(await service.analyze(sym))
        except DataProviderError:
            await update.message.reply_text(
                t("error_no_data", lang, symbol=sym), parse_mode=ParseMode.HTML)
            return
    a, b = reports
    lines = ["⚖️ <b>Comparison</b>", "",
             f"Technical — {a.symbol}: {a.tech.score:.0f} | {b.symbol}: {b.tech.score:.0f}",
             f"Fundamental — {a.symbol}: {a.fund.score:.0f} | {b.symbol}: {b.fund.score:.0f}",
             f"Composite — {a.symbol}: {a.rec.composite:.0f} | {b.symbol}: {b.rec.composite:.0f}", "",
             f"{a.symbol}: {rec_emoji(a.rec.label)} {a.rec.label}",
             f"{b.symbol}: {rec_emoji(b.rec.label)} {b.rec.label}"]
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


async def cmd_watchlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    lang = _lang(user_id)
    repo.get_or_create_user(user_id, update.effective_user.username)
    sub = context.args[0].lower() if context.args else "list"

    if sub == "add" and len(context.args) > 1:
        sym = normalize_symbol(context.args[1])
        ok = repo.add_to_watchlist(user_id, sym, detect_market(sym))
        key = "watchlist_added" if ok else "watchlist_exists"
        await update.message.reply_text(t(key, lang, symbol=sym), parse_mode=ParseMode.HTML)
    elif sub == "remove" and len(context.args) > 1:
        sym = normalize_symbol(context.args[1])
        ok = repo.remove_from_watchlist(user_id, sym)
        key = "watchlist_removed" if ok else "watchlist_not_found"
        await update.message.reply_text(t(key, lang, symbol=sym), parse_mode=ParseMode.HTML)
    else:
        items = repo.get_watchlist(user_id)
        if not items:
            await update.message.reply_text(t("watchlist_empty", lang),
                                            parse_mode=ParseMode.HTML)
            return
        symbols = [i.symbol for i in items]
        lines = ["⭐ <b>Your watchlist</b>", ""] + [f"• {s}" for s in symbols]
        await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML,
                                        reply_markup=watchlist_quick(symbols))


async def cmd_alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    lang = _lang(user_id)
    repo.get_or_create_user(user_id, update.effective_user.username)
    args = context.args
    if len(args) >= 4 and args[0].lower() == "add":
        symbol = normalize_symbol(args[1])
        condition = args[2].lower()
        try:
            value = float(args[3])
        except ValueError:
            await update.message.reply_text(t("alert_usage", lang))
            return
        if condition not in ("above", "below", "rsi_oversold", "score_buy"):
            await update.message.reply_text(t("alert_usage", lang))
            return
        repo.add_alert(user_id, symbol, condition, value)
        await update.message.reply_text(
            t("alert_added", lang, symbol=symbol, condition=condition, value=value),
            parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(t("alert_usage", lang))


async def cmd_digest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    lang = _lang(user_id)
    repo.get_or_create_user(user_id, update.effective_user.username)
    on = context.args and context.args[0].lower() == "on"
    repo.update_user_prefs(user_id, digest_enabled=on)
    await update.message.reply_text(t("digest_on" if on else "digest_off", lang),
                                    parse_mode=ParseMode.HTML)


async def cmd_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(t("settings_title", _lang(update.effective_user.id)),
                                    parse_mode=ParseMode.HTML,
                                    reply_markup=settings_keyboard())


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all inline-keyboard button presses."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    repo.get_or_create_user(user_id, query.from_user.username)
    lang = _lang(user_id)
    action, _, payload = (query.data or "").partition(":")

    if action == "lang":
        repo.update_user_prefs(user_id, language=payload)
        await query.edit_message_text(t("language_set", payload), parse_mode=ParseMode.HTML)
    elif action == "risk":
        repo.update_user_prefs(user_id, risk_profile=payload)
        await query.edit_message_text(t("risk_set", _lang(user_id), profile=payload),
                                      parse_mode=ParseMode.HTML)
    elif action == "sharia":
        await query.message.reply_text(t("sharia_scanning", lang, market=payload.upper()),
                                       parse_mode=ParseMode.HTML)
        reports = await service.scan_sharia(payload, top_n=5)
        if not reports:
            await query.message.reply_text(t("no_results", lang), parse_mode=ParseMode.HTML)
            return
        lines = [t("sharia_title", lang, market=payload.upper()), ""]
        for i, r in enumerate(reports, 1):
            lines.append(f"{i}. {r.sharia.badge} <b>{r.symbol}</b> — "
                         f"{r.rec.composite:.0f}/100 ({r.price:.2f} {r.currency})")
        lines += ["", t("sharia_footer", lang)]
        await query.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)
    elif action == "scan":
        await query.message.reply_text(t("analyzing", lang, symbol=payload.upper()),
                                       parse_mode=ParseMode.HTML)
        reports = await service.scan(payload, top_n=5)
        if not reports:
            await query.message.reply_text(t("no_results", lang), parse_mode=ParseMode.HTML)
            return
        lines = [t("scan_title", lang, market=payload.upper()), ""]
        for i, r in enumerate(reports, 1):
            lines.append(f"{i}. {rec_emoji(r.rec.label)} <b>{r.symbol}</b> — "
                         f"{r.rec.composite:.0f}/100 ({r.price:.2f} {r.currency})")
        await query.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)
    elif action == "watch":
        sym = normalize_symbol(payload)
        ok = repo.add_to_watchlist(user_id, sym, detect_market(sym))
        key = "watchlist_added" if ok else "watchlist_exists"
        await query.message.reply_text(t(key, lang, symbol=sym), parse_mode=ParseMode.HTML)
    elif action in ("tech", "fund", "analyze", "chart"):
        try:
            report = await service.analyze(payload)
        except DataProviderError:
            await query.message.reply_text(t("error_no_data", lang, symbol=payload),
                                           parse_mode=ParseMode.HTML)
            return
        if action == "tech":
            text = fmt.technical_section(report)
            await query.message.reply_text(text, parse_mode=ParseMode.HTML)
        elif action == "fund":
            await query.message.reply_text(fmt.fundamental_section(report),
                                           parse_mode=ParseMode.HTML)
        elif action == "analyze":
            text = (fmt.summary_card(report, lang) + "\n\n"
                    + fmt.recommendation_card(report))
            await query.message.reply_text(text, parse_mode=ParseMode.HTML)
        elif action == "chart":
            await query.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
            df = await _get_daily(payload)
            png = render_chart(df, report.symbol, report.currency)
            await query.message.reply_photo(
                photo=png, caption=f"📈 {report.symbol} — daily, last ~6 months",
                parse_mode=ParseMode.HTML)


async def _get_daily(symbol: str):
    import asyncio
    return await asyncio.to_thread(
        service.data.get_ohlcv, normalize_symbol(symbol), "1y", "1d")



async def cmd_sharia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Scan only Sharia-compliant candidates in a market."""
    lang = _lang(update.effective_user.id)
    market = context.args[0].lower() if context.args else None
    if market not in ("egx", "us", "etf"):
        await update.message.reply_text(t("sharia_pick", lang),
                                        reply_markup=market_picker("sharia"),
                                        parse_mode=ParseMode.HTML)
        return
    await _do_sharia_scan(update, market, lang)


async def _do_sharia_scan(update: Update, market: str, lang: str) -> None:
    status = await update.message.reply_text(
        t("sharia_scanning", lang, market=market.upper()), parse_mode=ParseMode.HTML)
    await _chat_action(update, ChatAction.TYPING)
    reports = await service.scan_sharia(market, top_n=5)
    await status.delete()
    if not reports:
        await update.message.reply_text(t("no_results", lang), parse_mode=ParseMode.HTML)
        return
    lines = [t("sharia_title", lang, market=market.upper()), ""]
    for i, r in enumerate(reports, 1):
        lines.append(
            f"{i}. {r.sharia.badge} {rec_emoji(r.rec.label)} <b>{r.symbol}</b> — "
            f"{r.rec.composite:.0f}/100 ({r.price:.2f} {r.currency}) — {r.sharia.status}")
    lines += ["", t("sharia_footer", lang), "",
              "Use /analyze &lt;SYMBOL&gt; for the full report."]
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


async def cmd_glossary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Explain a financial term, or list all terms."""
    from .glossary import all_terms_index, explain_term
    lang = _lang(update.effective_user.id)
    if context.args:
        term = " ".join(context.args)
        entry = explain_term(term, lang)
        if entry is None:
            # try case-insensitive / partial match
            from .glossary import GLOSSARY
            match = next((k for k in GLOSSARY if k.lower() == term.lower()), None)
            if match is None:
                match = next((k for k in GLOSSARY if term.lower() in k.lower()), None)
            entry = explain_term(match, lang) if match else None
            term = match or term
        if entry:
            await update.message.reply_text(f"📖 <b>{term}</b>\n{entry}",
                                            parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(t("glossary_unknown", lang, term=term),
                                            parse_mode=ParseMode.HTML)
    else:
        await _send_long(update, all_terms_index(lang))



async def cmd_portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Track holdings: /portfolio add SYMBOL QTY PRICE | remove SYMBOL | list."""
    user_id = update.effective_user.id
    lang = _lang(user_id)
    repo.get_or_create_user(user_id, update.effective_user.username)
    args = context.args or []
    sub = args[0].lower() if args else "list"

    if sub == "add" and len(args) >= 4:
        symbol = normalize_symbol(args[1])
        try:
            qty, price = float(args[2]), float(args[3])
        except ValueError:
            await update.message.reply_text(t("portfolio_usage", lang))
            return
        if qty <= 0 or price <= 0:
            await update.message.reply_text(t("portfolio_usage", lang))
            return
        repo.add_to_portfolio(user_id, symbol, detect_market(symbol), qty, price)
        await update.message.reply_text(
            t("portfolio_added", lang, symbol=symbol, qty=qty, price=price),
            parse_mode=ParseMode.HTML)
    elif sub == "remove" and len(args) >= 2:
        symbol = normalize_symbol(args[1])
        ok = repo.remove_from_portfolio(user_id, symbol)
        key = "portfolio_removed" if ok else "portfolio_not_found"
        await update.message.reply_text(t(key, lang, symbol=symbol),
                                        parse_mode=ParseMode.HTML)
    elif sub == "list":
        await _show_portfolio(update, user_id, lang)
    else:
        await update.message.reply_text(t("portfolio_usage", lang))


async def _show_portfolio(update: Update, user_id: int, lang: str) -> None:
    import asyncio
    items = repo.get_portfolio(user_id)
    if not items:
        await update.message.reply_text(t("portfolio_empty", lang),
                                        parse_mode=ParseMode.HTML)
        return
    status = await update.message.reply_text(
        t("analyzing", lang, symbol="portfolio"), parse_mode=ParseMode.HTML)
    await _chat_action(update, ChatAction.TYPING)

    lines = [t("portfolio_title", lang), ""]
    totals: dict[str, dict[str, float]] = {}  # currency -> {cost, value, pl}
    for item in items:
        currency = "EGP" if item.market == "egx" else "USD"
        try:
            quote = await asyncio.to_thread(service.data.get_quote, item.symbol)
            price = quote["price"]
        except Exception:
            price = None
        cost = item.quantity * item.buy_price
        if price is not None:
            pl_abs, pl_pct = fmt.compute_pnl(item.quantity, item.buy_price, price)
            value = item.quantity * price
            icon = "🟢" if pl_abs >= 0 else "🔴"
            lines.append(
                f"{icon} <b>{item.symbol}</b> ×{item.quantity:g} @ {item.buy_price:g}\n"
                f"   Now {price:.2f} {currency} | P/L {pl_abs:+,.2f} ({pl_pct:+.1f}%)")
            tot = totals.setdefault(currency, {"cost": 0.0, "value": 0.0, "pl": 0.0})
            tot["cost"] += cost
            tot["value"] += value
            tot["pl"] += pl_abs
        else:
            lines.append(f"⚪ <b>{item.symbol}</b> ×{item.quantity:g} @ {item.buy_price:g}"
                         f" — price unavailable")
    for cur, tot in totals.items():
        pct = (tot["pl"] / tot["cost"] * 100) if tot["cost"] else 0.0
        icon = "🟢" if tot["pl"] >= 0 else "🔴"
        lines.append(f"\n{icon} <b>Total ({cur})</b>: value {tot['value']:,.2f} | "
                     f"P/L {tot['pl']:+,.2f} ({pct:+.1f}%)")
    lines += ["", t("disclaimer_footer", lang)]
    await status.delete()
    await _send_long(update, "\n".join(lines))

