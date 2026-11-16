# Bacformer and BacBench

Requested in rewire-bio/rewire-benchmark-data issue #245. Bacformer is a bacterial-genome
contextual protein model: it embeds each protein of a genome with a base protein language model,
orders those vectors by their coordinates on the chromosome and plasmids, and runs a transformer
over them to produce contextual protein embeddings. It never reads nucleotides. BacBench is the
benchmark the same group built around it.

This batch registers the Bacformer family and both sizes, the nine released checkpoints, BacBench
and its six tasks, the six evaluation datasets, seventeen protocols, the twenty-six benchmarked
configurations, and the 186 printed cells of the six benchmark tables in version 3 of the preprint.

Extraction only. A different agent reviews it. Nothing is marked reproduced, no review sign-off is
claimed, and the batch has not been added to the store.

Frozen extraction hash: `batch.jsonl` SHA-256
`776ec11726d7f9f42ec845745341abe0bbfb3006c74b9851e00ca8910995a1ac` (490 records).

## Sources

| ID suffix | Artifact | SHA-256 |
| --- | --- | --- |
| `source-preprint-v3` | bioRxiv 2025.07.20.665723 v3 PDF, posted 17 August 2026; the only source of numeric values | `d86de3315063e038ec8d5bed60b7b1a916c137ee60973e55d9d5c82f078d8dfd` |
| `source-preprint-v2` | bioRxiv v2 PDF, posted 13 August 2025; retrieved and hashed, no value taken from it | `a842db88eabf2b83d4e0de861e8a6767a01ee3f72c62b6a177494ffafd6d9703` |
| `source-bacformer-readme` | Bacformer README at commit 61dca95 | `6e4fdabbd05c93ff63b0eb583ce6a9309eaa13998087cc32ddeaa6928025b235` |
| `source-bacbench-readme` | BacBench README at commit 64b7d45 | `c9d28efef5b4cc30adbcc9de224c350100f5aa2a15a025beaf10dcdeb86cd93e` |
| `source-bacformer-licence`, `source-bacbench-licence` | LICENSE at each pinned commit (byte-identical Apache 2.0 text) | `d7fe40bfc2a639daa18e4caf57fab7545ece94bd38fb181c1f5b780d3b8cfa01` |
| `source-hf-card-bacformer-masked-mag` | Model card, revision 340a08cf5d5cd7d9f1ffac9075cde733d108a82b | `d735d1b2c8caa57a9f6abf990a457b2aa084f626070e555d6c01ca4a46b6bf7c` |
| `source-hf-card-bacformer-masked-complete-genomes` | Model card, revision d1c461f1db75902e6502e5ba7588ea1a4ea96b29 | `02575bd9d4ae949e3c38a5a5890767b862c75bc2a20e84afa4a517bd2f067ff1` |
| `source-hf-card-bacformer-large-masked-mag` | Model card, revision cb92cdf04e1b32993a19fdd9cf6f8f49efde2665 | `3809ffe59057788ba942d697a085edcd8458edbf815a116018e38e721d1e788d` |
| `source-hf-card-bacformer-large-masked-complete-genomes` | Model card, revision 84f85c37a05e55559142b842c1569e265183b554 | `19142e40c2aa69f1b3125fb7594cc8c6ea9f775e1878645583df21952c175596` |
| `source-hf-card-bacformer-causal-mag` | Model card, revision e4c8d6dc4decaa88729ce3853b1f329fee3b4960 | `a054cf81eb8ca4abac0ffd2063358fc97cc38ebcd7b7e945ff2cb026d7cde12c` |
| `source-hf-card-bacformer-causal-complete-genomes` | Model card, revision 6d2af6ac98f5aaf420ab33b475b891c8398e3bb9 | `048353f8367af281dd2a9d13404d9f4a257247bb308be3bfb578315e56c8047d` |
| `source-hf-card-bacformer-for-ppi-prediction` | Model card, revision 553108a6a1190d45fabea32e64b0ddf8755e6e0e; auto-generated template | `0336368f8274a5ed09f54cee8d56a851ecee96026d9f391a6735762c16608a60` |

Every artifact except the two PDFs is kept in `artifacts/` with the bytes that were hashed, and each
was retrieved twice on 2026-11-15 with identical bytes.

### The preprint PDF needs care

