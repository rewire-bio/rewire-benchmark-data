# Research: Zheng et al. 2026, accelerated Clair3 (Bioinformatics 42(5), btag181)

Use case: `use-case-diagnostic-genomics-model-execution`. Pass: diagnostic genomics execution literature search, window 2025-10-01 to 2026-10-11. The search log, candidates and gaps for the whole pass are in `data/omics/lit-search-20261011-uc-execution/` (ledger, scope audit and report).

Selected because it is the only source found in the window that prints runtime, peak memory and accuracy for the same sample, platform and coverages, for a deep-learning variant caller and a competitor in GPU mode. It was an open lead in the 2026-10-09 ledger (`search-use-case-model-execution-genomics-q4`: "Long-read deep-learning caller runtimes (Clair3 GPU 2026) not opened").

Modelling:
- New model families `model-clair3` and `model-deepvariant` (no DeepVariant model record existed; earlier DeepVariant runs are Parabricks configurations).
- Configurations: Clair3 v1.2.0 GPU and DeepVariant v1.10-beta GPU for Supplementary Tables 1 and 2; three version-less configurations for Supplementary Table 3 (Clair3, Clair3 pileup, DeepVariant), because that table names no version and the text and supplement disagree on the DeepVariant version.
- Protocols: one per table and platform (Table 1 has one protocol over both platforms). Results carry the coverage in `metric_qualifier`, so comparisons pair the same coverage.
- Origin: Clair3 evaluations `author_reported` (the authors develop Clair3); DeepVariant evaluations `independent_paper`.
- All five judgements are drafted as `proxy`; see the limitations on each protocol.

Things a reviewer should judge:
1. Results 3.1.1 and 3.1.2 give runtimes for apparently the same comparisons that differ from Supplementary Table 2 (ONT 30x: Clair3 GPU 16 minutes in the text, 17 in the table; DeepVariant GPU 106 to 128 minutes in the text, 48 and 82 at 30x and 50x in the table) and name DeepVariant v1.8, while the table and command lines give v1.10-beta. The text likely describes Figure 2a runs, a different set. Whether this needs a source-level `evidence_concerns` entry (which would withhold every judgement citing the source) or only the protocol limitation recorded now.
2. Results 3.2 DeepVariant accuracy at ONT 10x and 20x (SNP F1 94.68% and 98.79%) differs from Supplementary Table 3 (94.89% and 99.17%).
3. Supplementary Table 1 prints both a LongPhase and a WhatsHap phasing column; the total equals the sum with LongPhase (500 + 72 + 396 + 87 = 1,055 against 1,056 printed for ONT 30x).
4. Whether the Table 2 memory figures are host or GPU memory (unstated), and the new metrics `mean-memory` and `data-io-volume` and unit `megabyte`.
5. `proxy` against `direct` for the two resource protocols.

## Records

| Kind | Count |
| --- | --- |
| claim | 6 |
| configuration | 5 |
| dataset | 2 |
| evaluation | 12 |
| model | 2 |
| protocol | 5 |
| result | 374 |
| source | 2 |
