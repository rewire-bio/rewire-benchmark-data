#!/usr/bin/env python3
"""Three-way reconciliation of Table S8 for the review pass.

Independent of extract/compare_s8.py. The mapping from a paper cell to a
stored metric file is written out here by hand from the paper's model labels
and the benchmark's file naming, not reused. The reviewer's own reading of
Table S8 (review/s8-reviewer-reading.tsv, written before extract/comparison.tsv
was opened) is the paper side.

Compares, for all 100 cells:
  A  reviewer reading of the paper  vs  stored value rounded to 3 dp
  B  reviewer reading of the paper  vs  the extractor's paper_value
  C  stored value rounded to 3 dp   vs  the extractor's stored_value_rounded_3dp
and also checks that the extractor mapped each cell to the same stored result.

Then accounts for all 156 stored results by metric file, independently.
"""

from __future__ import annotations

import csv
import glob
import json
import re
from decimal import ROUND_HALF_UP, Decimal

STORE = "data/evidence/results/*.jsonl"
BATCH = "data/omics/traitgym-20261116/"
PREFIX = "lit-genomics-20261011-traitgym-result-"

# paper label -> metric-file model stem
MODEL = {
    "GPN-MSA": "GPN-MSA",
    "GPN-Promoter": "GPN_final",
    "NT": "NucleotideTransformer",
    "HyenaDNA": "HyenaDNA",
    "Caduceus": "Caduceus",
    "SpeciesLM": "SpeciesLM",
    "AIDO.DNA": "AIDO.DNA",
    "Evo2 1B": "evo2_1b_base",
    "Evo2 7B": "evo2_7b",
    "Evo2 40B": "evo2_40b",
}
# paper column -> metric-file score suffix
SCORE = {
    "LLR": "_LLR.minus.score",
    "abs(LLR)": "_absLLR.plus.score",
    "L2 dist.": "_Embeddings.plus.euclidean_distance",
    "Cosine dist.": "_Embeddings.plus.cosine_distance",
    "Inner prod.": "_Embeddings.minus.inner_product",
}
DATASET = {"Mendelian traits": "mendelian_traits_matched_9", "Complex traits": "complex_traits_matched_9"}

# the files whose Embeddings twin Table S8 prints; a second published scoring
# variant of the same quantity, Mendelian only
DUPLICATES = {
    "Caduceus_InnerProduct.minus.score",
    "GPN-MSA_InnerProduct.minus.score",
    "GPN_final_EuclideanDistance.plus.score",
    "GPN_final_InnerProduct.minus.score",
    "HyenaDNA_InnerProduct.minus.score",
    "NucleotideTransformer_InnerProduct.minus.score",
}
NON_GLM = {
    "Borzoi_L2_L2.plus.all", "CADD.plus.RawScore", "Enformer_L2_L2.plus.all",
    "Sei.plus.seqclass_max_absdiff", "phastCons-43p.plus.score",
    "phyloP-100v.plus.score", "phyloP-241m.plus.score",
}


def r3(x: str) -> str:
    return str(Decimal(x).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))


def load_store():
    out = {}
    for f in glob.glob(STORE):
        for line in open(f):
            if PREFIX not in line:
                continue
            r = json.loads(line)
            if r.get("kind") != "result" or not r["id"].startswith(PREFIX):
                continue
            m = re.match(r"^(\S+?)/AUPRC_by_chrom_weighted_average/all/(.+?)\.csv,", r["attributes"]["source_locator"])
            assert m, r["id"]
            out[(m.group(1), m.group(2))] = r
    assert len(out) == 156, len(out)
    return out


