"""Composite scoring & recommendation engine.

Combines technical + fundamental sub-scores into a 0-100 composite and maps it
to STRONG BUY / BUY / HOLD / AVOID with a full trade plan for buy signals.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..config import settings
from .fundamental import FundamentalResult
from .technical import TechnicalResult

RECOMMENDATIONS = ("STRONG BUY", "BUY", "HOLD/WATCH", "AVOID")


@dataclass
class TradePlan:
    entry_low: float = 0.0
    entry_high: float = 0.0
    stop_loss: float = 0.0
    target1: float = 0.0
    target2: float = 0.0
    risk_reward: float = 0.0
    horizon: str = ""
    conviction: str = ""


@dataclass
class Recommendation:
    composite: float
    label: str
    tech_score: float
    fund_score: float
    reasons_for: list[str] = field(default_factory=list)
    risks_against: list[str] = field(default_factory=list)
    trade_plan: TradePlan | None = None


def recommendation_label(score: float) -> str:
    """Map composite score to recommendation band."""
    if score >= settings.band_strong_buy:
        return "STRONG BUY"
    if score >= settings.band_buy:
        return "BUY"
    if score >= settings.band_hold:
        return "HOLD/WATCH"
    return "AVOID"


def _build_trade_plan(tech: TechnicalResult) -> TradePlan:
    """ATR-based trade plan: entry zone, stop, targets, R:R."""
    price = tech.last_close
    atr = tech.atr_value if tech.atr_value > 0 else price * 0.02
    nearest_sup = max([s for s in tech.supports if s < price], default=None)
    nearest_res = min([r for r in tech.resistances if r > price], default=None)

    entry_low = price - 0.5 * atr
    entry_high = price + 0.2 * atr
    sl_from_atr = price - settings.atr_stop_multiplier * atr
    # use the tighter of ATR stop vs just-below-support
    stop = sl_from_atr
    if nearest_sup and nearest_sup < price:
        stop = max(sl_from_atr, nearest_sup - 0.3 * atr)
    t1 = nearest_res if nearest_res else price + 1.5 * atr
    t2 = price + 3 * atr if not nearest_res else nearest_res + 2 * atr

    risk = max(price - stop, 1e-9)
    reward = max(t1 - price, 0.0)
    rr = round(reward / risk, 2) if risk > 0 else 0.0

    horizon = "Swing (2-6 weeks)" if tech.timeframe_consensus.get("weekly", 50) < 60 else "Position (3-12 months)"
    conviction = ("High" if tech.score >= 75 else "Medium" if tech.score >= 60 else "Low")
    return TradePlan(entry_low=round(entry_low, 2), entry_high=round(entry_high, 2),
                     stop_loss=round(stop, 2), target1=round(t1, 2), target2=round(t2, 2),
                     risk_reward=rr, horizon=horizon, conviction=conviction)


def make_recommendation(tech: TechnicalResult, fund: FundamentalResult,
                        asset_type: str = "stock") -> Recommendation:
    """Combine sub-scores -> Recommendation with rationale and trade plan."""
    w = settings.weights.get(asset_type, settings.weights["stock"])
    composite = round(w["technical"] * tech.score + w["fundamental"] * fund.score, 1)
    label = recommendation_label(composite)

    bull = sorted([s for s in tech.signals if s.bias > 0.3], key=lambda s: -s.bias)
    bear = sorted([s for s in tech.signals if s.bias < -0.3], key=lambda s: s.bias)
    fbull = [m for m in fund.metrics if m.bias > 0.3]
    fbear = [m for m in fund.metrics if m.bias < -0.3]

    reasons_for = [s.note for s in bull][:2] + [f"{m.name}: {m.value} ({m.note})" for m in fbull][:2]
    risks = [s.note for s in bear][:1] + [f"{m.name}: {m.value} ({m.note})" for m in fbear][:1]
    if fund.low_confidence:
        risks.append("Fundamental data incomplete - reduced confidence")
    if not reasons_for:
        reasons_for = ["No strong bullish factors detected"]
    if not risks:
        risks = ["No major bearish factors detected"]

    plan = _build_trade_plan(tech) if label in ("BUY", "STRONG BUY") else None
    return Recommendation(composite=composite, label=label, tech_score=tech.score,
                          fund_score=fund.score, reasons_for=reasons_for[:3],
                          risks_against=risks[:2], trade_plan=plan)
