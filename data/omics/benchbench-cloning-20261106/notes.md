# BenchBench-Cloning

Requested in issue #235. BenchBench-Cloning is a benchmark of 65 molecular cloning tasks published
by Benchling with DNAForge as arXiv:2610.33355v1 on 23 October 2026 and announced on 30 October
2026. This batch registers the benchmark, its two task sets, its 15 named construct-design tasks,
its graders, its task corpus and the eight systems evaluated on it, and extracts the performance
tables.

Extraction only. A different agent reviews it. No record is marked reproduced and no review
sign-off is claimed.

## Sources

| ID suffix | Artifact | SHA-256 |
| --- | --- | --- |
| `source-arxiv-v1` | arXiv PDF v1, the primary source | `6f5044b1bbbd81ad86b23cb536e2cae6428e0d9126f11546041355518febdc39` |
| `source-arxiv-abs` | arXiv abstract page, for the date and licence | `f9e233e9c65ab7470e5817defe75e749436122d677da9e540d51b5384100ee65` |
| `source-benchling-announcement` | Benchling blog post of 30 October 2026 | `eb67d3c73b14e40232bb5ea7633c64572c893c60b4f22a225320dcbac20354bf` |

The PDF was downloaded twice on 2026-11-06 with identical bytes, so its hash is not a per-download
stamp. The abstract page was also fetched twice with identical bytes. The gzipped `pdftotext
-layout` text layer is kept in `artifacts/` because every stored value was parsed from it; its
hash is on the source record as `archive_sha256`. The PDF itself is refetchable at the versioned
URL and is not archived (coordinator ruling 7).

The GitHub repository gets no source record: nothing was retrieved from it, so there is nothing to
hash. The 404 is recorded on the dataset, the benchmark and a dedicated claim instead.

## Access and licence, rechecked at extraction time

Rechecked 2026-11-06 at 11:51:23Z, not taken from the issue:

- `https://github.com/benchling/benchbench-cloning` returns HTTP 404 from the web page and from
  the GitHub API. A repository search for `benchbench-cloning` returns `total_count: 0`, and the
  repository is absent from benchling's public repositories, so it is not renamed or moved.
- The arXiv abstract page resolves, `citation_title` and `citation_date` match the issue, and the
  page links `creativecommons.org/licenses/by/4.0/`.
- The Benchling announcement resolves and is dated 30 October 2026.

Consequences applied throughout: the dataset is not marked openly downloadable, its `access` field
states the 404 with the date, no evaluation is marked reproduced, and `code_licence` on the paper
source is `unavailable` rather than inheriting CC BY 4.0. CC BY 4.0 covers the article text only.

A detail the issue does not have: footnote 1 on page 3 offers only the **construct-design** tasks,
graders and reference solutions. The 50 protocol-development tasks, their hidden target sequences
and the cloning simulator are not offered for download anywhere in the preprint, so even a working
repository would not make that half of the suite reproducible. This is recorded as a claim on the
protocol-development benchmark.

## What was extracted, and what was not

### Extracted as results (224)

| Table | Cells | Protocols | Why it is safe |
| --- | --- | --- | --- |
| D2, all 24 lanes x 3 metrics | 72 | pass rate (protocol dev.), pass rate (construct design), aggregate score | Complete performance table; Table 2 is exactly its eight top-tier rows, cell for cell |
| G1, pass@5 and pass@10 | 16 | two separate best-of-k protocols | Printed with intervals; pass@1 in the same rows repeats Table 2, tying it to the same runs |
| G1, Solved >=1 and Solved all | 16 | two task-count protocols | Printed counts out of 50; the Solved >=1 count over 50 reproduces pass@10 for all eight systems |
| G2, all 15 tasks x 8 systems | 120 | two per-task protocols, split by grading kind | Each system's column sums to the numerator of its printed construct-design rate over 75 |

Table 2 is not stored separately. It duplicates the eight top-tier rows of Table D2 exactly, which
the parser asserts; storing it again would create 24 duplicate results with a different locator.
Each top-tier result's `source_locator` names both tables.

### Extracted as claims (223), not results

Coordinator ruling 5: a measurement that is not a system's performance on a benchmark panel stays
a claim. These are all grading-procedure accounting or dataset composition:

- Table C1 judge agreement, all 9 slices x 3 columns (27). Agreement between two graders, not
  performance.
- Table E1 first blocking failures, all 8 systems x 8 columns (64). Diagnostic classification of
  failures. Extracted in full because its `Graded` and `Passed` columns are the denominator and
  numerator evidence for the protocol-development pass rate; using two columns of a table while
  declining the rest would be the partial extraction the brief forbids.
