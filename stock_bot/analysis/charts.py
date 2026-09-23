"""Candlestick chart rendering with mplfinance (MA20/50, Bollinger, volume, RSI)."""

from __future__ import annotations

import io

import matplotlib
matplotlib.use("Agg")  # headless

import mplfinance as mpf
import pandas as pd

from . import indicators as ind


def render_chart(df: pd.DataFrame, symbol: str, currency: str = "") -> bytes:
    """Render a candlestick chart PNG and return it as bytes.

    Panels: price + MA20/MA50 + Bollinger (main), Volume, RSI(14).
    """
    data = df.tail(180).copy()  # last ~6 months for readability
    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)

    close = data["Close"]
    ma20 = ind.sma(close, 20)
    ma50 = ind.sma(close, 50)
    bb_u, bb_m, bb_l = ind.bollinger_bands(close)
    rsi_v = ind.rsi(close)

    apds = [
        mpf.make_addplot(ma20, color="orange", width=1.0),
        mpf.make_addplot(ma50, color="blue", width=1.0),
        mpf.make_addplot(bb_u, color="gray", width=0.7, linestyle="--"),
        mpf.make_addplot(bb_l, color="gray", width=0.7, linestyle="--"),
        mpf.make_addplot(rsi_v, panel=2, color="purple", ylabel="RSI", width=1.0),
    ]

    title = f"{symbol}" + (f" ({currency})" if currency else "")
    style = mpf.make_mpf_style(base_mpf_style="yahoo", gridstyle=":", y_on_right=False)
    buf = io.BytesIO()
    mpf.plot(
        data, type="candle", style=style, addplot=apds, volume=True,
        panel_ratios=(3, 1, 1.2), title=title, ylabel="Price", ylabel_lower="Volume",
        figsize=(11, 7.5), tight_layout=True, savefig=dict(fname=buf, dpi=110),
    )
    buf.seek(0)
    return buf.read()
