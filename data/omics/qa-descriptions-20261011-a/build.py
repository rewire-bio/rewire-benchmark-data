"""Issue #88, placeholder descriptions, batch A (59 records): the 49 mRNABench
linear-probe pipelines, the 8 "Named prediction method identified in the
cited primary source" methods, and DeepAffinity and DeepDTA.

Reads the original lines from origin/main, applies the changes below, writes
the store files in place and regenerates batch.jsonl (new sources and one
metadata-correction claim per changed description, all needs_review).
  python3 -I data/omics/qa-descriptions-20261011-a/build.py           write
  python3 -I data/omics/qa-descriptions-20261011-a/build.py --check   check only
Run from the repository root.
"""
import hashlib
import json
import subprocess
import sys

BASE = "47a06e988e8b7db72b6f4d3404f1d4db7bb0ca88"  # origin/main when batches a to e were integrated
HERE = "data/omics/qa-descriptions-20261011-a"
NOTE = "Replace a placeholder description with a sourced functional description (issue #88). Historical releases retain the original value."
MRNABENCH = "expansion-p3-mrnabench-2025"
PROTEINGYM_PAPER = "profile-protocol-proteingym-paper-xml-a58110e0"
PROTEINGYM_README = "run-doc-proteingym-readme-md-144fe22b"
HOPF = "qa-descriptions-20261011-a-source-hopf2017"
GEMME = "qa-descriptions-20261011-a-source-gemme2019"
RSALOR = "qa-descriptions-20261011-a-source-rsalor2025"

