#!/usr/bin/env python3
"""Merge the nine new AMP use cases and nineteen new mapping objects into
data/omics/use-cases/inputs.json (additive only; existing 17 use cases and
72 mappings are byte-identical other than array growth), then refresh
data/omics/use-cases/review.json's inputs.json digest and scope note.
Run scripts/omics/fix-amp-mapping-hashes.ts afterwards to replace the
placeholder evidence_sha256 values with the real mappingEvidenceHash.
"""
import hashlib
import json
import os
from pathlib import Path

# Fixed, explicit review completion time -- see build-amp-coverage.py for why
# this is not datetime.now(). Keep these constants in sync across the three
# AMP generator scripts.
REVIEWED_AT_ISO = os.environ.get("AMP_REVIEW_AT_ISO", "2026-10-07T13:38:59.000Z")

ROOT = Path(__file__).resolve().parents[2]
INPUTS = ROOT / "data/omics/use-cases/inputs.json"
REVIEW = ROOT / "data/omics/use-cases/review.json"
DRAFT = ROOT / "data/omics/use-case-coverage-amp-20261007/use-cases-draft.json"


def main():
    inputs = json.loads(INPUTS.read_text())
    draft = json.loads(DRAFT.read_text())
    existing_use_case_ids = {u["id"] for u in inputs["use_cases"]}
    existing_slugs = {u["slug"] for u in inputs["use_cases"]}
    existing_mapping_ids = {m["id"] for m in inputs["mappings"]}
    for u in draft["use_cases"]:
        if u["id"] in existing_use_case_ids or u["slug"] in existing_slugs:
            raise ValueError(f"Use case id/slug already exists: {u['id']} / {u['slug']}")
    for m in draft["mappings"]:
        if m["id"] in existing_mapping_ids:
            raise ValueError(f"Mapping id already exists: {m['id']}")
    before_use_cases = len(inputs["use_cases"])
    before_mappings = len(inputs["mappings"])
    inputs["use_cases"] = inputs["use_cases"] + draft["use_cases"]
    inputs["mappings"] = inputs["mappings"] + draft["mappings"]
    INPUTS.write_text(json.dumps(inputs, indent=2, sort_keys=False) + "\n")
    print(f"use_cases {before_use_cases} -> {len(inputs['use_cases'])}; mappings {before_mappings} -> {len(inputs['mappings'])}")

    review = json.loads(REVIEW.read_text())
    digest = hashlib.sha256(INPUTS.read_bytes()).hexdigest()
    review["files"]["inputs.json"] = digest
    review["reviewed_at"] = REVIEWED_AT_ISO
    review["reviewer"] = review["reviewer"] + "; Claude Sonnet AMP-integration worker, independently reviewed by Codex across two review cycles, for the 2026-10-07 AMP bounded intake (rewire.it#365, rewire-benchmark-data issues #10-19)"
    review["scope"] = review["scope"] + (
        " Same day, add a bounded additive AMP intake (rewire.it#365, rewire-benchmark-data issues #10-19): "
        "nine new use-case definitions (tumour-dna-somatic-variant-detection, tumour-rna-fusion-detection, "
        "patient-rna-splicing-validation, diagnostic-dna-pathogen-identification, diagnostic-rna-pathogen-detection, "
        "plasma-ctdna-fragmentomics, plasma-ctdna-methylation, cnv-detection-characterisation, "
        "diagnostic-genomics-model-execution) and nineteen new mapping objects: ten against the new use cases "
        "(oncology-RNA Lancet/Strelka2 virtual-tumour calling; EnFusion Seraseq synthetic reference standard and a "
        "separate NCH clinical-ascertainment mapping; FRASER known pathogenic splicing-event recovery; Karius DNA "
        "pathogen positive-percent-agreement; UCSF RNA-pathogen mNGS sensitivity; DELFI ctDNA fragmentomics; "
        "cfMethyl-Seq ctDNA methylation; DRAGEN 4.2 CNV 1-5kb deletion F-score; DRAGEN 4.2 single-sample runtime "
        "baseline) and nine proxy mappings onto existing use cases from a bounded Feng et al. 2025 DNA-foundation-"
        "model table expansion: two each for splice acceptor/donor (use-case-splicing-follow-up) and Arabidopsis "
        "promoter TATA/NonTATA (use-case-plant-promoter-reporters), one for pathogenic-versus-common SNP "
        "discrimination (use-case-rare-disease-candidate-ranking), and four (one per QTL type: eQTL/sQTL/paQTL/ipaQTL) "
        "for regulatory-variant-gene-follow-up; reusing the existing evidence-expansion-dna-foundation-models-2025-5d8ca9bc "
        "source unchanged. All 17 prior use cases and 72 prior mapping objects remain byte-identical. New source "
        "records and numerical evidence for this addition are bound by "
        "data/omics/use-case-coverage-amp-20261007/review.json. Automated source review, independently Codex-checked "
        "across two review cycles (workbench/amp-supervision/primary-review.md, "
        "workbench/amp-supervision/integration-review-corrections.md); not qualified human scientific review or "
        "independent experimental reproduction. No broad clinical validation is claimed for any new mapping."
    )
    review["limitations"] = review["limitations"] + [
        "The 2026-10-07 AMP intake's nine new use cases and nineteen new mappings are each a narrow proxy or direct "
        "measurement for one declared endpoint (see each use case's evidence_gaps and each mapping's limitations); "
        "none establishes broad clinical validation, qualified human scientific review, or Rewire model execution. "
        "All prior use cases, mappings and historic release bytes remain unchanged.",
    ]
    REVIEW.write_text(json.dumps(review, indent=2) + "\n")
    print("Updated review.json inputs.json digest to", digest)


if __name__ == "__main__":
    main()
