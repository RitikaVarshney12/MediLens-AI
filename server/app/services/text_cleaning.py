import re


def clean_text(raw_text: str) -> str:
    if not raw_text:
        return ""

    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

    # Merge lines that were broken mid-sentence: a line that doesn't end in
    # sentence-ending punctuation and is followed by a lowercase-starting
    # line is very likely one sentence split by PDF/OCR line wrapping.
    lines = [line.strip() for line in text.split("\n")]
    merged_lines: list[str] = []
    for line in lines:
        if not line:
            merged_lines.append("")
            continue
        previous = merged_lines[-1] if merged_lines else ""
        should_merge = (
            previous
            and previous[-1] not in ".:!?)]}"
            and line[0].islower()
        )
        if should_merge:
            merged_lines[-1] = f"{previous} {line}"
        else:
            merged_lines.append(line)

    text = "\n".join(merged_lines)

    # Collapse repeated spaces/tabs and excessive blank lines.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove common OCR artifacts: stray pipe characters used as column
    # separators, and non-printable control characters.
    text = re.sub(r"[^\S\n]*\|[^\S\n]*", " ", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)

    # Drop lines that are pure noise (only punctuation/symbols, no letters
    # or digits) - common OCR debris on scanned reports.
    cleaned_lines = [
        line for line in text.split("\n") if line == "" or re.search(r"[A-Za-z0-9]", line)
    ]

    return "\n".join(cleaned_lines).strip()