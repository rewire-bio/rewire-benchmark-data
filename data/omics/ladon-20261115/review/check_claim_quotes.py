#!/usr/bin/env python3
"""Check the batch's non-result records against the text of the sources they cite.

review/check_figure_labels.py re-reads the 101 printed figure labels. This script covers the
other 216 records: every quoted phrase and every number they state is looked for in the text of
one of the sources the record's `source_ids` name, so a claim cannot assert a quotation or a
count that its source does not carry. It checks presence in the cited artifact, not that the
number means what the record says it means; that part is the manual read recorded in the dated
review.

Artifacts are given as `<source-id>=<path>`; a PDF is converted with `pdftotext -layout`, HTML is
reduced to text by stripping tags. Curly quotes, dashes, non-breaking spaces and thousands
separators are normalised on both sides, and a number is also looked for without its separator.

Usage:
  python3 check_claim_quotes.py <batch.jsonl> <source-id>=<artifact> ...
"""

from __future__ import annotations

import html
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Tokens that no source is expected to print: our own review dates, the generic confidence level,
# and record-keeping numbers the batch adds rather than quotes.
IGNORED = {"2026", "2026-11-15", "95", "0.95", "2026-11-12", "24157116", "10", "20261115"}

# A quotation opens at a word boundary and closes before space or punctuation, so that the
# apostrophe in "Uno's" or "the report's" does not open one.
QUOTED = re.compile(r"(?:(?<=^)|(?<=[\s(\[]))'([^'\n]{4,}?)'(?=[\s.,;:)\]]|$)")
NUMBER = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?(?![\w])")
# Attribute keys that hold our own bookkeeping, or a record ID, rather than source text.
SKIP_KEYS = {
    "review", "missing_metadata", "evidence_concerns", "provenance_note",
    "protocol", "protocol_id", "source_id", "aggregation_source_id",
}
RECORD_ID = re.compile(r"ladon-20261115-[a-z0-9-]+")

# Tokens this check cannot find but a reviewer read and accepted, with the reason. They are
# reported, not skipped, so the output file says what was looked at and why it passed.
EXPLAINED = {
    ("ladon-20261115-data-tcga-cptac-transfer-both", "3,589"):
        "The field itself says '3,589 by extractor's sum; no combined count is printed'. "
        "2,461 + 1,128 = 3,589 from the page 12 table, and it is labelled as a sum.",
    ("ladon-20261115-method-t-effector-ifng", "T-effector / IFN-γ"):
        "Figure 6 on page 10 prints this row label, but the text layer breaks it across two "
        "lines ('T-effector / IFN-' then the gamma), so a contiguous search cannot find it. "
        "Read by eye on page 10.",
    ("ladon-20261115-protocol-transfer-pan-cancer", "Pan-Cancer, Mean of 2 transfers"):
        "The two halves are printed as the panel's two header lines; the comma joining them "
        "is the locator's, not the source's. Both strings occur on page 6.",
}


def normalise(text: str) -> str:
    text = html.unescape(text)
    for src, dst in (
        ("‘", "'"), ("’", "'"), ("“", '"'), ("”", '"'),
        ("–", "-"), ("—", "-"), ("−", "-"), (" ", " "),
        ("′", "'"), ("ﬁ", "fi"), ("ﬂ", "fl"),
    ):
        text = text.replace(src, dst)
    return re.sub(r"\s+", " ", text)


def artifact_text(path: Path) -> str:
    raw = path.read_bytes()
    if raw[:5] == b"%PDF-":
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "layout.txt"
            subprocess.run(
                ["pdftotext", "-layout", str(path), str(out)], check=True, capture_output=True
            )
            text = out.read_text(encoding="utf-8", errors="replace")
    else:
        text = raw.decode("utf-8", errors="replace")
        if path.suffix in {".html", ".htm"}:
            # <style> is noise, but <script> is evidence: the figure pages carry their row
            # labels and comparator notes inside a DATA object in a script element.
            text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.S | re.I)
            text = re.sub(r"<[^>]+>", " ", text)
    return normalise(text)


def strings_of(value, out: list[str]) -> None:
    if isinstance(value, str):
        out.append(value)
    elif isinstance(value, list):
        for item in value:
            strings_of(item, out)
    elif isinstance(value, dict):
        for key, item in value.items():
            if key not in SKIP_KEYS:
                strings_of(item, out)


def present(needle: str, texts: list[str]) -> bool:
    needle = normalise(needle).strip().strip(".,;:")
    if not needle:
        return True
    variants = {needle}
    if "," in needle:
        variants.add(needle.replace(",", ""))
    if needle.replace(".", "").isdigit() and "." in needle:
        variants.add(needle.rstrip("0").rstrip("."))
    return any(v and v in text for v in variants for text in texts)


def main(batch: Path, artifacts: dict[str, Path]) -> int:
    texts = {sid: artifact_text(path) for sid, path in artifacts.items()}
    records = [json.loads(line) for line in batch.read_text().splitlines() if line.strip()]
    rows: list[tuple[str, str, str, str]] = []
    checked = quotes = numbers = 0
    for record in records:
        if record["kind"] == "result":
            continue  # covered by review/check_figure_labels.py
        available = [texts[s] for s in record["source_ids"] if s in texts]
        if not available:
            rows.append((record["id"], "no_artifact", "", ",".join(record["source_ids"])))
            continue
        checked += 1
        fields: list[str] = [record.get("description", "")]
        strings_of(record["attributes"], fields)
        blob = RECORD_ID.sub(" ", " ".join(fields))
        for match in QUOTED.finditer(blob):
            phrase = match.group(1)
            quotes += 1
            if not present(phrase, available):
                reason = EXPLAINED.get((record["id"], phrase))
                rows.append(
                    (record["id"], "quote_explained" if reason else "QUOTE_NOT_FOUND", phrase,
                     reason or "")
                )
        for match in NUMBER.finditer(blob):
            token = match.group(0)
            if token in IGNORED or token.replace(",", "").rstrip("0").rstrip(".") in IGNORED:
                continue
            numbers += 1
            if not present(token, available):
                reason = EXPLAINED.get((record["id"], token))
                rows.append(
                    (record["id"], "number_explained" if reason else "NUMBER_NOT_FOUND", token,
                     reason or "")
                )
    out = Path(__file__).with_name("claim-quote-check.tsv")
    with out.open("w") as fh:
        fh.write("id\tstatus\ttoken\tnote\n")
        for row in rows:
            fh.write("\t".join(row) + "\n")
    unexplained = [r for r in rows if r[1].isupper() or r[1] == "no_artifact"]
    print(f"{checked} non-result records checked against their cited sources")
    print(
        f"{quotes} quoted phrases, {numbers} numbers; {len(rows)} not found by search, "
        f"{len(rows) - len(unexplained)} of them explained, {len(unexplained)} unexplained"
    )
    print(f"wrote {out.name}")
    for row in rows[:60]:
        print("  " + " | ".join(row))
    return 1 if unexplained else 0


if __name__ == "__main__":
    pairs = dict(arg.split("=", 1) for arg in sys.argv[2:])
    sys.exit(main(Path(sys.argv[1]), {k: Path(v) for k, v in pairs.items()}))
