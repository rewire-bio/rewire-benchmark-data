# Research: tumour RNA fusion detection use-case pass, 2026-10-09

Use case: `use-case-tumour-rna-fusion-detection` ("Which RNA-sequencing workflow detects and prioritises tumour gene fusions with useful sensitivity and a manageable false-positive review burden?"). It already had two judgements from one paediatric source (Seraseq reference and NCH cohort; Arriba, STAR-Fusion, EnFusion).

Bounds: cutoff 2026-10-09; budget 25 queries, 6 used; at most 3 sources, 2 extracted. Lane `rna`. Ledger IDs `search-use-case-rna-fusion-rna-q1` to `-q6`.

## Queries

| # | Query (abridged; exact strings in the ledger) | Channel | Outcome |
| --- | --- | --- | --- |
| 1 | fusion callers (STAR-Fusion, Arriba, FusionCatcher, JAFFA, CICERO, JAFFAL, LongGF) with benchmark or comparison | Europe PMC REST | Tamura et al. 2026 selected; CTAT-LR-Fusion screened |
| 2 | TITLE "Accuracy assessment of fusion transcript detection" | Europe PMC REST | Haas et al. 2019: accuracy in figures only |
| 3 | long-read fusion callers with benchmark or comparison | Europe PMC REST | Lin et al. 2026 selected |
| 4 | DREAM SMC-RNA fusion challenge | Europe PMC REST | Cell Systems 2021 not retrievable |
| 5 | adult or solid-tumour cohorts with orthogonal validation | Europe PMC REST | Br J Cancer 2026 and BMC Cancer 2025 screened; no printed per-caller table |
| 6 | title search, fusion caller comparison in solid tumours or FFPE | Europe PMC REST | Nothing usable |

## Decisions

| Source | Decision | Reason |
| --- | --- | --- |
| Tamura et al. 2026, NPJ Precis Oncol, Supplementary Tables 1, 3 and 5 | Extract every cell of Tables 3 and 5 (288 results); Table 1 for versions | 12 short-read callers, independent group, 170 + 26 haematologic cell lines; validated driver truth (Table 5) and consensus truth with false-positive counts (Table 3), the review-burden endpoint |
| Lin et al. 2026, J Mol Diagn, Tables 3 and 6 | Extract every cell (32 results); Table 5 as a claim | Four long-read callers on real paediatric B-ALL with clinical subtypes at two depths; one caller is the authors' |
| Haas et al. 2019 | Lead | Values would need recomputation from prediction lists |
| CTAT-LR-Fusion 2025 | Excluded | Developer paper; accuracy in figures |
| DREAM SMC-RNA 2021 | Gap | Not retrievable |
| Br J Cancer 2026 | Lead | Adult FFPE solid tumours; per-caller values only in figures |

## Modelling choices

- One protocol per truth definition and assay: Tamura driver and all-fusion analyses on conventional and targeted RNA-seq (4); Lin high and low depth (2). One judgement each.
- Relevance: the four driver and long-read protocols are `direct`. The two all-fusion protocols are `proxy`, because their truth is a consensus of the other callers and their false positives are single-caller calls; they are kept because they show the false-positive review burden the question asks about.
- Page groups: `tamura2026-driver` and `tamura2026-all` (strata conventional, targeted), `lin2026-longread` (strata high, low depth). Headline metric recall, except F1 for the consensus analysis.
- Methods are caller families; configurations carry the version printed in Tamura Supplementary Table 1. Lin et al. print no versions (missing reason `unreported`).
- 'na' cells are kept as printed with `numeric_value` null and an `undefined_reason`.
- Area facet `rna-transcriptomes` for new records (the use case itself carries `dna-genomes`).

## Things a reviewer should judge

1. Whether the all-fusion consensus protocols should be `proxy` or `outside_scope`.
2. The driver truth set's dependence on four-caller agreement (it does not exclude the evaluated caller).
3. FUSILLI as an author-reported comparator limited to its own B-ALL gene list.
4. The proposed setting and decision text, which would withhold the two existing judgements until re-pinned.

## Coverage

Bounded pass. Not covered: adult solid tumours and FFPE with printed per-caller values, DREAM SMC-RNA, short- and long-read callers on the same samples, Tamura clinical samples (figure-only), novel-fusion discovery.
