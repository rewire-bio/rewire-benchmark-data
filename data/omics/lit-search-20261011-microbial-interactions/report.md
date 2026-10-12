# Literature pass 2026-10-11: microbial and interactions lanes

Window: posted or published 2025-10-01 to 2026-10-11. Budget: about 30 queries per lane; 14 logged
searches in the microbial lane, 11 in the interactions lane, plus one source-resolution entry.

Focus: benchmark suites and independent comparisons that evaluate foundation models in these lanes,
and comparisons of those models against conventional methods.

The ledger is `ledger.jsonl` and the include and exclude decisions are `scope-audit.jsonl` in this
folder. Neither the shared `data/omics/search-ledger.jsonl` nor the shared `scope-audit.jsonl` was
touched; the team lead merges them.

Overlap with the protein-structure lane was agreed with that collector: complex and pose structure
accuracy benchmarks (FoldBench, co-folding pose papers, CASP16 pose, antibody and TCR structure
prediction) are theirs; binding, affinity and interaction-classification endpoints are mine.

## Candidates extracted

Five batches, 3,190 records in total, every record `needs_review`.

| Batch | Source | Records | Results |
| --- | --- | --- | --- |
| `lit-microbial-20261011-virobench` | ViroBench, arXiv 2605.25388v1, CC BY | 1,932 | 912 |
| `lit-interactions-20261011-leakctl` | PLABench, bioRxiv 2026.09.17.752433v1, CC BY-NC-ND | 363 | 279 |
| `lit-interactions-20261011-ppiemb` | Protein embeddings for GNN PPI prediction, Brief Bioinform bbag313, CC BY-NC | 715 | 308 |
| `lit-interactions-20261011-plmdta` | PLM embeddings for drug-target affinity, bioRxiv 2026.08.31.748056v1, CC BY-NC | 131 | 64 |
| `lit-interactions-20261011-mochibind` | Universal antibody-antigen affinity framework, iScience 116522, CC BY-NC-ND | 49 | 16 |

What each adds:

- **ViroBench** is the microbial lane's first broad foundation-model evaluation: 66 nucleotide
  foundation models and four conventional baselines on viral taxonomy and host classification, in
  three virus sets, two tasks and two split strategies (genus-disjoint and temporal), all with one
  frozen-embedding protocol and a standardised MLP head. It also puts BLAST and Kraken2 on the same
  protocol, and BLAST leads host classification on the ALL-virus genus-disjoint split (92.50 against
  the best foundation model, LucaVirus, at 84.56).
- **PLABench** gives the store its first independent, leakage-controlled evaluation of Boltz-2 for
  binding affinity, alongside eight other models on Davis and KIBA (warm, cold-target and cold-drug
  splits), the CASP16 L1000 and L3000 series and a ChEMBL v35 set filtered against every evaluated
  model's training data.
- **bbag313** varies only the protein representation while holding the PPI benchmarks and the GNN
  architectures fixed, across three protein language models, three structure models, three
  knowledge-graph embeddings, an ensemble and a random-feature baseline, with a protein-only MLP
  ablation.
- **plmdta** asks whether a protein language model beats a plain convolution encoder for drug-target
  affinity, with the drug encoder held fixed. It overlaps PLABench on Davis and KIBA under a
  different training protocol, so the two sets of numbers sit under separate protocols.
- **mochibind** scores Boltz-2 interface pLDDT and GeoDock as antibody-antigen affinity proxies
  against held-out antigens, which is the generalisation failure the lane cares about.

