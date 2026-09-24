"""Inline keyboards for bot interactions."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def analysis_actions(symbol: str) -> InlineKeyboardMarkup:
    """Buttons shown under an analysis report."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 Technical", callback_data=f"tech:{symbol}"),
            InlineKeyboardButton("💰 Fundamentals", callback_data=f"fund:{symbol}"),
        ],
        [
            InlineKeyboardButton("📈 Chart", callback_data=f"chart:{symbol}"),
            InlineKeyboardButton("⭐ Watchlist", callback_data=f"watch:{symbol}"),
        ],
    ])


def market_picker(prefix: str = "scan") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🇪🇬 EGX", callback_data=f"{prefix}:egx"),
        InlineKeyboardButton("🇺🇸 US", callback_data=f"{prefix}:us"),
        InlineKeyboardButton("📦 ETF", callback_data=f"{prefix}:etf"),
    ]])


def cheap_picker() -> InlineKeyboardMarkup:
    """Market picker for /cheap — stocks only (no ETF price threshold)."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🇪🇬 EGX (< 50 EGP)", callback_data="cheap:egx"),
        InlineKeyboardButton("🇺🇸 US (< 10 USD)", callback_data="cheap:us"),
    ]])


def settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🌐 English", callback_data="lang:en"),
            InlineKeyboardButton("🌐 العربية", callback_data="lang:ar"),
        ],
        [
            InlineKeyboardButton("🛡 Conservative", callback_data="risk:conservative"),
            InlineKeyboardButton("⚖️ Balanced", callback_data="risk:balanced"),
            InlineKeyboardButton("🎢 Aggressive", callback_data="risk:aggressive"),
        ],
    ])


def watchlist_quick(symbols: list[str]) -> InlineKeyboardMarkup:
    """One-tap re-analysis buttons for watchlist items (max 5 per row chunk)."""
    rows = []
    for i in range(0, min(len(symbols), 10), 2):
        chunk = symbols[i:i + 2]
        rows.append([InlineKeyboardButton(f"🔍 {s}", callback_data=f"analyze:{s}") for s in chunk])
    return InlineKeyboardMarkup(rows) if rows else None
