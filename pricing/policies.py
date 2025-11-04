"""
Site-specific pricing policy adjustments hook.

Examples supported out-of-the-box:
- Free shipping threshold (context: {"free_shipping_threshold": 500.0})
- Cash-on-delivery fee (context: {"cod_fee": 50.0, "cod": True})

Assumptions:
- Thresholds/fees are specified in the target currency (after normalization).
- This module only mutates the already-normalized amounts and recomputes effective.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Dict

from .types import NormalizedPrice, ParsedMonetary


def _q2(x: Decimal) -> Decimal:
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)


def _recompute_effective(np: NormalizedPrice) -> NormalizedPrice:
    eff = np.base.amount - np.discount.amount + np.shipping.amount + np.tax.amount
    if eff < Decimal("0"):
        eff = Decimal("0")
    eff = _q2(eff)
    effective = ParsedMonetary(amount=eff, currency=np.target_currency, raw_text="policy", kind="absolute")
    return replace(np, effective=effective)


def apply_site_policies(site: str, normalized_price: NormalizedPrice, context: Dict) -> NormalizedPrice:
    np = normalized_price
    notes = []
    # Free shipping threshold
    thr = context.get("free_shipping_threshold")
    if isinstance(thr, (int, float)):
        thr_dec = Decimal(str(thr))
        if np.base.amount >= thr_dec and np.shipping.amount > Decimal("0"):
            np = replace(np, shipping=replace(np.shipping, amount=Decimal("0")))
            np.breakdown["policy:shipping"] = f"Free shipping applied (threshold {thr_dec} {np.target_currency})"
    # COD fee
    if context.get("cod") and isinstance(context.get("cod_fee"), (int, float)):
        fee = _q2(Decimal(str(context["cod_fee"])) )
        np = replace(np, tax=replace(np.tax, amount=_q2(np.tax.amount + fee)))
        np.breakdown["policy:cod"] = f"COD fee +{fee} {np.target_currency}"

    # Recompute effective after policy adjustments
    np = _recompute_effective(np)
    return np