- Table E2 execution and grading statuses, all 8 systems x 7 columns (56). Same reason: it carries
  the denominator anomaly below.
- Table F1 adjudication outcomes, 6 outcomes x 2 columns (12). A verdict on the grader.
- Table F3 judge threshold, 8 systems x 3 columns plus 3 totals (27). Quantifies the judge's effect
  on the reported rates.
- Table 1 family shares, 9 (the counts are on the nine `dataset_subset` records).
- Figure 7 panel composition, 5. Digits printed in the figure and present in the text layer, so
  eligible under coordinator ruling 2, but they count construct presence in submissions, not
  performance.
- 23 descriptive claims: task counts, grading routes, attempt budget, licence, access, judge
  identity, wet-lab scope, two per-task failure modes, the announcement's framing.

Each number has its own claim and its own locator (coordinator ruling 11).

### Deliberately not extracted

- **Table D1 token usage, cost and runtime (24 lanes x 8 columns, 192 cells).** Not a molecular or
  omics endpoint, which is what brings an agent system into scope (`docs/collection.md` section 1).
  The table is sound: the parser asserts that its `Cost/attempt` and `Design cost` columns equal
  Table D2's `Proto ($)` and `Const ($)` for all 24 lanes, and those two cost columns are parsed
  and checked but not stored. Reviewer question 1 below.
- **Table F2, the 47 reviewed construct-design attempts.** A per-attempt adjudication listing with
  a prose basis and no metric. It is the evidence behind Table F1's counts, which are stored.
- **Figures 2, 3, 4, 5, 6 and E1.** Figures 2, 3 and 6 print the same numbers as Tables 2 and G2,
  and Figure E1 prints Table E1 as shares; storing them would double-store the same cells under a
  weaker locator. Figures 4 and 5 print no per-system numbers in the text layer, so they are gaps.
- **Any value from the Benchling announcement.** Its 30.6%, 22.2%, 20.5%, 8.8%, 72% and 27% were
  checked against Tables 2 and G1 and agree, but the preprint is the primary source for all of
  them.

## How the values were checked

Three passes, because a row-level pass is weak evidence here.

1. `extract/parse_tables.py` locates each table by its own caption line and searches only the lines
   between the previous caption and that caption. This matters: Figures 2, 3, 6 and E1 print the
   same numbers as Tables 2, G2 and E1, so a parser scanning the whole document could read a figure
   label instead of a table cell. Every row label is asserted, and each row is read with one
   anchored regex covering all of its numbers, so a cell cannot come from a neighbouring column.
2. `npm run -s batch -- check-values`: 224 of 224 results found, 112 `in_cell` and 112 `in_row`,
   no `wrong_column`, no `overclaimed_in_row`, no missing. Written to `value-check.tsv`.
3. `extract/check_tables.py`, an independent second parse that does not use those regexes. It
   slices each row by the character span of the printed column heading and compares. 280 cells
   compared (Table D2 24x5, Table G1 8x5, Table G2 15x8), no disagreement. Output in
   `extract/second-parse.txt`.

The second parse also audits what pass 2 is worth. Of the 104 results it left at `in_row`, 16 have
the stored value occurring more than once in their own row and 45 have another line in the document
starting with the same system label and containing the same value, nearly all of them Figure 2,
Figure 3 or Table 2 rows. For those an `in_row` pass alone is not evidence of the right cell, and
column assignment rests on passes 1 and 3. The reviewer's sampled manual check should concentrate
there; `extract/second-parse.txt` lists every case.

The repository's own table parser was tried as a fourth route. It confirms Table G2 cell by cell
and Table 2 cell by cell, which is a genuinely independent confirmation of 144 cells. It cannot
read Table D2 ("fewer than two body rows") and, asked for Table G1, it returns Table G2's body
instead, because both captions sit between the two bodies. Treat its Table G1 output as wrong, not
as a disagreement.

## Cross-checks that passed

Every one of these is asserted in `extract/parse_tables.py`, so the build fails if a later rerun
disagrees:

- Table 2 equals the eight top-tier rows of Table D2, cell for cell.
- Each system's Table G2 column sums to the numerator of its printed construct-design pass rate
  over 75 attempts (15 tasks x 5).
