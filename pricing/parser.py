"""
Parsing utilities to extract currency and numeric amounts from messy price text.

Features:
- Currency detection from symbols and codes (₹, Rs, INR, $, USD, €, EUR, £, GBP,
  ¥, JPY, AED, د.إ, CAD, AUD, etc.).
- Locale-aware numeric parsing for IN/US/EU formats, e.g.:
  - "₹ 1,29,999" (IN)
  - "$1,299.99" (US)
  - "1.299,99 €" (EU)
  - "1 299,99 €" (EU with space separators)
- Discount parsing for percentage ("10% OFF") and absolute ("-₹200").

Notes:
- Outputs use Decimal for precise arithmetic.
- This module is pure (no network calls), deterministic, and unit-testable.
"""

from __future__ import annotations

import re
from dataclasses import replace
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
from typing import Optional, Tuple

from .types import ParsedMonetary, RawPrice


# Mapping of currency indicators (symbols, codes, common prefixes) to ISO codes
_CURRENCY_MAP = {
    # INR variants
    "₹": "INR",
    "rs": "INR",
    "rs.": "INR",
    "inr": "INR",
    # USD variants
    "$": "USD",
    "usd": "USD",
    "us$": "USD",
    # EUR variants
    "€": "EUR",
    "eur": "EUR",
    # GBP variants
    "£": "GBP",
    "gbp": "GBP",
    # JPY variants
    "¥": "JPY",
    "jpy": "JPY",
    # AED variants
    "aed": "AED",
    "د.إ": "AED",
    "د": "AED",
    # CAD/AUD variants
    "cad": "CAD",
    "c$": "CAD",
    "aud": "AUD",
    "a$": "AUD",
}


_NBSP = "\xa0"
_THINSP = "\u2009"


def _bankers_round_2(dec: Decimal) -> Decimal:
    return dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)


def detect_currency(text: Optional[str], hint: Optional[str] = None) -> str:
    """Detect currency code from a hint or from the given text.

    Returns 'UNK' if unknown.
    """
    if hint:
        h = hint.strip().lower()
        return _CURRENCY_MAP.get(h, h.upper())
    if not text:
        return "UNK"
    t = text.strip().lower()
    # Quick checks for known symbols/codes anywhere in the string
    # Prefer longer tokens first (e.g., 'c$' before '$')
    for key in sorted(_CURRENCY_MAP.keys(), key=len, reverse=True):
        code = _CURRENCY_MAP[key]
        if key in t:
            return code
    # Word-boundary match for 3-letter codes
    m = re.search(r"\b([a-z]{3})\b", t)
    if m:
        return _CURRENCY_MAP.get(m.group(1), m.group(1).upper())
    return "UNK"


def _strip_currency_and_keep_separators(text: str) -> str:
    # Remove currency words/symbols but keep digits, separators, minus sign
    t = text.replace(_NBSP, " ").replace(_THINSP, " ")
    # Remove known currency tokens
    for token in sorted(_CURRENCY_MAP.keys(), key=len, reverse=True):
        t = t.replace(token, " ")
        t = t.replace(token.upper(), " ")
        t = t.replace(token.capitalize(), " ")
    # Remove other letters
    t = re.sub(r"[A-Za-z]", " ", t)
    # Keep digits, separators, spaces, and hyphen
    t = re.sub(r"[^0-9,.'\-\s]", " ", t)
    # Collapse spaces
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _infer_decimal_separator(num_text: str) -> Tuple[Optional[str], Optional[str]]:
    """Infer decimal and thousand separators.

    Returns (decimal_sep, thousand_sep). Either can be None.
    Heuristics:
    - If both ',' and '.', decimal is whichever appears last.
    - If only one of them exists, treat it as decimal only if 1-2 digits follow at end;
      otherwise it's a thousands separator.
    - Spaces and apostrophes can act as thousand separators.
    """
    s = num_text
    has_comma = "," in s
    has_dot = "." in s
    if has_comma and has_dot:
        last_comma = s.rfind(",")
        last_dot = s.rfind(".")
        if last_comma > last_dot:
            return ",", "."
        else:
            return ".", ","
    if has_comma:
        after = s.split(",")[-1]
        if re.fullmatch(r"\d{1,2}", after):
            return ",", None
        return None, ","
    if has_dot:
        after = s.split(".")[-1]
        if re.fullmatch(r"\d{1,2}", after):
            return ".", None
        return None, "."
    # No dot/comma — spaces/apostrophes may be thousand separators
    return None, None


