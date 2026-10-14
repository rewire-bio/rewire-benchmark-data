# Evo 2 zero-shot human variant effect prediction (Brixi et al., Nature 2026)

Issue rewire-bio/rewire-benchmark-data#129, genomics lane, 2026-10-14. Scope: the Evo 2 paper's own zero-shot
variant effect comparisons (ClinVar, SpliceVarDB, BRCA1, BRCA2). Existing Evo 2 source records were already in the
store but no evaluation cited them, so Evo 2's headline variant-effect numbers were absent from the catalogue.

## What was checked

- Existing source records for Evo 2 (`grep` over `data/entities/sources.jsonl` for evo2, Brixi, 638918): the GitHub
  README and LICENSE at commit 53f1959, the Hugging Face `evo2_7b` README and config, the Europe PMC journal full
  text (`evidence-official-8717ffb993cc8f7eddec`), the discovery and catalog project records, and the Europe PMC
  abstract record for the 2025 bioRxiv version (`qa-descriptions-20261010-source-evo2`). Only the journal full text
  is the paper itself; its artifact was re-downloaded and its hash matched, so it was reused.
- The Nature version was accessible, so the bioRxiv 2025.02.18.638918 version was not used. The version recorded on
  the new source records is Nature 652, 1349 (2026), DOI 10.1038/s41586-026-10176-5.
- Supplementary Information (73 pages) and Supplementary Data 1 (variant effect results workbook) were retrieved
  and hashed; see `sources.md` and `retrieval-log.md`.
- The main-text comparisons (Fig. 3b to e, Extended Data Figs. 4a to c and 5a to c) are bar charts of AUROC and
  AUPRC. Nothing was read from them. Supplementary Data 1 publishes the same per-model, per-stratum AUROC and AUPRC
  values as printed cells, and the figure legends name the strata, so the figures were used only to label protocols.

## What was extracted

Every data row of Supplementary Data 1, sheet "Sheet1" (705 rows, 21 models by 49 variant strata, two metrics per
row): 1,410 results. One protocol per stratum (49), one evaluation per model and stratum (705), one configuration
per model label (21), four datasets (ClinVar October 2024 filtered, SpliceVarDB, BRCA1 SGE, BRCA2), one benchmark
suite record, three new model family records (CodonBERT, EnCodon, DeCodon) and two new source records.

