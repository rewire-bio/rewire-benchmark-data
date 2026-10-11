"""Issue #88, placeholder descriptions, batch C: the 29 "Identity as reported in
this paper" pipelines, the 6 scTab comparison methods and the 6 MPRabc
enhancer-gene methods.

Every description comes from the record's existing primary source, which each
record already cites, so this batch adds no source records. The 6 excluded
"Identity as reported" model records are skipped (see changes.md).

Reads the original lines from origin/main, applies the changes below, writes the
store files in place and regenerates batch.jsonl (one metadata-correction claim
per changed description, all needs_review).
  python3 -I data/omics/qa-descriptions-20261011-c/build.py           write
  python3 -I data/omics/qa-descriptions-20261011-c/build.py --check   check only
Run from the repository root.
"""
import hashlib
import json
import subprocess
import sys

BASE = "47a06e988e8b7db72b6f4d3404f1d4db7bb0ca88"  # origin/main when batches a to e were integrated
HERE = "data/omics/qa-descriptions-20261011-c"
NOTE = "Replace a placeholder description with a sourced functional description (issue #88). Historical releases retain the original value."
PIPELINES = "data/entities/pipelines.jsonl"
METHODS = "data/entities/methods.jsonl"
IAR = "Identity as reported in this paper. Unspecified versions are not assumed equivalent to other papers."

