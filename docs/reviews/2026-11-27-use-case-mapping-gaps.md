# Which results in the store belong to a use case and are not tied to one

27 November 2026. 29,062 of the store's 52,878 results sit on 1,573 tests that no use case links,
while 11 of 31 boards rank nothing. This review asks which of those tests answer a use case's stated
question, what each board would become, and what is left over. Candidates are in
`kb/curation/use_case_mapping_candidates.jsonl` (521 rows, loaded by `kb/curate.py` as
`use_case_mapping_candidate`); section 7 accounts for every unmapped test. The counts below are as
this review was written, before anything was applied.

**Later the same day** the owner asked for the mappings to be applied. 12 candidates became reviewed
judgements ([use-case-mapping-gaps-2026-11-27.md](use-cases/use-case-mapping-gaps-2026-11-27.md)) and
nine of section 5's questions became use cases
([use-case-pages-2026-11-27.md](use-cases/use-case-pages-2026-11-27.md)). Every row of the candidates
file now carries `state` and, where it was not applied, `not_applied_reason`. Three gradings here
changed when each test was read again for that pass: PerturBench's Srivatsan20 and PBMC covariate
transfer are small-molecule, not genetic, perturbations; the Barbosa ClinVar splicing set is labelled
by clinical classification, which splicing-follow-up excludes, so it is `proxy`, not `direct`; and the
Evo 2 paper's 38 remaining ClinVar strata, counted as not examined in section 7, were graded in that
pass (coding SNV strata `proxy` on missense, noncoding strata `proxy` on regulatory variants, the
SpliceAI-and-Pangolin-low subset `proxy` on splicing, and the indel, microsatellite and non-SNV
classes `outside_scope`).

## 1. How a test is tied to a use case today

Three pieces. The `assessed_by` link on the `use_case` record names each protocol or task judged to
bear on it (492 links). A relevance judgement, a `claim` in `data/evidence/claims/` with `subject` the
use case and `field` `links:assessed_by:<test>`, grades it `direct`, `proxy` or `outside_scope`
(`data/vocab/relevance.ttl`) with an endpoint, rationale, constraints, limitations and sources. A
second worker reviews it, sets it `source_checked` and pins it with `npm run use-cases:repin`; only
then does it reach the site (`docs/use-cases.md`). Of the 493 judgements, 382 are `proxy`, 103
`direct` and 8 `outside_scope`, so `proxy` is the norm, including every ClinVar-style predictor
comparison on the missense use case and every structure-accuracy protocol on the structural one. This
proposal follows those precedents.

**A board does not read the grade.** `kb/board.py` reads the `assessed_by` links, and all 8 existing
`outside_scope` judgements keep theirs, with rationales that say so. Those 8 tests are therefore
fitted on their boards today. Either the board should skip `outside_scope` links or a refusal should
drop the link: the owner's call.

## 2. Candidates, by use case

182 tests carrying 3,268 results are proposed (52 `direct`, 137 `proxy`); 297 rows record a test that
was examined and refused, so a later pass need not re-examine it.

| Use case | Proposed | Example and reason |
| --- | --- | --- |
| cell-type-annotation-transfer | 30 direct | Open Problems label projection (16 tasks, 16 models), HyCell annotation transfer, scFoundation Zheng68K and Segerstolpe, scTab donor bootstrap: labels transferred to a held-out batch, scored by accuracy or F1 |
| structural-hypotheses-experiments | 54 proxy | CASP16 domain accuracy, CAPRI round 61 interfaces, ProteinBench fold accuracy, the remaining FoldBench classes and ClusPro rows |
| splicing-follow-up | 1 direct, 31 proxy | Barbosa ClinVar intronic splice-altering classification (direct); NT benchmark splice-site tasks, the AlphaGenome paper's splice-site classification, GTEx tissue splicing (proxy) |
| missense-pp3-bp4-calibrated-evidence | 11 proxy | Brandes et al. 2023 ClinVar and HGMD comparisons (37 models), EVEE deconfounded ClinVar, Lu et al. ClinVar, GUANinE cadd-snv, GPN-MSA COSMIC |
| genetic-perturbation-response | 10 direct, 3 proxy | PerturBench combination and covariate-transfer tasks, the same endpoint as the PerturBench v4 protocols already mapped |
| regulatory-variant-gene-follow-up | 10 proxy | TraitGym from a second study and from the AlphaGenome Atlas, matching the TraitGym mapping already held |
| rare-disease-candidate-ranking | 7 proxy | TraitGym Mendelian traits from the second study, PhyloGPN ClinVar, Lu et al. ClinVar, Evo 2 mitochondrial pathogenicity |
| mass-spectrum-molecule-shortlisting | 9 direct | MSAlign NPLIB1 and Spectraverse retrieval with no formula, and the MassSpecGym main retrieval table |
| phenotype-perturbation-selection | 2 direct, 8 proxy | Song et al. Virtual CRISPR hit prediction (18 models, direct); CPPC Challenge 1 and the reimplemented Challenge 2, Kendiukhov target ranking (proxy) |
| binder design, patient RNA splicing, target validation, lead optimisation | 13 proxy between them | RFD4-Proteina computational passers per GPU-hour; SpliceAI2 DM1 junction usage, OPA1 and Silverstein outlier recovery; the CPPC scores; PLABench CASP16 affinity under a leakage control |

