"""Build data/omics/editjumps-20261115/batch.jsonl from the transcribed tables.

Run from this directory, after check_tables.py has passed:

  python3 -I build_batch.py <text layer of the pinned arXiv PDF> > ../batch.jsonl

Everything the records state about EditJumps comes from one of the nine pinned sources. The
table values come from tables.py, which check_tables.py asserts against the PDF text layer; this
script re-runs those assertions before it writes anything.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_tables  # noqa: E402
import tables as T  # noqa: E402

BATCH = "editjumps-20261115"
DATE = "2026-11-16"
AT = "2026-11-16T00:40:00Z"


def rid(suffix):
    return f"{BATCH}-{suffix}"


# --------------------------------------------------------------------------------- sources
PDF = rid("source-arxiv-pdf-v1")
HTML = rid("source-arxiv-html-v1")
README = rid("source-code-readme")
LICENCE = rid("source-code-licence")
PERF = rid("source-code-performance")
LIMITS = rid("source-code-limitations")
CLAIMS_DOC = rid("source-code-claims")
CARD = rid("source-model-card")
ENCODER = rid("source-model-encoder-config")

PDF_SHA = "4211d8ef46c55efe8d89ba4ee6c0b4e57cca1e78d0856e9cdfbde37046a7f4e1"
PDF_URL = "https://arxiv.org/pdf/2609.18745v1"
COMMIT = "d827d47c3bcd29e0f4c15a15f9ac92a6cd859e99"
REVISION = "44a0ca3e224e16adac0e15e24400d22a17d4db5c"
RAW = f"https://raw.githubusercontent.com/VisiumCH/editjumps/{COMMIT}"
HF_RAW = f"https://huggingface.co/VisiumSA/EditJumps/raw/{REVISION}"

ESM2 = "catalog-model-esm-2"  # existing store identity, reused rather than duplicated

AREAS = ["protein-function", "proteins-complexes"]
FACETS = {"areas": AREAS, "contexts": ["research"]}


def facets(method_types=None, tasks=None):
    out = dict(FACETS)
    if method_types:
        out["method_types"] = method_types
    if tasks:
        out["tasks"] = tasks
    return out


EXTRACTOR_NOTE = (
    "Claude (Opus 5) extraction agent for issue #244; no human review claimed and no review "
    "sign-off claimed. Values were transcribed by hand from the pinned sources and then asserted "
    "against them by extract/check_tables.py, which matches each printed row as a whole so a value "
    "taken from a neighbouring column fails. Nothing was rerun and no value was recomputed."
)


def review(sha, url, note, methods=("transcription", "pdf-text-parse", "source-hash-verification")):
    return {
        "method": list(methods),
        "method_note": (
            "Extraction pass, not a review. Each artifact was downloaded, hashed, and read at the "
            "locator this record names. The arXiv PDF was downloaded twice with identical bytes; its "
            "text layer was produced with pdftotext -layout from poppler 26.08.0."
        ),
        "reviewer": ["claude"],
        "reviewer_note": EXTRACTOR_NOTE,
        "date": DATE,
        "reviewed_at": AT,
        "artifact_sha256": sha,
        "retrieval_url": url,
        "note": note,
    }


PDF_REVIEW = review(PDF_SHA, PDF_URL, "Read at the locator this record names in the pinned version 1 PDF.")


def record(id_, kind, name, description, attributes, links=None, source_ids=None, status="needs_review", extra_facets=None):
    return {
        "id": id_,
        "kind": kind,
        "name": name,
        "description": description,
        "status": status,
        "facets": extra_facets if extra_facets is not None else FACETS,
        "source_ids": source_ids if source_ids is not None else [PDF],
        "links": links or [],
        "attributes": attributes,
    }


records = []


def add(r):
    records.append(r)
    return r["id"]


# ------------------------------------------------------------------------------ limitations
L_IN_SILICO = (
    "Computational distribution comparison only. The value measures how similar generated "
    "sequences are to a reference set of natural sequences; it is not a measured binding "
    "affinity, specificity, stability or retained function."
)
L_REFSET = (
    "Scores depend on the size of the reference set. Expanding the reference alignment from 200 "
    "to 800 homologs alters the normalised spectrum MMD ratio by 50% on Ty1 and 26% on HER2-VH, "
    "which the paper states is large enough to invert method rankings, so the ordering of methods "
    "is not stable across reference-set sizes."
)
L_OVERLAP = (
    "113 of Ty1's and 103 of HER2-VH's 200 reference sequences were present in the training set. "
    "Re-evaluating with strictly disjoint reference sets shifted spectrum MMD by -36.7% on Ty1 and "
    "-12.6% on HER2-VH and increased covariance agreement by 12 to 17 points."
)
L_NOT_COMPARABLE = (
    "The paper states that its computed values and the published EvoFlows values are not comparable "
    "and that it could not recover the original experimental conditions from the EvoFlows paper. "
    "Table 1's caption adds that the two blocks are not comparable and that each row compares only "
    "against its own block's floor and ceiling."
)
L_DOMAIN_SHIFT = (
    "The two held-out targets are single-chain constructs, the camelid VHH Ty1 and the isolated "
    "heavy chain HER2-VH, while the training pairs are concatenated two-chain VH.VL sequences. The "
    "paper names this as a domain shift."
)
L_FRAMEWORK = (
    "Aggregate similarity is substantially driven by conserved framework scaffolds. 76% of residues "
    "are framework and 24% are complementarity-determining regions, and within those regions the "
    "model closes under 25% of the gap between random mutation and natural homologs, so a high "
    "aggregate score is not evidence of a better antigen-binding loop."
)
L_NON_CONVERGED = (
    "The scored editor was trained for 20,000 steps of batch size 16, which the sources state saw "
    "about 19% of one epoch of the training corpus, and the paper states the model remained "
    "non-converged at that budget."
)
L_NO_SEEDS = (
    "Seed values are not printed. Table 1's caption says it reports individual runs and intervals "
    "across three seeds; Table 2 prints one value per cell with no interval."
)
L_UNDEFINED = (
    "The EvoFlows paper names this metric without giving a definition or a scalar reduction, so the "
    "formulation scored here is the EditJumps authors' own choice."
)
L_UNRECOVERABLE = (
    "Reference set size, split, templates, seeds and metric implementation behind these published "
    "values could not be recovered from the EvoFlows paper, so the comparison fields are unknown."
)

OURS_LIMITS = [L_IN_SILICO, L_REFSET, L_OVERLAP, L_DOMAIN_SHIFT, L_FRAMEWORK, L_NO_SEEDS, L_NOT_COMPARABLE]
PUBLISHED_LIMITS = [L_IN_SILICO, L_REFSET, L_NOT_COMPARABLE, L_UNRECOVERABLE]


# ---------------------------------------------------------------------------- source records
CONCERN_APPLIES = []  # filled once the published-block records exist

add(record(
    PDF, "source", "When Edit Flows are Edit Jumps: replicating Edit Flows and EvoFlows (arXiv v1)",
    "The EditJumps paper: the preprint that reformulates Edit Flows and EvoFlows as a pure-jump process, "
    "describes the released editor and reports its evaluation against reimplemented baselines.",
    {
        "url": "https://arxiv.org/abs/2609.18745",
        "artifact_url": PDF_URL,
        "artifact_sha256": PDF_SHA,
        "media_type": "application/pdf",
        "version": "arXiv:2609.18745v1, 16 September 2026",
        "retrieved_at": "2026-11-16T00:03:00Z",
        "publication_status": "preprint",
        "source_locator": "17 pages; Tables 1 to 5 and Figures 1 to 4",
        "retrieval_note": (
            "Downloaded twice from the arXiv version 1 PDF endpoint with identical bytes. The text layer "
            "used for the value assertions is pdftotext -layout output, poppler 26.08.0, SHA-256 "
            "08fa7d4b91c13ddcd5531b66cdec3629427ad1ef9ceef047d785bf1c408617f5."
        ),
        "limitations": [
            "A preprint; the repository badges name the NeurIPS 2026 AIDaR workshop, and no peer-reviewed "
            "version was found.",
            "Figures 1, 2, 3 and 4 carry no printed numeric markers for their series, so the only values "
            "taken from them are the ones the captions and the body print in words.",
            "Table 2 prints two arms, BF-DiT and BF-ESM, that the paper, the repository and the model card "
            "never define, so the system behind those 20 cells cannot be identified.",
            "Table 1 heads the pairwise Levenshtein column 'diversity', while Figure 1's caption defines "
            "diversity as a ratio to real homolog pairs whose values run from about 1.0 to 1.4.",
        ],
        "missing_metadata": {
            "licence": {"reason": "unreported", "note": "No licence statement appears in the PDF; the arXiv abstract page was not pinned as a source."},
            "doi": {"reason": "unreported", "note": "No DOI is printed in the preprint."},
        },
        "evidence_concerns": [{
            "source_id": PDF,
            "message": (
                "The paper states in section 4 that its computed values and the published EvoFlows values "
                "are not comparable and that it could not recover the original experimental conditions from "
                "the EvoFlows paper, and Table 1's caption states that the two blocks are not comparable. "
                "The records carrying EvoFlows' own published values are therefore withheld from automatic "
                "comparison with the reimplemented block, and neither set may be pooled into one leaderboard."
            ),
            "source_locator": "Section 4, first sentence; Table 1 caption; Table 4 caption; Table 5",
            "artifact_sha256": PDF_SHA,
            "review_date": DATE,
            "applies_to": CONCERN_APPLIES,
        }],
        "review": PDF_REVIEW,
    },
))

add(record(
    HTML, "source", "EditJumps paper, arXiv HTML rendering of version 1",
    "The HTML rendering of the EditJumps preprint, whose marked-up tables give each printed cell its own "
    "column heading.",
    {
        "url": "https://arxiv.org/html/2609.18745v1",
        "artifact_url": "https://arxiv.org/html/2609.18745v1",
        "artifact_sha256": "ae0b05f6a7488dabd73990f02b6a6280a6673e0a6a0f2917713f913a5ec3ec4f",
        "media_type": "text/html",
        "version": "arXiv HTML rendering of version 1",
        "retrieved_at": "2026-11-16T00:08:00Z",
        "publication_status": "preprint",
        "source_locator": "Tables 1, 2, 3, 4 and 5 as HTML table markup",
        "retrieval_note": (
            "Used only to confirm which printed column heading each value of Tables 1, 2 and 4 sits under. "
            "No value was taken from it that the PDF does not print; a mutable rendering, so the hash "
            "describes one retrieval."
        ),
        "missing_metadata": {"licence": {"reason": "unreported", "note": "No licence statement in the rendering."}},
        "review": review(
            "ae0b05f6a7488dabd73990f02b6a6280a6673e0a6a0f2917713f913a5ec3ec4f",
            "https://arxiv.org/html/2609.18745v1",
            "Column headings read from the table markup and compared with the PDF text layer.",
            methods=("transcription", "source-hash-verification"),
        ),
    },
    links=[{"relation": "companion_of", "target_id": PDF}],
))


def repo_source(id_, path, sha, name, description, locator, note=None, limitations=None):
    attributes = {
        "url": f"https://github.com/VisiumCH/editjumps/blob/{COMMIT}/{path}",
        "artifact_url": f"{RAW}/{path}",
        "artifact_sha256": sha,
        "media_type": "text/markdown" if path.endswith(".md") else "text/plain",
        "version": f"Commit {COMMIT}",
        "retrieved_at": "2026-11-16T00:05:00Z",
        "publication_status": "official_project_source",
        "source_locator": locator,
        "code_licence": "MIT",
        "code_url": f"https://github.com/VisiumCH/editjumps/tree/{COMMIT}",
        "access_and_reuse": (
            "The MIT grant covers this repository and the released weights. It says nothing about the "
            "pretrained ESM-2 checkpoints or the Observed Antibody Space data the editor is trained on, "
            "which carry their own terms."
        ),
        "review": review(sha, f"{RAW}/{path}", note or "Read at the locator this record names.",
                          methods=("transcription", "source-hash-verification")),
    }
    if limitations:
        attributes["limitations"] = limitations
    return add(record(id_, "source", name, description, attributes,
                      links=[{"relation": "companion_of", "target_id": PDF}], source_ids=[id_]))


repo_source(README, "README.md", "fbf05022b8140519c13bf60db99276df3edcbaeac57f091f54a0dc3921716c05",
            "EditJumps repository README at the pinned commit",
            "The repository front page, which states what the editor takes and returns, how the edit budget "
            "behaves and the frame of the replication evaluation.",
            "'Overview', 'Comparison with Alternatives', 'Replication Scope', 'Quick Start' step 5 and "
            "'Ranking Candidates'")
repo_source(LICENCE, "LICENSE", "9f1abe28a25b5f6f95c58a81a647de3fa72ff6388d228c59bddd079255709989",
            "EditJumps repository licence file at the pinned commit",
            "The licence file granting MIT terms over the repository's code and the released weights.",
            "Lines 1 to 3 and the terms that follow",
            note="The model repository on Hugging Face serves a byte-identical licence file, so the hash does not distinguish them; the URL and revision do.")
repo_source(PERF, "docs/performance.md", "01e59ef27b2e93b118b15239e57c6500045c99facd72f0b956e78ecf161217e3",
            "EditJumps repository performance notes at the pinned commit",
            "The repository's hardware and throughput notes for the training, evaluation and data-build stages.",
            "'Hardware in use'; 'Training', ESM-2 35M Edit-Flow Editor (L4) and 20,000-Step Editor Runs (A100); "
            "'Evaluation and baselines', Generation Evaluation",
            limitations=["Its L4 figures for the same 20,000-step run differ from the paper's and from the model card's."])
repo_source(LIMITS, "docs/limitations.md", "e11bb92210012e08e6a0bc0e6298d098818419f3d661bdae6082c71de9c0b6d8",
            "EditJumps repository scope and limitations note at the pinned commit",
            "The repository's statement of what the editor does not do: no variant scoring, no property "
            "conditioning and only approximate edit budgets.",
            "'Scope and Limitations', the three bullets")
repo_source(CLAIMS_DOC, "docs/claims.md", "7c7103723b23aa8b36e58974717d5a6e4bc368c83167caac9e8954127c0bcfcc",
            "EditJumps repository pipeline claim classification at the pinned commit",
            "The repository's stage-by-stage record of which published decision each pipeline stage "
            "implements and where it deviates.",
            "'reproduction - 14 stages' table and 'Target Property Scope'")

add(record(
    CARD, "source", "EditJumps released model card on Hugging Face",
    "The model card of the released EditJumps weights, which states the trunk, parameter count, training "
    "corpus, objective, optimizer and training budget of the checkpoint.",
    {
        "url": "https://huggingface.co/VisiumSA/EditJumps",
        "artifact_url": f"{HF_RAW}/README.md",
        "artifact_sha256": "552199e1e3be6d07de661baf23876fcbc354f8cfd33b391d2913291a3a5a8c32",
        "media_type": "text/markdown",
        "version": f"Repository revision {REVISION}, last modified 2026-09-23",
        "retrieved_at": "2026-11-16T00:06:00Z",
        "publication_status": "official_project_source",
        "source_locator": "'Model details' table; the paragraph below it; 'License'",
        "licence": "MIT",
        "access_and_reuse": (
            "The card declares MIT for the code and the weights. The stock ESM-2 trunk it builds on and the "
            "Observed Antibody Space corpus it is trained from carry their own separate terms."
        ),
        "limitations": [
            "Two rows of the 'Model details' table carry the authors' own unresolved HTML comments, 'TODO: "
            "confirm head count/names' on the Heads row and 'TODO: confirm step' on the best validation loss row.",
            "Its training cost row and its best validation loss disagree with the paper's Appendix D.",
        ],
        "review": review("552199e1e3be6d07de661baf23876fcbc354f8cfd33b391d2913291a3a5a8c32",
                         f"{HF_RAW}/README.md", "Read at the locator this record names.",
                         methods=("transcription", "source-hash-verification")),
    },
    links=[{"relation": "companion_of", "target_id": PDF}], source_ids=[CARD],
))

add(record(
    ENCODER, "source", "EditJumps released encoder configuration",
    "The encoder configuration file shipped with the released weights, which fixes the trunk's layer count, "
    "hidden width, attention heads, vocabulary size and position encoding.",
    {
        "url": f"https://huggingface.co/VisiumSA/EditJumps/blob/{REVISION}/model/encoder/config.json",
        "artifact_url": f"{HF_RAW}/model/encoder/config.json",
        "artifact_sha256": "5ab36d96756d5a5f78582be7143e89fff113e15f36101f2658d7208d73667be9",
        "media_type": "application/json",
        "version": f"Repository revision {REVISION}",
        "retrieved_at": "2026-11-16T00:06:00Z",
        "publication_status": "official_project_source",
        "source_locator": "architectures, num_hidden_layers, hidden_size, intermediate_size, num_attention_heads, vocab_size, max_position_embeddings, position_embedding_type, dtype",
        "licence": "MIT",
        "review": review("5ab36d96756d5a5f78582be7143e89fff113e15f36101f2658d7208d73667be9",
                         f"{HF_RAW}/model/encoder/config.json", "Every field this record cites was read from the file.",
                         methods=("transcription", "source-hash-verification")),
    },
    links=[{"relation": "companion_of", "target_id": PDF}], source_ids=[ENCODER],
))


# ------------------------------------------------------------------------------- methods
M_EDITJUMPS = rid("method-editjumps")
M_EVOFLOWS = rid("method-evoflows")
M_EDIT_FLOWS = rid("method-edit-flows")
M_EVODIFF_MSA = rid("method-evodiff-msa")
M_EVOTUNING = rid("method-evotuning")

add(record(
    M_EDITJUMPS, "method", "EditJumps",
    "EditJumps proposes related variants of a seed amino-acid sequence by firing single-token insertions, "
    "deletions and substitutions one at a time at learned per-position rates in continuous time, so neither "
    "the edit positions, the edit count nor the output length is fixed in advance.",
    {
        "entity_level": "method",
        "reported_name": "EditJumps",
        "version": "Paper version 1 and repository commit " + COMMIT,
        "access": (
            "Open source under MIT at https://github.com/VisiumCH/editjumps with released weights at "
            "https://huggingface.co/VisiumSA/EditJumps. The pretrained ESM-2 trunk and the Observed Antibody "
            "Space corpus carry their own separate terms."
        ),
        "parameters": "35,213,590 in the released checkpoint",
        "model_family": "Pure-jump sequence editors over a pretrained ESM-2 encoder",
        "provenance_note": (
            "Registered from the paper, the repository at the pinned commit and the released model card. "
            "Everything reported about it is developer-reported and has not been independently reproduced by "
            "Rewire. The underlying protein language model identity is the existing ESM-2 record rather than a "
            "new one, and the released checkpoint is recorded as a configuration of this method, not as a new "
            "pretrained model."
        ),
        "source_locator": "Abstract; sections 1, 2 and 3; README 'Overview'; model card 'Model details'",
        "review": PDF_REVIEW,
    },
    links=[{"relation": "uses_model", "target_id": ESM2}],
    source_ids=[PDF, README, CARD],
    extra_facets=facets(["foundation_model"], ["antibody sequence editing", "protein sequence editing", "lead optimisation"]),
))

add(record(
    M_EVOFLOWS, "method", "EvoFlows",
    "EvoFlows generates protein sequence variants by adding time conditioning and per-position edit-rate and "
    "token heads to a pretrained ESM-2 encoder and fine-tuning the whole stack on homolog pairs of one family.",
    {
        "entity_level": "method",
        "reported_name": "EvoFlows",
        "version": "arXiv:2603.11703 as cited in the EditJumps paper",
        "provenance_note": (
            "The method EditJumps sets out to replicate. Registered at method level only: no code, weights or "
            "complete training specification were released, which is the finding the EditJumps paper reports."
        ),
        "source_locator": "Section 1; section 2.3; section 3; Table 5",
        "missing_metadata": {
            "checkpoint_revision": {"reason": "unavailable", "note": "No public code or weights, as Table 5 records."},
            "parameters": {"reason": "unreported", "note": "Not stated in the EditJumps paper."},
        },
        "access": "No public code or weights, which Table 5 of the EditJumps paper records as the reason its operational reproducibility from text is not answerable.",
        "review": PDF_REVIEW,
    },
    links=[{"relation": "uses_model", "target_id": ESM2}],
    extra_facets=facets(["foundation_model"], ["protein sequence editing"]),
))

add(record(
    M_EDIT_FLOWS, "method", "Edit Flows",
    "Edit Flows trains a Llama-architecture transformer from scratch to generate variable-length token "
    "sequences through insertion, deletion and substitution events that fire at learned rates in continuous "
    "time, with the state space capped at a fixed maximum length.",
    {
        "entity_level": "method",
        "reported_name": "Edit Flows",
        "version": "arXiv:2506.09018 as cited in the EditJumps paper",
        "provenance_note": (
            "The second method the EditJumps paper reformulates. Registered at method level only; the EditJumps "
            "paper records that no public code or weights exist and that its published deletion-supervision loss "
            "and its reference code disagree."
        ),
        "source_locator": "Sections 1 and 2.3; Appendix C 'Discrepancy in Deletion Supervision in Edit Flows'; Table 5",
        "missing_metadata": {
            "checkpoint_revision": {"reason": "unavailable", "note": "No public code or weights, as Table 5 records."},
            "parameters": {"reason": "unreported", "note": "Not stated in the EditJumps paper."},
        },
        "access": "No public code or weights, which Table 5 of the EditJumps paper records as the reason its operational reproducibility from text is not answerable.",
        "review": PDF_REVIEW,
    },
    extra_facets=facets(["foundation_model"], ["sequence editing"]),
))

add(record(
    M_EVODIFF_MSA, "method", "EvoDiff-MSA",
    "EvoDiff-MSA generates protein sequences by reversing a discrete diffusion corruption conditioned on a "
    "multiple sequence alignment of the target family, which it requires as an input.",
    {
        "entity_level": "method",
        "reported_name": "EvoDiff-MSA",
        "version": "Released model and weights as used by the EditJumps repository",
        "provenance_note": (
            "A comparator in the EditJumps evaluation. Its released model and weights are used; the "
            "mutation-budget masking that matches it to the section 4.2 frame is the EditJumps authors' addition."
        ),
        "source_locator": "Section 1; Figure 1 caption; docs/claims.md, evodiff_msa_baseline row",
        "missing_metadata": {"parameters": {"reason": "unreported", "note": "Not stated in the EditJumps paper or the repository docs that were pinned."}},
        "review": PDF_REVIEW,
    },
    source_ids=[PDF, CLAIMS_DOC],
    extra_facets=facets(["foundation_model"], ["protein sequence generation"]),
))

add(record(
    M_EVOTUNING, "method", "Evotuning",
    "Evotuning fine-tunes a protein masked language model on the sequences of one family and then infills "
    "masked positions of a template from that family, so it changes residues without changing the length.",
    {
        "entity_level": "method",
        "reported_name": "evotuning",
        "version": "As reimplemented at repository commit " + COMMIT,
        "provenance_note": (
            "A comparator in the EditJumps evaluation, reimplemented from the EvoFlows description and the "
            "original unified rational protein engineering paper. The family and its train and holdout split are "
            "the EditJumps authors' own."
        ),
        "source_locator": "Section 3 'The evotuning baseline'; Appendix A 'Evotuning Baseline Implementation and Sampling Protocol'; docs/claims.md, evotune_esm row",
        "review": PDF_REVIEW,
    },
    links=[{"relation": "uses_model", "target_id": ESM2}],
    source_ids=[PDF, CLAIMS_DOC],
    extra_facets=facets(["foundation_model"], ["protein sequence editing"]),
))


# ------------------------------------------------------------------------- configurations
C_EDITJUMPS = rid("config-editjumps-clock-40")
C_RELEASED = rid("config-released-checkpoint")
C_EVOTUNE = rid("config-evotuning-650m")
C_EVOTUNE_F = rid("config-evotuning-650m-forced")
C_EVODIFF = rid("config-evodiff-msa")
C_RAND_MUT = rid("config-random-mutations")
C_RAND_PAIR = rid("config-random-pairing")
C_REFERENCE = rid("config-real-homolog-reference")
C_PUB_EVOFLOWS = rid("config-published-evoflows")
C_PUB_EVOTUNE = rid("config-published-evotuning")
C_PUB_EVOTUNE_F = rid("config-published-evotuning-forced")
C_PUB_EVODIFF = rid("config-published-evodiff-msa")
C_PUB_RAND_MUT = rid("config-published-random-mutations")
C_PUB_RAND_PAIR = rid("config-published-random-pairing")

add(record(
    C_EDITJUMPS, "configuration", "EditJumps editor, clock normalisation 40",
    "The EditJumps editor at the setting whose scores the paper reports: an unfrozen pretrained ESM-2 35M "
    "trunk with three linear per-position rate heads and two token heads modulated by a sinusoidal time "
    "embedding, a linear interpolation schedule, clock normalisation 40 and Euler tau-leaping over 50 steps.",
    {
        "configuration_type": "paper_evaluation",
        "reported_name": "EditJumps",
        "version": "As scored in version 1 of the paper",
        "model_family": "EditJumps",
        "parameters": "ESM-2 35M trunk plus three rate heads and two token heads; the paper prints no total count for this arm",
        "head": (
            "Three per-position operation rate heads for insertion, deletion and substitution and two token "
            "prediction heads, all conditioned by Feature-wise Linear Modulation on an MLP of a sinusoidal time "
            "embedding. Section 3 states linear rather than MLP rate heads for this arm."
        ),
        "hyperparameters": (
            "Fine-tuned for 20,000 steps, batch size 16, Adam, learning rate 1e-4; linear schedule kappa_t = t; "
            "frozen holding-interval rates; clock normalisation 40, chosen for a budget of about 5 edits; Euler "
            "tau-leaping with 50 steps."
        ),
        "accelerator_details": "A single NVIDIA L4 GPU for the primary training run",
        "training_setting": "The ESM-2 trunk is unfrozen and fine-tuned jointly with the rate and token heads on aligned homolog pairs. One generalist editor is trained across the Observed Antibody Space paired subset and then applied zero-shot to held-out targets without per-family retraining.",
        "limitations": [
            L_NON_CONVERGED,
            L_DOMAIN_SHIFT,
            (
                "The edit budget is calibrated in expectation, not guaranteed per sequence: the paper states that "
                "clock normalisation has no closed-form mapping to realised edits, so a specific budget requires "
                "empirical calibration rather than deterministic control."
            ),
            (
                "Section 3 states this arm uses linear rate heads, while the released checkpoint's model card "
                "ships MLP rate heads and the ESM-2 masked language modelling head as the token head, so the "
                "scored arm and the downloadable weights are not stated to be the same configuration."
            ),
        ],
        "missing_metadata": {
            "checkpoint_sha256": {"reason": "unreported", "note": "The paper names no checkpoint file for the scored arm, and the released weights are described with a different head parameterisation."},
            "code_commit": {"reason": "unreported", "note": "The paper does not state the commit the reported runs were produced at."},
        },
        "provenance_note": (
            "The arm Tables 1, 2 and 4 score. Kept apart from the released checkpoint because the stated head "
            "parameterisation differs; no result in this batch is assigned to the downloadable weights."
        ),
        "source_locator": "Section 3 'Architecture and training protocol' and 'Supervision discrepancies and deviations'; Figure 2 ('ours: 40'); Appendix B item 1; Appendix D 'Training Protocol and Compute Resources'",
        "review": PDF_REVIEW,
    },
    links=[{"relation": "configuration_of", "target_id": M_EDITJUMPS}, {"relation": "uses_model", "target_id": ESM2}],
    extra_facets=facets(["foundation_model"]),
))

add(record(
    C_RELEASED, "configuration", "EditJumps released checkpoint",
    "The released EditJumps weights: a 35,213,590-parameter fp32 model over a stock ESM-2 t12 35M trunk of 12 "
    "layers, hidden width 480, 20 attention heads and vocabulary 33, with three MLP rate heads and the ESM-2 "
    "masked language modelling head as the token head, taking joined VH.VL antibody chains as input.",
    {
        "configuration_type": "reported_configuration",
        "reported_name": "VisiumSA/EditJumps",
        "version": f"Hugging Face repository revision {REVISION}",
        "checkpoint": "VisiumSA/EditJumps, files model/checkpoint.pt, model/evoflows_model.pt and model/encoder/",
        "checkpoint_revision": REVISION,
        "model_family": "EditJumps",
        "parameters": "35,213,590",
        "head": "Three rate heads parameterised as MLPs and two token heads, Feature-wise Linear Modulation on a time MLP; the quickstart loads it with rate_head mlp and q_head esm_lm_head",
        "hyperparameters": (
            "20,000 steps at batch size 16, which the card gives as 320,000 pairs and about 19% of one epoch; "
            "Adam, learning rate 1e-4 constant, no warm-up, decay or weight decay; gradient clipping 1.0; seed 0; "
            "Bregman rate-matching objective with a linear kappa schedule; fp32."
        ),
        "training_setting": "Fine-tuned from the stock facebook/esm2_t12_35M_UR50D checkpoint; the card states the trunk is deliberately stock rather than the project's own OAS-adapted trunk",
        "access_reuse": "Public download from Hugging Face under MIT for both the code and the weights",
        "limitations": [
            L_NON_CONVERGED,
            (
                "The card marks two of its own rows unresolved with TODO comments, on the head count and names "
                "and on the step at which the best validation loss was reached."
            ),
            (
                "No result in this batch is assigned to these weights. The paper's scored arm states linear rate "
                "heads while this checkpoint ships MLP rate heads and the ESM-2 language modelling head."
            ),
        ],
        "missing_metadata": {
            "weights_sha256": {"reason": "unextracted", "note": "The 697 MB of weight files were not downloaded; only the card and the encoder configuration were pinned."},
        },
        "provenance_note": (
            "A configuration of the EditJumps method, not a new pretrained model: it fine-tunes an existing "
            "released ESM-2 checkpoint, whose identity is the existing ESM-2 record."
        ),
        "source_locator": "Model card 'Model details' table and the paragraph below it; model/encoder/config.json",
        "review": review("552199e1e3be6d07de661baf23876fcbc354f8cfd33b391d2913291a3a5a8c32",
                         f"{HF_RAW}/README.md", "Every field was read from the model card table, except the trunk shape, which was read from the encoder configuration file.",
                         methods=("transcription", "source-hash-verification")),
    },
    links=[{"relation": "configuration_of", "target_id": M_EDITJUMPS}, {"relation": "uses_model", "target_id": ESM2}],
    source_ids=[CARD, ENCODER, LICENCE],
    extra_facets=facets(["foundation_model"]),
))

add(record(
    C_EVOTUNE, "configuration", "Evotuned ESM-2 650M, unforced infilling",
    "A stock ESM-2 650M trunk fine-tuned on one antibody family's training partition for 2,000 steps, then "
    "infilling entropy-selected masked positions of a template in random order at temperature 1.0, topping up "
    "masks over up to eight rounds until the realised substitution count matches the edit budget.",
    {
        "configuration_type": "paper_evaluation",
        "reported_name": "evotuning",
        "version": "As reimplemented and scored in version 1 of the paper",
        "model_family": "ESM-2",
        "parameters": "650M",
        "hyperparameters": (
            "Family adaptation: esm2_t33_650M_UR50D fine-tuned per family for 2,000 steps, batch size 16, AdamW, "
            "learning rate 5e-5, masking probability 15%. Sampling: b positions drawn without replacement from a "
            "per-column Shannon entropy profile, iterative infilling at temperature 1.0, up to 8 top-up rounds; "
            "b = 5 on Ty1 and b = 4 on HER2-VH."
        ),
        "training_setting": "Retrained separately for each target family: 36,417 sequences for Ty1 and 40,489 for HER2-VH",
        "accelerator_details": "A single NVIDIA A100 GPU, which the repository states is required by the 650M trunk's memory footprint",
        "limitations": [
            "Substitution-only at fixed sequence length; it cannot model insertions or deletions.",
            "In the unforced regime the masked language model frequently re-predicts the template residue, 71.7% unchanged on Ty1, so part of its distributional fidelity reflects non-intervention rather than generative editing.",
        ],
        "provenance_note": "A comparator reimplemented by the EditJumps authors from the EvoFlows description; the family splits are their own.",
        "source_locator": "Section 3 'The evotuning baseline'; Appendix A items 1 to 4; docs/performance.md 'Evotuning ESM-2-650M (A100)'",
        "review": PDF_REVIEW,
    },
    links=[{"relation": "configuration_of", "target_id": M_EVOTUNING}, {"relation": "uses_model", "target_id": ESM2}],
    source_ids=[PDF, PERF],
    extra_facets=facets(["foundation_model"]),
))

add(record(
    C_EVOTUNE_F, "configuration", "Evotuned ESM-2 650M, forced substitution",
    "The same family-adapted ESM-2 650M infilling run with the template residue masked out of the output "
    "logits at every selected position, so every selected position changes in a single pass.",
    {
        "configuration_type": "paper_evaluation",
        "reported_name": "evotuning (forced)",
        "version": "As reimplemented and scored in version 1 of the paper",
        "model_family": "ESM-2",
        "parameters": "650M",
        "hyperparameters": "As the unforced arm, with the template residue set to minus infinity in the output logits at every masked position, guaranteeing b mutations in a single pass",
        "training_setting": "Retrained separately for each target family: 36,417 sequences for Ty1 and 40,489 for HER2-VH",
        "limitations": [
            "Substitution-only at fixed sequence length; it cannot model insertions or deletions.",
            "Forcing a change at every selected position is a control that isolates non-intervention, not a design choice meant to improve the generated set.",
        ],
        "provenance_note": "A comparator reimplemented by the EditJumps authors from the EvoFlows description; it exists to separate generative editing from wild-type conservation.",
        "source_locator": "Section 3 'The evotuning baseline'; Appendix A item 4",
        "review": PDF_REVIEW,
    },
    links=[{"relation": "configuration_of", "target_id": M_EVOTUNING}, {"relation": "uses_model", "target_id": ESM2}],
    extra_facets=facets(["foundation_model"]),
))

add(record(
    C_EVODIFF, "configuration", "EvoDiff-MSA under a matched mutation budget",
    "The released EvoDiff-MSA model and weights run on an alignment of the target family with a mutation-budget "
    "mask that holds its realised edit count near the budget of the other arms.",
    {
        "configuration_type": "paper_evaluation",
        "reported_name": "EvoDiff-MSA",
        "version": "Released EvoDiff-MSA weights as run at repository commit " + COMMIT,
        "model_family": "EvoDiff",
        "hyperparameters": "Alignment-conditioned sampling with a mutation-budget mask; the MSA checkpoint is the released one, about 380 MB from Zenodo record 8045076",
        "limitations": ["It requires a full alignment of the target family as an input, rather than a single seed sequence."],
        "missing_metadata": {"parameters": {"reason": "unreported", "note": "Neither the paper nor the pinned repository docs print a parameter count."}},
        "provenance_note": "A comparator run by the EditJumps authors with the released weights; the budget-matching mask is their addition.",
        "source_locator": "Section 1; docs/claims.md, evodiff_msa_baseline row; docs/performance.md 'EvoDiff-MSA'",
        "review": PDF_REVIEW,
    },
    links=[{"relation": "configuration_of", "target_id": M_EVODIFF_MSA}],
    source_ids=[PDF, CLAIMS_DOC, PERF],
    extra_facets=facets(["foundation_model"]),
))

add(record(
    C_RAND_MUT, "configuration", "Random mutation floor",
    "Uniformly random single-residue substitutions applied to the template at the same realised edit budget as "
    "the learned arms, which sets the empirical floor each block is compared against.",
    {
        "configuration_type": "paper_evaluation",
        "reported_name": "random mutations",
        "version": "As scored in version 1 of the paper",
        "method_role": "Empirical floor of the reimplemented block",
        "limitations": ["A control rather than a design method; it carries no learned distribution over positions or residues."],
        "provenance_note": "The floor of the reimplemented block; Table 1's caption states each row compares against its own block's floor and ceiling.",
        "source_locator": "Table 1 caption; Table 2 row 'rand. mut.'",
        "review": PDF_REVIEW,
    },
    extra_facets=facets(["conventional_pipeline"]),
))

add(record(
    C_RAND_PAIR, "configuration", "Random homolog pairing ceiling",
    "Pairs of real family homologs scored against each other, which sets the empirical ceiling each block is "
    "compared against and whose edit counts are those between natural sequences rather than generated ones.",
    {
        "configuration_type": "paper_evaluation",
        "reported_name": "random pairing",
        "version": "As scored in version 1 of the paper",
        "method_role": "Empirical ceiling of the reimplemented block",
        "limitations": [
            "A control rather than a design method; nothing is generated, so its edit counts and pairwise distances describe the natural family.",
            "Its edits per sequence, about 23 on both families, are around five times the budget of the learned arms, so its distributional scores are not reached at a matched budget.",
        ],
        "provenance_note": "The ceiling of the reimplemented block; Table 1's caption states each row compares against its own block's floor and ceiling.",
        "source_locator": "Table 1 caption; Table 2 row 'rand. pair.'",
        "review": PDF_REVIEW,
    },
    extra_facets=facets(["conventional_pipeline"]),
))

add(record(
    C_REFERENCE, "configuration", "Natural homologs scored against natural homologs",
    "Held-out natural homologs scored against held-out natural homologs at a stated reference set size, which "
    "measures how far the agreement scores move with that size alone.",
    {
        "configuration_type": "paper_evaluation",
        "reported_name": "real homologs",
        "version": "As scored in version 1 of the paper",
        "method_role": "Sample-size control for the agreement metrics",
        "limitations": ["A control on the metric rather than a generative method; its scores show what the agreement metrics return when nothing is generated at all."],
        "provenance_note": "The control behind the paper's sample-size dependency finding in Appendix E.",
        "source_locator": "Appendix E 'Sample-Size Dependency and Grounded Baseline Controls'",
        "review": PDF_REVIEW,
    },
    extra_facets=facets(["conventional_pipeline"]),
))


def published_config(id_, name, reported, description, limitations, locator):
    return add(record(
        id_, "configuration", name, description,
        {
            "configuration_type": "reported_configuration",
            "reported_name": reported,
            "version": "As printed in the lower block of Table 1",
            "limitations": [L_UNRECOVERABLE] + limitations,
            "missing_metadata": {
                "hyperparameters": {"reason": "unavailable", "note": "The EditJumps paper states it could not recover the original experimental conditions."},
                "parameters": {"reason": "unreported", "note": "Not printed in the EditJumps paper."},
            },
            "provenance_note": (
                "Kept separate from the reimplemented arm of the same name because the paper states the two "
                "blocks are not comparable and that it could not recover the original conditions. Its values "
                "are the upstream paper's own, transcribed from the lower block of Table 1."
            ),
            "source_locator": locator,
            "review": PDF_REVIEW,
        },
        extra_facets=facets(["foundation_model"]),
    ))


published_config(C_PUB_EVOFLOWS, "EvoFlows, per-family retrained", "EvoFlows",
                 "An EvoFlows editor retrained separately on each target family before generating variants of that family's templates.",
                 ["Its realised edit counts, 14.64 on Ty1 and 35.27 on HER2-VH, are three to nine times those of the reimplemented arms, so its distributional scores are not at a matched budget."],
                 "Table 1, lower block, row 'EvoFlows'")
published_config(C_PUB_EVOTUNE, "Evotuned language model, published values", "evotuning",
                 "An evotuned protein language model that infills entropy-selected masked positions of a template, retrained per target family, with its trunk size, step budget and masking rate unstated.",
                 [], "Table 1, lower block, row 'evotuning'")
published_config(C_PUB_EVOTUNE_F, "Forced-substitution evotuned language model, published values", "evotuning (forced)",
                 "A forced-substitution evotuned language model that must change every masked position of a template, retrained per target family, with its trunk size, step budget and masking rate unstated.",
                 [], "Table 1, lower block, row 'evotuning (forced)'")
published_config(C_PUB_EVODIFF, "EvoDiff-MSA, published values", "EvoDiff-MSA",
                 "An alignment-conditioned EvoDiff-MSA run per target family, with its masking and budget-matching settings unstated.",
                 [], "Table 1, lower block, row 'EvoDiff-MSA'")
published_config(C_PUB_RAND_MUT, "Random mutation floor, published values", "random mutations",
                 "A uniform random substitution floor applied per target family, with its edit budget unstated.",
                 ["A control rather than a design method."], "Table 1, lower block, row 'random mutations'")
published_config(C_PUB_RAND_PAIR, "Random homolog pairing ceiling, published values", "random pairing",
                 "A real homolog pairing ceiling computed per target family, with its reference set size unstated.",
                 ["A control rather than a design method."], "Table 1, lower block, row 'random pairing'")


# ------------------------------------------------------------------------------ datasets
D_OAS = rid("data-oas-paired-corpus")
D_PAIRS = rid("data-oas-homolog-pairs")
D_TY1 = rid("data-ty1-family")
D_HER2 = rid("data-her2vh-family")
D_NATURAL = rid("data-heldout-natural-homologs")
D_SIX = rid("data-evoflows-six-families")

OAS_TERMS = (
    "Derived from the Observed Antibody Space database, whose own terms apply. The MIT grant on the "
    "EditJumps repository and weights does not extend to it."
)

add(record(
    D_OAS, "dataset", "Observed Antibody Space paired subset, as used by EditJumps",
    "The paired heavy and light chain variable domains of the Observed Antibody Space database, joined into "
    "single VH.VL strings by a delimiter token that is already in the ESM-2 vocabulary.",
    {
        "version": "As downloaded by the repository's download_oas stage at commit " + COMMIT,
        "total": 2586927,
        "species": "Antibody repertoires as deposited in the Observed Antibody Space database",
        "population": "2,586,927 joined VH.VL sequences",
        "repository": "https://opig.stats.ox.ac.uk/webapps/oas/",
        "reuse_restrictions": OAS_TERMS,
        "access": "Public download through the repository's download-oas command",
        "source_locator": "Model card 'Model details', Training data row; Appendix D 'Corpus Curation and Homolog Clustering'; docs/claims.md, download_oas row",
        "missing_metadata": {
            "accession": {"reason": "unreported", "note": "No data units, snapshot date or accession list is printed in the card, the paper or the pinned repository docs."},
            "split": {"reason": "unreported", "note": "The paper states the EvoFlows train, inference and holdout ratios are not stated upstream; the repository's own split ratios were not pinned."},
        },
        "review": review("552199e1e3be6d07de661baf23876fcbc354f8cfd33b391d2913291a3a5a8c32",
                         f"{HF_RAW}/README.md", "The sequence count was read from the model card; the joining rule and the clustering from the paper's Appendix D.",
                         methods=("transcription", "pdf-text-parse", "source-hash-verification")),
    },
    source_ids=[CARD, PDF, CLAIMS_DOC],
))

add(record(
    D_PAIRS, "dataset", "EditJumps training homolog pairs",
    "The aligned antibody homolog pairs the editor is trained on: 1,660,105 unordered pairs drawn from "
    "clusters of the paired Observed Antibody Space corpus and coupled by Needleman-Wunsch alignment.",
    {
        "version": "As built by the repository's build_homolog_pairs stage at commit " + COMMIT,
        "total": 1660105,
        "population": "1,660,105 symmetric pairs",
        "manifest": "MMseqs2 easy-cluster at minimum sequence identity 0.5 and coverage 0.8, clusters capped at 20 pairs per family",
        "label_semantics": "Each pair is a source and a target natural sequence; the supervision target is the set of single-token edits that carries one to the other under the alignment.",
        "reuse_restrictions": OAS_TERMS,
        "source_locator": "Appendix D 'Corpus Curation and Homolog Clustering'; Appendix C 'Augmented Training Path Construction'; model card 'Model details', Training data row",
        "missing_metadata": {
            "split": {"reason": "unreported", "note": "The paper states the upstream train, inference and holdout ratios are not stated; its own ratios are not printed either."},
            "tool_versions": {"reason": "unreported", "note": "No MMseqs2 version is printed, and the alignment's substitution matrix and gap penalties are left to third-party library defaults, which Appendix C records as a finding."},
        },
        "review": PDF_REVIEW,
    },
    links=[{"relation": "same_data_as", "target_id": D_OAS}],
    source_ids=[PDF, CARD],
))


def family_dataset(id_, name, description, locator, training_sequences):
    return add(record(id_, "dataset", name, description, {
        "version": "As built by the repository's seed_homologs stage at commit " + COMMIT,
        "population": training_sequences,
        "manifest": "MMseqs2 search at E-value at most 0.1 and coverage at least 0.8, with a 0.7 seed identity threshold to separate genuine homologs from invariant framework regions",
        "reuse_restrictions": OAS_TERMS,
        "source_locator": locator,
        "missing_metadata": {"accession": {"reason": "unreported", "note": "No accession list for the family members is printed."}},
        "review": PDF_REVIEW,
    }, links=[{"relation": "same_data_as", "target_id": D_OAS}]))


family_dataset(D_TY1, "Ty1 homolog family from the Observed Antibody Space",
               "Observed Antibody Space homologs of Ty1, the anti-SARS-CoV-2 camelid single-domain VHH used as "
               "one of the two held-out editing targets.",
               "Section 3 'Data curation and evaluation targets'; Appendix D 'Corpus Curation and Homolog Clustering'; Appendix A item 1",
               "36,417 sequences in the family training partition")
family_dataset(D_HER2, "HER2-VH homolog family from the Observed Antibody Space",
               "Observed Antibody Space homologs of HER2-VH, the isolated anti-HER2 trastuzumab heavy chain used "
               "as the second held-out editing target.",
               "Section 3 'Data curation and evaluation targets'; Appendix D 'Corpus Curation and Homolog Clustering'; Appendix A item 1",
               "40,489 sequences in the family training partition")

add(record(
    D_NATURAL, "dataset", "Held-out natural antibody homologs used as evaluation references",
    "The held-out natural family members the generated sets are scored against, drawn from families mined from "
    "the Observed Antibody Space.",
    {
        "version": "As built by the repository's seed_homologs stage at commit " + COMMIT,
        "population": "200 reference sequences per family in the reported frame; the sample-size analysis also scores sets of 20, 100 and 800",
        "reuse_restrictions": OAS_TERMS,
        "source_locator": "Appendix E 'Sample-Size Dependency and Grounded Baseline Controls' and 'Reference Construction and Overlap Impact'",
        "missing_metadata": {
            "accession": {"reason": "unreported", "note": "No sequence list is printed."},
            "split": {"reason": "conflicting", "note": "Described as held-out, but 113 of Ty1's and 103 of HER2-VH's 200 reference sequences had been present in the training set."},
        },
        "review": PDF_REVIEW,
    },
    links=[{"relation": "same_data_as", "target_id": D_OAS}],
))

add(record(
    D_SIX, "dataset", "The six evaluation datasets behind EvoFlows' published figures",
    "The six evaluation families the EvoFlows paper reports its own numbers across, whose composition and "
    "reference sets the replication could not recover.",
    {
        "version": "As reported in the EvoFlows paper",
        "population": "Six evaluation datasets, of which only Ty1 and HER2-VH were accessible to the replication",
        "source_locator": "Section 3 'Data curation and evaluation targets'; Table 4 caption; Appendix E 'Vector Graphic Extraction and Method Resolution' item 2; Figure 4",
        "missing_metadata": {
            "accession": {"reason": "unavailable", "note": "The paper states non-antibody targets have no homologs in the Observed Antibody Space and that anti-EphA2 is unrecoverable in public repositories."},
            "total": {"reason": "unreported", "note": "No per-family sequence counts are printed."},
            "split": {"reason": "unavailable", "note": "The replication states it could not recover the original experimental conditions."},
        },
        "review": PDF_REVIEW,
    },
))

# --------------------------------------------------------------------------- dataset subsets
S_TY1_200 = rid("data-ty1-references-200")
S_HER2_200 = rid("data-her2vh-references-200")
S_TY1_300 = rid("data-ty1-ceiling-300")
S_HER2_300 = rid("data-her2vh-ceiling-300")
S_TY1_DISJOINT = rid("data-ty1-references-200-disjoint")
S_HER2_DISJOINT = rid("data-her2vh-references-200-disjoint")
S_POOLED = rid("data-two-families-references-200")
S_N20 = rid("data-references-20")
S_N100 = rid("data-references-100")
S_N800 = rid("data-references-800")

FAMILY_SUBSETS = {}


def reference_subset(id_, source_dataset, name, description, attributes, links=None):
    base = {
        "source_dataset": source_dataset,
        "source_locator": "Section 3 'Data curation and evaluation targets'; Table 2 caption; Appendix E 'Reference Construction and Overlap Impact'",
        "review": PDF_REVIEW,
    }
    base.update(attributes)
    return add(record(id_, "dataset_subset", name, description, base,
                      links=links if links is not None else [{"relation": "same_data_as", "target_id": source_dataset}]))


reference_subset(S_TY1_200, D_TY1, "Ty1 reference holdout, 200 homologs",
                 "The 200 held-out Ty1 family homologs the generated Ty1 sets are scored against in the reported frame.",
                 {"population_count": "200", "split": "200 held-out family members; 20 templates are drawn for generation",
                  "limitations": ["113 of these 200 sequences had been present in the training set."]})
reference_subset(S_HER2_200, D_HER2, "HER2-VH reference holdout, 200 homologs",
                 "The 200 held-out HER2-VH family homologs the generated HER2-VH sets are scored against in the reported frame.",
                 {"population_count": "200", "split": "200 held-out family members; 20 templates are drawn for generation",
                  "limitations": ["103 of these 200 sequences had been present in the training set."]})
reference_subset(S_TY1_300, D_TY1, "Ty1 agreement ceiling set, 300 real homologs",
                 "The 300 real Ty1 homologs that set the agreement ceiling the covariance and mutual information product scores are normalised against.",
                 {"population_count": "300", "split": "300 real homologs used as the agreement ceiling",
                  "source_locator": "Table 2 caption, 'agreement ceiling 300 real homologs'"})
reference_subset(S_HER2_300, D_HER2, "HER2-VH agreement ceiling set, 300 real homologs",
                 "The 300 real HER2-VH homologs that set the agreement ceiling the covariance and mutual information product scores are normalised against.",
                 {"population_count": "300", "split": "300 real homologs used as the agreement ceiling",
                  "source_locator": "Table 2 caption, 'agreement ceiling 300 real homologs'"})
reference_subset(S_TY1_DISJOINT, D_TY1, "Ty1 reference holdout, strictly disjoint from training",
                 "The Ty1 reference set with every sequence that had appeared in training removed, used to measure what the overlap was worth.",
                 {"split": "Strictly disjoint from the training set",
                  "missing_metadata": {"population_count": {"reason": "unreported", "note": "The paper gives the overlap, 113 of 200, but not the size of the disjoint set it re-evaluated on."}},
                  "limitations": ["Re-evaluating on it shifted spectrum MMD by -36.7% and increased covariance agreement by 12 to 17 points, driven by greater sequence homogeneity, 23.00 against 24.90 Levenshtein distance."],
                  "source_locator": "Appendix E 'Reference Construction and Overlap Impact'"})
reference_subset(S_HER2_DISJOINT, D_HER2, "HER2-VH reference holdout, strictly disjoint from training",
                 "The HER2-VH reference set with every sequence that had appeared in training removed, used to measure what the overlap was worth.",
                 {"split": "Strictly disjoint from the training set",
                  "missing_metadata": {"population_count": {"reason": "unreported", "note": "The paper gives the overlap, 103 of 200, but not the size of the disjoint set it re-evaluated on."}},
                  "limitations": ["Re-evaluating on it shifted spectrum MMD by -12.6% and increased covariance agreement by 12 to 17 points."],
                  "source_locator": "Appendix E 'Reference Construction and Overlap Impact'"})
reference_subset(S_POOLED, D_NATURAL, "Two-family reference sets, 200 homologs each",
                 "The Ty1 and HER2-VH reference sets taken together, which the ceiling-normalised comparison is computed over.",
                 {"population_count": "400", "split": "200 held-out references per family, two families",
                  "subset_scope": "Ty1 and HER2-VH together, 200 references each",
                  "source_locator": "Table 4 caption, 'EditJumps is evaluated on two antibody families (200 references)'"},
                 links=[{"relation": "same_data_as", "target_id": S_TY1_200}, {"relation": "same_data_as", "target_id": S_HER2_200}])

for subset_id, size in ((S_N20, 20), (S_N100, 100), (S_N800, 800)):
    reference_subset(subset_id, D_NATURAL, f"Natural homolog reference set, {size} sequences",
                     f"A reference set of {size} held-out natural homologs, one of the sizes the agreement "
                     "scores between real homologs are recomputed at.",
                     {"population_count": str(size), "split": f"{size} natural homologs scored against natural homologs",
                      "missing_metadata": {"selected_assay": {"reason": "inapplicable", "note": "Sequence data, not an assay."}},
                      "source_locator": "Appendix E 'Sample-Size Dependency and Grounded Baseline Controls'"})

S_REF_800_ALIGNMENT = rid("data-references-800-alignment")
reference_subset(S_REF_800_ALIGNMENT, D_NATURAL, "Reference alignment expanded to 800 homologs",
                 "The reference alignment expanded from 200 to 800 homologs, the condition under which the "
                 "normalised spectrum MMD ratio is reported to change enough to invert method rankings.",
                 {"population_count": "800", "split": "800 homologs in the reference alignment",
                  "source_locator": "Section 5, 'expanding the reference alignment from 200 to 800 homologs'"})


# ---------------------------------------------------------------------------------- task
TASK = rid("task-antibody-variant-generation")
add(record(
    TASK, "task", "Homolog-like variant generation from a seed antibody sequence",
    "Given one seed amino-acid sequence and an approximate edit budget, propose related candidate sequences "
    "carrying substitutions, insertions and deletions, scored by how closely the generated set's sequence "
    "statistics match a reference set of held-out natural homologs of the same family.",
    {
        "task": "Homolog-like variant generation from a seed antibody sequence",
        "task_type": "Generative sequence editing scored by distributional similarity to natural sequences",
        "scope_note": (
            "Every endpoint under this task is a computational comparison between generated sequences and "
            "natural sequences. None of them is a measured biological property: no binding affinity, "
            "specificity, expression, stability or retained function is assayed anywhere in the source."
        ),
        "metric_direction": "unknown",
        "splits": "Held-out target families, with 20 templates drawn per family and a separate reference set of held-out family members",
        "source_locator": "Abstract; section 1; section 3 'Data curation and evaluation targets'; section 5; README 'Overview'",
    },
    source_ids=[PDF, README],
    extra_facets=facets(None, ["antibody sequence editing", "protein sequence editing", "lead optimisation"]),
))

# ------------------------------------------------------------------------------- protocols
TY1, HER2 = "ty1", "her2vh"
FAMILY_NAME = {TY1: "Ty1", HER2: "HER2-VH"}
FAMILY_REFERENCES = {TY1: S_TY1_200, HER2: S_HER2_200}
FAMILY_CEILING = {TY1: "300 real Ty1 homologs", HER2: "300 real HER2-VH homologs"}

# column -> (metric, direction, unit, unit_detail, qualifier, definition, extra limitations)
OURS_METRICS = {
    "edits": ("edit-count", "unknown", "count",
              "single-token edit operations: insertions, deletions and substitutions",
              "mean realised edits per generated sequence, 400 generated sequences per family",
              "Mean number of single-token edits realised between the template and the generated sequence, printed with a dash for direction because it is matched rather than ranked.",
              ["The budget is calibrated in expectation: the realised count varies per sequence and the paper states there is no closed-form mapping from the clock normalisation to it."]),
    "pairw. Lev.": ("levenshtein-distance", "unknown", "count",
                    "single-token edit operations",
                    "mean pairwise Levenshtein distance within the generated set, pooled over templates",
                    "Mean pairwise Levenshtein distance within the generated set, printed with an approximate sign because it is matched against the natural family rather than maximised.",
                    ["The EvoFlows paper leaves the reduction between a pooled and a within-template average ambiguous; the pooled reduction is used here."]),
    "MMD": ("maximum-mean-discrepancy", "lower", "unitless", None,
            "k-mer spectrum MMD between the generated set and a 200-sequence natural holdout, unnormalised",
            "Maximum mean discrepancy between the k-mer spectra of the generated set and the natural reference set.",
            ["The EvoFlows paper omits the kernel parameter k."]),
    "KL pos.": ("kullback-leibler-divergence", "lower", "unitless", None,
                "per-position amino-acid composition against a 200-sequence natural holdout",
                "Kullback-Leibler divergence between the per-position amino-acid composition of the generated set and that of the natural reference set.", []),
    "KL pool.": ("kullback-leibler-divergence", "lower", "unitless",
                 "value times 10^3 (printed column header scaling)",
                 "pooled amino-acid composition against a 200-sequence natural holdout",
                 "Kullback-Leibler divergence between the pooled amino-acid composition of the generated set and that of the natural reference set.", []),
    "JS pos.": ("jensen-shannon-divergence", "lower", "unitless",
                "value times 10^2 (printed column header scaling)",
                "per-position formulation chosen by the EditJumps authors, against a 200-sequence natural holdout",
                "Jensen-Shannon divergence between the per-position amino-acid distributions of the generated set and the natural reference set.", [L_UNDEFINED]),
    "cov. agr.": ("covariance-agreement", "higher", "unitless", None,
                  "residue covariance agreement against a 300-sequence natural homolog ceiling",
                  "Agreement between the residue pair covariance structure of the generated set and that of the natural reference set, normalised against a natural homolog ceiling.",
                  ["The EvoFlows paper specifies the covariance matrix but omits the scalar reduction, so the reduction scored here is the EditJumps authors' own choice.",
                   "The paper reports that this score moves with the reference partition alone, from 83.6% to 85.1%, and with the reference set size, from 0.790 at 20 references to 0.985 at 800."]),
    "MIP agr.": ("mutual-information-product-agreement", "higher", "unitless", None,
                 "mutual information product agreement against a 300-sequence natural homolog ceiling",
                 "Agreement between the mutual information product matrix of the generated set and that of the natural reference set, normalised against a natural homolog ceiling.",
                 ["The EvoFlows paper specifies the matrix but omits the scalar reduction, so the reduction scored here is the EditJumps authors' own choice.",
                  "The paper reports that computing the ceiling in an unaligned or mismatched frame shifts this score by 2.3 percentage points."]),
    "ΔH": ("entropy-delta", "unknown", "unitless", None,
                "positional entropy difference from the natural holdout; the target value is zero",
                "Difference between the positional sequence entropy of the generated set and that of the natural reference set, printed with a target of zero rather than a direction.",
                [L_UNDEFINED]),
    "prof. LL": ("log-likelihood", "higher", "unitless", None,
                 "profile log-likelihood of the generated sequences under the family alignment profile",
                 "Log-likelihood of the generated sequences under a position-specific profile of the family alignment.",
                 [L_UNDEFINED]),
}

OURS_PROTOCOL_SUFFIX = {
    "edits": "edits",
    "pairw. Lev.": "pairwise-levenshtein",
    "MMD": "spectrum-mmd",
    "KL pos.": "kl-positional",
    "KL pool.": "kl-pooled",
    "JS pos.": "js-positional",
    "cov. agr.": "covariance-agreement",
    "MIP agr.": "mip-agreement",
    "ΔH": "entropy-delta",
    "prof. LL": "profile-log-likelihood",
}

OURS_FRAME = (
    "One frame for every arm and both families: 20 templates per family and 20 variants per template, so 400 "
    "generated sequences, scored against a 200-sequence held-out natural homolog set, with the agreement "
    "ceiling computed on 300 real homologs. Sampling runs Euler tau-leaping over 50 steps. Every arm is held "
    "to a matched realised edit budget of about 4 to 5 edits per sequence."
)

ours_protocols = {}
for column, spec in OURS_METRICS.items():
    metric, direction, unit, unit_detail, qualifier, definition, extra = spec
    pid = rid("protocol-ours-200-" + OURS_PROTOCOL_SUFFIX[column])
    ours_protocols[column] = pid
    attributes = {
        "entity_classification": {
            "review_date": DATE,
            "rationale": "One protocol per metric and per reference-set condition: the paper reports that the reference-set size changes the scores, so a different reference set is a different protocol.",
            "source_ids": [PDF],
            "source_locator": "Table 2 caption; section 5; Appendix E",
            "ambiguities": [],
        },
        "metric": metric,
        "metric_direction": direction,
        "metric_qualifier": qualifier,
        "metric_definition": definition,
        "unit": unit,
        "protocol": OURS_FRAME,
        "heldout_test": ["20 templates and 200 held-out natural homologs per family", "Both families are held out from the generalist editor's training targets"],
        "aggregation": "Pooled over the 400 generated sequences of one family",
        "dataset": "Ty1 and HER2-VH homolog families mined from the paired Observed Antibody Space corpus",
        "task": "Homolog-like variant generation from a seed antibody sequence",
        "version": "Version 1 of the paper, Table 2 frame",
        "publication_status": "preprint",
        "reproducibility_note": (
            "Not reproduced by Rewire. The code and weights are public under MIT, but the paper states its "
            "scored arm uses a head parameterisation that differs from the released checkpoint's, and it names "
            "no commit for the reported runs."
        ),
        "scope_note": (
            "The endpoint is a computational comparison between generated sequences and natural sequences. It "
            "is not a measured binding, specificity, stability or function value."
        ),
        "limitations": OURS_LIMITS + extra,
        "missing_metadata": {
            "random_seeds": {"reason": "unreported", "note": "Table 1's caption mentions three seeds; no seed values are printed and Table 2 prints one value per cell."},
        },
        "review": PDF_REVIEW,
    }
    if unit_detail:
        attributes["unit_detail"] = unit_detail
    add(record(pid, "protocol", f"EditJumps section 4.2 frame, 200 references: {column}",
               f"{definition} Computed under the paper's section 4.2 frame: 20 templates and 20 variants per "
               "template against a 200-sequence held-out natural homolog set.",
               attributes, links=[{"relation": "evaluates_task", "target_id": TASK}]))


# -------------------------------------------------- published-block protocols (Table 1 lower)
PUBLISHED_METRICS = {
    "edits/seq": ("edit-count", "unknown", "count",
                  "single-token edit operations: insertions, deletions and substitutions",
                  "mean edits per sequence as the EvoFlows paper prints it, under conditions the replication could not recover",
                  "Mean number of edits per generated sequence."),
    "diversity": ("levenshtein-distance", "unknown", "count", "single-token edit operations",
                  "printed under the column heading 'diversity'; mean pairwise Levenshtein distance, under conditions the replication could not recover",
                  "Mean pairwise Levenshtein distance within the generated set, printed under a column headed 'diversity'."),
    "MMD": ("maximum-mean-discrepancy", "lower", "unitless", None,
            "k-mer spectrum MMD, under conditions and a reference set size the replication could not recover",
            "Maximum mean discrepancy between the k-mer spectra of the generated set and a natural reference set."),
    "KL x10^3": ("kullback-leibler-divergence", "lower", "unitless",
                 "value times 10^3 (printed column header scaling)",
                 "pooled amino-acid composition, under conditions the replication could not recover",
                 "Kullback-Leibler divergence between the pooled amino-acid composition of the generated set and that of a natural reference set."),
}
PUBLISHED_SUFFIX = {"edits/seq": "edits", "diversity": "pairwise-levenshtein", "MMD": "spectrum-mmd", "KL x10^3": "kl-pooled"}

published_protocols = {}
for column, (metric, direction, unit, unit_detail, qualifier, definition) in PUBLISHED_METRICS.items():
    pid = rid("protocol-published-" + PUBLISHED_SUFFIX[column])
    published_protocols[column] = pid
    attributes = {
        "entity_classification": {
            "review_date": DATE,
            "rationale": "The upstream paper's own published values are a separate protocol from the reimplemented frame, because the paper states the two blocks are not comparable and that it could not recover the original conditions.",
            "source_ids": [PDF],
            "source_locator": "Table 1 caption; section 4, first sentence",
            "ambiguities": ["Reference set size, templates, splits, seeds and metric implementation are unknown, so no comparison field can be filled."],
        },
        "metric": metric,
        "metric_direction": direction,
        "metric_qualifier": qualifier,
        "metric_definition": definition,
        "unit": unit,
        "protocol": (
            "The conditions under which the EvoFlows paper produced these values, which the replication states "
            "it could not recover from that paper. Per-family retraining is required by the original approach."
        ),
        "dataset": "The same two antibody families, Ty1 and HER2-VH, under the upstream paper's own reference sets",
        "task": "Homolog-like variant generation from a seed antibody sequence",
        "version": "As printed in the lower block of Table 1 of version 1 of the paper",
        "publication_status": "preprint",
        "reproducibility_note": (
            "Not reproduced. The paper states that the original experimental conditions could not be recovered "
            "and that these values are not comparable with its own."
        ),
        "scope_note": (
            "The endpoint is a computational comparison between generated sequences and natural sequences. It "
            "is not a measured binding, specificity, stability or function value."
        ),
        "limitations": PUBLISHED_LIMITS,
        "missing_metadata": {
            "heldout_test": {"reason": "unavailable", "note": "The split behind the published values is not recoverable from the EvoFlows paper."},
            "random_seeds": {"reason": "unavailable", "note": "Not recoverable from the EvoFlows paper."},
            "metric_implementation": {"reason": "unavailable", "note": "Six of the ten upstream metrics are not deterministically recomputable from the text."},
            "aggregation": {"reason": "unavailable", "note": "Not recoverable from the EvoFlows paper."},
        },
        "review": PDF_REVIEW,
    }
    if unit_detail:
        attributes["unit_detail"] = unit_detail
    add(record(pid, "protocol", f"EvoFlows published values, two families: {column}",
               f"{definition} Printed by the EvoFlows paper under conditions the replication states it could "
               "not recover, so none of this protocol's comparison fields is known.",
               attributes, links=[{"relation": "evaluates_task", "target_id": TASK}]))

# ------------------------------------------------- ceiling-normalised protocols (Table 4)
CEILING_METRICS = {
    "Covariance (% of ceiling)": ("covariance-agreement", "higher", "percent", None,
                                  "percent of the natural homolog ceiling",
                                  "Residue covariance agreement expressed as a percentage of the ceiling computed on held-out natural homologs."),
    "MIP (% of ceiling)": ("mutual-information-product-agreement", "higher", "percent", None,
                           "percent of the natural homolog ceiling",
                           "Mutual information product agreement expressed as a percentage of the ceiling computed on held-out natural homologs."),
    "Positional JS† (× floor)": ("jensen-shannon-divergence", "lower", "unitless",
                                           "multiple of the random-pairing floor",
                                           "positional formulation chosen by the EditJumps authors, expressed as a multiple of the floor",
                                           "Positional Jensen-Shannon divergence expressed as a multiple of the floor."),
    "Pairwise Distance‡": ("levenshtein-distance", "unknown", "unitless",
                                "ratio to the natural homolog value",
                                "pooled reduction, expressed as a ratio to natural homologs",
                                "Mean pairwise Levenshtein distance expressed as a ratio to the value natural homologs reach."),
}
CEILING_SUFFIX = {
    "Covariance (% of ceiling)": "covariance",
    "MIP (% of ceiling)": "mip",
    "Positional JS† (× floor)": "js-positional",
    "Pairwise Distance‡": "pairwise-distance",
}

ceiling_protocols = {"ours": {}, "published": {}}
for arm, label, frame, dataset_text, limits, extra_missing in (
    ("ours", "EditJumps, two families, 200 references",
     "Normalised against the ceiling computed on the two families' 200-sequence held-out reference sets.",
     "Ty1 and HER2-VH, 200 references each", OURS_LIMITS, {}),
    ("published", "EvoFlows published values, six families",
     "Normalised against the ceiling of the six evaluation datasets the EvoFlows paper reports, with the "
     "marker positions recovered from its Figure 3 by extracting vector paths and calibrating against axis ticks.",
     "The six evaluation datasets of the EvoFlows paper", PUBLISHED_LIMITS,
     {"heldout_test": {"reason": "unavailable", "note": "The split behind the published values is not recoverable from the EvoFlows paper."}}),
):
    for column, (metric, direction, unit, unit_detail, qualifier, definition) in CEILING_METRICS.items():
        pid = rid(f"protocol-ceiling-{arm}-" + CEILING_SUFFIX[column])
        ceiling_protocols[arm][column] = pid
        missing = {
            "random_seeds": {"reason": "unreported", "note": "No seed values are printed for the ceiling-normalised comparison."},
        }
        missing.update(extra_missing)
        attributes = {
            "entity_classification": {
                "review_date": DATE,
                "rationale": "The two columns of Table 4 are normalised against different ceilings, on different numbers of families and different reference sets, so each is its own protocol and the two must not be pooled.",
                "source_ids": [PDF],
                "source_locator": "Table 4 caption",
                "ambiguities": [],
            },
            "metric": metric,
            "metric_direction": direction,
            "metric_qualifier": qualifier,
            "metric_definition": definition,
            "unit": unit,
            "protocol": frame,
            "dataset": dataset_text,
            "task": "Homolog-like variant generation from a seed antibody sequence",
            "version": "As printed in Table 4 of version 1 of the paper",
            "publication_status": "preprint",
            "aggregation": "Normalised against the attainable ceiling computed on held-out natural homologs",
            "reproducibility_note": "Not reproduced by Rewire.",
            "scope_note": (
                "The endpoint is a computational comparison between generated sequences and natural sequences. "
                "It is not a measured binding, specificity, stability or function value."
            ),
            "limitations": limits + [
                "The paper states that ceilings are highly sensitive to the multiple sequence alignment "
                "projection: computing them in an unaligned or mismatched frame shifts mutual information "
                "product agreement by 2.3 percentage points, so ceilings only compare within one coordinate frame.",
                "The two columns of Table 4 rest on different numbers of families and different reference sets, "
                "so they are not a like-for-like comparison.",
            ],
            "missing_metadata": missing,
            "review": PDF_REVIEW,
        }
        if unit_detail:
            attributes["unit_detail"] = unit_detail
        add(record(pid, "protocol", f"Ceiling-normalised comparison, {label}: {column}",
                   f"{definition} {frame}", attributes,
                   links=[{"relation": "evaluates_task", "target_id": TASK}]))

# ------------------------------------- reference-set size protocols (Appendix E prose series)
size_protocols = {}
for size, subset in (("20", S_N20), ("100", S_N100), ("800", S_N800)):
    pid = rid(f"protocol-covariance-references-{size}")
    size_protocols[size] = pid
    add(record(
        pid, "protocol", f"Covariance agreement between natural homologs, {size} references",
        "Residue covariance agreement computed with natural homologs on both sides of the comparison at a "
        f"reference set of {size} sequences, which measures what the metric returns when nothing is generated.",
        {
            "entity_classification": {
                "review_date": DATE,
                "rationale": "Each reported reference-set size is its own protocol, because the paper's finding is that the score moves with that size alone.",
                "source_ids": [PDF],
                "source_locator": "Appendix E 'Sample-Size Dependency and Grounded Baseline Controls'",
                "ambiguities": ["The paper does not say which family or families this series is computed on."],
            },
            "metric": "covariance-agreement",
            "metric_direction": "higher",
            "metric_qualifier": f"natural homologs scored against natural homologs at a reference set of {size} sequences",
            "metric_definition": "Agreement between the residue pair covariance structure of two sets of natural homologs of the same family.",
            "unit": "unitless",
            "protocol": f"Score real homologs against real homologs with a reference set of {size} sequences.",
            "dataset": f"{size} held-out natural homologs",
            "task": "Homolog-like variant generation from a seed antibody sequence",
            "version": "As printed in Appendix E of version 1 of the paper",
            "publication_status": "preprint",
            "scope_note": "A control on the metric rather than on a generative method; nothing is generated.",
            "limitations": [
                "The series is the paper's demonstration that the agreement scores move with reference-set size "
                "alone, from 0.790 at 20 references to 0.985 at 800, so raw scores from evaluations with "
                "different reference-set sizes are stated to be mathematically non-comparable.",
                "The paper does not state which family or families the series is computed on.",
            ],
            "missing_metadata": {
                "random_seeds": {"reason": "unreported", "note": "No seeds or repeat counts are printed for the series."},
                "heldout_test": {"reason": "unreported", "note": "The family the series is computed on is not stated."},
            },
            "review": PDF_REVIEW,
        },
        links=[{"relation": "evaluates_task", "target_id": TASK}, {"relation": "uses_data", "target_id": subset}],
    ))

# ------------------------------- the 800-homolog alignment condition, which prints no scores
P_MMD_800 = rid("protocol-ours-800-spectrum-mmd")
add(record(
    P_MMD_800, "protocol", "EditJumps frame with the reference alignment expanded to 800 homologs: spectrum MMD",
    "Normalised spectrum MMD computed with the reference alignment expanded from 200 to 800 homologs, the "
    "condition under which the paper reports the normalised ratio changes enough to invert method rankings.",
    {
        "entity_classification": {
            "review_date": DATE,
            "rationale": "Registered as its own protocol because its reference set differs from the 200-sequence frame, which is the paper's point; no scores are printed under it.",
            "source_ids": [PDF],
            "source_locator": "Section 5, 'expanding the reference alignment from 200 to 800 homologs'",
            "ambiguities": [],
        },
        "metric": "maximum-mean-discrepancy",
        "metric_direction": "lower",
        "metric_qualifier": "k-mer spectrum MMD normalised against the reference floor, reference alignment of 800 homologs",
        "metric_definition": "Maximum mean discrepancy between the k-mer spectra of the generated set and an 800-sequence natural reference alignment, divided by the reference floor.",
        "unit": "unitless",
        "protocol": "As the 200-reference frame, with the reference alignment expanded to 800 homologs.",
        "dataset": "800 held-out natural homologs per family",
        "task": "Homolog-like variant generation from a seed antibody sequence",
        "version": "As described in section 5 of version 1 of the paper",
        "publication_status": "preprint",
        "scope_note": "A computational comparison between generated sequences and natural sequences, not a measured biological property.",
        "limitations": [
            "The paper prints only the change this condition causes, 50% on Ty1 and 26% on HER2-VH in the "
            "normalised ratio, and not the scores themselves, so no result is stored under this protocol.",
            "The paper states the change is large enough to invert method rankings, so the ordering of methods "
            "under normalised spectrum MMD is not stable across reference-set sizes.",
            L_IN_SILICO,
        ],
        "missing_metadata": {
            "random_seeds": {"reason": "unreported", "note": "No seeds are printed."},
            "measurement_status": {"reason": "unreported", "note": "The scores under this condition are not printed, only the percentage change from the 200-reference condition."},
        },
        "review": PDF_REVIEW,
    },
    links=[{"relation": "evaluates_task", "target_id": TASK}, {"relation": "uses_data", "target_id": S_REF_800_ALIGNMENT}],
))


# -------------------------------------------------------------- evaluations and results
OURS_ARMS = {
    "EditJumps": (C_EDITJUMPS, "editjumps",
                  "One seed amino-acid sequence per template and an approximate edit budget",
                  "Zero-shot: one generalist editor applied to a held-out target without per-family retraining",
                  "Clock normalisation 40, set for a budget of about 5 edits per sequence; Euler tau-leaping over 50 steps"),
    "rand. mut.": (C_RAND_MUT, "random-mutations",
                   "One template sequence and an edit budget",
                   "None; a control",
                   "Matched to the realised edit budget of the learned arms"),
    "rand. pair.": (C_RAND_PAIR, "random-pairing",
                    "Pairs of real family homologs",
                    "None; a control",
                    "Not budgeted: the distances are those between natural sequences, about 23 edits per pair"),
    "EvoDiff": (C_EVODIFF, "evodiff-msa",
                "A multiple sequence alignment of the target family and a mutation-budget mask",
                "Released EvoDiff-MSA weights, with the budget-matching mask added by the EditJumps authors",
                "Mutation-budget mask matched to the section 4.2 frame"),
    "Evotune": (C_EVOTUNE, "evotuning",
                "One template sequence, a per-column entropy profile from the family alignment and an edit budget",
                "Per-family retraining of a 650M trunk for 2,000 steps, then iterative infilling",
                "b = 5 on Ty1 and b = 4 on HER2-VH, topped up over up to 8 rounds"),
    "Evotune-f": (C_EVOTUNE_F, "evotuning-forced",
                  "One template sequence, a per-column entropy profile from the family alignment and an edit budget",
                  "Per-family retraining of a 650M trunk for 2,000 steps, then forced infilling",
                  "b = 5 on Ty1 and b = 4 on HER2-VH, guaranteed in a single pass"),
}

OURS_RESULT_NOTE = (
    "Transcribed by hand from the printed table and asserted against the pinned PDF's pdftotext -layout text "
    "layer by extract/check_tables.py, which matches each printed row as a whole, so a value taken from a "
    "neighbouring column fails. The same script asserts that Table 1's upper block prints exactly these values "
    "in its four columns, so the batch stores them once, from Table 2. The two family blocks of Table 2 repeat "
    "their row labels, which the script separates by splitting the printed block at the family heading; a "
    "locator-based value check cannot, so the sampled manual check must cover block assignment."
)
PUBLISHED_RESULT_NOTE = (
    "Transcribed by hand from the lower block of Table 1 and asserted against the pinned PDF's text layer by "
    "extract/check_tables.py, which matches the whole printed row. These are the EvoFlows paper's own reported "
    "values, which the EditJumps paper states are not comparable with its own and whose original conditions it "
    "could not recover; the source record carries an evidence concern scoped to them."
)


def evaluation(eval_id, config_id, protocol_id, data_id, origin, comparison, limitations, locator, note,
               retrospective=True, extra=None, label=None, summary=None):
    attributes = {
        "origin": origin,
        "protocol": comparison.get("protocol_text") or "",
        "comparison": {k: v for k, v in comparison.items() if k != "protocol_text"},
        "limitations": limitations,
        "source_locator": locator,
        "review": PDF_REVIEW,
    }
    if retrospective:
        attributes["retrospective"] = True
    if not attributes["protocol"]:
        del attributes["protocol"]
    if extra:
        attributes.update(extra)
    attributes["review"] = dict(PDF_REVIEW, note=note)
    add(record(eval_id, "evaluation", label or f"Evaluation {eval_id.split('eval-')[-1]}",
               summary or "One evaluated configuration on one protocol and one dataset.", attributes,
               links=[{"relation": "system", "target_id": config_id},
                      {"relation": "assessment", "target_id": protocol_id},
                      {"relation": "data", "target_id": data_id}]))


def result(result_id, eval_id, printed, metric, direction, unit, qualifier, locator, note,
           unit_detail=None, uncertainty=None, limitations=None, numeric=None, label=None, summary=None):
    attributes = {
        "printed_value": printed,
        "metric": metric,
        "metric_direction": direction,
        "metric_qualifier": qualifier,
        "unit": unit,
        "source_locator": locator,
        "review": dict(PDF_REVIEW, note=note),
    }
    attributes["numeric_value"] = printed if numeric is None else numeric
    if unit_detail:
        attributes["unit_detail"] = unit_detail
    if uncertainty:
        attributes["uncertainty"] = uncertainty
    else:
        attributes["missing_metadata"] = {
            "uncertainty": {"reason": "unreported", "note": "The table prints a single value with no interval."}
        }
    if limitations:
        attributes["limitations"] = limitations
    add(record(result_id, "result", label or f"Result {result_id.split('result-')[-1]}",
               summary or "One printed cell of the source's evaluation tables.", attributes,
               links=[{"relation": "evaluation", "target_id": eval_id}]))


# ---- Table 2, the reimplemented block, both families, every identified arm ----------------
for family in (TY1, HER2):
    for arm in T.TABLE2_ARMS_STORED:
        config_id, slug, inputs, adaptation, budget = OURS_ARMS[arm]
        for index, column in enumerate(T.TABLE2_COLUMNS):
            printed = T.TABLE2[family][arm][index]
            if printed == "–":
                continue  # a printed dash is not a value; it is never recorded as zero
            metric, direction, unit, unit_detail, qualifier, definition, extra = OURS_METRICS[column]
            protocol_id = ours_protocols[column]
            suffix = f"{OURS_PROTOCOL_SUFFIX[column]}-{slug}-{family}"
            eval_id = rid(f"eval-ours-200-{suffix}")
            evaluation(
                eval_id, config_id, protocol_id, FAMILY_REFERENCES[family], "author_reported",
                {
                    "protocol_id": protocol_id,
                    "protocol_text": OURS_FRAME,
                    "dataset_version": f"{FAMILY_NAME[family]} homolog family mined from the paired Observed Antibody Space corpus at repository commit {COMMIT}",
                    "split": f"20 templates and 20 variants per template, 400 generated sequences, scored against 200 held-out {FAMILY_NAME[family]} homologs; agreement ceiling {FAMILY_CEILING[family]}",
                    "population": f"One held-out antibody family, {FAMILY_NAME[family]}",
                    "inputs": inputs,
                    "adaptation": adaptation,
                    "metric_implementation": qualifier,
                    "aggregation": "Pooled over the 400 generated sequences of the family",
                    "budget": budget,
                },
                OURS_LIMITS + extra,
                f'Table 2, family block "{family}", row "{arm}", column "{column}"',
                "Reimplemented and run by the authors of the paper; transcribed here, not rerun.",
                extra={"seeds": "Table 1's caption states individual runs and intervals across three seeds; Table 2 prints one value per cell",
                       "scoring_population": f"400 generated sequences against 200 held-out {FAMILY_NAME[family]} homologs"},
                label=f"{arm} on {FAMILY_NAME[family]}, {column}, 200 references",
                summary="Developer-reported evaluation transcribed from the reimplemented block of the pinned EditJumps preprint; not reproduced.",
            )
            result(
                rid(f"result-ours-200-{suffix}"), eval_id, printed, metric, direction, unit, qualifier,
                f'Table 2, family block "{family}", row "{arm}", column "{column}"',
                OURS_RESULT_NOTE, unit_detail=unit_detail, limitations=OURS_LIMITS + extra,
                label=f"{arm} on {FAMILY_NAME[family]}, {column}, 200 references",
                summary="One printed cell of Table 2, the reimplemented block scored against a 200-sequence natural holdout.",
            )

# ---- Table 1, lower block: the EvoFlows paper's own published values ---------------------
PUBLISHED_ARMS = {
    "random pairing": (C_PUB_RAND_PAIR, "random-pairing"),
    "EvoFlows": (C_PUB_EVOFLOWS, "evoflows"),
    "evotuning": (C_PUB_EVOTUNE, "evotuning"),
    "evotuning (forced)": (C_PUB_EVOTUNE_F, "evotuning-forced"),
    "EvoDiff-MSA": (C_PUB_EVODIFF, "evodiff-msa"),
    "random mutations": (C_PUB_RAND_MUT, "random-mutations"),
}
PUBLISHED_FAMILY_COLUMN = {TY1: "Ty1", HER2: "HER2"}
# The column heading as the PDF prints it, which is what a locator-based value check looks for.
PRINTED_COLUMN = {"edits/seq": "edits/seq", "diversity": "diversity", "MMD": "MMD", "KL x10^3": "KL \u00d7103"}

for arm in T.TABLE1_LOWER_ROWS:
    config_id, slug = PUBLISHED_ARMS[arm]
    CONCERN_APPLIES.append(config_id)
    for column in T.TABLE1_LOWER_COLUMNS:
        metric, direction, unit, unit_detail, qualifier, definition = PUBLISHED_METRICS[column]
        protocol_id = published_protocols[column]
        for position, family in enumerate((TY1, HER2)):
            printed = T.TABLE1_LOWER[arm][column][position]
            suffix = f"{PUBLISHED_SUFFIX[column]}-{slug}-{family}"
            eval_id = rid(f"eval-published-{suffix}")
            result_id = rid(f"result-published-{suffix}")
            CONCERN_APPLIES.extend([eval_id, result_id])
            evaluation(
                eval_id, config_id, protocol_id, D_SIX, "author_reported",
                {
                    "protocol_id": protocol_id,
                    "protocol_text": "The conditions under which the EvoFlows paper produced these values, which the replication states it could not recover.",
                    "dataset_version": None,
                    "split": None,
                    "population": f"One antibody family, {FAMILY_NAME[family]}",
                    "inputs": None,
                    "adaptation": "Per-family retraining, which the original approach requires",
                    "metric_implementation": None,
                    "aggregation": None,
                    "budget": None,
                },
                PUBLISHED_LIMITS,
                f'Table 1, lower block, row "{arm}", column "{PRINTED_COLUMN[column]}", sub-column "{PUBLISHED_FAMILY_COLUMN[family]}"',
                "Values reported by the EvoFlows authors and reprinted by the EditJumps paper; neither run nor rerun here.",
                extra={"original_sdk_scope": "The EvoFlows paper's own reported values, reprinted for reference"},
                label=f"{arm} on {FAMILY_NAME[family]}, {column}, EvoFlows published values",
                summary="Reported by the EvoFlows authors under conditions the replication could not recover, and reprinted in the pinned EditJumps preprint; not reproduced.",
            )
            result(
                result_id, eval_id, printed, metric, direction, unit, qualifier,
                f'Table 1, lower block, row "{arm}", column "{PRINTED_COLUMN[column]}", sub-column "{PUBLISHED_FAMILY_COLUMN[family]}"',
                PUBLISHED_RESULT_NOTE, unit_detail=unit_detail, limitations=PUBLISHED_LIMITS,
                label=f"{arm} on {FAMILY_NAME[family]}, {column}, EvoFlows published values",
                summary="One printed cell of the lower block of Table 1, which holds the EvoFlows paper's own reported values.",
            )

for protocol_id in published_protocols.values():
    CONCERN_APPLIES.append(protocol_id)

# ---- Table 4, the ceiling-normalised comparison -------------------------------------------
CEILING_ARMS = {
    "EditJumps (Ours)": ("ours", C_EDITJUMPS, "editjumps", S_POOLED, OURS_LIMITS,
                         "Reimplemented and run by the authors of the paper; transcribed here, not rerun."),
    "EvoFlows (Published)": ("published", C_PUB_EVOFLOWS, "evoflows", D_SIX, PUBLISHED_LIMITS,
                             "Recovered by the EditJumps authors from the EvoFlows paper's Figure 3 by extracting vector paths and calibrating against axis ticks."),
}
for column_label, (arm_key, config_id, slug, data_id, limits, origin_note) in CEILING_ARMS.items():
    for row_label in T.TABLE4_ROWS:
        metric, direction, unit, unit_detail, qualifier, definition = CEILING_METRICS[row_label]
        protocol_id = ceiling_protocols[arm_key][row_label]
        printed = T.TABLE4[row_label][column_label]
        suffix = f"{CEILING_SUFFIX[row_label]}-{slug}"
        eval_id = rid(f"eval-ceiling-{arm_key}-{suffix}")
        result_id = rid(f"result-ceiling-{arm_key}-{suffix}")
        if arm_key == "published":
            CONCERN_APPLIES.extend([eval_id, result_id, protocol_id])
        uncertainty = None
        numeric = printed
        if "±" in printed:
            centre, spread = [p.strip() for p in printed.split("±")]
            numeric = centre
            uncertainty = {
                "type": "unresolved_spread", "value": spread, "printed": printed,
                "note": "The paper does not say what the spread is; Table 1's caption mentions intervals across three seeds.",
            }
        evaluation(
            eval_id, config_id, protocol_id, data_id, "author_reported",
            {
                "protocol_id": protocol_id,
                "protocol_text": "Metrics normalised against the attainable ceiling computed on held-out natural homologs.",
                "dataset_version": "Ty1 and HER2-VH, 200 references each" if arm_key == "ours" else None,
                "split": "Two antibody families, 200 references each" if arm_key == "ours" else None,
                "population": "Two antibody families" if arm_key == "ours" else "Six evaluation datasets",
                "inputs": "One seed amino-acid sequence per template and an approximate edit budget" if arm_key == "ours" else None,
                "adaptation": "Zero-shot, one generalist editor" if arm_key == "ours" else "Per-family retraining, which the original approach requires",
                "metric_implementation": qualifier,
                "aggregation": "Normalised against the natural homolog ceiling",
                "budget": "About 4 to 5 edits per sequence" if arm_key == "ours" else None,
            },
            limits,
            f'Table 4, row "{row_label}", column "{column_label}"',
            origin_note,
            label=f"{column_label}, {row_label}, ceiling-normalised",
            summary="Developer-reported ceiling-normalised comparison transcribed from the pinned EditJumps preprint; not reproduced.",
        )
        result(
            result_id, eval_id, printed, metric, direction, unit, qualifier,
            f'Table 4, row "{row_label}", column "{column_label}"',
            (OURS_RESULT_NOTE if arm_key == "ours" else PUBLISHED_RESULT_NOTE).replace(
                "Table 2", "Table 4").replace("the lower block of Table 1", "Table 4"),
            unit_detail=unit_detail, uncertainty=uncertainty, limitations=limits, numeric=numeric,
            label=f"{column_label}, {row_label}, ceiling-normalised",
            summary="One printed cell of Table 4, the ceiling-normalised comparison.",
        )

# ---- Appendix E: covariance agreement at three reference-set sizes -----------------------
for size, printed in T.COVARIANCE_BY_REFERENCE_SIZE:
    protocol_id = size_protocols[size]
    subset = {"20": S_N20, "100": S_N100, "800": S_N800}[size]
    eval_id = rid(f"eval-covariance-references-{size}")
    evaluation(
        eval_id, C_REFERENCE, protocol_id, subset, "author_reported",
        {
            "protocol_id": protocol_id,
            "protocol_text": f"Score real homologs against real homologs with a reference set of {size} sequences.",
            "dataset_version": None,
            "split": f"{size} natural homologs on each side of the comparison",
            "population": "Held-out natural antibody homologs; the paper does not say which family",
            "inputs": "Two sets of natural homologs of the same family",
            "adaptation": "None; nothing is generated",
            "metric_implementation": f"natural homologs scored against natural homologs at a reference set of {size} sequences",
            "aggregation": None,
            "budget": None,
        },
        [
            "A control on the metric, not a measurement of a generative method.",
            "The series is the paper's evidence that the agreement scores move with reference-set size alone, "
            "so raw scores from evaluations with different reference-set sizes are stated to be mathematically "
            "non-comparable and method orderings taken from them are not stable.",
            L_IN_SILICO,
        ],
        "Appendix E 'Sample-Size Dependency and Grounded Baseline Controls'",
        "Computed by the authors of the paper and printed in prose rather than a table; transcribed here, not rerun.",
        label=f"Natural homologs against natural homologs, covariance agreement, {size} references",
        summary="Developer-reported control on the metric, transcribed from the body text of the pinned EditJumps preprint; not reproduced.",
    )
    result(
        rid(f"result-covariance-references-{size}"), eval_id, printed, "covariance-agreement", "higher",
        "unitless", f"natural homologs scored against natural homologs at a reference set of {size} sequences",
        "Appendix E 'Sample-Size Dependency and Grounded Baseline Controls', the sentence beginning 'Scoring real homologs against real homologs'",
        "Transcribed from the body text, not a table. extract/check_tables.py asserts the printed phrase "
        f"'{printed} at N = {size}' is present in the pinned PDF's text layer. A locator-based value check "
        "cannot parse a prose locator, so this value needs the reviewer's manual check.",
        limitations=[
            "A control on the metric, not a measurement of a generative method.",
            "The paper states that raw scores from evaluations with different reference-set sizes are "
            "mathematically non-comparable, and that an apparent agreement score of 0.79 falls entirely within "
            "the random sampling variance of finite sets.",
            L_IN_SILICO,
        ],
        label=f"Natural homologs against natural homologs, covariance agreement, {size} references",
        summary="One value printed in the body text of Appendix E, where the covariance agreement between two sets of natural homologs is reported at three reference-set sizes.",
    )


# ------------------------------------------------------------------------------- claims
def claim(slug, subject, field, value, locator, sources, name, extra=None, limitations=None, rationale=None):
    sha = {PDF: PDF_SHA,
           CARD: "552199e1e3be6d07de661baf23876fcbc354f8cfd33b391d2913291a3a5a8c32",
           README: "fbf05022b8140519c13bf60db99276df3edcbaeac57f091f54a0dc3921716c05",
           PERF: "01e59ef27b2e93b118b15239e57c6500045c99facd72f0b956e78ecf161217e3",
           LIMITS: "e11bb92210012e08e6a0bc0e6298d098818419f3d661bdae6082c71de9c0b6d8",
           CLAIMS_DOC: "7c7103723b23aa8b36e58974717d5a6e4bc368c83167caac9e8954127c0bcfcc",
           LICENCE: "9f1abe28a25b5f6f95c58a81a647de3fa72ff6388d228c59bddd079255709989",
           ENCODER: "5ab36d96756d5a5f78582be7143e89fff113e15f36101f2658d7208d73667be9",
           HTML: "ae0b05f6a7488dabd73990f02b6a6280a6673e0a6a0f2917713f913a5ec3ec4f"}[sources[0]]
    attributes = {
        "field": field,
        "value": value,
        "source_locator": locator,
        "review": dict(PDF_REVIEW, artifact_sha256=sha,
                       note="Read at the locator this record names and transcribed; not independently checked."),
    }
    if limitations:
        attributes["limitations"] = limitations
    if rationale:
        attributes["rationale"] = rationale
    if extra:
        attributes.update(extra)
    return add(record(rid("claim-" + slug), "claim", name,
                      "A descriptive statement the source makes, with the location it is printed at.",
                      attributes, links=[{"relation": "subject", "target_id": subject}], source_ids=list(sources)))


# Identity and configuration of the released checkpoint
claim("released-parameters", C_RELEASED, "parameters", "35,213,590",
      "Model card 'Model details', Parameters row", [CARD], "Released checkpoint parameter count")
claim("released-trunk", C_RELEASED, "trunk",
      "Stock facebook/esm2_t12_35M_UR50D: 12 hidden layers, hidden size 480, intermediate size 1920, 20 "
      "attention heads, vocabulary 33, rotary position embeddings, fp32. The card states the trunk is "
      "deliberately stock ESM-2 rather than the project's own OAS-adapted trunk, because the EvoFlows "
      "specification calls for no domain adaptation.",
      "Model card 'Model details', Trunk and Precision rows, and the paragraph below the table; model/encoder/config.json",
      [CARD, ENCODER], "Released checkpoint trunk identity")
claim("released-training-corpus", C_RELEASED, "training_data",
      "1,660,105 unordered homolog pairs from the Observed Antibody Space paired corpus of 2,586,927 VH.VL "
      "sequences. Clusters were built with MMseqs2 easy-cluster at minimum sequence identity 0.5 and coverage "
      "0.8 and capped at 20 pairs per family.",
      "Model card 'Model details', Training data row; paper Appendix D 'Corpus Curation and Homolog Clustering'",
      [CARD, PDF], "Released checkpoint training corpus")
claim("released-training-budget", C_RELEASED, "training_budget",
      "20,000 steps at batch size 16, which the card gives as 320,000 pairs and about 19% of one epoch, and "
      "which it states is not converged and not claimed to be. Adam, learning rate 1e-4 constant, no warm-up, "
      "decay or weight decay, gradient clipping 1.0, seed 0.",
      "Model card 'Model details', Budget and Optimizer rows", [CARD], "Released checkpoint training budget",
      limitations=["The card's own Budget row states the run is not converged; nothing in the sources reports a converged run."])
claim("non-convergence", C_EDITJUMPS, "training_convergence",
      "Validation loss fell from 798.0 at initialisation to 149.6 at step 8,500, 138.7 at step 16,000 and 135.2 "
      "at step 19,999. The paper states the model remained non-converged at the 20,000-step budget, with the "
      "final four evaluations improving by 2.3 units over preceding checkpoints.",
      "Appendix D 'Training Protocol and Compute Resources'", [PDF], "Training did not converge",
      limitations=["Every reported score therefore comes from a model the authors state is not converged."])
claim("best-validation-loss-disagreement", C_RELEASED, "validation_loss",
      "The model card gives a best validation loss of 130.48 at step 18,500 and marks the step with its own "
      "'TODO: confirm step' comment, while Appendix D of the paper gives 135.2 at step 19,999 and no value "
      "below it. The two figures are not reconciled in either source.",
      "Model card 'Model details', Best val loss row; paper Appendix D 'Training Protocol and Compute Resources'",
      [CARD, PDF], "Best validation loss differs between the paper and the model card")
claim("head-parameterisation-disagreement", C_EDITJUMPS, "head",
      "Section 3 of the paper lists 'linear rather than MLP rate heads' as one of four operational adaptations "
      "of the scored arm, while the model card's Heads row gives three MLP rate heads and its quickstart loads "
      "the released weights with rate_head mlp and q_head esm_lm_head. Appendix E reports the two "
      "parameterisations give different edit ratios, 0.19 for the published Appendix A heads against 0.22 to "
      "0.28 for lightweight linear heads, so they are not interchangeable.",
      "Section 3 'Supervision discrepancies and deviations'; Figure 3 caption; Appendix E 'Non-Explanations for "
      "the Edit Budget Discrepancy'; model card 'Model details', Heads row and the quickstart command",
      [PDF, CARD], "The scored arm and the released weights state different head parameterisations",
      limitations=["No result in this batch is assigned to the released weights, because the sources do not state that the scored arm and the downloadable checkpoint are the same configuration."])

# Licensing
claim("licence-code-and-weights", M_EDITJUMPS, "licence",
      "All code, model weights and evaluation pipelines for EditJumps are released under an MIT licence. The "
      "repository and the model repository serve byte-identical MIT licence files, and the model card states MIT "
      "for both the code and the weights.",
      "Appendix D 'Operational Integrity and Artifact Verification'; repository LICENSE; model card 'License'",
      [PDF, LICENCE, CARD], "Code and weights licence")
claim("licence-scope", M_EDITJUMPS, "licence_scope",
      "The MIT grant covers this project's code and released weights. It does not cover the pretrained ESM-2 "
      "checkpoint the editor is fine-tuned from or the Observed Antibody Space corpus it is trained on, which "
      "carry their own separate terms and have their own source records.",
      "Model card 'Model details', Trunk and Training data rows, and 'License'; repository LICENSE",
      [CARD, LICENCE], "What the licence does not cover")

# The non-comparability statement and the reference-set finding
claim("values-not-comparable", C_PUB_EVOFLOWS, "comparability",
      "The paper states, before interpreting Table 1: 'our computed values and published EvoFlows values are "
      "not comparable and we could not recover the original experimental conditions from the paper'. Table 1's "
      "caption states the two blocks are not comparable and that each row compares against its own block's "
      "floor and ceiling. The paper also states its released artefacts 'are a specified baseline rather than a "
      "match to the published values, which the reported conditions do not allow us to recover'.",
      "Section 4, first sentence; Table 1 caption; section 1, contribution (ii)", [PDF],
      "The two sets of numbers are not comparable",
      rationale="Recorded as a claim and as an evidence concern on the source record, scoped to the records "
                "that carry the published values, so neither set can be pooled with the other in a comparison "
                "or a leaderboard.")
claim("reference-set-size-inverts-rankings", P_MMD_800, "reference_set_sensitivity",
      "Cross-study benchmarking frequently normalises scores. The paper reports that this holds for relative "
      "edit distance but fails for distributional estimators such as spectrum MMD: expanding the reference "
      "alignment from 200 to 800 homologs alters the normalised ratio by 50% on Ty1 and 26% on HER2-VH, 'a "
      "difference sufficiently large to invert method rankings'. Because both the numerator and the baseline "
      "floor contract with sample size, internal normalisation cannot replace standardised reference sets.",
      "Section 5, the paragraph beginning 'Furthermore, cross-study benchmarking frequently normalises scores'",
      [PDF], "Reference-set size can reverse the ordering of methods",
      limitations=["The paper prints the size of the change but not the scores under the 800-homolog condition, "
                   "so no result is stored for it."])
claim("agreement-scores-sample-size-dependent", C_REFERENCE, "reference_set_sensitivity",
      "Agreement metrics between generated and reference distributions exhibit severe sample-size dependency. "
      "Scoring real homologs against real homologs yields covariance scores of 0.790 at N = 20, 0.921 at "
      "N = 100 and saturates at 0.985 at N = 800, so the paper states that raw scores from evaluations with "
      "differing reference set sizes are mathematically non-comparable, and that an apparent agreement score of "
      "0.79 falls entirely within the random sampling variance of finite sets.",
      "Appendix E 'Sample-Size Dependency and Grounded Baseline Controls'", [PDF],
      "Agreement scores move with reference-set size alone")
claim("covariance-partition-sensitivity", ours_protocols["cov. agr."], "reference_set_sensitivity",
      "Covariance recovery shifts from 83.6% to 85.1% simply by varying reference partitions, which the paper "
      "gives as a reason that ungrounded metrics risk rewarding sequence conservatism rather than genuine "
      "biophysical fitness.",
      "Section 5, the paragraph beginning 'In computational protein engineering'", [PDF],
      "Covariance recovery moves with the reference partition")
claim("ceiling-frame-sensitivity", ceiling_protocols["ours"]["MIP (% of ceiling)"], "ceiling_sensitivity",
      "Ceilings are highly sensitive to multiple sequence alignment projections: computing ceilings in an "
      "unaligned or mismatched frame shifts mutual information product agreement by 2.3 percentage points, so "
      "ceilings must be evaluated in identical coordinate frames.",
      "Appendix E 'Ceiling Normalization and Alignment Frame Sensitivity'", [PDF],
      "Ceiling values depend on the alignment frame")
claim("reference-training-overlap", S_TY1_200, "training_overlap",
      "Evaluation references were 200 sequences per family drawn from held-out family members, but because the "
      "families were mined from the Observed Antibody Space, 113 of Ty1's and 103 of HER2-VH's reference "
      "sequences had been present in the training set. Re-evaluating with strictly disjoint reference sets "
      "shifted spectrum MMD by -36.7% on Ty1 and -12.6% on HER2-VH and increased covariance agreement by 12 to "
      "17 points, driven by greater sequence homogeneity in the disjoint subset, 23.00 against 24.90 "
      "Levenshtein distance.",
      "Appendix E 'Reference Construction and Overlap Impact'", [PDF],
      "More than half of the Ty1 reference set had been seen in training")

# What the evaluation does and does not measure
claim("evaluation-is-in-silico", TASK, "measurement_scope",
      "The paper states 'we note that our evaluation is strictly in silico'. Every reported number is a "
      "comparison between generated sequences and natural sequences: edit counts, pairwise and template "
      "Levenshtein distances, k-mer spectrum MMD, composition KL and Jensen-Shannon divergences, covariance and "
      "mutual information product agreement, entropy delta and profile or ESM-2 log-likelihood. No binding "
      "affinity, specificity, expression, stability or retained function is measured anywhere in the sources.",
      "Section 1, the paragraph ending 'reflect single-domain constructs'; Table 2 column headings; section 5",
      [PDF], "All reported evaluation is computational")
claim("no-variant-scoring", M_EDITJUMPS, "scope",
      "The editor generates variants without scoring their quality or confidence, and operates without target "
      "property conditioning, so the repository states that experimental assays or downstream property models "
      "are required to assess functional fitness. Its internal rate field distinguishes corrupted from natural "
      "sequences but gives no ranking signal among plausible variants.",
      "docs/limitations.md, the first two bullets; docs/claims.md 'Target Property Scope'",
      [LIMITS, CLAIMS_DOC], "The model does not score or rank the variants it proposes")
claim("edit-budget-approximate", M_EDITJUMPS, "edit_budget",
      "The edit budget is calibrated on average rather than guaranteed per sequence. The paper states that "
      "clock normalisation has no closed-form mapping to realised edits, because jump rates vary with time and "
      "sequence context, so achieving a specific edit budget requires empirical calibration rather than "
      "deterministic control. The repository states the --edits parameter 'provides approximate guidance via "
      "clock calibration' and that realised counts vary per sequence, and the README states '--edits is a "
      "target, not a guarantee'.",
      "Section 5 'Limitations'; docs/limitations.md, third bullet; README 'Quick Start' step 5",
      [PDF, LIMITS, README], "The edit budget holds in expectation, not per sequence")
claim("cdr-gap-closure", M_EDITJUMPS, "region_resolved_fidelity",
      "Partitioning antibody sequences by IMGT numbering puts 76% of residues in the structural framework and "
      "24% in complementarity-determining regions. Within the CDR loops, which dictate antigen binding, "
      "EditJumps closes 18.7% on Ty1 and 23.9% on HER2-VH of the composition KL distance between random "
      "mutation and natural homologs, which the paper's Limitations section gives as under 25%. In framework "
      "positions all methods approach the natural floor, 0.0001 to 0.0011. The paper states fidelity is "
      "substantially driven by conserved framework scaffolds.",
      "Section 5 'Limitations'; Appendix E 'Biophysical Analysis: IMGT Regions and Disulfide Retention'",
      [PDF], "High aggregate fidelity is dominated by conserved framework residues",
      limitations=["A high aggregate similarity score is therefore not evidence of a better antigen-binding "
                   "loop, and the candidate variants are not reported to be improved antibodies."])
claim("disulfide-retention", C_EDITJUMPS, "structural_constraint_retention",
      "EditJumps preserves the canonical structural disulfides at IMGT Cys23 and Cys104 in 100% of numberable "
      "generations, 393 of 393 on Ty1 and 389 of 389 on HER2-VH, against 89.0% and 93.8% under the random "
      "mutation baselines.",
      "Appendix E 'Biophysical Analysis: IMGT Regions and Disulfide Retention'", [PDF],
      "Canonical disulfides are retained in every numberable generation",
      limitations=["A sequence-level constraint check on numberable generations, not a measured structure or a folding assay."])
claim("domain-shift", C_EDITJUMPS, "domain_shift",
      "The training regime uses concatenated variable domains, paired VH.VL sequences, which the paper states "
      "introduces a domain shift when the editor is evaluated on isolated heavy chains and nanobodies across "
      "the two target families Ty1 and HER2-VH. The abstract-level statement is that the benchmark targets "
      "reflect single-domain constructs, contrasting with the paired heavy-light chain sequences used during "
      "generalist pretraining.",
      "Section 5 'Limitations'; section 1, the paragraph ending 'used during generalist pretraining'",
      [PDF], "Training is on two-chain pairs, evaluation on single-chain constructs")
claim("evaluation-targets", TASK, "evaluation_targets",
      "Antibody-wide pretraining restricts downstream evaluation to the two accessible antibody targets of the "
      "EvoFlows paper: Ty1, an anti-SARS-CoV-2 VHH, and HER2-VH, an anti-HER2 heavy chain, each evaluated "
      "across 20 templates and 200 held-out homologs. Non-antibody targets have no homologs in the Observed "
      "Antibody Space and anti-EphA2 is unrecoverable in public repositories.",
      "Section 3 'Data curation and evaluation targets'", [PDF], "Only two of the upstream targets could be evaluated")
claim("no-retrained-evoflows-comparator", C_PUB_EVOFLOWS, "comparator_availability",
      "The paper trains one editor on 1.66M homolog pairs and applies it to held-out targets, removing the "
      "per-target retraining the original requires, and states that no per-target-retrained EvoFlows exists to "
      "compare against.",
      "Section 1, contribution (iii)", [PDF], "There is no retrained EvoFlows to compare against")
claim("length-changes", M_EDITJUMPS, "output_behaviour",
      "Unlike infilling models that operate on fixed-length masks and only propose substitutions, this editor "
      "supports insertions and deletions: across 400 evaluated variants per family, roughly half showed length "
      "changes, 195 of 400 on Ty1 at 4.58 mean edits and 198 of 400 on HER2-VH at 4.08 mean edits.",
      "README 'Comparison with Alternatives', first bullet", [README], "About half the generated variants change length")

# Replication findings about the upstream papers
claim("six-of-ten-metrics-not-recomputable", M_EVOFLOWS, "specification_completeness",
      "Of the ten evaluation panels in Figure 3 of the EvoFlows paper, six cannot be deterministically "
      "recomputed from the text alone. Four are well specified, one of them only modulo an unstated MMD kernel "
      "parameter. Of the remaining six, three are referenced solely by name but have standard mathematical "
      "formalisation, two define pairwise matrices without specifying scalar reductions, and one admits "
      "multiple incompatible reductions. Table 3 lists each panel and what is omitted.",
      "Section 4 'Identifying EvoFlows' 10 evaluation metrics'; Table 3", [PDF],
      "Six of the ten upstream metrics are not reproducible from the text")
claim("clock-normalisation-governs-budget", M_EVOFLOWS, "undocumented_hyperparameter",
      "The clock normalisation hyperparameter is omitted from the EvoFlows text and governs the realised edit "
      "budget. A sweep across both families and three seeds finds that a clock rate of approximately 95 "
      "replicates the published edit ratio of 0.43, while the reported evaluation uses 40 for a budget of about "
      "5 edits, and a clock normalisation that optimises MMD sits around 80 or about 8.5 edits. Reconciling "
      "published and replicated edit distributions required reverse-engineering this parameter.",
      "Abstract; section 2.3 'Length-invariant clock normalization'; section 4 'Sensitivity to the clock "
      "normalization hyperparameter'; Figure 2 and its caption; Table 5",
      [PDF], "An undocumented clock normalisation sets the realised edit count")
claim("deletion-supervision-bug", M_EDIT_FLOWS, "specification_discrepancy",
      "The published Edit Flows loss and its reference code conflict on deletion supervision. Equation 23 "
      "assigns zero loss to aligned gap sites, whereas an off-by-one indexing error in the reference code "
      "supervises deletions on adjacent valid residues across 49.2% of training pairs. EditJumps follows "
      "Equation 23.",
      "Section 3 'Supervision discrepancies and deviations'; Appendix C 'Discrepancy in Deletion Supervision in "
      "Edit Flows'; Table 5", [PDF], "The upstream deletion loss and its code disagree")
claim("interpolation-schedule-discrepancy", M_EDIT_FLOWS, "specification_discrepancy",
      "The Edit Flows paper reports a cubic interpolation schedule in its narrative while its figure specifies "
      "a linear one with a code comment saying so. Both deposit identical total cross-entropy mass, but the "
      "linear schedule gives an expected kappa of 0.50 against 0.25 for the cubic, shifting supervision mass "
      "toward later times and raising the expected count of active edit targets per example from 32.7 to 50.1 "
      "across 400 homolog pairs. EditJumps adopts the linear schedule.",
      "Appendix C 'Interpolation Schedule Analysis'", [PDF], "The upstream interpolation schedule is stated two ways")
claim("alignment-parameters-unspecified", M_EVOFLOWS, "specification_completeness",
      "The EvoFlows paper specifies Needleman-Wunsch alignment for training pairs but omits the substitution "
      "matrix parameters and the gap opening and extension penalties, so training labels are partly governed by "
      "third-party library defaults.",
      "Appendix C 'Implicit Library Specifications in Sequence Alignment'", [PDF],
      "Upstream alignment parameters are left to library defaults")
claim("symmetric-pair-enumeration-replicated", D_PAIRS, "verification",
      "The EvoFlows paper states that training pairs are formed by unordered enumeration of homolog pairs. In a "
      "random sample of 2,000 training pairs, 44.9% showed a higher property score for the second sequence, and "
      "44.3% in an independent 4,000-pair audit, consistent with unbiased symmetric enumeration at about 50% "
      "and contrasting with oriented pairing at 100%. The paper states this protocol replicated cleanly without "
      "discrepancy.",
      "Appendix D 'Algorithmic Verification: Symmetric Pair Enumeration'; section 5", [PDF],
      "Symmetric pair enumeration replicated without discrepancy")
claim("trunk-capacity-not-the-cause", C_EDITJUMPS, "ablation",
      "Scaling the ESM-2 trunk from 35M to 650M shifts the edit ratio only from 0.180 to 0.182, well within the "
      "stated seed variance of plus or minus 0.01, so the paper reports an ESM-2 35M trunk matches the 650M "
      "trunk in realised edit scale and distributional fidelity at a fraction of the cost.",
      "Section 3 'Architecture and training protocol'; Appendix E 'Non-Explanations for the Edit Budget "
      "Discrepancy', Trunk capacity bullet", [PDF], "Trunk size does not explain the edit budget gap")
claim("sampler-discretisation", C_EDITJUMPS, "sampler",
      "Against an exact Gillespie mean of 71.29 plus or minus 0.15 edits on a fixed synthetic rate field over "
      "2,000 trajectories from a sequence of length 120, Euler tau-leaping over-fires by 4.44 plus or minus "
      "0.20 edits at 2 steps, 0.76 plus or minus 0.21 at 10 steps and 0.08 plus or minus 0.21 at 50 steps, the "
      "setting used throughout all experimental runs, a relative error under 0.3%.",
      "Appendix B 'Empirical Discretization Analysis: Euler vs. Exact Gillespie'", [PDF],
      "Euler sampling at 50 steps adds negligible discretisation error",
      limitations=["Measured on a fixed synthetic rate field, not on the trained editor."])
claim("sequence-recovery-against-chance", C_EDITJUMPS, "grounded_baseline",
      "An exact sequence recovery rate of 0.21 appears modest in isolation yet represents a 300-fold increase "
      "over chance at matched edit budgets for antibody leads, which the paper gives as its reason that in "
      "silico surrogates are easily misinterpreted without grounded empirical baselines.",
      "Section 5, first paragraph; Appendix E 'Sample-Size Dependency and Grounded Baseline Controls'", [PDF],
      "Sequence recovery of 0.21 is 300-fold over chance")
claim("published-values-recovered-from-a-figure", C_PUB_EVOFLOWS, "value_provenance",
      "Because the EvoFlows paper reported quantitative results exclusively in a figure without tabulated "
      "values, the numerical markers were recovered by extracting vector paths from the published PDF and "
      "calibrating against axis tick marks, with the six series resolved by tick pitch, by domain endpoints and "
      "against a legend printed in a later figure.",
      "Appendix E 'Vector Graphic Extraction and Method Resolution'", [PDF],
      "The published comparison values were recovered from a figure, not a table",
      limitations=["The values are a second-hand reading of a figure rather than printed numbers from the "
                   "upstream paper, which is a further reason they cannot be pooled with the reimplemented block."])
claim("evotuning-unforced-non-intervention", C_EVOTUNE, "control",
      "Because the unforced masked language model frequently re-predicts the template residue, 71.7% unchanged "
      "on Ty1, the paper also evaluates a forced variant that may not return a mask to its previous value, "
      "isolating how much of evotuning's fidelity reflects generative editing rather than non-intervention.",
      "Section 3 'The evotuning baseline'", [PDF], "Most unforced evotuning predictions leave the residue unchanged")

# Runtime, recorded once per source rather than flattened into one figure
claim("runtime-paper", C_EDITJUMPS, "runtime",
      "Primary model training was executed on a single NVIDIA L4 GPU for 20,000 steps at batch size 16 with "
      "Adam at learning rate 1e-4, in 6 h 29 m wall-clock time at 1.09 s/step.",
      "Appendix D 'Training Protocol and Compute Resources'", [PDF],
      "Training runtime as the paper states it",
      limitations=["The three sources give three different runtimes for the same 20,000-step run; they are "
                   "recorded separately rather than reconciled."])
claim("runtime-repository", C_EDITJUMPS, "runtime",
      "The repository's performance notes give the 35M edit-flow editor about 1.05 s/step on an L4 and about "
      "5.8 h for 20,000 steps, and separately record 20,000-step editor runs on an A100 at 3 h 0 m 43 s and "
      "0.54 s/step for the linear schedule and about 3 h 31 m at about 0.63 s/step for the cubic.",
      "docs/performance.md, 'ESM-2 35M Edit-Flow Editor (L4)' and '20,000-Step Editor Runs (A100)'", [PERF],
      "Training runtime as the repository states it",
      limitations=["Its L4 figures differ from the paper's for what both describe as the same 20,000-step run."])
claim("runtime-model-card", C_RELEASED, "runtime",
      "The model card's Training cost row gives about 3 h on one A100 at about 0.54 s/step and about 5.8 h on "
      "an L4.",
      "Model card 'Model details', Training cost row", [CARD],
      "Training runtime as the model card states it",
      limitations=["It names an A100 as the primary figure while the paper names a single L4, and gives no "
                   "wall-clock figure matching the paper's 6 h 29 m."])

# Framing and method identity
claim("unified-framing", M_EDITJUMPS, "framing",
      "The paper identifies Edit Flows and EvoFlows as instances of the pure-jump case of generator matching "
      "with a common jump kernel, and states the two regularity conditions a variable-length space requires: a "
      "non-explosion condition for well-defined waiting times, which Edit Flows achieves with a hard length cap "
      "while EvoFlows leaves the space nominally unbounded, and a length-dependent clock normalisation to stop "
      "the realised jump count growing with candidate length.",
      "Abstract; sections 1 and 2.3; section 7", [PDF], "Both upstream methods are one pure-jump process")
claim("unidentified-table-2-arms", ours_protocols["MMD"], "unidentified_arms",
      "Table 2 prints two further arms, BF-DiT and BF-ESM, whose 20 cells this batch does not store. The two "
      "labels appear nowhere else in the paper, in the repository at the pinned commit, including its 186 KB "
      "findings document, or in the model card, so the system behind those values cannot be identified.",
      "Table 2, rows 'BF-DiT' and 'BF-ESM'", [PDF], "Two arms of Table 2 are never defined",
      limitations=["Recording them would mean inventing an identity for the evaluated system, so they are a "
                   "recorded gap instead."])
claim("diversity-column-label", published_protocols["diversity"], "column_label",
      "Table 1 heads its pairwise Levenshtein column 'diversity', with values from 22.61 to 133.34, while "
      "Figure 1's caption defines diversity as the ratio of mean pairwise Levenshtein distance between the "
      "generated set and random real homolog pairs, whose axis runs from about 1.0 to 1.4. The two uses of the "
      "word are different quantities.",
      "Table 1 column heading 'diversity'; Figure 1 caption", [PDF],
      "The word diversity names two different quantities in the same paper")
claim("ai-use-statement", PDF, "ai_use",
      "The paper states that LLM-based assistance was used across code development, data analysis and "
      "manuscript preparation under direct author supervision, that all code implementations, algorithmic "
      "workflows and metric definitions were audited, verified and executed under the authors' direct "
      "oversight, and that all empirical claims and recovered data points were independently validated against "
      "raw artifacts by the authors.",
      "'AI Use Statement', all three paragraphs", [PDF], "The authors' statement on AI assistance")
claim("developer-reported", M_EDITJUMPS, "evidence_status",
      "Every value in this batch was produced and reported by the developers of EditJumps. None of it has been "
      "independently reproduced by Rewire, no model was run and no number was recomputed here.",
      "Section 4; Tables 1, 2 and 4; Appendix E", [PDF], "All evidence is developer-reported")


# -------------------------------------------------------------------------------- output
def main(text_layer):
    check_tables.main(text_layer)  # fails the build if any transcription disagrees with the PDF
    ids = [r["id"] for r in records]
    assert len(ids) == len(set(ids)), "duplicate record IDs"
    for r in records:
        if r["kind"] in ("result", "evaluation"):
            assert r["links"], f"{r['id']} has no links"
    print(f"records: {len(records)}", file=sys.stderr)
    counts = {}
    for r in records:
        counts[r["kind"]] = counts.get(r["kind"], 0) + 1
    for kind in sorted(counts):
        print(f"  {kind}: {counts[kind]}", file=sys.stderr)
    print(f"evidence concern applies_to: {len(CONCERN_APPLIES)} records", file=sys.stderr)
    out = []
    for r in sorted(records, key=lambda r: r["id"]):
        out.append(json.dumps(r, sort_keys=True, ensure_ascii=False))
    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main(sys.argv[1])
