# New use cases: corrections and the reconciled list, 2026-11-27

Reviewer: `claude`, the agent that wrote the use cases. Drafter and reviewer are the same agent; no
human scientific review. An independent verification pass is needed before merge.

Batch: `data/omics/use-case-pages-fixes-20261127/`, built from `extract/spec.json`.

## Corrections to genomic element annotation

A test-by-test reading of every GenBench protocol linked on 27 November found six that are not
genomic element annotation. Their judgements are withdrawn (claim status `excluded`, with the reason)
and their `assessed_by` links removed: bulk RNA expression, 3D genome structure in H1-ESC and HFF,
long-range species classification, human versus worm, and SARS-CoV-2 variant classification. The use
case's exclusions now name expression level, 3D structure and species or lineage classification, so
its 115 remaining judgements were re-pinned by id after this review. The three Drosophila enhancer
activity tasks (STARR-seq activity level) were regraded from `direct` to `proxy`, as GUANinE's
propensity tasks are.

## Reconciling the use case list with the team lead's

The team lead's list and the five candidates of `docs/reviews/2026-11-27-use-case-mapping-gaps.md`
section 5 now map to these use cases:

| Asked for | Created as | Why it differs |
| --- | --- | --- |
| noncoding-genome-annotation; a sequence-classification question for genomic language models | `genomic-sequence-element-annotation` | One use case, not two: GENEB, GUANinE, GenBench, SegmentNT and the NT tasks compare the same models on promoter, enhancer, histone-mark and splice-site labels, which one reader asks together. Coding-region tasks (protein-coding gene, exon, coding versus intergenomic) are in it, so "noncoding" would be wrong. BEND's tasks are task records and cannot be linked yet |
| rna-structure-prediction | `rna-structure-prediction` | Same |
| protein-representation-downstream | `protein-representation-property-prediction` | Same question, named for what is measured |
| mrna-construct-properties | merged into `rna-sequence-property-prediction` | mRNABench's own results are on task records, and its variant-probe protocols have one eligible evaluation each, so no mRNA property comparison can be linked; a separate page would hold nothing. The RNA page says the mRNA comparison is missing |
| metagenomic-taxonomy-research | `viral-microbial-sequence-classification` (new in this batch) | Dropped on the first pass for lack of evidence; reopened here with Bůžková et al. 2026's RVDB viral classification (including a BLAST comparison) and GenBench's species and SARS-CoV-2 variant tasks, two studies. Named for what the evidence measures: no linked test classifies metagenomic reads |
| single-cell data integration and batch correction | `single-cell-data-integration` | Now two studies: Kedzierska et al. 2025's scIB scoring of foundation-model embeddings is linked (`direct` on full embeddings, `proxy` after UMAP). scIB itself, SCMBench and Chen et al.'s clustering cannot be linked: scIB's protocol is not reviewed, and SCMBench's and Chen et al.'s sources carry evidence concerns |
| protein function annotation (CAFA) | `protein-function-annotation` | One study (HyPLM GO and EC probes); CAFA3's protocols are not reviewed. The page says so |
| gene regulatory network inference (BEELINE as one study) | `gene-regulatory-network-inference` | One study; BEELINE is not linked (its protocols are not reviewed) and the page counts it as one study |
| glycan property prediction (GlycanML) | `glycan-property-prediction` | One study (GlycanGT's run of the GlycanML tasks); GlycanML's own results link methods rather than configurations |
| protein design quality (ProteinBench, Genie 3) | `protein-design-quality` | One study (Genie 3); ProteinBench's generation tracks are task records |

Refusals stand as recorded: scIB, SCMBench and clustering for cell-type annotation; mRNABench against
UTR baselines; the others in the candidates file.
