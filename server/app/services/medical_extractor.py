"""Extracts lab parameters (name, value, unit, reference range) from cleaned
OCR/PDF text.

Four parsing stages are tried, in priority order, each only picking up
parameters the earlier stages missed:

1. Table parser (_try_parse_as_table): for pathology-report tables where
   each row is self-contained on one line ("Hemoglobin 12.3 gm% 14-18"),
   every value/unit/range is read strictly from that row's own line -
   never from a neighboring row. Used only when the whole document looks
   confidently tabular; otherwise it returns None and the remaining
   stages run instead.

2. Block parser (_extract_with_block_parser): for layouts where the
   value, unit, and reference range are split across several lines,
   sometimes with their own "VALUE"/"UNIT"/"REFERENCE" labels, or even
   read out before their own label (column-based OCR):

       HAEMOGLOBIN
       15
       g/dL
       13 - 17

   Each recognized parameter name starts a block: the lines immediately
   following it (forward) and immediately preceding it (backward), each
   up to a safety cap or until another recognized parameter name starts.

3. Single-line parser (_try_single_line_pass): a lower-confidence sweep
   for any parameter headings the block parser still didn't resolve,
   trying ONLY that heading's own line (no cross-line search at all).

4. Regex fallback (_try_regex_fallback): last resort for anything still
   missing - the same forward/backward search as the block parser, but
   with a much wider safety cap. It still stops at the next recognized
   parameter heading in either direction, so it can never pull a value
   from a different parameter's row - it only helps when the real value
   is simply further away than the standard block window.

Every stage feeds into the same completeness-preferring dedupe
(_dedupe): if a parameter is found more than once (by the same or
different stages), the record with the most fields populated (value +
unit + reference_range) wins; ties keep whichever was found first.

Each finding also carries an internal-only confidence score (never part
of the public API - see _to_public_dict) based on which stage produced
it and how many fields were populated.

Low-level number/unit/range parsing lives in lab_value_parsing.py; this
module is just the parameter catalog and the four parsing stages.
"""

import re
from dataclasses import dataclass
from typing import Any, Callable

from app.services.lab_value_parsing import (
    BARE_INEQUALITY_RE,
    BARE_RANGE_RE,
    INLINE_INEQUALITY_RE,
    INLINE_RANGE_RE,
    NAMED_REFERENCE_RE,
    PAREN_INEQUALITY_RE,
    PAREN_RANGE_RE,
    QUALITATIVE_VALUE_RE,
    UNIT_RE,
    VALUE_RE,
    is_noise_line,
)

