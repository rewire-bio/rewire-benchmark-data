# Research: tumour somatic SNV and indel use-case pass, 2026-10-09

Use case: `use-case-tumour-dna-somatic-variant-detection` ("Which calling or rescoring workflow reliably detects tumour SNVs and small indels under the available sequencing and normal-sample regime?"). Before this pass it had one judgement: Lancet versus Strelka2 on the Lancet paper's virtual tumour (two evaluations, author-reported for Lancet).

Bounds: cutoff 2026-10-09; budget 25 queries, 16 used; at most 3 sources extracted, 2 used. Lane `genomics`. In scope: several somatic callers scored on the same tumour-normal truth set with printed per-caller values. Out of scope under the current use-case definition: ctDNA, targeted panels, FFPE, copy-number and structural variants.

## Queries

Times for q1 to q10 and q14 are reconstructed from the saved files' timestamps (within about a minute); the others are from `date` output. The ledger IDs are `search-use-case-tumour-somatic-genomics-q1` to `-q16`.

| # | Query | Channel | Outcome |
| --- | --- | --- | --- |
| 1 | independent benchmark somatic SNV indel callers Mutect2 Strelka2 VarScan2 MuSE SEQC2 HCC1395 precision recall F1 table | web search | FANSe comparison (Front Genet 2022), two SEQC2 reanalysis preprints |
| 2 | Europe PMC `PMC9705725` | Europe PMC REST | FANSe developers' five-pipeline WES spike-in comparison; lead |
| 3 | "Toward best practice in cancer mutation detection with whole-genome and whole-exome sequencing" supplementary table F1 score callers | web search | Xiao et al. 2021 (SEQC2); MuSE 2 paper |
| 4 | Europe PMC `DOI:10.1038/s41587-021-00994-5` and `PMC11146589` | Europe PMC REST | Xiao 2021 not open access (XML HTTP 500); MuSE 2 excluded |
| 5 | benchmarking somatic small variant callers tumor-normal whole genome DeepSomatic Mutect2 Strelka2 NeuSomatic SEQC2 truth set independent comparison 2024 2025 | web search | DeepSomatic (developer), HG008 preprint, low tumour fraction simulation |
| 6 | Europe PMC `DOI:10.1186/s12859-024-05793-8` and `PMC11370364` | Europe PMC REST | Targeted low-fraction simulation; excluded |
| 7 | (HCC1395 OR SEQC2) AND (Mutect2 OR MuTect2) AND Strelka2, open access, 2019 to cutoff | Europe PMC REST | 20 hits; COSAP excluded; four leads |
| 8 | TITLE:(somatic AND benchmark/comparison/evaluation) AND callers, open access, 2016 to cutoff | Europe PMC REST | 32 hits; Guille et al. 2025 selected |
| 9 | HG008 somatic small variant benchmark GIAB ... precision recall | web search | GIAB HG008 data paper; Research Square preprint rs-11210923 |
| 10 | `researchsquare.com/article/rs-11210923/v1` | web fetch | Title only; not readable |
| 11 | ("whole genome" OR WGS) AND (HCC1395 OR SEQC2 OR "DREAM challenge" OR HG008) AND (VarScan2 OR MuSE OR SomaticSniper OR VarDict OR LoFreq) AND (precision AND recall), open access | Europe PMC REST | NeuSomatic SEQC2 2022 (lead); ctDNA benchmark (excluded by scope) |
| 12 | TITLE:"DeepSomatic"; TITLE:"Lancet2" | Europe PMC REST | DeepSomatic paper not open access; Lancet2 developer paper |
| 13 | ("DREAM challenge" OR "ICGC-TCGA DREAM") AND somatic AND callers AND (Strelka OR MuTect OR VarScan), open access | Europe PMC REST | 24 hits; Wang et al. 2020 selected |
| 14 | tumor-only somatic variant calling benchmark ... SEQC2 whole genome | web search | No tumour-only table found |
| 15 | (HG008 OR "HG008-T") AND somatic AND (benchmark OR "truth set"), 2023 to cutoff | Europe PMC REST | No peer-reviewed HG008 small-variant comparison |
| 16 | (FFPE OR formalin) AND somatic AND variant callers AND (Mutect2 OR Strelka2) AND (precision OR F1), open access | Europe PMC REST | Two FFPE leads; not opened |

## Decisions