Refused where a benchmark is in the same field but answers another question. Each reason is the use
case's own exclusion or endpoint.

| Refused | Rows | Why |
| --- | --- | --- |
| scIB, SCMBench integration, Chen et al. clustering, Kedzierska embedding scoring, HyCell batch correction, pseudotime and CD4 splits, the scTab hardware table | 38 | cell-type-annotation-transfer excludes batch mixing and embedding separation in as many words: they do not establish correct cell identity |
| MIST CANOPUS retrieval, MassSpecGym formula-known retrieval, de novo generation, spectrum simulation | 39 | the mass-spectrum use case names MIST and formula-conditioned retrieval in its exclusions |
| mRNABench (25 tests, 83 models), BEACON mean ribosome loading | 27 | utr-translation-baselines excludes benchmark-wide mRNABench results and other reporter systems; those 83 models are evidence for a new use case instead |
| Genie 3, Scaffold-Lab, ProteinBench backbone, co-design and sequence tracks, POISK | 29 | unconditional generation has no target, and POISK ranks known binders against decoys: neither is de novo design |
| ATOM3D, PFMBench binding, PLABench (35 rows); ProteinGym supervised and indel tracks, PGB terminator strength, the other FLIP2 landscapes (34) | 69 | hit-discovery excludes affinity prediction, scoring power and binding-site prediction; the rest are named in the exclusions of the use case they would have gone to |

TraitGym was already mapped as proxy to two use cases; its second study's ten tests go under those
same mappings, not into a new use case.

## 3. What each board would become

Computed with `kb/board.py` over a scratch copy of `kb.sqlite` with the candidates added as links.
Counts are the board's own: studies and groups that compared two systems, models fitted, models
ranked. "Comparable" is how many proposed results land in a group of two or more systems, the only
kind a board can use.

| Use case | Studies | Groups | Models | Ranked | Proposed results, comparable |
| --- | --- | --- | --- | --- | --- |
| cell-type-annotation-transfer | 4 to 7 | 30 to 59 | 23 to 52 | **0 to 5** | 439, 427 |
| missense-pp3-bp4-calibrated-evidence | 8 to 11 | 28 to 231 | 114 to 126 | **30 to 49** | 635, 567 |
| rare-disease-candidate-ranking | 10 to 12 | 100 to 135 | 158 to 167 | **35 to 41** | 245, 218 |
| splicing-follow-up | 9 to 13 | 74 to 116 | 40 to 59 | **6 to 9** | 160, 110 |
| genetic-perturbation-response | 7 to 9 | 84 to 120 | 41 to 49 | **5 to 6** | 279, 278 |
| regulatory-variant-gene-follow-up | 8 to 8 | 70 to 99 | 95 to 105 | 8 to 8 | 147, 113 |
| mass-spectrum-molecule-shortlisting | 3 to 4 | 15 to 27 | 9 to 14 | 3 to 3 | 68, 60 |
| structural-hypotheses-experiments | 3 to 5 | 21 to 57 | 8 to 16 | 3 to 3 | 917, 178 |
| phenotype-perturbation-selection | 3 to 5 | 25 to 44 | 48 to 88 | 0 to 0 | 180, 102 |
| therapeutic-target-validation, de-novo-binder-design, lead-optimisation-affinity-ranking, patient-rna-splicing-validation | each | unchanged ranking | | 0 to 0, except patient RNA 3 to 3 | 168 proposed, 145 comparable |

