# New use cases from the unmapped evidence, 2026-11-27

Reviewer: `claude`, the agent that wrote them, by reading each benchmark and protocol record and its
saved sources, checking every linked protocol against the use case's own question and exclusions, and
verifying the evaluation gates of `shared/omics/use-cases.ts` and the source hashes. Drafter and
reviewer are the same agent, so this is not the second-worker review `docs/use-cases.md` requires:
nine use cases and 254 judgements go live on merge without one. No human scientific review is
claimed, and an independent verification pass is needed.

The verification found 82 of these 254 judgements wrong or unsupported. Its fixes are in
[use-case-pages-verified-2026-11-27.md](use-case-pages-verified-2026-11-27.md): two use cases were
removed, and the counts and sentences below are corrected to the state after it.

Batch: `data/omics/use-case-pages-20261127/`. The questions come from
`docs/reviews/2026-11-27-use-case-mapping-gaps.md`, section 5. Every link is listed with the passage
it rests on in that batch's `applied.jsonl`.

## The use cases

| Use case | Protocols linked | Studies its evidence rests on |
| --- | --- | --- |
| `genomic-sequence-element-annotation` | 105 | 4: GenBench, SegmentNT, the Nucleotide Transformer benchmark, GUANinE v1.1 |
| `rna-structure-prediction` | 42 | 2: Ludaic and Elofsson 2026, the RhoFold+ CASP15 table |
| `glycan-property-prediction` | 21 | 1: the GlycanGT paper's Table S4 |
| `protein-representation-property-prediction` | 17 | 1: the HyPLM technical report |
| `single-cell-data-integration` | 10 | 2: the HyCell technical report, Kedzierska et al. 2025 |
| `protein-function-annotation` | 6 | 1: the HyPLM technical report |
| `protein-design-quality` | 5 | 1: the Genie 3 paper's Table 3 |

Each use case names its study count in `evidence_gaps`, so a one-study page does not read as settled.
None carries `evidence_checked`: no literature search ran for these questions, so each reads as not
yet checked. `depth_tier` follows the rule in `shared/omics/depth-tier.ts` from each use case's areas,
and `npm run depth-tier -- check` reports no record differing from it.

Three of the seven boards order models: genomic element annotation orders 6 models from 105
comparison groups in 4 studies (Enformer at positions 1 to 4, GENA-LM and Nucleotide Transformer at
1 to 3), RNA structure orders 2, resting on the RhoFold+ developers' table, and single-cell integration
orders 2. The rest have one study and say so. RNA sequence properties and gene regulatory network
inference were removed after verification; the verification review says why.

## Rulings on scope

- **Genomic sequence annotation is one question, separate from variant effect.** The same models are
  compared on promoter, enhancer, histone-mark and splice-site classification by one probe or one
  fine-tuning recipe per benchmark, and a reader choosing a model asks them together. Variant effect
  prediction is a different decision with four existing use cases, so it stays out. Splice-site
  classification is `direct`: the question names splice sites.
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
  `protein-stability` question, the embedding-throughput measure, which is a cost, and the ten-split
  regression average, which includes the excluded stability split. Whole-protein
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
| BEND, DART-Eval, mRNABench, NABench, BEACON, ProteinBench, GlycanML's own results, Open Problems integration | On `task` records whose evaluations name no protocol, or whose evaluations link a method rather than a configuration. A judgement must name a protocol and its evaluations must link configurations, so these need record work first |
| Gene-MTEB | 16 reviewed protocols, but no evaluation passes the gates |
| GUE, Genomic Benchmarks | Task records only; their datasets are re-run inside GenBench and GENEB |
| BEND variant effect protocols (through GFMBench) | Variant effect, which the annotation use case excludes |
| CAFA3 (3 protocols), BEELINE (54 protocols), scIB, CAMI, TAPE | Protocol records are `discovered`, not reviewed. These are the strongest second studies for function annotation, network inference, integration and representation probing once reviewed |
| Scaffold-Lab, SCMBench, DeepProtein | Protocols are reviewed, but a source they rest on carries an open evidence concern |
| FLIP, PFMBench | Results sit on `task` records whose evaluations name no protocol |
| GENEB full, 1-shot and 10-shot | Each evaluation mixes element categories with species, virus and averages over all tasks |
| GenBench means of tied rows, HyCell composite score, HyPLM ten-split average | Aggregates of tests tied on their own, or of scores this use case excludes |
| ViroBench | Its source carries an open evidence concern |
| HyPLM fluorescence, GB1 two-vs-rest and three-vs-rest, hydrolase to P06241, remote homology, secondary structure CB513 | A dataset their evaluations link is unavailable or unchecked, so no evaluation passes the gates. The builder prints each one |
| GUANinE cons30, cons100, cadd-snv, clinvar-snv, gpra-c, gpra-d | Conservation, variant scoring and synthetic promoter expression, which the annotation use case excludes; cadd-snv and clinvar-snv are already `proxy` on the missense use case. Its ccre and dnase propensity tasks are kept as `proxy`: they score element propensity |
| HyPLM ProteinGym zero-shot, NLL, perplexity, FLIP stability, embedding throughput | Named in the protein representation use case's exclusions |
| Wang et al. 2026 attention-map secondary structure (t4, t5) | Named in the RNA structure use case's exclusions |

## BEELINE counts as one study

BEELINE's results come from three source-data files of one paper (Pratapa et al. 2020). The store
counts them as three studies because none of the three source records carries the paper's DOI in its
`doi` field; `docs/reviews/2026-11-27-use-case-mapping-gaps.md` section 8 has the evidence and the
proposed rule. When BEELINE's protocols are reviewed, its results must count as one study.
