# Review: tumour RNA fusion citation year and depth ratio, 2026-10-12

Reviewer: a separate Claude review agent, independent of the agent that made the change. No human review is claimed.

Verdict: approved as made. Seven metadata-correction claims in `data/omics/qa-fusion-citation-20261012/batch.jsonl` are set to `source_checked`.

## 1. Scope of the diff

Compared the five changed store files with origin/main `e79f7a5` record by record. Six records differ, and only in the fields the claims name:

| Record | Field | Change |
| --- | --- | --- |
| `rna-fusion-leukaemia-20261011-config-arriba-2-4-0-igv-review` | `name` | Kim et al. 2025 to 2026 |
| `rna-fusion-leukaemia-20261011-protocol-conventional-diagnostics` | `name` | Kim et al. 2025 to 2026 |
| `use-case-tumour-rna-fusion-detection` | `attributes.evidence_gaps[10]` | Kim et al. 2025 to 2026 |
| `use-case-mapping-rna-fusion-leukaemia-20261011-conventional-diagnostics` | `name`, `attributes.comparison_title` | Kim et al. 2025 to 2026 |
| `use-case-summary-tumour-rna-fusion-detection` | `attributes.value` | Kim et al. 2025 to 2026; "one tenth of the depth" to "one eighth of the depth" |
| `rna-fusion-leukaemia-20261011-eval-arriba-conventional-diagnostics` | `name` | Kim et al. 2025 to 2026 |

Line counts and record order are unchanged. Each claim's `previous_value` equals the origin/main field exactly, and each `value` equals the working-tree field exactly. No "Kim et al. 2025" remains in the canonical store; the old text survives only in earlier batch folders, ledgers and reviews, which are historical and are not edited. Record IDs, including the source ID `rna-fusion-leukaemia-20261011-source-kim2025`, are unchanged.

## 2. Kim citation year

Crossref for 10.3343/alm.2025.0300: Annals of Laboratory Medicine volume 46, issue 3, pages 257-269; `published-online` 2025-10-16, `published-print` 2026-05-01. Crossref's `issued` date is the online date, 2025.

2026 is the volume and print year. The store mostly cites sources published online in one year and in print the next by that year:

- You et al. 2026: Nat Commun 17:223, published online 2025-12-07.
- Dalla-Torre et al. 2025: Nature Methods 22, published online 2024-11-28.
- `structure-informed-plm-2025`: Human Genetics 2025, online 2024, with `year` 2025.

One exception exists: Drost et al. 2025 (HGG Advances 7(1), published online 2025-09-22) is cited by its online year. It is outside this change and noted here as a possible follow-up.

## 3. Lin depth ratio

The Lin et al. 2026 dataset record `rna-fusion-20261009-data-lin2026-ball-nanopore` gives mean 11.2 M reads (high-depth cohort) and 1.4 M reads (low-depth cohort). I re-downloaded the Lin full-text XML (PMC13197905); its SHA-256 matches the source record. The abstract reports "mean of 11.2 and 1.4 million reads, respectively", and Results repeat both figures. 1.4 / 11.2 = 0.125, one eighth. "One tenth" was wrong.

## 4. Use-case effects

The protocol `name` is pinned by the Kim relevance judgement, so the change withholds that judgement until it is re-pinned. The judgement's endpoint, relevance, rationale and evaluations are unchanged; only the citation year in two labels differs, so I re-pinned it against this review. The summary's pins do not cover the changed fields, so `use-cases:repin` left them as they were; I reviewed its changed text here, and the change is recorded in provenance against this review.

Every judgement on `use-case-tumour-rna-fusion-detection` that was active on origin/main is active after the change, and the summary is still reviewed (checked with `deriveUseCaseInputs`).
