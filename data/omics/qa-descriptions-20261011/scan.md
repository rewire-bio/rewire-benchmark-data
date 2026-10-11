# Description scan for issue #88, 2026-10-11

Scope: every model, method and pipeline record on origin/main (613). A record is listed when its description matches one of the issue's patterns:
- text shared with another record;
- provenance phrasing ("as run in", "quoted in", "not a new execution", "identified in the cited", "as reported", "evaluated pipeline", "configuration of");
- an author, year, "Table" or "et al." in the text;
- fewer than six words;
- text equal to the record's name.

403 records match. Each is counted once, in the first group that fits, in the order below. No record was edited for this scan. The 8 records in this batch (changes.md) are marked "in this batch" or noted below.

Classes:
- **Placeholder**: says nothing about what the method does. These need a new description from a primary source.
- **Category only**: names a kind of tool, but the same text is shared by many different tools, so it does not distinguish them.
- **Mostly provenance**: says who trained or ran it, with little or nothing about the method itself.
- **Thin**: a category label of a few words rather than a sentence. It is functional but minimal; 43 of these are `discovered` catalogue records.
- **Stylistic**: functional text that also carries a locator, citation or year, or functional text legitimately shared by closely related tools. These need only light edits, or none.

| Class | Records |
| --- | --- |
| Placeholder | 167 |
| Category only | 65 |
| Mostly provenance | 22 |
| Thin | 75 |
| Stylistic | 74 |
| **Total** | **403** |

### Placeholder: 167 records

| Group | Count | Kinds | Statuses | Example IDs |
| --- | --- | --- | --- | --- |
| Linear-probe baseline placeholder | 49 | pipeline 49 | source_checked 49 | `mrnabench-variants-2025-method-aido-rna-1b600m`, `mrnabench-variants-2025-method-aido-rna-1b600m-cds`, `mrnabench-variants-2025-method-aido-rna-650m` |
| "Identity as reported in this paper" | 35 | pipeline 29, model 6 | needs_review 29, excluded 6 | `reported-model-0330736fd30b81`, `reported-model-74844d9e698bcd`, `reported-model-91d4548437068f` |
| Catalogue candidate placeholder | 26 | model 23, method 3 | discovered 26 | `catalog-model-alphagenome`, `catalog-model-boltz-2`, `catalog-model-chai-1` |
| "Language model identity as reported in this source" | 16 | model 16 | source_checked 16 | `tgtval-20261009-model-claude-3-5-sonnet`, `tgtval-20261009-model-claude-3-haiku`, `tgtval-20261009-model-claude-3-opus` |
| "Named prediction method identified in the cited primary source" | 8 | method 8 | source_checked 8 | `uc20260930-method-blasso-rhodopsin-predictor`, `uc20260930-method-evmutation`, `uc20260930-method-frame-aware-k-mer-random-forest` |
| "Method identity" in a named comparison (TAPE, scTab) | 12 | method 7, model 5 | discovered 6, source_checked 6 | `discovery-model-tape-bepler`, `discovery-model-tape-lstm`, `discovery-model-tape-resnet` |
| "Method or ablation in the primary-source enhancer-gene benchmark" | 6 | method 6 | source_checked 6 | `ucc-research-method-mprabc-abc`, `ucc-research-method-mprabc-full`, `ucc-research-method-mprabc-megamap` |
| "Method identity used in the Abdelaal et al. 2019 comparison" (in this batch) | 3 | method 3 | source_checked 3 | `ucc-research-method-abdelaal-scmapcell`, `ucc-research-method-abdelaal-scpred`, `ucc-research-method-abdelaal-svm-linear` |
| "Base method introduced by <author> (<year>)" | 2 | model 2 | source_checked 2 | `identity-model-deepaffinity`, `identity-model-deepdta` |
| scFoundation Table 4 pipelines ("reported in the primary table") | 7 | pipeline 7 | source_checked 7 | `scfoundation-2024-supp-table4-method-actinn`, `scfoundation-2024-supp-table4-method-celltypist`, `scfoundation-2024-supp-table4-method-scanpy` |
| "represented by its exact FoldBench configuration" | 2 | model 2 | source_checked 2 | `ucc-research-model-helixfold3`, `ucc-research-model-protenix` |
| "Prior mRNABench evaluated pipeline ... not a new execution" (in this batch) | 1 | pipeline 1 | source_checked 1 | `mimic-2026-mrnabench-method-dilated-resnet` |

