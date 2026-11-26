# Model pages, corrections after independent verification, 2026-11-26

Prepared by Claude agents. No human review is claimed.

## What was checked

Four verifier agents, which had not written the pages, read every statement of the 89 model pages in batches 1 to 4 against the saved source files: the summary, sections, facts, strengths, limitations, diagram, run steps and structured entries. They judged 2,369 statements. They also searched the saved files for every fact marked unreported, unextracted or unavailable, and compared every run-step command with its source.

## What they found

4 statements were wrong and 34 added a detail the sources read do not give; none was wholly unsupported. That is 38 of 2,369, or 1.6 percent. Typical cases: "not gated" stated for every checkpoint when the saved response covered one; a file count that included two folders; a licence attributed to weights when only the code carries it; a date the paper does give, recorded as not given.

## What changed

A fifth agent checked each finding against its source and corrected the content file. All 38 held up. 31 model records have their `profile`, and where a run step was affected their `run_guide`, replaced. No source record is added or changed, and no result, evaluation or claim.

The findings and the corrections are kept beside the content files: `fixes/<model>.verify.json` is the verifier's report and `fixes/<model>.json` lists each change with the text before and after.

## Per model

| Record | Changes | Where |
| --- | --- | --- |
| `gfm-guides-20261014-evo2-brixi2026-model-codonbert` | 1 | fact Code licence |
| `gfm-guides-20261014-evo2-brixi2026-model-decodon` | 2 | section How it works; fact Inputs |
| `gfm2-20261011-you2026-model-utr-lm` | 5 | section Versions and reproducibility; fact Known versions; strength 1; run_guide step Fine-tune for translation efficiency, explanation; fact Model type |
| `lit-genomics-20261011-dnalongbench-model-akita` | 1 | strength 3 |
| `lit-genomics-20261011-geneb-model-biofm` | 1 | fact Code licence |
| `lit-genomics-20261011-geneb-model-deepgene` | 1 | fact Access |
| `lit-genomics-20261011-geneb-model-eccdnamamba` | 3 | fact Training data; strength 3; fact Access |
| `lit-genomics-20261011-geneb-model-evo` | 1 | fact Access |
| `lit-genomics-20261011-geneb-model-genomeocean` | 1 | section How it works |
| `lit-genomics-20261011-geneb-model-genomics-fm` | 1 | fact Access |
| `lit-genomics-20261011-geneb-model-mutbert` | 1 | fact Access |
| `lit-genomics-20261011-geneb-model-omnina` | 1 | fact Known versions |
| `lit-genomics-20261011-geneb-model-plantcaduceus` | 1 | run_guide step Get the code at the pinned commit, explanation |
| `lit-genomics-20261011-geneb-model-space` | 1 | fact Access |
| `lit-genomics-20261011-guanine-model-aido-dna` | 1 | section Versions and reproducibility |
| `lit-genomics-20261011-ntbench-model-bpnet` | 1 | run_guide step Predict on the test chromosomes, explanation |
| `lit-genomics-20261011-traitgym-model-specieslm` | 1 | section Versions and reproducibility |
| `lit-microbial-20261011-virobench-model-omnireg-gpt` | 1 | strength 1 |
| `lit-microbial-20261011-virobench-model-virohyena` | 1 | fact Parameters |
| `lit-rna-20261011-rnagym-model-genslm` | 1 | structured rows for genslm_250M_patric, genslm_2.5B_patric and genslm_25B_patric (parameters), explained in notes |
| `lit-rna-20261011-rnagym-model-rnagenesis` | 1 | structured row 2 (Zaixi/RNAGenesis encoder on Hugging Face), field released |
| `lit-rna-20261011-rnalm-zeroshot-model-ernie-rna` | 1 | strength 3 |
| `lit-rna-20261011-rnalm-zeroshot-model-rfamllama` | 1 | run_guide summary |
| `lit-rna-20261011-rnalm-zeroshot-model-uni-rna` | 1 | section How it works |
| `model-execution-20261011-model-moderngena` | 1 | fact Code licence |
| `regulatory-variant-20261009-model-borzoi` | 1 | section Versions and reproducibility |
| `regulatory-variant-20261009-model-gpn` | 1 | fact Training cutoff |
| `regulatory-variant-20261009-model-hyenadna` | 1 | strength 2 |
| `regulatory-variant-20261009-model-trednet` | 1 | section Versions and reproducibility |
| `traitgym-20261116-model-gpn-promoter` | 1 | limitation 4 |
| `uc20260930-model-framepool` | 1 | fact Known versions |

## Limits

The verifiers judged statements against the files that were saved. A statement can be faithful to its source and the source can still be wrong. No run guide was executed.
