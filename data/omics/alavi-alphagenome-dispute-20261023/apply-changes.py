"""Apply the 2026-10-23 Alavi AlphaGenome dispute review to the store, in place.

Reviewed in docs/reviews/2026-10-23-alavi-alphagenome-dispute.md. No printed or numeric value changes.
  1. The 42 results of the nine AlphaGenome evaluations become `disputed`, each with a source warning.
  2. The article source gets an evidence concern scoped by `applies_to` to those nine evaluations.
  3. The multi-gene population text follows Supplemental Table VI, on the dataset and the twelve
     evaluations that repeat it. The previous value is kept in the two metadata-correction claims
     of this batch.
  4. The two relevance judgements move the AlphaGenome evaluations to `excluded_evaluations`, and the
     use-case summary stops quoting the disputed values.
  5. Revision 1 of the discrepancy review names the three multi-gene AlphaGenome evaluations instead of
     their six results, so it stays in the release, and the two multi-gene Borzoi evaluations
     (metadata-correction claim in this batch).

Only the lines of the records it changes are rewritten; it refuses to run twice. Run from the
repository root after `records -- add` of this batch, then `records -- change` and `use-cases:repin`
on the IDs it prints to the file named as its argument.
"""
import glob
import json
import sys

ARTICLE = "rna-splicing-20261011-alavi2026-source-article"
SUPPLEMENT = "rna-splicing-20261011-alavi2026-source-supplementary-tables"
ISSUE_SOURCE = "discrepancy-review-20261022-source-alavi-issue-2"
ISSUE = "https://github.com/marcel-2c8/Probing-genomic-foundation-models-2026/issues/2"
PROTOCOLS = ("multigene", "opa1-evaluation", "opa1-extended-positive-calls")
MODULES = ("either-module", "splice-scorer", "junction-scorer")
DISPUTED = sorted(f"rna-splicing-20261011-alavi2026-eval-{p}-alphagenome-{m}" for p in PROTOCOLS for m in MODULES)
DATASET = "rna-splicing-20261011-alavi2026-data-multigene"
MULTIGENE_PROTOCOL = "rna-splicing-20261011-alavi2026-protocol-multigene"
MAPPINGS = {
    "use-case-mapping-rna-splicing-20261011-alavi2026-multigene": "multigene",
    "use-case-mapping-rna-splicing-20261011-alavi2026-opa1-evaluation": "opa1-evaluation",
}
SUMMARY = "use-case-summary-patient-rna-splicing-validation"
REVIEW = "discrepancy-review-20261022-alavi-alphagenome-splicing"

RESULT_WARNING = (
    "Disputed on 2026-10-23: both AlphaGenome scripts of this source pass a 0-based position to AlphaGenome's "
    "1-based variant API, so every variant was scored one base from its true position. The author accepted the "
    f"bug on 2026-10-20 and is rerunning the analysis ({ISSUE}). The printed value is kept as transcribed until "
    "the rerun is published; do not compare it with other results."
)

CONCERN = {
    "source_id": ARTICLE,
    "message": (
        "The AlphaGenome rows of Tables III, IV and the extended OPA1 positive calls come from scripts that pass a "
        "0-based position to AlphaGenome's 1-based genome.Variant, so each variant was applied one base from its "
        "true position. The author labelled the report a bug on 2026-10-20 and said rerunning with the 1-based "
        "position substantially improved accuracy. The AlphaGenome results are disputed until the rerun is "
        "published; the other models' rows are not affected."
    ),
    "source_locator": (
        "Table III and Table IV, rows 'ALPHAGENOME (SPLICE SCORER)', 'ALPHAGENOME (JUNCTION SCORER)' and "
        "'ALPHAGENOME (EITHER MODULE)'; scripts 2c8_alphagenome_splicescorer.py lines 98 and 120 and "
        "2c8_alphagenome_junctionscorer.py lines 89 and 110 at commit 3c0c6cc; " + ISSUE
    ),
    "artifact_sha256": "e11f4bd8818992a831cb2829d934287c2587b108881c9785c2ef5c8cdc730004",
    "reviewed_at": "2026-10-23T00:00:00Z",
    "review_method": "ai-assisted-source-review",
    "applies_to": DISPUTED,
}

