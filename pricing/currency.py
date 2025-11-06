"""
Currency conversion utilities with a pluggable rate fetcher and TTL cache.

Design:
- Default base currency is INR.
- A safe built-in snapshot is provided; no network calls in core logic.
- Deterministic Decimal math with bankers rounding to 2 decimals for outputs.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Callable, Dict, Optional, Tuple


def _q2(x: Decimal) -> Decimal:
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)


# Fallback snapshot: approximate rates relative to INR
# Keys are ISO currency codes; values are INR per 1 unit of currency.
_DEFAULT_INR_RATES: Dict[str, Decimal] = {
    "INR": Decimal("1"),
    "USD": Decimal("83.00"),
    "EUR": Decimal("90.00"),
    "GBP": Decimal("100.00"),
    "JPY": Decimal("0.55"),
    "AED": Decimal("22.60"),
    "CAD": Decimal("61.00"),
    "AUD": Decimal("53.00"),
}


RateFetcher = Callable[[str, str], Decimal]


def _snapshot_fetcher(from_ccy: str, to_ccy: str) -> Decimal:
    """Fetch conversion rate using the embedded snapshot via INR cross rates.

    Returns multiplier to convert from from_ccy -> to_ccy.
    """
    f = from_ccy.upper()
    t = to_ccy.upper()
    if f == t:
        return Decimal("1")
    # Cross via INR
    if f in _DEFAULT_INR_RATES and t in _DEFAULT_INR_RATES:
        inr_per_f = _DEFAULT_INR_RATES[f]
        inr_per_t = _DEFAULT_INR_RATES[t]
        # from f to INR to t
        # amount_in_t = amount_in_f * (inr_per_f / inr_per_t)
        return (inr_per_f / inr_per_t)
    # Unknown currencies: fallback to 1:1 to avoid crashes (documented behavior)
    return Decimal("1")


@dataclass
class CurrencyConverter:
    """Currency converter with TTL caching and pluggable fetcher.

    fetcher: function returning rate multiplier from -> to.
    ttl_seconds: time-to-live for cached quotes.
    """

    base_currency: str = "INR"
    fetcher: RateFetcher = field(default_factory=lambda: _snapshot_fetcher)
    ttl_seconds: int = 3600
    _cache: Dict[Tuple[str, str], Tuple[float, Decimal]] = field(default_factory=dict)

    def _get_rate(self, from_ccy: str, to_ccy: str) -> Decimal:
        k = (from_ccy.upper(), to_ccy.upper())
        now = time.time()
        if k in self._cache:
            ts, rate = self._cache[k]
            if now - ts < self.ttl_seconds:
                return rate
        rate = self.fetcher(k[0], k[1])
        self._cache[k] = (now, Decimal(rate))
        return Decimal(rate)

    def convert(self, amount: Decimal, from_ccy: str, to_ccy: Optional[str] = None) -> Decimal:
        """Convert amount from from_ccy to to_ccy using Decimal math.

        Rounds to 2 decimals using bankers rounding. If currencies are unknown,
        uses a conservative identity rate (documented) to avoid crashing.
        """
        to = (to_ccy or self.base_currency).upper()
        f = from_ccy.upper()
        rate = self._get_rate(f, to)
        return _q2((amount or Decimal("0")) * rate)
