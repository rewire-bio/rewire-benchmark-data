"""Issue #88, placeholder descriptions, batch B: the 26 catalogue candidates,
10 of the 16 language models (6 have no findable primary source; gaps.md),
the 7 scFoundation Table 4 pipelines, the 2 FoldBench models and the 6 TAPE
records.

Reads the original lines from origin/main, applies the changes below, writes
the store files in place and regenerates batch.jsonl (new sources and one
metadata-correction claim per changed description, all needs_review).
  python3 -I data/omics/qa-descriptions-20261011-b/build.py           write
  python3 -I data/omics/qa-descriptions-20261011-b/build.py --check   check only
Run from the repository root.
"""
import hashlib
import json
import subprocess
import sys

BASE = "47a06e988e8b7db72b6f4d3404f1d4db7bb0ca88"  # origin/main when batches a to e were integrated
HERE = "data/omics/qa-descriptions-20261011-b"
NOTE = "Replace a placeholder description with a sourced functional description (issue #88). Historical releases retain the original value."
P = "qa-descriptions-20261011-b-source-"
CATALOGUE_PLACEHOLDER = "Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review."
TAPE_PAPER = "evidence-expansion-evidence-discovery-final-tape-6ee0c3e6"
FOLDBENCH = "ucc-research-source-foldbench-paper"
SCF_SUPP = "coverage-source-scfoundation-supp"

# Catalogue candidates whose reviewed profile summary is about a wider family than the record.
CATALOGUE_OVERRIDE = {
    "catalog-model-boltz-2": "Boltz-2 predicts biomolecular complex structures and binding affinity.",
}

