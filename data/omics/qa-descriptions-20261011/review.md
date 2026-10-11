# Review: issue #88 follow-up functional descriptions, 2026-10-11

Reviewer: a separate Claude review agent, independent of the extractor. No human review is claimed.

Verdict: approved with two corrections. All 8 descriptions are supported as written. I corrected the Kraken source's licence (CC BY 2.0, not 4.0) and added a Methods locator to the DNase correlation claim. All 9 batch records are now `source_checked`.

## 1. Scope of the diff

Compared `data/entities/methods.jsonl` and `pipelines.jsonl` with origin/main (`cc9d628`) record by record, with my own script rather than `build.py`.

- Exactly 8 records differ: 7 methods and 1 pipeline. Record order and IDs are unchanged.
- Only `description`, `source_ids` and `attributes.source_locator` changed. `source_ids` gained one entry on Kraken and dilated-resnet; `source_locator` gained a tail on dilated-resnet and the three regulatory-variant records. No existing source or locator text was removed.
- Every claim's `previous_value` equals the origin/main description exactly, `value` equals the working tree, and `source_ids` and `facets` equal the subject's.
- `build.py --check` passes after my edits.

## 2. Sources

All re-downloaded on 2026-10-11 from Europe PMC REST, which needs no email or other identifier.

| Source | Artifact | SHA-256 |
| --- | --- | --- |
| `expansion-p3-mrnabench-2025` | PMC12265608 fullTextXML | Matches the pin (`79f6264e...`) |
| `coverage-source-mimic-2026-v1-html` | arxiv.org/html/2604.24506v1 | Matches the pin (`6408e6fa...`) |
| `dna-pathogen-20261009-source-song2025` | PMC12705909 fullTextXML | Matches the pin (`7b122b55...`) |
| `regulatory-variant-20261009-source-gschwind2026` | PMC13471189 fullTextXML | Matches the pin (`df07ed8c...`) |
| `regulatory-variant-20261009-source-tang2025` | PMC12261763 fullTextXML | Matches the pin (`f6925cc2...`) |
| `ucc-research-source-abdelaal-2019-paper` | PMC6734286 fullTextXML | Matches the pin (`6df0937c...`) |
| `qa-descriptions-20261011-source-kraken` (new) | Europe PMC core search, DOI 10.1186/gb-2014-15-3-r46 | Does not match the pin. See below |

### The new Kraken source

Hash: three retrievals gave the same bytes (`c40f09ae...`), not the pinned `5209b274...`. The collector kept no copy of their retrieval, so I cannot see what differs. The record's `hash_scope` already says these responses are not byte-stable and that the title and abstract are the evidence, and the earlier review found the same for 10 Europe PMC search responses (key order only). I kept the pin, as the skill requires, and recorded the fresh hash in the review block.

Content: the fresh record is MED/24580807, PMC4053813, DOI 10.1186/gb-2014-15-3-r46, "Kraken: ultrafast metagenomic sequence classification using exact alignments.", Wood DE and Salzberg SL, Genome Biology 15(3), March 2014. Its abstractText contains both passages quoted in changes.md. Name, url, DOI, version, `publication_status` and `source_locator` are right.

Duplicates: none. The store's Kraken sources are all for Kraken 2 (repository files and the 2019 paper). Nothing pins the 2014 paper.

Licence: corrected. The search record's licence field is "cc by", with no version. The collector recorded CC-BY-4.0, the convention the earlier review set for such records. The article's own permissions block (PMC4053813 fullTextXML) says "Creative Commons Attribution License (http://creativecommons.org/licenses/by/2.0)", which is what BioMed Central used in 2014. The record now says `CC-BY-2.0`.

So the convention of recording a bare Europe PMC "cc by" as 4.0 does not hold for older BioMed Central articles. Other store sources whose licence was set that way may need the same check, especially BioMed Central articles from before 2015.

## 3. Descriptions against their sources

