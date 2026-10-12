# Protein-fitness and structure-design literature pass, 2026-10-11

Window: published or posted 2025-10-01 to 2026-10-11. Lanes: `protein-fitness`, `structure-design`.
Focus: benchmark suites and independent comparisons that put protein and structure foundation models next
to each other or next to conventional methods.

Searches, decisions and gaps are in `ledger.jsonl` (29 entries) and `scope-audit.jsonl` (26 decisions) in
this folder. They are not merged into the shared `data/omics/search-ledger.jsonl` or
`data/omics/scope-audit.jsonl`; the team lead merges them.

This report was written before review and lists the questions put to the reviewers. The independent
review and the corrections applied are in each batch's `review.md` and in
`docs/reviews/2026-10-11-protein-structure-suites.md`; they take precedence over this report.

## Store completeness check for these lanes

Before searching, the store was checked for the lanes' well-known suites. All of them already carry
results: ProteinGym (221 paper results plus a 97-row leaderboard snapshot), FLIP (155), FLIP2 (283),
ProteinBench (556), PFMBench (141), FoldBench (175), PoseBusters (through the Boltz stereochemistry
batch), CASP16 protein domains and CAPRI round 61 snapshots, Genie 3 (65) and ESMFold2 on Runs N' Poses
(11). This pass therefore added new benchmarks rather than filling suite gaps.

## Extracted

| Batch | Source | Lane | Tables | Results |
| --- | --- | --- | --- | --- |
| `lit-protein-20261011-deepprotein` | DeepProtein, Bioinformatics 2025, CC BY (10.1093/bioinformatics/btaf165) | protein-fitness | 2 to 8 | 436 |
| `lit-protein-20261011-prime` | PRIME, BMC Genomics 2026, CC BY (10.1186/s12864-026-12976-5) | protein-fitness | 1 | 168 |
| `lit-structure-20261011-scaffoldlab` | Scaffold-Lab, PLoS Comput Biol 2026, CC BY (10.1371/journal.pcbi.1014290) | structure-design | 3 | 160 |
| `lit-structure-20261011-lipp` | LiPP benchmark set, J Chem Inf Model 2026, CC BY (10.1021/acs.jcim.6c01457) | structure-design | 2 and 3 | 27 |
| `lit-structure-20261011-afesmfold` | AlphaFold against ESMFold, NAR Genom Bioinform 2026, CC BY-NC (10.1093/nargab/lqag002) | structure-design | 1 and 2 | 216 |

Five sources, 1007 results and 2067 records in all after review, including five relevance judgements.
Record counts per batch: DeepProtein 986, PRIME 370, Scaffold-Lab 339, LiPP 74 (plus one
metadata-correction claim), AlphaFold against ESMFold 298. The LiPP batch reuses the store's existing source
record for its paper, so it adds no source record.

What each one adds:

- **DeepProtein** is the broadest table-backed comparison in window: 18 methods, including ESM-1b,
  ESM-2-650M, Prot-T5-XL, ProtBert, the authors' fine-tuned DeepProt-T5 and two chemistry LLMs prompted
  for the task, against sequence and graph baselines, over 17 datasets from TAPE, PEER and TDC, with five
  seeds per cell and a resource-usage table.
- **PRIME** is a scale and representation study: ESM-2 at 8M, 150M and 650M and ESM-C at 300M and 600M,
  CLS against mean pooling, frozen against fine-tuned, on SARS-CoV-2 RBD binding and expression, under a
  random split and a position-stratified split that holds out whole mutated positions.
- **Scaffold-Lab** evaluates five backbone generation methods in one refolding pipeline at nine lengths,
  with designability, novelty, diversity, runtime and a TOPSIS ranking.
- **LiPP** is a new benchmark set of 331 lipid-protein complexes with a 36-complex post-cutoff test set,
  comparing three co-folding tools, DiffDock-L and AutoDock Vina.
- **AlphaFold against ESMFold** is an independent comparison on 1666 monomers and 994 dimers released
  2022 to 2024 with no close pre-2022 homologue, broken down by confidence, experimental method and
  template quality.

Each batch folder holds `batch.jsonl`, `claims.csv`, `sources.md`, `retrieval-log.md`, `research.md`,
the deterministic extractor under `extract/`, and, where a relevance judgement was made,
`use-case-links.json` with the proposed `assessed_by` links left unapplied. Every extractor asserts the
pinned artifact's SHA-256 before parsing and asserts the row and column labels.

