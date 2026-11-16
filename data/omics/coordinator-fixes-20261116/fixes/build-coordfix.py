#!/usr/bin/env python3
"""Build data/omics/coordinator-fixes-20261116/batch.jsonl (correction claims only), and
apply the eleven stored-record edits the claims keep the previous values of.

  python3 -I build-coordfix.py build        write batch.jsonl
  python3 -I build-coordfix.py plan         print the edits, change nothing
  python3 -I build-coordfix.py apply        apply the edits in place (idempotent)
"""
import json, os, hashlib, sys

def _root():
    here = os.path.abspath(os.getcwd())
    while True:
        if os.path.exists(os.path.join(here, "AGENTS.md")) and os.path.isdir(os.path.join(here, "data", "entities")):
            return here
        up = os.path.dirname(here)
        if up == here:
            raise SystemExit("run this from the repository root")
        here = up

ROOT = _root()
BATCH = os.path.join(ROOT, "data/omics/coordinator-fixes-20261116")
REVIEW_DOC = "docs/reviews/2026-11-16-coordinator-fixes.md"

REVIEWER_NOTE = (
    "Claude coordinator-fix agent; no human review claimed. It extracted none of the thirteen "
    "batches of 2026-11-15 and 2026-11-16. Each change is a reviewed correction to a stored record, "
    "justified by a dated review already in the repository and checked here against the store. "
    "Nothing was reproduced and no stored value was recomputed."
)
DATE = "2026-11-16"
AT = "2026-11-16T03:00:00Z"

def review(method, method_note, note, **extra):
    r = {
        "method": method,
        "method_note": method_note,
        "reviewer": ["claude"],
        "reviewer_note": REVIEWER_NOTE,
        "date": DATE,
        "reviewed_at": AT,
        "note": note,
    }
    r.update(extra)
    return r

def claim(cid, name, subject, field, previous, value, locator, rev, sources, areas, contexts=None, description=None):
    facets = {}
    if areas:
        facets["areas"] = areas
    if contexts:
        facets["contexts"] = contexts
    return {
        "id": cid,
        "kind": "claim",
        "name": name,
        "description": description or (
            "Correction made by the 2026-11-16 cross-batch coordinator fix pass. The previous value is kept here."
        ),
        "status": "source_checked",
        "facets": facets,
        "source_ids": sources,
        "links": [{"relation": "subject", "target_id": subject}],
        "attributes": {
            "field": field,
            "previous_value": previous,
            "value": value,
            "source_locator": locator,
            "review": rev,
        },
    }

records = []

# ---------------------------------------------------------------- item 1
SCOPE_OLD = "Predict expression changes after unseen perturbations."
SCOPE_NEW = (
    "Predict expression changes under a held-out perturbation condition. The held-out condition "
    "need not be an agent the model has never seen: a protocol under this task may hold out a dose, "
    "a time point or a cell context of an agent whose other conditions are available in training or "
    "in context, and each protocol record states which. A result under this task is therefore not "
    "evidence of prediction for an unseen perturbing agent unless its protocol says the agent itself "
    "was held out."
)
r1 = review(
    ["ai-assisted-source-review", "scope-review"],
    "Read the task record, every record in the store that links to it, and Appendix D.2 of "
    "arXiv:2607.23447v1, which is the first protocol to link to it. No value was read or recomputed.",
    "The scope note read as a claim that every protocol under this task holds out an unseen "
    "perturbing agent. The PerturbPFN Sci-Plex protocol, the first record in the store to link to "
    "this task, holds out the highest dose of a drug whose lower doses are available, which "
    "Appendix D.2 states. docs/reviews/2026-11-15-perturbpfn.md ruling 7 kept the link and left the "
    "scope note to the coordinator. The wording now covers dose, time and context holdouts and says "
    "a result here is not evidence about an unseen agent. The link, the task identity, the empty "
    "description, the status and the profile were not changed.",
)
records.append(claim(
    "metadata-correction-coordfix-20261116-cell-perturbation-scope-note",
    "Perturbation response: attributes.scope_note",
    "catalog-task-cell-perturbation",
    "attributes.scope_note", SCOPE_OLD, SCOPE_NEW,
    "arXiv:2607.23447v1 Appendix D.2, sentence \"The held-out drug is not completely unseen, since "
    "lower-dose responses are available\"; data/entities/tasks.jsonl, record catalog-task-cell-perturbation",
    r1,
    ["perturbpfn-20261115-source-arxiv-v1"],
    ["cells-tissues"],
))