| Record | Passage checked | Outcome |
| --- | --- | --- |
| `mimic-2026-mrnabench-method-dilated-resnet` | mRNABench Appendix A "Overview of Evaluated Models": "ab-initio supervised dilated CNN ... trained from scratch on the train split ... either three or four DilatedResNetBlocks". MIMIC Table S11 row "Dilated ResNet [71]", where [71] is mRNABench | Supported |
| `dna-pathogen-20261009-method-kraken` | Kraken abstractText: "assigning taxonomic labels to metagenomic DNA sequences"; "Using exact alignment of k-mers" | Supported |
| `regulatory-variant-20261009-method-distance-to-tss` | Gschwind Methods "Collection of published predictions and baseline predictors": "based on distance to TSS"; Supplementary Table 3 predictor "Distance to TSS" (configuration record) | Supported |
| `regulatory-variant-20261009-method-ep-dnase-correlation` | Results "Systematic benchmarking of ENCODE-rE2G": "correlating element and promoter accessibility across cell types"; Methods "Correlation of enhancer–promoter activity across cell types" | Supported; locator added |
| `regulatory-variant-20261009-method-residualbind` | Tang Methods "ResidualBind for lentiMPRA": "adding a dilated residual block after the first convolutional layer of the baseline CNN model"; Results Task 1: "trained a ResidualBind-like model (ResNet) using one-hot sequences" | Supported |
| `ucc-research-method-abdelaal-scmapcell` | Table 1 row scmapcell: kNN, rejection Yes; Results: "assigned as 'unlabeled' if the classifier is not confident enough"; Methods: 16 methods "developed specifically for scRNA-seq data" | Supported |
| `ucc-research-method-abdelaal-scpred` | Table 1 row scPred: "SVM with radial kernel", rejection Yes | Supported |
| `ucc-research-method-abdelaal-svm-linear` | Table 1 rows SVM and SVMrejection: "SVM (linear kernel)", Python 0.19.2, rejection No and Yes; Methods: general-purpose classifiers "from the scikit-learn library", `LinearSVC()` and `LinearSVC()` with `CalibratedClassifierCV()` | Supported |

Each new text is one sentence, says what the method does, and adds no fact beyond its passage. Where the old text carried facts (distance to TSS, DNase-seq at element and promoter, dilated residual design, training on lentiMPRA), the new text keeps them. Where it carried provenance, that is in `source_locator` or the added source.

Notes:

- Distance to TSS: the Results sentence cited in the claim's locator describes the closest-expressed-TSS baseline, a different predictor. It supports only the term "transcription start site". The description rests on the Methods sentence and the predictor name, which is enough.
- ResidualBind: "trained on one-hot sequences" matches the only linked configuration, "Residualbind, LentiMPRA-one-hot". Tang also trained a multi-task ResidualBind-like model on eCLIP data; this record is not linked to it, and "for lentiMPRA activity" keeps the two apart.
- Kraken: Song et al. 2025 ran "Kraken (Wood and Salzberg 2014)" through Galaxy, so the record is Kraken 1, and the 2014 paper is the right source.

## 4. The two flagged choices

Kraken, dropping "lowest common ancestor assignment": agree. The pinned evidence is the abstract, which does not mention it. The full text (PMC4053813, CC BY 2.0) does describe Kraken's LCA mapping, so a later change could pin the full text and restore the phrase. That is not needed for this fix.

DNase correlation, "across cell types": agree. It is the Results sentence's own wording, and the Methods section "Correlation of enhancer–promoter activity across cell types" confirms it: DNase-seq reads were counted at ENCODE4 cCREs and TSSs across 89 biosamples, and Pearson and Spearman correlations and GLS coefficients were computed for cCRE–TSS pairs within 1 Mb. The claim's locator cited only the Results sentence, which does not name DNase-seq. I added the Methods section to it. The description itself is unchanged.

## 5. Records marked

All 8 claims and the Kraken source are `source_checked`. Each has a review block: method, reviewer `claude`, reviewer note, date, method note and a note with the result. The source block also has the fresh `artifact_sha256` and `retrieval_url`. For claims, the collector's note is kept and the review result appended.

The edits are in `build.py`, so `build.py --check` still reproduces the store and `batch.jsonl`:

- `KRAKEN["attributes"]["licence"]`: `CC-BY-4.0` became `CC-BY-2.0`.
- The DNase correlation claim locator gained "; Methods 'Correlation of enhancer–promoter activity across cell types'".
- A block marked "Added by the independent review" sets each record's status and review.

The store edits are unchanged by the review.

## Checks run

Integration, after this review: on the branch, `records -- add` added the 9 batch records (SHACL passed), `build.py` applied the 8 edits and `records -- change` recorded them against this review. After rebasing onto origin/main (`de507ef`), `records check` reported "45613 records match their provenance", `build.py --check` passed, typecheck passed, `npm test` passed 515 of 515 tests in 48 files, and `npm run build` completed. The release files that the build generates locally were discarded rather than committed, because releases are cut by the release workflow.

## Limitations

- An automated review by a Claude agent, not human scientific review.
- The Kraken pin could not be reproduced byte for byte, and no copy of the pinned retrieval exists to compare with.
- Descriptions were checked against the cited sections, not whole papers.
