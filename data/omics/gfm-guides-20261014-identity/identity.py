"""Identity fixes for issue #129: duplicate catalog-* and discovery-* records.

Writes batch.jsonl (new claims, status needs_review) and edits the existing
records in the canonical store. Run from the repository root:

    python3 data/omics/gfm-guides-20261014-identity/identity.py

then record the edits and add the claims:

    npm run records -- change docs/reviews/2026-10-14-gfm-guide-record-fixes.md \
        data/omics/gfm-guides-20261014-identity <edited ids printed by this script>
    npm run records -- add data/omics/gfm-guides-20261014-identity/batch.jsonl \
        data/omics/gfm-guides-20261014-identity

The edits are idempotent: a second run finds nothing to change.
"""
import hashlib
import json
from pathlib import Path

BATCH = Path(__file__).parent
DATE = "2026-10-14"
REVIEW = {
    "method": ["scope-review"],
    "reviewer": ["claude"],
    "reviewer_note": "Claude research agent for issue #129; identity resolution from the linked records and their cited sources, not a review. Pending an independent review-evidence pass.",
    "date": DATE,
    "note": "Not reviewed. An alias_of or part_of link counts in navigation only once this claim is source_checked.",
}

# (alias record, canonical record, existing variant_of claim on the alias, evidence)
ALIASES = [
    ("catalog-model-evo-2", "discovery-model-evo-2", "model-evaluation-identity-1cd8474f1b1d39d47971",
     "Both records cite the same official Evo 2 artifacts (evidence-official-a248990b44d481814f47, -849b751ed4bf88622749, -b8df803e8f55324a4eb5, -8717ffb993cc8f7eddec) and carry the same profile. Configurations linked to catalog-model-evo-2 include Evo 2 40B (Alavi 2026) and Evo 2 7B (NABench), so it describes the family, not the 7B checkpoint."),
    ("catalog-model-esm-2", "discovery-model-esm-2", "profile-association-b77dc7ed3e4c0e21c842",
     "Both records cite the same official ESM artifacts (evidence-official-29d4b229a3aa426a6dfb, -d7e5c63feb0e0e627625, -28fc17fbe0c1d99da219). Configurations linked to catalog-model-esm-2 cover the 8M, 150M and 650M checkpoints (PRIME, DeepProtein), so it describes the family, not the 8M checkpoint."),
    ("catalog-model-esmfold", "discovery-model-esmfold", "profile-association-1e3a9f8e48d3e9042bca",
     "Both records cite the same official ESM and ESMFold artifacts (evidence-official-29d4b229a3aa426a6dfb, -fa53ab621979fb5f37c8, -867f2d1dcb4084248daa) and carry the same profile; each holds one family-level ESMFold configuration."),
    ("lit-genomics-20261011-geneb-benchmark-geneb", "discovery-benchmark-geneb", None,
     "Both records describe the GENEB suite in the darlednik/GENEB repository at commit 9642d481e40c0af23995dcd162b779613f789f97: src-discovery-darlednik-geneb is README.md and lit-genomics-20261011-geneb-source-leaderboard is leaderboard/leaderboard.json at the same commit. The leaderboard record is the suite's published aggregate, not a separate benchmark."),
]
# Redundant variant_of links on records that already have a reviewed alias_of between the same pair.
REDUNDANT_VARIANT = [
    ("catalog-model-dnabert-2", "discovery-model-dnabert-2", "profile-association-b98e7ae409d7f83b469e"),
    ("catalog-model-spliceai", "discovery-model-spliceai", "profile-association-10c89dc6780906fcd514"),
    # discovery-model-scgpt is a reviewed alias of catalog-model-scgpt, so this variant_of points
    # the canonical record at its own alias.
    ("catalog-model-scgpt", "discovery-model-scgpt", "profile-association-507834867ec7cde103f9"),
]
# Family records that carry one checkpoint's name as their version.
PREVIOUS_VERSIONS = {
    "catalog-model-evo-2": "7B",
    "catalog-model-esm-2": "8M",
    "catalog-model-esmfold": "v1",
    "catalog-model-dnabert-2": "117M",
    "catalog-model-spliceai": "1.3.1",
    "catalog-model-scgpt": "whole-human",
}
VERSIONS = {
    "catalog-model-evo-2": "Configurations linked to this record include Evo 2 40B and 7B.",
    "catalog-model-esm-2": "Configurations linked to this record include ESM-2 8M, 150M and 650M.",
    "catalog-model-esmfold": "Family record; the evaluated ESMFold version is held on each configuration (for example v1.0.3 in Mahtha et al. 2026).",
    "catalog-model-dnabert-2": "Family record and alias of discovery-model-dnabert-2; the 117M checkpoint is a configuration detail.",
    "catalog-model-spliceai": "Family record and alias of discovery-model-spliceai; package version 1.3.1 is held on the configurations that ran it.",
    "catalog-model-scgpt": "Canonical scGPT family record; configurations linked to it use several checkpoints (whole-human, scGPT 0.2.1, fine-tuned and zero-shot setups).",
}