def main() -> int:
    store = load_store()

    mine = {}
    with open(BATCH + "review/s8-reviewer-reading.tsv") as f:
        cols = f.readline().rstrip("\n").split("\t")[2:]
        for line in f:
            p = line.rstrip("\n").split("\t")
            for c, v in zip(cols, p[2:]):
                mine[(p[0], p[1], c)] = v
    assert len(mine) == 100, len(mine)

    extractor = {}
    with open(BATCH + "extract/comparison.tsv") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if row["status"] != "matched":
                continue
            extractor[(row["dataset"], row["paper_row"], row["paper_column"])] = row
    assert len(extractor) == 100, len(extractor)

    rows, a_diff, b_diff, c_diff, map_diff = [], [], [], [], []
    used = set()
    for (ds, model, col), paper in sorted(mine.items()):
        fn = MODEL[model] + SCORE[col]
        key = (DATASET[ds], fn)
        assert key in store, key
        used.add(key)
        stored = store[key]["attributes"]["numeric_value"]
        rounded = r3(stored)
        ex = extractor.get((ds, model, col))
        assert ex is not None, (ds, model, col)
        if paper != rounded:
            a_diff.append((ds, model, col, paper, rounded))
        if paper != ex["paper_value"]:
            b_diff.append((ds, model, col, paper, ex["paper_value"]))
        if rounded != ex["stored_value_rounded_3dp"]:
            c_diff.append((ds, model, col, rounded, ex["stored_value_rounded_3dp"]))
        if ex["stored_result_id"] != store[key]["id"]:
            map_diff.append((ds, model, col, store[key]["id"], ex["stored_result_id"]))
        rows.append([ds, model, col, paper, ex["paper_value"], stored, rounded,
                     ex["stored_value_rounded_3dp"], store[key]["id"], ex["stored_result_id"],
                     "ok" if (paper == rounded == ex["paper_value"] == ex["stored_value_rounded_3dp"]
                              and ex["stored_result_id"] == store[key]["id"]) else "DIFFERS"])

    with open(BATCH + "review/reconcile-s8.tsv", "w") as f:
        f.write("\t".join(["dataset", "model", "column", "reviewer_paper_value", "extractor_paper_value",
                           "stored_value", "reviewer_rounded_3dp", "extractor_rounded_3dp",
                           "reviewer_mapped_result", "extractor_mapped_result", "status"]) + "\n")
        for r in rows:
            f.write("\t".join(r) + "\n")

    print(f"cells: {len(rows)}")
    print(f"A reviewer paper reading vs stored rounded : {len(a_diff)} differences {a_diff or ''}")
    print(f"B reviewer paper reading vs extractor paper: {len(b_diff)} differences {b_diff or ''}")
    print(f"C reviewer rounding vs extractor rounding  : {len(c_diff)} differences {c_diff or ''}")
    print(f"D cell-to-stored-result mapping            : {len(map_diff)} differences {map_diff or ''}")

    # --- accounting of the other 56 ---
    rest = {k: v for k, v in store.items() if k not in used}
    assert len(rest) == 56, len(rest)
    groups = {"linear_probing": [], "non_glm_zero_shot": [], "duplicate_variant": [], "UNEXPLAINED": []}
    for (ds, fn), r in sorted(rest.items()):
        if fn.endswith(".LogisticRegression.chrom"):
            groups["linear_probing"].append((ds, fn))
        elif fn in NON_GLM:
            groups["non_glm_zero_shot"].append((ds, fn))
        elif fn in DUPLICATES:
            groups["duplicate_variant"].append((ds, fn))
        else:
            groups["UNEXPLAINED"].append((ds, fn))
    print("\naccounting of the other 56 stored results:")
    for g, v in groups.items():
        print(f"  {g}: {len(v)}")
    assert not groups["UNEXPLAINED"], groups["UNEXPLAINED"]

    # every linear-probing system must be absent from Table S8 (it prints zero-shot only)
    lp_systems = sorted({fn.removesuffix(".LogisticRegression.chrom") for _d, fn in groups["linear_probing"]})
    print(f"  linear probing systems ({len(lp_systems)}): {', '.join(lp_systems)}")
    # every non-gLM system on both datasets
    import collections
    per = collections.Counter(fn for _d, fn in groups["non_glm_zero_shot"])
    assert set(per) == NON_GLM and set(per.values()) == {2}, per
    print(f"  non-gLM zero-shot systems on both datasets: {len(per)} x 2")

    # are the duplicate variants genuinely distinguishable from the Embeddings twin?
    print("\nduplicate scoring variants: does the paper cell discriminate the two files?")
    twin = {
        "Caduceus_InnerProduct.minus.score": ("Caduceus", "Inner prod."),
        "GPN-MSA_InnerProduct.minus.score": ("GPN-MSA", "Inner prod."),
        "GPN_final_EuclideanDistance.plus.score": ("GPN-Promoter", "L2 dist."),
        "GPN_final_InnerProduct.minus.score": ("GPN-Promoter", "Inner prod."),
        "HyenaDNA_InnerProduct.minus.score": ("HyenaDNA", "Inner prod."),
        "NucleotideTransformer_InnerProduct.minus.score": ("NT", "Inner prod."),
    }
    undetermined = []
    for fn, (model, col) in sorted(twin.items()):
        dup = store[("mendelian_traits_matched_9", fn)]["attributes"]["numeric_value"]
        emb = store[("mendelian_traits_matched_9", MODEL[model] + SCORE[col])]["attributes"]["numeric_value"]
        paper = mine[("Mendelian traits", model, col)]
        verdict = ("discriminates" if r3(dup) != r3(emb)
                   else "SAME at 3 dp: mapping not determined by the printed value")
        if r3(dup) == r3(emb):
            undetermined.append((fn, paper))
        print(f"  {fn}: paper {paper}, Embeddings twin {r3(emb)} ({emb}), variant {r3(dup)} ({dup}) -> {verdict}")
        assert paper == r3(emb), (fn, paper, r3(emb))
    print(f"\ncells whose file mapping the printed value alone does not fix: {len(undetermined)}")
    bad = len(a_diff) + len(b_diff) + len(c_diff) + len(map_diff)
    print("\nOK" if bad == 0 else "\nDIFFERENCES FOUND")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
