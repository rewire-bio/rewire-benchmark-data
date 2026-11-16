#!/usr/bin/env python3
"""Reconcile the TraitGym paper's Table S8 with the TraitGym results already in the store.

The 156 stored TraitGym results come from the benchmark's Hugging Face metric CSVs
(`lit-genomics-20261011-traitgym-source-hf-metrics`), not from the paper. Table S8 of
the preprint prints the zero-shot AUPRC of ten gLMs under five scoring approaches on
both datasets: 100 cells. Appendix B.4 says the weighted-average-over-chromosomes
AUPRC is used for zero-shot scores as well as for linear probing, so the two are on
the same basis and the cells are directly comparable.

This script maps each Table S8 cell to the stored result whose `source_locator` names
the matching CSV, rounds the stored full-precision value to three decimal places, and
compares. It also accounts for every stored result that Table S8 does not cover.

Writes `extract/comparison.tsv`.
"""

from __future__ import annotations

import argparse
import csv
import decimal
import glob
import json
import pathlib
import sys

DATASETS = {"Mendelian traits": "mendelian_traits_matched_9",
            "Complex traits": "complex_traits_matched_9"}

# Model label in Table S8 -> the name the benchmark's metric files use.
MODEL_FILES = {
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

# Table S8 column -> the scoring suffix the metric files use. The embedding columns
# map to the `Embeddings.*` files, not to the `InnerProduct`/`EuclideanDistance`
# files, which the store also holds for six Mendelian rows as separate scoring
# variants: GPN_final_EuclideanDistance.plus.score is 0.347, while Table S8's
# GPN-Promoter L2 dist. cell is 0.345, which is Embeddings.plus.euclidean_distance.
SCORE_FILES = {
    "LLR": "LLR.minus.score",
    "abs(LLR)": "absLLR.plus.score",
    "L2 dist.": "Embeddings.plus.euclidean_distance",
    "Cosine dist.": "Embeddings.plus.cosine_distance",
    "Inner prod.": "Embeddings.minus.inner_product",
}

HF_SOURCE = "lit-genomics-20261011-traitgym-source-hf-metrics"
METRIC_DIR = "AUPRC_by_chrom_weighted_average/all"


def load_store(root: pathlib.Path) -> dict[str, dict]:
    records: dict[str, dict] = {}
    for pattern in ("data/entities/*.jsonl", "data/evidence/*/*.jsonl"):
        for path in sorted(glob.glob(str(root / pattern))):
            with open(path, encoding="utf-8") as handle:
                for line in handle:
                    record = json.loads(line)
                    records[record["id"]] = record
    return records


def stored_traitgym_results(records: dict[str, dict]) -> dict[str, dict]:
    """Stored results from the Hugging Face metrics source, keyed by metric CSV path."""
    evaluations = {r["id"] for r in records.values()
                   if r["kind"] == "evaluation" and HF_SOURCE in r.get("source_ids", [])}
    out: dict[str, dict] = {}
    for record in records.values():
        if record["kind"] != "result":
            continue
        links = [l["target_id"] for l in record["links"] if l["relation"] == "evaluation"]
        if not links or links[0] not in evaluations:
            continue
        locator = record["attributes"]["source_locator"]
        path = locator.split(",")[0].strip()
        assert path.endswith(".csv"), f"unexpected locator on {record['id']}: {locator}"
        assert path not in out, f"two stored results for {path}"
        out[path] = record
    assert len(out) == 156, f"expected 156 stored TraitGym results, found {len(out)}"
    return out


def round3(value: str, rounding: str) -> str:
    return str(decimal.Decimal(value).quantize(decimal.Decimal("0.001"), rounding=rounding))


def main() -> int:
    here = pathlib.Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=pathlib.Path, default=here.parents[3],
                        help="repository root (default: four levels above extract/)")
    parser.add_argument("--s8", type=pathlib.Path, default=here / "table-s8.tsv")
    parser.add_argument("--out", type=pathlib.Path, default=here / "comparison.tsv")
    args = parser.parse_args()

    records = load_store(args.root)
    stored = stored_traitgym_results(records)

    with args.s8.open(encoding="utf-8") as handle:
        s8 = list(csv.DictReader(handle, delimiter="\t"))
    assert len(s8) == 100, f"expected 100 Table S8 cells, found {len(s8)}"

    rows: list[dict[str, str]] = []
    used: set[str] = set()
    for cell in s8:
        dataset = DATASETS[cell["dataset"]]
        name = f"{MODEL_FILES[cell['model']]}_{SCORE_FILES[cell['score']]}"
        path = f"{dataset}/{METRIC_DIR}/{name}.csv"
        record = stored.get(path)
        assert record is not None, f"no stored result for {path}"
        used.add(path)
        full = record["attributes"]["printed_value"]
        half_even = round3(full, decimal.ROUND_HALF_EVEN)
        half_up = round3(full, decimal.ROUND_HALF_UP)
        agrees = cell["auprc"] in (half_even, half_up)
        rows.append({
            "status": "matched" if agrees else "DIFFERS",
            "dataset": cell["dataset"],
            "paper_row": cell["model"],
            "paper_column": cell["score"],
            "paper_value": cell["auprc"],
            "stored_result_id": record["id"],
            "stored_value": full,
            "stored_value_rounded_3dp": half_even,
            "stored_metric_file": path,
            "same_protocol": "yes",
            "note": ("weighted-average AUPRC on both sides (paper Appendix B.4)" if agrees
                     else "paper and store disagree at 3 dp"),
        })

    # Account for every stored result Table S8 does not print.
    for path, record in sorted(stored.items()):
        if path in used:
            continue
        name = path.split("/")[-1][: -len(".csv")]
        dataset = "Mendelian traits" if path.startswith("mendelian") else "Complex traits"
        if name.endswith("LogisticRegression.chrom"):
            status, note = "no_paper_counterpart", "linear probing; the paper prints it only in Figure 5"
        elif any(name.startswith(f"{m}_") for m in
                 ("Caduceus", "GPN-MSA", "GPN_final", "HyenaDNA", "NucleotideTransformer")) and (
                 "InnerProduct" in name or "EuclideanDistance" in name):
            status, note = ("no_paper_counterpart",
                            "duplicate scoring variant in the metric files; Table S8 prints the "
                            "Embeddings.* variant of the same score")
        else:
            status, note = ("no_paper_counterpart",
                            "not a gLM zero-shot score; Table S8 covers gLMs only and the paper "
                            "prints this model only in Figure 5")
        rows.append({
            "status": status, "dataset": dataset, "paper_row": "", "paper_column": "",
            "paper_value": "", "stored_result_id": record["id"],
            "stored_value": record["attributes"]["printed_value"],
            "stored_value_rounded_3dp": round3(record["attributes"]["printed_value"],
                                               decimal.ROUND_HALF_EVEN),
            "stored_metric_file": path, "same_protocol": "n/a", "note": note,
        })

    fields = ["status", "dataset", "paper_row", "paper_column", "paper_value",
              "stored_result_id", "stored_value", "stored_value_rounded_3dp",
              "stored_metric_file", "same_protocol", "note"]
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    matched = sum(1 for r in rows if r["status"] == "matched")
    differs = sum(1 for r in rows if r["status"] == "DIFFERS")
    uncovered = sum(1 for r in rows if r["status"] == "no_paper_counterpart")
    print(f"{args.out}: {len(rows)} rows")
    print(f"  matched            {matched}")
    print(f"  DIFFERS            {differs}")
    print(f"  no paper value     {uncovered}")
    assert matched + differs + uncovered == 156, "row accounting does not add up to 156"
    return 1 if differs else 0


if __name__ == "__main__":
    sys.exit(main())
