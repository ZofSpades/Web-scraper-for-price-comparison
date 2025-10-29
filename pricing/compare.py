"""
Offer comparison and ranking.

Sort key:
1) effective.amount ascending
2) rating descending
3) delivery_days ascending (None last)
4) in_stock True before False
5) reviews count descending

Stable and deterministic across runs.
"""

from __future__ import annotations

from decimal import Decimal
from typing import List

from .types import ProductOffer


def _delivery_key(days):
    return days if isinstance(days, int) else 10**9


def _rating_key(r):
    # Higher first -> negative for ascending sort; None treated as 0
    return -(r if isinstance(r, (int, float)) else 0.0)


def _reviews_key(n):
    # Higher first -> negative for ascending sort; None treated as 0
    return -(n if isinstance(n, int) else 0)


def rank_offers(offers: List[ProductOffer]) -> List[ProductOffer]:
    return sorted(
        offers,
        key=lambda o: (
            o.normalized.effective.amount,  # Decimal supports ordering
            _rating_key(o.rating),
            0 if (o.in_stock is True) else 1,
            _delivery_key(o.delivery_days),
            _reviews_key(o.reviews),
        ),
    )
