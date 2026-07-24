"""Low-level parsing utilities for lab report values: numbers (including
Indian- and Western-style comma grouping), units, and reference ranges.

Kept separate from medical_extractor.py's parameter catalog so each file
stays focused, and so the number/range parsing logic can be reused and
unit-tested on its own.
"""

import re

# --- Numbers -----------------------------------------------------------
# Handles both Indian-style grouping (e.g. "1,50,000", "5,100") and
# Western-style grouping (e.g. "150,000"), plus plain digits and decimals.
#
# The comma-grouped form is tried first so a genuine grouped number is
# captured whole. It only matches when a comma is actually followed by a
# valid 2-3 digit group, so a stray punctuation comma (e.g. "15, which is
# normal") safely falls through to the plain-number form instead of being
# swallowed into the match.
_COMMA_GROUPED_NUMBER = r"\d{1,3}(?:,\d{2,3})+(?:\.\d+)?"
_PLAIN_NUMBER = r"(?:\d+(?:\.\d+)?|\.\d+)"
_NUMBER = rf"(?:{_COMMA_GROUPED_NUMBER}|{_PLAIN_NUMBER})"

# A value, optionally paired like a blood pressure reading ("120/80").
VALUE_RE = re.compile(rf"{_NUMBER}(?:\s*/\s*{_NUMBER})?")

# --- Units ---------------------------------------------------------------
# Ordered so more specific/compound units are tried before short bare units
# (e.g. "%", "pg") that could otherwise match a smaller piece of the same
# text at the same starting position - Python's re module picks the first
# alternative that matches at a given position, not the longest one, so
# specific-before-generic ordering matters here.
UNIT_RE = re.compile(
    r"gm/dL|gm\s*%|[a-zA-Z\u00b5]{0,3}g/dL|"
    r"x\s*10\s*\^?\s*\d+\s*/\s*u?L|"
    r"lakhs?/cumm|lac(s)?/cumm|millions?/cumm|thousands?/cumm|cells?/cumm|/cumm|"
    r"/\s?[uµ]L|mIU/L|[uµ]IU/mL|ng/mL|pg/mL|mL/min(?:/1\.73\s*m2?)?|mmHg|"
    r"mEq/L|IU/L|U/L|mmol/L|ng/dL|mg/L|"
    r"%|bpm|\bsec(?:onds?)?\b|\bcumm\b|\bfL\b|\bpg\b|\bmm/hr\b|\bmm/hour\b",
    re.IGNORECASE,
)

# --- Reference ranges ------------------------------------------------------
# Common OCR renderings of a range separator: hyphen, en dash, em dash, or
# the word "to".
_RANGE_SEP = r"(?:-|\u2013|\u2014|to)"

# Reference range with an explicit label, e.g. "Ref Range: 13.0-17.0" or
# "Normal Range 4,800 - 10,800", possibly with a trailing unit.
NAMED_REFERENCE_RE = re.compile(
    r"(?:ref(?:erence)?\.?\s*(?:range)?|normal(?:\s*range)?|bio\.?\s*ref\.?\s*range)"
    rf"\s*[:\-]?\s*(?P<range>{_NUMBER}\s*{_RANGE_SEP}\s*{_NUMBER}(?:\s*\S+)?)",
    re.IGNORECASE,
)
# Reference range in parentheses, e.g. "(13.0 - 17.0)".
PAREN_RANGE_RE = re.compile(
    rf"\(([^()]*{_NUMBER}[^()]*{_RANGE_SEP}[^()]*{_NUMBER}[^()]*)\)", re.IGNORECASE
)
# A "bare" range with no label at all - very common in OCR output where the
# range sits on its own line, e.g. "13 - 17", "4,800 - 10,800", "4.8–10.8",
# or "13 to 17". Anchored to (almost) the whole line so it doesn't fire on
# a value/unit line that just happens to contain a dash somewhere.
# Tolerant of stray punctuation OCR sometimes inserts around the separator.
BARE_RANGE_RE = re.compile(
    rf"^\s*[:\-]?\s*{_NUMBER}\s*{_RANGE_SEP}\s*{_NUMBER}(?:\s+\S+)?\s*[.:]?\s*$",
    re.IGNORECASE,
)

# A range appearing anywhere within a line rather than occupying the whole
# line - the fallback for table rows where value, unit, and range are all
# on one line (e.g. "Hemoglobin | 15 | g/dL | 13-17").
INLINE_RANGE_RE = re.compile(rf"{_NUMBER}\s*{_RANGE_SEP}\s*{_NUMBER}", re.IGNORECASE)