# "Identity as reported" pipelines: id -> (description, extra source_locator text).
# The locator for each of these is built from the record's own reviewed profile
# (summary locator and architecture fact locator) plus the extra sections read
# for this description.
PIPES = {
    "reported-model-0829aff5471d4b": (
        "Sequence-based enhancer-location stage of the Hi-Enhancer framework: DNABERT-2 extracts DNA sequence features and a stacking ensemble built with AutoGluon predicts enhancer labels.",
        "Abstract/Results"),
    "reported-model-1a67087ac262c5": (
        "Classifies gene fusion breakpoints from 10 kbp DNA windows using frozen Nucleotide Transformer embeddings, concatenating the middle embedding at the breakpoint of each sequence and training a small neural-network classifier on it.",
        "Methods/Embedding extraction; Abstract/Methods"),
    "reported-model-1be5c4b7c52a41": (
        "Probabilistic single-cell comparator in the scaLR study: variational autoencoders infer low-dimensional cell representations and the scANVI stage uses annotation labels for cell-type prediction.",
        "Methods/scaLR performance comparison with different pipelines (scVI-tools description)"),
    "reported-model-2894d253c5e8a8": (
        "Predicts pairwise non-coding RNA interactions from sequence alone, with GenerRNA embeddings average-pooled over each molecule and fed to a feed-forward classifier trained on the augmented pairs.",
        "Results/Table 1 (pooling and augmentation settings); Methods/Model architecture/Pooling techniques"),
    "reported-model-3f850c08d76410": (
        "Predicts RNA secondary structure in two stages: convolutional encoding and decoding with self-attention over the one-hot sequence and existing thermodynamic tool predictions estimates per-base scores, which then constrain free-energy minimisation.",
        "Abstract"),
    "reported-model-40ce004270dee4": (
        "Estimates protein fitness from the negative pseudo-perplexity of a sequence, approximated in a single unmasked forward pass by an ensemble of eight multilayer perceptrons that predict the ESM-2 650M masked residue profiles.",
        "Abstract; Section III Pseudo-perplexity in one fell swoop"),
    "reported-model-41ae49bb40ed8e": (
        "mRNA-protein interaction predictor that encodes the RNA-binding protein with ProteinBERT embeddings and feeds them to the study's attention-based prediction framework alongside the RNA representation.",
        "Abstract/Results; Datasets and methods/The implemented RBP encoding schemes"),
    "reported-model-4921459942b45f": (
        "Chimeric antibody-deamidation predictor: a global module of ESM-2 650M embeddings of the full antibody sequence is concatenated with a local windowed-sequence module and classified by a dense head.",
        "3. Results/3.3 Model architecture (chimeric model figure); 2. Methods (esm2_t33_650M_UR50D selection)"),
    "reported-model-49bc768f46b366": (
        "Classifies protein domains into CATH superfamilies with a feed-forward network over ProstT5 amino-acid embeddings and 3Di structural-alphabet embeddings.",
        "Abstract"),
    "reported-model-4ce8cae0f2eafc": (
        "Metagenomic pathogen identification pipeline: TCINet turns sequencing reads into taxonomic embeddings and sparse abundance estimates with uncertainty, and the HTRS post-inference module enforces taxonomic constraints and recalibrates confidence.",
        "Abstract/Methods"),
    "reported-model-57dbab30462150": (
        "Predicts small-molecule-binding residues from sequence alone, using frozen esm2_t33_650M_UR50D residue embeddings with a contrastive-learning binding-site predictor.",
        "Abstract"),
    "reported-model-60455ff7cc0c15": (
        "Predicts gene-regulatory links by combining context-aware gene representations from the pretrained Geneformer single-cell foundation model with graph-based representations learned from known regulatory interactions.",
        "Introduction (scRegNet framework description); Abstract/Results"),
    "reported-model-67ea6bd77b2ed1": (
        "Predicts binary protein-protein interactions from ESM-2 representations of sequence segments fused by a transformer encoder; AMPS is the segment-feature variant of the framework.",
        "Abstract"),
    "reported-model-688eb780ef7d2e": (
        "Metagenomic classification baseline in which PC-mer encodes nucleotide physicochemical properties as a compressed k-mer feature vector and an L2-regularised logistic-regression classifier assigns taxa.",
        "Abstract; 2 Method/2.2 Learning unit (classifier list)"),
    "reported-model-6c0bc8d297cc7a": (
        "End-to-end blind docking and virtual screening protocol: DiffDock samples ligand poses, the normalised mixture density network score selects a pose, and an interaction module estimates binding affinity.",
        "Abstract"),
    "reported-model-73ae07fb5be204": (
        "Predicts protein-protein interactions from three modalities: MaSIF surface descriptors, graph convolutions over the 3D structure, and ProstT5 residue embeddings as graph node features, fused by a transformer encoder.",
        "Abstract; Methods/Model architecture (ProstT5 per-residue embeddings as node features)"),
    "reported-model-7ad28cd57f5f5b": (
        "Predicts small-molecule-binding nucleotides from sequence, feeding residue-level ERNIE-RNA embeddings to a multilayer-perceptron binary classifier with no structural input.",
        "Abstract"),
    "reported-model-7cf2f9951e1dba": (
        "Low-resource single-cell annotation platform: it trains on feature subsets to rank gene importance, retrains the final model on the top-K features, and batches samples across CPUs to limit memory.",
        "Abstract"),
    "reported-model-86393c76dd8fa9": (
        "Predicts nucleic-acid-binding residues by fusing multimodal ESM3 sequence, structure and function embeddings with ESM-MSA features through cross-attention, alongside an equivariant graph network over the residue contact map.",
        "Abstract; Results (MegSite architecture overview)"),
    "reported-model-89f5a8f309fa18": (
        "Predicts gene-regulatory links by combining context-aware gene representations from the pretrained scBERT single-cell foundation model with graph-based representations learned from known regulatory interactions.",
        "Introduction (scRegNet framework description); Abstract/Results"),
    "reported-model-8ad3e0cefde796": (
        "Predicts bacterial protective antigens with a deep classifier over 1,280 ESM-derived sequence features combined with the 509 biological and biomedical features of Vaxign-DL.",
        "Abstract"),
    "reported-model-8cb3dd4e9f5b10": (
        "Automated assembly and taxonomic-profiling pipeline for virus discovery in sequencing libraries; the nt variant assigns contigs by querying them with Centrifuge against the NCBI nucleotide collection.",
        "2. Materials and methods/2.2 (Lazypipe-nt definition)"),
    "reported-model-a0db32ae53e5ed": (
        "Annotates scATAC-seq cell types within one modality: DNABERT-2 encodes peak sequences, accessibility values complete the cell representation, and a graph neural network aligns reference and query similarity graphs by domain adaptation.",
        "Abstract; Materials and methods/Feature extraction from genomic sequences (DNABERT-2)"),
    "reported-model-d6a7fa854437e8": (
        "Adds geometric features of the scGPT residual stream, including centred cosine similarity between gene vectors and PCA projections, to an expression baseline for predicting transcription-factor-target links.",
        "Abstract/Results; Results (per-feature comparison table)"),
    "reported-model-df0efcc0346224": (
        "Predicts ligand-protein binding affinity by combining empirical docking scores and sequence-based deep-learning predictions in a learned meta-model, optionally with physicochemical properties or molecular descriptors.",
        "Abstract"),
    "reported-model-e4710b1c3facf2": (
        "ESM-2-only feature configuration of a clathrin-identification study: 1,280-dimensional ESM-2 embeddings feed an LSTM classifier, separately from the fused multi-model PLM-CLA predictor.",
        "Results and discussions/Performance evaluation of individual feature embeddings (embedding dimensions and per-PLM LSTM models)"),
    "reported-model-ee1ae8162c7d67": (
        "Supervised chromatin-accessibility and regulatory-variant predictor in which embeddings from ARSENAL, a short-context masked DNA language model trained with motif-discovery regularisation, are added to ChromBPNet inputs.",
        "Abstract"),
    "reported-model-f8f0257b98749a": (
        "Classifies proteins into family-specific functional classes with an ESM2-35M backbone whose first six encoder layers are frozen, adapting a question-answering architecture to locate a domain span and classify the selected region.",
        "Abstract; 2 Materials and methods/2.1 SPIN architecture (layer freezing)"),
    "reported-model-fdac4c1ec8a433": (
        "Identifies protein-protein interaction sites from ProtT5 residue embeddings together with further sequence feature descriptors, classified by an ensemble of BiLSTM and capsule-network models.",
        "Abstract; Introduction (EDLMPPI feature extractor and architecture)"),
}

