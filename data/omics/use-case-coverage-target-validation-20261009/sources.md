# Sources: therapeutic target validation use-case pass, 2026-10-09

Hashes are SHA-256 of the exact bytes read. Times are UTC. All three sources are CC BY 4.0, so their bytes may be redistributed, but none is archived in the batch: the three PDFs are 3.95 MB, 0.48 MB and 2.89 MB, and the repository keeps releases small. The `artifact_sha256` on each source record pins the bytes that were read, and each source record says so in `archive_note`.

| Source ID | What | Version | Retrieved | Artifact URL | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `tgtval-20261009-source-roohani2025` | Roohani et al., BioDiscoveryAgent: An AI Agent for Designing Genetic Perturbation Experiments | arXiv:2405.17631 version 3, updated 2025-03-09; published at ICLR 2025 | 20:51:27 | https://arxiv.org/pdf/2405.17631v3 | `dd94d80ec75c9bb84ec3989c910a313ef1a7aec57c772d3dd35ecadd250132a7` |
| `tgtval-20261009-source-gupta2025` | Gupta, Hartford and Liu, LLMs for Bayesian Optimization in Scientific Domains: Are We There Yet? | Findings of the ACL: EMNLP 2025, pages 15482-15510 | 20:55:36 | https://aclanthology.org/2025.findings-emnlp.838.pdf | `7dda0b590f2736b7d30e48b97167a0868a2b4bde253589d8aff7929d01506ff9` |
| `tgtval-20261009-source-debrouwer2026` | De Brouwer et al., AssayBench: An Assay-Level Virtual Cell Benchmark for LLMs and Agents | arXiv:2605.10876 version 1, posted 2026-05-11; not peer reviewed | 20:56:07 | https://arxiv.org/pdf/2605.10876v1 | `805b402c28e0daa186415af202e04df56bf0cd7c7b1f872a6db170ee3c6c623d` |

Licences as stated by each host: both arXiv abstract pages declare CC BY 4.0; the ACL Anthology page for the Gupta paper declares CC BY 4.0. The DOI recorded on the Gupta source is its arXiv preprint (arXiv:2509.21403) of the same work, noted in `version_note`, because the bytes read are the ACL version of record.

## No evidence concerns

No source carries an `evidence_concerns` entry. Three printing or interpretation points are recorded on the records themselves rather than as source concerns, because none is a transcription problem inside one source:

| Where | What |
| --- | --- |
| `tgtval-20261009-protocol-roohani2025-hitratio-round5`, `limitations` | Gupta et al. report that the same agent scores the same when its experimental feedback is replaced by randomly permuted outcomes. This bears on how the Roohani numbers should be read; both sets of numbers are stored as printed. |
| Gupta `GP` results, `source_anomaly` | Table 2 prints identical Gaussian-process values for the Llama-3.1-8B and Qwen-2-7B blocks, although the embeddings differ between backbones. |
| `tgtval-20261009-protocol-debrouwer2026-screen-gene-ranking`, `limitations` | Precision@100 divides by `min(100, positive-relevance genes)`, so it is not precision over a fixed 100 predictions when a screen has fewer than 100 hits. |

## Cross-source check recorded as a claim

`tgtval-20261009-claim-gupta2025-reported-numbers-conversion` records that Gupta's "BDA (Reported Numbers)" row divided by its printed ground-truth hit counts reproduces Roohani's all-gene hit ratios for Claude 3.5 Sonnet to the printed rounding on all four shared screens. This indicates both sources score against the same screens and hit sets.

## Reused records

None. The two existing judgements on this use case rest on the Cancer Immunotherapy Data Science Challenge records (`ucc-research-*`), which are a different benchmark; nothing in them matches these three sources.