# Canonical parameter name -> patterns that identify it in report text.
# Multiple OCR/report spellings map to the same canonical name.
#
# ORDERING MATTERS: entries whose pattern text is a substring of another
# entry's pattern (e.g. "HDL" inside "Non-HDL", "Creatinine" inside "BUN/
# Creatinine Ratio", "RBC" inside "Urine RBC", "BNP" inside "NT-proBNP",
# "Iron" inside "Total Iron Binding Capacity") are placed AFTER the more
# specific entry, so the more specific one claims the line first. See
# _find_heading_match().
PARAMETER_PATTERNS: dict[str, list[str]] = {
    # --- Urine routine (qualified urine-* entries first, since they'd
    # otherwise be swallowed by the same-named blood-panel entries below) ---
    "Urine pH": [r"urine\s*pH", r"\bpH\b"],
    "Specific Gravity": [r"specific\s*gravity"],
    "Urine Protein": [r"urine\s*protein", r"protein\s*\(\s*urine\s*\)"],
    "Urine Glucose": [r"urine\s*glucose", r"glucose\s*\(\s*urine\s*\)"],
    "Urine RBC": [r"urine\s*rbc", r"rbc\s*\(\s*urine\s*\)"],
    "Urine Albumin": [r"urine\s*albumin", r"albumin\s*\(\s*urine\s*\)"],
    "Urine Bilirubin": [r"urine\s*bilirubin"],
    "Pus Cells": [r"pus\s*cells?"],
    "Epithelial Cells": [r"epithelial\s*cells?"],
    "Leukocyte Esterase": [r"leu[ck]ocyte\s*esterase"],
    "Ketones": [r"ketones?"],
    "Nitrite": [r"nitrites?"],
    "Urobilinogen": [r"urobilinogen"],
    "Urine Casts": [r"\bcasts?\b"],
    "Urine Crystals": [r"crystals?"],
    "Bacteria": [r"bacteria"],

    # --- CBC ---
    "Hemoglobin": [r"h(?:ae|e)moglobin", r"\bHb\b"],
    "RBC": [r"\bRBC\b", r"red\s*blood\s*cell\s*count"],
    "WBC": [
        r"\bWBC\b",
        r"white\s*blood\s*cell\s*count",
        r"total\s*leu[ck]ocyte\s*count",
        r"\bleu[ck]ocyte(s)?\b",
        r"\bTLC\b",
    ],
    "Platelets": [r"platelet(s)?\s*count", r"\bplatelets?\b"],
    "MCV": [r"\bMCV\b"],
    "MCH": [r"\bMCH\b"],
    "MCHC": [r"\bMCHC\b"],
    "RDW": [r"\bRDW\b"],
    "MPV": [r"\bMPV\b"],
    "PDW": [r"\bPDW\b"],
    "PCT": [r"\bPCT\b"],
    "HCT": [r"\bHCT\b", r"h(?:ae|e)matocrit"],
    "PCV": [r"\bPCV\b"],
    "Absolute Neutrophils": [r"absolute\s*neutrophils?", r"\bANC\b"],
    "Absolute Lymphocytes": [r"absolute\s*lymphocytes?", r"\bALC\b"],
    "Neutrophils": [r"neutrophils?"],
    "Lymphocytes": [r"lymphocytes?"],
    "Monocytes": [r"monocytes?"],
    "Eosinophils": [r"eosinophils?"],
    "Basophils": [r"basophils?"],
    "ESR": [r"\bESR\b", r"erythrocyte\s*sedimentation\s*rate"],

    # --- Diabetes / glucose (FBS/PPBS/OGTT stay distinct; unqualified
    # Random Blood Sugar / RBS / Blood Sugar / Glucose all merge into one) ---
    "FBS": [r"\bFBS\b", r"fasting\s*blood\s*sugar", r"fasting\s*glucose"],
    "PPBS": [r"\bPPBS\b", r"post\s*prandial\s*(blood\s*)?(sugar|glucose)"],
    "OGTT": [r"\bOGTT\b", r"oral\s*glucose\s*tolerance\s*test"],
    "Glucose": [
        r"\bRBS\b",
        r"random\s*blood\s*sugar",
        r"random\s*glucose",
        r"\bglucose\b",
        r"blood\s*sugar",
    ],
    "HbA1c": [r"hba1c", r"glycosylated\s*h(?:ae|e)moglobin"],

    # --- Vitamins ---
    "Vitamin D": [r"vitamin[\s-]?d\s*3?", r"25[\s-]?oh[\s-]?vitamin[\s-]?d"],
    "Vitamin B12": [r"vitamin[\s-]?b[\s-]?12", r"\bb\s?12\b"],
    "Folate": [r"folate", r"vitamin[\s-]?b[\s-]?9"],

    # --- Thyroid (Free T3/T4 before plain T3/T4, which "Free T3" also matches) ---
    "TSH": [r"\bTSH\b", r"thyroid\s*stimulating\s*hormone"],
    "Anti TPO": [r"anti[\s-]?tpo", r"anti[\s-]?thyroid\s*peroxidase"],
    "Free T3": [r"\bfree\s*t\s*3", r"\bFT3\b"],
    "Free T4": [r"\bfree\s*t\s*4", r"\bFT4\b"],
    "T3": [r"\bT3\b(?!\d)", r"triiodothyronine"],
    "T4": [r"\bT4\b(?!\d)", r"thyroxine"],

    # --- Kidney function (ratio, then BUN, before plain Creatinine/Urea) ---
    "BUN/Creatinine Ratio": [
        r"bun\s*/?\s*creatinine(?:\s*ratio)?",
        r"bun\s*:\s*creatinine",
    ],
    "Creatinine": [r"\bs\.?\s*creatinine", r"serum\s*creatinine", r"creatinine"],
    "BUN": [r"\bBUN\b", r"blood\s*urea\s*nitrogen"],
    "Urea": [r"blood\s*urea", r"\burea\b"],
    "eGFR": [r"\begfr\b", r"estimated\s*gfr"],
    "Uric Acid": [r"uric\s*acid"],
    "Calcium": [r"\bcalcium\b"],
    "Magnesium": [r"\bmagnesium\b"],
    "Phosphorus": [r"\bphosphorus\b", r"\bphosphate\b"],
    "Bicarbonate": [r"bicarbonate", r"\bHCO3\b"],
    "TIBC": [r"\bTIBC\b", r"total\s*iron\s*binding\s*capacity"],
    "Transferrin Saturation": [r"transferrin\s*saturation", r"\bTSAT\b"],
    "Serum Iron": [r"serum\s*iron", r"\biron\b"],
    "Ferritin": [r"ferritin"],

    # --- Lipid profile (ratios/Non-HDL before plain HDL/LDL, which they contain) ---
    "Non-HDL": [r"non[\s-]?hdl"],
    "TC/HDL Ratio": [r"t\.?c\.?\s*/\s*hdl", r"total\s*cholesterol\s*/\s*hdl"],
    "LDL/HDL Ratio": [r"ldl\s*/\s*hdl"],
    "Cholesterol": [r"total\s*cholesterol", r"\bcholesterol\b"],
    "HDL": [r"\bHDL\b"],
    "LDL": [r"\bLDL\b"],
    "VLDL": [r"\bVLDL\b"],
    "Triglycerides": [r"triglycerides"],

    # --- Liver function (Direct/Indirect before Total, which also matches bare "Bilirubin") ---
    "SGOT/AST": [r"\bSGOT\b", r"\bAST\b"],
    "SGPT/ALT": [r"\bSGPT\b", r"\bALT\b"],
    "ALP": [r"\bALP\b", r"alkaline\s*phosphatase"],
    "GGT": [r"\bGGT\b", r"gamma[\s-]?glutamyl", r"gamma\s*gt"],
    "Direct Bilirubin": [r"\bdirect\s*bilirubin"],
    "Indirect Bilirubin": [r"\bindirect\s*bilirubin"],
    "Total Bilirubin": [r"total\s*bilirubin", r"\bbilirubin\b"],
    "A/G Ratio": [r"a\s*/\s*g\s*ratio", r"albumin\s*/\s*globulin\s*ratio"],
    "Total Protein": [r"total\s*protein"],
    "Albumin": [r"\bs\.?\s*albumin", r"\balbumin\b"],
    "Globulin": [r"globulin"],

    # --- Electrolytes ---
    "Sodium": [r"\bsodium\b"],
    "Potassium": [r"\bpotassium\b"],
    "Chloride": [r"\bchloride\b"],

    # --- Cardiac markers (NT-proBNP before BNP, which it contains) ---
    "Troponin": [r"troponin", r"\bTnI\b", r"\bTnT\b"],
    "CKMB": [r"\bCK-?MB\b", r"creatine\s*kinase[\s-]?mb"],
    "NT-proBNP": [r"nt[\s-]?pro[\s-]?bnp"],
    "BNP": [r"\bBNP\b", r"brain\s*natriuretic\s*peptide"],

    # --- Inflammatory markers ---
    "CRP": [r"\bCRP\b", r"c[\s-]reactive\s*protein"],
    "Procalcitonin": [r"procalcitonin"],

    # --- Coagulation ---
    "PT": [r"\bPT\b", r"prothrombin\s*time"],
    "INR": [r"\bINR\b"],
    "aPTT": [r"\baPTT\b", r"activated\s*partial\s*thromboplastin\s*time", r"\bPTT\b"],
    "Fibrinogen": [r"fibrinogen"],
    "D-Dimer": [r"d[\s-]dimer"],

    # --- Hormones ---
    "Prolactin": [r"prolactin"],
    "Testosterone": [r"testosterone"],
    "Cortisol": [r"cortisol"],
    "Insulin": [r"\binsulin\b"],
    "FSH": [r"\bFSH\b", r"follicle\s*stimulating\s*hormone"],
    "LH": [r"\bLH\b", r"luteinizing\s*hormone"],
    "Estradiol": [r"estradiol"],
    "Progesterone": [r"progesterone"],

    # --- Vitals ---
    "Blood Pressure": [r"blood\s*pressure", r"\bBP\b"],
    "Heart Rate": [r"heart\s*rate", r"pulse\s*rate"],
}