# mRNABench Appendix A, "Overview of Evaluated Models": one clause per model family.
FAMILY = {
    "utrbert": ("3'UTRBERT", "a Transformer mRNA model pretrained on the 3' UTRs of 100,000 human mRNAs"),
    "aido-rna": ("AIDO.RNA", "a Transformer RNA model trained on 42 million non-coding RNAs from RNAcentral"),
    "dnabert-s": ("DNABERT-S", "a Transformer DNA model trained by contrastive learning on prokaryotic genomes"),
    "dnabert2": ("DNABERT2", "a Transformer DNA model trained on a multispecies dataset with byte-pair-encoding tokens"),
    "ernierna": ("ERNIE-RNA", "a Transformer RNA model pretrained on 20 million non-coding RNAs with structural information added as attention-mask biases"),
    "evo1": ("Evo", "a StripedHyena DNA model trained autoregressively on the OpenGenome dataset"),
    "evo2": ("Evo 2", "a StripedHyena2 DNA model trained autoregressively on OpenGenome2, 9 trillion nucleotides across all domains of life"),
    "helix-mrna": ("Helix-mRNA", "an mRNA foundation model with a Mamba2 and Transformer hybrid backbone trained on 26 million mRNAs from eukaryotic and viral species"),
    "hyenadna": ("HyenaDNA", "a Hyena DNA model trained autoregressively on the human reference genome"),
    "nt": ("Nucleotide Transformer", "a Transformer DNA model on 6-mer tokens"),
    "orthrus": ("Orthrus", "a Mamba mRNA foundation model pretrained by contrastive learning on mRNA splice isoforms and orthologs"),
    "rinalmo": ("RiNALMo", "a Transformer RNA model trained on 36 million non-coding RNAs"),
    "rnabert": ("RNABERT", "a Transformer RNA model pretrained with masked language modelling and a structural alignment objective on 80,000 non-coding RNAs"),
    "rnaernie": ("RNAErnie", "a Transformer RNA model pretrained on 23 million non-coding RNAs with motif-level masking"),
    "rna-fm": ("RNA-FM", "a Transformer RNA foundation model pretrained on 23 million non-coding RNAs"),
    "rnamsm": ("RNA-MSM", "a Transformer RNA model trained on multiple sequence alignments of about 8 million non-coding RNAs"),
    "splicebert": ("SpliceBERT", "a Transformer mRNA model trained on 2 million vertebrate mRNAs"),
    "utrlm": ("UTR-LM", "a Transformer mRNA model pretrained on random and endogenous 5' UTR sequences from various species"),
}
# Checkpoint name -> (family, what the same table says about that checkpoint,
# or None). Size and context are left to the name and the source table.
CHECKPOINTS = {
    "utrbert-3mer": ("utrbert", "with a 3-mer tokenizer"),
    "utrbert-4mer": ("utrbert", "with a 4-mer tokenizer"),
    "utrbert-5mer": ("utrbert", "with a 5-mer tokenizer"),
    "utrbert-6mer": ("utrbert", "with a 6-mer tokenizer"),
    "aido-rna-650m": ("aido-rna", None),
    "aido-rna-1b600m": ("aido-rna", None),
    "aido-rna-650m-cds": ("aido-rna", "domain-adapted for mRNA on coding sequences"),
    "aido-rna-1b600m-cds": ("aido-rna", "domain-adapted for mRNA on coding sequences"),
    "dnabert-s": ("dnabert-s", None),
    "dnabert2": ("dnabert2", None),
    "ernierna": ("ernierna", None),
    "ernierna-ss": ("ernierna", "fine-tuned on secondary structure"),
    "evo-1–8k-base": ("evo1", "that is the base model"),
    "evo-1–131k-base": ("evo1", "trained with extended context"),
    "evo-1.5–8k-base": ("evo1", "trained on an Evo 1 dataset enlarged by 50%"),
    "evo2–1b-base": ("evo2", "trained as a base model on a mixture of genomic regions including mRNA"),
    "evo2–7b-base": ("evo2", "trained as a base model on a mixture of genomic regions including mRNA"),
    "evo2–7b": ("evo2", "with extended context, trained on long genomic sequences"),
    "helix-mrna": ("helix-mrna", None),
    "hyenadna-tiny-16k-d128": ("hyenadna", None),
    "hyenadna-small-32k": ("hyenadna", None),
    "hyenadna-medium-160k": ("hyenadna", None),
    "hyenadna-medium-450k": ("hyenadna", None),
    "hyenadna-large-1m": ("hyenadna", None),
    "nt-500m-human-ref": ("nt", "trained on the human reference genome"),
    "nt-500m-1000g": ("nt", "trained on the 1000 Genomes Project"),
    "nt-2.5b-1000g": ("nt", "trained on the 1000 Genomes Project"),
    "nt-2.5b-multi-species": ("nt", "trained on 850 genomes"),
    "nt-v2–50m-multi-species": ("nt", "from the v2 series, which uses RoPE and GLUs, trained on multiple species"),
    "nt-v2–100m-multi-species": ("nt", "from the v2 series, which uses RoPE and GLUs, trained on multiple species"),
    "nt-v2–250m-multi-species": ("nt", "from the v2 series, which uses RoPE and GLUs, trained on multiple species"),
    "nt-v2–500m-multi-species": ("nt", "from the v2 series, which uses RoPE and GLUs, trained on multiple species"),
    "orthrus-base-4": ("orthrus", None),
    "orthrus-large-6": ("orthrus", "pretrained with splice and codon tracks"),
    "orthrus-mlm": ("orthrus", None),
    "rinalmo": ("rinalmo", None),
    "rnabert": ("rnabert", None),
    "rnaernie": ("rnaernie", None),
    "rna-fm": ("rna-fm", None),
    "mrna-fm": ("rna-fm", "trained on 45 million coding-only sequences (the mRNA-FM variant)"),
    "rnamsm": ("rnamsm", None),
    "splicebert-v-1024nt": ("splicebert", None),
    "splicebert-v-510nt": ("splicebert", "with a 510-nucleotide context"),
    "splicebert-h-510nt": ("splicebert", "trained only on human sequences"),
    "utrlm-te-el": ("utrlm", "trained for translation efficiency and expression level"),
    "utrlm-mrl": ("utrlm", "trained for mean ribosome loading"),
}
PROBE = "Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from"
NAIVE = {
    "naive-4": "Linear probe, trained per mRNABench task, on hand-made sequence features (all k-mers of size three to seven and GC content), with no learned model.",
    "naive-6": "Linear probe, trained per mRNABench task, on hand-made sequence features (all k-mers of size three to seven, GC content, CDS length and exon count), with no learned model.",
    "naive-mamba": "Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from an untrained three-layer Mamba with 64 hidden dimensions and random initial weights.",
}


