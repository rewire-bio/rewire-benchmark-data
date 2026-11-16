#!/usr/bin/env python3
"""Build data/omics/poisk-20261115/batch.jsonl from the pinned bioRxiv v1 text layer.

    python3 extract/build_batch.py <layout.txt> <out.jsonl>

<layout.txt> is `pdftotext -layout` run on the pinned PDF
(sha256 526def150fb5ae8f9ac4533efcf16c86e547e636cdb9bfba9a574cd1e2a2f924). The script
asserts the sha256 of that text layer, then every table caption, row label and column
header before it reads a cell, and every prose sentence a transcribed value comes from.
Nothing is read from a figure. Records are written sorted by id.
"""

import hashlib
import json
import re
import sys

LAYOUT_SHA = "e75c18130ca43770d2f0ed05ae96528759666c0e4fa08f7725f5a32b21187696"
PDF_SHA = "526def150fb5ae8f9ac4533efcf16c86e547e636cdb9bfba9a574cd1e2a2f924"
PDF_URL = "https://www.biorxiv.org/content/10.64898/2026.10.24.761513v1.full.pdf"
XML_SHA = "4ae08208acb49686958e1ad6a040494f3234ff7035b8cf41756b913ed6caa826"
XML_URL = "https://www.biorxiv.org/content/early/2026/10/26/2026.10.24.761513.source.xml"
ZEN_V11_SHA = "1b95773c269ca57f971f3b60c5df4558c48edc88b11580ca46e97a06e3d99981"
ZEN_V101_SHA = "c1ee96e66dc4b8a694133aae0536dcc502c6d831b797d50337c002dd987505ee"
EXPLORER_SHA = "7795938b8f8bd488222d9a447f5148756029897d82acc127ef1babf158c46378"

B = "poisk-20261115"
DATE = "2026-11-15"

S_PAPER = f"{B}-source-manuscript-v1"
S_JATS = f"{B}-source-manuscript-v1-jats"
S_ZEN11 = f"{B}-source-zenodo-dataset-v1-1"
S_ZEN101 = f"{B}-source-zenodo-dataset-v1-0-1"
S_EXPLORER = f"{B}-source-explorer"

BENCH = f"{B}-benchmark-binder-decoy"
TASK = f"{B}-task-binder-decoy-discrimination"
D_V101 = f"{B}-dataset-poisk-v1-0-1"
D_V11 = f"{B}-dataset-poisk-v1-1"
SUB_BENCH = f"{B}-data-cofolding-benchmark-22494"
SUB_SCREEN = f"{B}-data-screening-27-targets"
SUB_EPITOPE = f"{B}-data-epitope-annotated-1232"
METHOD_CONSENSUS = f"{B}-method-structural-consensus"

AREAS = ["molecular-interactions", "proteins-complexes"]
FACETS = {"areas": AREAS, "contexts": ["research"]}
FACETS_MODEL = {"areas": AREAS, "contexts": ["research"], "method_types": ["foundation_model"]}

REVIEW_METHOD_NOTE = (
    "Extraction pass. Every stored table value was parsed from the pdftotext -layout text layer of the "
    "pinned bioRxiv v1 PDF by extract/build_batch.py, which asserts the sha256 of the text layer and then "
    "every table caption, row label and column header before reading a cell. Values the paper prints only "
    "in prose were transcribed by hand and the script asserts the sentence they come from. No value was "
    "read from a figure."
)
REVIEWER_NOTE = (
    "Claude (Opus 5) extraction agent; no human review claimed. Extraction only: no independent review is "
    "claimed and a different agent reviews this batch. Transcription from the pinned source is not reproduction."
)


def review(methods=None, note=None, artifact=PDF_SHA, url=PDF_URL):
    out = {
        "method": methods or ["deterministic-table-parse", "pdf-text-parse", "source-hash-verification"],
        "method_note": REVIEW_METHOD_NOTE,
        "reviewer": ["claude"],
        "reviewer_note": REVIEWER_NOTE,
        "date": DATE,
    }
    if artifact:
        out["artifact_sha256"] = artifact
    if url:
        out["retrieval_url"] = url
    if note:
        out["note"] = note
    return out


# --- engines -----------------------------------------------------------------------------
# key, printed name in Tables 1, 2 and 7, printed column head in Table 8, model record it configures
ENGINES = [
    ("alphafold-multimer", "AlphaFold-Multimer", "AF-M", f"{B}-model-alphafold-multimer"),
    ("boltz-2", "Boltz-2", "Boltz-2", "catalog-model-boltz-2"),
    ("intellifold-v2", "IntelliFold v2", "IF v2", f"{B}-model-intellifold"),
    ("openfold3", "OpenFold3", "OF3", f"{B}-model-openfold3"),
    ("protenix-v1", "Protenix-v1", "Prot-v1", "ucc-research-model-protenix"),
    ("protenix-v2", "Protenix-v2", "Prot-v2", "ucc-research-model-protenix"),
]
CONFIG = {key: f"{B}-config-{key}" for key, *_ in ENGINES}
PRINTED = {key: printed for key, printed, *_ in ENGINES}
T8COL = {key: col for key, _, col, _ in ENGINES}

SAMPLING = {
    "alphafold-multimer": "the five AlphaFold-Multimer parameter models as the five predictions",
    "boltz-2": "one diffusion sample at each of five random seeds",
    "intellifold-v2": "one diffusion sample at each of five random seeds",
    "openfold3": "one diffusion sample at each of five random seeds",
    "protenix-v1": "one diffusion sample at each of five random seeds",
    "protenix-v2": "one diffusion sample at each of five random seeds",
}
CONFIG_DESC = {
    "alphafold-multimer": (
        "Folds an antibody heavy chain, light chain and target sequence with AlphaFold-Multimer over its five "
        "parameter models, keeps the highest-confidence complex and ranks candidates by the full-Fv ipSAE score "
        "of that complex."
    ),
    "boltz-2": (
        "Folds an antibody heavy chain, light chain and target sequence with Boltz-2 at five random seeds, keeps "
        "the highest-confidence complex and ranks candidates by its full-Fv ipSAE score."
    ),
    "intellifold-v2": (
        "Folds an antibody heavy chain, light chain and target sequence with IntelliFold v2 at five random seeds, "
        "keeps the highest-confidence complex and ranks candidates by its full-Fv ipSAE score."
    ),
    "openfold3": (
        "Folds an antibody heavy chain, light chain and target sequence with OpenFold3 at five random seeds, keeps "
        "the highest-confidence complex and ranks candidates by its full-Fv ipSAE score."
    ),
    "protenix-v1": (
        "Folds an antibody heavy chain, light chain and target sequence with the first Protenix release at five "
        "random seeds, keeps the highest-confidence complex and ranks candidates by its full-Fv ipSAE score."
    ),
    "protenix-v2": (
        "Folds an antibody heavy chain, light chain and target sequence with the second Protenix release at five "
        "random seeds, keeps the highest-confidence complex and ranks candidates by its full-Fv ipSAE score."
    ),
}

NEW_MODELS = [
    (
        f"{B}-model-alphafold-multimer",
        "AlphaFold-Multimer",
        "AlphaFold-Multimer",
        "AlphaFold-Multimer predicts the structure of a multi-chain protein complex from the sequences of its "
        "chains, offering five trained parameter sets as alternative predictions.",
    ),
    (
        f"{B}-model-intellifold",
        "IntelliFold",
        "IntelliFold v2",
        "IntelliFold predicts an antibody-antigen complex structure from the heavy-chain, light-chain and target "
        "sequences and scores the predicted interface.",
    ),
    (
        f"{B}-model-openfold3",
        "OpenFold3",
        "OpenFold3",
        "OpenFold3 predicts all-atom biomolecular complex structures from sequence inputs and returns interface "
        "confidence estimates alongside the coordinates.",
    ),
]

CONSENSUS_CONFIGS = [
    (
        f"{B}-config-consensus-k3-dockq-0-23",
        "Cross-model structural consensus, at least three models at DockQ 0.23",
        "k >= 3, DockQ >= 0.23",
        "Counts how many of the six folding models reproduce a candidate's predicted pose at DockQ 0.23 or better "
        "and calls the candidate with more agreeing models the binder, requiring at least three.",
    ),
    (
        f"{B}-config-consensus-k3-dockq-0-80",
        "Cross-model structural consensus, at least three models at DockQ 0.80",
        "k >= 3, DockQ >= 0.80",
        "Counts how many of the six folding models reproduce a candidate's predicted pose at DockQ 0.80 or better "
        "and calls the candidate with more agreeing models the binder, requiring at least three.",
    ),
]

# --- protocols ---------------------------------------------------------------------------
IPSAE_NOTE = (
    "Full-Fv ipSAE: the interaction prediction Score from Aligned Errors computed asymmetrically with the paired "
    "antibody VH and VL concatenated as one chain against the target (VH+VL to Target), with a PAE cutoff of 10 "
    "angstrom and a distance cutoff of 10 angstrom, using a modified implementation of the ipSAE tool. It is a "
    "structural confidence score used here to rank candidates; it is not a measured binding or affinity value."
)

