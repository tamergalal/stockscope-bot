"""Repository layer: user, watchlist, alerts, recommendation log CRUD."""

from __future__ import annotations

from sqlalchemy import select

from .db import (Alert, PortfolioItem, RecommendationLog, SessionLocal, User,
                 WatchlistItem)


def get_or_create_user(telegram_id: int, username: str | None = None) -> User:
    with SessionLocal() as s:
        user = s.execute(select(User).where(User.telegram_id == telegram_id)).scalar_one_or_none()
        if user is None:
            user = User(telegram_id=telegram_id, username=username)
            s.add(user)
            s.commit()
            s.refresh(user)
        return user


def update_user_prefs(telegram_id: int, **fields) -> None:
    with SessionLocal() as s:
        user = s.execute(select(User).where(User.telegram_id == telegram_id)).scalar_one_or_none()
        if user:
            for k, v in fields.items():
                if hasattr(user, k):
                    setattr(user, k, v)
            s.commit()


def get_user(telegram_id: int) -> User | None:
    with SessionLocal() as s:
        return s.execute(select(User).where(User.telegram_id == telegram_id)).scalar_one_or_none()


def _user_pk(session, telegram_id: int) -> int | None:
    u = session.execute(select(User).where(User.telegram_id == telegram_id)).scalar_one_or_none()
    return u.id if u else None


def add_to_watchlist(telegram_id: int, symbol: str, market: str) -> bool:
    with SessionLocal() as s:
        uid = _user_pk(s, telegram_id)
        if uid is None:
            return False
        exists = s.execute(
            select(WatchlistItem).where(
                WatchlistItem.user_id == uid, WatchlistItem.symbol == symbol)
        ).scalar_one_or_none()
        if exists:
            return False
        s.add(WatchlistItem(user_id=uid, symbol=symbol, market=market))
        s.commit()
        return True


def remove_from_watchlist(telegram_id: int, symbol: str) -> bool:
    with SessionLocal() as s:
        uid = _user_pk(s, telegram_id)
        if uid is None:
            return False
        item = s.execute(
            select(WatchlistItem).where(
                WatchlistItem.user_id == uid, WatchlistItem.symbol == symbol)
        ).scalar_one_or_none()
        if item:
            s.delete(item)
            s.commit()
            return True
        return False


def get_watchlist(telegram_id: int) -> list[WatchlistItem]:
    with SessionLocal() as s:
        uid = _user_pk(s, telegram_id)
        if uid is None:
            return []
        return list(s.execute(
            select(WatchlistItem).where(WatchlistItem.user_id == uid)
        ).scalars().all())


def add_alert(telegram_id: int, symbol: str, condition: str, value: float) -> bool:
    with SessionLocal() as s:
        uid = _user_pk(s, telegram_id)
        if uid is None:
            return False
        s.add(Alert(user_id=uid, symbol=symbol, condition=condition, value=value, active=True))
        s.commit()
        return True


def get_active_alerts() -> list[Alert]:
    with SessionLocal() as s:
        return list(s.execute(select(Alert).where(Alert.active.is_(True))).scalars().all())


def deactivate_alert(alert_id: int) -> None:
    with SessionLocal() as s:
        alert = s.get(Alert, alert_id)
        if alert:
            alert.active = False
            s.commit()


def get_user_by_pk(user_pk: int) -> User | None:
    with SessionLocal() as s:
        return s.get(User, user_pk)


def get_digest_users() -> list[User]:
    with SessionLocal() as s:
        return list(s.execute(select(User).where(User.digest_enabled.is_(True))).scalars().all())


# ------------------------------------------------------------------ portfolio
def add_to_portfolio(telegram_id: int, symbol: str, market: str,
                     quantity: float, buy_price: float) -> bool:
    """Add a position. If the symbol already exists, average the cost basis."""
    with SessionLocal() as s:
        uid = _user_pk(s, telegram_id)
        if uid is None:
            return False
        existing = s.execute(
            select(PortfolioItem).where(
                PortfolioItem.user_id == uid, PortfolioItem.symbol == symbol)
        ).scalar_one_or_none()
        if existing:
            total_qty = existing.quantity + quantity
            existing.buy_price = round(
                (existing.quantity * existing.buy_price + quantity * buy_price) / total_qty, 4)
            existing.quantity = total_qty
        else:
            s.add(PortfolioItem(user_id=uid, symbol=symbol, market=market,
                                quantity=quantity, buy_price=buy_price))
        s.commit()
        return True


def remove_from_portfolio(telegram_id: int, symbol: str) -> bool:
    with SessionLocal() as s:
        uid = _user_pk(s, telegram_id)
        if uid is None:
            return False
        item = s.execute(
            select(PortfolioItem).where(
                PortfolioItem.user_id == uid, PortfolioItem.symbol == symbol)
        ).scalar_one_or_none()
        if item:
            s.delete(item)
            s.commit()
            return True
        return False


def get_portfolio(telegram_id: int) -> list[PortfolioItem]:
    with SessionLocal() as s:
        uid = _user_pk(s, telegram_id)
        if uid is None:
            return []
        return list(s.execute(
            select(PortfolioItem).where(PortfolioItem.user_id == uid)
        ).scalars().all())


def log_recommendation(symbol: str, market: str, composite: float, label: str) -> None:
    with SessionLocal() as s:
        s.add(RecommendationLog(symbol=symbol, market=market, composite=composite, label=label))
        s.commit()
