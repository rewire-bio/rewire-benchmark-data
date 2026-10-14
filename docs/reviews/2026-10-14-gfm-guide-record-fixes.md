# Record fixes from linking the GFM guides, 2026-10-14

Changes for rewire-benchmark-data#129, found while linking the two genomic foundation model guides to their records (release `2026-10-12-fcce59cc481b`). Prepared by a Claude research agent. This is not an independent review: every new record is `needs_review` and needs a separate `review-evidence` pass. No human review is claimed and nothing was executed.

## Duplicate model and benchmark records

The batch is `data/omics/gfm-guides-20261014-identity/`. `identity.py` in that folder writes the new claims (`batch.jsonl`) and makes the record edits listed below; it is idempotent and edits only the affected lines of the store.

Every `catalog-model-*` record below describes the same model family as its `discovery-model-*` twin. Both cite the same official artifacts and carry the same profile, and the configurations linked to the `catalog-*` record cover several checkpoints (for example Evo 2 40B and 7B, ESM-2 8M, 150M and 650M). The `catalog-*` records were linked as `variant_of` and carried one checkpoint's name as `version`, which made them read as checkpoints while holding family-level evidence. No record was deleted and no ID changed.

| Family | Canonical | Other record | Change |
| --- | --- | --- | --- |
| Evo 2 | `discovery-model-evo-2` | `catalog-model-evo-2` | New `alias_of` link and claim (`needs_review`); version `7B` removed |
| ESM-2 | `discovery-model-esm-2` | `catalog-model-esm-2` | New `alias_of` link and claim (`needs_review`); version `8M` removed |
| ESMFold | `discovery-model-esmfold` | `catalog-model-esmfold` | New `alias_of` link and claim (`needs_review`); version `v1` removed |
| DNABERT-2 | `discovery-model-dnabert-2` | `catalog-model-dnabert-2` | Reviewed `alias_of` kept; redundant `variant_of` link removed and its claim `profile-association-b98e7ae409d7f83b469e` superseded; version `117M` removed |
| SpliceAI | `discovery-model-spliceai` | `catalog-model-spliceai` | Reviewed `alias_of` kept; redundant `variant_of` removed and `profile-association-10c89dc6780906fcd514` superseded; version `1.3.1` removed |
| scGPT | `catalog-model-scgpt` | `discovery-model-scgpt` | Reviewed `alias_of` (discovery to catalog) kept; the canonical record's `variant_of` link to its own alias removed and `profile-association-507834867ec7cde103f9` superseded; version `whole-human` removed |
| GENEB | `discovery-benchmark-geneb` | `lit-genomics-20261011-geneb-benchmark-geneb` | New `part_of` link and claim (`needs_review`). Both are the darlednik/GENEB suite at commit `9642d481e40c`; the leaderboard record is its published aggregate. `alias_of` is allowed only between models, methods, configurations, pipelines and services (`shared/omics/relations.ts`), so the leaderboard joins the suite with `part_of` |

scGPT keeps `catalog-model-scgpt` as canonical because its alias is already reviewed in that direction and most scGPT configurations link to it. Reversing it would supersede a reviewed claim for no gain.

Each removed version is kept in a `metadata-correction-*` claim (`previous_value`), and the record now has `missing_metadata.version` `inapplicable` with a note. `entity_level` stays `family` on every record: with `alias_of` in place of `variant_of`, family is correct.

### Before the new alias claims are reviewed

An `alias_of` link counts in navigation only when a `source_checked` claim backs it. Until the reviewer accepts the three new alias claims and the GENEB `part_of` claim:

- Evo 2, ESM-2 and ESMFold keep their reviewed `variant_of` links, so the canonical record still rolls up the other record's results and no count drops. Each new alias claim carries a `supersedes` link to the `variant_of` claim it replaces. On accepting it, set the old claim to `superseded` and remove the `variant_of` link, as was done here for DNABERT-2, SpliceAI and scGPT.
- The GENEB leaderboard protocols' `part_of` links have no association claims, so the leaderboard results still do not roll up to either GENEB record. The linked counts below show them.

## GPN-MSA configurations

GPN-MSA had configurations but no model record; ten of them were `configuration_of` the GPN family (`regulatory-variant-20261009-model-gpn`), which is the single-sequence model. The batch `data/omics/gfm-guides-20261014-gpnmsa/` adds the model `gfm-guides-20261014-gpnmsa-model-gpn-msa` (bioRxiv 2023.10.10.561776 v2 and the songlab-cal/gpn repository at commit dc5fd287). `identity.py` repoints the ten configurations listed in that batch's `research.md` to it and adds one `needs_review` association claim per link, with the old target in `previous_value`. None of the old links had an association claim, so no reviewed rollup changes.

## Evaluations held on linked configurations

Result rollups follow only links backed by a reviewed association claim (`docs/record-contract.md`, "Explanatory profiles and supported associations"). 1,803 `configuration_of` links in the store have no such claim, which is why the list API gave 0 evaluations for HyenaDNA, Caduceus, GENA-LM and the GenBench and GENEB leaderboard records, and why the website hid configuration results on family pages that have direct results.

