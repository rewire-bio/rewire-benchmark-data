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
| Leaderboards per use case on the website | Built as a query (`kb/board.py`); not on the site |
| Review of the differences found inside papers and code | 65 are in a register, checked against saved files; ten reports are drafted for the owner |
| Running the run guides | Not started |

## Pages

1. **General-purpose language models: 50 records** (Claude, GPT, Gemini, Llama, Qwen and others)
   that a benchmark prompted. No page. Decision needed from the owner: a short standard page each
   (what it is, who makes it, which benchmark used it and how), or none.
2. **Pages set aside: 8.** A safety classifier interrupted an agent on each and they were not
   retried: BenchBench-Cloning and its two sub-sets, FrameFlow, ViroDNABERT2, PGraphDTA, the
   DeepProtein benchmark and the Genie 3 comparison. They need a person.
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
   attention network), BERTax (repository address), CIViC MCP (`executable_suite`). ProtBert's page says its
   weights are not under an open-source licence; they are AFL-3.0, which is. The ESM-1b run guide
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
13. **Leaderboards rank at the model, not the checkpoint.** They become trustworthy per use case as
    grounding reaches it.
14. **Rewire's Evo 2 cloud study.** Two platforms' results are identical to 16 digits and the
    platform labels moved between the protocol and the run. One set is probably mislabelled.
    Needs the owner.
15. **Metric names are not normalised** in the benchmark task facts (`AUPRC`, `auPRC`).

## Differences found in the sources

16. **65 differences** between a paper and its code, an abstract and its results, or a model
    card and its weights are in one register (`kb/curation/source_leads.jsonl`, guide in
    [leads.md](leads.md)), each with both passages quoted from saved files and graded. Ten are
    drafted as reports for the owner to send. Agents do not post to other organisations. First
    step: the owner posts the ones he chooses. About 40 small items (counts, names, two dead
    addresses) were not checked and are listed in `source_leads_left_out.jsonl`.
17. **Outcomes go in the store.** Every lead's outcome, report and reply is recorded as a
    discrepancy review, not only in an issue.

## Running things

18. **Run guides tried: 18 trials of 14 guides, 3 completed.** [run-guide-trials.md](run-guide-trials.md)
    runs a guide on a clean GitHub runner with no credentials and returns a receipt. SAFFRON,
    GPN-Promoter and MutBERT completed. Six guides missing an install line were corrected, and five
    whose sources fail on a clean machine now say so
    ([trial 2 review](reviews/2026-11-27-run-guide-trial-2.md)). Next: rerun the corrected guides,
    and try the rest of the candidates.
19. **Run guide status.** The schema has one status, `source_reviewed_not_executed`. An executed
    guide needs a second, with a receipt: commands, versions, hardware, output hash, time.
20. **Recipes.** A model can be rerun through `rewirebench` only when it has a registered adapter.
    Ten pretrained models have one; six were written from run guides on 27 November and each ran
    on a GitHub runner with a verified receipt (`docs/adapters.md` in rewire-benchmarks). Those
    runs are small checks, not benchmark results. First step: full-protocol recipes for the six,
    then more adapters. Of about 70 models surveyed, 23 have non-commercial or gated weights and
    20 state no weights licence; whether to adapt non-commercial weights is the owner's decision.
21. **GPU work is parked** until the value is shown. Nothing here needs it.

## Pipeline

22. **Agents still read the graph.** Every read has a database version, tested equal. Six steps
    remain before the intake agent can switch ([agents-off-the-graph.md](agents-off-the-graph.md)).
    The owner is told before the switch.
23. **The serving file still comes from the old builder.** Step 5 of the rebuild: the new core
    writes the file the website reads.
24. **Merge to live is about 25 minutes.** The website's adoption step is the longest stage.
25. **Schedules to confirm.** The nightly full check (00:47 UTC) and the nightly archive run
    (02:17 UTC) were added on 26 and 27 November and have not yet been seen to fire.
26. **Layers for the archive.** Rows made in CI use a different pdftotext version from the rows
    made earlier. Each row records its version. A pinned version in CI would remove the split.
27. **Deletion.** The graph build on the release path is gone. The graph code, the per-batch
    scripts and the compatibility export stay until the agents have switched and the nightly
    comparison has passed across several releases that change results. The owner is told first.

## Not started, from the product list

Use case pages with recommendations. Community-contributed results. Rewire's own benchmarks.
Checking a blog article against the database. Sharing a record with its model's developers.
