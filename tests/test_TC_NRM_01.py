from decimal import Decimal

from pricing.currency import CurrencyConverter
from pricing.normalize import normalize
from pricing.types import RawPrice


def test_TC_NRM_01():
    raw = RawPrice(site="X", price_text="₹1,000", currency_hint="INR", title="T")
    conv = CurrencyConverter(base_currency="INR")
    norm = normalize(raw, conv, target_ccy="INR")
    assert norm.effective.amount == Decimal("1000.00")