VOWEL_SOUND = {"AIDO.RNA", "ERNIE-RNA", "Evo", "Evo 2", "Orthrus", "RNA-FM", "RNABERT", "RNAErnie", "RNA-MSM"}


def mrnabench_description(name):
    if name in NAIVE:
        return NAIVE[name]
    family, note = CHECKPOINTS[name]
    short, clause = FAMILY[family]
    article = "an" if short in VOWEL_SOUND else "a"
    checkpoint = f"{article} {short} checkpoint {note}" if note else f"{article} {short} checkpoint"
    subject = f"the {short}" if short == "Nucleotide Transformer" else short
    # The source table prints an en dash in some checkpoint names; the description uses a hyphen.
    return f"{PROBE} {name.replace('\u2013', '-')}, {checkpoint}; {subject} is {clause}."


MRNABENCH_LOCATOR = (f"{MRNABENCH}: Appendix A, Overview of Evaluated Models (family and variant rows; naive baselines paragraph); "
                     "Section 4.3, Linear Probing ('training a linear classifier on frozen embeddings'; 'averaging over per-nucleotide embeddings')")

# id -> (store file, new description, sources added, claim source_locator)
OTHER = {
    "uc20260930-method-blasso-rhodopsin-predictor": (
        "data/entities/methods.jsonl",
        "Bayesian LASSO regression that predicts a rhodopsin's absorption wavelength from predefined physicochemical features of the amino acids in its sequence, without using its three-dimensional structure.",
        [],
        "uc20260930-source-rhomax-2024: Introduction (the approach of Inoue et al. 'utilizes the Bayesian LASSO ... based on predefined physicochemical features of amino acids. This approach does not take into account the geometric three-dimensional (3D) structure'); Comparison to Previous Methods",
    ),
    "uc20260930-method-frame-aware-k-mer-random-forest": (
        "data/entities/methods.jsonl",
        "Random forest whose input is the k-mer counts of the sequence computed separately for each of the three reading frames, trained on the same MPRA training set as FramePool50.",
        [],
        "uc20260930-source-framepool-2021: Methods, Random forest models ('the framed_forest model. This random forest takes as input the k-mer-counts for each frame (giving a vector of length 3*(4^k))'); S7 Fig caption",
    ),
    "uc20260930-method-k-mer-count-random-forest": (
        "data/entities/methods.jsonl",
        "Random forest whose input is a fixed-length vector of the sequence's 3-mer or 4-mer counts, with no reading-frame information, trained on the same MPRA training set as FramePool50.",
        [],
        "uc20260930-source-framepool-2021: Methods, Random forest models ('random forest models which use k-mer counts as input features ... 3mer_random_forest and 4mer_random_forest'); S7 Fig caption ('offers no frame information')",
    ),
    "uc20260930-method-jores-gc-and-motif-linear-regression": (
        "data/entities/methods.jsonl",
        "Linear model that predicts plant core promoter strength from the promoter's GC content and its maximum motif scores for six core promoter elements and 72 consensus transcription-factor binding motifs.",
        [],
        "uc20260930-source-jores-2021: Methods, Computational modelling of promoter strength ('a linear model for predicting promoter strength on the basis of the promoter's GC content and its maximum motif score for six core promoter elements ... and 72 consensus TF-binding motifs')",
    ),
    "uc20260930-method-evmutation": (
        "data/entities/methods.jsonl",
        "Unsupervised statistical model, fitted to a multiple sequence alignment of the protein family, that predicts mutation effects while explicitly capturing dependencies between residue positions.",
        [HOPF, PROTEINGYM_PAPER],
        f"{HOPF}: abstractText ('EVmutation, an unsupervised statistical method for predicting the effects of mutations that explicitly captures residue dependencies between positions'); {PROTEINGYM_PAPER}: Baselines (alignment-based models 'are trained on Multiple Sequence Alignments')",
    ),
    "uc20260930-method-site-independent": (
        "data/entities/methods.jsonl",
        "Alignment-based model, fitted to a multiple sequence alignment of the protein family, that predicts mutation effects from each position separately, without the dependencies between positions that EVmutation adds.",
        [HOPF, PROTEINGYM_PAPER],
        f"{PROTEINGYM_PAPER}: Baselines ('Alignment-based models, such as site-independent and EVmutation models [Hopf et al., 2017] ... are trained on Multiple Sequence Alignments'); {HOPF}: abstractText (EVmutation 'explicitly captures residue dependencies between positions'; most methods 'do not consider the interdependencies of residues')",
    ),
    "uc20260930-method-gemme": (
        "data/entities/methods.jsonl",
        "Global epistatic model that predicts mutational effects by modelling the evolutionary history of the natural sequences in a protein family's alignment, with a few interpretable parameters.",
        [GEMME],
        f"{GEMME}: abstractText ('predicts mutational outcomes by explicitly modeling the evolutionary history of natural sequences ... GEMME uses only a few biologically meaningful and interpretable parameters'); {PROTEINGYM_README}: baselines table, row GEMME (MSA)",
    ),
    "uc20260930-method-rsalor": (
        "data/entities/methods.jsonl",
        "Evolutionary score that predicts mutational effects from the log-odds ratio of wild-type and mutant residue frequencies in related proteins, scaled by the residue's relative solvent accessibility.",
        [RSALOR],
        f"{RSALOR}: abstractText ('a simple evolutionary score, based on the log-odd ratio (LOR) of wild-type and mutated residue frequencies in evolutionary related proteins, when scaled by the residue's relative solvent accessibility (RSA)'); {PROTEINGYM_README}: baselines table, row RSALOR (MSA & Structure)",
    ),
    "identity-model-deepaffinity": (
        "data/entities/models.jsonl",
        "Semi-supervised deep learning model that predicts compound-protein affinity from a compound SMILES string and a structure-annotated protein sequence, using recurrent encoders followed by convolutional layers.",
        [],
        "source-label-deepaffinity-arxiv-97d6e3ae: abstract, p.1 ('a semi-supervised deep learning model that unifies recurrent and convolutional neural networks'); §§2.2-2.4; the record's reviewed profile summary",
    ),
    "identity-model-deepdta": (
        "data/entities/models.jsonl",
        "Deep learning model that predicts drug-target binding affinity from a ligand SMILES string and a protein sequence, using a separate one-dimensional convolutional encoder for each.",
        [],
        "source-label-deepdta-arxiv-3c368fed: abstract, p.1 ('a deep-learning based model that uses only sequence information of both targets and drugs ... modeling of protein sequences and compound 1D representations with convolutional neural networks'); the record's reviewed profile summary",
    ),
}


