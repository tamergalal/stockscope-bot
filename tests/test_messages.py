"""Unit tests for message catalog & formatting helpers."""

from stock_bot.bot.messages import CATALOG, rec_emoji, score_emoji, t


def test_both_languages_have_same_keys():
    assert set(CATALOG["en"].keys()) == set(CATALOG["ar"].keys())


def test_translation_and_format():
    assert "StockScope" in t("welcome", "en")
    assert "AAPL" in t("watchlist_added", "en", symbol="AAPL")
    assert t("nonexistent_key", "en") == "nonexistent_key"


def test_score_emoji():
    assert score_emoji(80) == "🟢"
    assert score_emoji(50) == "🟡"
    assert score_emoji(20) == "🔴"


def test_rec_emoji():
    assert rec_emoji("BUY") == "🟢"
    assert rec_emoji("AVOID") == "🔴"
