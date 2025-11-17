"""
Normalization logic: compute effective prices in a common currency.

effective = clamp_min_0( base - discount + shipping + tax )

Notes:
- Conversion uses CurrencyConverter with a default target currency (INR).
- Missing shipping/tax are treated as 0.
- Breakdown retains readable notes for auditing/debugging.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import ROUND_HALF_EVEN, Decimal
from typing import Dict

from .currency import CurrencyConverter
from .parser import parse_raw_components
from .types import NormalizedPrice, ParsedMonetary, RawPrice


def _q2(x: Decimal) -> Decimal:
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)


def _as_target(pm: ParsedMonetary, conv: CurrencyConverter, target: str) -> ParsedMonetary:
    amt = conv.convert(pm.amount, pm.currency, target)
    return replace(pm, amount=amt, currency=target)


def normalize(raw: RawPrice, converter: CurrencyConverter, target_ccy: str = "INR") -> NormalizedPrice:
    base, shipping, tax, discount = parse_raw_components(raw)

    # Ensure shipping/tax default to 0 amounts when missing
    if shipping.amount is None:
        shipping = replace(shipping, amount=Decimal("0"))
    if tax.amount is None:
        tax = replace(tax, amount=Decimal("0"))

    # Convert base to target
    base_t = _as_target(base, converter, target_ccy)

    # Discount handling: percent values are % of base before conversion
    if discount.kind == "percent":
        disc_amt_base = _q2(base.amount * (discount.amount / Decimal("100")))
        discount = replace(discount, amount=disc_amt_base, currency=base.currency, kind="absolute")

    discount_t = _as_target(discount, converter, target_ccy)
    shipping_t = _as_target(shipping, converter, target_ccy)
    tax_t = _as_target(tax, converter, target_ccy)

    effective_amt = base_t.amount - discount_t.amount + shipping_t.amount + tax_t.amount
    if effective_amt < Decimal("0"):
        effective_amt = Decimal("0")
    effective_amt = _q2(effective_amt)
    effective = ParsedMonetary(amount=effective_amt, currency=target_ccy, raw_text="computed", kind="absolute")

    breakdown: Dict[str, str] = {
        "base": f"Base {base.amount} {base.currency} -> {base_t.amount} {target_ccy}",
        "discount": f"Discount {discount.amount} {discount.currency} -> {discount_t.amount} {target_ccy}",
        "shipping": f"Shipping {shipping.amount} {shipping.currency} -> {shipping_t.amount} {target_ccy}",
        "tax": f"Tax {tax.amount} {tax.currency} -> {tax_t.amount} {target_ccy}",
        "formula": "effective = base - discount + shipping + tax",
    }

    return NormalizedPrice(
        base=base_t,
        shipping=shipping_t,
        tax=tax_t,
        discount=discount_t,
        effective=effective,
        target_currency=target_ccy,
        breakdown=breakdown,
    )
