"""Technical analysis engine: indicators, patterns, levels, 0-100 score."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import indicators as ind

WEIGHTS = {"trend": 25.0, "momentum": 25.0, "volatility": 15.0, "volume": 15.0, "price_action": 20.0}


@dataclass
class Signal:
    """One interpreted finding: name, bias in [-1, +1], explanation."""
    name: str
    bias: float
    note: str


@dataclass
class TechnicalResult:
    score: float
    signals: list[Signal] = field(default_factory=list)
    supports: list[float] = field(default_factory=list)
    resistances: list[float] = field(default_factory=list)
    fib_levels: dict[str, float] = field(default_factory=dict)
    atr_value: float = 0.0
    last_close: float = 0.0
    timeframe_consensus: dict[str, float] = field(default_factory=dict)


def _last(series: pd.Series, default: float = float("nan")) -> float:
    try:
        return float(series.dropna().iloc[-1])
    except (IndexError, ValueError, TypeError):
        return default


def detect_candlestick_patterns(df: pd.DataFrame) -> list[Signal]:
    """Detect common 1-3 bar candlestick patterns on the latest bars."""
    out: list[Signal] = []
    if len(df) < 3:
        return out
    o, h, l, c = df["Open"], df["High"], df["Low"], df["Close"]
    o1, c1 = o.iloc[-2], c.iloc[-2]
    o2, c2, h2, l2 = o.iloc[-1], c.iloc[-1], h.iloc[-1], l.iloc[-1]
    body2 = abs(c2 - o2)
    range2 = max(h2 - l2, 1e-12)
    body1 = abs(c1 - o1)

    if c1 < o1 and c2 > o2 and c2 >= o1 and o2 <= c1 and body2 > body1:
        out.append(Signal("Bullish Engulfing", 0.8, "Bulls engulfed prior bearish candle"))
    elif c1 > o1 and c2 < o2 and c2 <= o1 and o2 >= c1 and body2 > body1:
        out.append(Signal("Bearish Engulfing", -0.8, "Bears engulfed prior bullish candle"))

    lower_wick = min(o2, c2) - l2
    upper_wick = h2 - max(o2, c2)
    if lower_wick > 2 * body2 and upper_wick < body2:
        out.append(Signal("Hammer", 0.6, "Long lower wick - sellers rejected"))
    elif upper_wick > 2 * body2 and lower_wick < body2:
        out.append(Signal("Shooting Star", -0.6, "Long upper wick - buyers rejected"))

    if body2 <= 0.1 * range2:
        out.append(Signal("Doji", 0.0, "Indecision candle"))

    o0, c0 = o.iloc[-3], c.iloc[-3]
    if c0 < o0 and body2 > 0 and c2 > (o0 + c0) / 2 and abs(c1 - o1) < 0.4 * abs(o0 - c0):
        out.append(Signal("Morning Star", 0.8, "3-bar bullish reversal"))
    elif c0 > o0 and c2 < o2 and c2 < (o0 + c0) / 2 and abs(c1 - o1) < 0.4 * abs(o0 - c0):
        out.append(Signal("Evening Star", -0.8, "3-bar bearish reversal"))
    return out


def find_swing_levels(df: pd.DataFrame, window: int = 5) -> tuple[list[float], list[float]]:
    """Clustered swing lows (supports) and swing highs (resistances)."""
    highs, lows = df["High"].values, df["Low"].values
    supports: list[float] = []
    resistances: list[float] = []
    n = len(df)
    for i in range(window, n - window):
        if highs[i] == highs[i - window: i + window + 1].max():
            resistances.append(float(highs[i]))
        if lows[i] == lows[i - window: i + window + 1].min():
            supports.append(float(lows[i]))

    def cluster(levels: list[float], tol: float = 0.02) -> list[float]:
        if not levels:
            return []
        levels = sorted(levels)
        clusters: list[list[float]] = [[levels[0]]]
        for lv in levels[1:]:
            if abs(lv - clusters[-1][-1]) / clusters[-1][-1] <= tol:
                clusters[-1].append(lv)
            else:
                clusters.append([lv])
        return [float(np.mean(cl)) for cl in clusters][-4:]

    return cluster(supports), cluster(resistances)


def analyze_technical(df: pd.DataFrame, weekly_df: pd.DataFrame | None = None) -> TechnicalResult:
    """Full technical analysis on a daily OHLCV DataFrame (>=60 rows recommended)."""
    close, high, low, volume = df["Close"], df["High"], df["Low"], df["Volume"]
    last_close = float(close.iloc[-1])
    signals: list[Signal] = []

    # ---- TREND ----
    sma50, sma200 = ind.sma(close, 50), ind.sma(close, 200)
    s50, s200 = _last(sma50), _last(sma200)
    trend_score = 50.0
    if not np.isnan(s50):
        trend_score += 12 if last_close > s50 else -12
        signals.append(Signal("Price vs SMA50", 0.6 if last_close > s50 else -0.6,
                              "Price " + ("above" if last_close > s50 else "below") + f" 50-day avg ({s50:.2f})"))
    if not np.isnan(s200):
        trend_score += 8 if last_close > s200 else -8
        signals.append(Signal("Price vs SMA200", 0.5 if last_close > s200 else -0.5,
                              "Price " + ("above" if last_close > s200 else "below") + f" 200-day avg ({s200:.2f})"))
    if not (np.isnan(s50) or np.isnan(s200)):
        diff = (sma50 - sma200).dropna().tail(10)
        if len(diff) >= 2:
            if diff.iloc[0] < 0 and diff.iloc[-1] > 0:
                trend_score += 10
                signals.append(Signal("Golden Cross", 1.0, "SMA50 crossed above SMA200"))
            elif diff.iloc[0] > 0 and diff.iloc[-1] < 0:
                trend_score -= 10
                signals.append(Signal("Death Cross", -1.0, "SMA50 crossed below SMA200"))
            elif s50 > s200:
                trend_score += 5
    adx_v, pdi, mdi = ind.adx(high, low, close)
    adx_last, pdi_last, mdi_last = _last(adx_v), _last(pdi), _last(mdi)
    if not np.isnan(adx_last):
        if adx_last > 25 and pdi_last > mdi_last:
            trend_score += 8
            signals.append(Signal("ADX", 0.7, f"Strong uptrend (ADX {adx_last:.0f})"))
        elif adx_last > 25 and mdi_last > pdi_last:
            trend_score -= 8
            signals.append(Signal("ADX", -0.7, f"Strong downtrend (ADX {adx_last:.0f})"))
        else:
            signals.append(Signal("ADX", 0.0, f"Weak trend / ranging (ADX {adx_last:.0f})"))
    trend_score = float(np.clip(trend_score, 0, 100))

    # ---- MOMENTUM ----
    momentum_score = 50.0
    rsi_v = ind.rsi(close)
    rsi_last = _last(rsi_v)
    if not np.isnan(rsi_last):
        if rsi_last >= 70:
            momentum_score -= 10
            signals.append(Signal("RSI", -0.5, f"Overbought ({rsi_last:.0f})"))
        elif rsi_last <= 30:
            momentum_score += 12
            signals.append(Signal("RSI", 0.8, f"Oversold ({rsi_last:.0f}) - rebound candidate"))
        elif rsi_last > 50:
            momentum_score += 6
            signals.append(Signal("RSI", 0.3, f"Bullish momentum zone ({rsi_last:.0f})"))
        else:
            momentum_score -= 6
            signals.append(Signal("RSI", -0.3, f"Bearish momentum zone ({rsi_last:.0f})"))
        if len(close) > 25:
            p_now, p_then = close.iloc[-1], close.iloc[-21]
            r_now, r_then = rsi_v.iloc[-1], rsi_v.iloc[-21]
            if not (np.isnan(r_now) or np.isnan(r_then)):
                if p_now < p_then and r_now > r_then:
                    momentum_score += 8
                    signals.append(Signal("RSI Divergence", 0.8, "Bullish divergence"))
                elif p_now > p_then and r_now < r_then:
                    momentum_score -= 8
                    signals.append(Signal("RSI Divergence", -0.8, "Bearish divergence"))
    macd_l, macd_s, macd_h = ind.macd(close)
    m_last, s_last, h_last = _last(macd_l), _last(macd_s), _last(macd_h)
    h_prev = _last(macd_h.iloc[:-1])
    if not (np.isnan(m_last) or np.isnan(s_last)):
        if m_last > s_last and h_prev <= 0 < h_last:
            momentum_score += 10
            signals.append(Signal("MACD", 0.9, "Fresh bullish crossover"))
        elif m_last < s_last and h_prev >= 0 > h_last:
            momentum_score -= 10
            signals.append(Signal("MACD", -0.9, "Fresh bearish crossover"))
        elif m_last > s_last:
            momentum_score += 6
            signals.append(Signal("MACD", 0.5, "MACD above signal"))
        else:
            momentum_score -= 6
            signals.append(Signal("MACD", -0.5, "MACD below signal"))
    k_v, _d_v = ind.stoch(high, low, close)
    k_last = _last(k_v)
    if not np.isnan(k_last):
        if k_last <= 20:
            momentum_score += 5
        elif k_last >= 80:
            momentum_score -= 5
    momentum_score = float(np.clip(momentum_score, 0, 100))


    # ---- VOLATILITY ----
    vol_score = 50.0
    atr_v = ind.atr(high, low, close)
    atr_last = _last(atr_v, 0.0)
    bb_u, bb_m, bb_l = ind.bollinger_bands(close)
    bu, bl = _last(bb_u), _last(bb_l)
    if not (np.isnan(bu) or np.isnan(bl)) and bu > bl:
        pct_b = (last_close - bl) / (bu - bl)
        if pct_b < 0.05:
            vol_score += 15
            signals.append(Signal("Bollinger %B", 0.7, "At lower band - bounce candidate"))
        elif pct_b > 0.95:
            vol_score -= 8
            signals.append(Signal("Bollinger %B", -0.4, "Stretched above upper band"))
        width = (bb_u - bb_l) / bb_m
        recent_w = width.dropna().tail(120)
        if len(recent_w) > 30 and recent_w.iloc[-1] <= recent_w.quantile(0.25):
            vol_score += 8
            signals.append(Signal("BB Squeeze", 0.4, "Volatility squeeze - big move brewing"))
    vol_score = float(np.clip(vol_score, 0, 100))

    # ---- VOLUME ----
    volume_score = 50.0
    if volume is not None and volume.sum() > 0:
        vol_avg20 = volume.rolling(20).mean()
        v_last, v_avg = float(volume.iloc[-1]), _last(vol_avg20)
        if not np.isnan(v_avg) and v_avg > 0:
            price_up = bool(close.iloc[-1] > close.iloc[-2]) if len(close) > 1 else True
            if v_last > 1.5 * v_avg and price_up:
                volume_score += 18
                signals.append(Signal("Volume Spike", 0.8, f"Volume {v_last / v_avg:.1f}x avg on up day"))
            elif v_last > 1.5 * v_avg and not price_up:
                volume_score -= 15
                signals.append(Signal("Volume Spike", -0.7, f"Volume {v_last / v_avg:.1f}x avg on down day"))
        obv_v = ind.obv(close, volume)
        if len(obv_v) > 20:
            obv_trend = obv_v.iloc[-1] - obv_v.iloc[-20]
            price_trend = close.iloc[-1] - close.iloc[-20]
            if obv_trend > 0 and price_trend > 0:
                volume_score += 10
                signals.append(Signal("OBV", 0.5, "OBV rising with price - accumulation"))
            elif obv_trend < 0 < price_trend:
                volume_score -= 12
                signals.append(Signal("OBV", -0.6, "Price up, OBV down - weak rally"))
            elif obv_trend > 0 > price_trend:
                volume_score += 10
                signals.append(Signal("OBV", 0.6, "Price down, OBV up - quiet accumulation"))
    volume_score = float(np.clip(volume_score, 0, 100))

    # ---- PRICE ACTION ----
    pa_score = 50.0
    supports, resistances = find_swing_levels(df)
    patterns = detect_candlestick_patterns(df)
    signals.extend(patterns)
    for s in patterns:
        pa_score += s.bias * 10
    nearest_sup = max([x for x in supports if x < last_close], default=None)
    nearest_res = min([x for x in resistances if x > last_close], default=None)
    if nearest_sup and atr_last > 0 and (last_close - nearest_sup) < atr_last:
        pa_score += 12
        signals.append(Signal("Near Support", 0.7, f"Bouncing near support {nearest_sup:.2f}"))
    if nearest_res and atr_last > 0 and (nearest_res - last_close) < atr_last:
        pa_score -= 10
        signals.append(Signal("Near Resistance", -0.6, f"Testing resistance {nearest_res:.2f}"))
    if len(high) > 55:
        prior_high = high.iloc[-51:-1].max()
        prior_low = low.iloc[-51:-1].min()
        if last_close > prior_high:
            pa_score += 12
            signals.append(Signal("Breakout", 0.9, f"Breakout above 50-day high ({prior_high:.2f})"))
        elif last_close < prior_low:
            pa_score -= 12
            signals.append(Signal("Breakdown", -0.9, f"Breakdown below 50-day low ({prior_low:.2f})"))
    pa_score = float(np.clip(pa_score, 0, 100))

    swing_high, swing_low = float(high.max()), float(low.min())
    fib = ind.fibonacci_levels(swing_high, swing_low)

    score = (trend_score * WEIGHTS["trend"] + momentum_score * WEIGHTS["momentum"]
             + vol_score * WEIGHTS["volatility"] + volume_score * WEIGHTS["volume"]
             + pa_score * WEIGHTS["price_action"]) / 100.0
    score = float(round(np.clip(score, 0, 100), 1))

    consensus: dict[str, float] = {"daily": score}
    if weekly_df is not None and len(weekly_df) > 30:
        wclose = weekly_df["Close"]
        ws30 = _last(ind.sma(wclose, 30))
        w_last = float(wclose.iloc[-1])
        w_score = 50.0
        if not np.isnan(ws30):
            w_score += 20 if w_last > ws30 else -20
        w_rsi = _last(ind.rsi(wclose))
        if not np.isnan(w_rsi):
            w_score += 15 if 50 < w_rsi < 70 else (-10 if w_rsi >= 70 else (-15 if w_rsi < 40 else 5))
        consensus["weekly"] = float(round(np.clip(w_score, 0, 100), 1))

    return TechnicalResult(score=score, signals=signals, supports=supports, resistances=resistances,
                           fib_levels=fib, atr_value=float(atr_last or 0.0), last_close=last_close,
                           timeframe_consensus=consensus)

