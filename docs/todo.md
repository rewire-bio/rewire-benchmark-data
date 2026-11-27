# What is left to do on the data

Written on 27 November 2026, after two days of filling in pages and rebuilding the pipeline. It
lists what is not done, grouped by the goal it serves, with the first step for each. Read
[knowledge-base.md](knowledge-base.md) for how the store works and [rebuild.md](rebuild.md) for
the design it is moving to. [scorecard.md](scorecard.md) has the current counts.

## Where the data stands

| | With a page | Total |
| --- | --- | --- |
| Models | 316 | 395 |
| Benchmarks | 128 | 136 |
| Methods | 15 | 618 |

- Every page was written by a research agent from saved sources, judged statement by statement by
  a second agent, and corrected by a third. No person has reviewed one.
- 215 models have a run guide. None has been executed.
- 3,270 of 3,435 source records have a copy in the private archive.
- 52,878 results. 138 are Rewire's own runs. 35% of results can be traced by program to a span in
  an archived source.

## In progress

| Work | State |
| --- | --- |
| Checkpoint and benchmark task facts on the records, so the website can show them | On the records: `checkpoints` on 199 model records (465 entries) and `benchmark_tasks` on 98 benchmarks (535 entries). The website does not show them yet |
| Leaderboards per use case on the website | Each release publishes a board per use case (`public/omics/boards/<release_id>.json`, [boards.md](boards.md)). 40 use cases now, 24 of them with an ordering. The website does not show them yet |
| Review of the differences found inside papers and code | 65 are in a register, checked against saved files; ten reports are drafted for the owner |
| Running the run guides | Not started |

## Use cases

Nine use cases were added on 27 November from evidence that was in the store and tied to no use case
([use-case-pages-2026-11-27.md](reviews/use-cases/use-case-pages-2026-11-27.md)): genomic element
annotation, RNA structure, RNA sequence properties, single-cell integration, protein function
annotation, gene regulatory network inference, protein representation probing, protein design quality
and glycan properties. Six of the nine rest on one study and say so, and none has had a literature
search. What they still need:

- A second-worker review. Drafter and reviewer were the same agent for all nine use cases and the 266
  judgements of 27 November, which both reviews state.
- A literature pass, so each can carry `evidence_checked`.
- Reviewed protocol records for CAFA3, BEELINE, scIB, CAMI, FLIP, FLIP2, TAPE, PFMBench and the
  DeepProtein benchmark. These are the second study for function annotation, network inference,
  integration and representation probing, and all are `discovered` today.
- Protocol records for the task-only benchmarks (BEND, DART-Eval, GUE, Genomic Benchmarks, Gene-MTEB,
  mRNABench, NABench, BEACON, ProteinBench, the Open Problems integration tasks). Their results are in
  the store but a judgement must name a protocol.
- A question for classifying viral and microbial sequences, drafted and dropped: ViroBench's source
  carries an open evidence concern and CAMI's protocols are unreviewed, so nothing could be linked.
- Baselines: none of the nine names a conventional comparator, because no source in the store
  establishes one for these questions.

## Pages

1. **General-purpose language models: 50 records** (Claude, GPT, Gemini, Llama, Qwen and others)
   that a benchmark prompted. No page. Decision needed from the owner: a short standard page each
   (what it is, who makes it, which benchmark used it and how), or none.
2. **Pages set aside: 12.** A safety classifier interrupted an agent on each and they were not
   retried: BenchBench-Cloning and its two sub-sets, FrameFlow, ViroDNABERT2, PGraphDTA, the
   DeepProtein benchmark, the Genie 3 comparison, and the revisions of DeCodon, EnCodon, E1 and
   ProGen3. They need a person. The four revisions are the only ones whose paper is already
   archived: the cdsFM, E1 and ProGen3 preprints are source records added on 27 November, with
   their text layers, so the work is to revise the pages from text the store already holds.
   ProGen3 is the one with a known fault on the live page: it says no source supports the two
   figures in the record's description, 46 billion parameters and 1.5 trillion amino-acid tokens.
   The archived paper states both, so the description is right and the page's gap is wrong.
