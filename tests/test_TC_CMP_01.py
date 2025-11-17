from decimal import Decimal

from pricing.compare import rank_offers
from pricing.types import NormalizedPrice, ParsedMonetary, ProductOffer


def test_TC_CMP_01():
    p1 = ProductOffer(
        site="A",
        title="A",
        url="#",
        normalized=NormalizedPrice(
            base=ParsedMonetary(Decimal("100"), "INR"),
            shipping=ParsedMonetary(Decimal("0"), "INR"),
            tax=ParsedMonetary(Decimal("0"), "INR"),
            discount=ParsedMonetary(Decimal("0"), "INR"),
            effective=ParsedMonetary(Decimal("100"), "INR"),
            target_currency="INR",
        ),
    )
    p2 = ProductOffer(
        site="B",
        title="B",
        url="#",
        normalized=NormalizedPrice(
            base=ParsedMonetary(Decimal("90"), "INR"),
            shipping=ParsedMonetary(Decimal("0"), "INR"),
            tax=ParsedMonetary(Decimal("0"), "INR"),
            discount=ParsedMonetary(Decimal("0"), "INR"),
            effective=ParsedMonetary(Decimal("90"), "INR"),
            target_currency="INR",
        ),
    )
    ranked = rank_offers([p1, p2])
    assert ranked[0].site == "B"