def europe_pmc_source(id, title, doi, version, url, retrieved_at, sha, licence, status):
    attrs = {
        "url": f"https://doi.org/{doi}",
        "artifact_url": url,
        "version": version,
        "retrieved_at": retrieved_at,
        "artifact_sha256": sha,
        "publication_status": status,
        "media_type": "application/json",
        "source_locator": "abstractText",
        "doi": doi,
        "hash_scope": "SHA-256 of one retrieval of a Europe PMC REST search response. These responses are not byte-stable (a later retrieval can differ in JSON key order); the title and abstractText fields are the evidence.",
    }
    if licence:
        attrs["licence"] = licence
    else:
        attrs["missing_metadata"] = {"licence": {"reason": "unreported", "note": "Europe PMC record gives no licence"}}
    return {"id": id, "kind": "source", "name": f"Abstract: {title}",
            "description": "Source text retrieved and hashed for the issue #88 placeholder-description fix.",
            "status": "needs_review", "facets": {}, "source_ids": [], "links": [], "attributes": attrs}


SOURCES = [
    europe_pmc_source(HOPF, "Mutation effects predicted from sequence co-variation", "10.1038/nbt.3769",
                      "Europe PMC core record MED/28092658 (title and abstract), Nature biotechnology 2017",
                      "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI%3A%2210.1038%2Fnbt.3769%22&format=json&resultType=core",
                      "2026-10-11T00:38:38Z", "6a91a29373ab03b0ebd3a03a7655536bd6abec369d1385146b4f94d1e0b5fbec", None, "peer_reviewed"),
    europe_pmc_source(GEMME, "GEMME: A Simple and Fast Global Epistatic Model Predicting Mutational Effects", "10.1093/molbev/msz179",
                      "Europe PMC core record MED/31406981 (title and abstract), Molecular biology and evolution 2019",
                      "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A31406981+AND+SRC%3AMED&format=json&resultType=core",
                      "2026-10-11T00:38:39Z", "64051ec6729aeb65a0e48487ef29f5ad2a81ccb9280bb753129a98de4f7a9ad9", "CC-BY-NC-4.0", "peer_reviewed"),
    europe_pmc_source(RSALOR, "Residue conservation and solvent accessibility are (almost) all you need for predicting mutational effects in proteins",
                      "10.1101/2025.02.03.636212", "Europe PMC preprint record PPR/PPR974202 (title and abstract), bioRxiv 2025",
                      "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI%3A%2210.1101%2F2025.02.03.636212%22&format=json&resultType=core",
                      "2026-10-11T00:38:40Z", "a2850ec41b5d52f8b8a0848012d522936f14619c427eaed5610301c0210e0a8d", "CC-BY-NC-ND-4.0", "preprint"),
]


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
    "note": "Approved. Checked the 10 method and model descriptions against their sources (EVmutation, GEMME and RSALOR abstracts, the FramePool k-mer random forests, the RhoMax BLASSO text) and spot-checked the 49 mRNABench rows against Appendix A; all accurate. Licences on the 3 new sources match their Europe PMC records. At the reviewer's suggestion, the en dash printed in some checkpoint names is written as a hyphen in the descriptions.",
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