PROTOCOLS = {
    "cohens-d-iptm": dict(
        name="POISK binder-decoy separation in ipTM, Cohen's d",
        description=(
            "Standardised mean difference between the ipTM score distributions of the 11,247 binder complexes and "
            "the 11,247 putative non-binder complexes of the POISK co-folding benchmark."
        ),
        metric="cohens-d", unit="unitless", direction="higher",
        qualifier="separation of binder and decoy ipTM score distributions over all 22,494 complexes",
        data=SUB_BENCH, denominator=22494,
        definition=(
            "\"Separation between binding and non-binding populations was quantified using Cohen's d\" "
            "(Section 3.2.1, quoted). The score is ipTM, the interface predicted template modelling score of the "
            "top-ranked structure."
        ),
        limitations=[
            "A distribution-separation statistic, not a decision accuracy; it says nothing about the threshold a "
            "user would pick.",
            "The non-binding population consists of putative negatives that were constructed, not antibodies shown "
            "experimentally not to bind.",
        ],
    ),
    "cohens-d-ipsae": dict(
        name="POISK binder-decoy separation in full-Fv ipSAE, Cohen's d",
        description=(
            "Standardised mean difference between the full-Fv ipSAE score distributions of the 11,247 binder "
            "complexes and the 11,247 putative non-binder complexes of the POISK co-folding benchmark."
        ),
        metric="cohens-d", unit="unitless", direction="higher",
        qualifier="separation of binder and decoy full-Fv ipSAE score distributions over all 22,494 complexes",
        data=SUB_BENCH, denominator=22494,
        definition=(
            "Cohen's d between the binder and decoy populations of the full-Fv ipSAE score. " + IPSAE_NOTE
        ),
        limitations=[
            "A distribution-separation statistic, not a decision accuracy.",
            "ipSAE values cluster at exactly zero when no confident interface is produced, which the paper says "
            "compresses the distribution (Appendix E).",
            "The non-binding population consists of constructed putative negatives.",
        ],
    ),
    "pairwise-coverage-100": dict(
        name="POISK pairwise binder-versus-decoy accuracy at 100% coverage",
        description=(
            "Share of the 11,247 binder and putative non-binder pairs in which the full-Fv ipSAE score of the "
            "patent-supported binder exceeds that of its paired decoy, over every pair, with exact ties scored as "
            "half a success."
        ),
        metric="paired-accuracy", unit="fraction", direction="higher",
        qualifier="binder scored above its matched putative decoy by full-Fv ipSAE, 100% coverage of the 11,247 pairs, exact ties at half credit",
        data=SUB_BENCH, denominator=11247, coverage_share="100%",
    ),
    "pairwise-coverage-75": dict(
        name="POISK pairwise binder-versus-decoy accuracy at 75% coverage",
        description=(
            "Share of binder and putative non-binder pairs in which the binder's full-Fv ipSAE exceeds its decoy's, "
            "over the 75% of the 11,247 pairs with the highest within-pair maximum ipSAE."
        ),
        metric="paired-accuracy", unit="fraction", direction="higher",
        qualifier="binder scored above its matched putative decoy by full-Fv ipSAE, top 75% of the 11,247 pairs ranked by within-pair maximum ipSAE, exact ties at half credit",
        data=SUB_BENCH, denominator=11247, coverage_share="75%",
    ),
    "pairwise-coverage-50": dict(
        name="POISK pairwise binder-versus-decoy accuracy at 50% coverage",
        description=(
            "Share of binder and putative non-binder pairs in which the binder's full-Fv ipSAE exceeds its decoy's, "
            "over the most confident half of the 11,247 pairs. This is the paper's headline pairwise figure."
        ),
        metric="paired-accuracy", unit="fraction", direction="higher",
        qualifier="binder scored above its matched putative decoy by full-Fv ipSAE, top 50% of the 11,247 pairs ranked by within-pair maximum ipSAE, exact ties at half credit",
        data=SUB_BENCH, denominator=11247, coverage_share="50%",
    ),
    "pairwise-coverage-25": dict(
        name="POISK pairwise binder-versus-decoy accuracy at 25% coverage",
        description=(
            "Share of binder and putative non-binder pairs in which the binder's full-Fv ipSAE exceeds its decoy's, "
            "over the 25% of the 11,247 pairs with the highest within-pair maximum ipSAE."
        ),
        metric="paired-accuracy", unit="fraction", direction="higher",
        qualifier="binder scored above its matched putative decoy by full-Fv ipSAE, top 25% of the 11,247 pairs ranked by within-pair maximum ipSAE, exact ties at half credit",
        data=SUB_BENCH, denominator=11247, coverage_share="25%",
    ),
    "pairwise-coverage-10": dict(
        name="POISK pairwise binder-versus-decoy accuracy at 10% coverage",
        description=(
            "Share of binder and putative non-binder pairs in which the binder's full-Fv ipSAE exceeds its decoy's, "
            "over the 10% of the 11,247 pairs with the highest within-pair maximum ipSAE."
        ),
        metric="paired-accuracy", unit="fraction", direction="higher",
        qualifier="binder scored above its matched putative decoy by full-Fv ipSAE, top 10% of the 11,247 pairs ranked by within-pair maximum ipSAE, exact ties at half credit",
        data=SUB_BENCH, denominator=11247, coverage_share="10%",
    ),
    "pairwise-tie-fraction": dict(
        name="POISK pairs left undecidable by identical ipSAE",
        description=(
            "Share of the 11,247 binder and putative non-binder pairs in which the binder and the decoy receive "
            "numerically identical full-Fv ipSAE, which the paper says is what caps pairwise accuracy at full coverage."
        ),
        metric="proportion", unit="percent", direction="unknown",
        qualifier="pairs in which binder and decoy receive numerically identical full-Fv ipSAE, over all 11,247 pairs",
        data=SUB_BENCH, denominator=11247,
        definition=(
            "\"The tie column is the fraction of all 11,247 pairs in which binder and decoy receive numerically "
            "identical ipSAE, which is what caps accuracy at full coverage\" (Table 7 caption, quoted)."
        ),
        limitations=[
            "A property of the engine's willingness to produce any confident interface, not of how well it ranks "
            "the interfaces it does produce.",
            "Lower is not straightforwardly better: the paper reports it to explain the compression of accuracy at "
            "full coverage, and states no desirable direction.",
        ],
    ),
    "screen-1in50-top1": dict(
        name="POISK 1-in-50 screening simulation, top-1 retrieval",
        description=(
            "How often ranking one patent-supported binder and 49 putative non-binders for the same antigen by "
            "full-Fv ipSAE puts the binder first, averaged over 27 antigen constructs with 20 trials each and 25 "
            "scenario-generation seeds."
        ),
        metric="top-1-accuracy", unit="percent", direction="higher",
        qualifier="retrieval; one patent-supported binder ranked against 49 putative decoys for the same antigen by full-Fv ipSAE, mean over 27 antigen constructs, 20 trials per construct per seed, 25 seeds",
        data=SUB_SCREEN, denominator=540,
    ),
    "screen-1in50-top10": dict(
        name="POISK 1-in-50 screening simulation, top-10 retrieval",
        description=(
            "How often ranking one patent-supported binder and 49 putative non-binders for the same antigen by "
            "full-Fv ipSAE puts the binder in the ten highest-scoring candidates."
        ),
        metric="top-10-accuracy", unit="percent", direction="higher",
        qualifier="retrieval; one patent-supported binder ranked against 49 putative decoys for the same antigen by full-Fv ipSAE, mean over 27 antigen constructs, 20 trials per construct per seed, 25 seeds",
        data=SUB_SCREEN, denominator=540,
    ),
    "epitope-recovery": dict(
        name="POISK epitope contact recovery",
        description=(
            "Share of the 1,232 binder records carrying residue-level patent epitope annotations in which the "
            "predicted complex places an antibody heavy atom within 4 angstrom of at least one annotated epitope "
            "residue."
        ),
        metric="success-rate", unit="percent", direction="higher",
        qualifier="at least one annotated epitope residue with a heavy atom within 4 angstrom of an antibody heavy atom, over 1,232 binder records with mappable patent epitope annotations",
        data=SUB_EPITOPE, denominator=1232,
        definition=(
            "\"We counted a record as recovered when at least one annotated epitope residue had a heavy atom "
            "within 4A of an antibody heavy atom\" (Section 3.3.2, quoted)."
        ),
        limitations=[
            "The reference is a patent text annotation mapped onto the folded antigen construct, not an "
            "experimentally resolved structure; the paper states no resolved structures were available.",
            "A single residue contact is a weak criterion: it does not establish that the predicted binding mode "
            "is correct.",
        ],
    ),
    "consensus-pairwise-accuracy": dict(
        name="POISK pairwise binder-versus-decoy accuracy under cross-model structural consensus",
        description=(
            "Share of eligible binder and putative non-binder pairs in which the candidate with more folding models "
            "agreeing on its pose, above a DockQ threshold, is the patent-supported binder."
        ),
        metric="paired-accuracy", unit="percent", direction="higher",
        qualifier="binder identified as the pair member with more agreeing folding-model poses above a DockQ threshold, over the pairs eligible at that threshold",
        data=SUB_BENCH,
        definition=(
            "\"we calculated DockQ scores for the Fv-antigen interface and defined consensus as two or more models "
            "predicting the same pose above a given threshold. For any given pair, a prediction was considered "
            "successful if the binder demonstrated structural agreement amongst more models than its decoy\" "
            "(Section 3.3.1, quoted)."
        ),
        limitations=[
            "Scored only on the pairs where the consensus requirement is met, so accuracy and coverage must be read "
            "together; the denominator changes with the threshold.",
            "Requires all six models to have been run on every candidate, which is the paper's own 9,000 GPU-hour "
            "budget rather than a practical screening configuration.",
        ],
    ),
    "consensus-pair-coverage": dict(
        name="POISK pair coverage under cross-model structural consensus",
        description=(
            "Share of the 11,247 binder and putative non-binder pairs that remain eligible for classification once a "
            "cross-model pose-agreement requirement is imposed."
        ),
        metric="proportion", unit="percent", direction="unknown",
        qualifier="share of the 11,247 pairs eligible for classification under a cross-model pose-agreement requirement",
        data=SUB_BENCH, denominator=11247,
        limitations=[
            "Coverage falls steeply as the requirement tightens, so a high consensus accuracy applies to a small "
            "share of candidates.",
        ],
    ),
}
for key, spec in PROTOCOLS.items():
    spec.setdefault("definition", None)
    spec.setdefault("limitations", [])
    spec.setdefault("denominator", None)
    spec.setdefault("coverage_share", None)

PROTOCOL_ID = {key: f"{B}-protocol-{key}" for key in PROTOCOLS}

COVERAGE_LOCATOR = {
    "100": "Table 7, row \"{row}\", column \"100%\"",
    "75": "Table 7, row \"{row}\", column \"75%\"",
    "50": "Table 7, row \"{row}\", column \"50%\"",
    "25": "Table 7, row \"{row}\", column \"25%\"",
    "10": "Table 7, row \"{row}\", column \"10%\"",
}

SCREEN_SEED_SCOPE = (
    "sample standard deviation of the per-seed means across the 25 scenario-generation seeds, in percentage "
    "points; Figure 5 plots plus or minus twice this quantity"
)


# --- parsing -----------------------------------------------------------------------------
def fail(message):
    raise SystemExit(f"build_batch.py: {message}")


def read_layout(path):
    data = open(path, "rb").read()
    got = hashlib.sha256(data).hexdigest()
    if got != LAYOUT_SHA:
        fail(f"text layer sha256 {got} is not the pinned {LAYOUT_SHA}")
    return data.decode("utf-8").splitlines()


def caption_index(lines, needle):
    hits = [i for i, l in enumerate(lines) if needle in l]
    if len(hits) != 1:
        fail(f"expected exactly one line holding {needle!r}, found {len(hits)}")
    return hits[0]


def assert_order(lines, start, stop, labels, what):
    """Exactly one line between start and stop must hold `labels` left to right, in order."""
    found = []
    for l in lines[start:stop]:
        at, pos, ok = -1, [], True
        for label in labels:
            at = l.find(label, at + 1)
            if at < 0:
                ok = False
                break
            pos.append(at)
        if ok and pos == sorted(pos):
            found.append(l)
    if len(found) != 1:
        fail(f"{what}: expected one line holding {labels} in order, found {len(found)}")


def numbers(line, label):
    rest = line.strip()[len(label):]
    return re.findall(r"-?\d+\.?\d*%?", rest)


def row_line(lines, start, stop, label):
    """The one line between start and stop whose text begins with `label`."""
    hits = [l for l in lines[start:stop] if l.strip().startswith(label)]
    if len(hits) != 1:
        fail(f"expected one row {label!r} between lines {start} and {stop}, found {len(hits)}")
    return hits[0]


def parse_table1(lines):
    cap = caption_index(lines, "Table 1: Summary of benchmark performance for six structure prediction models.")
    head = " ".join(lines[cap:cap + 14])
    for want in ["Cohen's d", "Accuracy at", "1-in-50", "ipTM", "ipSAE", "50% Pairs", "Top-1 Acc."]:
        if want.replace("'", "’") not in head and want not in head:
            fail(f"Table 1 header is missing {want!r}")
    assert_order(lines, cap, cap + 12, ["Cohen\u2019s d", "Accuracy at", "1-in-50"], "Table 1 group header")
    assert_order(lines, cap, cap + 12, ["ipTM", "ipSAE", "50% Pairs", "Top-1 Acc."], "Table 1 column header")
    out = {}
    for key, printed, *_ in ENGINES:
        cells = numbers(row_line(lines, cap, cap + 24, printed), printed)
        if len(cells) != 4:
            fail(f"Table 1 row {printed!r} gave {cells}, expected four cells")
        out[key] = dict(zip(["cohens_d_iptm", "cohens_d_ipsae", "accuracy_50", "top1"], cells))
    return out


def parse_table2(lines):
    cap = caption_index(lines, "Table 2: Epitope Recovery Rate by Engine")
    head = " ".join(lines[cap:cap + 6])
    for want in ["Epitope Recovery", "Records (%)", "Engine"]:
        if want not in head:
            fail(f"Table 2 header is missing {want!r}")
    out = {}
    for key, printed, *_ in ENGINES:
        cells = numbers(row_line(lines, cap, cap + 16, printed), printed)
        if len(cells) != 1:
            fail(f"Table 2 row {printed!r} gave {cells}, expected one cell")
        out[key] = cells[0]
    return out


def parse_table7(lines):
    cap = caption_index(lines, "Table 7: Pairwise binder-versus-decoy accuracy as a function of coverage.")
    head = " ".join(lines[cap:cap + 12])
    for want in ["Coverage", "Ties", "100%", "75%", "50%", "25%", "10%"]:
        if want not in head:
            fail(f"Table 7 header is missing {want!r}")
    assert_order(lines, cap, cap + 10, ["Model", "Ties"], "Table 7 row-label header")
    assert_order(lines, cap, cap + 10, ["100%", "75%", "50%", "25%", "10%"], "Table 7 coverage header")
    out = {}
    for key, printed, *_ in ENGINES:
        cells = numbers(row_line(lines, cap, cap + 22, printed), printed)
        if len(cells) != 6:
            fail(f"Table 7 row {printed!r} gave {cells}, expected six cells")
        if not cells[0].endswith("%"):
            fail(f"Table 7 row {printed!r} first cell {cells[0]!r} is not the tie percentage")
        out[key] = dict(zip(["ties", "c100", "c75", "c50", "c25", "c10"], cells))
    return out