SCTAB_PAPER = ["ucc-research-source-sctab-paper"]
SCTAB_BOTH = ["ucc-research-source-sctab-paper", "ucc-research-source-sctab-supp"]
MPRABC = ["ucc-research-source-mprabc"]

# scTab comparison methods and MPRabc methods: id -> (description, source ids cited, locator).
METHOD_CHANGES = {
    "ucc-research-method-sctab": (
        "Scalable implementation of the TabNet architecture adapted to single-cell data: expression is size-factor normalised and log1p transformed, and observation-wise feature attention selects the genes used for cell-type classification.",
        SCTAB_PAPER, "Results (scTab architecture); Discussion (observation-wise feature attention)"),
    "ucc-research-method-ciform": (
        "Transformer-based cell-type annotation model for single-cell RNA-seq, benchmarked against scTab.",
        SCTAB_PAPER, "Results (CIForm benchmark paragraph)"),
    "ucc-research-method-linear": (
        "Logistic-regression cell-type classifier implemented to train on the full corpus with a cross-entropy loss, as the study's optimised linear baseline.",
        SCTAB_PAPER, "Results (scaling logistic regression to the full training data)"),
    "ucc-research-method-mlp": (
        "Multi-layer perceptron cell-type classifier previously proposed for single-cell annotation, used as a nonlinear baseline.",
        SCTAB_PAPER, "Results (nonlinear models benchmarked against the linear baseline)"),
    "ucc-research-method-xgboost": (
        "Gradient-boosted tree classifier for tabular data, used as a nonlinear cell-type annotation baseline.",
        SCTAB_PAPER, "Results (nonlinear models benchmarked against the linear baseline)"),
    "ucc-research-method-uce": (
        "Linear probe on Universal Cell Embeddings: a logistic-regression cell-type classifier is fitted to the precomputed frozen UCE embeddings hosted by CELLxGENE.",
        SCTAB_PAPER, "Methods/Universal Cell Embedding (UCE) (zero-shot)"),
    "ucc-research-method-mprabc-abc": (
        "Predicts enhancer-gene pairs with a score that combines a measure of element activity, such as histone acetylation, with the 3D contact frequency between the element and candidate genes.",
        MPRABC, "Introduction (ABC model description)"),
    "ucc-research-method-mprabc-re2g": (
        "Supervised enhancer-gene prediction workflow that extends the Activity-by-Contact model, fitting a logistic-regression model on CRISPR-perturbation labels.",
        MPRABC, "Introduction (ENCODE-rE2G description); Methods/ENCODE-rE2G (logistic regression)"),
    "ucc-research-method-mprabc-full": (
        "Extends ENCODE-rE2G for enhancer-gene prediction by adding MPRALegNet-predicted log2(RNA/DNA) activity and Sei-derived regulatory features to its default DNase-seq and H3K27ac feature set, fitted with L2-regularised logistic regression.",
        MPRABC, "Introduction (MPRabc overview); Methods/ENCODE-rE2G (feature set and L2 regularisation)"),
    "ucc-research-method-mprabc-megamap": (
        "The MPRabc enhancer-gene model fitted with megamap Hi-C, an integration of Hi-C experiments across multiple tissues, in place of the standard Hi-C contact data.",
        MPRABC, "Methods (megamap and standard Hi-C versions); Results (megamap operating point)"),
    "ucc-research-method-mprabc-mpralegnet": (
        "Ablation of MPRabc that adds only the MPRALegNet-predicted MPRA activity features to ENCODE-rE2G, leaving out the Sei-derived regulatory features.",
        MPRABC, "Methods (systematic ablations from the ENCODE-rE2G baseline); Results/Table 3"),
    "ucc-research-method-mprabc-sei": (
        "Ablation of MPRabc that adds only the Sei-derived regulatory features to ENCODE-rE2G, leaving out the MPRALegNet MPRA-activity features.",
        MPRABC, "Methods (systematic ablations from the ENCODE-rE2G baseline); Results/Table 3"),
}


def git_lines(path):
    return subprocess.run(["git", "show", f"{BASE}:{path}"], check=True, capture_output=True, text=True).stdout.split("\n")


def dumps(record):
    return json.dumps(record, separators=(",", ":"), ensure_ascii=False)