def plan():
    changes = dict(OTHER)
    for line in git_lines("data/entities/pipelines.jsonl"):
        if not line:
            continue
        record = json.loads(line)
        if record["description"].startswith("Named representation or feature baseline with a task-specific linear probe"):
            assert record["source_ids"] == [MRNABENCH], record["id"]
            changes[record["id"]] = ("data/entities/pipelines.jsonl", mrnabench_description(record["name"]), [], MRNABENCH_LOCATOR)
    return changes


def main(check):
    changes = plan()
    claims, rows = [], []
    for path in sorted({c[0] for c in changes.values()}):
        base = git_lines(path)
        out = list(base)
        for i, line in enumerate(base):
            if not line:
                continue
            record = json.loads(line)
            change = changes.get(record["id"])
            if not change:
                continue
            assert dumps(record) == line, record["id"]
            _, description, added, claim_locator = change
            new = json.loads(line)
            new["description"] = description
            for source in added:
                assert source not in new["source_ids"], (record["id"], source)
                new["source_ids"].append(source)
            assert {k for k in record if record[k] != new[k]} <= {"description", "source_ids"}
            out[i] = dumps(new)
            digest = hashlib.sha256(f"{record['id']}:description:2026-10-11-a".encode()).hexdigest()[:20]
            claims.append({
                "id": f"metadata-correction-{digest}", "kind": "claim", "name": f"{record['name']}: description",
                "description": NOTE, "status": "needs_review", "facets": record["facets"], "source_ids": new["source_ids"],
                "links": [{"relation": "subject", "target_id": record["id"]}],
                "attributes": {"field": "description", "previous_value": record["description"], "value": description,
                               "source_locator": claim_locator},
            })
            rows.append(record["id"])
        sync(path, base, out, check)
    assert len(rows) == len(changes), (len(rows), len(changes))
    batch = [dumps(reviewed(s)) for s in SOURCES] + [dumps(reviewed(c)) for c in sorted(claims, key=lambda c: c["id"])]
    text = "\n".join(batch) + "\n"
    if check:
        assert open(f"{HERE}/batch.jsonl", encoding="utf8").read() == text, "batch.jsonl differs from the build"
    else:
        open(f"{HERE}/batch.jsonl", "w", encoding="utf8").write(text)
    print(f"{len(rows)} descriptions changed; batch has {len(batch)} records ({len(claims)} correction claims, {len(SOURCES)} sources)")
    return changes


if __name__ == "__main__":
    main("--check" in sys.argv)
