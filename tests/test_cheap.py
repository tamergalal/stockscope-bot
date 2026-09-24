"""Tests for the /cheap scan: Sharia-compliant stocks under a price cap."""

from __future__ import annotations

import asyncio
import string
from types import SimpleNamespace

from stock_bot.analysis.service import AnalysisService
from stock_bot.bot.messages import CATALOG
from stock_bot.config import settings


def _report(symbol, price, status, composite):
    return SimpleNamespace(
        symbol=symbol, price=price, currency="USD",
        sharia=SimpleNamespace(status=status),
        rec=SimpleNamespace(composite=composite, label="BUY"))


def _service_with(reports):
    svc = AnalysisService()

    async def fake_many(symbols, concurrency=5):
        return reports

    svc._analyze_many = fake_many
    return svc


def test_scan_cheap_filters_price_and_compliance():
    svc = _service_with([
        _report("CHEAP_OK", 8.0, "COMPLIANT", 70),
        _report("CHEAP_DOUBT", 9.0, "DOUBTFUL", 60),
        _report("PRICEY", 25.0, "COMPLIANT", 90),
        _report("HARAM", 5.0, "NON_COMPLIANT", 95),
    ])
    out = asyncio.run(svc.scan_cheap("us", max_price=10.0))
    symbols = [r.symbol for r in out]
    assert "CHEAP_OK" in symbols and "CHEAP_DOUBT" in symbols
    assert "PRICEY" not in symbols      # over the price cap
    assert "HARAM" not in symbols       # fails the Sharia screen


def test_scan_cheap_sorted_by_score_desc():
    svc = _service_with([
        _report("LOW", 5.0, "COMPLIANT", 50),
        _report("HIGH", 5.0, "COMPLIANT", 80),
    ])
    out = asyncio.run(svc.scan_cheap("us", max_price=10.0))
    assert [r.symbol for r in out] == ["HIGH", "LOW"]


def test_scan_cheap_custom_threshold():
    svc = _service_with([_report("MID", 30.0, "COMPLIANT", 70)])
    assert asyncio.run(svc.scan_cheap("egx", max_price=20.0)) == []
    assert len(asyncio.run(svc.scan_cheap("egx", max_price=50.0))) == 1


def test_cheap_defaults_from_settings():
    assert settings.cheap_max_price_egx == 50.0
    assert settings.cheap_max_price_us == 10.0


def test_cheap_threshold_helper():
    from stock_bot.bot.handlers import _cheap_threshold
    assert _cheap_threshold("egx", None) == settings.cheap_max_price_egx
    assert _cheap_threshold("us", None) == settings.cheap_max_price_us
    assert _cheap_threshold("egx", "30") == 30.0
    assert _cheap_threshold("us", "abc") is None
    assert _cheap_threshold("us", "-5") is None


def test_cheap_i18n_parity():
    """Every cheap_* message exists in EN and AR with identical placeholders."""
    cheap_keys = [k for k in CATALOG["en"] if k.startswith("cheap")]
    assert cheap_keys, "expected cheap_* messages in the EN catalog"
    for key in cheap_keys:
        assert key in CATALOG["ar"], key
        en_fields = {f for _, f, _, _ in string.Formatter().parse(CATALOG["en"][key]) if f}
        ar_fields = {f for _, f, _, _ in string.Formatter().parse(CATALOG["ar"][key]) if f}
        assert en_fields == ar_fields, key
