# Review: issue #88 description batches a to e, 2026-10-11

Independent review of the five description batches for issue #88, `data/omics/qa-descriptions-20261011-a` to `-e`. Reviewer: Claude review agent `reviewer-desc`, which did not write any of these batches. The batches were written by the Claude integrator agent, which also integrated them and wrote this record of the review. No human review is claimed.

Each batch replaces placeholder or category-only descriptions with one functional sentence taken from a source, keeps the old text in a `metadata-correction-*` claim, and adds a source record where no cited source described the method. Each folder holds `build.py` (which reproduces the store edits and `batch.jsonl`), `changes.md` (every change with its source passage), `gaps.md` and the receipt `review.json`, which binds the SHA-256 of every other file in the folder.

## Outcome

| Batch | Records changed | New sources | Verdict |
| --- | --- | --- | --- |
| a | 59 (49 mRNABench linear-probe pipelines, 8 named prediction methods, DeepAffinity, DeepDTA) | 3 | Approved; one optional wording change, applied |
| b | 51 (26 catalogue candidates, 10 language models, 7 scFoundation pipelines, 2 FoldBench models, 6 TAPE records) | 12 | Approved |
| c | 41 (29 "Identity as reported" pipelines, 6 scTab methods, 6 MPRabc methods) | 0 | Approved |
| d | 27 (23 ddG predictors, 4 conservation or selection scores) | 7 | Approved |
| e | 38 (missense variant-effect predictors) | 11 | Approved with two corrections, both applied |

216 records changed in total. In every batch the reviewer compared the store with origin/main and found that only `description` changed, plus appended `source_ids` where a batch adds a source (4 records in a, 23 in b, 7 in d and 11 in e). No ID, number or other field changed, and every referenced source ID resolves.

## What was checked

- **a.** The 10 method and model descriptions against their sources: the EVmutation, GEMME and RSALOR abstracts, the FramePool k-mer random forests and the RhoMax BLASSO text. All accurate. The 49 mRNABench rows were spot-checked against mRNABench Appendix A (Evo, NT-v2, naive baselines, Orthrus, SpliceBERT, UTR-LM, AIDO.RNA, mRNA-FM, Helix and others); all match. The licences of the 3 new sources match Europe PMC: GEMME CC BY-NC 4.0, RSALOR CC BY-NC-ND 4.0 (bioRxiv), Hopf 2017 none, with the missing-metadata note.
- **b.** The licences of the new sources against the arXiv abstract pages and Europe PMC: GPT-4o, o1 and gpt-oss CC BY 4.0; Llama 3 and Qwen2 the arXiv non-exclusive licence; CellTypist, Scanpy and scANVI CC BY; ACTINN, SingleCellNet and the Claude 3 model card none, each marked unreported. The 7 scFoundation pipeline descriptions against their abstracts, the language-model descriptions against their model cards and reports, and the TAPE architecture figures against the TAPE paper. All correct. The catalogue entries reuse reviewed profile summaries.
- **c.** All 11 scTab and MPRabc method descriptions against PMC11298532 and PMC13232518 (CIForm, linear, MLP, XGBoost, the UCE linear probe, scTab normalisation and observation-wise attention, megamap Hi-C, L2 logistic regression, the Sei and MPRALegNet ablations, the ABC definition). Also Lazypipe-nt, scaLR, CATHe2, DiffDock-NMDN, PC-mer with L2 logistic regression and Hi-Enhancer. All match. The other pipeline descriptions are consistent with their pinned papers.
- **d.** The 16 descriptions taken from Pancotti 2022, word for word against PMC8921618 section 2.2. ESM therm, RaSP and ELASPIC-2 against Chu 2024, ThermoMPNN against Dieckhaus 2024, ABYSSAL and phyloP against their abstracts. All match. Licences: PROSTATA, Stability Oracle, GERP++ and the B-statistic paper are CC BY 4.0 (Europe PMC says "cc by"; the PMC XML for the B-statistic paper and Crossref for GERP++ give 4.0). ABYSSAL, phastCons and phyloP are unreported with a missing-metadata note, which is correct.
- **e.** The 27 Chen 2020 descriptions row by row against Table 1 (PMC7033911), including the paired FATHMM, Eigen, PolyPhen-2 and CTAT rows. All match. AlphaMissense, MisFit, popEVE, VARITY, MetaRNN, MutFormer and gMVP were spot-checked against their abstracts; accurate. Licences on the other new sources match Europe PMC: LIST-S2 and PHACTboost CC BY-NC, MetaRNN and VARITY CC BY, MisFit, MutScore and popEVE CC BY-NC-ND; AlphaMissense, ClinPred and gMVP are not open access and are marked unreported.

## Corrections applied at integration

1. Batch e, `qa-descriptions-20261011-e-source-mutformer` (arXiv:2110.14746): the licence was recorded as unreported, but the arXiv abstract page shows CC BY 4.0. It is now `CC-BY-4.0`, which also matches how batch b recorded arXiv licences.
2. Batch e, `qa-descriptions-20261011-e-source-metarnn`: the source locator was "Abstract", but the description's flanking-codon and bidirectional-GRU detail comes from the Background of PMC9548151. The locator is now "Abstract; Background (flanking ±1 codon annotations read by bidirectional GRUs)", on the source and on the MetaRNN correction claim.
3. Batch a, optional: the source table prints some checkpoint names with an en dash (evo-1-8k-base, evo-1-131k-base, evo-1.5-8k-base, evo2-1b-base, evo2-7b, evo2-7b-base and the nt-v2 checkpoints). The descriptions now write a hyphen. The record names are unchanged.

The reviewer also noted, with no change needed, that the HelixFold 3 and Protenix descriptions in batch b are identical ("Open-source reproduction of AlphaFold 3 ..."); both are accurate.

## Recording

Every record in the five `batch.jsonl` files (59 + 51 + 41 + 27 + 38 correction claims and 33 sources) is `source_checked` with a `review` block naming this review and the folder's `review.json`. Each `build.py` now reads its originals from the commit the batches were integrated on (`47a06e9`), and its `--check` compares only the records it changes, so the five scripts verify one shared store. The 216 target records are identical at that commit and at the commit the batches were written against (`cc9d628`).

## Gaps

- 6 language models in batch b have no findable primary source and keep their old description (`qa-descriptions-20261011-b/gaps.md`).
- 6 excluded model records in the "Identity as reported in this paper" group were skipped (`qa-descriptions-20261011-c/changes.md`).
- Some Europe PMC full texts and search responses no longer reproduce their pinned bytes; each batch's `changes.md` lists them, and their `hash_scope` states that these responses are not byte-stable.
- The 22 mostly-provenance, 75 thin and 74 stylistic descriptions in `qa-descriptions-20261011/scan.md` are not part of these batches.

## Limitations

- An automated review by a Claude agent, not human scientific review.
- Descriptions were checked against the cited passages and abstracts, with the mRNABench and pipeline groups spot-checked rather than read in full.
