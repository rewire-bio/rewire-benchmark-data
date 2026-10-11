# Issue #88 category-only descriptions, batch E, 2026-10-11

Scope: the remaining 38 category-only records in `qa-descriptions-20261011/scan.md`, the ones whose description was "Variant effect predictor for missense variants." With batch D's 27, this finishes the 65 category-only records.

All 38 are changed; nothing is skipped and `gaps.md` is empty of records.

The method is the same as batches A to D: one functional sentence from a source, no provenance in the description, and the old text kept in a metadata-correction claim. `build.py` reads the original lines from origin/main, writes `methods.jsonl` in place and regenerates `batch.jsonl`; `--check` verifies without writing. Only `description` and `source_ids` change.

`batch.jsonl` holds 49 records, all `needs_review`: 11 new sources and 38 correction claims.

Integrated together with batches a to e on 2026-10-11, after independent review: see `review.json` in this folder and `docs/reviews/2026-10-11-description-batches-a-e.md`. The records are now `source_checked`. Before review: `records -- add` and `records -- change` were not yet run. In a throwaway copy of origin/main, adding the batch, applying `build.py` and recording the 38 changes passed SHACL, `records check` (45,653 records), typecheck and the canonical-store, attribute, profile, source-identity and evidence-completion tests. I did not run `npm run build`: it needs about 5 GB under `public/` and this machine has around 5 GB free in total, so the reviewer should run it once. The copy was deleted.

## Where the descriptions come from

27 records are described by Chen 2020 (`somatic-oncogenicity-20261009-source-chen2020`), which they already cite. Its Table 1, "Summary of 33 computational algorithms included in this study", gives each algorithm's input features and its method, which is exactly what these family records were missing. Those 27 gain no source. Where Chen 2020 lists two rows under one record (FATHMM disease and cancer, Eigen and Eigen-PC, PolyPhen-2 HumDiv and HumVar, CTAT cancer and population), the description says so, because the record is the family and its configurations carry the variant.

The other 11 are not described in any source they cite, so this batch adds the paper that introduces each one and takes the sentence from it. Chen 2020 predates them and Lee 2026 only groups them by family.

Chen 2020 was re-downloaded on 2026-10-11 and reproduces its `artifact_sha256` (PMC7033911).

## Sources added

Each artifact was retrieved on 2026-10-11 and hashed. Only Europe PMC REST and the arXiv API were used; no email or other personal identifier was sent.

| Source | Artifact | Licence |
| --- | --- | --- |
| `qa-descriptions-20261011-e-source-alphamissense` | Europe PMC core record MED/37733863, title and abstract (Science 2023) | Not stated |
| `qa-descriptions-20261011-e-source-clinpred` | Europe PMC core record MED/30220433, title and abstract (AJHG 2018) | Not stated |
| `qa-descriptions-20261011-e-source-gmvp` | Europe PMC core record MED/37484202, title and abstract (Nature Machine Intelligence 2022) | Not stated |
| `qa-descriptions-20261011-e-source-list-s2` | Europe PMC full-text XML, PMC7319545 (Nucleic Acids Research 2020) | CC BY-NC 4.0 |
| `qa-descriptions-20261011-e-source-metarnn` | Europe PMC full-text XML, PMC9548151 (Genome Medicine 2022) | CC BY 4.0 |
| `qa-descriptions-20261011-e-source-misfit` | Europe PMC full-text XML, PMC12092651 (Nature Communications 2025) | CC BY-NC-ND 4.0 |
| `qa-descriptions-20261011-e-source-mutformer` | arXiv:2110.14746 Atom response, title and abstract | CC BY 4.0 (arXiv abstract page; corrected in review) |
| `qa-descriptions-20261011-e-source-mutscore` | Europe PMC full-text XML, PMC8948164 (AJHG 2022) | CC BY-NC-ND 4.0 |
| `qa-descriptions-20261011-e-source-phactboost` | Europe PMC full-text XML, PMC11251492 (Molecular Biology and Evolution 2024) | CC BY-NC 4.0 |
| `qa-descriptions-20261011-e-source-popeve` | Europe PMC full-text XML, PMC12695638 (Nature Genetics 2025) | CC BY-NC-ND 4.0 |
| `qa-descriptions-20261011-e-source-varity` | Europe PMC full-text XML, PMC8546039 (AJHG 2021) | CC BY 4.0 |