OLD_POPULATION = (
    "76 functionally validated spliceogenic substitutions at canonical splice sites of 65 genes from "
    "Bournazos et al. 2022 (RNA diagnostics in clinically accessible specimens) and Dawes et al. 2023 "
    "(SpliceVault), with 107 high-confidence ClinVar benign intronic substitutions from 46 of the 65 genes"
)
NEW_POPULATION = (
    "76 functionally validated spliceogenic substitutions across 64 gene symbols: 26 at canonical ±1,2 "
    "positions, 35 at near-splice intronic positions (+3 to +7, -3 to -7 and -13) and 15 exonic "
    "substitutions, from Bournazos et al. 2022 (RNA diagnostics in clinically accessible specimens) and "
    "Dawes et al. 2023 (SpliceVault), with 107 high-confidence ClinVar benign intronic substitutions at "
    "±3 to ±10 from 46 of those genes"
)
POPULATION_DETAIL = {
    "positives": 76,
    "positives_canonical_plus_minus_1_2": 26,
    "positives_near_splice_intronic_beyond_2": 35,
    "positives_exonic": 15,
    "benign": 107,
    "gene_symbols": 64,
    "benign_gene_symbols": 46,
    "benign_offsets": "±3 to ±10",
    "basis": "Supplemental_Table_VI.xlsx, 183 data rows, classified by HGVS coding offset (classify-table-vi.py)",
}
SCOPE_NOTE = (
    "The preprint's text calls the positives substitutions 'within the canonical splice sites of 65 genes'; the "
    "population follows the author's per-variant Supplemental Table VI instead. The dataset name keeps the "
    "paper's '65 genes' label."
)

OLD_MULTIGENE_LIMITATION = (
    "Spliceogenic positives are canonical splice-site substitutions only; benign controls are ClinVar intronic "
    "substitutions from 46 of the 65 genes."
)
NEW_MULTIGENE_LIMITATION = (
    "Spliceogenic positives span canonical ±1,2 (26 of 76), near-splice intronic positions from +3 to +7, -3 "
    "to -7 and -13 (35) and exonic substitutions (15), by the paper's Supplemental Table VI, although its text "
    "calls them canonical splice-site variants; benign controls are ClinVar intronic substitutions at ±3 to "
    "±10 from 46 of the 64 gene symbols the table lists."
)
EXCLUSION_REASON = (
    "AlphaGenome's scores came from scripts that scored every variant one base from its true position, which the "
    "author accepted on 2026-10-20 (upstream issue #2). Its results are disputed and the source's evidence "
    "concern names this evaluation, so it is excluded until the rerun is published. Excluded at the 2026-10-23 "
    "review."
)
MAPPING_LIMITATION = (
    "AlphaGenome's three configurations are excluded over the 1-base coordinate offset in its scripts (upstream "
    "issue #2), so the judgement covers SpliceAI, Borzoi, NTv3 650M, Evo2 40B and Genos 10B."
)
OLD_ENDPOINT = "SpliceAI, AlphaGenome, Borzoi and the genomic foundation models"
NEW_ENDPOINT = "SpliceAI, Borzoi and the genomic foundation models"

OLD_SUMMARY = (
    "Alavi (2026, preprint) applied thresholds tuned on OPA1 variants to 76 functionally validated canonical "
    "splice-site variants and 107 ClinVar benign intronic variants from 65 genes: sensitivity and specificity "
    "were 88.2% and 99.1% for SpliceAI, 85.5% and 86.9% for pretrained NTv3 650M, 71.1% and 100% for Evo2 40B "
    "with a human identifier, 56.6% and 80.4% for AlphaGenome (either module) and 27.6% and 85.0% for Genos "
    "10B (Table IV)."
)
NEW_SUMMARY = (
    "Alavi (2026, preprint) applied thresholds tuned on OPA1 variants to 76 functionally validated spliceogenic "
    "variants (26 at canonical ±1,2, 35 at near-splice intronic positions and 15 exonic, by the paper's "
    "Supplemental Table VI) and 107 ClinVar benign intronic variants across 64 genes: sensitivity and "
    "specificity were 88.2% and 99.1% for SpliceAI, 85.5% and 86.9% for pretrained NTv3 650M, 71.1% and 100% "
    "for Evo2 40B with a human identifier and 27.6% and 85.0% for Genos 10B (Table IV). The paper's "
    "AlphaGenome rows are disputed and withheld: its scripts scored every variant one base from its true "
    "position, which the author accepted on 2026-10-20 and is rerunning (upstream issue #2)."
)

changed: list[str] = []


def evaluation_of(record):
    return next((l["target_id"] for l in record["links"] if l["relation"] == "evaluation"), None)