The other 18 boards are unchanged. Cell-type annotation would rank scFoundation at positions 1 to 2,
UCE at 1 to 4, Geneformer at 2 to 4, CellTypist at 2 to 5 and scGPT at 4 to 5, each on two or three
studies; the missense board's first rows stay AlphaMissense, GEMME and TranceptEVE, on 231 comparison
groups instead of 28.

A mapping can also remove a ranking. An earlier draft graded the HyPLM report's CASP14 and CASP15
contact-precision protocols as `proxy` here; that brought 12 protein language models on as a group no
study compares with AlphaFold 3, Boltz or Chai-1, which being larger became the main group and pushed
the three folding tools out, taking the ranking to none. The final proposal refuses those.

### A mechanical reason large leaderboards are invisible to boards

17 tests hold results for two or more systems and yet no group of two, so they produce no verdict and
every one of their systems is dropped: 2,652 results and 1,350 system slots. In 8 of them one field is
the cause. `scoring_conditions` holds a structured value (a `\x00`-prefixed JSON blob) carrying the
identity of the individual submission, and the board's group key includes it, so every group falls to
a single system.

The four affected imports: the Virtual Cell Challenge (1,048 systems, 1,048 results, one submission
per row), CASP16 protein domains (90 systems, 270 results; round, target, domain, submission and
participant id), the scIB RNA metrics export (68 systems, 821 results; the method configuration, such
as `combat_full` or `saucie_embed`) and four CAPRI round 61 targets (25 systems and 100 results each).

This is the largest single obstacle found: CASP, CAPRI and scIB are mapped here and still add almost
nothing until it is fixed, in the board or the import rather than a mapping. Either the blob moves to
a field the group key ignores, or `board.py` drops a structured `scoring_conditions` from the key.

## 4. The systems that are not model records

Boards fit every system but rank only model, method, pipeline and service records (`docs/boards.md`).
On four use cases most fitted systems fail that test.

| Use case | Not a model | What they are |
| --- | --- | --- |
| hit-discovery-virtual-screening | 29 | 23 CACHE #3 competition workflows (`WF1687` and so on), one study each; and 6 rescoring configurations. RTMScore, PIGNet2, PLANET and IGModel have no record of any kind in the store, so these are real methods that were never added, not mislabelled configurations |
| therapeutic-target-validation | 36 | CPPC original submission rows 2 to 24, 6 named only "unnamed method". A mix: scBERT and scVI have model records, so those rows need a parent link; scETM, scTenifoldNet and GeneVector have none and need a record first |
| phenotype-perturbation-selection | 36 | the same CPPC rows |
| plant-promoter-reporters | 12 | 8 are a model under a task label whose exact name is a record (DNABERT-2, GROVER, HyenaDNA, NT-v2, twice each): a missing `configuration_of` link. 2 are Caduceus-Ph, where "Caduceus" is a record and the Ph variant is a checkpoint. 2 are the Jores CNN, a real baseline with no record |

The last row is the general case: all 79 configurations of batch `amp-feng-20261007` carry a
`reported_name` that names a model and have no parent link. Linking the 36 whose reported name is
exactly a record (the other 43 are qualified, such as "Enformer, output tracks\*", and need a small
judgement about which head or checkpoint) would, on top of section 3,

raise splicing from 9 ranked models to 11 (14 not-a-model rows down to 6), rare disease from 41 to 44
(33 to 29), regulatory variants from 8 to 10 (56 to 40), and cut plant promoters' not-a-model rows
from 12 to 4 without yet giving it a ranking.

So CACHE and CPPC are partly a labelling question (`docs/todo.md` item 3) and partly missing records; amp-feng is a missing link worth fixing on its own.

## 5. The leftovers: candidate new use cases

Each candidate was boarded as a scratch use case, so these are `kb/board.py` counts, not raw tallies;
groups overlap where a benchmark spans two questions.