def normalize_numeric_string(text: str) -> Optional[Decimal]:
    """Parse a numeric value from an arbitrary locale-formatted string.

    Returns Decimal or None if no number is found.
    """
    if text is None:
        return None
    t = _strip_currency_and_keep_separators(text)
    if not t:
        return None
    # Keep only the last numeric token (often the price), but support negatives for discounts
    tokens = [tok for tok in re.findall(r"-?\s*[0-9][0-9,.'\s]*", t) if any(c.isdigit() for c in tok)]
    if not tokens:
        return None
    # Prefer a token that contains a minus sign (for negative values like discounts);
    # else take the last token which is commonly the price.
    neg_tokens = [tok for tok in tokens if "-" in tok]
    pick = max(neg_tokens, key=len) if neg_tokens else tokens[-1]
    s = pick.strip()
    # Remove non-breaking and thin spaces, apostrophes and normal spaces as thousand sep later
    s = s.replace(_NBSP, " ").replace(_THINSP, " ")
    dec_sep, thou_sep = _infer_decimal_separator(s)
    # Remove thousand separators: comma/dot/space/apostrophe that are not decimal
    work = s
    # Remove spaces/apostrophes used as thousand separators
    work = work.replace(" ", "").replace("'", "")
    if thou_sep:
        work = work.replace(thou_sep, "")
    if dec_sep and dec_sep != ".":
        work = work.replace(dec_sep, ".")
    # If no explicit decimal sep but there's a dot or comma left from ambiguous case, strip others
    work = re.sub(r"[^0-9.\-]", "", work)
    
    # Validate: ensure hyphen is only at the start (for negative numbers)
    if "-" in work:
        # Extract all hyphens
        hyphen_positions = [i for i, c in enumerate(work) if c == "-"]
        # Only keep the first hyphen if it's at position 0
        if hyphen_positions and hyphen_positions[0] == 0:
            # Remove all other hyphens
            work = "-" + work[1:].replace("-", "")
        else:
            # Hyphen not at start, remove all hyphens
            work = work.replace("-", "")
    
    # If multiple dots remain (malformed), keep last as decimal
    if work.count(".") > 1:
        last_dot = work.rfind(".")
        work = work[:last_dot].replace(".", "") + work[last_dot:]
    
    # Final validation: ensure the pattern is valid (optional minus, digits, optional decimal point with digits)
    if not re.fullmatch(r"-?\d+(\.\d+)?", work):
        return None
    
    try:
        return Decimal(work)
    except (InvalidOperation, ValueError):
        return None


def parse_monetary(text: Optional[str], currency_hint: Optional[str] = None) -> ParsedMonetary:
    """Parse a monetary value to amount and currency code.

    If parsing fails, returns amount=Decimal(0) and currency='UNK'.
    """
    amount = normalize_numeric_string(text or "")
    ccy = detect_currency(text, currency_hint)
    if amount is None:
        amount = Decimal("0")
    return ParsedMonetary(amount=amount, currency=ccy, raw_text=text or "", kind="absolute")


_PCT_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*%", re.IGNORECASE)


def parse_discount(text: Optional[str], currency_hint: Optional[str] = None) -> ParsedMonetary:
    """Parse discount which can be percentage or absolute monetary amount.

    - Percentage example: "10% OFF" -> kind='percent', amount=Decimal('10').
    - Absolute example: "-₹200" or "Save $50" -> kind='absolute', amount=Decimal('200').
    If nothing detected, returns amount=0, kind='absolute'.
    """
    raw = text or ""
    if not raw.strip():
        return ParsedMonetary(amount=Decimal("0"), currency=detect_currency(raw, currency_hint), raw_text=raw)

    m = _PCT_RE.search(raw)
    if m:
        num_txt = m.group(1).replace(",", ".")
        try:
            pct = Decimal(num_txt)
            return ParsedMonetary(amount=_bankers_round_2(pct), currency="PCT", raw_text=raw, kind="percent")
        except InvalidOperation:
            pass

    # Fallback: parse absolute monetary value
    pm = parse_monetary(raw, currency_hint)
    # absolute discounts should be positive amount regardless of sign in text
    amt = pm.amount.copy_abs()
    return replace(pm, amount=amt, kind="absolute")


def parse_raw_components(raw: RawPrice) -> Tuple[ParsedMonetary, ParsedMonetary, ParsedMonetary, ParsedMonetary]:
    """Parse base, shipping, tax, discount from a RawPrice."""
    base = parse_monetary(raw.price_text, raw.currency_hint)
    shipping = parse_monetary(raw.shipping_text, raw.currency_hint or base.currency)
    tax = parse_monetary(raw.tax_text, raw.currency_hint or base.currency)
    discount = parse_discount(raw.discount_text, raw.currency_hint or base.currency)
    return base, shipping, tax, discount
