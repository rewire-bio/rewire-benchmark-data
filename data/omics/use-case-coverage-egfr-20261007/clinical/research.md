# Clinical use-case evidence audit — EGFR NSCLC evidence-retrieval bounded ingestion, 2026-10-07

Scope: `use-case-egfr-nsclc-actionability-resistance-evidence` (B345/BL345, rewire-benchmarks #25; focused execution gap rewire-benchmarks #28; article plan rewire.it #345; programme rewire-benchmark-data #3). This is a bounded, additive intake following a two-cycle independent Codex review of the underlying research dossier (`docs/omics/evidence-research/egfr-nsclc-evidence-retrieval-2026-10-07.md`).

## What is added

CIViC-Fact v3 (bioRxiv doi:10.1101/2025.09.10.675443, posted 2026-08-29) is added as a second pan-cancer proxy for this use case, alongside the existing CIViC MCP proxy (`use-case-mapping-20260930-345-ba1ec69965eb`, unchanged). The added evidence is the source's own post-cutoff temporal-evaluation passage-retrieval result: 150 CIViC entries submitted or revised 2026-03-03 to 2026-06-09, reduced by sequential, source-defined exclusions (68 full-text inaccessible, 14 already present in the train/dev/test data, 2 non-content data errors, 24 requiring supplementary material or images, 2 substantially revised claims) to 40 scored entries. Both evaluated retriever configurations — a fine-tuned MedCPT cross-encoder and a pretrained (not fine-tuned) Qwen3-Reranker-8B — retrieved appropriate content, per manual curator review, for 37 of the 40 (92.5%). This is one temporal cohort scored under two configurations, not two independent cohorts, and involves no new execution by Rewire.

Passage retrieval here ranks candidate text within the single publication CIViC already links to each claim. It does not search an open literature corpus to find which study is relevant to an EGFR-NSCLC clinical question, and does not establish any EGFR- or NSCLC-specific score — the cohort carries no such tag. It is not a clinical efficacy result, and it is not the static SUPPORTS/REFUTES/NEI stance-classification accuracy (89% gold-evidence / 85% retrieved-evidence) or the v2-era BGE retriever manual-review figure (70/75) reported elsewhere in earlier versions of the same preprint; those are distinct, version-specific measurements under a different task schema and are not ingested here.

## What is not added

No new source or mapping record is created for CIViC MCP (doi:10.1093/bioadv/vbag209; Zenodo archive 10.5281/zenodo.20938836); it is already catalogued as of 30 September 2026 and its records are referenced, not duplicated, here. No attributes are appended to the existing `uc-clinical-20260930-civic-100-data` dataset record; the EGFR-triplet field facts discussed in the research dossier remain dossier-only observations and are not promoted into the catalogue by this pass.

## Version reconciliation

The cached PMC12458922 copy used in the prior research pass is bioRxiv v2 (posted 2025-09-15). The primary source catalogued here is bioRxiv v3 (posted 2026-08-29), under the same DOI but a different title and author list. v3's Table 2 reports evidence-retrieval document/entry counts (907/99/88 CIViC entries in the retrieval section) that are a different unit from the Methods-stated retrieval-subset example counts (n_train=3456/n_dev=1194/n_test=1120); this pass does not resolve that apparent unit discrepancy by inference and does not ingest either figure, since neither is the post-cutoff cohort result being added here.

## Independent review

Codex independently inspected the cached v3 PDF text and visually checked Supplementary Figure 2 (printed page 33 / PDF page 34), confirming the exact 150→66→42→40 selection chain and the 9/7/24 scored-entry breakdown. Codex also independently confirmed via EuropePMC/Zenodo API that the CIViC MCP published article and its Zenodo 20938836 archive are already catalogued, and created the focused execution-gap issue rewire-benchmarks #28 after a full title/body dedup check. This pass reconciles the dossier and intake materials to that issue without duplicating it.
