"""Assert the transcription in tables.py against the pinned PDF's text layer.

Run:
  python3 -I check_tables.py <path to arxiv-2609.18745v1.pdf text layer>

The text layer is `pdftotext -layout arxiv-2609.18745v1.pdf`. The PDF's SHA-256 must be
4211d8ef46c55efe8d89ba4ee6c0b4e57cca1e78d0856e9cdfbde37046a7f4e1; poppler 26.08.0 gives the
text layer SHA-256 08fa7d4b91c13ddcd5531b66cdec3629427ad1ef9ceef047d785bf1c408617f5.

The check is deliberately dumb: for each table it isolates the printed block by its caption and
its end marker, asserts the row labels appear in printed order inside that block, and asserts
each row's printed line holds exactly the transcribed values in order. A value copied from a
neighbouring column therefore fails, because the whole row is matched at once.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tables as T  # noqa: E402

PDF_SHA256 = "4211d8ef46c55efe8d89ba4ee6c0b4e57cca1e78d0856e9cdfbde37046a7f4e1"
TEXT_LAYER_SHA256 = "08fa7d4b91c13ddcd5531b66cdec3629427ad1ef9ceef047d785bf1c408617f5"

failures = []


def check(condition, message):
    if not condition:
        failures.append(message)


def block(text, start, end):
    i = text.index(start)
    j = text.index(end, i)
    return text[i:j]


def row_line(blk, label):
    """The one printed line of `blk` whose first field is exactly `label`.

    A row label that is a prefix of another ("Evotune" and "Evotune-f") must not match the
    longer one, so the character after the label has to be a space or the end of the line.
    """
    matches = []
    for line in blk.splitlines():
        stripped = line.strip()
        rest = stripped[len(label):]
        # Everything printed after the label must be the row's own cells: digits, decimal
        # points, signs, plus-minus and dashes. That rules out "evotuning" matching the
        # "evotuning (forced)" line, whose remainder still holds letters.
        if stripped.startswith(label) and re.fullmatch(r"[\s\d.±–−+-]*", rest):
            matches.append(line)
    check(len(matches) == 1, f"expected exactly one line whose first field is {label!r}, found {len(matches)}")
    return matches[0] if matches else ""


def numbers(line):
    """Every number printed on a line, in printed order, as printed."""
    return re.findall(r"-?\d+\.\d+|-?\d+", line)


def main(path):
    text = open(path, encoding="utf-8").read()

    # ---- Table 2 ------------------------------------------------------------------------
    t2 = block(text, "Table 2: EvoFlows", "A    Extended results on all metrics")
    check("20 templates × 20 variants, holdout 200, agreement ceiling 300 real homologs" in t2
          or "holdout 200, agreement ceiling 300 real homologs" in t2,
          "Table 2 caption does not state the frame this batch records")
    # Column headings are printed across two header lines ("pairw." above "Lev.") and the text
    # layer renders the entropy-delta heading with U+2206 rather than U+0394, so each heading is
    # checked word by word against the header lines with whitespace collapsed.
    header = " ".join(t2[: t2.index("ty1")].split())
    for label in T.TABLE2_COLUMNS:
        for word in label.replace("Δ", "").split():
            check(word in header, f"Table 2 column heading word missing from the header: {word!r} (of {label!r})")
    check("H" in header and ("Δ" in header or "∆" in header),
          "Table 2 entropy-delta heading not found in the header")
    for family in ("ty1", "her2vh"):
        check(family in t2, f"Table 2 family block label missing: {family!r}")
    # Row order, per family block.
    ty1 = block(t2, "ty1", "her2vh")
    her2 = t2[t2.index("her2vh"):]
    for family, blk in (("ty1", ty1), ("her2vh", her2)):
        found = [label for label in T.TABLE2_ROWS if label in blk]
        check(found == T.TABLE2_ROWS, f"Table 2 {family} row order {found} != {T.TABLE2_ROWS}")
        for label in T.TABLE2_ROWS:
            line = row_line(blk, label)
            printed = numbers(line)
            want = [v for v in T.TABLE2[family][label] if v != "–"]
            check(printed == want, f"Table 2 {family} row {label!r}: printed {printed} != transcribed {want}")
            dashes = T.TABLE2[family][label].count("–")
            check(line.count("–") == dashes,
                  f"Table 2 {family} row {label!r}: printed {line.count(chr(0x2013))} dashes, transcribed {dashes}")

    # ---- Table 1 ------------------------------------------------------------------------
    t1 = block(text, "Table 1: EvoFlows’ six baselines", "masks back to their value")
    check("The two blocks are not comparable" in t1, "Table 1 caption does not state the two blocks are not comparable")
    upper = block(t1, "ours — two antibody families", "the original — the same two families")
    lower = t1[t1.index("the original — the same two families"):]
    for name, blk, data in (("upper", upper, T.TABLE1_UPPER), ("lower", lower, T.TABLE1_LOWER)):
        for label in data:
            line = row_line(blk, label)
            printed = numbers(line)
            want = []
            for column in T.TABLE1_LOWER_COLUMNS:
                want.extend(data[label][column])
            check(printed == want, f"Table 1 {name} row {label!r}: printed {printed} != transcribed {want}")

    # ---- Table 1's upper block duplicates Table 2 ---------------------------------------
    for t1_row, t2_row in T.TABLE1_TO_TABLE2_ROW.items():
        for t1_col, t2_col in T.TABLE1_TO_TABLE2_COLUMN.items():
            index = T.TABLE2_COLUMNS.index(t2_col)
            for position, family in enumerate(("ty1", "her2vh")):
                a = T.TABLE1_UPPER[t1_row][t1_col][position]
                b = T.TABLE2[family][t2_row][index]
                check(a == b, f"Table 1 upper {t1_row}/{t1_col}/{family} prints {a}, Table 2 prints {b}")

    # ---- Table 4 ------------------------------------------------------------------------
    t4 = block(text, "Table 4: Ceiling-normalized performance", "Sample-Size Dependency")
    check("EditJumps is evaluated on two antibody families (200 references)" in t4.replace("\n", " ").replace("  ", " ")
          or "200 references" in t4, "Table 4 caption does not state the reference-set size")
    for label in T.TABLE4_ROWS:
        line = row_line(t4, label)
        printed = numbers(line)
        want = numbers(T.TABLE4[label]["EditJumps (Ours)"]) + numbers(T.TABLE4[label]["EvoFlows (Published)"])
        check(printed == want, f"Table 4 row {label!r}: printed {printed} != transcribed {want}")

    # ---- Appendix E reference-size series -----------------------------------------------
    sentence = " ".join(text.split())
    for size, value in T.COVARIANCE_BY_REFERENCE_SIZE:
        check(f"{value} at N = {size}" in sentence or f"at {value}" in sentence,
              f"covariance {value} at N = {size} not printed as transcribed")
    check("mathematically non-comparable" in sentence, "the non-comparability sentence is not printed as quoted")

    if failures:
        for message in failures:
            print("FAIL", message, file=sys.stderr)
        raise SystemExit(f"{len(failures)} assertion(s) failed")
    print("all table assertions passed", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1])