# ---------------------------------------------------------------- item 2
BEELINE_XML_SHA = "18986b6d4aae64c945146730f35acd5fd591366792a2b441879281b4f09e178e"
BEELINE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7098173/fullTextXML"
DESC_OLD = ("Entry in BEELINE, identified only by its entry label; the model or method behind it is "
            "not identified.")
PROV_OLD = ("Exact source-reported configuration or submission label. Family membership, checkpoint "
            "identity and aliases have not been inferred.")

BEELINE_METHOD_NOTE = (
    "Re-fetched the BEELINE paper's Europe PMC full text XML, the artifact of the stored source "
    "record evidence-discovery-final-beeline, and read its Methods paragraph for the named tool. "
    "The retrieval hashes to " + BEELINE_XML_SHA + ", while the source record pins "
    "99b59a6941878779b34ab8eed9ea27c8d8967c24fb67b92fce418e7f512d3a11 and carries no hash_scope: "
    "Europe PMC regenerates this XML, so the pinned hash does not reproduce. The sentences quoted "
    "here were read from this retrieval. No value was read or recomputed."
)

BEELINE = {
    "grnboost2": {
        "method_id": "perturbpfn-20261115-method-grnboost2",
        "method_name": "GRNBoost2",
        "desc_new": ("Entry in BEELINE for the GRNBoost2 method; the entry gives its label only, so "
                     "no run settings are recorded."),
        "locator": ("Methods, paragraph headed \"GRNBoost2\": \"GRNBoost2 is a fast alternative for "
                    "GENIE3 ... Like GENIE3, GRNBoost2 trains a regression model to select the most "
                    "important regulators for each gene in the dataset. GRNBoost2 achieves its "
                    "efficiency by using stochastic Gradient Boosting Machine regression with "
                    "early-stopping regularization\"; reference 8, Moerman et al., \"GRNBoost2 and "
                    "Arboreto: efficient and scalable inference of gene regulatory networks\""),
        "identity": ("BEELINE's GRNBOOST2 entry is GRNBoost2 from the arboreto package, which is what "
                     "perturbpfn-20261115-method-grnboost2 describes."),
        "ids": {
            "0c21015c": "acquired-configuration-0c21015ca18f77aa85cf",
            "20bd9426": "acquired-configuration-20bd9426a3b1748c4ac0",
            "9ef0d0be": "acquired-configuration-9ef0d0bed99b8227586a",
        },
        "name": "GRNBOOST2",
    },
    "ppcor": {
        "method_id": "perturbpfn-20261115-method-ppcor",
        "method_name": "PPCOR (partial Pearson correlation)",
        "desc_new": ("Entry in BEELINE for the PPCOR partial-correlation method; the entry gives its "
                     "label only, so no run settings are recorded."),
        "locator": ("Methods, paragraph headed \"PPCOR\": \"This R package computes the partial and "
                    "semi-partial correlation coefficients for every pair of variables (genes, in our "
                    "case) with respect to all the other variables ... We use this package to compute "
                    "the partial correlation coefficients\"; reference 7, Kim, \"ppcor: An R Package "
                    "for a Fast Calculation to Semi-partial Correlation Coefficients\""),
        "identity": ("BEELINE's PPCOR entry is the ppcor R package's partial correlation, which is what "
                     "perturbpfn-20261115-method-ppcor describes. BEELINE does not print the word "
                     "Pearson; ppcor's partial correlation is Pearson by default and the paper names "
                     "the same package, so the two records describe one tool."),
        "ids": {
            "4bcb697c": "acquired-configuration-4bcb697cf9c276193491",
            "7b1b949b": "acquired-configuration-7b1b949b9fc16f608074",
            "89290921": "acquired-configuration-89290921419c9429cb59",
        },
        "name": "PPCOR",
    },
}

