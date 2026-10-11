# Research: independent long-read fusion caller benchmark (Dorney et al. 2026)

Use case: `use-case-tumour-rna-fusion-detection`. Pass: 2026-10-11 oncology literature search (lane `uc-oncology`), window 2025-10-01 to 2026-10-11. Ledger queries `f-q01`, `f-q02`, `f-q05`, `f-q06`, `f-q09` and lookups `f-a01`, `f-a02`.

## Why this source

The first independent benchmark of six long-read fusion callers (CTAT-LR-Fusion, FusionSeeker, GFSeeker, Genion, JAFFAL, LongGF); the authors developed none of them. It also sequences one cancer cell line (Huh7) on ONT, PacBio Kinnex and Illumina, which touches the use case's gap "No linked study compares short-read and long-read callers on the same samples". bioRxiv preprint v1 (2026-08-12), CC BY 4.0.

## What was extracted

The preprint prints its per-caller metrics only in figures; the tables in the XML are images (recommendations, read counts, library metrics). The authors' repository (MIT licence for project data, `DATA_LICENSES.md`) holds the tables behind the figures. At commit `83e629fe`:

- `Figures/Input_dataframes/stat_summary.tsv`: every cell of the 50 rows (caller by depth by read identity) for False_Point, True_Point, Precision, Recall and F1. 250 results. The FDR column (1 minus precision) and Sensitivity column (asserted identical to Recall) are not recorded; there is no FDR concept in the metric vocabulary.
- `Figures/Input_dataframes/counts_SGNex_summary.tsv.gz`: every cell of the 172 rows (caller by cell line by library by depth) for knownnumber and novelnumber. 344 results.
- Results text: the three Huh7 known-fusion counts printed for PacBio Kinnex (20), ONT PCR-cDNA (17) and Illumina (15), each for the union of callers on that platform. 3 results.

These are the source's own rows, recorded as stored; no value was computed. The run scripts and the two R scripts that write these tables are pinned in the same bundle for the read-support filter and caller versions.

## Things a reviewer should judge

1. Repository tables as printed values. They are the authors' official repository files behind the figures; the preprint text agrees where it prints numbers (CTAT-LR-Fusion recall 0.14 at 85% and 0.28 at 95% identity, and no F1 above 0.35).
2. A conflict to note: Results gives false-call counts of 632 (GFSeeker), 519 (FusionSeeker), 106 (JAFFAL) and 38 (CTAT-LR-Fusion), which match no row of `stat_summary.tsv` (at 100 Gb and 95% identity the table has 767, 704, 182 and 134). The scenario or filter behind the prose numbers is not stated. Kept as a protocol limitation; a reviewer may prefer an evidence concern on the preprint source.
3. The Spiked_Number denominator is 187 to 208 at 1 Gb and 397 at 10 Gb and 85% identity, not 400; unexplained in the source.
4. Relevance after review: simulated and Huh7 protocols `proxy`; K562 and MCF7 `direct`. The Huh7 comparison pools callers per platform, so it compares platforms, not callers. JAFFAL reuses the stored JAFFA method (reviewer-onc-2, D1).