def short(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:20]


def load(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def main() -> None:
    files = {p: load(p) for p in sorted(Path("data/entities").glob("*.jsonl")) + sorted(Path("data/evidence").glob("*/*.jsonl"))}
    by_id = {r["id"]: r for rows in files.values() for r in rows}
    edited: set[str] = set()
    batch = []

    def claim(cid, subject, name, description, field, attrs, sources, extra_links=()):
        rec = by_id[subject]
        return {
            "id": cid,
            "kind": "claim",
            "name": name,
            "description": description,
            "status": "needs_review",
            "facets": {k: v for k, v in rec.get("facets", {}).items() if k in ("areas", "method_types")},
            "source_ids": sources,
            "links": [{"relation": "subject", "target_id": subject}, *extra_links],
            "attributes": {"field": field, **attrs, "review": REVIEW},
        }

    for alias, canonical, old_claim, evidence in ALIASES:
        rec = by_id[alias]
        # alias_of links model subjects only; a benchmark joins its suite with part_of.
        relation = "part_of" if rec["kind"] == "benchmark" else "alias_of"
        link = {"relation": relation, "target_id": canonical}
        if link not in rec["links"]:
            rec["links"].append(link)
            edited.add(alias)
        sources = sorted(set(rec["source_ids"]) | set(by_id[canonical]["source_ids"]))
        supersedes = [{"relation": "supersedes", "target_id": old_claim}] if old_claim else []
        described = (
            f"{alias} and {canonical} describe the same {rec['kind']}. {canonical} is the canonical record."
            if relation == "alias_of"
            else f"{alias} is the published leaderboard of the suite {canonical}, so it is linked to it with part_of; "
            "the relation contract allows alias_of only between models, methods, configurations, pipelines and services."
        )
        batch.append(claim(
            f"identity-20261014-{short(alias + '|' + relation + '|' + canonical)}", alias,
            f"{rec['name']}: {'alias of' if relation == 'alias_of' else 'part of'} {by_id[canonical]['name']}",
            described
            + (f" Replaces the variant_of claim {old_claim}: a family is not a variant of itself." if old_claim else ""),
            f"links:{relation}:{canonical}",
            {"target_id": canonical, "source_locator": evidence},
            sources, supersedes,
        ))

    for record_id, target, old_claim in REDUNDANT_VARIANT:
        rec = by_id[record_id]
        before = len(rec["links"])
        rec["links"] = [l for l in rec["links"] if not (l["relation"] == "variant_of" and l["target_id"] == target)]
        if len(rec["links"]) != before:
            edited.add(record_id)
        old = by_id[old_claim]
        if old["status"] != "superseded":
            old["status"] = "superseded"
            edited.add(old_claim)

    for record_id, note in VERSIONS.items():
        rec = by_id[record_id]
        attrs = rec["attributes"]
        previous = PREVIOUS_VERSIONS[record_id]
        if "version" in attrs:
            assert attrs.pop("version") == previous, record_id
            attrs.setdefault("missing_metadata", {})["version"] = {"reason": "inapplicable", "note": note}
            rec["attributes"] = dict(sorted(attrs.items()))
            edited.add(record_id)
        batch.append(claim(
            f"metadata-correction-{short(record_id + '|attributes.version')}", record_id,
            f"{rec['name']}: version",
            f"Remove the checkpoint version from a family record. {note}",
            "attributes.version",
            {"previous_value": previous, "value": "absent; missing_metadata.version is inapplicable for a family record",
             "source_locator": f"Records linked to {record_id} by configuration_of and family in the canonical store, release 2026-10-14-a2714d701935"},
            rec["source_ids"],
        ))

    # Rewrite only the edited lines, so every other record keeps its exact bytes.
    for path in files:
        lines = path.read_text().splitlines()
        changed = False
        for i, line in enumerate(lines):
            rid = json.loads(line)["id"] if line else None
            if rid in edited:
                lines[i] = json.dumps(by_id[rid], ensure_ascii=False, separators=(",", ":"))
                changed = True
        if changed:
            path.write_text("".join(line + "\n" for line in lines if line))
    out = BATCH / "batch.jsonl"
    if not out.exists():
        out.write_text("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in batch))
    print(" ".join(sorted(edited)))


if __name__ == "__main__":
    main()