# Patterns are compiled once at import time and reused for every document,
# rather than re-parsed on every call.
_COMPILED_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    name: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    for name, patterns in PARAMETER_PATTERNS.items()
}

# How many lines to search on either side of a parameter-name line during
# the standard block-parser stage, if no other recognized parameter
# heading is found first. Sized generously to comfortably fit a
# fully-split "name / value / unit / reference" layout, including one
# with its own "VALUE"/"UNIT"/"REFERENCE" labels.
MAX_BLOCK_LINES = 12

# Wider cap used only by the last-resort regex-fallback stage, for
# parameters whose value genuinely sits further away than the standard
# block window (e.g. extra commentary lines in between). It still stops
# at the next recognized parameter heading in either direction, so it can
# never cross into a different parameter's row.
FALLBACK_MAX_BLOCK_LINES = 40


@dataclass
class ExtractedParameter:
    parameter: str
    value: str
    unit: str | None
    reference_range: str | None
    confidence: float
    stage: str


def _find_heading_match(line: str) -> tuple[str, re.Match[str]] | None:
    """Returns (canonical_name, match) for the first parameter pattern that
    matches this line, or None if the line doesn't look like any known
    parameter's heading. Used both to detect a new parameter to extract and
    to detect where the current parameter's block should stop."""
    for canonical_name, patterns in _COMPILED_PATTERNS.items():
        for pattern in patterns:
            match = pattern.search(line)
            if match:
                return canonical_name, match
    return None


