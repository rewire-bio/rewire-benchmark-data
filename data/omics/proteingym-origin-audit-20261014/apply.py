"""Origin audit of the existing ProteinGym evaluations (issue #161).

Reads the canonical store, decides each evaluation's origin by the rules in
docs/reviews/2026-10-14-proteingym-origin-audit.md, and writes:

- corrections.csv: one row per changed field (record_id, field, old_value, new_value, evidence);
- batch.jsonl: one metadata-correction claim per row, keeping the previous value;
- the edited evaluation lines in data/evidence/evaluations/ (only the origin and, for the AMFR
  rows, the description; every other byte of each line is left as it is).

Run from the repository root: python3 -I data/omics/proteingym-origin-audit-20261014/apply.py
Then record the change with `npm run records -- change` and add batch.jsonl with
`npm run records -- add`. The script refuses to run if any targeted record is not in the state
it expects, so it cannot be applied twice.
"""

import csv
import glob
import hashlib
import json
import os

BATCH = "data/omics/proteingym-origin-audit-20261014"
REVIEW = "docs/reviews/2026-10-14-proteingym-origin-audit.md"
DATE = "2026-10-14"

PAPER_SOURCE = "evidence-expansion-proteingym-a3b08cc4"
PAPER_SHA = "a3b08cc4a6befd64620cf0f287d78d55a36dc2639955f52c5655f83833c50104"
PAPER_URL = "https://papers.nips.cc/paper/2023/file/cac723e5ff29f65e3fcbb0739ae91bee-Paper-Datasets_and_Benchmarks.pdf"
AMFR_SOURCE = "uc20260930-source-proteingym-amfr-spearman"
AMFR_SHA = "f432423b87f79ac9778dfac86e3d95be041d246bc618dc0a406b35b0b7466437"
AMFR_URL = "https://raw.githubusercontent.com/OATML-Markslab/ProteinGym/144fe22b07dfaeec2b366f2346203a9838a55b4c/benchmarks/DMS_zero_shot/substitutions/Spearman/DMS_substitutions_Spearman_DMS_level.csv"
README_SOURCE = "run-doc-proteingym-readme-md-144fe22b"

# Configurations in the paper's Tables 2 to 4 whose method no ProteinGym author developed. The
# ProteinGym authors generated these scores and computed the metrics, so the rows are
# independent_paper. Developer lists are from the paper's reference list.
THIRD_PARTY = {
    "proteingym-method-carp-640m": "CARP: Yang, Lu and Fusi 2023",
    "proteingym-method-esm-1b": "ESM-1b: Rives et al. 2021",
    "proteingym-method-esm-1v-ensemble": "ESM-1v: Meier et al. 2021",
    "proteingym-method-esm-2-15b": "ESM-2: Lin et al. 2023",
    "proteingym-method-esm-if1": "ESM-IF1: Hsu et al. 2022b",
    "proteingym-method-gemme": "GEMME: Laine, Karami and Carbone 2019; scores from the GEMME web tool run by the ProteinGym authors (Appendix A.4.1)",
    "proteingym-method-hmm": "profile HMM: HMMER, Eddy 2011",
    "proteingym-method-mif-st": "MIF-ST: Yang, Zanichelli and Yeh 2023b",
    "proteingym-method-msa-transformer-ensemble": "MSA Transformer: Rao et al. 2021",
    "proteingym-method-progen2-m": "ProGen2: Nijkamp et al. 2022",
    "proteingym-method-progen2-xl": "ProGen2: Nijkamp et al. 2022",
    "proteingym-method-proteinmpnn": "ProteinMPNN: Dauparas et al. 2022",
    "proteingym-method-protgpt2": "ProtGPT2: Ferruz, Schmidt and Hoecker 2022",
    "proteingym-method-provean": "PROVEAN: Choi et al. 2012",
    "proteingym-method-unirep": "UniRep: Alley et al. 2019",
    "proteingym-method-unirep-evotuned": "UniRep: Alley et al. 2019; evotuning by the ProteinGym authors",
    "proteingym-method-vespa": "VESPA: Marquet et al. 2022",
}