# Single-sided inequality ranges, common for eGFR/HDL/LDL/etc: "<130",
# "> 40", "\u2264 5.0", "\u2265 90".
_INEQUALITY = r"[<>\u2264\u2265]=?"
BARE_INEQUALITY_RE = re.compile(
    rf"^\s*{_INEQUALITY}\s*{_NUMBER}(?:\s+\S+)?\s*$", re.IGNORECASE
)
INLINE_INEQUALITY_RE = re.compile(rf"{_INEQUALITY}\s*{_NUMBER}", re.IGNORECASE)
PAREN_INEQUALITY_RE = re.compile(rf"\(\s*({_INEQUALITY}\s*{_NUMBER})\s*\)", re.IGNORECASE)

# Semi-quantitative/qualitative results common on urinalysis and similar
# panels, where there is no numeric reading at all (e.g. "Nil", "Trace",
# "2+"). Used only as a fallback when no numeric value is found.
QUALITATIVE_VALUE_RE = re.compile(
    r"\b(?:nil|negative|positive|trace|absent|present|occasional|few|many|plenty|numerous)\b|[1-4]\+",
    re.IGNORECASE,
)

# --- Noise lines -----------------------------------------------------------
_NOISE_LINE_PATTERNS = [
    re.compile(r"^page\s*\d+(\s*of\s*\d+)?$", re.IGNORECASE),
    re.compile(r"^[-_*=]{3,}$"),
    re.compile(r"^end\s*of\s*report$", re.IGNORECASE),
    re.compile(r"^this\s*is\s*a\s*computer[\s-]generated\s*report.*$", re.IGNORECASE),
    re.compile(r"^electronically\s*(verified|authenticated|signed).*$", re.IGNORECASE),
    re.compile(r"^authorized\s*signatory$", re.IGNORECASE),
    re.compile(r"^(report\s*)?printed\s*(on|date|at).*$", re.IGNORECASE),
    re.compile(r"^qr\s*code.*$", re.IGNORECASE),
    re.compile(r"^scan\s*(the\s*)?qr.*$", re.IGNORECASE),
    re.compile(r"^barcode.*$", re.IGNORECASE),
    re.compile(r"^specimen\s*(collected|received).*$", re.IGNORECASE),
    re.compile(r"^collected\s*(on|at).*$", re.IGNORECASE),
    re.compile(r"^report\s*(date|status)\s*[:\-].*$", re.IGNORECASE),
    re.compile(
        r"^dr\.?\s+[a-z][a-z .]*,?\s*(md|do|mbbs|md\.?\s*path|frcp|phd|dnb)\b.*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(test|parameter|investigation)s?\s*\|?\s*(value|result)s?\s*\|?"
        r"\s*(unit)?\s*\|?\s*(reference|range|normal).*$",
        re.IGNORECASE,
    ),
]


def is_noise_line(line: str) -> bool:
    """True for lines that carry no parameter data: page numbers, plain
    separator lines, etc."""
    return any(pattern.match(line) for pattern in _NOISE_LINE_PATTERNS)


# --- Numeric normalization (internal use only) ------------------------------
# The reports.structured_json schema (and the frontend that reads it) only
# expect {parameter, value, unit, reference_range} with `value` as a
# display string - that contract is unchanged. These helpers exist so a
# true numeric value CAN be computed when needed internally (e.g. a future
# phase, or extra validation) without requiring a schema or frontend change.

_LAKH_MULTIPLIER = 100_000
_MILLION_MULTIPLIER = 1_000_000
_THOUSAND_MULTIPLIER = 1_000


def parse_numeric_value(display_value: str) -> float | None:
    """Converts a display value like "5,100" or "3.5" into a plain float
    (e.g. "1,50,000" -> 150000.0). Returns None for compound values like
    "120/80" (no single numeric value) or unparseable input."""
    cleaned = display_value.strip()
    if "/" in cleaned:
        return None
    cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def estimate_numeric_value(display_value: str, unit: str | None) -> float | None:
    """Best-effort true numeric value for a (value, unit) pair, applying the
    multiplier implied by units like "lakh/cumm" or "million/cumm" - e.g.
    value="3.5", unit="lakhs/cumm" -> 350000.0."""
    base = parse_numeric_value(display_value)
    if base is None:
        return None

    unit_text = (unit or "").lower()
    if "lakh" in unit_text or "lac" in unit_text:
        return base * _LAKH_MULTIPLIER
    if "million" in unit_text:
        return base * _MILLION_MULTIPLIER
    if "thousand" in unit_text:
        return base * _THOUSAND_MULTIPLIER
    return base