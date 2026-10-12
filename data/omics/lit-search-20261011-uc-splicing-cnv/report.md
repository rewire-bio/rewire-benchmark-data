# Literature pass 2026-10-11: patient-RNA splicing validation and CNV detection

Collector: Claude research agent `uc-splicing-cnv`. No human review is claimed. Nothing was executed or reproduced. Every record is `needs_review`; nothing has been added to the store.

- Use cases: `use-case-patient-rna-splicing-validation` and `use-case-cnv-detection-characterisation`.
- Window: published or posted 2025-10-01 to 2026-10-11.
- Budget: about 30 queries per use case. Used: 12 logged splicing searches and lookups, 15 CNV, plus source retrievals. Europe PMC title and abstract queries, full-text queries, the bioRxiv/medRxiv API and one review follow-up.
- Search log: `ledger.jsonl` (27 rows). Include and exclude decisions: `scope-audit.jsonl` (23 rows). Both use the field sets of the shared files, which were not edited.

Before searching I read both use-case records, their linked protocols and judgements, the 2026-10-09 dossiers in `docs/reviews/use-cases/`, the `research.md` and `coverage.json` of the 2026-10-09 batches, and the shared ledger and scope audit. Sources already in `data/entities/sources.jsonl` were skipped by DOI. The live pages were not opened; I worked from the records the pages are built from.

## Extracted (5 sources, 651 records)

| Batch | Source | Tables | Results | Other records | Use case | Judgements |
| --- | --- | --- | --- | --- | --- | --- |
| `use-case-coverage-rna-splicing-20261011-silverstein2026` | Silverstein et al., medRxiv 2026 (v1, CC0) | Table S9, all 81 cells | 81 | 2 sources, 1 dataset, 3 protocols, 3 methods, 9 configurations, 9 evaluations, 1 claim | patient-RNA splicing | 3 (splicing direct; expression and allelic imbalance proxy) |
| `use-case-coverage-rna-splicing-20261011-fortier2026` | Fortier, Rudy and Scherer, PLOS One 2026 (CC BY) | Tables 1 to 6, all 96 cells | 96 | 1 source, 6 datasets, 6 protocols, 2 models, 1 method, 4 configurations, 24 evaluations | patient-RNA splicing | 4 (all proxy; none for the two ClinVar-labelled tables) |
| `use-case-coverage-rna-splicing-20261011-alavi2026` | Alavi, bioRxiv 2026 (v1, CC BY-NC-ND) | Tables III and IV, all 168 cells | 168 | 1 source, 3 datasets, 3 protocols, 1 model, 12 configurations, 36 evaluations | patient-RNA splicing | 2 (both proxy) |
| `use-case-coverage-cnv-20261011-zhang2026` | Zhang, Zhang and Chen, Global Medical Genetics 2026 (CC BY-NC-ND) | Tables 3 and 4, all 65 cells | 65 | 1 source, 1 dataset, 3 protocols, 5 methods, 5 configurations, 15 evaluations | CNV | 3 (all proxy) |
| `use-case-coverage-cnv-20261011-hwang2026` | Hwang et al., Genes 2026 (CC BY) | Table 4, all 48 cells | 48 | 1 source, 1 dataset, 2 protocols, 1 method, 8 configurations, 8 evaluations | CNV | 2 (both proxy) |

Why these: Silverstein et al. is the first table in the store with per-tool false positives on patient RNA-seq, which the use case lists as a gap. Fortier et al. is an independent comparison of SpliceAI and its open reimplementations on four experimentally labelled sets. Alavi is the only in-window source that scores genomic foundation models (NTv3 650M, Evo2 40B, Genos 10B) and AlphaGenome against splice variants confirmed in patient RNA. Zhang et al. covers the characterisation half of the CNV question (automated ACMG classification). Hwang et al. adds duplications and exome CNV callers against an orthogonal array truth set.

Each batch folder has `batch.jsonl`, `claims.csv`, `coverage.json`, `sources.md`, `retrieval-log.md`, `research.md`, `use-case-links.json` (proposed `assessed_by` links, not applied) and an `extract/` script that re-creates `batch.jsonl` from the pinned artifact and asserts headers and row labels. CC0 and CC BY artifacts are archived as gzip under `artifacts/`; the two CC BY-NC-ND sources are not archived. All five batches pass a dry run of the store validators (`addBatch` checks without writing: vocabularies, attributes, derivations, record links).

## Not extracted

