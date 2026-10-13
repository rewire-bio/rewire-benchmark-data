# Research notes

Scope: rewire-benchmark-data#19 (parent rewire.it#365). Extend the existing Feng et al. 2025 records to the remaining decision-relevant tables. Bounded to one paper; not a literature search.

## What was already in the store (release 2026-10-12-5b983e4ada23)

- Source `dna-foundation-models-2025` (discovered) with two Table 3 Human 5mC results (`lit-001`, `lit-002`).
- Source `evidence-expansion-dna-foundation-models-2025-5d8ca9bc` (article XML) with the 7 October AMP intake, prefix `amp-feng-20261007-`: Table 1 Acceptor and Donor, Table 2 Arabidopsis TATA and NonTATA, all of Table 5 (pathogenic vs common SNPs, 22 values) and all of Table 6 (four QTL types, 96 values). 138 results, 79 evaluations, 9 protocols, 9 use-case judgements (all proxy).
- Source `evidence-reported-dna-foundation-models-2025-readme-md` (author README at commit 3f4c81c).

All of these are reused. No existing record is changed.

## Added in this batch

- Table 1 (human sequence classification): the 22 rows not yet extracted, 5 models each, 110 AUC results. One protocol and one dataset per row, with training and test sizes and class counts from Supplementary Data 6.
- Table 4 (GTEx whole-blood gene expression): 8 rows, average Pearson correlation and average MSE, 16 results. Two protocols because the long-input rows cover a 768-gene subset.
- Baseline CNN comparator: Supplementary Data 1 and 2 print only which models were significantly better or worse than the CNN, not the CNN's AUC. Recorded as one `reported_finding` claim per Table 1 row and for the two Arabidopsis promoter rows (26 claims), including the existing splice and Arabidopsis protocols. The CNN significantly beat all five models on Donor and on Arabidopsis NonTATA, and four of five on Acceptor and Arabidopsis TATA.
- TAD recognition: a protocol and dataset with no evaluations, and a `reported_finding` claim. The paper prints no TAD score; it reports a qualitative null result for NT-v2 attention.
- A `tables_not_extracted` claim on the article source listing what is still not extracted.
- Two proxy relevance judgements (status needs_review) mapping the expression protocols to `use-case-regulatory-variant-gene-follow-up`.

## Frozen embeddings versus label-free scoring

Every Feng result is a frozen pretrained representation plus a supervised random forest fitted on the task's labels: classification (Tables 1-3), per-gene regression (Table 4), and classification of alternate-minus-reference embedding differences (Tables 5-6). None is a label-free variant-effect or likelihood score. The TAD analysis trains nothing and reports no metric. Every new protocol, configuration and evaluation says so.

## Data access and reproduction constraints

- GTEx v8 individual-level WGS and expression are protected; the expression benchmark is not in the authors' Hugging Face dataset (Data availability). Recorded in `access` on both expression datasets and `access_note` on both protocols.
- The other benchmarks use public files (Hugging Face processed datasets; InstaDeep long-range benchmark for pathogenic variants; Borzoi QTL files and Basenji Hi-C files on Google Cloud Storage).
- The author repository needs a separate GPU environment per model, local checkpoints, and job scripts that take a job index and placeholder paths. The pinned `job_scripts/gtex_hyena.py` reads `long_seqs_by_gene`, crops to 6,000 bp and writes to a folder named `cadph_long`, so the script alone does not show which settings produced each Table 4 row. Recorded in `reproducibility_note` on the expression protocols. Nothing was executed by Rewire.

## Use-case mapping decisions

- Expression (Table 4): proxy for `use-case-regulatory-variant-gene-follow-up`. It tests whether the representation explains inter-individual cis-sequence effects on expression; it does not score variants, link elements to genes or measure perturbations.
- Table 1 rows other than splice sites: not mapped. They classify reference sequences into region types (promoter, enhancer, TFBS, open chromatin, coding). None of the 26 use cases makes that decision, and a mapping would overstate their relevance.
- No change to the existing nine mappings. The splice-site protocols stay on `use-case-splicing-follow-up` and are not mapped to `use-case-patient-rna-splicing-validation`, because they classify sequence windows and use no patient RNA.

## Source discrepancies found

- The main text places the TAD region at about token positions 300-700; the Supplementary Fig. 2 caption says about 200-600.
- The main text calls the expression hyperparameter grid Supplementary Table 6; the PDF prints it as Supplementary Table 5.
- The main text refers to "the 4 mC detection tasks (Table 4)"; 4mC results are in Table 3.
- Supplementary Data 6 gives Enhancer Ensembl the same sizes as Enhancer with a three-class label distribution, though Table 1 reports a binary AUC.
- Already noted by the 7 October batch: the Variant effect text quotes AlphaGenome "AUC = 0.80 for sQTLs"; Table 6 prints 0.7147 for sQTL (0.8029 is eQTL).
