"""
Integration adapter to run pricing normalization and ranking on scraped rows.

integrate_pricing(scraped_rows) -> {"offers": [...], "cheapest": ProductOffer}

Expected row keys (dict per row):
- site (str)
- price_text (str)
- currency_hint (optional str)
- shipping_text (optional str)
- tax_text (optional str)
- discount_text (optional str)
- rating (optional float)
- reviews (optional int)
- delivery_days (optional int)
- in_stock (optional bool)
- title (optional str)
- url (optional str)
- context (optional dict) -> for policy hooks

No network calls are made from core logic. CurrencyConverter uses a snapshot.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .compare import rank_offers
from .currency import CurrencyConverter
from .normalize import normalize
from .policies import apply_site_policies
from .types import ProductOffer, RawPrice


def integrate_pricing(scraped_rows: List[dict], target_currency: str = "INR") -> Dict[str, object]:
    converter = CurrencyConverter(base_currency=target_currency)
    offers: List[ProductOffer] = []
    for row in scraped_rows:
        raw = RawPrice(
            site=row.get("site", "unknown"),
            price_text=row.get("price_text"),
            currency_hint=row.get("currency_hint"),
            shipping_text=row.get("shipping_text"),
            tax_text=row.get("tax_text"),
            discount_text=row.get("discount_text"),
            rating=row.get("rating"),
            reviews=row.get("reviews"),
            delivery_days=row.get("delivery_days"),
            in_stock=row.get("in_stock", True),
            title=row.get("title"),
            url=row.get("url"),
            context=row.get("context", {}),
        )
        norm = normalize(raw, converter, target_currency)
        # Apply site-specific policies if any
        norm = apply_site_policies(raw.site, norm, raw.context)
        offer = ProductOffer(
            site=raw.site,
            title=raw.title,
            url=raw.url,
            normalized=norm,
            rating=raw.rating,
            reviews=raw.reviews,
            delivery_days=raw.delivery_days,
            in_stock=(raw.in_stock is not False),
            raw=raw,
        )
        offers.append(offer)

    sorted_offers = rank_offers(offers)
    cheapest = sorted_offers[0] if sorted_offers else None
    return {"offers": sorted_offers, "cheapest": cheapest}
