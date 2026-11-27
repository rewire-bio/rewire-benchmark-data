# New use cases from the unmapped evidence, 2026-11-27

Reviewer: `claude`, the agent that wrote them, by reading each benchmark and protocol record and its
saved sources, checking every linked protocol against the use case's own question and exclusions, and
verifying the evaluation gates of `shared/omics/use-cases.ts` and the source hashes. Drafter and
reviewer are the same agent, so this is not the second-worker review `docs/use-cases.md` requires:
nine use cases and 254 judgements go live on merge without one. No human scientific review is
claimed, and an independent verification pass is needed.

Batch: `data/omics/use-case-pages-20261127/`. The questions come from
`docs/reviews/2026-11-27-use-case-mapping-gaps.md`, section 5. Every link is listed with the passage
it rests on in that batch's `applied.jsonl`.

## The use cases

| Use case | Protocols linked | Studies its evidence rests on |
| --- | --- | --- |
| `genomic-sequence-element-annotation` | 121 | 5: GenBench, the GENEB leaderboard, SegmentNT, the Nucleotide Transformer benchmark, GUANinE v1.1 |
| `rna-structure-prediction` | 42 | 2: Ludaic and Elofsson 2026, the RhoFold+ CASP15 table |
| `rna-sequence-property-prediction` | 32 | 2: Wang et al. 2026, the RNAGym fitness leaderboard |
| `glycan-property-prediction` | 21 | 1: the GlycanGT paper's Table S4 |
| `protein-representation-property-prediction` | 17 | 1: the HyPLM technical report |
| `single-cell-data-integration` | 9 | 1: the HyCell technical report |
| `protein-function-annotation` | 6 | 1: the HyPLM technical report |
| `protein-design-quality` | 5 | 1: the Genie 3 paper's Table 3 |
| `gene-regulatory-network-inference` | 1 | 1: the geneRNIB result in the PerturbPFN paper, whose comparators are copied figures the board leaves out |

Each use case names its study count in `evidence_gaps`, so a one-study page does not read as settled.
None carries `evidence_checked`: no literature search ran for these questions, so each reads as not
yet checked. `depth_tier` follows the rule in `shared/omics/depth-tier.ts` from each use case's areas,
and `npm run depth-tier -- check` reports no record differing from it.

Two of the nine boards gain an ordering: genomic element annotation orders 6 models from 162
comparison groups in 5 studies (Nucleotide Transformer and GENA-LM share positions 1 to 2), and RNA
sequence properties 6 models from 32 groups in 2 studies. RNA structure orders 2. The rest have one
study and say so.

## Rulings on scope

- **Genomic sequence annotation is one question, separate from variant effect.** The same models are
  compared on promoter, enhancer, histone-mark and splice-site classification by one probe or one
  fine-tuning recipe per benchmark, and a reader choosing a model asks them together. Variant effect
  prediction is a different decision with four existing use cases, so it stays out, and the splice-site
  tasks are `proxy` here because the splicing use cases hold the same tasks: grading them `direct` in
  both places would present one comparison as two independent ones.
- **RNA splits in two.** Structure prediction and sequence-property prediction have different inputs,
  different users and no shared metric, so they are two use cases. Wang et al. 2026's attention-derived
  secondary structure is excluded from the structure use case, because that use case's own exclusions
  name it: it measures what a language model learned, not a structure to act on. Its family, type and
  fitness tasks are `direct` on the sequence-property use case.
- **Single-cell integration is separate from annotation transfer.** The existing
  `cell-type-annotation-transfer` use case excludes batch mixing and embedding separation in as many
  words, so those scores needed their own question. The HyCell annotation-transfer protocols stay on
  the annotation use case (batch `use-case-mapping-gaps-20261127`) and are not repeated here.
- **Protein representation probing is separate from protein variant effect.** The zero-shot ProteinGym
  protocols of the HyPLM report measure likelihood scoring, which is the existing
  `protein-variant-effect-prediction` question, so they are excluded here; so are the GO and EC probes,
  which went to protein function annotation, the perplexity and likelihood protocols, which measure the
  model's fit to sequences rather than a property, the FLIP stability landscape, which is the
  `protein-stability` question, and the embedding-throughput measure, which is a cost. Whole-protein
  melting temperature (meltome, thermostability) is kept: it is a measured property of the protein, not
  the folding stability of a substitution.
- **Protein design quality is unconditional generation only.** Designing a binder to a chosen target is
  the existing `de-novo-binder-design` use case. Every measure linked here is computational, and the use
  case says so.
- **Dropped: classifying viral and microbial sequences.** It is a real question, but no evidence can be
  linked: ViroBench's source carries an open evidence concern, the CAMI protocol records are not
  reviewed, and BacBench, which is reviewed, scores bacterial genome embeddings on gene and strain
  properties rather than taxonomic assignment. A page with no evidence would say less than the review
  does. BacBench is a candidate for a separate question about bacterial genome models.
- **Not opened: protein-protein interaction prediction.** Its evidence is single-study tests spread
  across PLABench, an OGBl-ppa embedding comparison and the HyPLM HumanPPI probe, which is already
  linked to protein representation probing. No question stood up on its own.

## Protocols considered and not linked

| Protocol group | Why |
| --- | --- |
| BEND, DART-Eval, GUE, Genomic Benchmarks, Gene-MTEB, mRNABench, NABench, BEACON, ProteinBench, GlycanML's own results, Open Problems integration | On `task` records whose evaluations name no protocol, or whose evaluations link a method rather than a configuration. A judgement must name a protocol and its evaluations must link configurations, so these need record work first |
| CAFA3 (3 protocols, 438 entries), BEELINE (62 protocols), scIB, CAMI, Scaffold-Lab, FLIP, FLIP2, TAPE, PFMBench, DeepProtein | Protocol records are `discovered`, not reviewed. These are the strongest second studies for function annotation, network inference, integration and representation probing once reviewed |
| ViroBench | Its source carries an open evidence concern |
| HyPLM fluorescence, GB1 two-vs-rest and three-vs-rest, hydrolase to P06241, remote homology, secondary structure CB513 | A dataset their evaluations link is unavailable or unchecked, so no evaluation passes the gates. The builder prints each one |
| GUANinE cons30, cons100, cadd-snv, clinvar-snv, gpra-c, gpra-d | Conservation, variant scoring and synthetic promoter expression, which the annotation use case excludes; cadd-snv and clinvar-snv are already `proxy` on the missense use case. Its ccre and dnase propensity tasks are kept as `proxy`: they score element propensity |
| HyPLM ProteinGym zero-shot, NLL, perplexity, FLIP stability, embedding throughput | Named in the protein representation use case's exclusions |
| Wang et al. 2026 attention-map secondary structure (t4, t5) | Named in the RNA structure use case's exclusions |
| GenBench and Nucleotide Transformer splice-site tasks | Linked as `proxy`, not `direct`: the splicing use cases hold the same tasks, and grading them `direct` in both places would present one comparison as two |

## BEELINE counts as one study

BEELINE's results come from three source-data files of one paper (Pratapa et al. 2020). The store
counts them as three studies because none of the three source records carries the paper's DOI in its
`doi` field; `docs/reviews/2026-11-27-use-case-mapping-gaps.md` section 8 has the evidence and the
proposed rule. The gene regulatory network use case's text says BEELINE is one study.