def _collect_parameter_block(
    lines: list[str], start_index: int, name_match_end: int, max_lines: int = MAX_BLOCK_LINES
) -> tuple[list[str], list[str]]:
    """Gathers the forward and backward neighboring lines for one
    parameter's value/unit/range, each stopping early if it hits another
    parameter's heading. Returned separately (not merged) because forward
    is always searched first and backward is only a fallback - see
    _search_forward_then_backward()."""
    forward: list[str] = []

    same_line_remainder = lines[start_index][name_match_end:].strip()
    if same_line_remainder:
        forward.append(same_line_remainder)

    for offset in range(1, max_lines + 1):
        next_index = start_index + offset
        if next_index >= len(lines):
            break
        next_line = lines[next_index]
        if _find_heading_match(next_line) is not None:
            break
        forward.append(next_line)

    backward: list[str] = []
    for offset in range(1, max_lines + 1):
        prev_index = start_index - offset
        if prev_index < 0:
            break
        prev_line = lines[prev_index]
        if _find_heading_match(prev_line) is not None:
            break
        backward.append(prev_line)

    return forward, backward


def _search_forward_then_backward(
    forward: list[str], backward: list[str], extractor: Callable[[list[str]], str | None]
) -> str | None:
    """Tries the forward block first (the normal reading order) and only
    consults the backward block if forward found nothing at all - handles
    column-based OCR where a value is read out before its label (e.g. "15"
    then "HEMOGLOBIN"), without letting a *different*, nearby parameter's
    leftover unit/range line get picked up just because it's physically
    closer than this parameter's own (further away) unit/range."""
    result = extractor(forward)
    if result is not None:
        return result
    return extractor(backward)


def _line_range_span(line: str) -> tuple[int, int] | None:
    """Span of the reference-range portion of a line, if it has an
    explicitly labeled or parenthesized one - used to keep a value match
    from being taken out of the range itself (requirement: never extract
    the reference range as the value)."""
    named_match = NAMED_REFERENCE_RE.search(line)
    if named_match:
        return named_match.span("range")

    paren_match = PAREN_RANGE_RE.search(line)
    if paren_match:
        return paren_match.span(1)

    return None


