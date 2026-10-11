# Issue #88 follow-up: functional descriptions, 2026-10-11

Scope: `mimic-2026-mrnabench-method-dilated-resnet`, left unchanged by qa-descriptions-20261010 (its review, section 4), and the seven borderline method records listed under "Later follow-up for #88" in qa-suffix-reasons-20261010/review.md.

Method, as in qa-descriptions-20261010:
- one sentence saying what the method does, written from its primary source;
- provenance kept out of the description, in `attributes.source_locator`, or carried by a source in `source_ids`;
- the old text kept in a metadata-correction claim.

The store is edited in place in `data/entities/methods.jsonl` (7 lines) and `data/entities/pipelines.jsonl` (1 line). `build.py` reads the original lines from origin/main, applies the changes, writes the store files and regenerates `batch.jsonl`; `build.py --check` repeats the checks without writing. Only `description`, `source_ids` and `attributes.source_locator` change, and the script asserts that.

`batch.jsonl` holds 9 records, all `needs_review`: one new source (the Kraken paper's Europe PMC record) and 8 correction claims, each with `previous_value` equal to origin/main and `value` equal to the new description.

Not done: `records -- add` and `records -- change`. In a throwaway copy of origin/main, adding `batch.jsonl`, applying `build.py` and recording the 8 changes passed SHACL, `records check` (45,613 records) and the source-identity, attribute and evidence-completion tests. That copy was deleted.

## Sources read

Each artifact was re-downloaded on 2026-10-11 and hashed. No email or other personal identifier was sent; Europe PMC REST needs none.

| Source | Artifact | SHA-256 against the pin |
| --- | --- | --- |
| `expansion-p3-mrnabench-2025` | Europe PMC full text PMC12265608 | Matches (`79f6264e...`) |
| `dna-pathogen-20261009-source-song2025` | Europe PMC full text PMC12705909 | Matches (`7b122b55...`) |
| `regulatory-variant-20261009-source-gschwind2026` | Europe PMC full text PMC13471189 | Matches (`df07ed8c...`) |
| `regulatory-variant-20261009-source-tang2025` | Europe PMC full text PMC12261763 | Matches (`f6925cc2...`) |
| `ucc-research-source-abdelaal-2019-paper` | Europe PMC full text PMC6734286 | Matches (`6df0937c...`) |
| `qa-descriptions-20261011-source-kraken` (new) | Europe PMC core search record MED/24580807, PMC4053813 | New pin `5209b274...`; licence CC BY per the record |

## Changed records

### `mimic-2026-mrnabench-method-dilated-resnet` (pipeline)

- Old: Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution.
- New: Supervised dilated convolutional network baseline, built from three or four DilatedResNet blocks and trained from scratch on each task's training split.
- Source: `expansion-p3-mrnabench-2025`, Appendix A "Overview of Evaluated Models", baselines paragraph: "we include an ab-initio supervised dilated CNN comparison. This model is trained from scratch on the train split in evaluations. This supervised CNN uses a DilatedResNet architecture consiting of either three or four DilatedResNetBlocks."
- Provenance: the old text is appended to `attributes.source_locator`, as on the ten sibling MIMIC pipelines. `expansion-p3-mrnabench-2025` is added to `source_ids`.
- The review of qa-descriptions-20261010 proposed a version ending "with task scores quoted from prior work in MIMIC Table S11". That clause is provenance, so it is kept in `source_locator` instead.

### `dna-pathogen-20261009-method-kraken` (method)

- Old: Exact k-mer classifier with lowest common ancestor assignment, cited as Wood and Salzberg 2014.
- New: Classifier that assigns taxonomic labels to metagenomic DNA sequences by exact alignment of k-mers.
- Source: the new `qa-descriptions-20261011-source-kraken`, Wood and Salzberg 2014, "Kraken: ultrafast metagenomic sequence classification using exact alignments", Genome Biology, DOI 10.1186/gb-2014-15-3-r46, abstractText: "Kraken is an ultrafast and highly accurate program for assigning taxonomic labels to metagenomic DNA sequences ... Using exact alignment of k-mers, Kraken achieves classification accuracy comparable to the fastest BLAST program."
- Song et al. 2025 (the record's existing source, Methods "Data Analysis" paragraph 1) names Kraken only by the citation, so it does not support any functional wording.
- "Lowest common ancestor assignment" is dropped. It is true of Kraken, but the pinned abstract does not state it, and the body of the paper is not pinned.
- Provenance: the citation is now the added source.

### `regulatory-variant-20261009-method-distance-to-tss` (method)

- Old: Baseline that ranks element-gene pairs by distance from the element to the gene's TSS, computed by Gschwind et al. 2026 (Methods 'Collection of published predictions and baseline predictors').
- New: Baseline that ranks element-gene pairs by the distance from the element to the gene's transcription start site.
- Source: `regulatory-variant-20261009-source-gschwind2026`, Methods "Collection of published predictions and baseline predictors": "Baseline predictors were generated for 1,458 biosamples based on distance to TSS, nearest expressed gene and variants thereof". Results "Systematic benchmarking of ENCODE-rE2G" lists "linking elements to the closest expressed transcription start site (TSS)" among the simple baselines.
- Provenance: "baseline computed by Gschwind et al. 2026, Methods 'Collection of published predictions and baseline predictors'" is appended to `attributes.source_locator`.

### `regulatory-variant-20261009-method-ep-dnase-correlation` (method)

- Old: Baseline using the correlation of DNase-seq signal at the element and the promoter, computed by Gschwind et al. 2026 (Supplementary Table 3 row label).
- New: Baseline that links elements to genes by correlating DNase-seq accessibility at the element and at the gene's promoter across cell types.
- Source: `regulatory-variant-20261009-source-gschwind2026`, Results "Systematic benchmarking of ENCODE-rE2G": the simple baselines include "correlating element and promoter accessibility across cell types".
- Provenance: "baseline computed by Gschwind et al. 2026, Supplementary Table 3 row label" is appended to `attributes.source_locator`.
- For review: "across cell types" comes from the Results sentence. The old text said only "correlation of DNase-seq signal".

### `regulatory-variant-20261009-method-residualbind` (method)

- Old: Residual dilated CNN architecture defined by Tang et al. 2025 (Methods 'ResidualBind for lentiMPRA') and trained on lentiMPRA by them.
- New: Convolutional network for lentiMPRA activity that adds a dilated residual block after the first convolutional layer of a baseline CNN and is trained on one-hot sequences.
- Source: `regulatory-variant-20261009-source-tang2025`, Methods "ResidualBind for lentiMPRA": "We designed the ResidualBind model by adding a dilated residual block after the first convolutional layer of the baseline CNN model". Results "Task 1": "we trained a ResidualBind-like model (ResNet) using one-hot sequences".
- Provenance: "defined and trained on lentiMPRA by Tang et al. 2025, Methods 'ResidualBind for lentiMPRA'" is appended to `attributes.source_locator`.

### `ucc-research-method-abdelaal-scmapcell` (method)

- Old: Method identity used in the Abdelaal et al. 2019 comparison.
- New: Cell-type classifier for single-cell RNA-seq data that labels each cell with a k-nearest-neighbour classifier and can leave cells unlabelled.
- Source: `ucc-research-source-abdelaal-2019-paper`, Table 1, row "scmapcell": underlying classifier "kNN", rejection option "Yes". Results "All classifiers perform well in intra-dataset experiments": with a rejection option "a cell is assigned as 'unlabeled' if the classifier is not confident enough".
- Provenance: `source_locator` already reads Table 1, row "scmapcell"; nothing moves.

### `ucc-research-method-abdelaal-scpred` (method)

- Old: Method identity used in the Abdelaal et al. 2019 comparison.
- New: Cell-type classifier for single-cell RNA-seq data built on a support vector machine with a radial kernel, which can leave cells unlabelled.
- Source: `ucc-research-source-abdelaal-2019-paper`, Table 1, row "scPred": underlying classifier "SVM with radial kernel", rejection option "Yes".
- Provenance: `source_locator` already reads Table 1, row "scPred"; nothing moves.

### `ucc-research-method-abdelaal-svm-linear` (method)

- Old: Method identity used in the Abdelaal et al. 2019 comparison.
- New: General-purpose support vector machine classifier with a linear kernel from scikit-learn, used with and without a rejection option that leaves low-confidence cells unlabelled.
- Source: `ucc-research-source-abdelaal-2019-paper`, Table 1, rows "SVM" and "SVM rejection": "SVM (linear kernel)", Python, version 0.19.2, rejection option "No" and "Yes". Methods "Classification methods": "support vector machine (SVM) with linear kernel, SVM with rejection option (SVM rejection)", from "the scikit-learn library in Python".
- Provenance: `source_locator` already reads Table 1, rows "SVM" and "SVM rejection"; nothing moves.

## For the reviewer

- Check each new sentence against the quoted passage. Two choices to look at: "across cell types" for the DNase correlation baseline, and dropping "lowest common ancestor" for Kraken.
- Re-download the new Kraken source. Europe PMC search responses are not byte-stable, so the title and abstractText are the evidence (see its `hash_scope`).
- Then set the 9 batch records to `source_checked` with a review block, or correct them in `build.py` and rerun it.

## Integration, after review

```
npm run records -- add data/omics/qa-descriptions-20261011/batch.jsonl data/omics/qa-descriptions-20261011
npm run records -- change data/omics/qa-descriptions-20261011/review.md data/omics/qa-descriptions-20261011 <the 8 record IDs above>
```

Add the batch first: the edited Kraken record cites the new source, so `records -- change` cannot validate the store until that source is in it.