| Candidate | Question | Studies | Groups | Models | Would rank | First rows |
| --- | --- | --- | --- | --- | --- | --- |
| noncoding-genome-annotation | Which DNA sequence model annotates regulatory elements and genome features in my species? | 11 | 235 | 113 | **13** | LucaOne, GENA-LM, Enformer |
| rna-structure-prediction | Which method predicts an RNA's secondary or three-dimensional structure reliably enough to plan an experiment? | 8 | 143 | 69 | **12** | Evo, AIDO.RNA, RiNALMo |
| protein-representation-downstream | Which protein language model representation gives the best downstream property predictions? | 6 | 256 | 62 | **9** | Prot-T5-XL, CNN, ESMC |
| mrna-construct-properties | Which sequence model predicts an mRNA construct's properties well enough to screen designs? | 2 | 32 | 68 | **9** | RNA-FM, utrbert-6mer, utrlm-te-el |
| metagenomic-taxonomy-research | Which classifier assigns metagenomic reads to the right taxon in a research survey? | 9 | 56 | 74 | **6** | Evo 2, Kraken2, Evo |
| grn-inference | Which method infers a gene regulatory network from single-cell expression that matches known regulation? | 3 | 184 | 34 | 0 | none once BEELINE counts as one study (section 8) |

Three more would rank nothing today, every model being in one study: protein function annotation
(3 studies, 156 systems, all from CAFA), protein-protein interaction prediction (3, 19) and glycan
property prediction (2, 27).

Corrections to the counts this review started from:

- **GENEB is two records**, "GENEB leaderboard" (1 study, 27 models) and "GENEB" (1 study, 11 models),
  not one benchmark with 2 studies. They are probably the same benchmark and should be merged.
- **TraitGym** is already mapped and **mRNABench** is excluded by utr-translation-baselines, so
  neither is a new use case on its own.
- **The Virtual Cell Challenge** is the largest unmapped test in the store (1,048 systems, 1 study),
  but every system is a competition submission and the next subsection explains why it is invisible anyway.
- Confirmed single-study as described: ViroBench, CAMI, NABench, the zero-shot RNA benchmark, GUANinE,
  SegmentNT, DART-Eval and the RNA secondary-structure tests.

## 6. Why the thin use cases stay thin

Ten boards would still rank nothing, measured on the most favourable scratch database (this proposal
plus the parent links of section 4). Each use case's own `evidence_gaps` were read; the count of gaps
that name a source not yet extracted is the test for cause (b). No test under a benchmark these use
cases already link is left unexamined, so cause (a) is excluded except where stated.