3. **Records that are not models: about 15.** LLF, MFE, DeepGraphDTA and LCDD-team (table rows and
   a challenge team), Emb-Cos and the MassSpecGym DeepSets predictor (baselines built inside a
   benchmark), the Cellpose conditions, four benchmark-built Tier 1 baselines, six generic
   baselines (CNN, GCN and others). First step: decide a kind for them (`baseline` exists) and
   retype the records, then describe each on its benchmark's page.
4. **Benchmarks with no usable public source: 5.** HECTOR 2026, "Where single-cell foundation
   models help", ESMFold2 Runs N' Poses (preprint only, rate limited) and two above.
5. **Methods: 603 of 618 have no page.** Not started. First step: triage. Most are tools named in
   one benchmark table; decide which tiers get a page.
6. **Pages still resting on an abstract.** 5 papers are refused by bioRxiv's rate limit (DeepGene,
   DeCodon and EnCodon, RNA-km, ProGen3, E1). PromoterAI and ENIGMA 2024 are paywalled and
   RFamLlama is behind a robot check; those need a browser with access. About 20 more bioRxiv
   addresses are recorded in the notes of batches 7 to 10 and the benchmark batches. First step:
   run them through the slow single queue, then revise the pages as in
   `docs/reviews/2026-11-27-model-pages-revision-1.md`. RNAGenesis has its paper saved and still
   needs its revision.
7. **Structured facts for the first three model batches.** 52 of their 74 records have no
   checkpoint list. First step: the revision procedure, without a new paper.
8. **Corrections to existing records** that the page work showed are needed and that were not
   made: ESCOTT's description (the allele frequency step belongs to PRESCOTT), ProGen3's
   description (figures no source supports), Graph_RG (not structure-based), BACPI (graph
   attention network), BERTax (repository address), CIViC MCP (`executable_suite`). The ESM-1b run guide
   loads the original fair-esm file while the `rewirebench` adapter loads a pinned port; the two
   weight files have not been compared.
9. **One page on two records.** Eight Tier 1 models carry the same page on two records. A
   correction to one must be made on both. First step: make the batch tool do that itself.

## Results and comparisons

10. **Agents do not add results from papers.** They add models, sources and pages. This is the
    largest gap in the design: step 2 of the primer. First step: a brief and checker for
    extracting a paper's result tables as observations, tested on one paper already in the store
    by hand so the output can be compared.
11. **Grounding at scale.** Results name a model family, not a checkpoint, and a protocol, not a
    comparable setting. One slice (ClinVar and BRCA1, 472 results) is grounded and reviewed. First
    step: the remaining Tier 1 use cases, each with the verifier pass, since single-agent
    grounding was wrong on one line in ten.
12. **Settings.** 21 pilot settings exist. 175 results sit in a "missense" setting but are other
    variant classes, and five supervised rows sit in label-free settings. First step: split them.
13. **Boards rank at the model, not the checkpoint.** They become trustworthy per use case as
    grounding reaches it. Only models compared in two or more studies get a row, so 11 of 31 boards
    have none yet. Store fixes the boards showed: all 79 configurations of batch
    `amp-feng-20261007` (Caduceus-Ph, DNABERT-2, Enformer, GROVER, HyenaDNA, NT-v2 and others under
    a task label) have no parent model, so they are not ranked; 48 of them on the regulatory board
    and 11 on rare disease were compared in two or more studies. Their `reported_name` names the
    model. Strelka2 on tumour DNA has the same gap. An ensemble is recorded as a method (the
    majority-vote consensus of somatic callers, ranked 1 to 3 on tumour DNA). First step: the
    website section that reads the file.
14. **Rewire's Evo 2 cloud study.** Two platforms' results are identical to 16 digits and the
    platform labels moved between the protocol and the run. One set is probably mislabelled.
    Needs the owner.
15. **Metric names are not normalised** in the benchmark task facts (`AUPRC`, `auPRC`).