## Vocabulary

Two metric concepts were added to `data/vocab/metric.ttl` for Scaffold-Lab's Table 3:
`topsis-relative-closeness` (the Ci and mean Ci columns) and `rank` (the rank column). Both need review
with the batches. No existing concept covers either, and both are needed to extract every cell of the
table rather than a selection.

## Candidates not extracted

Figure-only results, with no published per-item rows to compute from:

- A comprehensive benchmarking of AlphaFold3 (10.1093/bib/bbaf616, Brief Bioinform 2025). Nine benchmarks
  against AlphaFold2, AlphaFold-Multimer, RoseTTAFoldNA, NuFold, RhoFold+ and trRosettaRNA. The JATS full
  text has no tables at all. Its supplementary file was not retrieved and is the best remaining lead in
  the structure lane.
- Simple baselines rival protein language models in mutation-dense design of function tasks
  (10.64898/2026.05.01.722313, bioRxiv, CC BY). Seven protein language models against PSSM baselines on
  six mutation-dense landscapes; retrieved and read in full, but every ROC AUC and Spearman value is in a
  figure and the text gives only ranges. The strongest fitness-lane lead if the authors publish tables.
- Beyond additivity: zero-shot methods cannot predict impact of epistasis (10.64898/2026.02.17.706292).
- Benchmarking Generative AI Protein Models (10.1093/gpbjnl/qzag014), EC-Bench (10.1093/bioadv/vbag004),
  Quantifying uncertainty in protein representations (10.1038/s41592-026-03028-7), the Ginkgo Datapoints
  antibody developability competition (10.1080/19420862.2026.2634216, whose Table 3 names winning teams
  without scores), Evaluating zero-shot prediction of monomeric protein design success
  (10.1002/pro.70453), Scalable embedding fusion with protein language models (10.1093/bib/bbag014) and
  Supervised learning of protein variant effects (10.1002/pro.70526).

Not retrievable:

- Benchmarking co-folding methods on covalent protein-ligand complexes (10.1038/s41401-025-01721-5) and
  Benchmarking cofolding methods for molecular glue ternary structures (10.1021/acs.jcim.5c01860): both
  subscription only, no open full text, so their tables are unchecked.
- Evaluating generalization in protein-ligand cofolding methods (10.1038/s41594-026-01797-5), the journal
  version of Runs N' Poses: subscription only. The preprint was already excluded on 2026-10-09 because
  its per-method success rates are figures; this pass adds that the journal version is also closed.

Out of scope or deferred:

- CASP16 assessment series (Proteins 2025): per-group values are figures and the groups are teams rather
  than named methods. The store already holds the CASP16 protein-domain score table and a CAPRI round 61
  snapshot.
- Benchmarking unsupervised protein mutational effect predictors (Research Square,
  10.21203/rs.3.rs-10582140/v1): free full text but no JATS table inventory; not retrieved in this pass.
- Unified sampling framework and experimental benchmarking of sequence- and structure-based protein
  models (10.64898/2026.05.08.723784): CC BY-ND, so no records were created.
- Generalise or Memorise? Benchmarking ligand-conditioned protein generation
  (10.64898/2026.02.06.704305): preprint, not screened for printed tables within budget.
- Clinical missense predictor comparisons found by the fitness queries (gene-identity bias in ClinVar
  benchmarks, an activating-driver calibration map, pharmacogenomic predictor evaluations) belong to the
  genomics and use-case lanes and were left to them.
- Benchmarking TCR-pMHC structure prediction (10.1093/bib/bbag289) and the Boltz-2 reliability evaluation
  (10.1021/acs.jctc.6c01334): in scope for a later structure pass, not retrieved within budget.

## Gaps

- The AlphaFold3 comprehensive benchmarking supplement, and the LiPP, Scaffold-Lab and DeepProtein
  supplementary files, were not retrieved. Several figure-only candidates might become extractable from
  supplementary tables.
- ProteinGym's supervised and indel benchmarks, and the full v1.3 zero-shot leaderboard beyond the AMFR
  snapshot, are still partly unextracted.
- No in-window antibody or binder design benchmark with printed per-model values was found. The Ginkgo
  competition is the closest and prints only winners.