# Configurations whose method has at least one ProteinGym author among its developers, or which
# the paper says are defined in Notin et al. 2023 (ProteinNPT; all four authors are ProteinGym
# authors). These keep author_reported.
OWN = {
    "proteingym-method-site-independent": "Hopf et al. 2017 (Marks)",
    "proteingym-method-evmutation": "Hopf et al. 2017 (Marks)",
    "proteingym-method-deepsequence-ensemble": "Riesselman, Ingraham and Marks 2018 (Marks)",
    "proteingym-method-wavenet": "Shin et al. 2021 (Kollasch, Marks)",
    "proteingym-method-eve-ensemble": "Frazer et al. 2021 (Frazer, Notin, Dias, Gal, Marks)",
    "proteingym-method-tranception-l": "Notin et al. 2022a",
    "proteingym-method-tranception-m": "Notin et al. 2022a",
    "proteingym-method-trancepteve-l": "Notin et al. 2022b",
    "proteingym-method-trancepteve-m": "Notin et al. 2022b",
    "proteingym-method-rita-l": "Hesslow et al. 2022 (Notin, Marks)",
    "proteingym-method-rita-xl": "Hesslow et al. 2022 (Notin, Marks)",
    "proteingym-method-npt-proteinnpt": "Notin et al. 2023",
    "proteingym-method-ohe-none": "supervised baseline defined in Notin et al. 2023",
    "proteingym-method-ohe-deepsequence": "supervised baseline defined in Notin et al. 2023",
    "proteingym-method-ohe-esm-1v": "supervised baseline defined in Notin et al. 2023",
    "proteingym-method-ohe-msat": "supervised baseline defined in Notin et al. 2023",
    "proteingym-method-ohe-tranception": "supervised baseline defined in Notin et al. 2023",
    "proteingym-method-ohe-trancepteve": "supervised baseline defined in Notin et al. 2023",
    "proteingym-method-embed-esm-1v": "supervised baseline defined in Notin et al. 2023",
    "proteingym-method-embed-msat": "supervised baseline defined in Notin et al. 2023",
    "proteingym-method-embed-tranception": "supervised baseline defined in Notin et al. 2023",
}

PAPER_LOCATOR = (
    "Section 4.1 'Baselines': 'We implement a diverse set of 50+ zero-shot baselines'; Section 4.2 'Baselines' and "
    "Appendix A.4.2: supervised baselines 'defined in Notin et al. [2023]'; Appendix A.3.3: 'all of the model "
    "predictions can be reproduced using this repository'; Appendix A.4.1 per-baseline scoring; reference list"
)
AMFR_LOCATOR = (
    "DMS_substitutions_Spearman_DMS_level.csv: per-model columns with no scorer field; README.md at 144fe22, "
    "'New baselines' (lines 159-170) and Acknowledgements (line 222)"
)
OLD_AMFR_DESCRIPTION = "Author-reported evaluation, source checked; not independently reproduced."
NEW_AMFR_DESCRIPTION = "Official ProteinGym assay-level Spearman for the AMFR assay at commit 144fe22; transcribed, not reproduced."


def system_of(record):
    return next(link["target_id"] for link in record["links"] if link["relation"] == "system")


def claim_id(record_id, field):
    digest = hashlib.sha256(f"{record_id}\n{field}".encode()).hexdigest()[:20]
    return f"metadata-correction-pgorigin-20261014-{digest}"