def _extract_value_from(block: list[str]) -> str | None:
    for line in block:
        stripped = line.strip()

        # A line that's purely a reference range or inequality (e.g.
        # "13 - 17" or "<130") is never the value itself, even if it
        # appears before the real value line (OCR line ordering isn't
        # always reliable).
        if BARE_RANGE_RE.match(stripped) or BARE_INEQUALITY_RE.match(stripped):
            continue

        range_span = _line_range_span(line)
        match = VALUE_RE.search(line)
        if match is None:
            continue

        if range_span is not None and range_span[0] <= match.start() < range_span[1]:
            # The only number found on this line sits inside its labeled/
            # parenthesized range (e.g. "Ref Range: 13-17") - look for a
            # real value elsewhere on the same line (e.g. before the
            # range), otherwise this line has nothing usable.
            alt_match = VALUE_RE.search(line[: range_span[0]])
            if alt_match is None:
                continue
            match = alt_match

        # Comma-grouped numbers (Indian "5,100" or Western "150,000") are
        # matched whole so nothing is lost, then commas are stripped for a
        # clean display value ("5100"). A trailing "+" (semi-quantitative
        # grading, e.g. "2+" on a urinalysis) is preserved rather than
        # truncated to the bare digit.
        end = match.end()
        suffix = "+" if end < len(line) and line[end] == "+" else ""
        return match.group(0).strip().replace(",", "") + suffix

    # No numeric value anywhere in the block - fall back to a
    # semi-quantitative result (e.g. urinalysis: "Nil", "Trace", "2+").
    for line in block:
        stripped = line.strip()
        if BARE_RANGE_RE.match(stripped) or BARE_INEQUALITY_RE.match(stripped):
            continue
        qualitative_match = QUALITATIVE_VALUE_RE.search(line)
        if qualitative_match:
            return qualitative_match.group(0)

    return None


def _extract_value(forward: list[str], backward: list[str]) -> str | None:
    return _search_forward_then_backward(forward, backward, _extract_value_from)


def _extract_unit_from(block: list[str]) -> str | None:
    for line in block:
        match = UNIT_RE.search(line)
        if match:
            return match.group(0)
    return None


def _extract_unit(forward: list[str], backward: list[str]) -> str | None:
    return _search_forward_then_backward(forward, backward, _extract_unit_from)


def _extract_reference_range_from(block: list[str]) -> str | None:
    # Every pattern is checked per-line, never on lines joined together:
    # joining with spaces would let a greedy trailing-token match bleed
    # across a line boundary into unrelated text (e.g. a section heading a
    # couple of lines below), corrupting the extracted range.
    for line in block:
        named_match = NAMED_REFERENCE_RE.search(line)
        if named_match:
            return named_match.group("range").strip().replace(",", "")

    for line in block:
        paren_match = PAREN_RANGE_RE.search(line)
        if paren_match:
            return paren_match.group(1).strip().replace(",", "")

    for line in block:
        paren_ineq_match = PAREN_INEQUALITY_RE.search(line)
        if paren_ineq_match:
            return paren_ineq_match.group(1).strip().replace(",", "")

    for line in block:
        bare_match = BARE_RANGE_RE.match(line.strip())
        if bare_match:
            return bare_match.group(0).strip(" :.").replace(",", "")

    for line in block:
        bare_ineq_match = BARE_INEQUALITY_RE.match(line.strip())
        if bare_ineq_match:
            return bare_ineq_match.group(0).strip(" :.").replace(",", "")

    for line in block:
        inline_match = INLINE_RANGE_RE.search(line)
        if inline_match:
            return inline_match.group(0).strip().replace(",", "")

    for line in block:
        inline_ineq_match = INLINE_INEQUALITY_RE.search(line)
        if inline_ineq_match:
            return inline_ineq_match.group(0).strip().replace(",", "")

    return None


