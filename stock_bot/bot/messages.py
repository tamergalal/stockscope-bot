"""Message catalogs (English + Arabic) and formatting helpers."""

from __future__ import annotations

CATALOG: dict[str, dict[str, str]] = {
    "en": {
        "welcome": (
            "👋 Welcome to <b>StockScope Bot</b>!\n\n"
            "I analyze <b>EGX</b> stocks, <b>US stocks</b>, and <b>ETFs</b> with combined "
            "technical + fundamental analysis.\n\n"
            "Try:\n"
            "• /analyze AAPL — full report\n"
            "• /analyze COMI.CA — Egyptian stock\n"
            "• /scan etf — top ETF picks\n"
            "• /help — all commands"
        ),
        "help": (
            "<b>Commands</b>\n"
            "/analyze &lt;SYMBOL&gt; — full technical + fundamental report\n"
            "/technical &lt;SYMBOL&gt; — technical section only\n"
            "/fundamental &lt;SYMBOL&gt; — fundamentals only\n"
            "/scan &lt;egx|us|etf&gt; — top BUY candidates\n"
            "/compare &lt;SYM1&gt; &lt;SYM2&gt; — side-by-side scores\n"
            "/watchlist add|remove|list — manage your watchlist\n"
            "/alert add &lt;SYM&gt; &lt;above|below&gt; &lt;price&gt; — price alert\n"
            "/digest on|off — daily market digest\n"
            "/settings — language & risk profile\n"
            "/sharia &lt;egx|us|etf&gt; — ☪️ Sharia-compliant picks\n"
            "/cheap &lt;egx|us&gt; [max_price] — 💸☪️ cheap Sharia-compliant stocks\n"
            "/glossary &lt;term&gt; — 📖 explain any term (RSI, P/E, …)\n"
            "/portfolio add|remove|list — 💼 track your holdings P/L\n"
            "/disclaimer — legal disclaimer"
        ),
        "analyzing": "🔎 Analyzing <b>{symbol}</b>… fetching market data, please wait.",
        "error_no_data": "❌ Couldn't fetch data for <b>{symbol}</b>. Check the symbol or try again later.",
        "error_generic": "⚠️ Something went wrong. Please try again.",
        "market_egx": "🇪🇬 EGX",
        "market_us": "🇺🇸 US",
        "market_etf": "📦 ETF",
        "watchlist_empty": "Your watchlist is empty. Add with /watchlist add AAPL",
        "watchlist_added": "✅ Added <b>{symbol}</b> to your watchlist.",
        "watchlist_exists": "ℹ️ <b>{symbol}</b> is already in your watchlist.",
        "watchlist_removed": "🗑 Removed <b>{symbol}</b> from your watchlist.",
        "watchlist_not_found": "ℹ️ <b>{symbol}</b> not found in your watchlist.",
        "alert_added": "🔔 Alert set: <b>{symbol}</b> {condition} {value}",
        "alert_usage": "Usage: /alert add AAPL above 200",
        "digest_on": "📬 Daily digest enabled (delivered each morning).",
        "digest_off": "📭 Daily digest disabled.",
        "settings_title": "⚙️ <b>Settings</b>",
        "language_set": "🌐 Language set to English.",
        "risk_set": "🎯 Risk profile set to <b>{profile}</b>.",
        "pick_market": "Pick a market to scan:",
        "scan_title": "🔥 Top BUY candidates — {market}",
        "no_results": "No qualifying candidates right now.",
        "disclaimer_footer": "⚠️ <i>Educational analysis, not financial advice.</i>",
        "sharia_pick": "☪️ Pick a market to scan for <b>Sharia-compliant</b> candidates:",
        "sharia_scanning": "☪️ Screening <b>{market}</b> for Sharia-compliant candidates…",
        "sharia_title": "☪️ Top Sharia-compliant candidates — {market}",
        "sharia_footer": ("<i>Screening: no prohibited activities + debt & cash < 33% of market cap "
                          "(AAOIFI-inspired). Verify with Zoya/Islamicly or your scholar.</i>"),
        "glossary_unknown": "❓ Unknown term: <b>{term}</b>. Use /glossary to list all terms.",
        "cheap_pick": ("💸 Find <b>Sharia-compliant</b> stocks under <b>{egx:g} EGP</b> "
                       "(EGX) or <b>{usd:g} USD</b> (US) — pick a market:"),
        "cheap_scanning": ("💸 Scanning <b>{market}</b> for Sharia-compliant stocks "
                           "under <b>{price:g} {currency}</b>…"),
        "cheap_title": "💸☪️ Cheap &amp; Sharia-compliant — {market} (under {price:g} {currency})",
        "cheap_empty": ("No Sharia-compliant {market} stocks under {price:g} {currency} "
                        "right now. Try /cheap {market_lower} with a higher price."),
        "cheap_usage": "Usage: /cheap egx  |  /cheap us  |  /cheap egx 30  |  /cheap us 5",
        "portfolio_usage": "Usage: /portfolio add AAPL 10 150.5  |  /portfolio remove AAPL  |  /portfolio list",
        "portfolio_added": "💼 Added <b>{qty:g} × {symbol}</b> @ {price:g} to your portfolio.",
        "portfolio_removed": "🗑 Removed <b>{symbol}</b> from your portfolio.",
        "portfolio_not_found": "ℹ️ <b>{symbol}</b> not found in your portfolio.",
        "portfolio_empty": "💼 Your portfolio is empty. Add with /portfolio add AAPL 10 150.5",
        "portfolio_title": "💼 <b>Your Portfolio (live P/L)</b>",
    },
    "ar": {
        "welcome": (
            "👋 أهلاً بك في <b>StockScope Bot</b>!\n\n"
            "أحلل أسهم <b>البورصة المصرية</b> و<b>الأسهم الأمريكية</b> و<b>صناديق المؤشرات</b> "
            "بالتحليل الفني والمالي معًا.\n\n"
            "جرّب:\n"
            "• /analyze AAPL — تقرير كامل\n"
            "• /analyze COMI.CA — سهم مصري\n"
            "• /scan etf — أفضل الصناديق\n"
            "• /help — كل الأوامر"
        ),
        "help": (
            "<b>الأوامر</b>\n"
            "/analyze &lt;SYMBOL&gt; — تقرير فني + مالي كامل\n"
            "/technical &lt;SYMBOL&gt; — التحليل الفني فقط\n"
            "/fundamental &lt;SYMBOL&gt; — التحليل المالي فقط\n"
            "/scan &lt;egx|us|etf&gt; — أفضل فرص الشراء\n"
            "/compare &lt;SYM1&gt; &lt;SYM2&gt; — مقارنة بين سهمين\n"
            "/watchlist add|remove|list — إدارة قائمة المتابعة\n"
            "/alert add &lt;SYM&gt; &lt;above|below&gt; &lt;price&gt; — تنبيه سعري\n"
            "/digest on|off — ملخص يومي\n"
            "/settings — اللغة والمخاطرة\n"
            "/sharia &lt;egx|us|etf&gt; — ☪️ فرص متوافقة مع الشريعة\n"
            "/cheap &lt;egx|us&gt; [max_price] — 💸☪️ أسهم رخيصة متوافقة شرعًا\n"
            "/glossary &lt;term&gt; — 📖 شرح أي مصطلح (RSI, P/E, …)\n"
            "/portfolio add|remove|list — 💼 متابعة أرباح/خسائر محفظتك\n"
            "/disclaimer — إخلاء المسؤولية"
        ),
        "analyzing": "🔎 جاري تحليل <b>{symbol}</b>… يرجى الانتظار.",
        "error_no_data": "❌ تعذّر جلب بيانات <b>{symbol}</b>. تحقق من الرمز وحاول لاحقًا.",
        "error_generic": "⚠️ حدث خطأ ما. حاول مرة أخرى.",
        "market_egx": "🇪🇬 البورصة المصرية",
        "market_us": "🇺🇸 الأمريكية",
        "market_etf": "📦 صناديق",
        "watchlist_empty": "قائمة المتابعة فارغة. أضف بـ /watchlist add AAPL",
        "watchlist_added": "✅ تمت إضافة <b>{symbol}</b> لقائمتك.",
        "watchlist_exists": "ℹ️ <b>{symbol}</b> موجودة بالفعل.",
        "watchlist_removed": "🗑 تم حذف <b>{symbol}</b>.",
        "watchlist_not_found": "ℹ️ <b>{symbol}</b> غير موجودة في قائمتك.",
        "alert_added": "🔔 تم ضبط تنبيه: <b>{symbol}</b> {condition} {value}",
        "alert_usage": "الاستخدام: /alert add AAPL above 200",
        "digest_on": "📬 تم تفعيل الملخص اليومي.",
        "digest_off": "📭 تم إيقاف الملخص اليومي.",
        "settings_title": "⚙️ <b>الإعدادات</b>",
        "language_set": "🌐 تم ضبط اللغة على العربية.",
        "risk_set": "🎯 تم ضبط المخاطرة على <b>{profile}</b>.",
        "pick_market": "اختر السوق للمسح:",
        "scan_title": "🔥 أفضل فرص الشراء — {market}",
        "no_results": "لا توجد فرص مؤهلة الآن.",
        "disclaimer_footer": "⚠️ <i>تحليل تعليمي وليس نصيحة استثمارية.</i>",
        "sharia_pick": "☪️ اختر السوق للبحث عن فرص <b>متوافقة مع الشريعة</b>:",
        "sharia_scanning": "☪️ جاري فحص <b>{market}</b> بحثًا عن فرص متوافقة شرعًا…",
        "sharia_title": "☪️ أفضل الفرص المتوافقة مع الشريعة — {market}",
        "sharia_footer": ("<i>الفحص: استبعاد الأنشطة المحرمة + الدين والنقدية أقل من 33% من "
                          "القيمة السوقية (معايير AAOIFI). تحقق عبر Zoya/Islamicly أو عالمك.</i>"),
        "glossary_unknown": "❓ مصطلح غير معروف: <b>{term}</b>. استخدم /glossary لعرض الكل.",
        "cheap_pick": ("💸 أسهم <b>متوافقة مع الشريعة</b> بسعر أقل من <b>{egx:g} جنيه</b> "
                       "(مصر) أو <b>{usd:g} دولار</b> (أمريكا) — اختر السوق:"),
        "cheap_scanning": ("💸 جاري البحث في <b>{market}</b> عن أسهم متوافقة شرعًا "
                           "بسعر أقل من <b>{price:g} {currency}</b>…"),
        "cheap_title": "💸☪️ أسهم رخيصة ومتوافقة شرعًا — {market} (أقل من {price:g} {currency})",
        "cheap_empty": ("لا توجد أسهم متوافقة شرعًا في {market} بسعر أقل من {price:g} "
                        "{currency} حاليًا. جرّب /cheap {market_lower} بسعر أعلى."),
        "cheap_usage": "الاستخدام: /cheap egx  |  /cheap us  |  /cheap egx 30  |  /cheap us 5",
        "portfolio_usage": "الاستخدام: /portfolio add AAPL 10 150.5  |  /portfolio remove AAPL  |  /portfolio list",
        "portfolio_added": "💼 تمت إضافة <b>{qty:g} × {symbol}</b> بسعر {price:g} لمحفظتك.",
        "portfolio_removed": "🗑 تم حذف <b>{symbol}</b> من محفظتك.",
        "portfolio_not_found": "ℹ️ <b>{symbol}</b> غير موجودة في محفظتك.",
        "portfolio_empty": "💼 محفظتك فارغة. أضف بـ /portfolio add AAPL 10 150.5",
        "portfolio_title": "💼 <b>محفظتك (الربح/الخسارة المباشرة)</b>",
    },
}

DEFAULT_LANG = "en"


def t(key: str, lang: str = DEFAULT_LANG, **kwargs) -> str:
    """Translate a message key, with optional format kwargs."""
    text = CATALOG.get(lang, CATALOG[DEFAULT_LANG]).get(key)
    if text is None:
        text = CATALOG[DEFAULT_LANG].get(key, key)
    return text.format(**kwargs) if kwargs else text


def score_emoji(score: float) -> str:
    return "🟢" if score >= 65 else "🟡" if score >= 45 else "🔴"


def rec_emoji(label: str) -> str:
    return {"STRONG BUY": "🚀", "BUY": "🟢", "HOLD/WATCH": "🟡", "AVOID": "🔴"}.get(label, "⚪")
