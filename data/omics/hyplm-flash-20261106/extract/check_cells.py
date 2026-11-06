"""Independent cell checks for the values scripts/omics/batch.py check-values could
place only in their row (in_row) or not at all (locator_not_parsed).

1. A second parse with pdftotext -raw, a different text mode from the -layout parse,
   must give the same ordered value sequence for every row of Tables 3, 5, 6 and 7.
2. Table 3: each PPL must equal exp(NLL) at its printed precision, which fixes NLL
   against PPL within each panel.
3. Table 5: each row's printed average must equal the mean of its five categories.

Usage: python3 -I check_cells.py <pdf> <out.tsv>
"""

import math
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parse import (TABLE3_MODELS, TABLE5_ROWS, TABLE6_MODELS, TABLE7_MODELS, TASKS, parse)

VALUE = r"[−-]?\d\.\d{2,3}|–"


def raw_rows(pdf, labels, caption, stop):
    text = subprocess.run(["pdftotext", "-raw", pdf, "-"], check=True,
                          capture_output=True).stdout.decode()
    body = text[text.index(caption):]
    body = body[:body.index(stop)] if stop in body else body
    out, cursor = {}, 0
    for label in labels:
        # A row starts a line, optionally after a rank number; a caption mention does not.
        m = re.compile(r"(?m)^(?:\d+\s+)?" + re.escape(label) + r"\s").search(body, cursor)
        assert m, (caption, label)
        j = body.index("\n", m.end())
        out[label] = re.findall(VALUE, body[m.end():j])
        cursor = j
    return out


def main(pdf, out_path):
    parsed = parse(pdf)
    rows = []
    t3 = raw_rows(pdf, TABLE3_MODELS, "Table 3: Masked-residue likelihood", "Outlook.")
    for model, values in t3.items():
        mine = parsed["table3"][model]
        layout = [mine["nll_uniref"], mine["ppl_uniref"], mine["nll_pdb"], mine["ppl_pdb"]]
        assert values == layout, ("Table 3", model, values, layout)
        for nll, ppl in [(layout[0], layout[1]), (layout[2], layout[3])]:
            # NLL is printed to 3 dp and PPL to 2 dp, so the printed PPL must lie within
            # exp of the NLL's rounding interval, widened by PPL's own half unit.
            low = math.exp(float(nll) - 0.0005) - 0.005
            high = math.exp(float(nll) + 0.0005) + 0.005
            assert low - 1e-9 <= float(ppl) <= high + 1e-9, (model, nll, ppl, low, high)
        rows.append(("Table 3", model, "raw sequence equal; PPL = exp(NLL)"))
    t5 = raw_rows(pdf, TABLE5_ROWS, "Table 5: Top of the ProteinGym", "Table 6:")
    for label, values in t5.items():
        mine = parsed["table5"][label]
        cols = ["Activity", "Binding", "Expression", "Organismal fitness", "Stability", "Average"]
        assert values == [mine[c] for c in cols], ("Table 5", label, values)
        mean = sum(float(mine[c]) for c in cols[:5]) / 5
        # Each category is rounded to 3 dp (mean error up to 0.0005) and the average is
        # rounded on its own (another 0.0005), so the bound is 0.001.
        assert abs(mean - float(mine["Average"])) <= 0.001 + 1e-9, (label, mean)
        rows.append(("Table 5", label, "raw sequence equal; average = mean of five"))
    labels = [t for t, _ in TASKS]
    for caption, models, stop, table in [
            ("Table 6: All tasks, part 1", TABLE6_MODELS, "Table 7:", "Table 6"),
            ("Table 7: All tasks, part 2", TABLE7_MODELS, "\f13", "Table 7")]:
        raw = raw_rows(pdf, labels, caption, stop)
        for task, values in raw.items():
            layout = [parsed["tasks"].get((task, m), "–") for m in models]
            assert values == layout, (table, task, values, layout)
            rows.append((table, task, "raw sequence equal"))
    with open(out_path, "w") as handle:
        handle.write("table\trow\tcheck\n")
        for row in rows:
            handle.write("\t".join(row) + "\n")
    print(f"{len(rows)} rows checked, all equal")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
