"""Unit tests for portfolio storage (cost averaging) and P/L math.

Uses an isolated in-memory SQLite DB (env var set before stock_bot imports;
python-dotenv does not override pre-set env vars).
"""

import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from stock_bot.bot.formatting import compute_pnl  # noqa: E402
from stock_bot.storage import repo  # noqa: E402
from stock_bot.storage.db import init_db  # noqa: E402

TG_ID = 999000111


def setup_module():
    init_db()
    repo.get_or_create_user(TG_ID, "tester")


def test_add_and_get_portfolio():
    assert repo.add_to_portfolio(TG_ID, "AAPL", "us", 10, 150.0)
    items = repo.get_portfolio(TG_ID)
    assert len(items) == 1
    assert items[0].symbol == "AAPL"
    assert items[0].quantity == 10
    assert items[0].buy_price == 150.0


def test_cost_averaging_on_second_buy():
    # +10 @ 170 -> average of (10@150, 10@170) = 20 @ 160
    repo.add_to_portfolio(TG_ID, "AAPL", "us", 10, 170.0)
    item = repo.get_portfolio(TG_ID)[0]
    assert item.quantity == 20
    assert item.buy_price == 160.0


def test_remove_from_portfolio():
    assert repo.remove_from_portfolio(TG_ID, "AAPL") is True
    assert repo.get_portfolio(TG_ID) == []
    assert repo.remove_from_portfolio(TG_ID, "AAPL") is False


def test_compute_pnl():
    pl_abs, pl_pct = compute_pnl(10, 100.0, 120.0)
    assert pl_abs == 200.0
    assert pl_pct == 20.0
    pl_abs, pl_pct = compute_pnl(5, 200.0, 180.0)
    assert pl_abs == -100.0
    assert pl_pct == -10.0


def test_portfolio_isolated_per_user():
    repo.add_to_portfolio(TG_ID, "COMI.CA", "egx", 100, 50.0)
    assert repo.get_portfolio(TG_ID + 1) == []  # another user sees nothing
    repo.remove_from_portfolio(TG_ID, "COMI.CA")
