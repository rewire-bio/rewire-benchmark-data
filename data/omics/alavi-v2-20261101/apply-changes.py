"""Apply the 2026-11-01 Alavi v2 review to the stored use-case claims, in place.

Reviewed in docs/reviews/2026-11-01-alavi-v2-rerun.md. No result value changes.
  1. The two relevance judgements on the multi-gene and OPA1 evaluation protocols list the four version 2
     AlphaGenome evaluations of their protocol as reviewed, cite version 2, and say that the version 1
     AlphaGenome evaluations stay excluded.
  2. The use-case summary replaces the sentence saying the AlphaGenome rows are being rerun with the rerun
     values from version 2 Table IV.

Only the lines of the records it changes are rewritten; it refuses to run twice. Run from the repository root
after `records -- add` of this batch, then `records -- change` and `use-cases:repin` on the IDs it prints to
the file named as its argument.
"""
import glob
import json
import sys

V2 = "rna-splicing-20261101-alavi2026-v2-source-article"
P = "rna-splicing-20261101-alavi2026-v2"
KEYS = ("alphagenome-composite", "alphagenome-splice-site-usage", "alphagenome-splice-sites", "alphagenome-splice-junctions")
MAPPINGS = {
    "use-case-mapping-rna-splicing-20261011-alavi2026-multigene": ("multigene", "Table IV; Methods A and D; Results F 'Multi-gene benchmarking'"),
    "use-case-mapping-rna-splicing-20261011-alavi2026-opa1-evaluation": ("opa1-evaluation", "Table III columns 'Accuracy' to 'Type II error'; Methods B, D and I"),
}
SUMMARY = "use-case-summary-patient-rna-splicing-validation"

OLD_LIMITATION = (
    "AlphaGenome's three configurations are excluded over the 1-base coordinate offset in its scripts (upstream "
    "issue #2), so the judgement covers SpliceAI, Borzoi, NTv3 650M, Evo2 40B and Genos 10B."
)
NEW_LIMITATION = (
    "AlphaGenome's three version 1 configurations stay excluded over the 1-base coordinate offset in their "
    "scripts (upstream issue #2). Its four configurations from version 2 of the preprint (posted 2026-10-31) "
    "were rerun with the corrected position and are included."
)
OLD_PREPRINT = "Preprint (bioRxiv v1), not peer reviewed."
NEW_PREPRINT = "Preprint (bioRxiv versions 1 and 2), not peer reviewed; version 2 changed only the AlphaGenome rows."
OLD_ENDPOINT = "SpliceAI, Borzoi and the genomic foundation models"
NEW_ENDPOINT = "SpliceAI, AlphaGenome (version 2 rerun), Borzoi and the genomic foundation models"

OLD_SUMMARY = (
    "The paper's AlphaGenome rows are disputed and withheld: its scripts scored every variant one base from its "
    "true position, which the author accepted on 2026-10-20 and is rerunning (upstream issue #2)."
)
NEW_SUMMARY = (
    "Version 1 of the paper scored every AlphaGenome variant one base from its true position (upstream issue #2), "
    "and those rows are withheld. In version 2, rerun with the corrected position, sensitivity and specificity "
    "were 92.1% and 99.1% for AlphaGenome's splice-junction score, 78.9% and 100% for its splice-site score, "
    "57.9% and 100% for the composite score of AlphaGenome's splicing notebook and 23.7% and 100% for "
    "splice-site usage (Table IV); the four scores used different thresholds, all tuned on OPA1 variants."
)
SUMMARY_VALUES = {  # every number in NEW_SUMMARY, by version 2 result
    "multigene-alphagenome-splice-junctions-sensitivity": "70 (92.1%)",
    "multigene-alphagenome-splice-junctions-specificity": "106 (99.1%)",
    "multigene-alphagenome-splice-sites-sensitivity": "60 (78.9%)",
    "multigene-alphagenome-splice-sites-specificity": "107 (100%)",
    "multigene-alphagenome-composite-sensitivity": "44 (57.9%)",
    "multigene-alphagenome-composite-specificity": "107 (100%)",
    "multigene-alphagenome-splice-site-usage-sensitivity": "18 (23.7%)",
    "multigene-alphagenome-splice-site-usage-specificity": "107 (100%)",
}
batch = {json.loads(l)["id"]: json.loads(l) for l in open("data/omics/alavi-v2-20261101/batch.jsonl")}
for key, printed in SUMMARY_VALUES.items():
    assert batch[f"{P}-result-{key}"]["attributes"]["printed_value"] == printed, key

changed: list[str] = []


def edit_claim(record):
    a = record["attributes"]
    if record["id"] in MAPPINGS:
        pkey, locator = MAPPINGS[record["id"]]
        new = [f"{P}-eval-{pkey}-{k}" for k in KEYS]
        assert all(e in batch for e in new) and not set(new) & set(a["reviewed_evaluations"]), record["id"]
        a["reviewed_evaluations"] = sorted(a["reviewed_evaluations"] + new)
        assert OLD_LIMITATION in a["limitations"] and OLD_PREPRINT in a["limitations"], record["id"]
        a["limitations"] = [NEW_LIMITATION if l == OLD_LIMITATION else NEW_PREPRINT if l == OLD_PREPRINT else l
                            for l in a["limitations"]]
        assert OLD_ENDPOINT in a["endpoint"], record["id"]
        a["endpoint"] = a["endpoint"].replace(OLD_ENDPOINT, NEW_ENDPOINT)
        record["source_ids"] = [*record["source_ids"], V2]
        a["citation_locators"] = [*a["citation_locators"], {"source_id": V2, "locator": locator}]
        a["source_locator"] += f"; {V2}: {locator}"
        return True
    if record["id"] == SUMMARY:
        assert OLD_SUMMARY in a["value"], "summary sentence not found"
        a["value"] = a["value"].replace(OLD_SUMMARY, NEW_SUMMARY)
        record["source_ids"] = [*record["source_ids"], V2]
        a["source_locator"] += f"; {V2}: Table IV, AlphaGenome rows"
        return True
    return False


def dumps(record):
    return json.dumps(record, ensure_ascii=False, separators=(",", ":"))


for path in sorted(glob.glob("data/evidence/claims/*.jsonl")):
    lines = open(path, encoding="utf-8").read().splitlines()
    dirty = False
    for i, line in enumerate(lines):
        record = json.loads(line)
        if not edit_claim(record):
            continue
        assert dumps(json.loads(line)) == line, f"{record['id']}: line does not round-trip"
        lines[i] = dumps(record)
        changed.append(record["id"])
        dirty = True
    if dirty:
        open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")

assert sorted(changed) == sorted([*MAPPINGS, SUMMARY]), changed
print(f"{len(changed)} records changed")
open(sys.argv[1], "w").write("\n".join(changed) + "\n")