The v3 PDF's container bytes are not stable: bioRxiv regenerates the file per request (its producer
metadata is a conversion tool with a current timestamp). Two downloads minutes apart gave
`d86de331...` and `08fcc83a...`. Their `pdftotext -layout` text layers are byte-identical, SHA-256
`86636e89b167d7304b3a83ee7f159cad0a9bdbe97019588ce836087b8fe3b0b2`, and that text layer is what every
value was read from. It is archived gzipped as
`artifacts/biorxiv-665723v3-text-layer.txt.gz` (`0afdefd78a410d036d1c4f17e33bdf481e8d76241ee02f4c84c7c4be91ee72aa`),
recorded on the source record as `archive_sha256`, with the instability recorded in `hash_scope`.
A reviewer who refetches the PDF should expect a different file hash and compare the text layer.

## Retrieval, against what the issue reported

The issue said a v2 retrieval returned HTTP 403 at discovery and asked for Europe PMC or the bioRxiv
API before giving up. What happened on 2026-11-15:

- The bioRxiv details API returned three versions: v1 (2025-07-20), v2 (2025-08-13) and
  **v3 (2026-08-19)**. The issue treats the 2025-07-20 v1 as the current preprint; it is not.
- `https://www.biorxiv.org/content/10.1101/2025.07.20.665723v3.full.pdf` and the v2 early-path PDF
  both returned HTTP 200 over plain curl. No 403 was reproduced. The JATS `source.xml` path from the
  API returned a 301 with an empty body.
- Europe PMC holds the study as PPR1052405 with full text (`inEPMC: Y`). Its full-text XML
  (`bccc8cdc96bc08199a9af2a88238bd77ecfebda1949b4fd5bbea39534f6d5b61`) carries article-version number
  3 and its prose figures match the v3 PDF, but it contains **no tables at all**, so it could not be
  used for the result tables. It is not registered as a source; no record rests on it.
- Europe PMC's supplementary bundle for PPR1052405
  (`eca540172cfb6dad26cb76871bb2557816c7d1cd23a1c933a215ad269be10896`) holds four figure images and
  the per-row CSV files for Supplementary Tables 3 to 8 (per-gene essentiality predictions,
  environment-specific genes, AMR attribution scores). None of them is a benchmark result table and
  nothing was computed from them, so they are not registered either.

v2 and v3 are different reports of the same study and must not be pooled. v2 has no Bacformer Large
and prints different values for the same analyses (for example "almost 95% balanced accuracy" for
genus-level retrieval and 0.81 ± 0.07 median essentiality AUROC in v3, against different figures in
v2). A further trap: the v2 text layer mis-encodes digits, because its body font maps digits onto
punctuation, so "1.3 million" reads as "!.# million" and "0.91 ± 0.08" as "+.)! ± +.+(". Nothing can
be transcribed from the v2 text layer without a page render. The v3 text layer is clean.

## What was extracted

186 results, one per printed cell, from the six supplementary tables that carry benchmark
performance:

| Table | Cells | What it reports |
| --- | --- | --- |
| S1 | 24 | Operon identification, zero-shot, 12 systems x AUROC and AUPRC |
| S12 | 18 | Strain clustering (deprecated task), 6 systems x ARI, NMI and ASW |
| S13 | 48 | Protein-protein interaction, 12 systems x zero-shot and finetuned x AUROC and AUPRC |
| S14 | 24 | Gene essentiality, 12 systems x AUROC and AUPRC |
| S16 | 24 | Phenotypic traits, 12 systems x AUROC and AUPRC |
| S18 | 48 | Antibiotic resistance, 12 systems x binary AUROC and AUPRC and MIC-regression R squared and Pearson |

`extract/parse_tables.py` locates each table by its own printed caption, searches only the lines
between the previous caption and that caption, and asserts every row label in the printed order. The
twelve systems appear in two different printed orders (Tables S1 and S14 list Evo and Evo-2 second
and third; S13, S16 and S18 list them fifth and sixth) and both orders are asserted as printed.
`extract/check_tables.py` re-reads the same cells by character position against each table's printed
metric header, without using the first parser, and agrees on all 186 cells.

### What was not extracted, and why

- **Table S2** (operon paired statistical comparison: mean differences and Wilcoxon p-values for 11
  comparators). Differences and p-values, not performance; recorded as a gap to keep the batch bounded.
- **Table S15** (protein function prediction, 11 systems x macro F1 and macro accuracy, zero-shot and
  finetuned). BacBench does not list protein function prediction among its tasks, so it falls outside
  the benchmark this batch registers.