Three of the eleven (AlphaMissense, ClinPred, gMVP) are not open access, so their pinned artifact is the Europe PMC search record and the evidence is its abstract, the same shape batches B and D used. MutFormer has no journal version in Europe PMC; its source is the arXiv preprint that introduces it, whose title names MutFormer. The review set its licence from the arXiv abstract page and extended the MetaRNN source locator to the Background passage that the description's GRU detail comes from. Two Europe PMC records carry the title "Improved pathogenicity prediction for rare human missense variants": the pinned one (PMC8546039) is the VARITY article, and the other (PMC8715197) returns an empty abstract.

## Changed records

### Described from Chen 2020 Table 1 (27)

| Record | Name | New description |
| --- | --- | --- |
| `somatic-oncogenicity-20261009-method-candra` | CanDrA | Scores missense variants with a support vector machine over structural, evolutionary and genomic features together with the scores of published predictors. |
| `somatic-oncogenicity-20261009-method-chasm` | CHASM | Scores missense variants with a random forest over structural, evolutionary and genomic features. |
| `somatic-oncogenicity-20261009-method-ctat` | CTAT (cancer and population ensembles) | Scores missense variants with principal-component ensembles of other predictors: the cancer ensemble combines TransFIC, FATHMM, CHASM and CanDrA, and the population ensemble combines SIFT, PolyPhen-2, MutationAssessor and VEST. |
| `somatic-oncogenicity-20261009-method-dann` | DANN | Scores variants with a deep neural network over conservation, epigenetic signals, the scores of other predictors and genetic context. |
| `somatic-oncogenicity-20261009-method-deogen2` | DEOGEN2 | Scores missense variants with a random forest over evolutionary, protein, gene and pathway features together with PROVEAN scores. |
| `somatic-oncogenicity-20261009-method-eigen` | Eigen | Scores variants by an unsupervised spectral method that combines the scores of other tools, allele frequencies and epigenomic signals; the paper evaluates both the Eigen and the Eigen-PC variant. |
| `somatic-oncogenicity-20261009-method-fathmm-mkl` | FATHMM-MKL | Scores variants by multiple kernel learning over conservation and epigenomic signals. |
| `somatic-oncogenicity-20261009-method-fathmm-xf` | FATHMM-XF | Scores variants by multiple kernel learning over conservation, genomic features and epigenomic signals. |
| `somatic-oncogenicity-20261009-method-fathmm` | FATHMM | Scores missense variants with hidden Markov models over sequence homology; the paper evaluates both the disease-weighted and the cancer-weighted variant. |
| `somatic-oncogenicity-20261009-method-genocanyon` | GenoCanyon | Scores a position by the posterior probability that it is functional, from unsupervised statistical learning over conservation and biochemical annotation. |
| `somatic-oncogenicity-20261009-method-integrated-fitcons` | Integrated_fitCons | Scores the fitness consequences of a position by applying the INSIGHT evolutionary model to integrated epigenomic signals. |
| `somatic-oncogenicity-20261009-method-lrt` | LRT | Scores a variant by a likelihood ratio test of codon neutrality from sequence homology. |
| `somatic-oncogenicity-20261009-method-m-cap` | M-CAP | Scores missense variants with a gradient-boosted tree classifier over the scores of published predictors and conservation. |
| `somatic-oncogenicity-20261009-method-metalr` | MetaLR | Scores missense variants with a logistic regression over nine prediction scores and 1000 Genomes allele frequencies. |
| `somatic-oncogenicity-20261009-method-metasvm` | MetaSVM | Scores missense variants with a radial-kernel support vector machine over nine prediction scores and 1000 Genomes allele frequencies. |
| `somatic-oncogenicity-20261009-method-mpc` | MPC | Scores missense variants with a logistic regression over regional missense constraint, missense badness and PolyPhen-2 scores. |
| `somatic-oncogenicity-20261009-method-mutationassessor` | MutationAssessor | Scores a substitution from sequence homology with a combinatorial entropy formalism. |
| `somatic-oncogenicity-20261009-method-mutationtaster` | MutationTaster | Scores variants with a naive Bayes classifier over conservation, genetic context and regulatory features. |
| `somatic-oncogenicity-20261009-method-mutpred` | MutPred | Scores missense variants with a random forest over protein structural and functional properties, conservation and SIFT scores. |
| `somatic-oncogenicity-20261009-method-mvp` | MVP | Scores missense variants with a deep neural network over sequence and structural features, the scores of published predictors and conservation. |
| `somatic-oncogenicity-20261009-method-polyphen2` | PolyPhen-2 | Scores missense variants with a naive Bayes classifier over eight sequence-based and three structure-based features; the paper evaluates both the HumDiv and the HumVar trained variant. |
| `somatic-oncogenicity-20261009-method-primateai` | PrimateAI | Scores missense variants with a deep residual neural network over sequence homology. |
| `somatic-oncogenicity-20261009-method-provean` | PROVEAN | Scores a substitution by the change it causes in an alignment score against homologous sequences. |
| `somatic-oncogenicity-20261009-method-revel` | REVEL | Scores missense variants with a random forest over the scores of published predictors. |
| `somatic-oncogenicity-20261009-method-sift` | SIFT | Position-specific scoring matrix built from sequence homology found by PSI-BLAST. |
| `somatic-oncogenicity-20261009-method-transfic` | TransFIC | Transforms the functional impact scores of SIFT, PolyPhen-2 and MutationAssessor. |
| `somatic-oncogenicity-20261009-method-vest4` | VEST4 | Scores missense variants with a random forest over amino-acid-related features, DNA context, conservation and protein structure. |

