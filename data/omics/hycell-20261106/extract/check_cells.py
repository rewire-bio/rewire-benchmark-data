"""Independent placement of the HyCell cells that check-values left at in_row or did
not parse. A second parse with pdftotext -raw, a different text mode from the
-layout parse, anchored at each table's own caption and stopped at the next one,
must give the same ordered value sequence for every row of Tables 3, 4 and 5 and
of Figure 1b. Anchoring each table to its own caption is what rules out a
shared-window false pass between Tables 3 and 4, which repeat row labels and in
places values.

Usage: python3 -I check_cells.py <pdf> <out.tsv>
"""

import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parse import ATLASES, FIG1B_MODELS, MODELS, PRINTED, TABLE5_ATLASES, parse

V = r"0\.\d{3}"


def region(text, start, stop):
    body = text[text.index(start):]
    return body[:body.index(stop)]


def rows(body, labels, n, printed=None):
    printed = printed or {}
    out, cursor = {}, 0
    for label in labels:
        shown = printed.get(label, label)
        # A row is a line that holds the label and at least n values after it; a caption
        # or prose mention of the same name carries no values and is skipped.
        pat = re.compile(r"(?m)(?:^|\s)" + re.escape(shown) + r"(?=\s)(?P<tail>[^\n]*)$")
        for m in pat.finditer(body, cursor):
            values = re.findall(V, m.group("tail"))
            if len(values) >= n:
                break
        else:
            raise AssertionError((label, shown))
        out[label] = values[-n:]
        cursor = m.end()
    return out


def main(pdf, out_path):
    p = parse(pdf)
    raw = subprocess.run(["pdftotext", "-raw", pdf, "-"], check=True,
                         capture_output=True).stdout.decode()
    checked = []
    t3 = rows(region(raw, "Table 3: Zero-shot embeddings", "Table 4: Score S"), MODELS, 5, PRINTED)
    for m in MODELS:
        assert t3[m] == [p["table3"][m][c] for c in ["S", "Bio", "Batch", "LR", "kNN"]], ("T3", m, t3[m])
        checked.append(("Table 3", m))
    t4 = rows(region(raw, "Table 4: Score S", "3.2 Results"), MODELS, 7, PRINTED)
    for m in MODELS:
        assert t4[m] == list(p["table4"][m].values()), ("T4", m, t4[m])
        checked.append(("Table 4", m))
    t5 = rows(region(raw, "Table 5: Annotation", "6 Availability"), TABLE5_ATLASES, 3)
    for a in TABLE5_ATLASES:
        r = p["table5"][a]
        assert t5[a] == [r["Fine-tuned"], r["Frozen + LR"], r["Frozen + kNN"]], ("T5", a, t5[a])
        checked.append(("Table 5", a))
    # Raw mode prints Figure 1b's rotated column headers as plain words, in order, just
    # before the matrix, so it confirms the column identities the layout parse inferred.
    f1_body = region(raw, "batch-grouped inference\n", "a Zero-shot score on 7 held-out atlases")
    headers = f1_body[len("batch-grouped inference\n"):].split("Immune ")[0].split()
    assert headers == ["HyCell", "UCE", "Stack", "scFoundation", "scGPT", "Tahoe-x1"], headers
    assert [h for h in headers] == [m.split(" (")[0] for m in FIG1B_MODELS], headers
    f1 = rows(f1_body, ATLASES + ["Mean"], 6)
    for a in ATLASES + ["Mean"]:
        assert f1[a] == [p["figure1b"][(a, m)] for m in FIG1B_MODELS], ("F1b", a, f1[a])
        checked.append(("Figure 1b", a))
    with open(out_path, "w") as handle:
        handle.write("table\trow\tcheck\n")
        for table, label in checked:
            handle.write(f"{table}\t{label}\traw sequence equal to the layout parse\n")
    print(f"{len(checked)} rows checked, all equal")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