| Candidate | Reason |
| --- | --- |
| Eveleigh et al., Genome Biology 2026, sequencing technologies on HG002 (doi:10.1186/s13059-026-04048-4) | SV caller precision, recall and F1 on T2T-Q100 v1.1 and CMRG truth are printed in Additional file 2 (two tables of 106 rows), which would fill the 'T2T-Q100 or CMRG truth' gap. But the PDF puts captions after tables, and the Results prose F1 values (for example SVIM insertions 86.66% and DRAGEN insertions 44.72%) match neither table, so which table is discovery and which genotyping is uncertain. SVs are mostly below 1 kb. Worth extracting once a reviewer or the authors settle the table identity. |
| MAJIQ-CLIN, Genet Med 2026 (doi:10.1016/j.gim.2026.102628) | Developer comparison with other splicing outlier tools. Published version (CC BY) not retrievable: no PMC copy, Elsevier API metadata only, publisher HTTP 403. The preprint is from February 2025, outside the window. |
| Prenatal WES versus CMA letter, Clin Transl Med 2026 (doi:10.1002/ctm2.70761) | One unnamed pipeline; concordance and PPV with confidence intervals, including 56 P/LP duplications. No tool comparison. Candidate for single-pipeline duplication evidence. |
| SV benchmarking frameworks, PLOS Comput Biol 2026 (doi:10.1371/journal.pcbi.1014824) | Shows how Truvari, EvalSVcallers and SVbenchmark matching change the same callers' scores on HG002 and NA12878; per-caller metrics are in figures. Bears on the use case's comparability gap; candidate for a protocol-only record. |
| HG008 somatic SV callers, Front Genet 2026 | Precision, recall and F1 in a supplementary figure only. |
| SCOUT tumour-evolution simulation, bioRxiv 2026 | ASCAT, Sequenza and Battenberg accuracy is figure-only in the text read; supplementary tables T8 to T10 not opened. |
| Seven exome CNV tools on amniotic-fluid WES, Genomics 2026 | No open full text found. |
| Synthetic gene variant splicing benchmark, bioRxiv 2026.08.24.746734 | Massively parallel assay endpoint; fits `use-case-splicing-follow-up`, not this pass. |
| Diagnostic-yield cohorts (Solve-RD, NGRL 5,412 blood RNA-seq, stratified blood RNA-seq, PBL RNA-seq) | Report yield, not per-tool accuracy. |
| Silverstein Tables S3 to S5, S7, S8 | Per-event detections behind Table S9; could be added as `event-detected` results later. |
| Reviews: Genome Biol 2026 CNV strategies, Nat Genet 2026 AI splicing prediction | Leads only; the CNV review's cited benchmarks predate the window or are stored. |

## Gaps

- No in-window germline whole-genome CNV caller benchmark with clean printed values was found; the Genome Biology table-identity problem blocks the one candidate. No deep-learning or foundation-model CNV caller was evaluated in the window.
- Tumour or somatic CNV: still no printed per-caller values (SCOUT and HG008 are figure-only in what was read).
- MAJIQ-CLIN's tool comparison remains unread.
- Long-read CNV: no multi-caller benchmark with printed values.
- Figures were not read in any source. Supplements were read only for Silverstein et al.

## What needs a reviewer's judgement

