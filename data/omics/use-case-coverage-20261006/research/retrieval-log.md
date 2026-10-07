# Retrieval log

2026-10-06: this additive-intake pass performs no new literature search. The two facts ingested here
(scTab deep-ensemble uncertainty ROC-AUC values 0.782 and 0.891) were located during the bounded,
dated search already recorded in `docs/omics/evidence-research/cell-type-annotation-transfer-2026-10-06.md`,
which retrieved `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11298532/fullTextXML` at
2026-10-06T12:16:47Z (SHA-256 `e61b11cd873f3d13e891e9c33bac0847070826200f8fbe0b3969d994f1c52290`).

This ingestion pass re-verified that fetch is byte-identical to an independent re-fetch of the same
URL performed by a separate reviewer into `workbench/source-review-20261006/PMC11298532.xml`
(gitignored, not part of this release) before transcribing the two values into catalogue records.

## 2026-10-06, same-day continuation: Abdelaal et al. 2019 (Baron Human, intra-dataset) ingested; scArches re-checked and held

No new literature search was performed for this continuation either. Both candidates were already
identified in the 2026-10-06 research dossier; this pass re-checked each against the cached primary
text before deciding whether to ingest.

- Re-fetched/re-verified: `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6734286/fullTextXML`
  (Abdelaal et al. 2019), SHA-256 `6df0937c5a2d8ba06465ba356c2321fb9f52d9ecf23456876acd82f828b41d4c`,
  verified byte-identical against `workbench/source-review-20261006/PMC6734286.xml` (gitignored) at
  2026-10-06T22:58:14Z. Re-read Methods ("Intra-dataset classification," "Inter-dataset classification"),
  Results ("Benchmarking automatic cell identification methods (intra-dataset evaluation)"), Table 1,
  Table 2, and the Table 2 footnotes ("a Used for intra-dataset evaluation", "b Used for inter-dataset
  evaluation") to confirm the Baron Human dataset's intra-dataset scope and exact population (8,569
  cells, 17,499 genes, 14/13 cell populations, inDrop) before ingesting. **Ingested**: four median
  F1-score values and three cells-left-unlabeled percentages, all explicitly intra-dataset.
- Re-read: `workbench/source-review-20261006/PMC8763644.xml` (Lotfollahi et al. 2022 / scArches, SHA-256
  `6b746e28e26ea717160045d869fe426de23afc6b53d95e2581a0d5b431c191c4`, already catalogued as checked-but-
  not-ingested in the research dossier) and its supplement
  (`workbench/source-review-20261006/PMC8763644_supp1.txt`). Searched specifically for an explicit
  accuracy-formula definition applicable to the headline "~84% accuracy" figure (Fig. 4c). Found one
  explicit formula, but for a *different* figure (Supplementary Fig. 17: "the accuracy (#correct/#all_cells)
  ... calculated for all cells **excluding trachea**") -- the unseen-tissue cells are explicitly excluded
  there, whereas Fig. 4c's own text ("~84% accuracy **across all tissues**") does not state whether its
  denominator excludes cells labelled "unknown." No formula statement was found attached to Fig. 4c
  itself. **Not ingested**; recorded as unresolved (see `research.md`).

## 2026-10-06/07, independent review and provenance correction

An independent review found four issues in the Abdelaal ingestion above, all now corrected directly in
`records.jsonl` (byte-identical scTab lines 1-6 preserved exactly; only the Abdelaal records, lines
7-27, were rewritten):

1. **Invented precision in `retrieved_at`.** The research dossier explicitly states individual
   per-file retrieval timestamps were not logged for the five-source batch fetch, only the bounded
   window 12:16:47Z-12:18:28Z UTC. The prior version of this ingestion used the window's end,
   `2026-10-06T12:18:28Z`, as Abdelaal's own `retrieved_at` value -- an invented exactness the source
   data does not support. **Corrected**: re-fetched `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6734286/fullTextXML`
   directly in this review pass, request started `2026-10-06T23:28:54Z` UTC (an actual, logged
   timestamp), response SHA-256 `6df0937c5a2d8ba06465ba356c2321fb9f52d9ecf23456876acd82f828b41d4c` --
   byte-identical to the earlier cached copy, confirming no version drift. `retrieved_at` now records
   this real fetch time.
2. **Stable, committed cache path.** The source record's `local_cache_path` previously pointed only to
   `workbench/source-review-20261006/PMC6734286.xml`, which is gitignored and not part of any release
   artifact. **Corrected**: the re-fetched bytes are archived as a committed, gzip-compressed artifact
   at `data/omics/use-case-coverage-20261006/research/artifacts/abdelaal-2019-pmc6734286-fulltext.xml.gz`
   (tracked in version control; round-trip SHA-256 verified identical), referenced from the source
   record via a new `review_artifact` attribute, matching the `review_artifact` convention already used
   elsewhere in this repository (e.g. `data/omics/reviewed/protocol-evidence-2026-09-23/retrievals.json`).
3. **`metric_direction` on the three unlabeled-percentage results.** These were recorded as `"lower"`
   (lower unlabeled % = better), which asserts a universal direction the metric does not have: percentage
   unlabeled is a coverage/rejection-rate choice, not a standalone performance figure -- a classifier can
   reduce it by accepting more low-confidence calls, which may raise or lower its own median F1-score
   depending on whether those calls are correct. **Corrected** to `metric_direction: "unknown"`, the
   schema's own third value for exactly this case (`services/omics/src/validation.ts`: `["higher",
   "lower", "unknown"]`; no new value was invented). Each result's `scope_note` and the protocol's
   `limitations` now state the F1/rejection tradeoff explicitly: percentage unlabeled must be read
   jointly with the same classifier's median F1-score, not in isolation.
4. **8,569-cell denominator.** Table 2 states 8,569 cells for the Baron Human dataset overall; this was
   being used as if it were also the confirmed exact scored denominator for each classifier's median F1
   or unlabeled-percentage result. **Corrected**: the dataset and protocol/evaluation records now state
   explicitly that 8,569 is the Table 2 dataset-size figure, not independently confirmed as the exact
   per-classifier scored denominator (per-fold or per-classifier exclusions, if any, are not detailed in
   the retrieved main text).

No printed value (0.991/0.984/0.981/0.980 median F1; 1.5%/4.2%/10.8% unlabeled) changed. All six scTab
records and all prior mappings/records remain byte-identical; only the 21 Abdelaal records were
rewritten, and only for the four items above.

Other candidate sources identified in the research dossier (Hao et al. 2021, Xu et al. 2021, Domínguez
Conde et al. 2022, Chechekhina et al. 2026/scParadise) remain explicitly **not** ingested; see
`workbench/cell-type-ingestion-plan.md` (gitignored) for which of those facts are independently
checkable candidates for a future pass and which must stay unresolved.