## Differences found in the sources

16. **73 differences** between a paper and its code, an abstract and its results, or a model
    card and its weights are in one register (`kb/curation/source_leads.jsonl`, guide in
    [leads.md](leads.md)), each with both passages quoted from saved files and graded. Ten are
    drafted as reports for the owner to send. Agents do not post to other organisations. First
    step: the owner posts the ones he chooses. About 40 small items (counts, names, two dead
    addresses) were not checked and are listed in `source_leads_left_out.jsonl`.
17. **Outcomes go in the store.** Every lead's outcome, report and reply is recorded as a
    discrepancy review, not only in an issue.

## Running things

18. **Run guides: 4 of 16 complete; 7 more pass every step up to one that needs the reader's own
    data, an input the sources do not provide, or a change not yet run.**
    [run-guide-trials.md](run-guide-trials.md) runs a guide on a clean GitHub runner with no
    credentials and returns a receipt. 16 guides have had 31 runs.
    - Complete: SAFFRON, GPN-Promoter, MutBERT and ESM-1b.
    - Trial 5 ([review](reviews/2026-11-27-run-guide-trial-5.md)) took CARP, MIF and MIF-ST to
      their last step. They stopped there on an output folder the README never creates; it is
      now created but not yet run.
    - Stack and GPN-MSA stop at the reader's own data, and DNALONGBENCH at a manual data download.
    - MSA Transformer stops on the shipped example alignment, whose sequences have unequal
      lengths.
    - Five guides fail because of their own sources and say so; draft reports to developers are
      in the [trial 2 review](reviews/2026-11-27-run-guide-trial-2.md) and the
      [trial 4 review](reviews/2026-11-27-run-guide-trial-4.md).

    The correction loop of one missing package per run is stopped here. The next step is item 19.
19. **Check a guide's imports before a trial.** Trials of CARP, MIF and MSA Transformer each
    failed on one missing package per run, because their packages declare no dependencies. A
    `trial.py imports <record id>` command should fetch, at the guide's pinned commit, the scripts
    the steps run and the package they import. It should parse them without running them, and list
    every third-party import that no install line covers. The trial 4 review did this by hand.
20. **Run guide status.** The schema has one status, `source_reviewed_not_executed`. An executed
    guide needs a second, with a receipt: commands, versions, hardware, output hash, time.
21. **Recipes.** A model can be rerun through `rewirebench` only when it has a registered adapter.
    Ten pretrained models have one; six were written from run guides on 27 November and each ran
    on a GitHub runner with a verified receipt (`docs/adapters.md` in rewire-benchmarks). Those
    runs are small checks, not benchmark results. First step: full-protocol recipes for the six,
    then more adapters. Of about 70 models surveyed, 23 have non-commercial or gated weights and
    20 state no weights licence; whether to adapt non-commercial weights is the owner's decision.
22. **GPU work is parked** until the value is shown. Nothing here needs it.

## Pipeline

23. **Agents still read the graph.** Every read has a database version, tested equal. Six steps
    remain before the intake agent can switch ([agents-off-the-graph.md](agents-off-the-graph.md)).
    The owner is told before the switch.
24. **The serving file still comes from the old builder.** Step 5 of the rebuild: the new core
    writes the file the website reads.
25. **Merge to live is about 25 minutes.** The website's adoption step is the longest stage.
26. **Schedules to confirm.** The nightly full check (00:47 UTC) and the nightly archive run
    (02:17 UTC) were added on 26 and 27 November and have not yet been seen to fire.
27. **Layers for the archive.** Rows made in CI use a different pdftotext version from the rows
    made earlier. Each row records its version. A pinned version in CI would remove the split.
28. **Deletion.** The graph build on the release path is gone. The graph code, the per-batch
    scripts and the compatibility export stay until the agents have switched and the nightly
    comparison has passed across several releases that change results. The owner is told first.

## Not started, from the product list

Use case pages with recommendations. Community-contributed results. Rewire's own benchmarks.
Checking a blog article against the database. Sharing a record with its model's developers.