- **Tables S10, S11, S17** (context parameters, GPU-hours per model and task, per-drug genome counts).
  Configuration and dataset metadata rather than results. The S11 row labels are quoted in the
  parameter-count claims because they disagree with Table S9.
- **Main-text prose figures** (zero-shot operon AUROC range 0.76 to 0.92, essentiality 0.81 ± 0.07 and
  0.64 masked, PPI attention 0.99 ± 0.03 neighbourhood and 0.64 ± 0.05 co-occurrence, over 94% and
  over 98.5% trait balanced accuracy, percentage-point improvements). These describe Bacformer-only
  analyses on protocols the paper does not tabulate, and several are summaries of figures. Left as a
  gap rather than reconstructed.
- **Every figure**. Figures 1 to 4 and S1 to S14 print no numbers in the text layer and were not read
  by eye or from pixels.
- **AAI and ANI clustering comparators**. The Methods describe them; Table S12 does not include them,
  and the Methods state ANI failed to give meaningful similarities for many pairs.

## Decisions taken, with reasons

1. **Version 3 is the source of record.** It is the current version and the only one with Bacformer
   Large. v2 is registered for the version history only, with `scope_decision` saying no value came
   from it.
2. **Two configurations per benchmarked system, not one per task.** `config-<system>-zero-shot` covers
   the runs with no trained parameters (operon, PPI zero-shot, clustering) and
   `config-<system>-linear-probe` the runs with a trained linear head on frozen embeddings (PPI
   finetuned, essential genes, traits, AMR). The source states the head and its schedule per task, so
   those details live on the protocol; the configuration carries the checkpoint and the adaptation.
   A reviewer who prefers one configuration per task would have to split 24 records; the question is
   listed below.
3. **The clustering checkpoint is left unresolved.** Table S9 names
   `macwiatrak/bacformer-masked-complete-genomes` and `...-large-masked-complete-genomes` for the
   study, but the BacBench README footnote says strain clustering used the MAG checkpoints because
   the inputs are MAGs, and the clustering dataset is 6,071 MAGs. No source names the checkpoint for
   Table S12. The two clustering runs therefore have their own configurations
   (`config-bacformer-zero-shot-clustering`, `config-bacformer-large-zero-shot-clustering`) which
   point at the family record, with `missing_metadata.checkpoint` set to `conflicting`. Every other
   table uses the complete-genome checkpoints Table S9 names.
4. **One protocol per metric.** A protocol carries a single `metric` concept, so each table-column
   pair is its own protocol: 17 in total.
5. **Parameter counts are recorded, not chosen.** Nine claims hold each printed figure with its own
   locator, and the model records carry no parameter value (the `model` kind has no such attribute);
   the disagreement is stated in `provenance_note` instead. The configurations that Table S9 covers
   carry its figure, except base Bacformer, where the same source prints two (`conflicting`).
6. **MAG and complete-genome checkpoints are separate records.** The model cards state that each
   complete-genome checkpoint is initialised from the matching MAG checkpoint and further pretrained
   on about 40,000 RefSeq genomes, so they are different configurations of one architecture and no
   result may be moved between them.
7. **Existing store identities reused.** `discovery-model-esm-2` and `discovery-model-esmc` are the
   upstream protein language models, linked with `uses_model` from the Bacformer records and the
   configurations rather than duplicated. Comparator families reuse `discovery-model-dnabert-2`,
   `discovery-model-evo-2`, `discovery-model-nucleotide-transformer`, `catalog-model-prokbert`,
   `lit-genomics-20261011-geneb-model-evo`, `lit-genomics-20261011-guanine-model-mistral-dna` and
   `lit-protein-20261011-deepprotein-model-protbert`. `discovery-model-nucleotide-transformer` was
   chosen over `catalog-model-nt-v2`, whose version field says "50M multi-species" while the
   benchmarked checkpoint is the 250M multi-species v2. Only gLM2 had no record in the store, so
   `model-glm2` is new. No vocabulary concept was missing, so there is no `vocab-proposal.ttl`.
8. **Units.** S1, S13, S14, S16 and S18 print values on a 0 to 100 scale, including R squared and the
   Pearson correlation, so `unit` is `percent` with `unit_detail` saying so. S12 prints 0 to 1 values,
   so `unitless`. ASW maps to the `silhouette-score` concept with the printed name in the qualifier.
