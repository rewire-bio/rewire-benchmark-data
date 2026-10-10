# Store form: source_label removed

`batch.jsonl` is the reviewed batch and is unchanged, so the receipt in `review.json` still binds the reviewed bytes.

`source_label` is reserved for records renamed through a reviewed `source_identity` (`shared/omics/source-identity.ts`). The store copies of the 46 Wu et al. 2025 evaluations below had a label of the form "Row label as printed: <name>" and no identity. Under rule 2, the printed row name was appended to `source_locator` as `; row '<name>'`, for example "Table S3 row 18; row 'Geneformer + LangCell'", and `source_label` was removed.

No other field and no value changed.

| Record | Rule |
| --- | --- |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-ensemble-geneformer-langcell` | 2: appended row 'Geneformer + LangCell' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-ensemble-geneformer-sccello` | 2: appended row 'Geneformer + scCello' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-ensemble-geneformer-scfoundation` | 2: appended row 'Geneformer + scFoundation' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-ensemble-geneformer-scgpt` | 2: appended row 'Geneformer + scGPT' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-ensemble-geneformer-uce` | 2: appended row 'Geneformer + UCE' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-ensemble-langcell-sccello` | 2: appended row 'LangCell + scCello' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-ensemble-langcell-scfoundation` | 2: appended row 'LangCell + scFoundation' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-ensemble-langcell-scgpt` | 2: appended row 'scGPT + LangCell' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-ensemble-langcell-uce` | 2: appended row 'UCE + LangCell' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-ensemble-logit-aggregation` | 2: appended row 'Logit aggregation' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-ensemble-majority-voting` | 2: appended row 'Majority voting' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-ensemble-sccello-scfoundation` | 2: appended row 'scFoundation + scCello' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-ensemble-sccello-scgpt` | 2: appended row 'scGPT + scCello' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-ensemble-sccello-uce` | 2: appended row 'UCE + scCello' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-ensemble-scfoundation-scgpt` | 2: appended row 'scGPT + scFoundation' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-ensemble-scfoundation-uce` | 2: appended row 'UCE + scFoundation' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-ensemble-scgpt-uce` | 2: appended row 'scGPT + UCE' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-geneformer-onclass` | 2: appended row 'Geneformer' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-langcell-onclass` | 2: appended row 'LangCell' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-sccello-onclass` | 2: appended row 'scCello' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-scfoundation-onclass` | 2: appended row 'scFoundation' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-scgpt-onclass` | 2: appended row 'scGPT' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-hlca-to-ts-uce-onclass` | 2: appended row 'UCE' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-ensemble-geneformer-langcell` | 2: appended row 'Geneformer + LangCell' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-ensemble-geneformer-sccello` | 2: appended row 'Geneformer + scCello' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-ensemble-geneformer-scfoundation` | 2: appended row 'Geneformer + scFoundation' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-ensemble-geneformer-scgpt` | 2: appended row 'Geneformer + scGPT' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-ensemble-geneformer-uce` | 2: appended row 'Geneformer + UCE' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-ensemble-langcell-sccello` | 2: appended row 'LangCell + scCello' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-ensemble-langcell-scfoundation` | 2: appended row 'LangCell + scFoundation' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-ensemble-langcell-scgpt` | 2: appended row 'scGPT + LangCell' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-ensemble-langcell-uce` | 2: appended row 'UCE + LangCell' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-ensemble-logit-aggregation` | 2: appended row 'Logit aggregation' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-ensemble-majority-voting` | 2: appended row 'Majority voting' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-ensemble-sccello-scfoundation` | 2: appended row 'scFoundation + scCello' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-ensemble-sccello-scgpt` | 2: appended row 'scGPT + scCello' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-ensemble-sccello-uce` | 2: appended row 'UCE + scCello' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-ensemble-scfoundation-scgpt` | 2: appended row 'scGPT + scFoundation' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-ensemble-scfoundation-uce` | 2: appended row 'UCE + scFoundation' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-ensemble-scgpt-uce` | 2: appended row 'scGPT + UCE' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-geneformer-onclass` | 2: appended row 'Geneformer' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-langcell-onclass` | 2: appended row 'LangCell' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-sccello-onclass` | 2: appended row 'scCello' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-scfoundation-onclass` | 2: appended row 'scFoundation' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-scgpt-onclass` | 2: appended row 'scGPT' to source_locator, source_label removed |
| `cell-type-20261009-eval-wu2025-ts-to-hlca-uce-onclass` | 2: appended row 'UCE' to source_locator, source_label removed |
