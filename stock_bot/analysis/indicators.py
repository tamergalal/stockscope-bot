"""Technical indicator library implemented natively with pandas/numpy.

Chosen over pandas-ta/TA-Lib for zero binary dependencies and compatibility
with all Python versions (pandas-ta requires numba, unavailable on 3.14+).
All functions accept/return pandas Series aligned to the input index.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def sma(series: pd.Series, length: int) -> pd.Series:
    """Simple moving average."""
    return series.rolling(window=length, min_periods=length).mean()


def ema(series: pd.Series, length: int) -> pd.Series:
    """Exponential moving average."""
    return series.ewm(span=length, adjust=False, min_periods=length).mean()


def rsi(close: pd.Series, length: int = 14) -> pd.Series:
    """Relative Strength Index (Wilder smoothing)."""
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1 / length, min_periods=length, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / length, min_periods=length, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out = 100 - (100 / (1 + rs))
    # When there are no losses at all RSI is 100
    return out.fillna(100.0).where(avg_loss.notna() | avg_gain.notna())


def macd(
    close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """MACD line, signal line, histogram."""
    macd_line = ema(close, fast) - ema(close, slow)
    signal_line = macd_line.ewm(span=signal, adjust=False, min_periods=signal).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def stoch(
    high: pd.Series, low: pd.Series, close: pd.Series, k: int = 14, d: int = 3
) -> tuple[pd.Series, pd.Series]:
    """Stochastic %K and %D."""
    lowest_low = low.rolling(window=k, min_periods=k).min()
    highest_high = high.rolling(window=k, min_periods=k).max()
    rng = (highest_high - lowest_low).replace(0, np.nan)
    pct_k = 100 * (close - lowest_low) / rng
    pct_d = pct_k.rolling(window=d, min_periods=d).mean()
    return pct_k, pct_d


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat(
        [(high - low), (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    return tr


def atr(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14) -> pd.Series:
    """Average True Range (Wilder smoothing)."""
    tr = true_range(high, low, close)
    return tr.ewm(alpha=1 / length, min_periods=length, adjust=False).mean()


def adx(
    high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Average Directional Index, +DI, -DI (Wilder)."""
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = pd.Series(
        np.where((up_move > down_move) & (up_move > 0), up_move, 0.0), index=high.index
    )
    minus_dm = pd.Series(
        np.where((down_move > up_move) & (down_move > 0), down_move, 0.0), index=high.index
    )
    tr = true_range(high, low, close)
    atr_w = tr.ewm(alpha=1 / length, min_periods=length, adjust=False).mean()
    plus_di = 100 * plus_dm.ewm(alpha=1 / length, min_periods=length, adjust=False).mean() / atr_w.replace(0, np.nan)
    minus_di = 100 * minus_dm.ewm(alpha=1 / length, min_periods=length, adjust=False).mean() / atr_w.replace(0, np.nan)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    adx_line = dx.ewm(alpha=1 / length, min_periods=length, adjust=False).mean()
    return adx_line, plus_di, minus_di


def bollinger_bands(
    close: pd.Series, length: int = 20, std: float = 2.0
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Bollinger upper, middle (SMA), lower bands."""
    mid = sma(close, length)
    sigma = close.rolling(window=length, min_periods=length).std(ddof=0)
    upper = mid + std * sigma
    lower = mid - std * sigma
    return upper, mid, lower


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """On-Balance Volume."""
    direction = np.sign(close.diff()).fillna(0.0)
    return (direction * volume.fillna(0.0)).cumsum()


def vwap(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
    """Cumulative VWAP over the loaded period (anchored to first bar)."""
    typical = (high + low + close) / 3
    vol = volume.replace(0, np.nan)
    cum_tp_vol = (typical * vol).cumsum()
    cum_vol = vol.cumsum()
    return cum_tp_vol / cum_vol


def roc(close: pd.Series, length: int = 12) -> pd.Series:
    """Rate of change (percent)."""
    return close.pct_change(periods=length) * 100


def williams_r(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14) -> pd.Series:
    """Williams %R (-100..0)."""
    hh = high.rolling(window=length, min_periods=length).max()
    ll = low.rolling(window=length, min_periods=length).min()
    return -100 * (hh - close) / (hh - ll).replace(0, np.nan)


def ichimoku(
    high: pd.Series, low: pd.Series, close: pd.Series
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    """Ichimoku: tenkan(9), kijun(26), senkou_a, senkou_b (52)."""
    def midpoint(period: int) -> pd.Series:
        return (
            high.rolling(window=period, min_periods=period).max()
            + low.rolling(window=period, min_periods=period).min()
        ) / 2

    tenkan = midpoint(9)
    kijun = midpoint(26)
    senkou_a = ((tenkan + kijun) / 2).shift(26)
    senkou_b = midpoint(52).shift(26)
    return tenkan, kijun, senkou_a, senkou_b


def pivot_points(high: float, low: float, close: float) -> dict[str, float]:
    """Classic floor-trader pivot levels from a reference period."""
    p = (high + low + close) / 3
    r1 = 2 * p - low
    s1 = 2 * p - high
    r2 = p + (high - low)
    s2 = p - (high - low)
    return {"pivot": p, "r1": r1, "s1": s1, "r2": r2, "s2": s2}


def fibonacci_levels(swing_high: float, swing_low: float) -> dict[str, float]:
    """Fibonacci retracement levels from a swing (0% = low, 100% = high)."""
    diff = swing_high - swing_low
    return {
        "0.0%": swing_low,
        "23.6%": swing_low + 0.236 * diff,
        "38.2%": swing_low + 0.382 * diff,
        "50.0%": swing_low + 0.500 * diff,
        "61.8%": swing_low + 0.618 * diff,
        "78.6%": swing_low + 0.786 * diff,
        "100.0%": swing_high,
    }

    minus_di = 100 * minus_dm.ewm(alpha=1 / length, min_periods=length, adjust=False).mean() / atr_w.replace(0, np.nan)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    adx_line = dx.ewm(alpha=1 / length, min_periods=length, adjust=False).mean()
    return adx_line, plus_di, minus_di