1. Silverstein et al.: five discrepancies are recorded as source limitations (22 versus 21 true-negative samples; OUTRIDER + GTEx 83% in prose versus 4 of 5 in Table S9; LeafcutterMD 67 versus FRASER 68 positives on the same tissue sets; a typed 0 for LeafcutterMD F1; per-tool denominators). Decide whether any should be an `evidence_concern` that blocks comparison.
2. Silverstein et al.: ANEVA-H is `author_reported` because two authors wrote the ANEVA-h preprint (reference 36). Splicing judged `direct`; expression and allelic imbalance `proxy`.
3. Silverstein et al.: accuracy, precision and MCC mix event-level positives with sample-level negatives (any outlier in a negative sample is one false positive). The metric qualifier says so; check that it is enough.
4. Fortier et al.: Legacy Ensemble rows are `author_reported` (the authors' employer supplies the VarSeq algorithms). Two prose slips recorded as limitations. The Riepe, CI-SpliceAI, SPiP and Barbosa protocols also bear on `use-case-splicing-follow-up`; no judgement was added for that use case.
5. Alavi: the Genos 10B row is taken as Genos-10B v1 from the Results wording; two Table IV percentages do not match their counts (15/107 printed 13.9%, 31/107 printed 28.7%). Type II error and positive-call rates use the `proportion` concept with qualifiers, because the vocabulary has no false-negative-rate concept; no vocabulary was added.
6. Zhang et al.: Table 4 'Accuracy' per reference class is recorded as `recall` with a qualifier; Table 3 averaging across classes is unstated, so `comparison.aggregation` is unreported. Relevance `proxy` for classification of detected CNVs; a reviewer may prefer `outside_scope`.
7. Hwang et al.: post-filter rows are `author_reported` (the filter is the authors'), and the reference exon count shrinks after filtering. Prose and table differ slightly (recorded as limitations).
8. The proposed summaries below.

## Proposed summary updates (not applied)

Per docs/use-cases.md, these replace the current summary claims only after the judgements they describe are reviewed. Every number is from a stored or batch result; the reviewer should trim to what is approved.

### use-case-patient-rna-splicing-validation

Keep the current text and add before its last two sentences:

> Silverstein et al. (2026, preprint), a clinical research group that did not develop the splicing callers, scored eight RNA-seq tools on 97 previously diagnosed neuromuscular samples and also counted outlier calls in true-negative samples (Table S9). On known pathogenic splicing events in muscle and fibroblast RNA-seq, rMATS-turbo detected 15 of 23 and MINTIE 8 of 23; on muscle, fibroblast and cycloheximide-treated fibroblast RNA-seq FRASER detected 21 of 68 and LeafcutterMD none of 67; FRASER2.0, run on muscle only, detected 2 of 16. Every one of these callers except FRASER2.0 reported outliers in every true-negative sample it was run on (rMATS-turbo and MINTIE 9 of 9, FRASER and LeafcutterMD 21 of 21); FRASER2.0 did so in 2 of 6. Denominators differ by tool, and a negative sample with any outlier counts as one false positive. Two DNA-based comparisons add proxy evidence. Fortier et al. (2026), independent of the SpliceAI reimplementations' developers, report balanced accuracy on functional splice-assay variants in ABCA4 and MYBPC3 of 0.836 for SpliceAI, 0.794 for CI-SpliceAI and 0.746 for OpenSpliceAI with thresholds tuned per gene, and on 242 deep intronic pathogenic variants with matched controls of 0.940, 0.890 and 0.841 with thresholds tuned on that set (Tables 2 and 4). Alavi (2026, preprint) applied thresholds tuned on OPA1 variants to 76 splice-site variants confirmed by RNA studies and 107 benign variants in 65 genes: sensitivity was 88.2% for SpliceAI, 85.5% for pretrained NTv3 650M, 71.1% for Evo2 40B with a human identifier, 56.6% for AlphaGenome and 27.6% for Genos 10B (Table IV).

Proposed `evidence_gaps` change: replace "Among the sources extracted, no RNA-seq caller comparison reports false positives per sample in a table; outlier workload is figure-only in Segarra-Casas et al." with "False positives are tabulated only as true-negative samples with any outlier (Silverstein et al. Table S9); outlier counts per sample remain figure-only." Add "MAJIQ-CLIN (Genet Med 2026) compares splicing outlier tools but could not be retrieved as full text."

### use-case-cnv-detection-characterisation

Keep the current text and replace its last sentence with:

> Hwang et al. (2026) compared four exome callers with chromosomal microarray CNVs in 39 clinical exomes, scored per exon and including duplications: sensitivity and PPV were 0.758 and 0.025 for ExomeDepth, 0.662 and 0.096 for CNVkit, 0.768 and 0.239 for CoNIFER and 0.170 and 0.041 for cn.MOPS; after the authors removed each tool's recurrently miscalled regions ExomeDepth reached 0.903 and 0.102 on a smaller reference set (Table 4). For characterisation, Zhang et al. (2026) ran five automated ACMG classifiers on 3,031 expert-classified CNVs: five-category accuracy ranged from 48.76% (X-CNV) to 69.81% (MarCNV-ISV), and pathogenic deletions were recognised more often than pathogenic duplications by every tool (AnnotSV 95.16% versus 86.39%) (Tables 3 and 4). None of the comparisons shown covers tumour samples or long reads, and none evaluates a foundation model.

Proposed `evidence_gaps` change: replace "Duplication evidence is limited to 10 HG002 duplication truth events in one source" with "Whole-genome duplication evidence is limited to 10 HG002 duplication truth events in one source; exome duplication evidence is exon-level against CMA (Hwang et al. 2026)." Add "The Genome Biology 2026 HG002 T2T-Q100 and CMRG SV benchmark is not stored because its supplementary table identity is ambiguous."
