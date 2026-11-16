#!/usr/bin/env python3
"""Check every compiled Table 2 cell against the BEND values already in the store.

Table 2's caption says "We report the best result among models in each family", and the
DNABERT, GENA-LM, HyenaDNA and Nucleotide Transformer rows and the Expert Method row are
reproduced from Marin et al. (BEND). This script recomputes each of those 35 cells from
the stored BEND results and reports where the printed value is not the family maximum.
It also reports which family subset, if any, reproduces every printed cell of a row.

Usage:
  python3 -I family-best.py <repo-root> <batch.jsonl>
"""

import glob
import itertools
import json
import os
import sys

# BEND members of each printed Table 2 family row, by stored result ID stem.
FAMILIES = {
    "DNABERT": ["dnabert", "dnabert-2"],
    "GENA-LM": ["gena-lm-bert", "gena-lm-bigbird"],
    "HyenaDNA": ["hyenadna-large", "hyenadna-tiny"],
    "Nucleotide Transformer": ["nt-h", "nt-ms", "nt-1000g", "nt-v2"],
}
# Printed Table 2 column -> stored BEND result suffix.
COLUMNS = {
    "Gene Finding (MCC)": "gene-finding-mcc",
    "Enhancer Annotation (AUPRC)": "enhancer-auprc",
    "Chromatin Accessibility (AUROC)": "chromatin-auroc",
    "Histone Modification (AUROC)": "histone-auroc",
    "CpG Methylation (AUROC)": "cpg-auroc",
    "Expression VEP (AUROC)": "variant-expression-auroc",
    "Disease VEP (AUROC)": "variant-disease-auroc",
}
EXPERT = {
    "Gene Finding (MCC)": "augustus-gene-finding-mcc",
    "Enhancer Annotation (AUPRC)": "enformer-enhancer-auprc",
    "Chromatin Accessibility (AUROC)": "basset-chromatin-auroc",
    "Histone Modification (AUROC)": "basset-histone-auroc",
    "CpG Methylation (AUROC)": "basset-cpg-auroc",
    "Expression VEP (AUROC)": "deepsea-variant-expression-auroc",
    "Disease VEP (AUROC)": "deepsea-variant-disease-auroc",
}
ROW_SLUG = {"DNABERT": "dnabert", "GENA-LM": "gena-lm", "HyenaDNA": "hyenadna",
            "Nucleotide Transformer": "nucleotide-transformer"}
COL_SLUG = {"Gene Finding (MCC)": "gene-finding", "Enhancer Annotation (AUPRC)": "enhancer",
            "Chromatin Accessibility (AUROC)": "chromatin",
            "Histone Modification (AUROC)": "histone", "CpG Methylation (AUROC)": "cpg",
            "Expression VEP (AUROC)": "expression-vep", "Disease VEP (AUROC)": "disease-vep"}


def stored_bend(root):
    values = {}
    for path in glob.glob(os.path.join(root, "data/evidence/results/*.jsonl")):
        for line in open(path):
            record = json.loads(line)
            if record["id"].startswith("bend-result-"):
                values[record["id"][len("bend-result-"):]] = record["attributes"]["printed_value"]
    return values


def printed(batch):
    values = {}
    for line in open(batch):
        record = json.loads(line)
        if record["kind"] != "result":
            continue
        locator = record["attributes"].get("source_locator", "")
        if locator.startswith("Table 2, row '"):
            row = locator.split("row '")[1].split("'")[0]
            col = locator.split("column '")[1].split("'")[0]
            values[(row, col)] = (record["id"], record["attributes"]["printed_value"])
    return values


def main():
    root, batch = sys.argv[1], sys.argv[2]
    bend = stored_bend(root)
    cells = printed(batch)
    mismatches = []

    print("Expert Method row against the stored BEND expert values")
    for col, stem in EXPERT.items():
        rid, value = cells[("Expert Method", col)]
        stored = bend.get(stem)
        flag = "match" if stored == value else f"MISMATCH (stored {stored})"
        print(f"  {col:34s} printed {value}  {flag}")
        if stored != value:
            mismatches.append((rid, "Expert Method", col, value, stored))

    for row, members in FAMILIES.items():
        print(f"\n{row} row against the maximum of the stored BEND family values")
        for col, suffix in COLUMNS.items():
            rid, value = cells[(row, col)]
            member_values = {m: bend.get(f"{m}-{suffix}") for m in members}
            have = {m: v for m, v in member_values.items() if v is not None}
            best = max(have.values(), key=float) if have else None
            flag = "match" if best == value else f"NOT THE MAXIMUM (stored max {best})"
            print(f"  {col:34s} printed {value}  members {have}  {flag}")
            if best != value:
                mismatches.append((rid, row, col, value, best))

        # Which subset of the family, if any, reproduces every printed cell of this row?
        fits = []
        for size in range(1, len(members) + 1):
            for subset in itertools.combinations(members, size):
                ok = True
                for col, suffix in COLUMNS.items():
                    _rid, value = cells[(row, col)]
                    have = [bend[f"{m}-{suffix}"] for m in subset if f"{m}-{suffix}" in bend]
                    if not have or max(have, key=float) != value:
                        ok = False
                        break
                if ok:
                    fits.append(subset)
        print(f"  family subsets reproducing all 7 printed cells: {fits or 'none'}")

    print(f"\n{len(mismatches)} of 35 compiled cells are not the stored value or family maximum:")
    for rid, row, col, value, stored in mismatches:
        print(f"  {rid}: {row} / {col}: printed {value}, stored {stored}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