The engine (`shared/omics/catalogue-query.ts`) now adds `linked_evaluation_count` and `linked_result_count` to each entry of `list().evaluation_summaries`. They count results on the record and on every record linked to it by `configuration_of`, `variant_of`, `family`, `alias_of` (model subjects) or `part_of` (benchmark subjects), transitively, whether or not a claim backs the link. Each result and each evaluation is counted once. `uses_model` and `evaluates_task` are not followed. The verified counts and `results()` are unchanged, so no result is attributed to a model without a reviewed link. Serving contract 3.2 carries the new fields; on older files they equal the verified counts.

Counts on the current store (verified, then linked evaluations):

| Record | Verified | Linked |
| --- | --- | --- |
| `discovery-model-esmfold` | 14 | 32 (includes the 18 Mahtha et al. 2026 evaluations) |
| `discovery-model-alphafold-3` | 2 | 76 |
| `catalog-model-scgpt` | 3 | 191 |
| `catalog-model-geneformer` | 5 | 189 |
| `regulatory-variant-20261009-model-hyenadna` | 0 | 240 |
| `regulatory-variant-20261009-model-caduceus` | 0 | 143 |
| `lit-genomics-20261011-geneb-benchmark-geneb` | 0 | 123 |
| `lit-genomics-20261011-genbench-benchmark-genbench` | 0 | 350 |

The website change that lists these configurations on family pages with direct results is in rewire-bio/rewire-database.

Backfilling association claims for the 1,803 unbacked links is left open: each needs a source locator and review, and is out of scope here.

## Evidence cited in the guides with no record

Extracted by Claude research agents, transcription only, every record `needs_review`. Each batch folder has `batch.jsonl`, `claims.csv`, `sources.md`, `retrieval-log.md` and `research.md`; the extraction note for the reviewer and every gap are in `research.md`. All batches were added to the store with `records -- add` from their `batch.jsonl`.

| Item | Batch | Records | Main gaps |
| --- | --- | --- | --- |
| Kedzierska et al. 2025, Genome Biol 26:101 | `data/omics/gfm-guides-20261014-kedzierska2025/` | 113 evaluations, 602 results (Additional file 1 tables) | AvgBIO and average batch rows need new metric concepts; subsample columns ambiguous; figures not read |
| Kendiukhov 2026, BMC Genomics 27:634 | `data/omics/gfm-guides-20261014-kendiukhov2026/` | 20 evaluations, 20 results | The incremental AUROC differences, the paper's central numbers, need a difference metric concept; ranges not recorded |
| Evo 2 (Brixi et al., Nature 2026) ClinVar, splice, BRCA1 and BRCA2 | `data/omics/gfm-guides-20261014-evo2-brixi2026/` | 705 evaluations, 1,410 results from Supplementary Data 1 (21 models, 49 strata) | Main-text bar charts not read; Supplementary Data 1 holds the same values |
| GPN-MSA model and coding-variant evaluation | `data/omics/gfm-guides-20261014-gpnmsa/` | Model record; 53 evaluations, 104 results (Supplementary Table 4 ablation, two DMS AUROCs in the text) | ClinVar, COSMIC and DMS comparisons with ESM-1b, CADD and others are figure-only; gnomAD odds ratios need an odds-ratio concept |
| ESM-1b coding-variant pathogenicity (Brandes et al., Nat Genet 2023) | `data/omics/gfm-guides-20261014-esm1b/` | 42 evaluations, 80 results (Supplementary Table 2) | Head-to-head columns, indel and stop-gain sheets not yet extracted |
| Evo sequence generation (Nguyen et al., Science 2024) | `data/omics/gfm-guides-20261014-evo-generation/` | 2 evaluations, 2 results: 11 of 24 IS200-like and 3 of 24 IS605-like generated elements active (Results text) | CRISPR-Cas design results are figure-only |
| Mahtha et al. 2026 abstract against Table 2 | `data/omics/gfm-guides-20261014-mahtha2026-claim/` | 1 claim: abstract says 77% of dimers for AlphaFold2 and AlphaFold3; Table 2 gives 763/994 (76.8%) and 745/994 (74.9%) | None |

The issue gave the GPN-MSA preprint DOI incorrectly; the source record uses 10.1101/2023.10.10.561776.

After adding, 230 of the new evaluations had their `missing_metadata` keys in a different order from the one `normalizeAttributes` writes (`tests/attributes.test.ts`). The keys were reordered in the batch files and the store, with no value changed, and recorded with `records -- change` against this review.

## Independent review

The independent review of these batches and claims is in `docs/reviews/2026-10-14-gfm-guide-evidence-review.md`. Every batch is now `source_checked` except 120 disputed results (2 Kendiukhov CRISPRa, 114 in four Evo 2 strata, 4 Brandes text values). All 20 identity claims were accepted, and the `variant_of` follow-up for Evo 2, ESM-2 and ESMFold is done.
