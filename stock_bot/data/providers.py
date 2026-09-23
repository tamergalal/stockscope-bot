"""Market data providers.

YFinanceProvider covers EGX (.CA), US stocks, and ETFs for OHLCV + basic info.
FMPProvider (optional, needs FMP_API_KEY) enriches US fundamentals.
All network calls are synchronous (yfinance limitation) and are executed in
threads by callers; results are cached with TTL.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

import pandas as pd
import requests
import yfinance as yf
from cachetools import TTLCache

from ..config import settings

logger = logging.getLogger(__name__)


class DataProviderError(Exception):
    """Raised when market data cannot be fetched for a symbol."""


def _retry(fn, attempts: int = 3, base_delay: float = 1.0):
    """Run fn with exponential backoff; re-raise the last exception."""
    last_exc: Exception | None = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - provider errors are heterogeneous
            last_exc = exc
            delay = base_delay * (2 ** i)
            logger.warning("Provider attempt %d failed (%s); retrying in %.1fs", i + 1, exc, delay)
            time.sleep(delay)
    raise DataProviderError(str(last_exc))


class YFinanceProvider:
    """Yahoo Finance-backed provider for OHLCV, quotes, and basic fundamentals."""

    def __init__(self) -> None:
        self._ohlcv_cache: TTLCache = TTLCache(maxsize=512, ttl=settings.ohlcv_cache_ttl)
        self._info_cache: TTLCache = TTLCache(maxsize=512, ttl=settings.fundamentals_cache_ttl)

    def get_ohlcv(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Return OHLCV DataFrame indexed by date, columns Open/High/Low/Close/Volume."""
        key = (symbol, period, interval)
        if key in self._ohlcv_cache:
            return self._ohlcv_cache[key]

        def _fetch() -> pd.DataFrame:
            df = yf.Ticker(symbol).history(period=period, interval=interval, auto_adjust=True)
            if df is None or df.empty:
                raise DataProviderError(f"No price data returned for {symbol}")
            df = df[["Open", "High", "Low", "Close", "Volume"]].dropna(subset=["Close"])
            df.index = pd.to_datetime(df.index).tz_localize(None)
            return df

        df = _retry(_fetch)
        self._ohlcv_cache[key] = df
        return df

    def get_info(self, symbol: str) -> dict[str, Any]:
        """Return the raw yfinance .info dict (cached 24h). Never raises."""
        if symbol in self._info_cache:
            return self._info_cache[symbol]
        info: dict[str, Any] = {}
        try:
            info = dict(_retry(lambda: yf.Ticker(symbol).info or {}, attempts=2))
        except Exception as exc:  # noqa: BLE001
            logger.warning("info fetch failed for %s: %s", symbol, exc)
        self._info_cache[symbol] = info
        return info

    def get_quote(self, symbol: str) -> dict[str, Any]:
        """Latest price snapshot derived from recent OHLCV."""
        df = self.get_ohlcv(symbol, period="5d", interval="1d").dropna(subset=["Close"])
        last = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else last
        change_pct = float((last["Close"] - prev["Close"]) / prev["Close"] * 100) if prev["Close"] else 0.0
        return {
            "price": float(last["Close"]),
            "change_pct": round(change_pct, 2),
            "volume": float(last.get("Volume", 0) or 0),
            "date": str(df.index[-1].date()),
        }



class FMPAuthError(Exception):
    """FMP rejected the key/plan (401/403) — disable for the session."""


class FMPProvider:
    """Financial Modeling Prep fundamentals (US stocks/ETFs). Optional.

    Auto-disables for the session if the key/plan is rejected (401/403), so
    the bot falls back to yfinance without wasting time on retries.
    """

    BASE = "https://financialmodelingprep.com/api/v3"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or settings.fmp_api_key
        self._disabled = False
        self._cache: TTLCache = TTLCache(maxsize=256, ttl=settings.fundamentals_cache_ttl)

    @property
    def available(self) -> bool:
        return bool(self.api_key) and not self._disabled

    def _get(self, path: str) -> Any:
        url = f"{self.BASE}{path}"
        if url in self._cache:
            return self._cache[url]

        def _fetch():
            resp = requests.get(url, params={"apikey": self.api_key}, timeout=15)
            if resp.status_code in (401, 403):
                raise FMPAuthError(f"FMP {resp.status_code}: key/plan rejected")
            resp.raise_for_status()
            return resp.json()

        try:
            data = _retry(_fetch, attempts=2)
        except FMPAuthError:
            self._disabled = True
            logger.warning("FMP disabled for this session (key/plan rejected). "
                           "Fundamentals will use yfinance fallback.")
            raise
        self._cache[url] = data
        return data

    def key_metrics(self, symbol: str) -> dict[str, Any]:
        """Latest annual key metrics (PE, PB, ROE, etc.) or {} if unavailable."""
        if not self.available:
            return {}
        try:
            data = self._get(f"/key-metrics/{symbol.upper()}?limit=1")
            return data[0] if isinstance(data, list) and data else {}
        except Exception as exc:  # noqa: BLE001
            logger.warning("FMP key_metrics failed for %s: %s", symbol, exc)
            return {}

    def ratios(self, symbol: str) -> dict[str, Any]:
        if not self.available:
            return {}
        try:
            data = self._get(f"/ratios/{symbol.upper()}?limit=1")
            return data[0] if isinstance(data, list) and data else {}
        except Exception as exc:  # noqa: BLE001
            logger.warning("FMP ratios failed for %s: %s", symbol, exc)
            return {}


@dataclass
class DataService:
    """Facade combining providers; the rest of the app only talks to this."""

    yf_provider: YFinanceProvider = field(default_factory=YFinanceProvider)
    fmp_provider: FMPProvider = field(default_factory=FMPProvider)

    def get_ohlcv(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        return self.yf_provider.get_ohlcv(symbol, period, interval)

    def get_quote(self, symbol: str) -> dict[str, Any]:
        return self.yf_provider.get_quote(symbol)

    def get_fundamentals(self, symbol: str, market: str) -> dict[str, Any]:
        """Merged fundamentals: yfinance info (+ FMP ratios for US symbols)."""
        info = self.yf_provider.get_info(symbol)
        merged: dict[str, Any] = {"yf": info, "fmp_metrics": {}, "fmp_ratios": {}}
        if market == "us" and self.fmp_provider.available:
            merged["fmp_metrics"] = self.fmp_provider.key_metrics(symbol)
            merged["fmp_ratios"] = self.fmp_provider.ratios(symbol)
        return merged