- Each system's Table 2 protocol-development pass rate equals its Table E1 passed count over 500.
- Each system's Table G1 `Solved >=1` count over 50 equals its printed pass@10.
- Table G1 pass@1 repeats the Table 2 protocol-development column.
- Every Table D2 aggregate equals (50 x protocol + 15 x construct) / 65 to within 0.05 points.
- Table D1's two cost columns equal Table D2's for all 24 lanes.
- Table 1's nine family counts sum to 50 and its nine shares to 100.
- Table C1's two task slices and its six per-system slices each sum to 387, and 450 minus the 63
  declined attempts is 387.
- Table F1's outcomes sum to 600 and 1800; Table F3's columns sum to 400, 142 and 34.
- Table E1's seven category counts sum to the graded total in every row.
- Table A1 gives 10 rubric-judged and 5 deterministic-only tasks and 6 tasks supplying experimental
  records, and its task names match Table G2's.

## Gaps

1. **Code and data are not retrievable.** The repository 404s; the dataset has no accession,
   archive DOI or manifest; hidden target sequences, grader code and rubric text were not obtained.
2. **The code and data licence is unverified** and stays so. CC BY 4.0 covers the article only.
3. **The protocol-development denominator is not stated.** Every printed pass rate equals the Table
   E1 passed count divided by 500, including for Grok 4.7 (498 graded) and Gemini 3.8 Flash (496
   graded). Table E2 records 548 recorded attempts and 50 unscored for Grok 4.7, against an
   expected 500. The paper never says whether ungraded attempts count as failures or are dropped,
   nor how Grok 4.7 came to have 548 recorded attempts. Recorded on the protocol, on the
   evaluations' `coverage`, and in the Table E2 claims.
4. **Gemini 4 Argon, low effort, construct design, 31.9%.** The only pass rate in the paper that
   does not lie on the grid a mean of binary outcomes must occupy: with 15 tasks and 5 attempts the
   value must be a multiple of 1/75 = 1.333 points, and the neighbours are 30.7 (23 passes) and
   32.0 (24 passes). Its printed 95% interval `[10.7, 52.0]` is also identical to the same system's
   top-effort interval two rows below. Stored as printed, with `source_anomaly` and
   `source_warnings` on the result. The aggregate does not disambiguate: 31.9 and 32.0 both give
   15.8.
5. **pass@k estimator not printed.** The paper does not say whether pass@k is the unbiased
   combinatorial estimator or an empirical resample, and does not say how it handles the `k = 9
   cap` it records for Grok 4.7 (2 tasks) and Gemini 3.8 Flash (4 tasks).
6. **No per-task results for the protocol-development set.** The 50 tasks are never named; only the
   nine dominant-constraint families of Table 1 are given, with counts and shares but no scores.
7. **No per-task or per-lane results below top effort.** Tables E1, E2, F1 (top-tier column), F3,
   G1 and G2 are top-effort only.
8. **Figures 4 and 5 print no numbers** in the text layer: the pass@k curves and the cost frontier
   are not extractable. Figure E1's shares are a restatement of Table E1.
9. **Judge agreement covers six of eight systems.** Table C1 excludes Gemini 4 Argon and Claude
   Mythos 5.1 (the judge itself), and drops the 63 of 450 attempts the judge declined, so the
   agreement figures rest on a self-selected subset.
10. **No DOI** is served for the preprint.
11. **Rounding residue on one aggregate.** GPT-6.1 Sol at max effort: the printed components give
    22.15, the table prints 22.2. Consistent with the authors rounding unrounded inputs; recorded
    in the aggregate protocol's review note, not as a discrepancy.
12. **The announcement's framing is not supported by the paper.** Benchling writes that Kimi K3's
    8.8% highlights "the gap between frontier and open-weight models at this task", but Table 2
    puts Gemini 3.8 Flash, a hosted frontier model, at 8.6%, below Kimi K3. Recorded as an
    `evidence_concerns` entry on the announcement source, scoped with `applies_to` to the single
    claim that cites it (coordinator ruling 4) so that nothing else is withheld.

## Decisions taken

- **One protocol per metric and per grading kind** (coordinator rulings 1 and 9), giving nine
  protocols. Simulator-graded, deterministic and model-judged grading are never pooled into one
  protocol with a note. The one place the paper itself pools two grading kinds is its
  construct-design pass rate, which mixes deterministic-only (5 tasks) and deterministic-times-judge
  (10 tasks); that is recorded as a limitation on the protocol, and the per-task protocols keep the
  two apart.
- **Best-of-k is never merged with single-attempt performance.** pass@5 and pass@10 are separate
  protocols with their own `metric_qualifier` saying so, and the solved-task counts say they are
  coverage counts under repeated sampling.