- Four structure-accuracy leads fell between this pass and the microbial-interactions pass and were
  screened by neither: the kinase co-folding benchmark (10.1038/s44386-026-00068-z), Bento docking
  (10.64898/2025.12.30.696741), and protein-peptide AlphaFold and OpenFold3 evaluations
  (10.64898/2026.04.21.720042, 10.1093/gpbjnl/qzag026). The interactions pass records the same gap;
  a third collector is the lead's call.
- Co-folding generalisation is the clearest evidence gap in the structure lane: the three benchmarks that
  measure it (Runs N' Poses, the covalent-complex and the molecular-glue benchmarks) are all closed or
  figure-only, so the only post-cutoff co-folding numbers this pass adds are LiPP's 36 complexes.
- arXiv preprints were screened by title and abstract only: 24 in window in the fitness lane, 50 in the
  structure lane. None was retrieved in full.
- Channels were Europe PMC, the arXiv API and one web search. No leaderboard or repository result files
  were retrieved, unlike the genomics pass, because none of the five extracted benchmarks publishes one.

## What needs a reviewer's judgement

1. **DeepProtein's correlation metric.** The regression column is printed as rho; Figure 3's caption calls
   it "Spearman (Pearson) Coefficient". The batch uses the generic `correlation` concept, puts the
   ambiguity in every `metric_qualifier`, and records an `evidence_concerns` entry on the source so these
   values cannot feed automatic comparison. Confirm or correct.
2. **The two new vocabulary concepts** (`topsis-relative-closeness`, `rank`) and their definitions.
3. **Scaffold-Lab's designability cutoff.** The store's `designability` concept is defined as sc-RMSD
   below 2 Angstrom; Scaffold-Lab uses sc-TM above 0.5. The batch keeps the concept and records the
   cutoff in `metric_qualifier` rather than adding a concept.
4. **Unreported units.** Scaffold-Lab's efficiency column and PRIME's RMSE have no printed unit; both use
   `unit-unreported` rather than an inferred one.
5. **Non-numeric cells.** DeepProtein's OOM, "Length Exceeded" and NaN cells are results with a missing
   value reason; its 12 `/` cells and LiPP's 13 `-` cells (4 in Table 2, 9 in Table 3; corrected in review) are left out entirely. Confirm both choices.
6. **LiPP origins.** The LiPP columns are the authors' own runs; the PoseBusters columns are literature
   values (`paper_compilation`), and two AlphaFold 3 cells carry the paper's dagger for a different
   training cutoff.
7. **Printed spacing.** `printed_value` reproduces the JATS cell text, and the XML is inconsistent about
   the space around the plus-minus sign (the same DeepProtein row holds both "0.680 ± 0.001" and
   "0.678±0.001"). A self-check against the stripped XML text matched every digit; 79 DeepProtein
   values and the two dagger-prefixed LiPP values matched only after normalising spacing or the footnote
   marker. Nothing was invented, and a reviewer comparing against the PDF should compare digits.
8. **DeepProtein identity.** Table 8 says "Prot-T5" where Tables 2 to 7 say "Prot-T5-XL". They are kept
   as separate configurations because the article does not say they are the same checkpoint.
9. **Five relevance judgements**, all `needs_review`, with the proposed `assessed_by` links left
   unapplied in each batch's `use-case-links.json`: four on
   `use-case-structural-hypotheses-experiments` (the two LiPP post-cutoff test-set protocols, both
   proxy; the AlphaFold and ESMFold monomer class counts, direct; the dimer class counts, proxy) and one
   on `use-case-protein-stability` (DeepProtein's Stability rho protocol, proxy).

## Validation

Every batch was added with `npm run records -- add`, which checks the schema, the attribute registry,
the controlled vocabularies and the SHACL shapes, and all five conform. The batches are therefore
already in the canonical store on this branch, so any correction the review asks for goes through
`npm run records -- change <review.md> <batch-dir> <record-id>...` rather than a re-add.

`npx tsc --noEmit -p .` is clean and `python3 -m unittest discover -s scripts/omics/tests` passes (10
tests). Of the vitest suite, vocab, attributes, canonical-store, omics-data, omics-extraction-integrity,
derivations, omics-facet-scoping, omics-relation-parity, omics-benchmark-evidence,
omics-use-case-release, omics-evidence-release, linked-data and prepared-catalogue were run against the store with these
records and pass; the whole suite has not been run end to end on this branch yet, and the machine was
running several teammates' validations at the same time. No build was
run; CI does that.
