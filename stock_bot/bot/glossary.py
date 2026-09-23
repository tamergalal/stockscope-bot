"""Glossary of financial/technical terms, English + Arabic.

Used to (a) auto-explain terms appearing in reports and (b) power /glossary.
"""

from __future__ import annotations

GLOSSARY: dict[str, dict[str, str]] = {
    "RSI": {
        "en": "Relative Strength Index (0-100). Above 70 = overbought (may pull back), below 30 = oversold (may rebound).",
        "ar": "مؤشر القوة النسبية (0-100). فوق 70 = تشبع شرائي (احتمال هبوط)، تحت 30 = تشبع بيعي (احتمال ارتداد).",
    },
    "MACD": {
        "en": "Moving Average Convergence Divergence. MACD crossing above its signal line = bullish momentum shift.",
        "ar": "مؤشر تقارب وتباعد المتوسطات. تقاطعه لأعلى فوق خط الإشارة = تحول إيجابي في الزخم.",
    },
    "ADX": {
        "en": "Average Directional Index. Above 25 = strong trend; below = sideways/ranging market.",
        "ar": "مؤشر متوسط الاتجاه. فوق 25 = اتجاه قوي، أقل من ذلك = سوق عرضي بدون اتجاه.",
    },
    "SMA": {
        "en": "Simple Moving Average — average closing price over N days. Price above it = uptrend.",
        "ar": "المتوسط المتحرك البسيط — متوسط سعر الإغلاق خلال عدد من الأيام. السعر فوقه = اتجاه صاعد.",
    },
    "OBV": {
        "en": "On-Balance Volume — cumulative volume flow. Rising OBV = buyers accumulating.",
        "ar": "مؤشر حجم التداول التراكمي. ارتفاعه = المشترون يتجمّعون (ضغط شرائي).",
    },
    "ATR": {
        "en": "Average True Range — measures daily volatility. Used to size stop-losses.",
        "ar": "متوسط المدى الحقيقي — يقيس التقلب اليومي. يُستخدم لتحديد وقف الخسارة.",
    },
    "Bollinger": {
        "en": "Bollinger Bands — volatility bands around the 20-day average. Touching the lower band can signal a bounce.",
        "ar": "أحزمة بولينجر — نطاقات تقلب حول متوسط 20 يومًا. ملامسة الحزمة السفلى قد تعني ارتدادًا.",
    },
    "Golden Cross": {
        "en": "50-day average crossing above the 200-day average — a major long-term bullish signal.",
        "ar": "تقاطع متوسط 50 يومًا فوق متوسط 200 يوم — إشارة صعود قوية طويلة المدى.",
    },
    "Support": {
        "en": "Price level where buying historically stopped declines (a 'floor').",
        "ar": "مستوى سعري يتوقف عنده الهبوط تاريخيًا بسبب دخول المشترين (أرضية).",
    },
    "Resistance": {
        "en": "Price level where selling historically stopped rallies (a 'ceiling').",
        "ar": "مستوى سعري يتوقف عنده الصعود تاريخيًا بسبب البيع (سقف).",
    },
    "Breakout": {
        "en": "Price moving above a key resistance — often starts a new uptrend.",
        "ar": "اختراق السعر لمقاومة مهمة — غالبًا بداية موجة صعود جديدة.",
    },
    "Divergence": {
        "en": "Price and an indicator move in opposite directions — warns the trend may reverse.",
        "ar": "تحرك السعر عكس المؤشر — تحذير من احتمال انعكاس الاتجاه.",
    },
    "P/E": {
        "en": "Price-to-Earnings ratio — price paid per $1 of profit. Lower vs peers = cheaper.",
        "ar": "مكرر الربحية — السعر المدفوع مقابل كل جنيه/دولار ربح. الأقل من المنافسين = أرخص.",
    },
    "P/B": {
        "en": "Price-to-Book — price vs net asset value per share. Below benchmark = potentially undervalued.",
        "ar": "مضاعف القيمة الدفترية — السعر مقابل صافي قيمة الأصول للسهم. الأقل من المعيار = مقوم بأقل من قيمته.",
    },
    "ROE": {
        "en": "Return on Equity — profit generated per $1 of shareholders' equity. Higher = better quality.",
        "ar": "العائد على حقوق الملكية — الربح الناتج عن كل جنيه من أموال المساهمين. الأعلى = جودة أفضل.",
    },
    "D/E": {
        "en": "Debt-to-Equity — leverage level. High D/E = more financial risk.",
        "ar": "نسبة الدين إلى حقوق الملكية — مستوى الاقتراض. الارتفاع = مخاطر مالية أكبر.",
    },
    "EPS": {
        "en": "Earnings Per Share — net profit divided by share count. Growing EPS drives stock prices.",
        "ar": "ربحية السهم — صافي الربح مقسومًا على عدد الأسهم. نموها يدفع سعر السهم.",
    },
    "FCF": {
        "en": "Free Cash Flow — cash left after expenses & investments. Positive FCF = self-funding company.",
        "ar": "التدفق النقدي الحر — النقد المتبقي بعد المصاريف والاستثمارات. الموجب = شركة تمول نفسها.",
    },
    "Yield": {
        "en": "Dividend yield — annual dividends as % of the price. Income for holders.",
        "ar": "عائد التوزيعات — التوزيعات السنوية كنسبة من السعر. دخل دوري للمساهم.",
    },
    "Expense Ratio": {
        "en": "Annual fund fee as % of your investment. Lower = more of the returns stay with you.",
        "ar": "نسبة المصاريف السنوية للصندوق. كلما قلّت زادت حصتك من العائد.",
    },
    "AUM": {
        "en": "Assets Under Management — fund size. Large AUM = better liquidity and stability.",
        "ar": "الأصول المُدارة — حجم الصندوق. الحجم الكبير = سيولة واستقرار أفضل.",
    },
    "Drawdown": {
        "en": "Largest peak-to-trough loss. Smaller drawdowns = calmer ride.",
        "ar": "أكبر خسارة من القمة للقاع. الانخفاض الأصغر = مخاطرة أهدأ.",
    },
    "Stop-loss": {
        "en": "Pre-set exit price that limits your loss if the trade goes wrong. Never skip it.",
        "ar": "سعر خروج محدد مسبقًا يحدّ خسارتك إذا سارت الصفقة عكسك. لا تتجاهله أبدًا.",
    },
    "Risk/Reward": {
        "en": "Potential profit vs potential loss. Aim for 2:1 or better.",
        "ar": "الربح المحتمل مقابل الخسارة المحتملة. استهدف 2:1 أو أفضل.",
    },
    "Composite": {
        "en": "Final 0-100 score blending technical + fundamental analysis (50/50 for stocks, 60/40 for ETFs).",
        "ar": "الدرجة النهائية (0-100) المدمجة من التحليل الفني والمالي (50/50 للأسهم، 60/40 للصناديق).",
    },
    "Sharia": {
        "en": "Islamic-law compliance screen: no prohibited activities (alcohol, gambling, riba-based finance) + debt & cash below 33% of market cap.",
        "ar": "فلتر التوافق الشرعي: استبعاد الأنشطة المحرمة (خمور، قمار، تمويل ربوي) + الدين والنقدية أقل من 33% من القيمة السوقية.",
    },
    "Sukuk": {
        "en": "Islamic bonds — asset-backed certificates paying profit (not interest). Halal alternative to bond ETFs.",
        "ar": "الصكوك الإسلامية — شهادات مرتبطة بأصول توزع ربحًا (وليس فائدة). بديل حلال لصناديق السندات.",
    },
    "Purification": {
        "en": "Donating the small non-compliant income portion of dividends to charity to 'purify' returns.",
        "ar": "التطهير: التبرع بالجزء الصغير غير المتوافق من التوزيعات لتطهير العائد شرعًا.",
    },
    "Riba": {
        "en": "Interest/usury — prohibited in Islamic finance. Bond ETFs and conventional banks earn riba.",
        "ar": "الربا — الفائدة المحرمة شرعًا. صناديق السندات والبنوك التقليدية تتعامل بالربا.",
    },
}


def explain_term(term: str, lang: str = "en") -> str | None:
    """Return the explanation for a term, or None if unknown."""
    entry = GLOSSARY.get(term.strip())
    return (entry.get(lang) or entry.get("en")) if entry else None


def explain_used_terms(text_hints: list[str], lang: str = "en", max_terms: int = 6) -> list[str]:
    """Return one-line explanations for glossary terms found in the hints."""
    found: list[str] = []
    blob = " ".join(text_hints).lower()
    for term, entry in GLOSSARY.items():
        if term.lower() in blob:
            found.append(f"• <b>{term}</b>: {entry.get(lang) or entry['en']}")
        if len(found) >= max_terms:
            break
    return found


def all_terms_index(lang: str = "en") -> str:
    """Full glossary listing for /glossary with no args."""
    lines = ["📖 <b>Glossary / المصطلحات</b>", ""]
    for term, entry in GLOSSARY.items():
        lines.append(f"• <b>{term}</b> — {entry.get(lang) or entry['en']}")
    return "\n".join(lines)