def _extract_reference_range(forward: list[str], backward: list[str]) -> str | None:
    return _search_forward_then_backward(forward, backward, _extract_reference_range_from)


# --- Confidence scoring (internal only - see _to_public_dict) --------------
_STAGE_MULTIPLIER: dict[str, float] = {
    "table": 1.0,
    "block_forward": 0.95,
    "block_backward": 0.85,
    "single_line": 0.8,
    "regex_fallback": 0.6,
}


def _value_is_qualitative(value: str) -> bool:
    return bool(QUALITATIVE_VALUE_RE.fullmatch(value)) or value.endswith("+")


def _compute_confidence(
    value: str, unit: str | None, reference_range: str | None, stage: str
) -> float:
    """Rough internal confidence signal from four inputs: parameter match
    (always true if a finding exists), value match (numeric readings score
    higher than a qualitative/semi-quantitative fallback), unit match, and
    reference-range match - scaled by how reliable the producing stage's
    OCR-consistency generally is (table > block-forward > block-backward >
    single-line > regex-fallback)."""
    score = 0.25
    score += 0.15 if _value_is_qualitative(value) else 0.25
    score += 0.20 if unit is not None else 0.0
    score += 0.20 if reference_range is not None else 0.0
    score *= _STAGE_MULTIPLIER.get(stage, 0.5)
    return round(min(max(score, 0.0), 1.0), 2)


def _completeness(finding: ExtractedParameter) -> int:
    return 1 + (finding.unit is not None) + (finding.reference_range is not None)


def _dedupe(findings: list[ExtractedParameter]) -> list[ExtractedParameter]:
    """Keeps the most complete record per parameter (value + unit +
    reference_range beats fewer populated fields); ties keep whichever was
    found first."""
    best: dict[str, ExtractedParameter] = {}
    order: list[str] = []
    for finding in findings:
        name = finding.parameter
        if name not in best:
            best[name] = finding
            order.append(name)
            continue
        if _completeness(finding) > _completeness(best[name]):
            best[name] = finding
    return [best[name] for name in order]


def _parse_table_row(canonical_name: str, remainder: str, stage: str) -> ExtractedParameter | None:
    """Parses one row entirely from the text that follows the parameter
    name ON THAT SAME LINE - never from a neighboring row."""
    if not remainder:
        return None
    row = [remainder]
    value = _extract_value_from(row)
    if value is None:
        return None
    unit = _extract_unit_from(row)
    reference_range = _extract_reference_range_from(row)
    confidence = _compute_confidence(value, unit, reference_range, stage)
    return ExtractedParameter(canonical_name, value, unit, reference_range, confidence, stage)


def _try_parse_as_table(lines: list[str]) -> list[ExtractedParameter] | None:
    """Stage 1 - table parser: treats each line as one independent table
    row - parameter, value, unit, and reference range must all come from
    that single line, never from a neighboring row. Returns None (letting
    the caller move to the next stage) unless the document looks
    confidently tabular: every recognized parameter heading found a value
    on its own line, with at least two such rows."""
    rows: list[ExtractedParameter] = []
    recognized_heading_count = 0

    for line in lines:
        heading = _find_heading_match(line)
        if heading is None:
            continue
        recognized_heading_count += 1

        canonical_name, match = heading
        remainder = line[match.end():].strip()
        row = _parse_table_row(canonical_name, remainder, "table")
        if row is not None:
            rows.append(row)

    if recognized_heading_count == 0:
        return None
    if len(rows) != recognized_heading_count or len(rows) < 2:
        return None

    return _dedupe(rows)


def _extract_with_block_parser(lines: list[str]) -> list[ExtractedParameter]:
    """Stage 2 - block parser: every recognized heading is evaluated
    independently (a repeated heading is not skipped - later dedupe picks
    whichever occurrence is more complete)."""
    findings: list[ExtractedParameter] = []

    for index, line in enumerate(lines):
        heading = _find_heading_match(line)
        if heading is None:
            continue

        canonical_name, match = heading
        forward, backward = _collect_parameter_block(lines, index, match.end())

        value = _extract_value_from(forward)
        stage = "block_forward"
        if value is None:
            value = _extract_value_from(backward)
            stage = "block_backward"
        if value is None:
            # Parameter name found but no nearby value - most likely just
            # a section heading, not a real result.
            continue

        unit = _extract_unit(forward, backward)
        reference_range = _extract_reference_range(forward, backward)
        confidence = _compute_confidence(value, unit, reference_range, stage)
        findings.append(
            ExtractedParameter(canonical_name, value, unit, reference_range, confidence, stage)
        )

    return findings