for key, spec in BEELINE.items():
    for short, rid in spec["ids"].items():
        prov_new = PROV_OLD + (
            " The method this entry configures was established from the BEELINE paper's own Methods "
            "and is recorded as a configuration_of link to " + spec["method_id"] + "; the run settings, "
            "checkpoint identity and aliases behind the label are still not inferred."
        )
        rev_link = review(
            ["ai-assisted-source-review", "source-hash-verification"],
            BEELINE_METHOD_NOTE,
            spec["identity"] + " The entry had an empty links array and no parent. configuration_of is "
            "the relation shared/omics/relations.ts defines for a configuration to the method it "
            "configures, and lit-cells-networks-20261011-ye2026grn-config-grnboost is the store's "
            "precedent for a benchmark entry parented to a method record this way. Left for the "
            "coordinator by docs/reviews/2026-11-15-perturbpfn.md. The entry's status stays discovered: "
            "the parent is now known, the run settings are not.",
            artifact_sha256=BEELINE_XML_SHA,
            retrieval_url=BEELINE_URL,
        )
        records.append(claim(
            "metadata-correction-coordfix-20261116-beeline-%s-%s-link" % (key, short),
            "links:configuration_of:%s: %s in BEELINE (%s)" % (spec["method_id"], spec["name"], short),
            rid,
            "links:configuration_of:%s" % spec["method_id"],
            "No links.",
            "One link: configuration_of %s" % spec["method_id"],
            spec["locator"],
            rev_link,
            ["evidence-discovery-final-beeline", "perturbpfn-20261115-source-arxiv-v1"],
            ["biological-networks", "single-cell"], ["research"],
        ))
        rev_desc = review(
            ["ai-assisted-source-review", "source-hash-verification"],
            BEELINE_METHOD_NOTE,
            "The description said the model or method behind the entry is not identified, which the "
            "configuration_of link makes false, and the provenance note said family membership had not "
            "been inferred. Both now say what is known and what is still not: the method is named, the "
            "run settings are not recorded.",
            artifact_sha256=BEELINE_XML_SHA,
            retrieval_url=BEELINE_URL,
        )
        records.append(claim(
            "metadata-correction-coordfix-20261116-beeline-%s-%s-description" % (key, short),
            "%s in BEELINE (%s): description and attributes.provenance_note" % (spec["name"], short),
            rid,
            "description and attributes.provenance_note",
            "description: %s | attributes.provenance_note: %s" % (DESC_OLD, PROV_OLD),
            "description: %s | attributes.provenance_note: %s" % (spec["desc_new"], prov_new),
            spec["locator"],
            rev_desc,
            ["evidence-discovery-final-beeline", "perturbpfn-20261115-source-arxiv-v1"],
            ["biological-networks", "single-cell"], ["research"],
        ))

# ---------------------------------------------------------------- item 3
r3 = review(
    ["ai-assisted-source-review", "scope-review"],
    "Read the configuration, its source locator, the new OpenFold3 model record and every other "
    "configuration of the same ESMFold2 batch. No value was read or recomputed.",
    "The configuration is named \"OpenFold3 (MSA)\" and had an empty links array, so it had no parent. "
    "poisk-20261115-model-openfold3 is a family-level OpenFold3 model record already in the store. "
    "family is the relation every other configuration of this batch uses to reach its model record, "
    "for example esmfold2-2026-runs-n-poses-method-alphafold3-msa to discovery-model-alphafold-3; "
    "configuration_of would say this configuration belongs to the POISK paper's own run, which it does "
    "not. docs/reviews/2026-11-16-poisk.md ruling 7 identified the orphan, declined to create a "
    "duplicate model record and left the edge to the coordinator. No description, status or "
    "missing_metadata changed: the edge adds a parent and asserts nothing about the checkpoint, which "
    "both records still record as unreported.",
)
records.append(claim(
    "metadata-correction-coordfix-20261116-openfold3-msa-family",
    "links:family:poisk-20261115-model-openfold3: OpenFold3 (MSA)",
    "esmfold2-2026-runs-n-poses-method-openfold3-msa",
    "links:family:poisk-20261115-model-openfold3",
    "No links.",
    "One link: family poisk-20261115-model-openfold3",
    "data/entities/configurations.jsonl, record esmfold2-2026-runs-n-poses-method-openfold3-msa, "
    "source_locator \"Figure 2C Runs N' Poses, bar label OpenFold3 (MSA); Appendix A.2.10\"; "
    "data/entities/models.jsonl, record poisk-20261115-model-openfold3",
    r3,
    ["model-coverage-esmfold2-2026-v1-source", "poisk-20261115-source-manuscript-v1"],
    ["proteins-complexes"],
))