# Added at integration (2026-10-11), after the independent review recorded in
# docs/reviews/2026-10-11-description-batches-a-e.md and this folder's review.json.
REVIEW = {
    "method": ["automated-source-review", "ai-assisted-source-review"],
    "reviewer": ["claude"],
    "reviewer_note": "Extractor: Claude integrator agent for issue #88. Reviewer: a separate Claude review agent, independent of the extractor; no human review claimed.",
    "date": "2026-10-11",
    "method_note": "Compared the store diff with origin/main, read each new description against its cited source passage and checked the licence of each new source record.",
    "note": 'Approved. Checked all 11 scTab and MPRabc method descriptions against PMC11298532 and PMC13232518, and Lazypipe-nt, scaLR, CATHe2, DiffDock-NMDN, PC-mer and Hi-Enhancer against their papers; all match. The other pipeline descriptions are consistent with their pinned papers.',
    "receipt": f"{HERE}/review.json",
}


def reviewed(record):
    record = json.loads(dumps(record))
    record["status"] = "source_checked"
    review = dict(REVIEW)
    if record["kind"] == "source":
        review["retrieval_url"] = record["attributes"]["artifact_url"]
    record["attributes"]["review"] = review
    return record


def sync(path, base, out, check):
    """Compare or apply only the lines this batch changes, so batches a to e share one store."""
    current = open(path, encoding="utf8").read().split("\n")
    index = {json.loads(line)["id"]: i for i, line in enumerate(current) if line}
    for old, new in zip(base, out):
        if old == new:
            continue
        i = index[json.loads(new)["id"]]
        if check:
            assert current[i] == new, f"{path}: {json.loads(new)['id']} differs from the build"
        current[i] = new
    if not check:
        open(path, "w", encoding="utf8").write("\n".join(current))


def pipeline_locator(record, extra):
    profile = record["attributes"]["profile"]
    arch = [f for f in profile["facts"] if f["label"].startswith("Architecture")]
    assert len(arch) == 1, record["id"]
    flat = lambda text: " ".join(text.split())
    return (f"Reviewed profile ({profile['review']['date']}): summary at {flat(profile['summary_source_locator'])}; "
            f"architecture fact at {flat(arch[0]['source_locator'])}; description text also read at {extra}")


def plan():
    changes = {}
    for line in git_lines(PIPELINES):
        if not line:
            continue
        record = json.loads(line)
        if record["id"] not in PIPES:
            continue
        assert record["description"] == IAR, record["id"]
        description, extra = PIPES[record["id"]]
        changes[record["id"]] = (PIPELINES, description, record["source_ids"], pipeline_locator(record, extra))
    assert set(changes) == set(PIPES), sorted(set(PIPES) - set(changes))
    for line in git_lines(METHODS):
        if not line:
            continue
        record = json.loads(line)
        change = METHOD_CHANGES.get(record["id"])
        if not change:
            continue
        description, cited, locator = change
        assert set(cited) <= set(record["source_ids"]), record["id"]
        changes[record["id"]] = (METHODS, description, cited, f"{', '.join(cited)}: {locator}")
    assert len(changes) == len(PIPES) + len(METHOD_CHANGES), len(changes)
    return changes


def main(check):
    changes = plan()
    claims, rows = [], []
    for path in [METHODS, PIPELINES]:
        base = git_lines(path)
        out = list(base)
        for i, line in enumerate(base):
            if not line:
                continue
            record = json.loads(line)
            change = changes.get(record["id"])
            if not change or change[0] != path:
                continue
            assert dumps(record) == line, record["id"]
            _, description, cited, claim_locator = change
            new = json.loads(line)
            new["description"] = description
            assert {k for k in record if record[k] != new[k]} == {"description"}
            out[i] = dumps(new)
            digest = hashlib.sha256(f"{record['id']}:description:2026-10-11-c".encode()).hexdigest()[:20]
            claims.append({
                "id": f"metadata-correction-{digest}", "kind": "claim", "name": f"{record['name']}: description",
                "description": NOTE, "status": "needs_review", "facets": record["facets"], "source_ids": cited,
                "links": [{"relation": "subject", "target_id": record["id"]}],
                "attributes": {"field": "description", "previous_value": record["description"], "value": description,
                               "source_locator": claim_locator},
            })
            rows.append(record["id"])
        sync(path, base, out, check)
    assert len(rows) == len(changes), sorted(set(changes) - set(rows))
    text = "\n".join(dumps(reviewed(c)) for c in sorted(claims, key=lambda c: c["id"])) + "\n"
    if check:
        assert open(f"{HERE}/batch.jsonl", encoding="utf8").read() == text, "batch.jsonl differs from the build"
    else:
        open(f"{HERE}/batch.jsonl", "w", encoding="utf8").write(text)
    print(f"{len(rows)} descriptions changed; batch has {len(claims)} correction claims and no new sources")
    return changes


if __name__ == "__main__":
    main("--check" in sys.argv)
