"""Unit tests for indicator math."""

import numpy as np
import pandas as pd
import pytest

from stock_bot.analysis import indicators as ind


@pytest.fixture
def series() -> pd.Series:
    np.random.seed(0)
    return pd.Series(np.cumsum(np.random.randn(300)) + 100,
                     index=pd.date_range("2024-01-01", periods=300))


def test_sma(series):
    s = ind.sma(series, 20)
    assert abs(s.iloc[-1] - series.iloc[-20:].mean()) < 1e-9
    assert s.isna().sum() == 19


def test_ema(series):
    e = ind.ema(series, 12)
    assert not e.isna().all()
    assert e.iloc[-1] != series.iloc[-1]  # EMA differs from price


def test_rsi_bounds(series):
    r = ind.rsi(series, 14)
    valid = r.dropna()
    assert (valid >= 0).all() and (valid <= 100).all()


def test_rsi_all_gains():
    up = pd.Series(range(1, 40), dtype=float)
    r = ind.rsi(up, 14)
    assert r.iloc[-1] == pytest.approx(100.0)


def test_macd(series):
    m, s, h = ind.macd(series)
    assert len(m) == len(series)
    # histogram = macd - signal
    idx = -1
    assert h.iloc[idx] == pytest.approx(m.iloc[idx] - s.iloc[idx])


def test_true_range_and_atr(series):
    h = series + 1
    l = series - 1
    tr = ind.true_range(h, l, series)
    assert not tr.dropna().empty
    a = ind.atr(h, l, series, 14)
    assert a.dropna().iloc[-1] > 0


def test_adx(series):
    h = series + 1
    l = series - 1
    adx_v, pdi, mdi = ind.adx(h, l, series, 14)
    assert not adx_v.dropna().empty
    assert (pdi.dropna() >= 0).all() and (mdi.dropna() >= 0).all()


def test_bollinger(series):
    u, m, l = ind.bollinger_bands(series, 20, 2.0)
    assert u.iloc[-1] > m.iloc[-1] > l.iloc[-1]


def test_pivot_points():
    p = ind.pivot_points(110, 90, 100)
    assert p["pivot"] == pytest.approx(100.0)
    assert p["r1"] > p["pivot"] > p["s1"]


def test_fibonacci():
    fib = ind.fibonacci_levels(200, 100)
    assert fib["0.0%"] == 100
    assert fib["100.0%"] == 200
    assert fib["61.8%"] == pytest.approx(161.8)