CLAUDE3_LOC = f"{P}claude3: model card abstract, p.1"
CLAUDE35_LOC = f"{P}claude3: Claude 3.5 Sonnet Model Card Addendum, section 1 Introduction"
# id -> (store file, new description, sources added, claim source_locator)
CHANGES = {
    "tgtval-20261009-model-claude-3-opus": ("data/entities/models.jsonl",
        "Large multimodal model with vision capabilities, the most capable of Anthropic's Claude 3 family.",
        [f"{P}claude3"], f"{CLAUDE3_LOC} ('Claude 3 Opus, our most capable offering'; 'All new models have vision capabilities')"),
    "tgtval-20261009-model-claude-3-sonnet": ("data/entities/models.jsonl",
        "Large multimodal model with vision capabilities in Anthropic's Claude 3 family, positioned between Opus and Haiku in skills and speed.",
        [f"{P}claude3"], f"{CLAUDE3_LOC} ('Claude 3 Sonnet, which provides a combination of skills and speed')"),
    "tgtval-20261009-model-claude-3-haiku": ("data/entities/models.jsonl",
        "Large multimodal model with vision capabilities, the fastest and least expensive of Anthropic's Claude 3 family.",
        [f"{P}claude3"], f"{CLAUDE3_LOC} ('Claude 3 Haiku, our fastest and least expensive model')"),
    "tgtval-20261009-model-claude-3-5-sonnet": ("data/entities/models.jsonl",
        "Large multimodal model from Anthropic, an evolution of the Claude 3 family with improved coding and visual processing.",
        [f"{P}claude3"], f"{CLAUDE35_LOC} ('Claude 3.5 Sonnet offers improved capabilities, including better coding and visual processing. Since it is an evolution of the Claude 3 model family')"),
    "tgtval-20261009-model-gpt-4o": ("data/entities/models.jsonl",
        "Autoregressive omni model from OpenAI, trained end to end across text, vision and audio, that accepts text, audio, image and video input and generates text, audio and image output.",
        [f"{P}gpt-4o"], f"{P}gpt-4o: abstract"),
    "tgtval-20261009-model-o1-preview": ("data/entities/models.jsonl",
        "Model in OpenAI's o1 series, trained with large-scale reinforcement learning to reason using a chain of thought before answering.",
        [f"{P}o1"], f"{P}o1: abstract ('The o1 model series is trained with large-scale reinforcement learning to reason using chain of thought')"),
    "tgtval-20261009-model-o1-mini": ("data/entities/models.jsonl",
        "Model in OpenAI's o1 series, trained with large-scale reinforcement learning to reason using a chain of thought before answering.",
        [f"{P}o1"], f"{P}o1: abstract ('The o1 model series is trained with large-scale reinforcement learning to reason using chain of thought')"),
    "tgtval-20261009-model-gpt-oss-120b": ("data/entities/models.jsonl",
        "Open-weight reasoning model from OpenAI with a mixture-of-experts Transformer architecture, trained by large-scale distillation and reinforcement learning.",
        [f"{P}gpt-oss"], f"{P}gpt-oss: abstract"),
    "tgtval-20261009-model-llama-3-1-8b": ("data/entities/models.jsonl",
        "Language model in Meta's Llama 3 herd, which natively supports multilinguality, coding, reasoning and tool use.",
        [f"{P}llama3"], f"{P}llama3: abstract ('a herd of language models that natively support multilinguality, coding, reasoning, and tool usage')"),
    "tgtval-20261009-model-qwen-2-7b": ("data/entities/models.jsonl",
        "Language model in the Qwen2 series, a suite of foundational and instruction-tuned language models from 0.5 to 72 billion parameters.",
        [f"{P}qwen2"], f"{P}qwen2: abstract"),
    "scfoundation-2024-supp-table4-method-actinn": ("data/entities/pipelines.jsonl",
        "Cell-type classifier for single-cell RNA-seq that trains a neural network with three hidden layers on datasets with predefined cell types and predicts cell types in other datasets.",
        [f"{P}actinn"], f"{P}actinn: abstractText; {SCF_SUPP}: Supplementary Table 4 (cell type annotation on Zheng68K and Segerstolpe)"),
    "scfoundation-2024-supp-table4-method-celltypist": ("data/entities/pipelines.jsonl",
        "Machine-learning tool for rapid cell-type annotation of single-cell RNA-seq data.",
        [f"{P}celltypist"], f"{P}celltypist: abstractText ('CellTypist, a machine learning tool for rapid and precise cell type annotation'); {SCF_SUPP}: Supplementary Table 4"),
    "scfoundation-2024-supp-table4-method-scanpy": ("data/entities/pipelines.jsonl",
        "Python toolkit for single-cell gene expression analysis, with methods for preprocessing, visualisation, clustering, trajectory inference and differential expression testing.",
        [f"{P}scanpy"], f"{P}scanpy: abstractText; {SCF_SUPP}: Supplementary Table 4"),
    "scfoundation-2024-supp-table4-method-scanvi": ("data/entities/pipelines.jsonl",
        "Semi-supervised variant of scVI, a deep generative model of single-cell transcriptomics, that uses existing cell-state annotations to label cells in new datasets.",
        [f"{P}scanvi"], f"{P}scanvi: abstractText ('scANVI, a semi-supervised variant of scVI designed to leverage existing cell state annotations'); {SCF_SUPP}: Supplementary Table 4"),
    "scfoundation-2024-supp-table4-method-scbert": ("data/entities/pipelines.jsonl",
        "Transformer model, pretrained on unlabelled single-cell RNA-seq data in the manner of BERT, that is fine-tuned to annotate cell types.",
        [f"{P}scbert"], f"{P}scbert: abstractText; {SCF_SUPP}: Supplementary Table 4"),
    "scfoundation-2024-supp-table4-method-singlecellnet": ("data/entities/pipelines.jsonl",
        "Tool that classifies query single-cell RNA-seq data by comparison with reference single-cell RNA-seq data, across platforms and species.",
        [f"{P}singlecellnet"], f"{P}singlecellnet: title and abstractText; {SCF_SUPP}: Supplementary Table 4"),
    "scfoundation-2024-supp-table4-method-scfoundation": ("data/entities/pipelines.jsonl",
        "Cell-type annotation with scFoundation, a model that produces contextual cell and gene representations from gene-expression measurements.",
        ["evidence-official-9863509ad10b824dc96b"],
        f"catalog-model-scfoundation profile summary (evidence-official-9863509ad10b824dc96b: Results pre-training framework; Methods Embedding, Encoder, Decoder); {SCF_SUPP}: Supplementary Table 4"),
    "ucc-research-model-helixfold3": ("data/entities/models.jsonl",
        "Open-source reproduction of AlphaFold 3 that predicts the all-atom structures of biomolecular complexes.",
        [], f"{FOLDBENCH}: Introduction ('the training code and datasets of AlphaFold 3 are not publicly available ... several open-source reproductions such as Boltz-1, Protenix, Chai-1 and HelixFold 3 have emerged'; 'five recent all-atom predictors')"),
    "ucc-research-model-protenix": ("data/entities/models.jsonl",
        "Open-source reproduction of AlphaFold 3 that predicts the all-atom structures of biomolecular complexes.",
        [], f"{FOLDBENCH}: Introduction (as for HelixFold 3)"),
    "discovery-model-tape-transformer": ("data/entities/models.jsonl",
        "Protein language model in the TAPE benchmark: a 12-layer Transformer with 512 hidden units and 8 attention heads (about 38 million parameters), pretrained by masked-token prediction.",
        [TAPE_PAPER], f"{TAPE_PAPER}: Models and Experimental Setup, Architectures and Training"),
    "discovery-model-tape-lstm": ("data/entities/models.jsonl",
        "Protein language model in the TAPE benchmark: two three-layer LSTMs with 1,024 hidden units for the forward and backward directions, pretrained by next-token prediction.",
        [TAPE_PAPER], f"{TAPE_PAPER}: Models and Experimental Setup, Architectures and Training"),
    "discovery-model-tape-resnet": ("data/entities/models.jsonl",
        "Protein language model in the TAPE benchmark: a dilated residual network of 35 blocks, each with two convolutional layers of 256 filters, kernel size 9 and dilation rate 2, pretrained by masked-token prediction.",
        [TAPE_PAPER], f"{TAPE_PAPER}: Models and Experimental Setup, Architectures and Training"),
    "discovery-model-tape-bepler": ("data/entities/models.jsonl",
        "Protein language model of Bepler et al. as benchmarked in TAPE: a two-layer bidirectional language model followed by three bidirectional LSTMs with 512 hidden units, trained by next-token prediction.",
        [TAPE_PAPER], f"{TAPE_PAPER}: Models and Experimental Setup, Architectures and Training"),
    "discovery-model-tape-unirep": ("data/entities/models.jsonl",
        "Protein language model of Alley et al. (UniRep) as benchmarked in TAPE: a unidirectional multiplicative LSTM with 1,900 hidden units, trained by next-token prediction.",
        [TAPE_PAPER], f"{TAPE_PAPER}: Models and Experimental Setup, Architectures and Training"),
}
ONE_HOT = ("Baseline featurisation in the TAPE benchmark that encodes the protein's amino-acid sequence one-hot, with no learned representation.",
           [TAPE_PAPER], f"{TAPE_PAPER}: Models and Experimental Setup, Baselines ('a one-hot encoding of the input amino acid sequence, which provides a simple baseline')")