New metric concepts, all defined in the sources and given scope notes: `concordance-index`,
`modified-squared-correlation` (Roy's rm2) and `hits-at-100` (the OGB ogbl-ppa official metric). No
concept respells an existing one.

## Candidates not extracted

Highest value first. Full reasons are in `scope-audit.jsonl`.

| Candidate | Why not extracted |
| --- | --- |
| Systematic benchmarking of foundation models and classical baselines for microbiome disease prediction (10.21203/rs.3.rs-8912605/v1, CC BY) | The strongest remaining microbial candidate: TabPFN, MGM and GPT embeddings against elastic net and random forest over 83 cohorts and 20 diseases, with a 41-sheet supplementary workbook of per-cohort AUROCs. Not extracted because the per-cohort matrices need their own extractor and the pass had reached its source cap. The workbook was downloaded and inspected (SHA-256 `0cccf9f2e06661a33688247c487b0e9dd59aefbd6bda287b1bff12229183c317`). |
| LEMMIv2 (10.1186/s13059-026-04089-9) | Continuous benchmarking framework with a catalogue of metagenomic and 16S profilers. The store holds no LEMMI records at all. Conventional profilers only, so it is off this pass's foundation-model focus, but it is the biggest named-suite gap in the lane. |
| Boltz-2 reliability against the ESMACS physics protocol (10.1021/acs.jctc.6c01334, CC BY) | Independent evaluation of a foundation model on 3CLPro and TNKS2, but the full-text XML carries no results tables: the values are in figures. |
| Phage-host prediction benchmark of 27 tools (10.1093/bib/bbaf626, CC BY) | Rigorous benchmark, but its Table 2 is a tool-feature matrix and the per-tool values are in figures and a narrative supplementary PDF. |
| DNABERT-2 against ESM-2 for virulence-factor classification under leave-one-pathogen-out (10.1016/j.compbiolchem.2026.109327) | Directly on focus (nucleotide against protein foundation model), but not open access and no full text was retrieved. |
| CASP16 pharmaceutical pose and affinity assessment (10.1002/prot.70061, CC BY) | The published tables give baseline pose accuracy only; per-group affinity values are in figures and an unretrieved supplementary docx. PLABench covers the same CASP16 series with printed per-model affinity metrics. |
| OpenBind first release (10.64898/2026.08.27.747600, CC BY) | New open structure-affinity dataset and benchmark; not retrieved in this pass. |
| Boltz-2 for therapeutic antibody-antigen screening (10.64898/2026.05.13.724924) | On focus, but the retrieved PDF prints results in figures and in supplementary tables that were not retrieved. |
| Systematic data leakage in protein-ligand affinity benchmarks (10.64898/2026.06.29.735309, CC BY) | Retrieved; its tables are assay-correlation analyses and a FEP+ figure rather than a model comparison table. |
| Experimental assessment of AI-based interactome mapping (10.1038/s41467-026-70942-x, CC BY) | An experimental test of predicted interactomes; the evidence is spread over 24 supplementary workbooks and would need a scoped extractor. |
| Metagenomic binning benchmark (10.1038/s41467-026-71521-w) | Conventional binners only, no foundation model. |
| Tabular foundation model robustness on gut microbiome data (arXiv 2606.24995) | In lane and on focus; not retrieved. |
| Compass benchmark inside the Waypoint preprint (10.64898/2026.05.02.722381) | The benchmark is introduced in its own developer paper, so its headline numbers are author-reported for the proposed model. |
| LAMBDA journal version (10.1093/nargab/lqag103) | The preprint is already in the store with 102 results. The journal version would be a superseding source, not new evidence. Worth a follow-up. |
| Mutation-effect tool evaluation without experimental structures (10.1093/bib/bbag035) | Per-tool values are in figures; Table 3 is a baseline summary by data source. |
| Phage stress test for Evo 2 (10.64898/2026.09.23.753910) | In lane, on focus, with printed AUROC tables, but its endpoint is the viability of specific engineered changes to phage genomes. This collector did not transcribe it. It needs an explicit decision by the owner before anyone extracts it. |
| Benchmark audits (10.1039/d6sc01799a and the TDC leaderboard critiques) | About benchmark quality rather than model performance. Useful context for the store's PLINDER, PoseBusters and TDC records; not benchmark evidence. |
| DeepProtein (10.1093/bioinformatics/btaf165) | Its Table 4 carries PPI affinity and classification and its Table 5 epitope and paratope prediction, which are interaction endpoints. Extracted by the lit-protein-structure collector instead, because they sit in the same multi-task table set as that lane's content. Not extracted here, by agreement, to avoid duplicate records. |
| PhageBench (arXiv 2604.05775) | Evaluates general-purpose large language models on phage bioinformatics questions, not sequence or structure models. Out of scope. |

## Gaps

1. **The named interaction suites are still empty.** PLINDER, PoseBusters, ATOM3D and the TDC
   molecular tasks sit in the store as `discovered` records with no results. This pass did not close
   that: no in-window source was found that prints a multi-model comparison on them, and their
   official leaderboards and repositories were not retrieved. Closing it needs a leaderboard
   retrieval pass, not a literature search.
2. **LEMMI, CAMI, OPAL and AMBER.** The microbial lane has CAMI II and OPAL only through the
   pathogen use-case batches. LEMMIv2 exists and is unrepresented.
3. **No microbial binning or taxonomic-classification benchmark of foundation models.** ViroBench
   covers viral classification; nothing in the window puts DNABERT-S, Evo and GenomeOcean on binning
   or general metagenomic taxonomy under one protocol.
4. **No TCR-pMHC specificity challenge results.** No IMMREP25 overview or community challenge
   results were located for the window; the TCR literature in it is almost entirely developer
   papers.
5. **Figure-only evidence.** Nine of the unextracted candidates fail only because their per-model
   values are in figures. None was read by eye, by colour or from pixels.
6. **Query breadth.** Four Europe PMC queries returned more hits than the 40 screened (349, 431, 256
   and 175, plus 769 and 8,086 for the two suite-name queries, which match unrelated literature).
   Coverage is bounded, not exhaustive.
7. **Three structure-side leads screened by neither lane.** The split with the protein-structure
   collector left pose and complex accuracy to them, and their pass closed without screening the
   kinase conformational-state co-folding benchmark (10.1038/s44386-026-00068-z), Bento docking
   (10.64898/2025.12.30.696741) or the AlphaFold and OpenFold3 protein-peptide evaluations
   (10.64898/2026.04.21.720042 and 10.1093/gpbjnl/qzag026). This pass had reached its source cap and
   did not take them. They are in `scope-audit.jsonl` as a shared gap and need a third collector.
8. **Microbial developer papers.** The window holds many new microbial foundation models (Genos-m,
   BiomeGPT, MicroGenomer, MGM2, LucaVirus, HViLM, a taxonomy-informed sparse DNA model). They were
   screened from titles and abstracts only; none was opened to check whether it contains an
   independent multi-model comparison table.

## What needs a reviewer's judgement

1. **bbag313 prose against its tables.** The Results prose conflicts with Tables 5 and 6 in three
   ways: it names ProtT5 where the tables print ProstT5; it reports a "GraphSAGE with DistMult"
   result although DistMult is not a column; and its percentage gains do not follow from the printed
   cells (it says ESM-2 with GraphSAGE gains 6% Hits@100 on OGBl-ppa, where the table prints GS
   random 0.0104 and GS ESM-2 0.2421). The printed values are what the records hold, and the source
   record carries an `evidence_concerns` entry. The reviewer should decide whether that concern
   blocks comparisons.
2. **ViroBench's taxonomy aggregation.** The taxonomy columns print one Macro-F1 per model although
   the source predicts five taxonomic ranks and never states how they are combined. For the rows
   spot-checked the value equals the mean of the five per-rank values in Table 26. That is recorded
   as an observation in the protocol limitations; no value was computed from it. The reviewer should
   confirm whether the protocols should say more.
3. **ViroBench's standard deviations.** Recorded as `uncertainty` with scope "across hyperparameter
   settings", from Section 4.1.2 (window configurations and learning rates), not across seeds. Worth
   a second reading.
4. **PLABench origin for FlowDock.** FlowDock is by Morehead and Cheng, and Cheng is the senior
   author of PLABench, so FlowDock's evaluations are `author_reported` and the other eight are
   `independent_paper`. That call should be checked.
5. **PLABench ChEMBL35 aggregation.** The text calls the analysis target-centric but does not say
   whether Table 4 pools all 4,862 complexes or averages over the 71 targets.
   `comparison.aggregation` is null with a missing reason.
6. **mochibind pair counts.** The pairwise accuracies have no denominator: how many pairs per antigen
   were sampled, and how, is in STAR Methods prose that was not fully transcribed. The reviewer
   should decide whether a pair count is needed before these support comparison.
7. **Unit choice for error metrics.** MSE, RMSE and MAE in PLABench and plmdta carry no printed unit
   and are recorded as `unit-unreported` with `unit_detail` naming each dataset's affinity scale
   (Davis and CASP16 pKd, KIBA score), following the store's existing convention.
8. **NT v3 pretraining coverage in ViroBench.** Table 3 lists it as phage-specific and Table 9 as
   non-viral; Table 25 groups it under phage-specific, which is what the configurations record.
9. **Use-case relevance judgements.** None were added. No extracted protocol bears directly on a use
   case in `data/entities/use-cases.jsonl`: the closest, `use-case-structural-hypotheses-experiments`,
   is about structural hypotheses rather than affinity ranking, and the two pathogen use cases are
   about clinical diagnostic workflows rather than viral taxonomy from foundation-model embeddings.
   The reviewer may disagree, in which case ViroBench's host-classification protocols and PLABench's
   ChEMBL35 protocol are the candidates.

## Checks run

`npx tsc --noEmit -p .` passes. `npx vitest run` passes (48 files, 515 tests). All five batches
validate together against the store (3,190 records against 52,446 existing) through the record
schema, the vocabularies and the attribute registry. `npm run records -- add` has not been run: the
batches are unreviewed, and the reviewer writes the receipt first.

No batch was marked reviewed by this collector.