# ---------------------------------------------------------------- item 4
TEXT_LAYER = "c6e95eb807550bb97aa2b8991c013f28fe11742006582c25818fcf90cad30c79"
PDF_SHA = "688e3788e0555b0b1089f474c5cc7dfd22113fdaa168339c1b9f21490fa22646"
HASH_OLD = (
    "SHA-256 of the PDF bytes as downloaded 2026-10-14T12:02:16Z. bioRxiv rewrites the XMP dates and "
    "document IDs, the Info ModDate and the trailer /ID on download, so a re-download does not "
    "reproduce the hash; the review found a fresh copy of the same length differing only in those 51 "
    "bytes, with an identical pdftotext -layout text layer."
)
HASH_NEW = HASH_OLD + (
    " The text layer is the stable check, and this is its hash: pdftotext -layout (poppler 26.08.0) on "
    "a download of the artifact URL writes a 137,403-byte file whose SHA-256 is " + TEXT_LAYER + ". "
    "Every value the store holds from this source was read from that text layer, not from the PDF "
    "bytes. Two further passes confirm it. The 2026-11-16 review of the published version took three "
    "downloads that gave two distinct PDF hashes at one byte length and that same text layer, and a "
    "fourth download on 2026-11-16, 2,247,726 bytes with PDF SHA-256 " + PDF_SHA + ", reproduced it "
    "again."
)
r4 = review(
    ["source-hash-verification", "pdf-text-parse"],
    "Downloaded https://www.biorxiv.org/content/10.1101/2023.10.10.561776v2.full.pdf for this pass. "
    "The first attempts returned HTTP 429 with the 17-byte body \"error code: 1015\", Cloudflare's "
    "rate-limit response; a later attempt returned the PDF, 2,247,726 bytes and 37 pages, SHA-256 "
    + PDF_SHA + ", which is not the pinned artifact_sha256, as expected. pdftotext -layout (poppler "
    "26.08.0) on it wrote a 137,403-byte file hashing to " + TEXT_LAYER + ", the hash ruling 5 of "
    "docs/reviews/2026-11-16-gpn-msa-published.md names. The text layer is this preprint: its first "
    "line reads \"this version posted April 6, 2024\", it carries the CC-BY-NC-ND 4.0 notice, and it "
    "holds the caption \"Supplementary Table 4: Ablation study\" that the stored ablation results are "
    "located at. No stored value was re-read or recomputed.",
    "hash_scope asserted that a fresh download has an identical text layer without naming that "
    "layer's hash, so the check it promises could not be run. It now names the hash, the command and "
    "the poppler version, and records this download's size and PDF hash as a second data point for the "
    "container's instability. artifact_sha256 was not touched: it is not wrong about what was "
    "downloaded on 2026-10-14, and the stored results pin it.",
    artifact_sha256=TEXT_LAYER,
    retrieval_url="https://www.biorxiv.org/content/10.1101/2023.10.10.561776v2.full.pdf",
)
records.append(claim(
    "metadata-correction-coordfix-20261116-gpnmsa-v2-hash-scope",
    "GPN-MSA (bioRxiv v2): hash_scope",
    "gfm-guides-20261014-gpnmsa-source-biorxiv-v2",
    "hash_scope", HASH_OLD, HASH_NEW,
    "One download of https://www.biorxiv.org/content/10.1101/2023.10.10.561776v2.full.pdf on "
    "2026-11-16 and its pdftotext -layout output",
    r4,
    ["gfm-guides-20261014-gpnmsa-source-biorxiv-v2"],
    ["dna-genomes"], ["research"],
))

