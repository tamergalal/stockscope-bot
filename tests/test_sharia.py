"""Unit tests for Sharia screening and the glossary."""

from stock_bot.analysis import sharia
from stock_bot.bot.glossary import (GLOSSARY, all_terms_index, explain_term,
                                    explain_used_terms)


# ------------------------------------------------------------ stock screens
def test_conventional_bank_fails_activity_screen():
    info = {"sector": "Financial Services", "industry": "Banks - Regional",
            "marketCap": 100e9, "totalDebt": 5e9, "totalCash": 2e9}
    res = sharia.screen_stock("COMI.CA", info)
    assert res.status == sharia.STATUS_NON_COMPLIANT


def test_islamic_bank_whitelisted():
    info = {"sector": "Financial Services", "industry": "Banks - Regional",
            "marketCap": 50e9, "totalDebt": 1e9, "totalCash": 1e9}
    res = sharia.screen_stock("ADIB.CA", info)
    assert res.status == sharia.STATUS_COMPLIANT


def test_high_debt_fails_ratio_screen():
    info = {"sector": "Technology", "industry": "Software",
            "marketCap": 10e9, "totalDebt": 5e9, "totalCash": 0.5e9}
    res = sharia.screen_stock("XXXX", info)
    assert res.status == sharia.STATUS_NON_COMPLIANT
    assert any("debt" in r.lower() for r in res.reasons)


def test_clean_company_passes():
    info = {"sector": "Technology", "industry": "Semiconductors",
            "marketCap": 100e9, "totalDebt": 10e9, "totalCash": 5e9}
    res = sharia.screen_stock("NVDA", info)
    assert res.status == sharia.STATUS_COMPLIANT
    assert res.badge


def test_missing_data_is_doubtful_not_crash():
    res = sharia.screen_stock("UNKNOWN", {})
    assert res.status == sharia.STATUS_DOUBTFUL


def test_known_conventional_financials_blacklisted():
    # Even with NO sector/industry data (common for EGX on free providers)
    for sym in ("COMI.CA", "HRHO.CA", "JPM", "V"):
        res = sharia.screen_stock(sym, {})
        assert res.status == sharia.STATUS_NON_COMPLIANT, sym


# -------------------------------------------------------------- ETF screens
def test_known_islamic_etf_passes():
    assert sharia.screen_etf("HLAL", {}).status == sharia.STATUS_COMPLIANT
    assert sharia.screen_etf("SPSK", {}).status == sharia.STATUS_COMPLIANT


def test_bond_etf_fails():
    info = {"longName": "iShares 20+ Year Treasury Bond ETF", "category": "Bond"}
    assert sharia.screen_etf("TLT", info).status == sharia.STATUS_NON_COMPLIANT


def test_gold_etf_is_doubtful():
    info = {"longName": "SPDR Gold Shares", "category": "Commodities"}
    assert sharia.screen_etf("GLD", info).status == sharia.STATUS_DOUBTFUL


def test_generic_equity_etf_is_doubtful():
    info = {"longName": "SPDR S&P 500 ETF Trust", "category": "Large Blend"}
    assert sharia.screen_etf("SPY", info).status == sharia.STATUS_DOUBTFUL


# ------------------------------------------------------------------ glossary
def test_glossary_language_parity():
    for term, entry in GLOSSARY.items():
        assert "en" in entry and "ar" in entry, f"{term} missing a language"


def test_explain_term():
    assert "Relative Strength" in explain_term("RSI", "en")
    assert "القوة النسبية" in explain_term("RSI", "ar")
    assert explain_term("NO_SUCH_TERM") is None


def test_explain_used_terms():
    hints = ["RSI", "MACD", "P/E"]
    out = explain_used_terms(hints, "en")
    assert any("RSI" in line for line in out)
    assert any("MACD" in line for line in out)


def test_all_terms_index_contains_key_terms():
    idx = all_terms_index("en")
    for term in ("RSI", "P/E", "Sharia", "Sukuk"):
        assert term in idx
