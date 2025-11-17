"""
Datatypes for pricing pipeline: raw inputs from scrapers, parsed monetary values,
normalized price breakdowns, product offers, and ranking result container.

Design goals:
- Lightweight dataclasses with clear fields
- Use Decimal for precise money math with bankers rounding
- Keep optional fields for robustness when data is missing
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class RawPrice:
    """Raw scraped inputs for a single product offer.

    All text fields are as-scraped, potentially messy. Optional hints allow
    site adapters to pass extra context, e.g. detected currency code.
    """

    site: str
    price_text: Optional[str]
    currency_hint: Optional[str] = None
    shipping_text: Optional[str] = None
    tax_text: Optional[str] = None
    discount_text: Optional[str] = None

    rating: Optional[float] = None
    reviews: Optional[int] = None
    delivery_days: Optional[int] = None
    in_stock: Optional[bool] = True

    title: Optional[str] = None
    url: Optional[str] = None

    # Free-form context for policy hooks (e.g., thresholds, COD fees)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ParsedMonetary:
    """A parsed monetary-like value with currency code and notes.

    kind can be 'absolute' or 'percent' for discounts. For non-discount values,
    kind is always 'absolute'.
    """

    amount: Decimal
    currency: str
    raw_text: str = ""
    kind: str = "absolute"
    notes: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class NormalizedPrice:
    """All monetary components converted to a target currency with an effective total.

    - base, shipping, tax, discount are amounts in the target currency.
    - effective is clamped to >= 0.
    - breakdown contains human-readable debug notes for auditability.
    """

    base: ParsedMonetary
    shipping: ParsedMonetary
    tax: ParsedMonetary
    discount: ParsedMonetary
    effective: ParsedMonetary
    target_currency: str
    breakdown: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ProductOffer:
    """A product offer ready for comparison and display."""

    site: str
    title: Optional[str]
    url: Optional[str]
    normalized: NormalizedPrice

    rating: Optional[float] = None
    reviews: Optional[int] = None
    delivery_days: Optional[int] = None
    in_stock: bool = True

    # Keep original raw for traceability if needed by callers
    raw: Optional[RawPrice] = None


@dataclass(frozen=True)
class RankingResult:
    """Container for ranked offers and the cheapest one."""

    offers: List[ProductOffer]
    cheapest: Optional[ProductOffer]