# ---------------------------------------------------------------- item 5
DUP = "evidence-expansion-p2-phylogpn-2025-807f3a26cbfa"
r5_note = (
    "phylogpn-2025 and " + DUP + " pin the same bytes: both carry artifact_sha256 "
    "807f3a26cbfa9b5ce238d92164bd523302c67d1c5794b08273c51cca1acd4224 and the same Europe PMC "
    "fullTextXML artifact URL. docs/reviews/2026-11-16-phylogpn.md ruling 3 made phylogpn-2025 the "
    "survivor, gave it a supersedes link to the duplicate and set the duplicate's status to superseded, "
    "and left this record's references to the coordinator. This task was the only record still citing "
    "the duplicate. Retargeting the reference withdraws no evidence, because the two records pin one "
    "artifact, and moves no locator. The record stays needs_review and the other three legacy records "
    "behind b2-phylogpn-2025 were left alone: ruling 5 is right that retiring that silo is a decision "
    "of its own."
)
r5_method = (
    "Read both source records, their hashes and URLs, this task record and every record in the store "
    "that cites the duplicate. No source artifact was retrieved and no value was read or recomputed."
)
records.append(claim(
    "metadata-correction-coordfix-20261116-legacy-task-source-ids",
    "ClinVar 3-prime UTR variant classification: source_ids",
    "reported-task-ed3dd3b83c4505",
    "source_ids",
    json.dumps(["phylogpn-2025", DUP]),
    json.dumps(["phylogpn-2025"]),
    "data/entities/sources.jsonl, records phylogpn-2025 and " + DUP + ", both with artifact_sha256 "
    "807f3a26cbfa9b5ce238d92164bd523302c67d1c5794b08273c51cca1acd4224",
    review(["ai-assisted-source-review", "scope-review"], r5_method,
           "The retired duplicate is dropped from source_ids; phylogpn-2025, the survivor, was already "
           "listed, so this removes a redundant pointer to a superseded record. " + r5_note),
    ["phylogpn-2025"],
    ["dna-genomes"],
))
records.append(claim(
    "metadata-correction-coordfix-20261116-legacy-task-primary-sources",
    "ClinVar 3-prime UTR variant classification: attributes.benchmark_research.primary_sources",
    "reported-task-ed3dd3b83c4505",
    "attributes.benchmark_research.primary_sources",
    json.dumps([DUP]),
    json.dumps(["phylogpn-2025"]),
    "data/entities/sources.jsonl, records phylogpn-2025 and " + DUP + ", both with artifact_sha256 "
    "807f3a26cbfa9b5ce238d92164bd523302c67d1c5794b08273c51cca1acd4224",
    review(["ai-assisted-source-review", "scope-review"], r5_method,
           "primary_sources named only the retired duplicate. It now names phylogpn-2025, the same "
           "bytes under the surviving ID. " + r5_note),
    ["phylogpn-2025"],
    ["dna-genomes"],
))