- **Agent scaffold as method, LLM as model** (`docs/collection.md` section 1): five harness
  `method` records, eight `model` records at `entity_level: service`, and 24 `configuration`
  records, one per system and reasoning setting, each `configuration_of` its harness and
  `uses_model` its model. `facets.method_types` is filled on every configuration, model and method.
- **Models stay at service level.** Only a served model id is printed, with no checkpoint, snapshot
  date or revision, so no record is assigned to a concrete checkpoint.
- **Nothing reused from the store.** None of the eight 2026 frontier models, neither BenchBench
  benchmark, and no Benchling source is present in `main`. The nearest hits are
  `ucpheno-20261022-model-gpt-5-6-sol` and `ucpheno-20261022-model-claude-opus-4-8`, which are
  different versions, and `pfmbench-*-cloning-clf`, which is a protein function class named
  "cloning" and nothing to do with molecular cloning. Checked by grepping
  `data/entities/*.jsonl` and `data/evidence/*/*.jsonl`.
- **No vocabulary concepts added.** `success-rate` and `count` cover every stored metric; what
  distinguishes the results goes in `metric_qualifier`, per coordinator ruling 10.
  `data/vocab/*.ttl` is untouched.
- **Caveats on `task` and `evaluator` records live in `scope_note`.** Those two kinds declare
  neither `limitations` nor `review` in `shared/omics/attribute-registry.ts`; the store's
  convention for them is `scope_note` (for example
  `lit-agents-20261013-biomlbench-task-tdcommons-herg`). Nothing was dropped, and the schema was
  not changed to suit this batch.
- **Per-task evaluations point at the task record.** The 120 Table G2 evaluations use the task as
  `assessment` and the grading-kind subset as `data`, so task identity and grading kind are both
  on the edge rather than in prose.
- **The advisor tool was unavailable** when called before writing (it returned "The advisor tool is
  unavailable. Do not try to use it again."), so the scope decisions above are the extractor's own
  and the reviewer should weigh them as such.

## Questions for the reviewer

1. Should Table D1's token, cost and runtime columns be extracted as results? The argument against
   is that cost is not a molecular endpoint; the argument for is that the paper devotes Section 4.3
   and Figure 5 to the cost frontier, the catalogue has `compute-cost` and `us-dollar` concepts,
   and the two cost columns are already parsed and cross-checked against Table D2. If they should
   be stored, should the token columns go with them, given they are means with no spread printed?
2. Is 224 results plus 223 claims the right size for this lane, given the issue asked for no
   numeric leaderboard extraction until configurations, denominators and tables were reviewed? That
   review is what this batch did, and the record counts follow from choosing whole tables rather
   than headline rows. Should any chosen table be dropped instead?
3. How should the Gemini 4 Argon low-effort 31.9% be handled? It is stored as printed with
   `source_anomaly` and `source_warnings`. Should it instead carry an `evidence_concerns` entry on
   the paper source scoped to that one result, or be withheld?
4. Is 500 the right denominator for every protocol-development result, including Grok 4.7 and
   Gemini 3.8 Flash whose graded counts are 498 and 496? The arithmetic says the authors used 500;
   the paper does not say it. Should those two systems' results carry a warning as well as the
   coverage note?
5. Should the aggregate score be a `result` at all, or a claim? It is a weighted average the
   authors computed from two measured rates rather than a measurement, but it is the paper's
   headline number and the one the announcement quotes.
6. Is `success-rate` the right metric concept for the aggregate, given Tables 2 and D2 head the
   column "Aggregate %" while Figures 2 and 5 call the same quantity "Aggregate accuracy (%)"? The
   alternative is `accuracy`; a new concept would respell an existing one, which ruling 6 forbids.
7. Is the evidence concern on the announcement source correctly scoped? It names only
   `claim-announcement-open-weight-gap` in `applies_to`, so the paper's results are untouched. The
   alternative reading is that an announcement that misstates its own paper's ranking is unreliable
   as a whole.
8. Should the five Figure 7 counts (39/39, 38/39, 0/39) be claims, as stored, or results? They are
   printed digits present in the text layer, so ruling 2 permits them, but they count construct
   presence in submitted panels rather than scored performance, which ruling 5 sends to claims.
9. Does the `dataset` record need a second dataset for the construct-design source studies? Six
   tasks reuse experimental records from published papers, which this batch records as a limitation
   rather than as separate dataset records, because no file-level provenance is printed.