def main():
    files = sorted(glob.glob("data/evidence/evaluations/*.jsonl"))
    lines = {f: open(f, encoding="utf-8").read().split("\n") for f in files}
    rows, kept = [], []
    for f, content in lines.items():
        for i, line in enumerate(content):
            if not line:
                continue
            record = json.loads(line)
            rid = record["id"]
            if rid.startswith("proteingym-evaluation-"):
                system = system_of(record)
                if record["attributes"]["origin"] != "author_reported":
                    raise SystemExit(f"{rid}: origin is {record['attributes']['origin']}, expected author_reported")
                if system in OWN:
                    kept.append((rid, system))
                    continue
                if system not in THIRD_PARTY:
                    raise SystemExit(f"{rid}: unclassified system {system}")
                rows.append({
                    "record_id": rid, "field": "attributes.origin", "old_value": "author_reported",
                    "new_value": "independent_paper", "name": record["name"], "source": "paper",
                    "evidence": f"ProteinGym paper: the ProteinGym authors scored this baseline and computed the metric; "
                                f"the method is by authors outside ProteinGym ({THIRD_PARTY[system]})",
                })
                old = '"origin":"author_reported"'
                if content[i].count(old) != 1:
                    raise SystemExit(f"{rid}: origin text not found once")
                content[i] = content[i].replace(old, '"origin":"independent_paper"')
            elif rid.startswith("uc20260930-proteingym-amfr-eval-"):
                if record["attributes"]["origin"] != "author_reported" or record["description"] != OLD_AMFR_DESCRIPTION:
                    raise SystemExit(f"{rid}: not in the expected state")
                rows.append({
                    "record_id": rid, "field": "attributes.origin", "old_value": "author_reported",
                    "new_value": "unreported", "name": record["name"], "source": "amfr",
                    "evidence": "ProteinGym 144fe22 assay-level file does not say who generated each model's scores; "
                                "ProteinGym computed the metric (ruling 2 of docs/reviews/vep-literature-2026-10-14-review.md)",
                })
                rows.append({
                    "record_id": rid, "field": "description", "old_value": OLD_AMFR_DESCRIPTION,
                    "new_value": NEW_AMFR_DESCRIPTION, "name": record["name"], "source": "amfr",
                    "evidence": "The old description said 'Author-reported', which the origin change makes untrue",
                })
                for old, new in (('"origin":"author_reported"', '"origin":"unreported"'),
                                 (json.dumps(OLD_AMFR_DESCRIPTION), json.dumps(NEW_AMFR_DESCRIPTION))):
                    if content[i].count(old) != 1:
                        raise SystemExit(f"{rid}: {old} not found once")
                    content[i] = content[i].replace(old, new)
    for f, content in lines.items():
        open(f, "w", encoding="utf-8").write("\n".join(content))

    rows.sort(key=lambda r: (r["record_id"], r["field"]))
    with open(os.path.join(BATCH, "corrections.csv"), "w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, ["record_id", "field", "old_value", "new_value", "evidence"], extrasaction="ignore",
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    claims = []
    for r in rows:
        paper = r["source"] == "paper"
        what = "origin" if r["field"] == "attributes.origin" else "description"
        summary = f"Correct the {what} from {r['old_value']!r} to {r['new_value']!r} (ProteinGym origin audit, issue #161)." \
            if what == "origin" else "Correct the description, which called the row author-reported (ProteinGym origin audit, issue #161)."
        claims.append({
            "id": claim_id(r["record_id"], r["field"]),
            "kind": "claim",
            "name": f"{r['name']}: {r['field']}",
            "description": summary,
            "status": "needs_review",
            "facets": {},
            "source_ids": [PAPER_SOURCE] if paper else [AMFR_SOURCE, README_SOURCE],
            "links": [{"relation": "subject", "target_id": r["record_id"]}],
            "attributes": {
                "field": r["field"],
                "previous_value": r["old_value"],
                "value": r["new_value"],
                "source_locator": PAPER_LOCATOR if paper else AMFR_LOCATOR,
                "review": {
                    "method": ["source-hash-verification", "automated-source-review"],
                    "reviewer": ["claude"],
                    "reviewer_note": "Claude agent that made the origin judgement and applied it; no separate review yet; no human review claimed",
                    "date": DATE,
                    "method_note": "Re-retrieved the source (SHA-256 matches the source record) and read the passages in source_locator; "
                                   "compared the developers of the evaluated method with the ProteinGym author list.",
                    "artifact_sha256": PAPER_SHA if paper else AMFR_SHA,
                    "retrieval_url": PAPER_URL if paper else AMFR_URL,
                    "note": f"{r['evidence']}. See {REVIEW}.",
                },
            },
        })
    claims.sort(key=lambda c: c["id"])
    with open(os.path.join(BATCH, "batch.jsonl"), "w", encoding="utf-8") as out:
        for c in claims:
            out.write(json.dumps(c, ensure_ascii=False, separators=(",", ":")) + "\n")
    with open(os.path.join(BATCH, "changed-ids.txt"), "w", encoding="utf-8") as out:
        out.write("\n".join(sorted({r["record_id"] for r in rows})) + "\n")
    print(f"changed rows {len(rows)}, records {len({r['record_id'] for r in rows})}, kept author_reported {len(kept)}")


if __name__ == "__main__":
    main()