9. **Spread.** Each result carries `uncertainty` of type `standard_deviation` with the printed string,
   the scope quoted from the caption, and `n` only where the source states the count (5 strains for
   S1; 37 and 56 antibiotics for S18, taken from the Methods and said so in the note). S12 adds
   `method: bootstrap` and `resamples: 10` from its caption.
10. **Status `needs_review` everywhere.** The extraction is complete but unreviewed; `source_checked`
    is the reviewer's to set.
11. **Captions.** `metric_definition` holds each table's caption with the en dash of
    "gene-essentiality" and "Protein-protein" written as a hyphen, to keep house style. The printed
    values themselves are byte-exact, including the plus-minus sign and the leading zeros of
    "03.95 ± 21.04" and "00.53 ± 00.72".

## Questions the issue asked, and what the sources say

- **Parameter counts.** Base Bacformer: 27M on all four base model cards, in preprint Table S9 and in
  the BacBench README table; 26M in the Bacformer README "Requirements" and in preprint Table S11.
  Bacformer Large: 300M in the README and on both large model cards (once as "more than 300M"); 332M
  in preprint Tables S9 and S11; 27M in the BacBench README table. Not resolved here. Two
  observations for the reviewer: the BacBench table's 27M for Bacformer Large repeats its Bacformer
  row while changing the dimension to 960, which looks like a copy, and the preprint's 332M for
  Bacformer Large is exactly the figure the same table gives ESM-C. Hugging Face serves a safetensors
  parameter total of 50,852,241 for every base checkpoint and 431,765,841 for both large ones; those
  totals are API metadata rather than a printed statement, so they are recorded only here and on the
  card source records' `access_note`, and no record rests on them.
- **Which checkpoints exist.** The README checkpoint table lists eight. Six resolve on Hugging Face
  and are pinned by revision. Two, `bacformer-causal-protein-family-modeling-complete-genomes` and
  `bacformer-for-essential-genes-prediction`, returned HTTP 401 from both the page and the model API
  to an anonymous request on 2026-11-15, so they are registered from the README row alone with
  `access` and a claim recording the 401. A ninth, `bacformer-for-ppi-prediction`, is named only in
  the preprint Methods; it resolves and serves weights but its card is the auto-generated template
  with no description, training data or licence.
- **MAG versus complete genomes.** Distinct, on the model cards' own wording; recorded as separate
  checkpoint records plus the `complete_genome_pretraining` claim.
- **Which BacBench tasks have printed numeric results, and where.** All five active tasks, in the
  preprint's supplementary tables: operon S1, PPI S13, essential genes S14, phenotypic traits S16,
  antibiotic resistance S18. None in the BacBench repository, which prints no numbers and has
  "Create model leaderboard for each task" unchecked on its to-do list. The preprint also tabulates
  the deprecated strain clustering task (S12) and a protein function task BacBench does not list
  (S15). Table S11's GPU-hour columns are exactly the five active tasks, which ties the preprint's
  benchmark to BacBench's current task set.
- **Do the current BacBench splits differ from the ones the preprint evaluated?** BacBench's news
  entry of 13.05.2026 moved essential genes and PPI to genus-aware splits and deprecated strain
  clustering. Version 3 of the preprint, posted August 2026, describes genus-level 60/20/20 splits for
  both tasks, so its protocol matches the current description; version 2 predates the change. This
  cannot be checked beyond the prose: no split manifest, seed list or BacBench commit is published
  for the runs. Recorded as a claim plus a gap, and the protocol records say so.
- **Upstream protein language model, and does the store hold it?** Base Bacformer uses ESM-2 t12 35M
  (`facebook/esm2_t12_35M_UR50D`), already in the store as `discovery-model-esm-2` (which
  `catalog-model-esm-2` aliases). Bacformer Large uses ESM-C, in the store as `discovery-model-esmc`.
  The sources disagree on which ESM-C artifact: the model cards and preprint Table S9 name
  EvolutionaryScale's `esmc_300m` (`esmc-300m-2024-12`), while the Bacformer README names the ESM++
  reimplementation `Synthyra/ESMplusplus_small`. Both statements are recorded as claims, and the
  BacBench README lists ESMPlusPlus as a separate benchmarked model from ESM-C.