All evaluations have origin `author_reported`: the Evo 2 authors scored every model themselves ("For each benchmark,
we score the same variants with all models", Supplementary Information A.3.12). Comparison fields the paper does not
state (`metric_implementation`, `aggregation`, `budget`, and `adaptation` for the supervised comparators) are null
with a missing reason. All records are `needs_review`.

### IDs reused

- Source: `evidence-official-8717ffb993cc8f7eddec`.
- Model and method families for the configurations: `discovery-model-evo-2` (Evo 2 40B, 7B, 40B base, 7B base),
  `lit-genomics-20261011-geneb-model-evo` (Evo 1), `discovery-model-nucleotide-transformer` (NT),
  `uc20260930-model-esm-1b` (ESM-1b), `discovery-model-esm-2` (ESM-2 650M), `discovery-model-rna-fm` (RNA-FM),
  `regulatory-variant-20261009-model-gpn` (GPN-MSA), `discovery-model-spliceai`, `discovery-model-pangolin`,
  `somatic-oncogenicity-20261009-method-alphamissense`, `somatic-oncogenicity-20261009-method-cadd`,
  `somatic-oncogenicity-20261009-method-phylop` (the four PhyloP configurations).

Nothing in the store matched the paper's own ClinVar, SpliceVarDB, BRCA1 or BRCA2 populations at protocol level, so
new protocol and dataset records were created. The existing ClinVar and BRCA1 records belong to other benchmarks
(GFMBench-API, GUANinE, BEND, Cubuk 2021, Ramadane-Morchadi 2025, Smith and Kitzman 2023) with different filters,
splits and labels; there is no SpliceVarDB record in the store. `regulatory-variant-20261009-model-gpn` is the GPN
family record and is used as the family for the GPN-MSA configuration; GPN-MSA has no separate family record.

### Model naming

Evo 2 configurations follow the source's labels: "Evo 2 40B", "Evo 2 7B", "Evo 2 40B base", "Evo 2 7B base". The
base models are defined in Supplementary Information A.1.4 as the checkpoints after pretraining and before context
extension. The four Evo 2 configurations link `configuration_of` to `discovery-model-evo-2`, the canonical family
record (`catalog-model-evo-2` is being made its alias, so it is not used here).

## Extraction note for the reviewer

Method: `extract/extract_evo2_brixi2026.py`, run with the three pinned artifacts. It asserts their SHA-256 values,
reads the workbook with `extract/ooxml.py` (a stdlib OOXML reader, byte-identical to the one in
`data/omics/use-case-coverage-rna-splicing-20261011-silverstein2026/extract/`), and asserts the header `A1:J1`, 705
data rows, no rows past 706, no formulas, the count arithmetic in every row, stratum-count consistency across
models, the BRCA1 and BRCA2 class counts against Supplementary Information A.3.15, and that the model labels match
the 21 configurations. `printed_value` is the shortest round-trip decimal of the stored double, with the raw stored
string in `raw_xml_value`; the cells carry the number format "0.000", recorded in `workbook_number_format`, so the
workbook displays three decimals while storing full precision. No value was rounded or recomputed, and no
derivation is used: every value is a printed cell.

Tables extracted: Supplementary Data 1, sheet "Sheet1", all 705 data rows and both metric columns (1,410 cells).

Tables and figures not extracted, with reasons:

- Fig. 3b to e, Extended Data Fig. 4a to c, Extended Data Fig. 5a to c: bar charts. The values behind them are in
  Supplementary Data 1 and were taken from there.
- Supplementary Tables 6, 7 and 8 (Supplementary Information pages 39 and 40) print zero-shot AUROC, AUPRC and one
  Spearman r for Evo 2 7B base against an unreleased 7B data-ablation model on ClinVar, SpliceVarDB and BRCA1. They
  were not extracted: the ablation model is not a released configuration, and several Evo 2 7B base values conflict
  with Supplementary Data 1 at three decimals (ClinVar all SNV AUROC 0.957 and AUPRC 0.927 versus 0.960 and 0.944
  in the workbook's ClinVar "Both" SNV row; coding non-SNV AUROC 0.918 versus 0.865; SpliceVarDB intronic AUROC
  0.923 versus 0.925; BRCA1 values agree). The conflict is recorded in the Supplementary Information source record's
  `limitations`. A reviewer may decide this warrants an `evidence_concerns` entry instead or as well.
- Supplementary Table 5 (ClinVar AUROC at 40,000 steps, 0.63 and 0.73 for two 550M repeat-reweighting ablations) and
  the 0.82 figure in the same section: ablation models that are not released configurations, on a ClinVar protocol
  the section does not define. Not extracted.
- Supplementary Table 11 and the DART-eval numbers in the main text and Supplementary Information C.3 (caQTL,
  dsQTL, task 1 and task 2 values): a different benchmark, out of this batch's scope.
- Gene essentiality AUROC and AUPRC values printed in the main text (Evo 2 40B AUROC 0.66, AUPRC 0.15, with ranges
  for other models and PhyloP): out of scope for this variant-effect batch, and the comparator values are printed
  only as ranges, which cannot be assigned to models.
- The BRCA1 supervised classifier result in the main text (AUROC 0.95, AUPRC 0.88 on the 789-variant test set,
  Fig. 3i): a supervised ridge regression on Evo 2 embeddings, a different protocol from the zero-shot strata, and
  the comparator values in Fig. 3i are a figure. Not extracted. A reviewer may want it added as its own protocol.

Gaps and conflicts a reviewer should weigh:

1. Variant counts in Supplementary Data 1 differ from the Fig. 3 legend for seven strata: ClinVar coding SNVs
   14,313 against 14,319 in the legend, noncoding SNVs 33,747 against 34,761, coding non-SNVs 978 against 1,236,
   noncoding non-SNVs 3,623 against 3,894; SpliceVarDB exonic 1,179 against 1,181 and intronic 3,708 against 3,769;
   BRCA1 coding SNVs 2,768 against 2,077. BRCA1 noncoding (1,125) and BRCA1 all SNVs (3,893) agree with both the
   legend and Supplementary Information A.3.15. Populations in the records follow the workbook, because that is
   where the values come from. Recorded in the Supplementary Data 1 source record's `limitations`.
2. The ClinVar "Both" rows (SNV 89,126, Indel 25,501, Microsatellite 618) are much larger than the sum of the
   coding and noncoding rows (48,060 SNVs). "Both" is therefore not the union of the two strata, and the source does
   not say what it is. The three ClinVar "Both" protocols carry this in `limitations`.
3. Coding Indel (1,150) plus coding Microsatellite (172) do not sum to coding non-SNV (978); the relation between
   the "non-SNV", "Indel" and "Microsatellite" variant types is not stated.
4. The `Sub_category` labels "Poorly conserved" and "Not conserved" do not match the bin names in Supplementary
   Information A.3.13 ("weakly conserved", 0 <= phyloP < 0.5; "accelerated evolution", phyloP < 0). The mapping is
   not stated, so the protocol records quote the workbook label and say the mapping is unstated. "Far from splice
   site" and "Intergenic" are likewise undefined in the Supplementary Information.
5. Model labels are spelled inconsistently in the sheet: "phyloP 100/241/447/470" on the SpliceVarDB rows and
   "PhyloP 100/241/447/470" elsewhere. Both spellings are listed in each configuration's `source_locator`; they are
   treated as the same configuration because the counts and strata match.
6. Checkpoints are unreported for Evo 1, NT, RNA-FM, GPN-MSA, CADD (reference 132 is the CADD v1.7 paper but the
   version used is not stated), AlphaMissense, SpliceAI, Pangolin and the PhyloP scores. Those configurations carry
   `missing_metadata.version` with reason `unreported` and are kept at family level.
7. Training overlap between the supervised comparators (AlphaMissense, CADD, SpliceAI, Pangolin) and the evaluation
   variants is not reported. Every protocol says so in `limitations`.
8. No uncertainty is printed anywhere in Supplementary Data 1; every result has
   `missing_metadata.uncertainty` with reason `unreported`.
9. SpliceVarDB has no version or download date, and the positive and negative class names are not printed; the
   dataset record says the class names are unstated and the protocols describe the positive class as
   "splice-altering" from the main text's wording.
10. The article licence is CC BY-NC-ND 4.0, so no archived copy of any artifact is kept in the batch folder. A
    reviewer re-checking the values must re-download the two supplementary files; the hashes are in `sources.md`.
11. `catalog-model-evo-2` is not referenced by this batch. If the alias change lands, the Evo 2 configurations
    already point at `discovery-model-evo-2` and need no edit.
