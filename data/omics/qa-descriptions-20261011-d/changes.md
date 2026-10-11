# Issue #88 category-only descriptions, batch D, 2026-10-11

Scope: 27 of the 65 category-only records in `qa-descriptions-20261011/scan.md`:

- the 23 records whose description was "Protein stability-change (ddG) predictor.";
- the 4 records whose description was "Conservation or selection score used as a predictor."

All 27 are changed; nothing is skipped and `gaps.md` is empty of records. The remaining 38 category-only records (the missense variant-effect predictors) are the next batch.

The method is the same as batches A to C: one functional sentence from a source, no provenance in the description, and the old text kept in a metadata-correction claim. `build.py` reads the original lines from origin/main, writes `methods.jsonl` in place and regenerates `batch.jsonl`; `--check` verifies without writing. Only `description` and `source_ids` change.

`batch.jsonl` holds 34 records, all `needs_review`: 7 new sources and 27 correction claims.

Integrated together with batches a to e on 2026-10-11, after independent review: see `review.json` in this folder and `docs/reviews/2026-10-11-description-batches-a-e.md`. The records are now `source_checked`. Before review: `records -- add` and `records -- change` were not yet run. In a throwaway copy of origin/main, adding the batch, applying `build.py` and recording the 27 changes passed SHACL, `records check` (45,638 records), typecheck and the canonical-store, attribute, profile, source-identity and evidence-completion tests. I did not finish `npm run build`: it fills roughly 5 GB under `public/` and this machine had about 1.5 GB free, so I stopped it to avoid starving the other agents, and the reviewer should run it once. The copy was deleted.

## Where the descriptions come from

20 of the 27 are described by a benchmark source the record already cites, so those records gain no source:

- Pancotti 2022 (`protein-stability-20261009-source-pancotti2022`) section 2.2 "Evaluated methods" describes each of the 21 tools it benchmarks in one or two sentences. 16 records are described from it: ACDC-NN, DDGun, mCSM, SDM, DUET, DynaMut, FoldX, SAAFEC-SEQ, MUpro, Rosetta, ThermoNet, PremPS, PoPMuSiC, MAESTRO, INPS and I-Mutant. Where the paper describes a sequence-based and a structure-based version under one name (DDGun and DDGun3D, INPS and INPS3D), the description says so, because these records are family records and their configurations carry the version.
- Dieckhaus 2024 (`protein-stability-20261009-source-dieckhaus2024`) describes ThermoMPNN, which it introduces.
- Chu 2024 (`protein-stability-20261009-source-chu2024`) describes ESM therm, which it introduces, and describes RaSP and ELASPIC-2 in its introduction.

The other 7 are named in their cited benchmark sources only as table rows or in passing, so this batch adds each method's own paper as a source and takes the sentence from it: ABYSSAL, PROSTATA, Stability Oracle, GERP, phastCons, phyloP and the background-selection B value.

## Sources re-checked

The four cited benchmark sources were re-downloaded on 2026-10-11 and all four reproduce their `artifact_sha256`: Pancotti 2022 (PMC8921618), Dieckhaus 2024 (PMC10861915), Chu 2024 (PMC11293664) and Chen 2020 (PMC7033911, used by the next batch). The fifth, `somatic-oncogenicity-20261009-source-lee2026`, is a biorxiv.org full-text HTML page whose bytes differ from the pin, as its own `hash_scope` predicts ("the full-text HTML page, which is mutable"). Nothing in this batch relies on it: Lee 2026 groups the conservation scores by family rather than describing them, which is why the 4 conservation records get their own papers.

## Sources added

Each artifact was retrieved on 2026-10-11 and hashed. Only Europe PMC REST was used; no email or other personal identifier was sent.

| Source | Artifact | Licence |
| --- | --- | --- |
| `qa-descriptions-20261011-d-source-abyssal` | Europe PMC core record PPR/PPR590902, title and abstract (bioRxiv preprint) | Not stated |
| `qa-descriptions-20261011-d-source-prostata` | Europe PMC full-text XML, PMC10651431 (Bioinformatics 2023) | CC BY 4.0 |
| `qa-descriptions-20261011-d-source-stability-oracle` | Europe PMC full-text XML, PMC11266546 (Nature Communications 2024) | CC BY 4.0 |
| `qa-descriptions-20261011-d-source-gerp` | Europe PMC full-text XML, PMC2996323 (PLoS Computational Biology 2010, GERP++) | CC BY 4.0 |
| `qa-descriptions-20261011-d-source-phastcons` | Europe PMC core record MED/16024819, title and abstract (Genome Research 2005) | Not stated |
| `qa-descriptions-20261011-d-source-phylop` | Europe PMC core record MED/19858363, title and abstract (Genome Research 2010) | Not stated |
| `qa-descriptions-20261011-d-source-bstatistic` | Europe PMC full-text XML, PMC2669884 (PLoS Genetics 2009) | CC BY 4.0 |

Which paper defines each score is Lee 2026's own citation: it lists its conservation features as "GERP++ [34], phyloP [35], phastCons [36]; background-selection B-statistic [37]", whose references are Davydov 2010, Pollard 2010, Siepel 2005 and McVicker 2009. The record named GERP therefore takes the GERP++ paper, which is the score Lee 2026 used.

phastCons and phyloP are not open access, so their pinned artifact is the Europe PMC search record and the evidence is its abstract. Each abstract states what the score is, which is all these family records need. The four records that gain one of these sources keep the benchmark source they already cited.

## Changed records

### ddG predictors described from Pancotti 2022, section 2.2