| Use case | Cause | Evidence |
| --- | --- | --- |
| hit-discovery-virtual-screening | (a) and (b) | 35 systems fitted, 29 are competition workflows or rescoring methods with no record and 4 are one-study. 7 of 11 gaps name sources not extracted (DUD-E, MF-PCBA, DockM8, Kawano et al.) or not open access (CACHE #1 and #2) |
| therapeutic-target-validation and phenotype-perturbation-selection | (a) and (c) | 61 and 88 systems fitted, 36 CPPC rows each, 24 and 52 one-study. Only 3 of 10 and 1 of 11 gaps name a source; the rest say no benchmark scores nominations prospectively, against a matched budget or a therapeutic window |
| de-novo-binder-design | (b) | 7 fitted, 5 one-study, and each study tested its own designs on its own target with its own hit definition. But 9 of 17 gaps name sources not extracted (BenchBB, ProtDBench, BoltzGen Tables 2 and 3, PXDesign Tables 1 and 2, Filius et al. Table S3, the Adaptyv round 2 repository), so this is collection, not absence |
| unresolved-rare-disease-reanalysis | (b) | 2 systems, 1 comparing study. 6 of 11 gaps name sources: two papers not open access, AMELIE 3's tables are images, and Kaschta et al. is the only two-method comparison found |
| lead-optimisation-affinity-ranking | (b) and (c) | 16 fitted, 15 one-study. The OpenFE industry benchmark is paywalled and three further benchmark papers were not retrieved; separately, every published machine-learning number is an average over series, as the use case states |
| egfr-nsclc-actionability-resistance-evidence | (c) | 16 fitted, 14 one-study. 5 of 10 gaps name sources, but the first gap states that no independently adjudicated benchmark for this endpoint was found, and each study uses its own question set |
| plant-promoter-reporters | (a) and scope | 11 fitted, 4 not model records, 7 one-study. Its own gaps say the two reporter hosts and three sequence species cannot be pooled, so three studies share no test |
| rhodopsin-wavelength-transfer | (b) by choice | 2 systems, 1 comparing study, 20 groups. Its gaps record that RhoMax Tables 2 and 3 were inspected and deliberately not added, and its exclusions keep it to the frozen probes |
| utr-translation-baselines | (b) by choice | 4 fitted, all one-study. Its first gap says only two procedural controls have a matched result in this protocol, and its exclusions rule out the benchmark-wide results that exist |

(a) results are in the store and only the tie or the record kind is missing. (b) sources are known and
results were not collected. (c) the store shows no shared test. Two use cases are thin by their own
stated scope and marked "by choice": widening them is the owner's decision. No claim is made about the
literature beyond what the store and these gap notes hold.

## 7. Coverage of this pass

Of the 1,573 unmapped tests and their 29,062 results: 182 tests (3,268 results) are proposed, 272
(5,192) were examined and refused, 599 (13,370) fall in a candidate new use case of section 5, and
522 (7,232) were not examined. Largest groups not examined, for the next pass: the Evo 2 paper's 38 remaining variant-effect tests
(1,072 results), the Virtual Cell Challenge (1,048, see the subsection in 3), HyInv inverse folding (498), the rest of
GFMBench-API (432), the Nucleotide Transformer 18-task benchmark outside its splice tasks (353),
ProteinBench's generation tracks (172) and PepSpecBench (168).

## 8. One paper counted as three studies: BEELINE

The published discrepancy `discrepancy-0311356983b743d6` ("GRNBoost2 and PPCOR: BEELINE ... reverses
the order") sets one source against two others, all three named "BEELINE: 10.1038/s41592-019-0690-6
source data published 2020". They are `acquired-source-0f6c059ffdc338b70a5c`, `-31344fb7e5e8ae6b9666`
and `-3156602fda847ae943b4`: three source-data CSVs of one Nature Methods paper (supplementary files
MOESM12, MOESM14 and MOESM13). Each is its own source record with its own hash, which is right, but
none has the `doi` field filled: the DOI appears only in the name and the URL.

Both `kb/migrate.py` (study for the boards) and `kb/discrepancies.py` (`_studies`) join sources into one
study by the `doi` field, by GitHub repository, by `companion_of`, and, in the finder, by appearing
together on a result. `board.py` also joins study ids that share a part. None of these sees a DOI held
only in a URL, so BEELINE is three studies to both. The "disagreement" is BEELINE's Figure 2 data
against its other two figures, a difference inside one paper.

How many: of 216 discrepancies, 1 has all its studies resolve to one publication once DOIs in URLs and
names are read, and it is this one (public, unresolved). Store-wide, 292 sources carry a DOI only in
the URL or name; BEELINE is the only DOI whose results are split over more than one study. On boards:
BEELINE is mapped to no use case, so it counts on no board today. On the scratch GRN board of section 5
it counted as three studies and produced the only 3 ranked rows; counted as one, that board ranks none.

Proposed rule: sources whose `doi` field, or a DOI in a publisher supplementary URL, is the same are one
study, for boards and for the finder. A difference between results of one paper is a different finding
("inside one paper") and is not listed as a disagreement between studies. The data fix is to fill the
`doi` field of the 292 sources, which makes the existing rule work without new code.

## Next steps, in order of what they buy

1. Decide how `board.py` should treat a structured `scoring_conditions` (section 3): four of the
   store's largest leaderboards are invisible to every board until it is settled.
2. Review the 52 `direct` and 137 `proxy` candidates as relevance judgements. Cell-type annotation
   gains a first ranking; missense gains 19 rows and rare disease 6.
3. Add the 36 mechanical `configuration_of` links in batch `amp-feng-20261007`, judge the other 43,
   and decide whether a board should read an `outside_scope` test at all (section 1).
4. Open the five strongest new use cases, from non-coding genome annotation and RNA structure.