def edit_result(record):
    if evaluation_of(record) not in DISPUTED:
        return False
    assert record["status"] == "source_checked", f"{record['id']} is already {record['status']}"
    record["status"] = "disputed"
    record["attributes"]["source_warnings"] = [*record["attributes"].get("source_warnings", []), RESULT_WARNING]
    return True


def edit_evaluation(record):
    comparison = record["attributes"].get("comparison") or {}
    if comparison.get("protocol_id") != MULTIGENE_PROTOCOL:
        return False
    assert comparison["population"] == OLD_POPULATION, record["id"]
    comparison["population"] = NEW_POPULATION
    return True


def edit_entity(record):
    attributes = record["attributes"]
    if record["id"] == DATASET:
        assert attributes["population"] == OLD_POPULATION, "dataset population already changed"
        attributes["population"] = NEW_POPULATION
        attributes["population_detail"] = POPULATION_DETAIL
        attributes["scope_note"] = SCOPE_NOTE
        record["source_ids"] = [*record["source_ids"], SUPPLEMENT]
        return True
    if record["id"] == ARTICLE:
        assert not attributes.get("evidence_concerns"), "article already carries a concern"
        attributes["evidence_concerns"] = [CONCERN]
        return True
    return False


def edit_claim(record):
    attributes = record["attributes"]
    if record["id"] in MAPPINGS:
        drop = {f"rna-splicing-20261011-alavi2026-eval-{MAPPINGS[record['id']]}-alphagenome-{m}" for m in MODULES}
        kept = [e for e in attributes["reviewed_evaluations"] if e not in drop]
        assert len(kept) == len(attributes["reviewed_evaluations"]) - 3, record["id"]
        attributes["reviewed_evaluations"] = kept
        attributes["excluded_evaluations"] = [
            *attributes.get("excluded_evaluations", []), *({"id": e, "reason": EXCLUSION_REASON} for e in sorted(drop))]
        assert OLD_ENDPOINT in attributes["endpoint"], record["id"]
        attributes["endpoint"] = attributes["endpoint"].replace(OLD_ENDPOINT, NEW_ENDPOINT)
        limitations = [NEW_MULTIGENE_LIMITATION if l == OLD_MULTIGENE_LIMITATION else l for l in attributes["limitations"]]
        attributes["limitations"] = [*limitations, MAPPING_LIMITATION]
        return True
    if record["id"] == REVIEW:
        evaluations = sorted({"-".join(l["target_id"].split("-")[:-1]).replace("-result-", "-eval-")
                              for l in record["links"]})
        assert evaluations == [e for e in DISPUTED if "-multigene-" in e], evaluations
        # Borzoi is the other system of the discrepancy; a resolved finding takes its systems from these.
        borzoi = [f"rna-splicing-20261011-alavi2026-eval-multigene-borzoi-{v}" for v in ("128-bp", "32-bp")]
        record["links"] = [{"relation": "subject", "target_id": e} for e in evaluations + borzoi]
        return True
    if record["id"] == SUMMARY:
        assert OLD_SUMMARY in attributes["value"], "summary sentence not found"
        attributes["value"] = attributes["value"].replace(OLD_SUMMARY, NEW_SUMMARY)
        record["source_ids"] = [*record["source_ids"], SUPPLEMENT, ISSUE_SOURCE]
        attributes["source_locator"] += (
            f"; {SUPPLEMENT}: Supplemental_Table_VI.xlsx, 183 data rows; {ISSUE_SOURCE}: the owner's comment of "
            "2026-10-20"
        )
        return True
    return False


def dumps(record):
    return json.dumps(record, ensure_ascii=False, separators=(",", ":"))


EDITORS = {
    "data/evidence/results/*.jsonl": edit_result,
    "data/evidence/evaluations/*.jsonl": edit_evaluation,
    "data/entities/datasets.jsonl": edit_entity,
    "data/entities/sources.jsonl": edit_entity,
    "data/evidence/claims/*.jsonl": edit_claim,
}

for pattern, editor in EDITORS.items():
    for path in sorted(glob.glob(pattern)):
        lines = open(path, encoding="utf-8").read().splitlines()
        dirty = False
        for i, line in enumerate(lines):
            record = json.loads(line)
            if not editor(record):
                continue
            # The store writes JSON.stringify lines; this serialiser must reproduce them.
            assert dumps(json.loads(line)) == line, f"{record['id']}: line does not round-trip"
            lines[i] = dumps(record)
            changed.append(record["id"])
            dirty = True
        if dirty:
            open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")

print(f"{len(changed)} records changed")
open(sys.argv[1], "w").write("\n".join(changed) + "\n")