# ---------------------------------------------------------------- item 6
r6 = review(
    ["ai-assisted-source-review", "scope-review"],
    "Read the model record, both GPN-Star source records, ruling 9 of "
    "docs/reviews/2026-11-16-gpn-star.md and the six recommendations in "
    "data/omics/gpn-star-20261116/notes.md. No source artifact was retrieved and no value was read or "
    "recomputed.",
    "The record cited only vep-uc-20261014-source-gpn-star, whose URL is mutable and whose stored hash "
    "pins a preview PDF; the gpn-star review established that the URL now serves the version of record "
    "and added companion_of from that record to gpn-star-20261116-source-nature-2026. Naming the "
    "version of record among this model's sources changes no value, because a model record holds no "
    "measurement, and lit-genomics-20261011-traitgym-benchmark-traitgym was corrected the same way on "
    "2026-11-16 (metadata-correction-traitgym-20261116-benchmark-source-ids). The other five "
    "enrichments ruling 9 lists (status, version, access, licence, training_data) and the family or "
    "variant_of edges to GPN and GPN-MSA are not applied: they are additions carried by claims this "
    "batch's subject already has, not corrections of wrong fields, and the status move is a judgement "
    "about the record's evidence state across the whole pass.",
)
records.append(claim(
    "metadata-correction-coordfix-20261116-gpn-star-source-ids",
    "GPN-Star: source_ids",
    "vep-uc-20261014-model-gpn-star",
    "source_ids",
    json.dumps(["vep-uc-20261014-source-gpn-star"]),
    json.dumps(["vep-uc-20261014-source-gpn-star", "gpn-star-20261116-source-nature-2026"]),
    "data/entities/sources.jsonl, record gpn-star-20261116-source-nature-2026, the version of record "
    "doi:10.1038/s41586-026-11005-5; data/entities/sources.jsonl, record "
    "vep-uc-20261014-source-gpn-star and its companion_of link",
    r6,
    ["gpn-star-20261116-source-nature-2026"],
    ["dna-genomes"], ["research"],
))

# ---------------------------------------------------------------- the stored-record edits
def set_scope_note(rec):
    assert rec["attributes"]["scope_note"] in (SCOPE_OLD, SCOPE_NEW)
    rec["attributes"]["scope_note"] = SCOPE_NEW

def beeline_edit(method_id, desc_new, prov_new):
    def edit(rec):
        links = rec["links"]
        if not any(l["relation"] == "configuration_of" for l in links):
            links.append({"relation": "configuration_of", "target_id": method_id})
        assert links == [{"relation": "configuration_of", "target_id": method_id}], links
        assert rec["description"] in (DESC_OLD, desc_new)
        rec["description"] = desc_new
        assert rec["attributes"]["provenance_note"] in (PROV_OLD, prov_new)
        rec["attributes"]["provenance_note"] = prov_new
    return edit

def openfold3_family(rec):
    if not any(l["relation"] == "family" for l in rec["links"]):
        rec["links"].append({"relation": "family", "target_id": "poisk-20261115-model-openfold3"})
    assert rec["links"] == [{"relation": "family", "target_id": "poisk-20261115-model-openfold3"}]

def set_hash_scope(rec):
    assert rec["attributes"]["hash_scope"] in (HASH_OLD, HASH_NEW)
    rec["attributes"]["hash_scope"] = HASH_NEW

def legacy_task(rec):
    assert rec["source_ids"] in (["phylogpn-2025", DUP], ["phylogpn-2025"]), rec["source_ids"]
    rec["source_ids"] = ["phylogpn-2025"]
    br = rec["attributes"]["benchmark_research"]
    assert br["primary_sources"] in ([DUP], ["phylogpn-2025"]), br["primary_sources"]
    br["primary_sources"] = ["phylogpn-2025"]

def gpn_star_sources(rec):
    want = ["vep-uc-20261014-source-gpn-star", "gpn-star-20261116-source-nature-2026"]
    assert rec["source_ids"] in (["vep-uc-20261014-source-gpn-star"], want), rec["source_ids"]
    rec["source_ids"] = want

EDITS = {
    "catalog-task-cell-perturbation": ("data/entities/tasks.jsonl", set_scope_note),
    "esmfold2-2026-runs-n-poses-method-openfold3-msa": ("data/entities/configurations.jsonl", openfold3_family),
    "gfm-guides-20261014-gpnmsa-source-biorxiv-v2": ("data/entities/sources.jsonl", set_hash_scope),
    "reported-task-ed3dd3b83c4505": ("data/entities/tasks.jsonl", legacy_task),
    "vep-uc-20261014-model-gpn-star": ("data/entities/models.jsonl", gpn_star_sources),
}
for key, spec in BEELINE.items():
    prov_new = PROV_OLD + (
        " The method this entry configures was established from the BEELINE paper's own Methods "
        "and is recorded as a configuration_of link to " + spec["method_id"] + "; the run settings, "
        "checkpoint identity and aliases behind the label are still not inferred."
    )
    for rid in spec["ids"].values():
        EDITS[rid] = ("data/entities/configurations.jsonl",
                      beeline_edit(spec["method_id"], spec["desc_new"], prov_new))