| Source | Decision | Reason |
| --- | --- | --- |
| Wang et al. 2020, Sci Rep, Supplementary Tables S1-S2 | Extract every cell (720 results) | Eight WGS tumour-normal pairs (four simulated DREAM sets, CLL, AML, COLO829, a paediatric brain tumour), eight callers, NeuSomatic and majority-vote ensembles, with recall, precision, F1 and call counts per dataset. The authors did not develop the eight callers or NeuSomatic. |
| Guille et al. 2025, Brief Bioinform, Supplementary Table S7 | Extract every cell (198 results) | Held-out SEQC2 HCC1395 exome sample; 16 SNV and 13 indel callers, including DeepSomatic, NeuSomatic, VarNet, Lancet and Mutect2 4.2.2.0, plus four retained ensembles; TP, FP, TPR, FPR, F1 and PPV. Independent academic group. |
| Guille et al. 2025, Tables S1-S2 | Not extracted | 3,276 cells (four datasets by four post-alignment procedures). Kept out to keep the batch small; Table S7 is the held-out test. Recorded as a lead and gap. |
| NeuSomatic SEQC2 2022 (Genome Biol), Additional file 2 | Not extracted | Developer paper; the tables are in a PDF with rotated column headers, which would need position-based parsing; about 700 cells per table. Strongest lead for SEQC2 WGS, purity, coverage and FFPE strata. |
| Xiao et al. 2021 (Nat Biotechnol, SEQC2) | Not retrieved | Not open access through Europe PMC |
| Lancet2 2026 | Not extracted | Developer paper; supplementary bundle HTTP 500; main results in figures |
| DeepSomatic 2025 | Not retrieved | Not open access; developer paper |
| HG008 preprint (Research Square rs-11210923) | Not extracted | Not peer reviewed; page content not readable; draft truth set |
| ctDNA benchmark, Nat Commun 2025 | Excluded under current scope | ctDNA is excluded in the use case; lead if the scope changes |
| MuSE 2 (Genome Res 2024) | Excluded | Truth is earlier consensus calls that include MuSE |
| BMC Bioinformatics 2024 low tumour fraction | Excluded | Simulated ultra-deep targeted panels |
| COSAP 2024 | Excluded | No per-caller accuracy table |

## Modelling choices

- One protocol per truth set and variant type: 13 for Wang (8 SNV, 5 indel; DREAM sets 1-2, AML have no indel truth) and 2 for Guille. Each has one relevance judgement, grouped for the page as `wang2020-wgs-snv`, `wang2020-wgs-indel` (strata are datasets, in table order) and `guille2025-seqc2-fd-wes` (strata SNVs, indels). Headline metric F1.
- One configuration per printed row label and study, linked `configuration_of` to a method family record. Versions are as printed in Wang Methods and Guille Table 1. Wang's two VarDict rows and two NeuSomatic rows are separate configurations. The meaning of `NeuSomatic_Lowqual` and `NeuSomatic_Pass` is not defined in the source; the configuration text says so.
- Ensembles are configurations of one method, "Majority-vote consensus of somatic callers", with origin `author_reported` because they are each paper's own approach. Individual callers are `independent_paper`.
- Method types: `conventional_pipeline` for classic callers and ensembles, `supervised_machine_learning` for DeepSomatic, NeuSomatic and VarNet. `foundation_model_eligible` is false throughout.
- `access` on method records is the download location printed in Guille Table 1. No licence was recorded: the sources do not state caller licences, apart from the commercial-licence footnote for DRAGEN and TNScope, which are not in Table S7.
- The column `P` (truth count) is stored as `denominator` on each protocol, not as a result. Wang's truth counts are asserted against article Table 1.
- FPR in Table S7 is stored as `false-positive-rate`; its denominator is not defined in the source (recorded in `missing_metadata`).
- Existing records reused: none. The AMP Lancet and Strelka2 configurations configure a different evaluation and have no method link; new method records were made (see `coverage.json`).

## Things a reviewer should judge

1. Guille Results "Validation" says the ensembles beat "the best individual tool" by 2.7% (SNV) and 10.2% (indel); Table S7 prints higher F1 for DeepSomatic-WES (0.9006, 0.8119). The stated gains match Mutect and Mutect2. Table values recorded.
2. Guille prose gives DeepSomatic a mean indel F1 of 0.807; Table S6 (not extracted) prints 0.5643.
3. Guille Table S7 labels DeepSomatic as `DeepSomatic-WES`; the supplementary command uses `--model_type=WGS`.
4. Guille ran NeuSomatic with a SEQC2 HCC1395 WGS checkpoint on an HCC1395 validation sample; Wang ran NeuSomatic with a DREAM3 model on data that include DREAM set 3. Either may not be held out.
5. Guille Table 2 and Methods give different accessions and platform wording for the validation sample.
6. Precision on Wang's real tumours is low for most callers (for example MuTect2 0.157 on AML). The authors note the curated truth sets may be incomplete, which lowers measured precision.
7. Whether any of items 1-5 should become a source `evidence_concerns` entry. Doing so withholds every judgement that cites that source.

## Coverage

Bounded pass against the sources above. Not systematic. Not covered: tumour-only calling, FFPE, ctDNA, targeted panels, HG008, SEQC2 WGS caller comparisons with printed tables, long-read somatic callers, Guille Tables S1-S6 and Wang Tables S3-S9.
