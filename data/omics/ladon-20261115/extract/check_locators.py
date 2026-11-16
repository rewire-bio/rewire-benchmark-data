"""Check that each result's printed value occurs on the PDF page its source_locator names.

npm run batch -- check-values only parses 'Table N' locators, and this report has no tables, so
it lists every result as locator_not_parsed. This script is a weaker, independent check: it takes
the first '(page N)' or 'Page N' in each locator, and looks for the printed value as a whole token
on that page of the pdftotext -layout text layer (and, for values with an interval, the printed
interval as well). It does not check column assignment; parse_figures.py and check_against_web.py do.

Usage: python3 -I extract/check_locators.py batch.jsonl ladon.layout.txt > extract/locator-check.txt
"""

import json
import re
import sys


def main(batch, layout):
    text = open(layout, encoding="utf-8").read().replace("\f", "")
    pages, cur = {}, []
    for line in text.split("\n"):
        m = re.search(r"Ladon · Blank Bio · (\d+) / 47", line)
        if m:
            pages[int(m.group(1))] = " ".join(" ".join(cur).split())
            cur = []
        else:
            cur.append(line)
    bad = 0
    n = 0
    for line in open(batch, encoding="utf-8"):
        r = json.loads(line)
        if r["kind"] != "result":
            continue
        n += 1
        a = r["attributes"]
        m = re.search(r"\(page (\d+)\)|Page (\d+)", a["source_locator"])
        page = int(m.group(1) or m.group(2))
        body = pages[page]
        ok = re.search(r"(?<![\d.])" + re.escape(a["printed_value"]) + r"(?![\d])", body) is not None
        unc = a.get("uncertainty", {}).get("printed")
        if unc:
            ok = ok and " ".join(unc.split()) in body
        print(f"{r['id']}\tpage {page}\t{a['printed_value']}\t{'found' if ok else 'NOT FOUND'}")
        bad += not ok
    print(f"# {n} results, {bad} not found on the named page")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