### Described from the paper that introduces the method (11)

| Record | Name | New description |
| --- | --- | --- |
| `somatic-oncogenicity-20261009-method-alphamissense` | AlphaMissense | An adaptation of AlphaFold, fine-tuned on human and primate variant population frequencies, that predicts missense variant pathogenicity from structural context and evolutionary conservation. |
| `somatic-oncogenicity-20261009-method-clinpred` | ClinPred | Scores missense variants by combining two machine-learning algorithms over existing pathogenicity scores and gnomAD population allele frequencies, trained on confidently annotated ClinVar variants. |
| `somatic-oncogenicity-20261009-method-gmvp` | gMVP | Graph attention neural network whose nodes carry amino-acid features and whose edges are weighted by co-evolution strength, pooling information from the local protein context and from correlated distal positions. |
| `somatic-oncogenicity-20261009-method-list-s2` | LIST-S2 | Quantifies the conservation of a position from local sequence identity and taxonomic distances in a multiple alignment, for sequences from any organism rather than human alone. |
| `somatic-oncogenicity-20261009-method-metarnn` | MetaRNN | Recurrent neural network over other predictors' scores, conservation scores and population allele frequencies, with flanking-codon annotations read by bidirectional gated recurrent units, trained to separate rare pathogenic from rare benign nonsynonymous variants; a companion model covers non-frameshift indels. |
| `somatic-oncogenicity-20261009-method-misfit` | MisFit | Graphical model that estimates the fitness effect of a missense variant, jointly modelling its molecular-level effect and its selection coefficient in humans, rather than predicting pathogenicity. |
| `somatic-oncogenicity-20261009-method-mutformer` | MutFormer | Transformer language model over reference and mutated human protein sequences, combining self-attention and convolutional layers, pretrained on protein sequences and fine-tuned for deleteriousness prediction. |
| `somatic-oncogenicity-20261009-method-mutscore` | MutScore | Random forest that combines qualitative features of the DNA substitution with the within-gene positional clustering of pathogenic and benign missense variants. |
| `somatic-oncogenicity-20261009-method-phactboost` | PHACTboost | Gradient-boosted tree classifier that combines PHACT phylogeny-aware scores with features from multiple sequence alignments and phylogenetic trees. |
| `somatic-oncogenicity-20261009-method-popeve` | popEVE | Deep generative model that combines evolutionary and human population data to score variant deleteriousness on a scale calibrated across the proteome. |
| `somatic-oncogenicity-20261009-method-varity` | VARITY | Predicts the pathogenicity of rare missense variants, trained on a larger reservoir of training variants whose accuracy and representativity are uncertain, excluding features informed by variant annotation and protein identity to limit circularity and bias. |

Each of these eleven records keeps the benchmark source it already cited and gains the new one.