| Record | New description |
| --- | --- |
| `protein-stability-20261009-method-acdc-nn` | Neural-network predictor of the stability change on point mutation whose architecture is antisymmetric by construction, taking the amino acids neighbouring the mutation and multiple sequence alignments as input. |
| `protein-stability-20261009-method-ddgun` | Untrained predictor that combines evolutionary information with statistical potentials in an antisymmetric linear score; the 3D version adds a structural statistical potential weighted by the accessibility of the mutated residue. |
| `protein-stability-20261009-method-mcsm` | Predicts the effect of a point mutation on stability from graph-based structural signatures that encode the distance patterns between atoms in the residue environment. |
| `protein-stability-20261009-method-sdm` | Statistical potential energy function that scores a mutation from environment-specific amino-acid substitution frequencies within homologous families, as a proxy for the free-energy difference between wild type and mutant. |
| `protein-stability-20261009-method-duet` | Meta-predictor that combines the mCSM and SDM scores with a support vector machine. |
| `protein-stability-20261009-method-dynamut` | Consensus machine-learning predictor that combines the effects of a mutation on stability and on dynamics as computed by DUET, Bio3D and ENCoM. |
| `protein-stability-20261009-method-foldx` | Empirical force-field method that predicts the effect of a point mutation from a linear combination of free-energy terms, including an entropy contribution, Van der Waals forces, hydrogen bonds and electrostatic interactions. |
| `protein-stability-20261009-method-saafec-seq` | Gradient-boosting decision-tree predictor that uses physico-chemical properties, sequence features and evolutionary information. |
| `protein-stability-20261009-method-mupro` | Sequence-based support vector machine that encodes the residues in a window centred on the mutated position. |
| `protein-stability-20261009-method-rosetta` | Computes the stability change as the difference in Rosetta energy between the simulated wild-type and mutant structures. |
| `protein-stability-20261009-method-thermonet` | Deep 3D convolutional network that predicts the stability change from multi-channel voxel grids of biophysical properties derived from atom coordinates. |
| `protein-stability-20261009-method-premps` | Random-forest regression predictor that uses evolutionary and structure-based features, trained on a dataset with equal numbers of stabilising and destabilising mutations. |
| `protein-stability-20261009-method-popmusic` | Energy-function method that combines 13 statistical potentials with volume-dependent terms for the wild-type and mutant amino acids, weighted by the solvent accessibility of the mutated residue. |
| `protein-stability-20261009-method-maestro` | Multi-agent predictor based on statistical scoring functions, combining an ensemble of neural networks, support vector regressors and multiple linear regressors into a consensus model. |
| `protein-stability-20261009-method-inps` | Support vector method with a radial-basis-function kernel over BLOSUM62 substitution scores, the alignment-score difference between native and variant sequence, hydrophobicity and evolutionary information; the 3D version adds relative solvent accessibility and a structural statistical potential. |
| `protein-stability-20261009-method-i-mutant` | Support vector method with a radial-basis-function kernel over 42 features, including temperature, pH, an encoding of the mutation, and an encoding of the spatial residue environment where a structure is available or of the nearest sequence neighbours otherwise. |

### ddG predictors described from the paper that introduces them

| Record | Source | New description |
| --- | --- | --- |
| `protein-stability-20261009-method-thermompnn` | Dieckhaus 2024, Abstract | Deep neural network that predicts the stability change of a point mutation from an input structure, by transfer learning on features extracted from ProteinMPNN. |
| `protein-stability-20261009-method-esm-therm` | Chu 2024, Abstract and Introduction | Protein language model fine-tuned on the folding stability of 528,000 natural and de novo sequences from 461 protein domains, which also accommodates deletions, insertions and multiple-point mutations. |
| `protein-stability-20261009-method-rasp` | Chu 2024, Introduction | Convolutional-neural-network stability predictor trained on Rosetta-computed stability changes, operating directly on the input protein structure. |
| `protein-stability-20261009-method-elaspic-2` | Chu 2024, Introduction | Stability predictor that operates on both an ESM sequence embedding and a graph-neural-network structural embedding. |
| `protein-stability-20261009-method-abyssal` | new source, abstract | ESM-2 network with an added light-attention mechanism, trained on the mega-scale stability dataset, which predicts the stability change on single mutation and satisfies the antisymmetry property. |
| `protein-stability-20261009-method-prostata` | new source, Abstract | Transformer-based model, built by knowledge transfer on a curated stability dataset, that predicts the change in protein stability on point mutation from sequence. |
| `protein-stability-20261009-method-stability-oracle` | new source, Abstract | Structure-based graph-transformer framework for identifying thermodynamically stabilising mutations, trained with thermodynamic permutations for data augmentation and structural amino-acid embeddings that represent a mutation from a single structure. |

### Conservation or selection scores

| Record | Source | New description |
| --- | --- | --- |
| `somatic-oncogenicity-20261009-method-gerp` | new source, Abstract | Scores selective constraint position by position in a multiple alignment by maximum-likelihood evolutionary rate estimation, and defines constrained elements from runs of high-scoring positions by dynamic programming. |
| `somatic-oncogenicity-20261009-method-phastcons` | new source, abstract | Conservation score from a two-state phylogenetic hidden Markov model fitted to a multiple alignment by maximum likelihood, from which conserved elements are predicted. |
| `somatic-oncogenicity-20261009-method-phylop` | new source, abstract | Tests whether the substitution rate at a site departs from the neutral rate, in either direction and optionally within a particular clade of the phylogeny. |
| `somatic-oncogenicity-20261009-method-bstatistic` | new source, Results | The background-selection B value: the expected fraction of neutral diversity remaining at a site, computed from the local recombination rate and the density of conserved segments. |

McVicker 2009 defines B as "the expected fraction of neutral diversity that is present at a site", with values near 0 meaning diversity has been almost entirely removed by selection. The description says what the score is and does not claim which release of the track a given result used, which stays on the configurations.