def parse_table8_summary(lines):
    cap = caption_index(lines, "Table 8: Top-1 accuracy (%) in the 1-in-50 screening simulation for each antigen construct.")
    head = " ".join(lines[cap:cap + 14])
    for want in ["UniProt", "AF-M", "Boltz-2", "IF v2", "OF3", "Prot-v1", "Prot-v2"]:
        if want not in head:
            fail(f"Table 8 header is missing {want!r}")
    assert_order(lines, cap, cap + 12, ["#", "UniProt", "n", "L"] + [col for _, _, col, _ in ENGINES],
                 "Table 8 column header")
    body = lines[cap:cap + 60]
    constructs = [l for l in body if re.match(r"\s*\d{1,2}\s+[A-Z]\d[A-Z0-9]{3,5}\s", l)]
    if len(constructs) != 27:
        fail(f"Table 8 body holds {len(constructs)} construct rows, expected 27")
    rows = {}
    for label, field in [
        ("Mean over targets", "mean"),
        ("SD across targets (pp)", "sd_targets"),
        ("SD across seeds (pp)", "sd_seeds"),
    ]:
        cells = numbers(row_line(lines, cap, cap + 60, label), label)
        if len(cells) != 6:
            fail(f"Table 8 row {label!r} gave {cells}, expected six cells")
        rows[field] = {key: cells[i] for i, (key, *_) in enumerate(ENGINES)}
    return rows


PROSE = {
    "top1_prot_v2": (
        "identifying the true binder as the top-ranked candidate in 28.9% of tests",
        "28.9",
    ),
    "top1_boltz": ("Boltz-2 reached a Top-1 accuracy of 3.1%", "3.1"),
    "top10_pair": (
        "placing the true binder in the Top-10 in 54.7% and 56.0% of cases, respectively",
        ("54.7", "56.0"),
    ),
    "consensus_023": ("the pairwise accuracy is 73.1% and covers 54.2% of the pairs", ("73.1", "54.2")),
    "consensus_080_acc": ("at k ≥ 3 and DockQ ≥ 0.80, accuracy reaches 96.8%", "96.8"),
    "consensus_080_cov": (
        "leaving only 3.0% of pairs eligible for classification at this stringent consensus level",
        "3.0",
    ),
    "error_bars": ("error bars indicate ±2σ (sample standard deviation across runs)", None),
    "trials": (
        "20 independent simulation tests per target, resulting in a total of 540 unique discovery trials",
        None,
    ),
    "seeds": ("Each simulation was repeated over 25 independent random seeds", None),
    "putative": (
        "these pairs remain putative negatives and have not been experimentally validated for lack of binding",
        None,
    ),
    "ties_half": ("Exact ties receive half credit", None),
    "half_dataset": ("achieving an accuracy of 0.87 at the half-dataset mark", None),
    "full_coverage": ("Over all 11,247 pairs, without this filter, Protenix-v2 reaches 0.72", None),
}


def assert_prose(lines):
    flat = re.sub(r"\s+", " ", " ".join(lines))
    for key, (sentence, _) in PROSE.items():
        if sentence not in flat:
            fail(f"prose assertion {key} not found in the pinned text layer: {sentence!r}")


# --- record helpers ----------------------------------------------------------------------
def record(rid, kind, name, description, attributes, links=None, sources=None, facets=None, status="source_checked"):
    return {
        "id": rid,
        "kind": kind,
        "name": name,
        "description": description,
        "status": status,
        "facets": facets if facets is not None else dict(FACETS),
        "source_ids": sources or [S_PAPER],
        "links": links or [],
        "attributes": attributes,
    }


def claim(slug, subject, field, value, locator, sources=None, rationale=None, limitations=None, name=None,
          methods=None, artifact=PDF_SHA, url=PDF_URL):
    attrs = {"field": field, "value": value, "source_locator": locator, "review": review(
        methods=methods or ["pdf-text-parse", "source-hash-verification"], artifact=artifact, url=url,
    )}
    if rationale:
        attrs["rationale"] = rationale
    if limitations:
        attrs["limitations"] = limitations
    return record(
        f"{B}-claim-{slug}", "claim", name or f"POISK: {field.replace('_', ' ')}",
        "Descriptive fact transcribed from the pinned source with its own locator.",
        attrs, links=[{"relation": "subject", "target_id": subject}], sources=sources or [S_PAPER],
        facets={},
    )


def evaluation(rid, name, config, protocol_key, data, locator, extra=None):
    spec = PROTOCOLS[protocol_key]
    comparison = {
        "protocol_id": PROTOCOL_ID[protocol_key],
        "dataset_version": "POISK dataset version 1.0.1; the folding predictions of the six models were run against that version",
        "split": "Evaluation only; the benchmark is scored in full and nothing is held out for training",
        "population": spec["qualifier"],
        "inputs": "Antibody heavy-chain and light-chain amino-acid sequences and the target amino-acid sequence, with ColabFold multiple sequence alignments and no templates",
        "adaptation": "Zero-shot: no model was trained or fine-tuned on POISK",
        "metric_implementation": IPSAE_NOTE,
        "aggregation": spec.get("aggregation_note") or "As printed by the source for this endpoint",
        "budget": "Folding all 22,494 complexes with all six models took approximately 9,000 NVIDIA B200 GPU-hours",
    }
    attrs = {
        "origin": "author_reported",
        "protocol": PROTOCOL_ID[protocol_key],
        "comparison": comparison,
        "retrospective": True,
        "source_locator": locator,
        "version": "bioRxiv preprint v1 posted 26 October 2026, retrieved 2026-11-15",
        "limitations": [
            "Reported by the authors of the benchmark, who built the dataset and ran every model on it. Not "
            "reproduced by Rewire.",
            "The scores being ranked are structural confidence scores, not measured binding or affinity.",
            "The negatives are putative: constructed from repertoire antibodies or by germline reversion, not shown "
            "experimentally not to bind.",
        ],
        "review": review(note="Transcribed from the pinned preprint; not rerun."),
    }
    if spec["denominator"]:
        attrs["denominator"] = spec["denominator"]
    if extra:
        attrs.update(extra)
    return record(
        rid, "evaluation", name,
        "Author-reported measurement transcribed from the pinned preprint. Not independently reproduced.",
        attrs,
        links=[
            {"relation": "system", "target_id": config},
            {"relation": "assessment", "target_id": PROTOCOL_ID[protocol_key]},
            {"relation": "data", "target_id": data},
        ],
    )


def result(rid, name, eval_id, protocol_key, printed, numeric, locator, extra=None, unit=None, qualifier=None):
    spec = PROTOCOLS[protocol_key]
    attrs = {
        "metric": spec["metric"],
        "metric_qualifier": qualifier or spec["qualifier"],
        "metric_direction": spec["direction"],
        "unit": unit or spec["unit"],
        "printed_value": printed,
        "numeric_value": numeric,
        "source_locator": locator,
        "review": review(),
    }
    if spec["denominator"]:
        attrs["denominator"] = spec["denominator"]
    if extra:
        attrs.update(extra)
    return record(
        rid, "result", name,
        "Author-reported value transcribed from the pinned preprint. Not independently reproduced.",
        attrs, links=[{"relation": "evaluation", "target_id": eval_id}], facets={},
    )


