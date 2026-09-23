"""HTML report formatting from analysis results."""

from __future__ import annotations

from ..analysis.service import FullReport
from ..config import DISCLAIMER_SHORT
from .glossary import explain_used_terms
from .messages import rec_emoji, score_emoji, t


def summary_card(r: FullReport, lang: str = "en") -> str:
    market_key = f"market_{r.market}"
    sign = "+" if r.change_pct >= 0 else ""
    lines = [
        f"<b>{r.name}</b> ({r.symbol}) — {t(market_key, lang)}",
        f"💵 {r.price:.2f} {r.currency} ({sign}{r.change_pct}%)",
        "",
        f"{score_emoji(r.tech.score)} Technical: <b>{r.tech.score:.0f}</b>/100",
        f"{score_emoji(r.fund.score)} Fundamental: <b>{r.fund.score:.0f}</b>/100"
        + (" <i>(low confidence)</i>" if r.fund.low_confidence else ""),
    ]
    if r.sharia:
        lines.append(f"{r.sharia.badge} Sharia: <b>{r.sharia.status}</b>")
    lines += [
        "",
        f"{rec_emoji(r.rec.label)} <b>{r.rec.label}</b> — composite <b>{r.rec.composite:.0f}</b>/100",
    ]
    return "\n".join(lines)


def compute_pnl(quantity: float, buy_price: float, current_price: float) -> tuple[float, float]:
    """Return (absolute P/L, percent P/L) for a position."""
    pl_abs = (current_price - buy_price) * quantity
    pl_pct = ((current_price - buy_price) / buy_price * 100) if buy_price else 0.0
    return round(pl_abs, 2), round(pl_pct, 2)


def _glossary_block(hints: list[str], lang: str) -> list[str]:
    explained = explain_used_terms(hints, lang)
    return ["", "📖 <b>Terms explained:</b>"] + explained if explained else []


def technical_section(r: FullReport, lang: str = "en") -> str:
    lines = [f"📊 <b>Technical Analysis — {r.symbol}</b>", ""]
    hints: list[str] = []
    for s in r.tech.signals:
        icon = "🟢" if s.bias > 0.3 else "🔴" if s.bias < -0.3 else "⚪"
        lines.append(f"{icon} <b>{s.name}</b>: {s.note}")
        hints.append(s.name)
    if r.tech.supports:
        lines.append(f"\n🧱 Supports: {', '.join(f'{x:.2f}' for x in r.tech.supports)}")
        hints.append("Support")
    if r.tech.resistances:
        lines.append(f"🚧 Resistances: {', '.join(f'{x:.2f}' for x in r.tech.resistances)}")
        hints.append("Resistance")
    cons = r.tech.timeframe_consensus
    if "weekly" in cons:
        lines.append(f"🕐 Timeframes: daily {cons['daily']:.0f} / weekly {cons['weekly']:.0f}")
    lines.append(f"\nTechnical score: <b>{r.tech.score:.0f}/100</b> {score_emoji(r.tech.score)}")
    lines += _glossary_block(hints, lang)
    return "\n".join(lines)


def fundamental_section(r: FullReport, lang: str = "en") -> str:
    lines = [f"💰 <b>Fundamental Analysis — {r.symbol}</b>", ""]
    hints: list[str] = []
    for m in r.fund.metrics:
        icon = "🟢" if m.bias > 0.3 else "🔴" if m.bias < -0.3 else "⚪"
        lines.append(f"{icon} <b>{m.name}</b>: {m.value} — {m.note}")
        hints.append(m.name)
    lines.append(f"\n<i>{r.fund.summary}</i>")
    lines.append(f"Fundamental score: <b>{r.fund.score:.0f}/100</b> {score_emoji(r.fund.score)}")
    lines += _glossary_block(hints, lang)
    return "\n".join(lines)


def sharia_section(r: FullReport, lang: str = "en") -> str:
    """Sharia-compliance card."""
    if not r.sharia:
        return ""
    s = r.sharia
    lines = [f"☪️ <b>Sharia Compliance — {r.symbol}</b>", "",
             f"{s.badge} Status: <b>{s.status}</b>", ""]
    lines += [f"  • {reason}" for reason in s.reasons]
    lines += ["", f"<i>{s.note}</i>"]
    lines += _glossary_block(["Sharia", "Sukuk", "Riba", "Purification"], lang)
    return "\n".join(lines)


def recommendation_card(r: FullReport) -> str:
    rec = r.rec
    lines = [
        f"🎯 <b>Recommendation — {r.symbol}</b>",
        "",
        f"{rec_emoji(rec.label)} <b>{rec.label}</b> ({rec.composite:.0f}/100)",
        "",
        "<b>Why:</b>",
    ]
    lines += [f"  ✅ {x}" for x in rec.reasons_for]
    lines.append("<b>Risks:</b>")
    lines += [f"  ⚠️ {x}" for x in rec.risks_against]
    if rec.trade_plan:
        tp = rec.trade_plan
        lines += [
            "",
            f"📋 <b>Trade Plan</b> ({tp.horizon}, {tp.conviction} conviction)",
            f"  • Entry zone: {tp.entry_low:.2f} – {tp.entry_high:.2f} {r.currency}",
            f"  • Stop-loss: {tp.stop_loss:.2f} {r.currency}",
            f"  • Targets: T1 {tp.target1:.2f} / T2 {tp.target2:.2f} {r.currency}",
            f"  • Risk/Reward: {tp.risk_reward:.1f} | Risk ≤ 2% of portfolio",
        ]
    lines += ["", DISCLAIMER_SHORT]
    return "\n".join(lines)