def source(id, name, url, artifact, version, retrieved_at, sha, licence, status, locator, scope, media):
    attrs = {"url": url, "artifact_url": artifact, "version": version, "retrieved_at": retrieved_at, "artifact_sha256": sha,
             "publication_status": status, "media_type": media, "source_locator": locator, "hash_scope": scope}
    if licence:
        attrs["licence"] = licence
    else:
        attrs["missing_metadata"] = {"licence": {"reason": "unreported", "note": "The retrieved record or document gives no licence"}}
    return {"id": id, "kind": "source", "name": name,
            "description": "Source text retrieved and hashed for the issue #88 placeholder-description fix.",
            "status": "needs_review", "facets": {}, "source_ids": [], "links": [], "attributes": attrs}


EPMC_SCOPE = "SHA-256 of one retrieval of a Europe PMC REST search response. These responses are not byte-stable (a later retrieval can differ in JSON key order); the title and abstractText fields are the evidence."
ARXIV_SCOPE = "SHA-256 of one retrieval of an arXiv API Atom response for this identifier. The response is not guaranteed byte-stable; the title and summary fields are the evidence."
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query="
ARXIV = "https://export.arxiv.org/api/query?id_list="
SOURCES = [
    source(f"{P}claude3", "The Claude 3 Model Family: Opus, Sonnet, Haiku (Anthropic model card, with Claude 3.5 addenda)",
           "https://www.anthropic.com/claude-3-model-card",
           "https://www-cdn.anthropic.com/c6a80a657af445f40e31afac050f3bf76d3b1404/Claude%203%20Model%20Card.pdf",
           "PDF created 2024-10-22, 64 pages, including the June and October 2024 addenda", "2026-10-11T00:57:58Z",
           "88ae851f53c3034d436816164ce49a876b333fa9b550fb7ef29838182b59ba7d", None, "official_project_source",
           "Abstract, p.1; Claude 3.5 Sonnet Model Card Addendum, section 1", "SHA-256 of the PDF bytes served at artifact_url.", "application/pdf"),
    source(f"{P}gpt-4o", "Abstract: GPT-4o System Card (arXiv:2410.21276)", "https://arxiv.org/abs/2410.21276", f"{ARXIV}2410.21276",
           "arXiv:2410.21276 (title and abstract)", "2026-10-11T00:57:06Z", "c3866761db90f5305c9de058c83a1f0a8b7024e2ed19c5cd5a8612ea49498d81",
           "CC-BY-4.0", "preprint", "summary", ARXIV_SCOPE, "application/atom+xml"),
    source(f"{P}o1", "Abstract: OpenAI o1 System Card (arXiv:2412.16720)", "https://arxiv.org/abs/2412.16720", f"{ARXIV}2412.16720",
           "arXiv:2412.16720 (title and abstract)", "2026-10-11T00:57:09Z", "a80a58c5e52afb90137fda30abde87d1260a899474e63329edb99fb90067307d",
           "CC-BY-4.0", "preprint", "summary", ARXIV_SCOPE, "application/atom+xml"),
    source(f"{P}gpt-oss", "Abstract: gpt-oss-120b & gpt-oss-20b Model Card (arXiv:2508.10925)", "https://arxiv.org/abs/2508.10925", f"{ARXIV}2508.10925",
           "arXiv:2508.10925 (title and abstract)", "2026-10-11T00:57:12Z", "53712f4b5a62b8eab4c1095440fb936924e6ccfc616d27d27f4db90d8fd5cb83",
           "CC-BY-4.0", "preprint", "summary", ARXIV_SCOPE, "application/atom+xml"),
    source(f"{P}llama3", "Abstract: The Llama 3 Herd of Models (arXiv:2407.21783)", "https://arxiv.org/abs/2407.21783", f"{ARXIV}2407.21783",
           "arXiv:2407.21783 (title and abstract)", "2026-10-11T00:57:15Z", "4478b5fb0212644f89ec0f6f51d64ed4fc67abdd0af7595d96d49e4a1519cb7e",
           "arXiv non-exclusive licence to distribute 1.0 (http://arxiv.org/licenses/nonexclusive-distrib/1.0/)", "preprint", "summary", ARXIV_SCOPE, "application/atom+xml"),
    source(f"{P}qwen2", "Abstract: Qwen2 Technical Report (arXiv:2407.10671)", "https://arxiv.org/abs/2407.10671", f"{ARXIV}2407.10671",
           "arXiv:2407.10671 (title and abstract)", "2026-10-11T00:57:19Z", "ad370bb7ba48b47139e73c98c00fa0d9128e8a464012bc1ed327abb0c3605dd0",
           "arXiv non-exclusive licence to distribute 1.0 (http://arxiv.org/licenses/nonexclusive-distrib/1.0/)", "preprint", "summary", ARXIV_SCOPE, "application/atom+xml"),
    source(f"{P}actinn", "Abstract: ACTINN: automated identification of cell types in single cell RNA sequencing", "https://doi.org/10.1093/bioinformatics/btz592",
           f"{EPMC}DOI%3A%2210.1093/bioinformatics/btz592%22&format=json&resultType=core", "Europe PMC core record MED/31359028 (title and abstract), Bioinformatics 2020",
           "2026-10-11T00:58:59Z", "7fb2d86fa8f08860d57911adb52e8844220d915a891f1144e03310aabab4dc6d", None, "peer_reviewed", "abstractText", EPMC_SCOPE, "application/json"),
    source(f"{P}celltypist", "Abstract: Cross-tissue immune cell analysis reveals tissue-specific features in humans (CellTypist)", "https://doi.org/10.1126/science.abl5197",
           f"{EPMC}DOI%3A%2210.1126/science.abl5197%22&format=json&resultType=core", "Europe PMC core record MED/35549406 (title and abstract), Science 2022",
           "2026-10-11T00:59:00Z", "5f61b64a9214620eabddc95d0f514d40bdd9d98ab537223c8eca458100dfa404", "CC-BY-4.0", "peer_reviewed", "abstractText", EPMC_SCOPE, "application/json"),
    source(f"{P}scanpy", "Abstract: SCANPY: large-scale single-cell gene expression data analysis", "https://doi.org/10.1186/s13059-017-1382-0",
           f"{EPMC}DOI%3A%2210.1186/s13059-017-1382-0%22&format=json&resultType=core", "Europe PMC core record MED/29409532 (title and abstract), Genome biology 2018",
           "2026-10-11T00:59:01Z", "2ccec8651e795ef20410dda5c5d8d0010be3cb02f3b5f697c5e5404165bc6fdb", "CC-BY-4.0", "peer_reviewed", "abstractText", EPMC_SCOPE, "application/json"),
    source(f"{P}scanvi", "Abstract: Probabilistic harmonization and annotation of single-cell transcriptomics data with deep generative models (scANVI)", "https://doi.org/10.15252/msb.20209620",
           f"{EPMC}DOI%3A%2210.15252/msb.20209620%22&format=json&resultType=core", "Europe PMC core record MED/33491336 (title and abstract), Molecular systems biology 2021",
           "2026-10-11T00:59:03Z", "d8aff9fd2b294e50d5eac0bdc9091fd9c29164612e8dcf5981d84d07a7860ba4", "CC-BY-4.0", "peer_reviewed", "abstractText", EPMC_SCOPE, "application/json"),
    source(f"{P}scbert", "Abstract: scBERT as a Large-scale Pretrained Deep Language Model for Cell Type Annotation of Single-cell RNA-seq Data", "https://doi.org/10.1101/2021.12.05.471261",
           f"{EPMC}TITLE%3A%22scBERT%20as%20a%20large-scale%20pretrained%20deep%20language%20model%22&format=json&resultType=core", "Europe PMC preprint record PPR/PPR428747 (title and abstract), bioRxiv 2021",
           "2026-10-11T00:59:14Z", "0a1fd6b679260955dc4382dd73b4f94f51fcf575ce0915d011913db425e99dff", None, "preprint", "abstractText", EPMC_SCOPE, "application/json"),
    source(f"{P}singlecellnet", "Abstract: SingleCellNet: A Computational Tool to Classify Single Cell RNA-Seq Data Across Platforms and Across Species", "https://doi.org/10.1016/j.cels.2019.06.004",
           f"{EPMC}DOI%3A%2210.1016/j.cels.2019.06.004%22&format=json&resultType=core", "Europe PMC core record MED/31377170 (title and abstract), Cell systems 2019",
           "2026-10-11T00:59:05Z", "83091e83e3ceb3380dea6bf03dcb491623c6fc8e5f8dde0bbd113519e94201a5", None, "peer_reviewed", "abstractText", EPMC_SCOPE, "application/json"),
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
    "note": "Approved. Checked the new sources' licences against the arXiv abstract pages and Europe PMC, the 7 scFoundation pipeline descriptions against their abstracts, the language-model descriptions against their model cards and reports, and the TAPE architecture figures against the TAPE paper; all correct. The catalogue entries reuse reviewed profile summaries.",
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
    changes = dict(CHANGES)
    for path in ["data/entities/models.jsonl", "data/entities/methods.jsonl"]:
        for line in git_lines(path):
            if not line:
                continue
            record = json.loads(line)
            if record["description"] == CATALOGUE_PLACEHOLDER:
                profile = record["attributes"]["profile"]
                assert set(profile["summary_source_ids"]) <= set(record["source_ids"]), record["id"]
                text = CATALOGUE_OVERRIDE.get(record["id"], profile["summary"])
                changes[record["id"]] = (path, text, [], f"Reviewed profile summary ({profile['review']['date']}): "
                                         f"{', '.join(profile['summary_source_ids'])}: {profile['summary_source_locator']}")
            if record["id"] == "discovery-model-tape-one-hot" or (record["name"] == "TAPE One Hot"):
                changes[record["id"]] = (path, *ONE_HOT)
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
            for s in added:
                if s not in new["source_ids"]:
                    new["source_ids"].append(s)
            assert {k for k in record if record[k] != new[k]} <= {"description", "source_ids"}
            out[i] = dumps(new)
            digest = hashlib.sha256(f"{record['id']}:description:2026-10-11-b".encode()).hexdigest()[:20]
            claims.append({
                "id": f"metadata-correction-{digest}", "kind": "claim", "name": f"{record['name']}: description",
                "description": NOTE, "status": "needs_review", "facets": record["facets"], "source_ids": new["source_ids"],
                "links": [{"relation": "subject", "target_id": record["id"]}],
                "attributes": {"field": "description", "previous_value": record["description"], "value": description,
                               "source_locator": claim_locator},
            })
            rows.append(record["id"])
        sync(path, base, out, check)
    assert len(rows) == len(changes), sorted(set(changes) - set(rows))
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
