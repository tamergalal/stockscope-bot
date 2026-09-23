"""Fundamental analysis engine.

Produces a 0-100 fundamental score from merged provider data:
- US stocks: valuation, quality, growth, financial health, dividends
- EGX stocks: same framework, tolerant of missing fields (free data is sparse)
- ETFs: cost, size/liquidity, yield, returns, drawdown
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FundamentalMetric:
    name: str
    value: str
    bias: float           # -1 .. +1
    note: str


@dataclass
class FundamentalResult:
    score: float
    metrics: list[FundamentalMetric] = field(default_factory=list)
    coverage: float = 0.0
    low_confidence: bool = False
    summary: str = ""


def _f(x: Any) -> float | None:
    """Coerce to float or None."""
    try:
        v = float(x)
        return v if v == v else None
    except (TypeError, ValueError):
        return None


def _fmt_pct(x: float | None) -> str:
    return f"{x * 100:.1f}%" if x is not None else "N/A"


_US_BENCH = {"pe": 22.0, "pb": 4.0, "roe": 0.15, "de": 1.0, "margin": 0.10, "rev_growth": 0.08}
_EGX_BENCH = {"pe": 10.0, "pb": 1.8, "roe": 0.18, "de": 1.2, "margin": 0.12, "rev_growth": 0.15}


def _score_stock(info: dict[str, Any], market: str) -> FundamentalResult:
    bench = _EGX_BENCH if market == "egx" else _US_BENCH
    metrics: list[FundamentalMetric] = []
    points = 50.0
    present = 0
    expected = 10

    def add(name: str, value: str, bias: float, note: str, pts: float) -> None:
        nonlocal points, present
        metrics.append(FundamentalMetric(name, value, bias, note))
        points += pts
        present += 1

    pe = _f(info.get("trailingPE"))
    if pe is not None:
        cheap = pe < bench["pe"]
        add("P/E (TTM)", f"{pe:.1f}", 0.6 if cheap else -0.4,
            ("Below" if cheap else "Above") + f" {market.upper()} benchmark ({bench['pe']:.0f})",
            6 if cheap else -4)
    fwd_pe = _f(info.get("forwardPE"))
    if fwd_pe is not None and pe is not None:
        improving = fwd_pe < pe
        add("Forward P/E", f"{fwd_pe:.1f}", 0.5 if improving else -0.3,
            "Earnings expected to grow" if improving else "Earnings expected to shrink",
            5 if improving else -4)
    pb = _f(info.get("priceToBook"))
    if pb is not None:
        cheap = pb < bench["pb"]
        add("P/B", f"{pb:.2f}", 0.4 if cheap else -0.3,
            f"vs benchmark {bench['pb']:.1f}", 4 if cheap else -3)
    roe = _f(info.get("returnOnEquity"))
    if roe is not None:
        good = roe > bench["roe"]
        add("ROE", _fmt_pct(roe), 0.7 if good else -0.4,
            ("Strong" if good else "Weak") + f" ROE (benchmark {bench['roe'] * 100:.0f}%)",
            7 if good else -5)
    margin = _f(info.get("profitMargins"))
    if margin is not None:
        good = margin > bench["margin"]
        add("Net Margin", _fmt_pct(margin), 0.5 if good else -0.3,
            f"vs benchmark {bench['margin'] * 100:.0f}%", 5 if good else -4)
    de = _f(info.get("debtToEquity"))
    if de is not None:
        de_ratio = de / 100.0
        ok = de_ratio < bench["de"]
        add("Debt/Equity", f"{de_ratio:.2f}", 0.5 if ok else -0.5,
            ("Manageable" if ok else "Elevated") + " leverage", 5 if ok else -5)
    rev_g = _f(info.get("revenueGrowth"))
    if rev_g is not None:
        good = rev_g > bench["rev_growth"]
        add("Revenue Growth (YoY)", _fmt_pct(rev_g), 0.6 if good else -0.4,
            ("Strong" if good else "Sluggish") + " top-line growth", 6 if good else -4)
    eps_g = _f(info.get("earningsGrowth"))
    if eps_g is not None:
        good = eps_g > 0.10
        add("EPS Growth (YoY)", _fmt_pct(eps_g), 0.6 if good else -0.4,
            "Double-digit earnings growth" if good else "Weak earnings growth", 5 if good else -4)
    div_y = _f(info.get("dividendYield"))
    if div_y is not None and div_y > 0:
        add("Dividend Yield", _fmt_pct(div_y), 0.4 if div_y > 0.02 else 0.1, "Income-generating", 3)
    fcf = _f(info.get("freeCashflow"))
    if fcf is not None:
        add("Free Cash Flow", "Positive" if fcf > 0 else "Negative",
            0.6 if fcf > 0 else -0.6, "Cash generation" if fcf > 0 else "Burning cash",
            4 if fcf > 0 else -5)

    coverage = present / expected
    score = float(round(max(0.0, min(100.0, points)), 1))
    low_conf = coverage < 0.6
    if market == "egx":
        metrics.append(FundamentalMetric(
            "EGX Context", "EGP market", 0.0,
            "Egyptian market: factor in EGP inflation/devaluation when comparing to US names"))
    summary = ("Valuation & quality look attractive" if score >= 65 else
               "Fundamentals are mixed" if score >= 45 else "Fundamentals look weak")
    if low_conf:
        summary += " (limited data - low confidence)"
    return FundamentalResult(score=score, metrics=metrics, coverage=round(coverage, 2),
                             low_confidence=low_conf, summary=summary)


def _score_etf(info: dict[str, Any], ohlcv_stats: dict[str, Any]) -> FundamentalResult:
    metrics: list[FundamentalMetric] = []
    points = 55.0
    present = 0
    expected = 6

    def add(name: str, value: str, bias: float, note: str, pts: float) -> None:
        nonlocal points, present
        metrics.append(FundamentalMetric(name, value, bias, note))
        points += pts
        present += 1

    er = _f(info.get("annualReportExpenseRatio")) or _f(info.get("netExpenseRatio"))
    if er is not None:
        cheap = er < 0.005
        add("Expense Ratio", _fmt_pct(er), 0.6 if cheap else -0.3,
            "Low cost" if cheap else "Higher cost", 8 if cheap else -4)
    aum = _f(info.get("totalAssets"))
    if aum is not None:
        big = aum > 1e9
        add("AUM", f"${aum / 1e9:.1f}B", 0.5 if big else -0.3,
            "Large & liquid" if big else "Smaller fund - check liquidity", 6 if big else -4)
    dy = _f(info.get("yield")) or _f(info.get("dividendYield"))
    if dy is not None and dy > 0:
        add("Yield", _fmt_pct(dy), 0.5 if dy > 0.025 else 0.2, "Income", 5)
    r1 = ohlcv_stats.get("return_1y")
    if r1 is not None:
        add("1Y Return", _fmt_pct(r1), 0.6 if r1 > 0.08 else (-0.4 if r1 < 0 else 0.1),
            "Trailing 1-year performance", 6 if r1 > 0.08 else (-5 if r1 < 0 else 0))
    mdd = ohlcv_stats.get("max_drawdown_1y")
    if mdd is not None:
        ok = mdd > -0.20
        add("Max Drawdown (1Y)", _fmt_pct(mdd), 0.4 if ok else -0.5,
            "Contained drawdowns" if ok else "Deep drawdowns", 4 if ok else -5)
    r3 = ohlcv_stats.get("return_3y_ann")
    if r3 is not None:
        add("3Y Annualized", _fmt_pct(r3), 0.5 if r3 > 0.06 else -0.2, "Longer-term record",
            5 if r3 > 0.06 else -3)

    coverage = present / expected
    score = float(round(max(0.0, min(100.0, points)), 1))
    summary = ("Solid, efficient fund" if score >= 65 else
               "Acceptable fund characteristics" if score >= 45 else "Weak fund characteristics")
    return FundamentalResult(score=score, metrics=metrics, coverage=round(coverage, 2),
                             low_confidence=coverage < 0.5, summary=summary)


def compute_price_stats(df: Any) -> dict[str, Any]:
    """Return stats used by ETF scoring: 1Y return, 3Y annualized, max drawdown."""
    close = df["Close"]
    stats: dict[str, Any] = {}
    if len(close) > 2:
        stats["return_1y"] = float(close.iloc[-1] / close.iloc[0] - 1)
    if len(close) > 60:
        years = len(close) / 252.0
        stats["return_3y_ann"] = float((close.iloc[-1] / close.iloc[0]) ** (1 / years) - 1)
    cummax = close.cummax()
    dd = (close / cummax - 1).min()
    stats["max_drawdown_1y"] = float(dd)
    return stats


def analyze_fundamental(data: dict[str, Any], market: str,
                        ohlcv_stats: dict[str, Any] | None = None) -> FundamentalResult:
    """Entry point: merged provider data -> FundamentalResult."""
    info = data.get("yf", {}) or {}
    if market == "etf":
        return _score_etf(info, ohlcv_stats or {})
    return _score_stock(info, market)