def main():
    if len(sys.argv) != 3:
        fail("usage: build_batch.py <layout.txt> <out.jsonl>")
    lines = read_layout(sys.argv[1])
    assert_prose(lines)
    t1, t2, t7, t8 = parse_table1(lines), parse_table2(lines), parse_table7(lines), parse_table8_summary(lines)

    # cross-checks between tables that the paper prints twice
    if t1["protenix-v2"]["top1"] != "0.29" or t8["mean"]["protenix-v2"] != "28.9":
        fail("the two printings of the Protenix-v2 1-in-50 top-1 value changed")
    if t1["protenix-v2"]["accuracy_50"] != "0.87" or t7["protenix-v2"]["c50"] != "0.868":
        fail("the two printings of the Protenix-v2 50%-coverage accuracy changed")

    recs = []

    # ---------------- sources ----------------
    recs.append(record(
        S_PAPER, "source",
        "Tupikina et al. 2026, Can Folding Models Tell Binders from Bluffers? Evidence from POISK (bioRxiv v1 PDF)",
        "The bioRxiv preprint that introduces the POISK dataset and benchmarks six folding models as binder-decoy "
        "classifiers; every stored value comes from this PDF.",
        {
            "url": PDF_URL,
            "version": "v1, posted 26 October 2026",
            "retrieved_at": "2026-11-15T23:32:24Z",
            "doi": "10.64898/2026.10.24.761513",
            "publication_status": "preprint",
            "artifact_sha256": PDF_SHA,
            "archive_sha256": "39d2ff104527916aa9b33386ca5d2830d2efd9e14b4d98258af54f07b0598950",
            "artifact_format": "application/pdf, 16 pages",
            "licence": "CC BY 4.0, as printed in the per-page banner of the PDF",
            "article_licence": "CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)",
            "retrieval_method": "curl; bioRxiv rate-limited the first attempts with HTTP 429 and served the PDF on retry",
            "hash_scope": "The PDF bytes. The gzipped pdftotext -layout text layer kept in artifacts/ carries archive_sha256; every stored table value was parsed from that text layer.",
            "source_locator": "Whole preprint; per-value locators are on each record",
            "limitations": [
                "Preprint, not certified by peer review as posted. The project site states the paper was accepted at "
                "NeurIPS 2026; no peer-reviewed version was retrieved.",
                "A version 2 of this preprint was posted on 14 November 2026. Its abstract as served by the bioRxiv "
                "API is identical to v1's, but its full text was not available in the bioRxiv JATS feed and its PDF "
                "was not retrieved. Every record in this batch is pinned to v1.",
                "Tables 1 to 9 are images in the bioRxiv JATS XML, so values were read from the PDF text layer, not "
                "from XML table markup.",
            ],
            "review": review(
                methods=["source-hash-verification", "pdf-text-parse"],
                note="The PDF was downloaded on 2026-11-15 and its sha256 recorded. pdftotext (poppler 26.08.0) "
                     "-layout produced the text layer whose sha256 the extraction script asserts.",
            ),
        },
    ))
    recs.append(record(
        S_JATS, "source",
        "Tupikina et al. 2026 POISK preprint, bioRxiv JATS XML (v1)",
        "The bioRxiv production XML for version 1 of the POISK preprint, which carries the article text, the figure "
        "and table captions and the article metadata.",
        {
            "url": XML_URL,
            "version": "v1 production XML, posted 26 October 2026",
            "retrieved_at": "2026-11-15T23:30:15Z",
            "doi": "10.64898/2026.10.24.761513",
            "publication_status": "preprint",
            "artifact_sha256": XML_SHA,
            "artifact_format": "application/xml (JATS)",
            "licence": "CC BY 4.0",
            "source_locator": "Article body, appendices and float captions",
            "limitations": [
                "Every table is a graphic in this XML, so no table cell can be read from it; it was used for the "
                "article text, the captions and the metadata only.",
                "Downloaded twice on 2026-11-15 with identical bytes.",
            ],
            "review": review(
                methods=["source-hash-verification", "automated-source-review"],
                note="Fetched twice with identical bytes. The body text was compared with the PDF text layer for the "
                     "passages quoted in this batch.",
                artifact=XML_SHA, url=XML_URL,
            ),
        },
        links=[{"relation": "companion_of", "target_id": S_PAPER}],
        sources=[S_JATS],
    ))
    recs.append(record(
        S_ZEN101, "source",
        "POISK dataset version 1.0.1 on Zenodo (record 19883049)",
        "The Zenodo record for POISK version 1.0.1, the dataset release the manuscript links and the one the six "
        "models' folding predictions were run against.",
        {
            "url": "https://zenodo.org/records/19883049",
            "artifact_url": "https://zenodo.org/api/records/19883049",
            "version": "1.0.1, published 29 April 2026",
            "retrieved_at": "2026-11-15T23:36:08Z",
            "doi": "10.5281/zenodo.19883049",
            "publication_status": "official_project_source",
            "artifact_sha256": ZEN_V101_SHA,
            "artifact_format": "application/json (Zenodo REST record)",
            "licence": "CC BY 4.0, as declared in the record metadata (license id cc-by-4.0)",
            "source_locator": "Record metadata and description",
            "limitations": [
                "Mutable record: the API reported revision 6, created 2026-04-29 and last updated 2026-11-03. The "
                "hash describes one retrieval of the metadata record.",
                "The 234 MB and 124 MB data files were not downloaded, so no data file is hashed here; the row and "
                "patent counts come from the manuscript and from the record descriptions.",
                "The record states no position on the patent rights in the filings the data is extracted from.",
            ],
            "review": review(
                methods=["source-hash-verification", "automated-source-review"],
                note="Retrieved from the Zenodo REST API on 2026-11-15; the declared licence, version, publication "
                     "date and file list were read from that response.",
                artifact=ZEN_V101_SHA, url="https://zenodo.org/api/records/19883049",
            ),
        },
        links=[{"relation": "companion_of", "target_id": S_PAPER}],
        sources=[S_ZEN101],
    ))
    recs.append(record(
        S_ZEN11, "source",
        "POISK dataset version 1.1 on Zenodo (record 21775623)",
        "The Zenodo record for POISK version 1.1, which corrects version 1.0.1, adds the six models' folding "
        "structures and metrics, and states which dataset version those predictions were run against.",
        {
            "url": "https://zenodo.org/records/21775623",
            "artifact_url": "https://zenodo.org/api/records/21775623",
            "version": "1.1, published 23 October 2026",
            "retrieved_at": "2026-11-15T23:36:08Z",
            "doi": "10.5281/zenodo.21775623",
            "publication_status": "official_project_source",
            "artifact_sha256": ZEN_V11_SHA,
            "artifact_format": "application/json (Zenodo REST record)",
            "licence": "CC BY 4.0, as declared in the record metadata (license id cc-by-4.0)",
            "source_locator": "Record metadata, description sections 'Dataset Structure and Documentation', 'Quality Control and Algorithmic Audit' and 'Relationship to the folding predictions', and the file list",
            "limitations": [
                "Mutable record: the API reported revision 4, created and last updated 2026-10-24. The hash "
                "describes one retrieval of the metadata record.",
                "The 18 data and artifact files, which total tens of gigabytes, were not downloaded, so none is "
                "hashed here; only the Zenodo file list with its md5 digests was read.",
                "The record states no position on the patent rights in the filings the data is extracted from.",
            ],
            "review": review(
                methods=["source-hash-verification", "automated-source-review"],
                note="Retrieved from the Zenodo REST API on 2026-11-15; the row count, column count, audit tiers, "
                     "folding-version statement and chain-pair warning were read from that response.",
                artifact=ZEN_V11_SHA, url="https://zenodo.org/api/records/21775623",
            ),
        },
        links=[{"relation": "companion_of", "target_id": S_PAPER}],
        sources=[S_ZEN11],
    ))
    recs.append(record(
        S_EXPLORER, "source",
        "POISK Explorer project site",
        "The project's search site for POISK records, which carries the project's own description of the dataset and "
        "its publication status.",
        {
            "url": "https://poisk-explorer.github.io/",
            "version": "Site as served on 2026-11-15",
            "retrieved_at": "2026-11-15T23:36:33Z",
            "publication_status": "official_project_source",
            "artifact_sha256": EXPLORER_SHA,
            "artifact_format": "text/html",
            "source_locator": "Landing page header and the 'A guide to POISK' panel",
            "limitations": [
                "Mutable site; the hash describes one retrieval.",
                "The record and patent counts are filled in by client-side JavaScript, so the served HTML shows "
                "placeholders and no count could be read from it.",
            ],
            "missing_metadata": {"licence": {"reason": "unreported", "note": "The served page states no licence."}},
            "review": review(
                methods=["source-hash-verification", "automated-source-review"],
                note="Retrieved once on 2026-11-15. Only text present in the served HTML was used.",
                artifact=EXPLORER_SHA, url="https://poisk-explorer.github.io/",
            ),
        },
        links=[{"relation": "companion_of", "target_id": S_PAPER}],
        sources=[S_EXPLORER],
    ))

    # ---------------- models ----------------
    for rid, name, reported, description in NEW_MODELS:
        recs.append(record(
            rid, "model", name, description,
            {
                "entity_level": "family",
                "reported_name": reported,
                "provenance_note": (
                    f"The preprint names this engine only as \"{reported}\" among the six folding models it "
                    "evaluates. No release tag, commit, weights hash or parameter count is printed, so the record "
                    "stays at family level and the evaluated setup is on the configuration record."
                ),
                "source_locator": "Section 2.3 'Folding and structural scoring'; Table 1 row labels",
                "missing_metadata": {
                    "version": {"reason": "inapplicable", "note": "Family record; the evaluated release is named on the configuration."},
                    "checkpoint_revision": {"reason": "unreported", "note": "No checkpoint, commit or weights hash is printed for any of the six engines."},
                    "training_data": {"reason": "unreported", "note": "The Discussion states that several evaluated models disclose limited detail on their training data."},
                    "licence": {"reason": "unreported", "note": "No model licence or terms are printed."},
                    "access": {"reason": "unreported", "note": "The NeurIPS checklist states only that all six evaluated models are publicly available or accessible."},
                },
                "review": review(methods=["pdf-text-parse", "source-hash-verification"]),
            },
            facets=dict(FACETS_MODEL),
        ))

    recs.append(record(
        METHOD_CONSENSUS, "method", "Cross-model structural consensus binder ranking",
        "Calls the candidate in an antibody pair whose predicted pose is reproduced by more folding models, above a "
        "DockQ threshold, the binder.",
        {
            "entity_level": "method",
            "reported_name": "structural consensus",
            "provenance_note": (
                "Defined in Section 3.3.1 as a signal independent of any single engine's confidence head. It has no "
                "implementation of its own beyond DockQ comparisons between the six engines' predicted poses."
            ),
            "source_locator": "Section 3.3.1 'Predicting binding with structural prediction consensus'",
            "parameters": "Two parameters: the number of agreeing models k and the DockQ threshold at which two poses count as agreeing",
            "missing_metadata": {
                "version": {"reason": "inapplicable", "note": "An analysis defined in the paper, not a released tool."},
            },
            "review": review(methods=["pdf-text-parse", "source-hash-verification"]),
        },
        facets=dict(FACETS),
    ))

    # ---------------- configurations ----------------
    for key, printed, _, model_id in ENGINES:
        recs.append(record(
            CONFIG[key], "configuration", f"{printed} with full-Fv ipSAE ranking", CONFIG_DESC[key],
            {
                "configuration_type": "paper_evaluation",
                "reported_name": printed,
                "version": f"Printed only as \"{printed}\"",
                "parameters": (
                    "ColabFold multiple sequence alignments, no templates, five predictions per complex "
                    f"({SAMPLING[key]}), highest-confidence prediction retained for scoring"
                ),
                "selection": "The highest confidence prediction of the five was selected for further analysis",
                "foundation_model_eligible": True,
                "score_training_overlap": (
                    "Antibodies sharing 95% or more sequence identity with any antibody in SAbDab were excluded from "
                    "the benchmark, and Appendix J reports a temporal and a training-cutoff split analysis. The "
                    "Discussion states that incomplete training-data disclosure prevents fully excluding overlap."
                ),
                "provenance_note": (
                    f"The folding setup the preprint describes for {printed}. The engine is identified by its printed "
                    "name only: no checkpoint, commit, container or weights hash is given."
                ),
                "source_locator": "Section 2.3 'Folding and structural scoring'; Table 1 row \"" + printed + "\"",
                "missing_metadata": {
                    "checkpoint": {"reason": "unreported", "note": "No checkpoint name, release tag or weights hash is printed."},
                    "checkpoint_revision": {"reason": "unreported", "note": "No commit or revision is printed."},
                    "hyperparameters": {"reason": "unreported", "note": "Beyond ColabFold MSAs, no templates, five predictions and top-confidence selection, no sampling settings are printed."},
                    "code": {"reason": "unavailable", "note": "No benchmark code repository is offered in the preprint; only the ipSAE tool URL is given."},
                },
                "review": review(methods=["pdf-text-parse", "source-hash-verification"]),
            },
            links=[{"relation": "configuration_of", "target_id": model_id}],
            facets=dict(FACETS_MODEL),
        ))

    for rid, name, setting, description in CONSENSUS_CONFIGS:
        recs.append(record(
            rid, "configuration", name, description,
            {
                "configuration_type": "paper_evaluation",
                "reported_name": setting,
                "version": f"Consensus requirement {setting}",
                "parameters": f"Agreement requirement {setting}, with DockQ computed on the Fv-antigen interface of each engine's top-ranked structure",
                "provenance_note": (
                    "A consensus setting the preprint reports in Section 3.3.1. It combines the predicted poses of "
                    "the six engines and has no checkpoint of its own."
                ),
                "source_locator": "Section 3.3.1; Figure 7",
                "missing_metadata": {
                    "code": {"reason": "unavailable", "note": "No implementation of the consensus analysis is offered for download."},
                },
                "review": review(methods=["pdf-text-parse", "source-hash-verification"]),
            },
            links=[{"relation": "configuration_of", "target_id": METHOD_CONSENSUS}]
            + [{"relation": "uses_model", "target_id": m} for m in sorted({m for *_, m in ENGINES})],
            facets=dict(FACETS_MODEL),
        ))

    # ---------------- datasets ----------------
    recs.append(record(
        D_V101, "dataset", "POISK patent-derived antibody dataset, version 1.0.1",
        "Antibody heavy and light chain sequences, target sequences and functional metadata extracted from US "
        "patent filings by an LLM pipeline, released as a flat table with per-record audit fields.",
        {
            "version": "1.0.1",
            "reported_name": "POISK: Patent-extracted Organization of Immunoglobulin Sequence Knowledge",
            "total": 89074,
            "split": "No train, validation or test split; a single release table",
            "assay": "None. Records are extracted from patent text; affinities and epitopes are whatever the filing reports",
            "species": "Antibodies from mouse-derived, humanized and other sources; the co-folding benchmark keeps human-targeting records only",
            "accession": "10.5281/zenodo.19883049",
            "archive_doi": "10.5281/zenodo.19883049",
            "repository": "https://zenodo.org/records/19883049",
            "access": "Public download from Zenodo. The data files themselves were not downloaded for this batch, so none is hashed here.",
            "reuse_restrictions": (
                "The Zenodo record declares CC BY 4.0 for the dataset. Neither Zenodo record nor the preprint states "
                "any position on the patent rights in the filings the records are extracted from, and the licence on "
                "the compilation is not a licence to the patented antibodies. The record advises verifying critical "
                "sequences or affinities against the original patents before experimental work."
            ),
            "label_semantics": (
                "A record asserts that a patent provides explicit evidence that the antibody binds the named target. "
                "It is not a measured affinity unless the record carries one, and it is not a structure."
            ),
            "scope_note": (
                "89,074 records describing 78,174 unique antibodies from 10,110 US patents, spanning over 2,000 "
                "unique target sequences. This is the version the manuscript links and the version the six models' "
                "folding predictions were run against."
            ),
            "source_locator": "Section 2.1 'Data extraction'; Section 3.1 'Dataset'; Zenodo record 19883049 metadata",
            "missing_metadata": {
                "denominator": {"reason": "unreported", "note": "The Zenodo 1.0.1 record description states no row count; 89,074 is the manuscript's extracted-record count."},
            },
            "review": review(
                methods=["pdf-text-parse", "automated-source-review", "source-hash-verification"],
                note="Counts from the preprint; licence, version, publication date and file list from the pinned "
                     "Zenodo API response for record 19883049.",
            ),
        },
        sources=[S_PAPER, S_ZEN101],
    ))
    recs.append(record(
        D_V11, "dataset", "POISK patent-derived antibody dataset, version 1.1",
        "The current POISK release: a flat table of patent-extracted antibody and target sequences with audit "
        "fields, published together with the six folding models' predicted structures and per-complex metrics.",
        {
            "version": "1.1",
            "reported_name": "POISK: Patent-extracted Organization of Immunoglobulin Sequence Knowledge",
            "total": 93193,
            "split": "No train, validation or test split; a single release table",
            "assay": "None. Records are extracted from patent text",
            "accession": "10.5281/zenodo.21775623",
            "archive_doi": "10.5281/zenodo.21775623",
            "repository": "https://zenodo.org/records/21775623",
            "access": "Public download from Zenodo; 18 files, including per-engine structure archives and PAE arrays. No file was downloaded for this batch.",
            "reuse_restrictions": (
                "The Zenodo record declares CC BY 4.0 for the dataset. It states no position on the patent rights in "
                "the underlying filings, and the licence on the compilation is not a licence to the patented "
                "antibodies."
            ),
            "scope_note": (
                "93,193 rows and 47 columns, each row carrying a distinct unique_record_id. The record states that "
                "version 1.1 corrects errors found in version 1.0.1 and adds the folding data for the paper's "
                "benchmark, and that those folding predictions were run against version 1.0.1 rather than against "
                "this release. The 93,193 rows are therefore not the manuscript's 89,074 extracted records and not "
                "the benchmark's 22,494 complexes."
            ),
            "source_locator": "Zenodo record 21775623, description sections 'Dataset Structure and Documentation' and 'Relationship to the folding predictions'",
            "missing_metadata": {
                "label_semantics": {"reason": "unextracted", "note": "The 47-column schema file poisk_dataset_column_description.csv was not downloaded."},
            },
            "review": review(
                methods=["automated-source-review", "source-hash-verification"],
                note="Read from the pinned Zenodo API response for record 21775623. The data files were not downloaded.",
                artifact=ZEN_V11_SHA, url="https://zenodo.org/api/records/21775623",
            ),
        },
        links=[{"relation": "same_data_as", "target_id": D_V101}],
        sources=[S_ZEN11],
    ))

    recs.append(record(
        SUB_BENCH, "dataset_subset", "POISK co-folding binder-decoy benchmark set (22,494 complexes)",
        "The balanced benchmark the paper folds: 11,247 patent-supported antibody-antigen pairs with no known "
        "resolved structure, each paired with a putative non-binding antibody against the same antigen.",
        {
            "version": "As described in bioRxiv v1 Section 2.2; folded against POISK dataset version 1.0.1",
            "split": "Evaluation only; all 22,494 complexes are scored and none is held out",
            "source_dataset": D_V101,
            "positive_count": 11247,
            "test_count": 22494,
            "subset_scope": (
                "Records with a novel, human-targeting antibody and an explicit antigen sequence, with conditional "
                "(for example pH-dependent) binding excluded, antigen length between 50 and 750 residues, duplicates "
                "removed, and antibodies sharing 95% or more sequence identity with any SAbDab antibody excluded by "
                "Diamond BLASTP. Each of the 11,247 remaining binders is paired with one putative non-binder for the "
                "same antigen."
            ),
            "limitations": [
                "The 11,247 negatives are putative: 7,647 are nearest-CDR matches retrieved from the Observed "
                "Antibody Space and 3,600 are germline-reverted with randomised CDR-H3. The paper states they have "
                "not been experimentally validated for lack of binding.",
                "Excluding antibodies close to SAbDab reduces but does not establish absence from the models' "
                "training data; the Discussion says incomplete training-data disclosure prevents fully excluding "
                "overlap.",
                "Binder labels rest on an LLM extraction from patent text, audited on a 40-record manual sample.",
            ],
            "source_locator": "Section 2.2 'Co-folding benchmark data preparation'; Appendix D.1",
            "review": review(methods=["pdf-text-parse", "source-hash-verification"]),
        },
        links=[
            {"relation": "same_data_as", "target_id": D_V101},
            {"relation": "used_in", "target_id": BENCH},
        ],
    ))
    recs.append(record(
        SUB_SCREEN, "dataset_subset", "POISK 1-in-50 screening targets (27 antigen constructs)",
        "The 27 antigen constructs with at least 75 patent-derived binders each, used to build one-binder-in-fifty "
        "candidate pools for the screening simulation.",
        {
            "version": "As described in bioRxiv v1 Section 3.2.3",
            "split": "Evaluation only",
            "source_dataset": SUB_BENCH,
            "independent_groups": 27,
            "test_count": 540,
            "subset_scope": (
                "27 targets from the benchmark that possessed at least 75 patent-derived binders. Each trial draws "
                "one binder and 49 putative non-binders for the same antigen; 20 trials per target give 540 "
                "discovery trials, repeated under 25 scenario-generation seeds."
            ),
            "limitations": [
                "Distinct constructs can share a UniProt accession, so 27 constructs are fewer than 27 distinct "
                "proteins: Q02223 and P18627 each appear twice in Table 8.",
                "Restricted to targets with many patent-derived binders, which is not a random sample of screening "
                "problems.",
            ],
            "source_locator": "Section 3.2.3 '1-in-50 zero-shot screening simulation'; Table 8 columns '#' and 'UniProt'",
            "review": review(methods=["pdf-text-parse", "source-hash-verification"]),
        },
        links=[
            {"relation": "same_data_as", "target_id": SUB_BENCH},
            {"relation": "used_in", "target_id": BENCH},
        ],
    ))
    recs.append(record(
        SUB_EPITOPE, "dataset_subset", "POISK binder records with mappable patent epitope annotations (1,232)",
        "The benchmark binder records whose patent-reported epitope residues could be mapped onto the folded antigen "
        "construct, used to test where the models place the antibody.",
        {
            "version": "As described in bioRxiv v1 Section 3.3.2",
            "split": "Evaluation only",
            "source_dataset": SUB_BENCH,
            "test_count": 1232,
            "subset_scope": (
                "The 1,232 binder records of the benchmark carrying residue-level epitope annotations (a linear range "
                "or explicit contact residues) that could be mapped to the folded antigen construct."
            ),
            "limitations": [
                "The reference epitope is a patent text annotation, not an experimentally resolved interface.",
            ],
            "source_locator": "Section 3.3.2; Appendix C Table 5 row '+ residue-level epitope (linear range or explicit contact residues)'",
            "review": review(methods=["pdf-text-parse", "source-hash-verification"]),
        },
        links=[
            {"relation": "same_data_as", "target_id": SUB_BENCH},
            {"relation": "used_in", "target_id": BENCH},
        ],
    ))

    # ---------------- task and benchmark ----------------
    recs.append(record(
        TASK, "task", "Discriminating antibody binders from sequence-similar putative non-binders",
        "Given an antibody heavy and light chain and a target sequence, decide which candidate antibodies bind the "
        "target, scored by how the method ranks a patent-supported binder against sequence-similar candidates.",
        {
            "task": "Antibody binder screening by ranking candidate sequences against a chosen antigen",
            "metric": "paired-accuracy",
            "metric_direction": "higher",
            "metric_qualifier": "binder ranked above a sequence-similar putative non-binder for the same antigen",
            "scope_note": (
                "The decision the task stands in for is which antibody candidates to test for binding to a chosen "
                "antigen. Methods are scored on ranking only; no record on this task asserts a measured binding "
                "affinity."
            ),
            "source_locator": "Section 1 'Introduction'; Section 2.2",
            "version": "As defined in bioRxiv v1",
        },
    ))
    recs.append(record(
        BENCH, "benchmark", "POISK co-folding binder-versus-decoy benchmark",
        "Scores structure prediction models as zero-shot binder classifiers on 22,494 antibody-antigen complexes "
        "drawn from patent filings, by how their interface confidence ranks patent-supported binders against "
        "putative non-binders for the same antigen.",
        {
            "entity_level": "suite",
            "version": "bioRxiv v1, 26 October 2026; folds run against POISK dataset version 1.0.1",
            "task": "Ranking candidate antibody sequences for binding to a chosen antigen using folding-model interface confidence",
            "split": "Evaluation only; 11,247 binder and putative non-binder pairs, all scored",
            "executable_suite": False,
            "scope_note": (
                "Three distinct counts belong to three different things and must not be substituted for one another: "
                "89,074 records is what the extraction pipeline produced for POISK version 1.0.1, 22,494 complexes "
                "(11,247 pairs) is this benchmark, and 93,193 rows is the current Zenodo version 1.1 table. The "
                "benchmark's endpoints are ranking endpoints: ipSAE and ipTM are structural confidence scores, and "
                "no result here is a measured binding or affinity value."
            ),
            "limitations": [
                "The negatives are putative. 7,647 of the 11,247 are nearest-CDR matches from the Observed Antibody "
                "Space and 3,600 are germline-reverted with randomised CDR-H3 at 85% or more total identity; the "
                "paper states they have not been experimentally validated for lack of binding.",
                "Binder labels come from an LLM extraction of patent text, audited by the same model and then on a "
                "40-record manual sample.",
                "Excluding antibodies within 95% identity of SAbDab reduces but does not establish absence from any "
                "model's training data; the Discussion says incomplete training-data disclosure prevents fully "
                "excluding overlap.",
                "Discrimination does not establish where the antibody binds: the best engine contacts an annotated "
                "epitope residue in 62.8% of the 1,232 annotated records.",
                "Neither the benchmark code nor a split manifest is offered for download; only the dataset, the "
                "folding artifacts and the ipSAE tool URL are.",
                "Author-reported throughout, retrospective, and not reproduced by Rewire.",
            ],
            "source_locator": "Sections 2.2, 2.3, 3.2 and 3.3; Appendices C, D, F and H",
            "missing_metadata": {
                "split_manifest": {"reason": "unavailable", "note": "No per-pair split manifest is published; the Zenodo release holds the dataset table and the folding artifacts, not the pair list."},
                "runner": {"reason": "unavailable", "note": "No benchmark harness or evaluation code is offered for download."},
            },
            "review": review(methods=["pdf-text-parse", "source-hash-verification"]),
        },
        links=[
            {"relation": "evaluates_task", "target_id": TASK},
            {"relation": "uses_data", "target_id": SUB_BENCH},
        ],
        sources=[S_PAPER, S_ZEN11],
    ))

    # ---------------- protocols ----------------
    for key, spec in PROTOCOLS.items():
        attrs = {
            "metric": spec["metric"],
            "metric_direction": spec["direction"],
            "metric_qualifier": spec["qualifier"],
            "unit": spec["unit"],
            "version": "bioRxiv v1, 26 October 2026",
            "task": "Ranking candidate antibody sequences for binding to a chosen antigen using folding-model interface confidence",
            "metric_implementation": IPSAE_NOTE if key != "cohens-d-iptm" else
                "ipTM, the interface predicted template modelling score of the top-ranked structure; a confidence "
                "score, not a measured binding value.",
            "review": review(methods=["pdf-text-parse", "source-hash-verification"]),
        }
        if spec["definition"]:
            attrs["metric_definition"] = spec["definition"]
        if spec["denominator"]:
            attrs["denominator"] = spec["denominator"]
        if spec["limitations"]:
            attrs["limitations"] = spec["limitations"]
        if key.startswith("pairwise-coverage"):
            attrs["selection"] = (
                f"Pairs ranked by the higher of their two ipSAE scores; the top {spec['coverage_share']} retained. "
                "Exact ties receive half credit."
            )
            attrs["aggregation"] = "Mean over the retained pairs, ties at half credit"
            attrs["source_locator"] = "Appendix F; Table 7 column \"" + spec["coverage_share"] + "\""
        elif key.startswith("screen-1in50"):
            attrs["selection"] = (
                "27 targets with at least 75 patent-derived binders; each trial draws one binder and 49 putative "
                "non-binders for the same antigen"
            )
            attrs["aggregation"] = (
                "Mean over 27 targets of the per-target mean over 20 trials, averaged over 25 scenario-generation seeds"
            )
            attrs["random_seeds"] = "25 independent scenario-generation seeds"
            attrs["replicates"] = "20 trials per target per seed, 540 discovery trials in total"
            attrs["uncertainty_reporting"] = {
                "type": "standard_deviation",
                "n": 25,
                "scope": SCREEN_SEED_SCOPE,
                "note": (
                    "\"Bars show mean top-1, top-5, and top-10 accuracy (by ipSAE ranking) over 25 independent runs "
                    "with different random seeds; error bars indicate +/-2 sigma (sample standard deviation across "
                    "runs)\" (Figure 5 caption, quoted with the symbols spelled out). These are not confidence "
                    "intervals. Table 8 additionally prints a standard deviation across targets, which is a "
                    "different quantity on a different axis."
                ),
            }
            attrs["control"] = "Random selection of one candidate in fifty, a 2% baseline stated by the paper"
            attrs["source_locator"] = "Section 3.2.3; Figure 5 caption; Table 8 summary rows"
            attrs["scope_limitations"] = (
                "Top-1 and top-10 retrieval are different endpoints from pairwise accuracy and rest on a different "
                "denominator (540 trials over 27 targets, not 11,247 pairs). They are never pooled."
            )
        elif key == "epitope-recovery":
            attrs["selection"] = "The 1,232 benchmark binder records with residue-level patent epitope annotations mappable to the folded construct"
            attrs["aggregation"] = "Share of records recovered, over 1,232"
            attrs["success_threshold"] = {"criterion": "at least one annotated epitope residue with a heavy atom within 4 angstrom of an antibody heavy atom"}
            attrs["source_locator"] = "Section 3.3.2; Table 2"
        elif key.startswith("consensus"):
            attrs["selection"] = "Pairs where the stated number of models agree on a pose above the stated DockQ threshold"
            attrs["aggregation"] = "Share of eligible pairs classified correctly; coverage reported separately"
            attrs["source_locator"] = "Section 3.3.1; Figure 7"
        elif key.startswith("cohens-d"):
            attrs["aggregation"] = "Standardised mean difference between the binder and decoy score distributions"
            attrs["source_locator"] = "Section 3.2.1; Table 1 columns \"Cohen's d\""
        elif key == "pairwise-tie-fraction":
            attrs["source_locator"] = "Appendix F; Table 7 column \"Ties\""
        recs.append(record(
            PROTOCOL_ID[key], "protocol", spec["name"], spec["description"], attrs,
            links=[
                {"relation": "part_of", "target_id": BENCH},
                {"relation": "uses_data", "target_id": spec["data"]},
                {"relation": "evaluates_task", "target_id": TASK},
            ],
        ))

    # ---------------- evaluations and results ----------------
    def add_pair(key, protocol_key, data, eval_locator, extra_eval=None):
        eid = f"{B}-eval-{key}-{protocol_key}"
        recs.append(evaluation(
            eid, f"{PRINTED.get(key, key)} on {PROTOCOLS[protocol_key]['name']}",
            CONFIG.get(key, key), protocol_key, data, eval_locator, extra=extra_eval,
        ))
        return eid

    for key, printed, *_ in ENGINES:
        # Table 1, Cohen's d ipTM and ipSAE
        for protocol_key, field, column in [
            ("cohens-d-iptm", "cohens_d_iptm", "ipTM"),
            ("cohens-d-ipsae", "cohens_d_ipsae", "ipSAE"),
        ]:
            loc = f"Table 1, row \"{printed}\", column \"Cohen’s d\", sub-column \"{column}\""
            eid = add_pair(key, protocol_key, SUB_BENCH, loc)
            value = t1[key][field]
            recs.append(result(
                f"{B}-result-{key}-{protocol_key}", f"{printed}, {PROTOCOLS[protocol_key]['name']}",
                eid, protocol_key, value, value, loc,
                extra={"missing_metadata": {"uncertainty": {"reason": "unreported", "note": "Table 1 prints no spread for Cohen's d; the paper says the pairwise benchmarks run on the full set of pairs without random sampling."}}},
            ))

        # Table 7, tie fraction and the five coverage levels
        loc = f"Table 7, row \"{printed}\", column \"Ties\""
        eid = add_pair(key, "pairwise-tie-fraction", SUB_BENCH, loc)
        value = t7[key]["ties"]
        recs.append(result(
            f"{B}-result-{key}-pairwise-tie-fraction", f"{printed}, pairs left undecidable by identical ipSAE",
            eid, "pairwise-tie-fraction", value, value.rstrip("%"), loc,
            extra={"missing_metadata": {"uncertainty": {"reason": "inapplicable", "note": "A count over all 11,247 pairs, not an estimate from a sample."}}},
        ))

        for share, field in [("100", "c100"), ("75", "c75"), ("50", "c50"), ("25", "c25"), ("10", "c10")]:
            protocol_key = f"pairwise-coverage-{share}"
            loc = COVERAGE_LOCATOR[share].format(row=printed)
            eid = add_pair(key, protocol_key, SUB_BENCH, loc)
            value = t7[key][field]
            recs.append(result(
                f"{B}-result-{key}-{protocol_key}-t7", f"{printed}, pairwise accuracy at {share}% coverage",
                eid, protocol_key, value, value, loc,
                extra={"missing_metadata": {"uncertainty": {"reason": "unreported", "note": "Table 7 prints no spread; the paper says the pairwise benchmarks operate on the full set of 11,247 pairs without random sampling, so error bars do not apply."}}},
            ))
            if share == "50":
                loc1 = f"Table 1, row \"{printed}\", column \"Accuracy at\", sub-column \"50% Pairs\""
                recs.append(result(
                    f"{B}-result-{key}-{protocol_key}-t1", f"{printed}, pairwise accuracy at the dataset midpoint",
                    eid, protocol_key, t1[key]["accuracy_50"], t1[key]["accuracy_50"], loc1,
                    extra={
                        "rounding_note": (
                            f"Table 1 prints this endpoint to two decimals as {t1[key]['accuracy_50']}; Table 7 prints "
                            f"the same quantity to three decimals as {t7[key]['c50']}. Both printings are kept, each "
                            "with its own locator."
                        ),
                        "missing_metadata": {"uncertainty": {"reason": "unreported", "note": "Table 1 prints no spread for this column."}},
                    },
                ))

        # Table 2, epitope recovery
        loc = f"Table 2, row \"{printed}\", column \"Epitope Recovery Records (%)\""
        eid = add_pair(key, "epitope-recovery", SUB_EPITOPE, loc)
        value = t2[key]
        recs.append(result(
            f"{B}-result-{key}-epitope-recovery", f"{printed}, epitope contact recovery",
            eid, "epitope-recovery", value, value, loc,
            extra={
                "coverage": {"scored": 1232, "eligible": 1232, "unit": "binder records with mappable patent epitope annotations"},
                "missing_metadata": {"uncertainty": {"reason": "unreported", "note": "Table 2 prints a single percentage per engine with no spread."}},
            },
        ))

        # 1-in-50 top-1: Table 8 summary row and the Table 1 column
        loc8 = f"Table 8, row \"Mean over targets\", column \"{T8COL[key]}\""
        eid = add_pair(key, "screen-1in50-top1", SUB_SCREEN, loc8, extra_eval={
            "n_runs": 25,
            "seeds": "25 independent scenario-generation seeds",
            "total_targets": 27,
            "repeat_count": "20 trials per target per seed; 540 discovery trials",
            "coverage": {"scored": 540, "eligible": 540, "unit": "discovery trials per seed", "repeats": 25},
            "uncertainty": {
                "type": "standard_deviation",
                "value": t8["sd_seeds"][key],
                "printed": t8["sd_seeds"][key],
                "unit": "percentage points",
                "n": 25,
                "scope": SCREEN_SEED_SCOPE,
                "source_column": "Table 8 summary row \"SD across seeds (pp)\"",
            },
        })
        recs.append(result(
            f"{B}-result-{key}-screen-1in50-top1-t8", f"{printed}, 1-in-50 top-1 retrieval, mean over 27 targets",
            eid, "screen-1in50-top1", t8["mean"][key], t8["mean"][key], loc8,
            extra={
                "coverage": {"scored": 540, "eligible": 540, "unit": "discovery trials per seed", "repeats": 25},
                "uncertainty": {
                    "type": "standard_deviation",
                    "value": t8["sd_seeds"][key],
                    "printed": t8["sd_seeds"][key],
                    "unit": "percentage points",
                    "n": 25,
                    "scope": SCREEN_SEED_SCOPE,
                    "source_column": "Table 8 summary row \"SD across seeds (pp)\"",
                    "note": (
                        "Table 8 also prints a standard deviation across targets for this engine "
                        f"({t8['sd_targets'][key]} percentage points), which measures between-target spread rather "
                        "than run-to-run spread and is kept as a separate claim record."
                    ),
                },
                "replicates_or_seeds": "25 scenario-generation seeds, 20 trials per target per seed",
                "scope_note": (
                    "Mean over the 27 antigen constructs. Table 8's per-construct values range from 2.2% to 70.8% "
                    "for Protenix-v2, so this aggregate hides a wide spread of screening difficulty."
                ),
            },
        ))
        loc1 = f"Table 1, row \"{printed}\", column \"1-in-50\", sub-column \"Top-1 Acc.\""
        recs.append(result(
            f"{B}-result-{key}-screen-1in50-top1-t1", f"{printed}, 1-in-50 top-1 retrieval as printed in Table 1",
            eid, "screen-1in50-top1", t1[key]["top1"], t1[key]["top1"], loc1,
            unit="fraction",
            extra={
                "rounding_note": (
                    f"Table 1 prints this endpoint as the fraction {t1[key]['top1']}; Table 8's \"Mean over targets\" "
                    f"row prints the same quantity as {t8['mean'][key]} percent. Both printings are kept, each with "
                    "its own locator."
                ),
                "missing_metadata": {"uncertainty": {"reason": "unreported", "note": "Table 1 prints no spread for this column; the spread is in Table 8 and Figure 5."}},
            },
        ))

    # 1-in-50 top-10: only two engines have a printed value
    for key, value in [("protenix-v2", "54.7"), ("intellifold-v2", "56.0")]:
        printed = PRINTED[key]
        loc = (
            "Section 3.2.3, sentence beginning \"Protenix-v2 and IntelliFold v2 demonstrated comparable retrieval in "
            f"broader rankings\", value for {printed}"
        )
        eid = add_pair(key, "screen-1in50-top10", SUB_SCREEN, loc, extra_eval={
            "n_runs": 25,
            "seeds": "25 independent scenario-generation seeds",
            "total_targets": 27,
            "repeat_count": "20 trials per target per seed; 540 discovery trials",
        })
        recs.append(result(
            f"{B}-result-{key}-screen-1in50-top10", f"{printed}, 1-in-50 top-10 retrieval",
            eid, "screen-1in50-top10", f"{value}%", value, loc,
            extra={
                "missing_metadata": {"uncertainty": {"reason": "unextracted", "note": "The spread for top-10 retrieval is shown only as a Figure 5 error bar with no printed number."}},
                "scope_note": "Printed in prose. Figure 5 plots top-1, top-5 and top-10 for all six engines, but prints no numbers for the other values.",
            },
        ))

    # cross-model structural consensus
    CONSENSUS = [
        (
            f"{B}-config-consensus-k3-dockq-0-23", "k3-dockq-0-23", "73.1", "54.2",
            "Section 3.3.1, sentence beginning \"When at least three models agree on a pose at a DockQ threshold of 0.23\"",
            "at least three models agreeing at DockQ 0.23 or better",
        ),
        (
            f"{B}-config-consensus-k3-dockq-0-80", "k3-dockq-0-80", "96.8", "3.0",
            "Section 3.3.1, sentence beginning \"For instance, at k ≥ 3 and DockQ ≥ 0.80\"",
            "at least three models agreeing at DockQ 0.80 or better",
        ),
    ]
    for config_id, slug, accuracy, coverage_share, locator, setting in CONSENSUS:
        eid = f"{B}-eval-consensus-{slug}-accuracy"
        recs.append(evaluation(
            eid, f"Cross-model structural consensus ({setting}) on POISK pairwise accuracy",
            config_id, "consensus-pairwise-accuracy", SUB_BENCH, locator,
        ))
        recs.append(result(
            f"{B}-result-consensus-{slug}-accuracy",
            f"Cross-model structural consensus ({setting}), pairwise accuracy",
            eid, "consensus-pairwise-accuracy", f"{accuracy}%", accuracy, locator,
            qualifier=(
                "binder identified as the pair member with more agreeing folding-model poses, "
                f"{setting}, over the pairs eligible at that threshold"
            ),
            extra={
                "coverage": {"note": f"Covers {coverage_share}% of the 11,247 pairs; the eligible pair count is not printed as an integer."},
                "scope_note": (
                    f"Accuracy on eligible pairs only. The same sentence states that {coverage_share}% of pairs are "
                    "eligible at this setting; that share is recorded as its own result."
                ),
                "missing_metadata": {"uncertainty": {"reason": "unreported", "note": "No spread is printed for the consensus accuracies."}},
            },
        ))
        eid2 = f"{B}-eval-consensus-{slug}-coverage"
        recs.append(evaluation(
            eid2, f"Cross-model structural consensus ({setting}) on POISK pair coverage",
            config_id, "consensus-pair-coverage", SUB_BENCH, locator,
        ))
        recs.append(result(
            f"{B}-result-consensus-{slug}-coverage",
            f"Cross-model structural consensus ({setting}), share of pairs eligible",
            eid2, "consensus-pair-coverage", f"{coverage_share}%", coverage_share, locator,
            qualifier=f"share of the 11,247 pairs eligible for classification with {setting}",
            extra={"missing_metadata": {"uncertainty": {"reason": "inapplicable", "note": "A share of the full pair set, not an estimate from a sample."}}},
        ))

    # ---------------- claims ----------------
    P = "Section"
    recs.append(claim(
        "extraction-pipeline", D_V101, "extraction_pipeline",
        "Antibody chains were collected from GenBank (heavy, lambda and kappa, 70 to 1000 amino acids) and "
        "classified with ANARCI, giving 10,110 eligible US patents. Antigen identification, chain pairing and 36 "
        "further fields were extracted from the patent text with the Google Generative AI Python library and the "
        "Gemini 3 Pro model, with Pydantic schemas. Missing antigen sequences were looked up in UniProt by target "
        "identity and organism. Gemini also acted as auditor: fields it flagged as not explicitly mentioned were "
        "excluded, and records flagged for incorrect chain pairing were removed.",
        f"{P} 2.1 'Data extraction'",
        rationale="The dataset's labels rest on this pipeline, so its steps and its self-audit are part of what a reader needs to judge the benchmark's labels.",
    ))
    recs.append(claim(
        "dataset-record-counts", D_V101, "record_counts",
        "The pipeline extracted 89,074 records describing 78,174 unique antibodies, from 10,110 eligible US "
        "patents. The 11,247 benchmark binders come from 1,546 distinct patents.",
        f"{P} 2.1; Appendix C",
    ))
    recs.append(claim(
        "dataset-composition", D_V101, "composition",
        "The collection spans over 2,000 unique target sequences, with 91.8% of records carrying explicit target "
        "metadata. Canonical monoclonal VH/VL antibodies are 85.6% of entries, bispecific 7.4% and single-domain "
        "VHH 3.9%.",
        f"{P} 3.1 'Dataset'",
    ))
    recs.append(claim(
        "andd-overlap", D_V101, "overlap_with_other_resources",
        "A comparison with the Antibody and Nanobody Design Dataset found only 716 shared antibody-antigen entries.",
        f"{P} 3.1",
    ))
    recs.append(claim(
        "manual-audit", D_V101, "manual_audit",
        "A manual audit of 40 records against their source patents found 19 of 20 benchmark records (95%) and 18 of "
        "20 records from the full dataset correct in every populated field, with 181 of 184 audited field instances "
        "correct. Two of the three errors were conservative omissions; the third was a human target labelled "
        "Humanized. No record in either sample asserted an antibody-antigen binding pair its patent does not "
        "support, which the authors say does not completely rule out their existence elsewhere.",
        f"{P} 2.1; Appendix B, Table 4",
        limitations=[
            "40 records out of 89,074. The authors report it as evidence that the pipeline's error modes are the "
            "expected ones, not as a tight estimate of dataset-wide precision.",
            "A single annotator, about six hours of work.",
        ],
    ))
    recs.append(claim(
        "audit-verdict-tiers-v1-0-1", D_V101, "audit_fields",
        "The version 1.0.1 record describes audit.verdict as \"A categorical reliability score (e.g., CONTRADICTED, "
        "PLAUSIBLE, CONFIRMED)\", with audit.flags naming fields with potential mismatches and audit.reasoning "
        "explaining the extracted value.",
        "Zenodo record 19883049, description section 'Quality Control and Algorithmic Audit'",
        name="POISK: audit fields in dataset version 1.0.1",
        sources=[S_ZEN101], methods=["automated-source-review", "source-hash-verification"],
        artifact=ZEN_V101_SHA, url="https://zenodo.org/api/records/19883049",
        limitations=["The version 1.1 record describes a different three-tier scheme (CONFIRMED, PLAUSIBLE, REVIEW)."],
    ))
    recs.append(claim(
        "dataset-licence-v1-0-1", D_V101, "licence_and_patent_rights",
        "Zenodo declares CC BY 4.0 for POISK version 1.0.1. Neither the record nor the manuscript states any "
        "position on the patent rights in the filings the records are extracted from. The record advises users to "
        "verify critical sequences or affinity data against the original patent documents, reachable through the "
        "patent_id column, before starting downstream experimental validation.",
        "Zenodo record 19883049, metadata field 'license' and description section 'Usage and Limitations'",
        name="POISK: licence and patent rights, dataset version 1.0.1",
        sources=[S_ZEN101], methods=["automated-source-review", "source-hash-verification"],
        artifact=ZEN_V101_SHA, url="https://zenodo.org/api/records/19883049",
        rationale="A licence on the compilation is not a licence to the antibodies the patents claim; recorded so that no reader infers freedom to operate from the dataset licence.",
    ))
    recs.append(claim(
        "v1-1-row-count", D_V11, "release_contents",
        "POISK version 1.1 holds 93,193 rows and 47 columns, each row carrying a distinct unique_record_id. The "
        "record states that version 1.1 corrects errors found in version 1.0.1 and adds folding data for the "
        "paper's benchmark.",
        "Zenodo record 21775623, description section 'Dataset Structure and Documentation'",
        sources=[S_ZEN11], methods=["automated-source-review", "source-hash-verification"],
        artifact=ZEN_V11_SHA, url="https://zenodo.org/api/records/21775623",
        limitations=[
            "93,193 is the current release's row count. It is neither the manuscript's 89,074 extracted records nor "
            "the benchmark's 22,494 complexes, and no result in this batch rests on it.",
        ],
    ))
    recs.append(claim(
        "v1-1-folding-version", D_V11, "folding_artifact_version",
        "The version 1.1 record states of the published folding metrics and structures: \"These predictions were run "
        "against dataset version 1.0.1, not against this release.\"",
        "Zenodo record 21775623, description section 'Relationship to the folding predictions'",
        sources=[S_ZEN11], methods=["automated-source-review", "source-hash-verification"],
        artifact=ZEN_V11_SHA, url="https://zenodo.org/api/records/21775623",
        rationale="The data version and the folding artifacts are pinned separately in this batch because the release that carries the artifacts is not the release they were computed from.",
    ))
    recs.append(claim(
        "v1-1-folding-metrics-files", D_V11, "folding_metrics_files",
        "poisk_all_models_folding_metrics.zip holds folding metrics including ipTM and ipSAE from the six "
        "benchmarked models: one CSV per model, 22,494 rows each, sharing 28 columns in different column orders. "
        "The same archive, with the same md5 digest, is attached to both the 1.0.1 and the 1.1 record.",
        "Zenodo records 19883049 and 21775623, file lists and description section 'Relationship to the folding predictions'",
        sources=[S_ZEN11, S_ZEN101], methods=["automated-source-review", "source-hash-verification"],
        artifact=ZEN_V11_SHA, url="https://zenodo.org/api/records/21775623",
    ))
    recs.append(claim(
        "v1-1-chain-pair-labels", D_V11, "score_column_provenance",
        "The version 1.1 record states that each ipSAE-style score ships beside a column naming the chain pair it "
        "was computed on (ipsae_chain_pair, cdr_ipsae_chain_pair and the *_ab_as_single_chain_label pair), and "
        "warns: \"Read that label before ranking on a score: a value whose pair is not antibody-against-antigen is "
        "not a binding metric.\"",
        "Zenodo record 21775623, description section 'Relationship to the folding predictions'",
        sources=[S_ZEN11], methods=["automated-source-review", "source-hash-verification"],
        artifact=ZEN_V11_SHA, url="https://zenodo.org/api/records/21775623",
        rationale="Anyone recomputing the paper's endpoints from the released metrics has to pick the right chain-pair column; the published scores are not interchangeable.",
    ))
    recs.append(claim(
        "v1-1-target-sequence-provenance", D_V11, "target_sequence_provenance",
        "In version 1.1 the target sequences carry their provenance: target.sequence is the sequence the release "
        "holds, target.sequence_from_patent what the patent's GenBank deposit holds, and target.sequence_from_uniprot "
        "what the named UniProt entry holds.",
        "Zenodo record 21775623, description section 'Dataset Structure and Documentation'",
        sources=[S_ZEN11], methods=["automated-source-review", "source-hash-verification"],
        artifact=ZEN_V11_SHA, url="https://zenodo.org/api/records/21775623",
    ))
    recs.append(claim(
        "v1-1-audit-verdicts", D_V11, "audit_fields",
        "In version 1.1 audit.verdict has three tiers: CONFIRMED, where every field was explicitly supported by the "
        "patent text; PLAUSIBLE, where nothing contradicted the record but support was partial, indirect or "
        "inferred; and REVIEW, where the record appeared incorrect or its correctness could not be established. The "
        "record states that REVIEW is not an assertion that a row is false.",
        "Zenodo record 21775623, description section 'Quality Control and Algorithmic Audit'",
        name="POISK: audit fields in dataset version 1.1",
        sources=[S_ZEN11], methods=["automated-source-review", "source-hash-verification"],
        artifact=ZEN_V11_SHA, url="https://zenodo.org/api/records/21775623",
        limitations=["The version 1.0.1 record describes the tiers differently, as CONTRADICTED, PLAUSIBLE and CONFIRMED."],
    ))
    recs.append(claim(
        "v1-1-licence", D_V11, "licence_and_patent_rights",
        "Zenodo declares CC BY 4.0 for POISK version 1.1. The record states no position on the patent rights in the "
        "underlying filings, and repeats that users should verify critical sequences or affinity data against the "
        "original patent documents before downstream experimental validation.",
        "Zenodo record 21775623, metadata field 'license' and description section 'Usage and Limitations'",
        name="POISK: licence and patent rights, dataset version 1.1",
        sources=[S_ZEN11], methods=["automated-source-review", "source-hash-verification"],
        artifact=ZEN_V11_SHA, url="https://zenodo.org/api/records/21775623",
    ))
    recs.append(claim(
        "benchmark-selection", SUB_BENCH, "selection_rules",
        "The benchmark subset keeps novel, human-targeting antibodies with explicitly defined antigen sequences. "
        "Records indicating conditional (for example pH-dependent) binding were excluded because folding models do "
        "not account for those conditions. Antigen length was restricted to 50 to 750 residues for computational "
        "feasibility, duplicates were removed, and Diamond BLASTP excluded antibodies sharing 95% or more identity "
        "with any SAbDab antibody, leaving 11,247 unique antibody-antigen sequence sets.",
        f"{P} 2.2 'Co-folding benchmark data preparation'",
    ))
    recs.append(claim(
        "decoy-construction", SUB_BENCH, "negative_construction",
        "Putative non-binders were built by KA-Search against the Observed Antibody Space for the closest VH CDR "
        "match to each binder, paired with the original antigen. For the 32% of records with no close OAS match, "
        "germline-encoded regions were reverted to their inferred germline sequences and the CDR-H3 loops "
        "randomised by sampling from AbLang predictions while keeping total identity at 85% or above. The final "
        "benchmark holds 22,494 records with an equal split between binding and non-binding instances.",
        f"{P} 2.2",
    ))
    recs.append(claim(
        "decoy-composition", SUB_BENCH, "negative_composition",
        "Of the 11,247 decoys, 7,647 (68.0%) are retrieved from the Observed Antibody Space with KA-Search and "
        "3,600 (32.0%) are generated by germline reversion with CDR-H3 randomisation. Both classes are paired "
        "against human antigens.",
        "Appendix D.1",
    ))
    recs.append(claim(
        "putative-negatives", SUB_BENCH, "negative_label_status",
        "The paper states of the non-binding subset: \"while the biological context strongly supports the assumption "
        "of non-reactivity, these pairs remain putative negatives and have not been experimentally validated for "
        "lack of binding.\" Appendix D adds that neither the tolerance argument nor the naive-repertoire argument is "
        "a measurement and that the authors claim no numerical false-negative rate.",
        f"{P} 2.2; Appendix D.1",
        rationale="Every accuracy on this benchmark is an accuracy against constructed negatives, so no result here is evidence of measured non-binding.",
        limitations=[
            "The decoys were not assayed. A pair in which the decoy does in fact bind, or the binder does not, is "
            "mislabelled, and the paper bounds rather than measures that fraction.",
        ],
    ))
    recs.append(claim(
        "label-noise-sensitivity", SUB_BENCH, "label_noise_sensitivity",
        "To test whether the engines simply prefer patent-derived sequences, 300 benchmark datapoints were sampled "
        "under a target-uniqueness constraint, balanced 150 germline-reverted and 150 OAS-matched, and their targets "
        "shuffled so that neither candidate binds the antigen it is folded against; the sampling was repeated under "
        "five seeds (42 to 46), giving 30,000 structure predictions and about 250 NVIDIA B200 GPU-hours. On the "
        "invalid triplets Protenix-v2 scored the patent-derived sequence higher in 50.3% of surviving pairs against "
        "72.4% on the same pairs with their correct targets, and Boltz-2 52.5% against 55.4%.",
        "Appendix D.2; Table 6 'Mean' column",
        rationale="This is the paper's own check on the putative-negative design, and it is the evidence behind the claim that the discrimination is not an artefact of sequence provenance.",
        limitations=[
            "Two engines and 300 triplets, limited by compute.",
            "Pairs where both members score exactly zero are excluded, so the percentages are over surviving pairs.",
            "The full per-seed cells of Table 6 are not extracted as results in this batch; only the headline means "
            "are recorded here.",
        ],
    ))
    recs.append(claim(
        "evidence-tiers", SUB_BENCH, "evidence_tiers",
        "Among the 11,247 benchmark binders, all 11,247 (100.0%) carry explicit binding evidence and a concrete "
        "antigen sequence, 5,967 (53.1%) a reported binding-affinity value, 3,888 (34.6%) any epitope "
        "characterisation and 1,232 (11.0%) a residue-level epitope. The tiers overlap and are not successive "
        "filters. Within the 3,888 epitope-characterised records, 1,003 are discontinuous or conformational, 826 "
        "linear, 501 functional or competitive and 1,558 not further specified.",
        "Appendix C; Table 5",
        rationale="The paper recommends selecting records by the evidence an application needs rather than treating all records as equivalent.",
    ))
    recs.append(claim(
        "sabdab-overlap", SUB_BENCH, "structural_overlap",
        "Only 1,828 of the benchmark antibodies target antigens with known structures in SAbDab, and only 70 records "
        "have a cumulative CDR edit distance of 10 or less to a SAbDab antibody against the same target. The paper "
        "says this minimal structural overlap substantially reduces the risk of data leakage from PDB-derived "
        "training data.",
        f"{P} 3.1",
        limitations=[
            "Reduced risk is not absence: the Discussion states that incomplete training-data disclosure for some "
            "engines prevents fully excluding overlap.",
        ],
    ))
    recs.append(claim(
        "ipsae-definition", BENCH, "scoring_metric_definition",
        "ipSAE was computed for the top-ranked structure of each record across all six models with a modified "
        "implementation of the ipSAE tool (https://github.com/DunbrackLab/IPSAE), using the predicted structures and "
        "their PAE matrices. The metric was computed asymmetrically with the paired antibody VH and VL concatenated "
        "as a single chain against the target (VH+VL to Target), with a PAE cutoff of 10 angstrom and a distance "
        "cutoff of 10 angstrom. The full-Fv ipSAE was selected as the primary evaluation metric for all subsequent "
        "analyses.",
        f"{P} 2.3 'Folding and structural scoring'; {P} 3.2.1",
        rationale="The headline numbers all rest on this score, and the paper's own framing is that it is a structural confidence score, not a binding measurement.",
        limitations=[
            "A modified implementation is named but not pinned to a commit or version.",
            "ipSAE values cluster at exactly zero when no confident interface is produced.",
        ],
    ))
    recs.append(claim(
        "folding-protocol", BENCH, "folding_protocol",
        "All six models used MSAs computed with ColabFold and no templates. The diffusion-based models generated one "
        "sample at each of five random seeds; AlphaFold-Multimer used its five parameter models. The highest "
        "confidence prediction was selected for analysis. Each of the 22,494 complexes was folded by all six "
        "engines with five predictions, giving 674,820 structure predictions and about 9,000 NVIDIA B200 GPU-hours; "
        "MSAs were computed once per unique sequence and excluded from the reported timings.",
        f"{P} 2.3; Appendix L",
    ))
    recs.append(claim(
        "screen-denominators", PROTOCOL_ID["screen-1in50-top1"], "trial_denominators",
        "27 targets were identified with at least 75 patent-derived binders each, with 20 independent simulation "
        "tests per target, giving 540 unique discovery trials; each simulation was repeated over 25 independent "
        "random seeds. Each trial ranks one true binder against 49 randomly selected non-binding decoys for the same "
        "target, against a 2% random baseline.",
        f"{P} 3.2.3; Figure 5 caption; Table 8 caption",
        rationale="The pairwise and the 1-in-50 endpoints rest on different denominators (11,247 pairs against 540 trials over 27 targets) and are never pooled.",
    ))
    recs.append(claim(
        "screen-uncertainty", PROTOCOL_ID["screen-1in50-top1"], "uncertainty_definition",
        "The Figure 5 caption states: \"Bars show mean top-1, top-5, and top-10 accuracy (by ipSAE ranking) over 25 "
        "independent runs with different random seeds; error bars indicate +/-2 sigma (sample standard deviation "
        "across runs).\" The NeurIPS checklist repeats that these are twice the sample standard deviation across "
        "runs and that the pairwise benchmarks, which use all 11,247 pairs without random sampling, carry no error "
        "bars. Table 8 separately prints a standard deviation across targets, a different quantity.",
        "Figure 5 caption; NeurIPS Paper Checklist item 7; Table 8 summary rows",
        rationale="The error bars are twice a sample standard deviation across seeds, not confidence intervals, and the two standard deviations in Table 8 measure different things.",
    ))
    recs.append(claim(
        "coverage-definition", PROTOCOL_ID["pairwise-coverage-50"], "coverage_definition",
        "The headline pairwise accuracy is measured after discarding the half of the pairs for which both members "
        "scored lowest. Appendix F states this \"is not the accuracy over the benchmark as a whole\" and reports "
        "accuracy at 100%, 75%, 50%, 25% and 10% coverage, where coverage is the fraction of the 11,247 pairs kept "
        "after ranking pairs by the higher of their two ipSAE scores. Exact ties receive half credit. Over all "
        "11,247 pairs Protenix-v2 reaches 0.72, against 0.87 at the midpoint.",
        f"Appendix F; {P} 3.2.2",
        rationale="The 87% and the 72% are the same engine on the same pairs at two coverage levels; quoting the first as the benchmark accuracy would overstate it.",
    ))
    recs.append(claim(
        "tie-effect", PROTOCOL_ID["pairwise-coverage-100"], "undecidable_pairs",
        "When both members of a pair fail to produce a confident interface, ipSAE returns exactly zero for both and "
        "the pair is undecidable; such pairs are scored at 0.5 rather than dropped. OpenFold3 leaves 37.9% of pairs "
        "undecidable and Protenix-v2 only 2.9%, so part of the gap between them at full coverage reflects how often "
        "each engine produces any interface prediction at all, not how well it ranks the ones it produces.",
        "Appendix F; Table 7 column \"Ties\"",
    ))
    recs.append(claim(
        "epitope-localisation", BENCH, "epitope_localisation",
        "Patent epitope residue annotations could be mapped to the folded antigen construct for 1,232 binder "
        "records. Even the best-scoring model, Protenix-v2, placed the antibody in contact with the annotated "
        "epitope in only 62.8% of cases. The paper concludes that binding discrimination does not establish accurate "
        "epitope localization and that a confident prediction is not necessarily a correct one.",
        f"{P} 3.3.2; {P} 4 'Discussion'",
    ))
    recs.append(claim(
        "affinity-correlation", BENCH, "affinity_correlation",
        "Heterogeneous affinity and potency measurements (KD, KA, IC50, EC50) were standardised to pAffinity across "
        "the 5,207 binders with reported values that parse unambiguously. Binned comparisons show a marginal trend "
        "toward higher ipSAE at higher affinity, but the paper says the signal is too weak to be predictive and that "
        "the models appear to capture a binary binding or non-binding distinction rather than a graded measure of "
        "interaction strength.",
        f"{P} 3.2.4; {P} 4; Appendix I",
        rationale="States in the authors' own words that the confidence scores are not affinity estimates.",
    ))
    recs.append(claim(
        "training-data-disclosure", BENCH, "training_data_disclosure",
        "The Discussion states that several evaluated models disclose limited detail on their training data, that "
        "the temporal analysis provides no temporal evidence that training-data overlap drives the observed "
        "performance hierarchy, and that incomplete training-data disclosure for some of these models prevents "
        "fully excluding overlap or disentangling improvements in binding prediction from differences in "
        "training-set coverage.",
        f"{P} 4 'Discussion'",
    ))
    recs.append(claim(
        "temporal-analysis", BENCH, "contamination_analysis",
        "Benchmark pairs were grouped by the publication date of the binder's source patent, one bucket before 2018 "
        "and six-month buckets to H1 2025, with bucket sizes from 305 to 3,229 pairs and bootstrap 95% confidence "
        "intervals. Accuracy does not systematically decline toward more recent patents: Protenix-v2 moves from "
        "0.716 to 0.689 and IntelliFold v2 from 0.654 to 0.669. Splitting at each engine's stated PDB training "
        "cutoff, the largest pre-minus-post difference across all six engines is 1.8 percentage points (IntelliFold "
        "v2) and 0.6 points for both Protenix releases, against a spread between engines of more than ten points.",
        "Appendix J; Figures 13 and 14",
        limitations=[
            "An external probe, not a disclosure. Patent ingestion timing is a proxy for training-corpus membership.",
            "The per-bucket values are shown as figures; only the quoted endpoints are printed in the text.",
        ],
    ))
    recs.append(claim(
        "consensus-high-stringency", BENCH, "consensus_coverage",
        "Requiring agreement among five or six models restricts coverage sharply: when all six models must agree, "
        "about half the dataset is excluded even at a DockQ threshold of 0.01, and at DockQ 0.23 or better the "
        "retained pairs reach at least 90% pairwise accuracy. At k of 3 or more and DockQ 0.80 accuracy reaches "
        "96.8% but only 3.0% of pairs remain eligible.",
        f"{P} 3.3.1; Appendix K; Figures 7 and 16",
        limitations=[
            "The k of 5 and k of 6 accuracies are given as \"at least 90%\" rather than as printed values, so they "
            "are recorded here as a claim and not as results.",
        ],
    ))
    recs.append(claim(
        "compute-budget", BENCH, "compute_budget",
        "Folding all 22,494 complexes across the six models required approximately 9,000 GPU-hours on NVIDIA B200 "
        "GPUs, for 674,820 structure predictions in total. The label-noise experiment of Appendix D.2 took a further "
        "250 B200 GPU-hours.",
        f"{P} 2.3; Appendix L; Appendix D.2",
        rationale="The cost of running all six engines on every candidate is what separates this benchmark from a practical screening configuration.",
    ))
    recs.append(claim(
        "publication-status", S_PAPER, "publication_status",
        "The POISK Explorer landing page states \"Read the paper - Accepted at NeurIPS 2026\". The pinned bioRxiv v1 "
        "PDF carries the standard banner that it was not certified by peer review, and no peer-reviewed version was "
        "retrieved.",
        "POISK Explorer landing page, hero section; bioRxiv v1 PDF per-page banner",
        sources=[S_EXPLORER, S_PAPER], methods=["automated-source-review", "source-hash-verification", "pdf-text-parse"],
        artifact=EXPLORER_SHA, url="https://poisk-explorer.github.io/",
        rationale="Recorded as the project's own statement. The source record keeps publication_status preprint because the pinned artifact is the preprint.",
    ))
    for key, printed, *_ in ENGINES:
        recs.append(claim(
            f"screen-target-spread-{key}", CONFIG[key], "screening_variability_across_targets",
            f"In the 1-in-50 screening simulation, {printed} has a standard deviation of {t8['sd_targets'][key]} "
            f"percentage points in top-1 accuracy across the 27 antigen constructs, against "
            f"{t8['sd_seeds'][key]} points across the 25 sampling seeds. For Protenix-v2 the per-construct top-1 "
            "accuracy ranges from 2.2% to 70.8%. Between-target variation exceeds sampling variation for every "
            "engine.",
            f"Table 8, row \"SD across targets (pp)\", column \"{T8COL[key]}\"; Table 8, row \"SD across seeds (pp)\", column \"{T8COL[key]}\"; Appendix H",
            rationale=(
                "Table 8's between-target standard deviation is a printed value with no metric concept in "
                "data/vocab/metric.ttl to carry it as a result, and it is a different quantity from the across-seed "
                "spread recorded as the result's uncertainty. It is kept here so the printed cell is not lost."
            ),
            name=f"POISK: {printed} screening variability across targets",
        ))

    # ---------------- write ----------------
    ids = [r["id"] for r in recs]
    if len(ids) != len(set(ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        fail(f"duplicate record ids: {dupes}")
    recs.sort(key=lambda r: r["id"])
    with open(sys.argv[2], "w", encoding="utf-8") as fh:
        for r in recs:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    counts = {}
    for r in recs:
        counts[r["kind"]] = counts.get(r["kind"], 0) + 1
    print(f"{len(recs)} records: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))


if __name__ == "__main__":
    main()