- **What Apache-2.0 covers.** The preprint's availability statement, the pinned LICENSE files and the
  card front matter agree that Apache-2.0 covers the Bacformer repository code and its released
  checkpoints, and separately the BacBench repository code. It does not cover: the base protein
  language models (the README itself notes ESM++ is under the EvolutionaryScale Cambrian Open License
  Agreement), the ten comparator models, the released PPI checkpoint, which declares no licence, or
  the third-party measurements behind the datasets (MGnify, SPIRE, NCBI RefSeq and GenBank, STRING
  DB, the Database of Essential Genes v15, the NCBI AST browser, two phenotype catalogues, and the
  authors' own long-read RNA sequencing). The dataset records say this in `reuse_restrictions`.
  Hugging Face card metadata declares `apache-2.0` for ten of the thirteen dataset repositories named
  in the BacBench README and nothing for the operon DNA copy and the two strain-clustering copies, as
  observed on 2026-11-15; those cards were not pinned as sources, so dataset terms remain a gap.

## Gaps

1. Supplementary Tables S2, S10, S11, S15 and S17 were not extracted (reasons above).
2. No figure was read; every figure-only number is unrecorded.
3. Main-text prose figures for the Bacformer-only analyses were not extracted.
4. The number of test genomes behind the PPI and essentiality means and medians is not printed, so
   those denominators are unreported.
5. Table S16's caption says the spread is across 5 seeds while the Methods say three independent runs;
   the source does not reconcile them. Recorded as a claim and as `source_warnings` on the 24 S16
   results, not as an evidence concern.
6. No split manifest, seed list or BacBench commit is published for any run, so none of these numbers
   is reproducible as printed.
7. Dataset licences were observed only in Hugging Face card metadata, which this batch did not pin.
8. Two README-listed checkpoints returned HTTP 401 and could not be inspected; HTTP 401 does not
   distinguish a private repository from one that does not exist.
9. The ESM++ and Cambrian Open License Agreement licence texts were not retrieved; only the README's
   statement about them is recorded.
10. Whether the preprint's Bacformer Large runs used a checkpoint revision from after the 2025-05-15
    embedding bug fix cannot be settled from these sources.
11. The Europe PMC deposit and its supplementary CSV files were retrieved and hashed but not
    registered, because nothing was extracted from them.
12. The author's LinkedIn announcement named in the issue was not retrieved: it is not a primary
    source, and the issue records that commenting is restricted. Nothing rests on it.

## Checks run by the extractor

```sh
python3 -I data/omics/bacformer-20261115/extract/parse_tables.py     # 186 cells, row labels asserted
python3 -I data/omics/bacformer-20261115/extract/check_tables.py     # column-position recheck, agrees
python3 -I data/omics/bacformer-20261115/extract/build_batch.py      # writes batch.jsonl
npx tsx data/omics/bacformer-20261115/extract/validate_batch.ts      # schema, attributes, vocabulary,
                                                                     # descriptions, relations
gzip -dc data/omics/bacformer-20261115/artifacts/biorxiv-665723v3-text-layer.txt.gz > /tmp/v3.txt
npm run -s batch -- check-values data/omics/bacformer-20261115 \
  bacformer-20261115-source-preprint-v3=/tmp/v3.txt                  # 36 in_cell, 150 in_row, 0 other
```

`value-check.tsv` in this folder is the extractor's own run of that last command, kept as a record of
the check; the reviewer reruns it. The text layer is the artifact to pass, not the PDF, because the
PDF's bytes change per download. The reviewer's hash run needs a refetched PDF for
`source-preprint-v3` and will see a different file hash; the text layer is the stable comparison.

## Questions for the reviewer to rule on

1. The base and large parameter counts (five and four printed figures). Pick one with a reason,
   mark one printed figure as an error on its source, or leave the claims as they stand.
2. Whether the BacBench README's "Bacformer Large, 27M" warrants an `evidence_concerns` entry on
   `source-bacbench-readme` scoped to the parameter claim.
3. Whether the Table S16 seed conflict (5 seeds against three runs) warrants an evidence concern on
   the two phenotypic-trait protocols rather than the result-level warning used here.
4. Configuration granularity: two adaptations per system, or one configuration per system and task.
5. Whether the unresolved clustering checkpoint should instead be assigned to the complete-genome
   checkpoints on the strength of Table S9's study-wide statement.
6. Whether Table S15 (protein function prediction) should be added, given that BacBench does not list
   the task but the Bacformer README does.
7. Whether the strain clustering protocols should carry an evidence concern for selecting the Leiden
   hyperparameters on the same metrics the table reports, rather than only the limitation and warning
   recorded here.
8. Whether `discovery-model-nucleotide-transformer` or `catalog-model-nt-v2` is the right family for
   the benchmarked 250M v2 checkpoint.
