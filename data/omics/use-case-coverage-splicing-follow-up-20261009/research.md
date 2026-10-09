# Research: splicing follow-up use-case pass, 2026-10-09

Use case: `use-case-splicing-follow-up` ("Which evaluated configurations can inform selection of human SNVs for follow-up splicing experiments?"). Existing judgements, all `proxy`: MFASS v2 ranking and top-100 precision, DNA foundation-model acceptor and donor AUC (Feng), and the matched-annotation MFASS study. Exclusions: indels; patient-RNA effects, pathogenicity and diagnosis; pooling the matched MFASS study with historical runs.

Bounds: cutoff 2026-10-09; budget 25 queries, 5 used; at most 3 sources extracted. Lane `rna`. In scope: independent comparisons of several splice predictors on experimentally measured human SNV splicing effects (reporter or minigene assays, saturation mutagenesis, genome editing), with printed per-method values. Patient-RNA evidence from the parallel patient-RNA pass is not reused.

## Queries

| # | Time (UTC) | Query | Channel | Outcome |
| --- | --- | --- | --- | --- |
| 1 | 20:49:18 | `(SpliceAI OR MMSplice OR Pangolin) AND ("massively parallel" OR MFASS OR "Vex-seq" OR MaPSy OR "saturation mutagenesis" OR minigene) AND (benchmark OR comparison OR "performance") AND (splicing) AND PUB_YEAR:[2019 TO 2026]` | Europe PMC REST | 388 hits; Smith and Kitzman 2023 (PMC10734170), Znabu et al. MFASS preprint, Genome Biol 2026 distillation paper, OpenSplice preprint |
| 2 | 20:51:13 | `(CAGI5 OR CAGI6 OR "Vex-seq" OR MaPSy) AND (splicing) AND (assessment OR challenge OR prediction) AND PUB_YEAR:[2018 TO 2026]` | Europe PMC REST | 77 hits; CAGI5 assessment (PMC6744318), CAGI6 assessment (patient RNA, out of scope here) |
| 3 | 20:51:51 | `DOI:10.64898/2026.07.21.739871` (core result type) | Europe PMC REST | Znabu et al. authors and abstract; independent of the tool developers |
| 4 | 20:51:51 | `(Riepe OR ABCA4 OR "midigene") AND (SpliceAI OR MMSplice OR "deep learning") AND (splice) AND (benchmark OR benchmarking) AND PUB_YEAR:[2020 TO 2026]` | Europe PMC REST | 30 hits; Riepe et al. 2021 (PMC8360004) |
| 5 | 20:58:20 | `(CFTR OR BRCA1 OR BRCA2 OR MST1R OR "saturation genome editing") AND (minigene OR "splicing assay") AND (SpliceAI AND (Pangolin OR MMSplice OR SQUIRLS)) AND (sensitivity OR AUC OR "precision") AND PUB_YEAR:[2021 TO 2026]` | Europe PMC REST | 15 hits; SeqSplice (Genome Res 2025) and SPiP (Hum Mutat 2022) as leads; no new independent saturation comparison |

## Decisions

| Source | Decision | Reason |
| --- | --- | --- |
| Smith and Kitzman 2023, Genome Biology, Additional file 3 sheet 'Sensitivity 10% SDV' | Extract all cells | Independent comparison of 8 predictors on four saturation minigene MPSAs, BRCA1 saturation genome editing and a curated MLH1 set, by variant class. prAUC per dataset is figure-only, so the printed transcriptome-normalised sensitivity is the decision-relevant table |
| Smith and Kitzman other Table S2 sheets and Table S3 | Not extracted | 5% and 20% call-rate sheets and the sensitivity-AUC sheet repeat the design; left out to keep the batch lean |
| Riepe et al. 2021, Human Mutation, Tables 3-5 | Extract all cells | Independent comparison of 11 tools on ABCA4 and MYBPC3 variants with mini- or midigene results; full confusion matrices printed |
| Znabu et al. 2026, bioRxiv preprint, Results table | Extract all cells | Independent head-to-head of Pangolin, SpliceAI, SpliceTransformer, MMSplice and SPANR on all labelled MFASS SNVs with bootstrap intervals |
| CAGI5 splicing assessment (Mount et al. 2019) | Not extracted; lead | Per-submission correlations and AUCs for challenge entries; most entries are not released tools. Author-manuscript licence (fair use) |
| CAGI6 splicing assessment (PMC11976748) | Excluded here | Patient-RNA VUS challenge; belongs to the patient-RNA use case |
| Genome Biol 2026 distillation paper (PMC13495316) | Lead | Tables only in Additional file 1; not opened |
| PLoS One 2026 (PMC13170886) | Lead | SpliceAI-family tools only |
| OpenSplice preprint, SeqSplice (Genome Res 2025) | Leads | Not screened for per-tool tables |

## Modelling choices

- Each Smith and Kitzman dataset is its own protocol (different assay and exon); variant class (all, exonic, intronic, intronic excluding essential splice sites) is the `metric_qualifier`. The six judgements share one comparison group.
- Riepe has one protocol per table (ABCA4 noncanonical, ABCA4 deep intronic, MYBPC3 noncanonical).
- The Znabu evaluations reuse `rewire-mfass-v2-dataset` as data, but have their own protocol. They must not be pooled with `rewire-mfass-v2` or `rewire-mfass-matched-v1-protocol`.
- Relevance: `proxy` for every assay-based protocol, matching the reasoning of the four existing MFASS and Feng judgements (assay-measured endpoint; transfer to another experiment not established). The MLH1 column is `outside_scope` because its labels mix patient blood RNA, minigene results and a pathogenicity rule. A reviewer may prefer `direct` for the assay sets; the rationale is recorded in each claim.
- Metric concepts: `negative-predictive-value` copied byte for byte from the RNA pathogen branch; `true-negative-count` added (STATO_0000597) for Riepe's TN column.
- All evaluations are `independent_paper`: none of the authors developed the tools compared. Whether Smith and Kitzman also produced any of the benchmark MPSA datasets was not checked; that would be a dataset link, not a tool link.

## Things a reviewer should judge

1. Riepe Tables 3-5 do not state the cutoff; Table 2 cutoffs are ROC-optimal on the same data. Recorded as a limitation and `missing_metadata`, not an evidence concern.
2. Riepe selection: ABCA4 variants were chosen with Alamut tools, MYBPC3 with MaxEntScan; both favour the tools used for selection.
3. Smith and Kitzman: SpliceAI benchmark scores are from 1.3.1, but its background threshold used 1.3 precomputed scores. Masking for SpliceAI and Pangolin in Table S2 is not stated.
4. The prose medians (SpliceAI 87.3%, ConSpliceML 85.8%, Pangolin 79.9%) agree with the 'all variants' row of the extracted sheet; stored as a claim.
5. Znabu et al. is a preprint; scores for three tools were orchestrated with the authors' "Proto tool ecosystem". The 27,733 count matches the store's MFASS v2 cohort, but variant-level identity was not checked.
6. Smith and Kitzman source bytes differ from the existing `evidence-expansion-splice-evaluation-6960a140` record for the same URL.

## Coverage

Bounded pass. Not systematic. Not covered: CAGI5 per-submission tables, Vex-seq or MaPSy comparisons of current tools, prAUC values (figure-only in Smith and Kitzman), OpenSplice, SeqSplice and other saturation sets (CFTR), and the remaining Smith and Kitzman sheets.