CHANGED_IDS = sorted(EDITS)

def undo_scope_note(rec):
    assert rec["attributes"]["scope_note"] in (SCOPE_OLD, SCOPE_NEW)
    rec["attributes"]["scope_note"] = SCOPE_OLD

def undo_beeline(method_id):
    def edit(rec):
        rec["links"] = [l for l in rec["links"]
                        if not (l["relation"] == "configuration_of" and l["target_id"] == method_id)]
        rec["description"] = DESC_OLD
        rec["attributes"]["provenance_note"] = PROV_OLD
    return edit

def undo_openfold3(rec):
    rec["links"] = [l for l in rec["links"]
                    if not (l["relation"] == "family" and l["target_id"] == "poisk-20261115-model-openfold3")]

def undo_hash_scope(rec):
    rec["attributes"]["hash_scope"] = HASH_OLD

def undo_legacy_task(rec):
    rec["source_ids"] = ["phylogpn-2025", DUP]
    rec["attributes"]["benchmark_research"]["primary_sources"] = [DUP]

def undo_gpn_star(rec):
    rec["source_ids"] = ["vep-uc-20261014-source-gpn-star"]

UNDO = {
    "catalog-task-cell-perturbation": undo_scope_note,
    "esmfold2-2026-runs-n-poses-method-openfold3-msa": undo_openfold3,
    "gfm-guides-20261014-gpnmsa-source-biorxiv-v2": undo_hash_scope,
    "reported-task-ed3dd3b83c4505": undo_legacy_task,
    "vep-uc-20261014-model-gpn-star": undo_gpn_star,
}
for key, spec in BEELINE.items():
    for rid in spec["ids"].values():
        UNDO[rid] = undo_beeline(spec["method_id"])

def run_edits(write, undo=False):
    by_file = {}
    for rid, (relpath, _) in EDITS.items():
        by_file.setdefault(relpath, []).append(rid)
    touched = 0
    for relpath, rids in sorted(by_file.items()):
        full = os.path.join(ROOT, relpath)
        with open(full, encoding="utf-8") as fh:
            lines = fh.read().split("\n")
        out = []
        seen = set()
        for line in lines:
            if not line:
                out.append(line)
                continue
            rec = json.loads(line)
            if rec["id"] in EDITS:
                before = line
                (UNDO[rec["id"]] if undo else EDITS[rec["id"]][1])(rec)
                after = json.dumps(rec, ensure_ascii=False, separators=(",", ":"))
                seen.add(rec["id"])
                if after != before:
                    touched += 1
                    print("EDIT %s in %s" % (rec["id"], relpath))
                else:
                    print("already current %s" % rec["id"])
                out.append(after)
            else:
                out.append(line)
        missing = set(rids) - seen
        assert not missing, missing
        if write:
            with open(full, "w", encoding="utf-8") as fh:
                fh.write("\n".join(out))
    print("%d lines rewritten (write=%s)" % (touched, write))

# ---------------------------------------------------------------- main
mode = sys.argv[1] if len(sys.argv) > 1 else "build"
if mode == "build":
    os.makedirs(BATCH, exist_ok=True)
    path = os.path.join(BATCH, "batch.jsonl")
    with open(path, "w", encoding="utf-8") as fh:
        for rec in sorted(records, key=lambda r: r["id"]):
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    ids = [r["id"] for r in sorted(records, key=lambda r: r["id"])]
    assert len(set(ids)) == len(ids)
    print("%d claims -> %s" % (len(records), path))
    print("sha256", hashlib.sha256(open(path, "rb").read()).hexdigest())
    for i in ids:
        print(" ", i)
elif mode == "plan":
    run_edits(False)
    print("\nchange ids (%d):" % len(CHANGED_IDS))
    print(" ".join(CHANGED_IDS))
elif mode == "apply":
    run_edits(True)
elif mode == "revert":
    run_edits(True, undo=True)
else:
    sys.exit("unknown mode %s" % mode)
