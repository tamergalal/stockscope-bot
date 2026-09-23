"""Sharia-compliance screening (AAOIFI-inspired methodology).

Screens securities on two levels:
1. Business activity — excludes prohibited industries (conventional banking,
   insurance, alcohol, tobacco, gambling, weapons, adult entertainment, pork).
2. Financial ratios — interest-bearing debt/market cap < 33%,
   cash & interest-bearing securities/market cap < 33%.

Statuses: COMPLIANT, NON_COMPLIANT, DOUBTFUL (mixed/borderline),
UNKNOWN (insufficient data). Approximation from public data — verify with
your scholar or a certified screener (Zoya, Islamicly, Musaffa).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

DEBT_TO_MCAP_MAX = 0.33
CASH_TO_MCAP_MAX = 0.33

PROHIBITED_KEYWORDS = (
    "bank", "lending", "mortgage", "insurance", "alcohol", "brewer", "distiller",
    "tobacco", "gambl", "casino", "lottery", "weapon", "defense contractor",
    "adult", "pork", "pornography", "credit services",
)

ISLAMIC_INSTITUTIONS = {"ADIB.CA"}

# Known conventional (riba-based) financials — activity screen fails even when
# the data provider omits sector/industry fields (common for EGX on yfinance)
NON_COMPLIANT_TICKERS = {
    # EGX conventional banks & financiers
    "COMI.CA", "HRHO.CA", "BTFH.CA", "CCAP.CA", "CIEB.CA", "SAUD.CA",
    # US conventional banks / lenders / insurers
    "JPM", "BAC", "WFC", "C", "GS", "MS", "USB", "PNC", "COF", "AXP",
    "BLK", "SCHW", "MET", "PRU", "AIG", "ALL", "TRV", "BRK-B", "BRK-A",
    "PYPL", "SOFI", "V", "MA",  # payment networks (interest-linked revenue)
}

# US-listed Sharia-screened ETFs (screened by the issuer already)
SHARIA_ETFS: dict[str, dict] = {
    "HLAL": {"name": "Wahed FTSE USA Shariah ETF", "type": "US equities"},
    "SPUS": {"name": "SP Funds S&P 500 Sharia Industry Exclusions", "type": "US equities"},
    "UMMA": {"name": "Wahed Dow Jones Islamic World ETF", "type": "Global equities"},
    "SPSK": {"name": "SP Funds Dow Jones Global Sukuk ETF", "type": "Sukuk (Islamic bonds)"},
    "ISDU": {"name": "iShares MSCI USA Islamic", "type": "US equities"},
    "ISDE": {"name": "iShares MSCI Emerging Markets Islamic", "type": "EM equities"},
    "ISWD": {"name": "iShares MSCI World Islamic", "type": "Developed equities"},
}

# Seeds prioritized in /sharia scans; verdicts are still computed dynamically
SHARIA_EGX_SEED = {
    "ADIB.CA", "SWDY.CA", "JUFO.CA", "EFID.CA", "ISPH.CA", "RMDA.CA",
    "CLHO.CA", "ETEL.CA", "ESRS.CA", "ABUK.CA", "MFPC.CA", "SKPC.CA",
    "AMOC.CA", "ORWE.CA", "TMGH.CA", "PHDC.CA", "CIRA.CA",
}
SHARIA_US_SEED = {
    "MSFT", "NVDA", "GOOGL", "TSLA", "AMD", "AVGO", "QCOM", "TXN",
    "XOM", "CVX", "JNJ", "PFE", "ABBV", "CAT", "GE", "ADBE", "CRM",
    "ORCL", "CSCO", "IBM", "HD", "NKE", "UBER", "PLTR",
}

STATUS_COMPLIANT = "COMPLIANT"
STATUS_NON_COMPLIANT = "NON_COMPLIANT"
STATUS_DOUBTFUL = "DOUBTFUL"
STATUS_UNKNOWN = "UNKNOWN"

_BADGE = {
    STATUS_COMPLIANT: "☪️✅",
    STATUS_NON_COMPLIANT: "☪️❌",
    STATUS_DOUBTFUL: "☪️🟡",
    STATUS_UNKNOWN: "☪️❔",
}


@dataclass
class ShariaResult:
    status: str
    reasons: list[str] = field(default_factory=list)
    badge: str = ""
    note: str = ""

    def __post_init__(self) -> None:
        if not self.badge:
            self.badge = _BADGE.get(self.status, "☪️❔")


def _f(x: Any) -> float | None:
    try:
        v = float(x)
        return v if v == v else None
    except (TypeError, ValueError):
        return None


def screen_stock(symbol: str, info: dict[str, Any]) -> ShariaResult:
    """Screen a single stock using activity + financial ratio filters."""
    reasons: list[str] = []
    fail = doubt = False

    sector = str(info.get("sector", "") or "").lower()
    industry = str(info.get("industry", "") or "").lower()
    summary = str(info.get("longBusinessSummary", "") or "").lower()
    text = f"{sector} {industry} {summary[:400]}"

    sym = symbol.upper()
    if sym in ISLAMIC_INSTITUTIONS:
        reasons.append("Islamic financial institution (Sharia-supervised)")
    elif sym in NON_COMPLIANT_TICKERS:
        return ShariaResult(
            STATUS_NON_COMPLIANT,
            ["Known conventional (interest-based) financial institution"],
            note="Conventional banks/lenders/insurers operate on riba — not Sharia-compliant")
    elif any(k in text for k in PROHIBITED_KEYWORDS):
        return ShariaResult(
            STATUS_NON_COMPLIANT,
            [f"Prohibited core activity ({info.get('sector', '?')} / {info.get('industry', '?')})"],
            note="Core business involves interest, alcohol, gambling, or other prohibited activity")

    mcap = _f(info.get("marketCap"))
    debt = _f(info.get("totalDebt"))
    cash = _f(info.get("totalCash"))

    if mcap and mcap > 0:
        if debt is not None:
            d_ratio = debt / mcap
            if d_ratio >= DEBT_TO_MCAP_MAX:
                fail = True
                reasons.append(f"Interest-bearing debt/market cap = {d_ratio:.0%} (limit 33%)")
            else:
                reasons.append(f"Debt/market cap = {d_ratio:.0%} (within 33% limit)")
        if cash is not None:
            c_ratio = cash / mcap
            if c_ratio >= CASH_TO_MCAP_MAX:
                doubt = True
                reasons.append(f"Cash & interest-bearing securities = {c_ratio:.0%} of market cap (limit 33%)")
            else:
                reasons.append(f"Cash/market cap = {c_ratio:.0%} (within limit)")
    else:
        doubt = True
        reasons.append("Market cap / balance-sheet data unavailable - verify manually")

    if fail:
        status = STATUS_NON_COMPLIANT
        note = "Fails financial ratio screen"
    elif doubt:
        status = STATUS_DOUBTFUL
        note = "Borderline or incomplete data - verify with Zoya/Islamicly or your scholar"
    else:
        status = STATUS_COMPLIANT
        note = ("Passes activity & financial screens. Note: dividends may still need "
                "small 'purification' (donating the non-compliant income portion).")

    return ShariaResult(status, reasons, note=note)


def screen_etf(symbol: str, info: dict[str, Any]) -> ShariaResult:
    """Screen an ETF: known Islamic funds pass; bond funds fail; others doubtful."""
    sym = symbol.upper()
    if sym in SHARIA_ETFS:
        ftype = SHARIA_ETFS[sym]["type"]
        return ShariaResult(
            STATUS_COMPLIANT,
            [f"Sharia-screened by the fund issuer ({ftype})"],
            note="Holdings are pre-screened by an Islamic advisory board")
    category = str(info.get("category", "") or "").lower()
    long_name = str(info.get("longName", "") or "").lower()
    blob = f"{category} {long_name}"
    if "sukuk" in blob:
        return ShariaResult(STATUS_COMPLIANT, ["Sukuk (Islamic bond) fund"],
                            note="Sukuk are asset-backed Islamic instruments")
    if any(k in blob for k in ("bond", "treasury")):
        return ShariaResult(
            STATUS_NON_COMPLIANT,
            ["Conventional bond/interest-bearing fund"],
            note="Bond ETFs earn interest (riba); consider sukuk funds like SPSK")
    if "gold" in blob or "silver" in blob:
        return ShariaResult(
            STATUS_DOUBTFUL,
            ["Commodity-backed fund"],
            note="Physical gold ETFs are considered halal by many scholars (spot settlement conditions apply)")
    return ShariaResult(
        STATUS_DOUBTFUL,
        ["Holdings not Sharia-screened"],
        note="May hold non-compliant companies - prefer screened funds: HLAL, SPUS, UMMA, ISDU")


def screen(symbol: str, market: str, info: dict[str, Any]) -> ShariaResult:
    """Entry point: market-aware screening."""
    if market == "etf":
        return screen_etf(symbol, info)
    return screen_stock(symbol, info)

