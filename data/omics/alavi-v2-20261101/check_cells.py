"""Second, independent parse of the AlphaGenome cells of Alavi 2026 v2 Tables III and IV.

Usage: python3 -I check_cells.py <v2 full.pdf> <batch folder>

build.py reads `pdftotext -layout`, where a two-line row label straddles the value line. This check reads
`pdftotext -raw` instead, where each label is printed on its own lines before the value line, and checks the
header order of the columns. It compares every AlphaGenome cell with the printed_value in batch.jsonl,
asserts that all 56 match, and writes cell-check.tsv.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

PDF, OUT = sys.argv[1], sys.argv[2]
assert hashlib.sha256(open(PDF, "rb").read()).hexdigest() == "07bd32fffc1b31c222d43b0b18c213928e3fe111cc71c02fe2f95e64e6f7a798"
TOK = re.compile(r"\d+ \(\d+(?:\.\d+)? ?%\)|\d+(?:\.\d+)?%")
HEADERS = {
    "III": ("ACCURACY PPV TYPE I SPECIFICITY SENSITIVITY TYPE II POSITIVE POSITIVE", 6,
            ["Accuracy", "PPV", "Type I error", "Specificity", "Sensitivity", "Type II error", "Positive mutations", "Positive VUS"]),
    "IV": ("ACCURACY PPV TYPE I ERROR SPECIFICITY SENSITIVITY TYPE II ERROR", 9,
           ["Accuracy", "PPV", "Type I error", "Specificity", "Sensitivity", "Type II error"]),
}
SUFFIXES = ["COMPOSITE", "SPLICE-SITE USAGE", "SPLICE-SITES", "SPLICE-JUNCTIONS"]

batch = {}
for line in open(os.path.join(OUT, "batch.jsonl")):
    r = json.loads(line)
    if r["kind"] == "result":
        m = re.match(r"Table (III|IV), row '([^']+)', column '([^']+)'", r["attributes"]["source_locator"])
        batch[m.groups()] = (r["id"], r["attributes"]["printed_value"])

rows, matched = [], 0
for t, (header, page, cols) in HEADERS.items():
    raw = subprocess.run(["pdftotext", "-raw", "-f", str(page), "-l", str(page), PDF, "-"],
                         capture_output=True, text=True, check=True).stdout.split("\n")
    start = raw.index(f"TABLE {t}")
    body = raw[start:start + 60]
    head = " ".join(body[:body.index(next(l for l in body if l.startswith("SPLICEAI")))])
    pos = 0
    for word in header.split():  # header words appear in this order before the first value row
        pos = head.index(word, pos) + len(word)
    for suffix in SUFFIXES:
        k = next(i for i in range(len(body) - 2) if body[i] == "ALPHAGENOME" and body[i + 1] == suffix)
        cells = TOK.findall(body[k + 2])
        assert len(cells) == len(cols), (t, suffix, cells)
        for col, cell in zip(cols, cells):
            rid, printed = batch[(t, "ALPHAGENOME " + suffix, col)]
            ok = printed == cell
            matched += ok
            rows.append((rid, f"Table {t}", "ALPHAGENOME " + suffix, col, cell, printed, "match" if ok else "MISMATCH"))
assert matched == len(batch) == 56, (matched, len(batch))
with open(os.path.join(OUT, "cell-check.tsv"), "w") as f:
    f.write("id\ttable\trow\tcolumn\traw_parse\tprinted_value\tstatus\n")
    for r in sorted(rows):
        f.write("\t".join(r) + "\n")
print(f"{matched} of {len(batch)} AlphaGenome cells match the raw-order parse")