### Category only: 65 records

| Group | Count | Kinds | Statuses | Example IDs |
| --- | --- | --- | --- | --- |
| "Variant effect predictor for missense variants." | 38 | method 38 | source_checked 38 | `somatic-oncogenicity-20261009-method-alphamissense`, `somatic-oncogenicity-20261009-method-candra`, `somatic-oncogenicity-20261009-method-chasm` |
| "Protein stability-change (ddG) predictor." | 23 | method 23 | source_checked 23 | `protein-stability-20261009-method-abyssal`, `protein-stability-20261009-method-acdc-nn`, `protein-stability-20261009-method-ddgun` |
| "Conservation or selection score used as a predictor." | 4 | method 4 | source_checked 4 | `somatic-oncogenicity-20261009-method-bstatistic`, `somatic-oncogenicity-20261009-method-gerp`, `somatic-oncogenicity-20261009-method-phastcons` |

### Mostly provenance: 22 records

| Group | Count | Kinds | Statuses | Example IDs |
| --- | --- | --- | --- | --- |
| Benchmark-author baselines ("trained ... by the <benchmark> authors") | 22 | method 22 | source_checked 22 | `atom3d-method-3dcnn`, `atom3d-method-enn`, `atom3d-method-gnn` |

### Thin: 75 records

| Group | Count | Kinds | Statuses | Example IDs |
| --- | --- | --- | --- | --- |
| Category label under six words, no sentence | 75 | method 41, model 30, pipeline 4 | discovered 43, source_checked 32 | `discovery-model-agro-nucleotide-transformer`, `discovery-model-alphafold-3`, `discovery-model-basenji` |

### Stylistic: 74 records

| Group | Count | Kinds | Statuses | Example IDs |
| --- | --- | --- | --- | --- |
| Locator in the text: "(Table 1)", "(paper Table 4)", "Table S4", "MIMIC Table S11" | 19 | pipeline 15, model 3, method 1 | source_checked 15, needs_review 4 | `cell-type-20261009-model-langcell`, `cell-type-20261009-model-sccello`, `cell-type-20261009-model-uce` |
| Author citation in the text ("Defined in Hou et al. ref N", "of Xiong et al.", "computed by Gschwind et al. 2026") | 15 | method 15 | source_checked 15 | `ctdnafrag-20261009-method-end-motif`, `ctdnafrag-20261009-method-fragment-coverage`, `ctdnafrag-20261009-method-fragment-end-count` |
| Year in the text only (TREC 2020 systems, a model version date) | 15 | method 14, model 1 | source_checked 15 | `egfrnsclc-20261009-model-gpt-4o`, `dna-pathogen-20261009-method-kraken`, `egfrnsclc-20261009-method-trec2020-pm-alibaba` |
| Functional text shared by related tools (for example "Short-read fusion caller using STAR alignments.") | 24 | method 22, model 2 | source_checked 24 | `egfrnsclc-20261009-model-llama-3-1-70b`, `egfrnsclc-20261009-model-qwen-2-5-72b`, `cnv-20261009-method-delly` |
| Other provenance phrasing ("cited as", "in one linked comparison") | 1 | method 1 | source_checked 1 | `somatic-20261009-method-neusomatic` |

## Notes

- `dna-pathogen-20261009-method-kraken` (in this batch) is counted under "Year in the text only", because "cited as Wood and Salzberg 2014" matches the year pattern before the provenance one.
- The "Identity as reported in this paper" group includes 6 `excluded` model records, which are not published.
- "Functional text shared by related tools" is usually acceptable: for example, two structural variant callers that the source describes in the same words. A reviewer may still want each tool's own sentence.
- The counts come from the patterns above. A record can fail the issue in a way the patterns miss, and some matches (the TREC 2020 systems) are fine as written.
