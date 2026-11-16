#!/usr/bin/env python3
"""Rebuild Extended Data Table 1 from Vision OCR observations.

Input: the tsv written by tools/ocr (x y w h conf text, normalised, origin bottom-left).
Output: a tsv of row label, then the 8 numeric columns in left-to-right order.

No stored value is consulted anywhere in this file.
"""
import sys
import re

path = sys.argv[1]
rows = []
for line in open(path):
    line = line.rstrip("\n")
    if not line or line.startswith("#"):
        continue
    x, y, w, h, conf, text = line.split("\t", 5)
    rows.append((float(x), float(y), float(w), float(h), float(conf), text))

NUM = re.compile(r"^\d+\.\d+$")

# group observations into bands by vertical centre
items = [(x + w / 2.0, y + h / 2.0, x, conf, text) for (x, y, w, h, conf, text) in rows]
items.sort(key=lambda t: -t[1])

bands = []
for it in items:
    placed = False
    for b in bands:
        if abs(b[0] - it[1]) < 0.018:
            b[1].append(it)
            b[0] = sum(q[1] for q in b[1]) / len(b[1])
            placed = True
            break
    if not placed:
        bands.append([it, [it]] if False else [it[1], [it]])
bands.sort(key=lambda b: -b[0])

out = []
for ycentre, members in bands:
    members.sort(key=lambda t: t[0])
    labels = [m for m in members if not NUM.match(m[4])]
    nums = [m for m in members if NUM.match(m[4])]
    if not nums:
        out.append(("LABEL-ONLY/HEADER", ycentre, [m[4] for m in members]))
        continue
    label = " ".join(m[4] for m in labels) if labels else ""
    out.append((label, ycentre, [(round(m[0], 4), m[4], m[3]) for m in nums]))

print("# bands: %d" % len(out))
for label, yc, cells in out:
    if isinstance(cells[0], tuple):
        print("%.4f\t%s\t%s" % (yc, label, "\t".join(c[1] for c in cells)))
        print("#   x: %s" % " ".join("%.3f" % c[0] for c in cells))
        print("#   conf: %s" % " ".join("%.3f" % c[2] for c in cells))
    else:
        print("%.4f\t%s\t%s" % (yc, label, "|".join(cells)))
