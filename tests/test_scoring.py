"""Unit tests for market detection, scoring bands, and recommendation logic."""

import numpy as np
import pandas as pd
import pytest

from stock_bot.analysis.fundamental import analyze_fundamental
from stock_bot.analysis.scoring import (make_recommendation,
                                        recommendation_label)
from stock_bot.analysis.technical import TechnicalResult, analyze_technical
from stock_bot.data.symbols import detect_market, normalize_symbol


# ------------------------------------------------------------- market detect
@pytest.mark.parametrize("sym,expected", [
    ("COMI.CA", "egx"), ("comi.ca", "egx"), ("SWDY.CA", "egx"),
    ("AAPL", "us"), ("msft", "us"), ("SPY", "etf"), ("qqq", "etf"),
])
def test_detect_market(sym, expected):
    assert detect_market(sym) == expected


def test_normalize_symbol():
    assert normalize_symbol("comi") == "COMI.CA"
    assert normalize_symbol("comi.ca") == "COMI.CA"
    assert normalize_symbol("aapl") == "AAPL"


# ------------------------------------------------------------- scoring bands
@pytest.mark.parametrize("score,label", [
    (85, "STRONG BUY"), (80, "STRONG BUY"), (70, "BUY"), (65, "BUY"),
    (50, "HOLD/WATCH"), (45, "HOLD/WATCH"), (30, "AVOID"), (0, "AVOID"),
])
def test_recommendation_bands(score, label):
    assert recommendation_label(score) == label


def _df(n=260, trend=1.0):
    np.random.seed(7)
    idx = pd.date_range("2025-01-01", periods=n, freq="B")
    close = pd.Series(100 + np.linspace(0, 30 * trend, n)
                      + np.cumsum(np.random.randn(n) * 0.8), index=idx)
    return pd.DataFrame({
        "Open": close.shift(1).fillna(close.iloc[0]),
        "High": close + pd.Series(np.abs(np.random.randn(n)) * 0.8, index=idx),
        "Low": close - pd.Series(np.abs(np.random.randn(n)) * 0.8, index=idx),
        "Close": close,
        "Volume": np.random.randint(500, 2000, n).astype(float),
    })


def test_technical_result_shape():
    res = analyze_technical(_df())
    assert 0 <= res.score <= 100
    assert res.last_close > 0
    assert res.atr_value > 0
    assert res.fib_levels["100.0%"] > res.fib_levels["0.0%"]


def test_recommendation_buy_has_trade_plan():
    tech = TechnicalResult(score=80, last_close=100, atr_value=2.0,
                           supports=[95.0], resistances=[110.0])
    fund = analyze_fundamental({"yf": {"trailingPE": 15, "returnOnEquity": 0.2}},
                               "us")
    rec = make_recommendation(tech, fund, "stock")
    assert rec.label in ("BUY", "STRONG BUY")
    assert rec.trade_plan is not None
    assert rec.trade_plan.stop_loss < tech.last_close
    assert rec.trade_plan.target1 > tech.last_close


def test_recommendation_hold_has_no_plan():
    tech = TechnicalResult(score=50, last_close=100, atr_value=2.0)
    fund = analyze_fundamental({"yf": {}}, "us")
    rec = make_recommendation(tech, fund, "stock")
    assert rec.label in ("HOLD/WATCH", "AVOID")
    assert rec.trade_plan is None


def test_egx_sparse_fundamentals_low_confidence():
    res = analyze_fundamental({"yf": {"trailingPE": 8}}, "egx")
    assert res.low_confidence
    assert res.coverage < 0.6
