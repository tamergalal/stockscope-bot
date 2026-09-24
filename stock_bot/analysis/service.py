"""Analysis orchestrator: fetches data and runs the full pipeline per symbol."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from ..data.providers import DataService
from ..data.symbols import detect_market, normalize_symbol, symbol_meta
from ..storage.repo import log_recommendation
from .fundamental import FundamentalResult, analyze_fundamental, compute_price_stats
from .scoring import Recommendation, make_recommendation
from .sharia import (SHARIA_EGX_SEED, SHARIA_ETFS, SHARIA_US_SEED,
                     ShariaResult, screen)
from .technical import TechnicalResult, analyze_technical


@dataclass
class FullReport:
    symbol: str
    market: str
    currency: str
    name: str
    tech: TechnicalResult
    fund: FundamentalResult
    rec: Recommendation
    price: float
    change_pct: float
    sharia: ShariaResult = None


class AnalysisService:
    """High-level facade used by bot handlers. All blocking I/O runs in threads."""

    def __init__(self, data: DataService | None = None) -> None:
        self.data = data or DataService()

    async def analyze(self, raw_symbol: str) -> FullReport:
        """Full pipeline for one symbol (async wrapper around sync providers)."""
        return await asyncio.to_thread(self._analyze_sync, raw_symbol)

    def _analyze_sync(self, raw_symbol: str) -> FullReport:
        market = detect_market(raw_symbol)
        symbol = normalize_symbol(raw_symbol, market)

        df_daily = self.data.get_ohlcv(symbol, period="1y", interval="1d")
        weekly = None
        try:
            weekly = self.data.get_ohlcv(symbol, period="3y", interval="1wk")
        except Exception:
            weekly = None

        tech = analyze_technical(df_daily, weekly_df=weekly)
        stats = compute_price_stats(df_daily) if market == "etf" else None
        fund_data = self.data.get_fundamentals(symbol, market)
        fund = analyze_fundamental(fund_data, market, stats)
        asset_type = "etf" if market == "etf" else "stock"
        rec = make_recommendation(tech, fund, asset_type)
        sharia_res = screen(symbol, market, fund_data.get("yf", {}))

        # Derive the price snapshot from the already-fetched daily bars instead
        # of a separate quote request — saves one network round-trip per symbol
        # (matters a lot when scanning a whole universe).
        df = df_daily.dropna(subset=["Close"])
        last = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else last
        price = float(last["Close"])
        change_pct = (round(float((last["Close"] - prev["Close"]) / prev["Close"] * 100), 2)
                      if prev["Close"] else 0.0)
        meta = symbol_meta(symbol)
        currency = "EGP" if market == "egx" else "USD"

        log_recommendation(symbol, market, rec.composite, rec.label)

        return FullReport(
            symbol=symbol, market=market, currency=currency,
            name=meta.get("name", fund_data.get("yf", {}).get("shortName", symbol)),
            tech=tech, fund=fund, rec=rec,
            price=price, change_pct=change_pct,
            sharia=sharia_res,
        )

    async def _analyze_many(self, symbols: list[str],
                            concurrency: int = 5) -> list[FullReport]:
        """Analyze many symbols concurrently (bounded to stay rate-limit friendly).

        Provider calls are blocking network I/O, so running ~5 in parallel cuts
        a full-universe scan from minutes to tens of seconds without hammering
        Yahoo. Symbols that fail (delisted, no data) are skipped.
        """
        sem = asyncio.Semaphore(concurrency)

        async def _one(sym: str) -> FullReport | None:
            async with sem:
                try:
                    return await self.analyze(sym)
                except Exception:
                    return None

        results = await asyncio.gather(*(_one(s) for s in symbols))
        return [r for r in results if r is not None]

    async def scan(self, market: str, top_n: int = 5) -> list[FullReport]:
        """Analyze all symbols of a market, return top N by composite score."""
        from ..data.symbols import EGX_SYMBOLS, ETF_SYMBOLS, US_SYMBOLS
        universe = {"egx": EGX_SYMBOLS, "us": US_SYMBOLS, "etf": ETF_SYMBOLS}.get(market, {})
        reports = await self._analyze_many(list(universe))
        reports.sort(key=lambda r: r.rec.composite, reverse=True)
        return reports[:top_n]

    async def scan_sharia(self, market: str, top_n: int = 5) -> list[FullReport]:
        """Scan the Sharia-compliant universe of a market, ranked by score.

        Universe: EGX/US seed lists (activity-screened) or known Islamic ETFs.
        Financial-ratio screens are re-applied from live data.
        """
        universe: list[str] = {
            "egx": sorted(SHARIA_EGX_SEED),
            "us": sorted(SHARIA_US_SEED),
            "etf": sorted(SHARIA_ETFS.keys()),
        }.get(market, [])
        analyzed = await self._analyze_many(universe)
        reports = [r for r in analyzed if r.sharia.status != "NON_COMPLIANT"]
        reports.sort(key=lambda r: r.rec.composite, reverse=True)
        return reports[:top_n]

    async def scan_cheap(self, market: str, max_price: float,
                         top_n: int = 10) -> list[FullReport]:
        """Sharia-compliant stocks priced at/below max_price, ranked by score.

        Unlike scan_sharia, the universe is the FULL market list (not just the
        Sharia seed lists) — compliance and price are both checked from live
        data, so cheap names outside the seeds are found too.
        """
        from ..data.symbols import EGX_SYMBOLS, US_SYMBOLS
        universe = {"egx": EGX_SYMBOLS, "us": US_SYMBOLS}.get(market, {})
        analyzed = await self._analyze_many(list(universe))
        reports = [r for r in analyzed
                   if r.sharia.status != "NON_COMPLIANT" and r.price <= max_price]
        reports.sort(key=lambda r: r.rec.composite, reverse=True)
        return reports[:top_n]