def _try_single_line_pass(lines: list[str], already_found: set[str]) -> list[ExtractedParameter]:
    """Stage 3 - single-line parser: a lower-confidence sweep for any
    heading the block parser didn't resolve, using only that heading's own
    line (no cross-line search)."""
    findings: list[ExtractedParameter] = []

    for line in lines:
        heading = _find_heading_match(line)
        if heading is None:
            continue

        canonical_name, match = heading
        if canonical_name in already_found:
            continue

        remainder = line[match.end():].strip()
        row = _parse_table_row(canonical_name, remainder, "single_line")
        if row is None:
            continue

        findings.append(row)
        already_found.add(canonical_name)

    return findings


def _try_regex_fallback(lines: list[str], already_found: set[str]) -> list[ExtractedParameter]:
    """Stage 4 - last resort: the same forward/backward search as the
    block parser, but with a much wider safety cap (FALLBACK_MAX_BLOCK_LINES).
    Still stops at the next recognized parameter heading in either
    direction, so it can never pull a value from a different parameter's
    row - it only helps when a real value for THIS parameter is simply
    further away than the standard block window."""
    findings: list[ExtractedParameter] = []

    for index, line in enumerate(lines):
        heading = _find_heading_match(line)
        if heading is None:
            continue

        canonical_name, match = heading
        if canonical_name in already_found:
            continue

        forward, backward = _collect_parameter_block(
            lines, index, match.end(), max_lines=FALLBACK_MAX_BLOCK_LINES
        )
        value = _extract_value_from(forward)
        if value is None:
            value = _extract_value_from(backward)
        if value is None:
            continue

        unit = _extract_unit(forward, backward)
        reference_range = _extract_reference_range(forward, backward)
        confidence = _compute_confidence(value, unit, reference_range, "regex_fallback")
        findings.append(
            ExtractedParameter(
                canonical_name, value, unit, reference_range, confidence, "regex_fallback"
            )
        )
        already_found.add(canonical_name)

    return findings


def _to_public_dict(finding: ExtractedParameter) -> dict[str, Any]:
    """Serializes ONLY the public, frontend-facing fields - confidence and
    stage are internal and never leave this module."""
    return {
        "parameter": finding.parameter,
        "value": finding.value,
        "unit": finding.unit,
        "reference_range": finding.reference_range,
    }


def extract_medical_parameters(text: str) -> list[dict[str, Any]]:
    """Returns a list of {parameter, value, unit, reference_range} dicts -
    the schema stored in reports.structured_json and read by the
    frontend. A parameter is only included if a value was actually found
    (numeric or, failing that, a semi-quantitative token like "Nil"/"2+");
    a bare heading with no value is silently skipped rather than producing
    an incorrect entry. Each parameter appears at most once, keeping its
    most complete record.

    Runs, in order, until every recognized heading has a value or all
    stages are exhausted: table parser, block parser, single-line parser,
    regex fallback. See the module docstring for what each stage handles."""
    if not text:
        return []

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    lines = [line for line in lines if not is_noise_line(line)]

    table_rows = _try_parse_as_table(lines)
    if table_rows is not None:
        return [_to_public_dict(finding) for finding in table_rows]

    block_findings = _extract_with_block_parser(lines)
    found_names = {finding.parameter for finding in block_findings}

    single_line_findings = _try_single_line_pass(lines, found_names)
    fallback_findings = _try_regex_fallback(lines, found_names)

    all_findings = block_findings + single_line_findings + fallback_findings
    deduped = _dedupe(all_findings)
    return [_to_public_dict(finding) for finding in deduped]