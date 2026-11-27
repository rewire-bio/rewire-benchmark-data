# Moving the agents off the graph

The owner decided on 26 November 2026 that agents read the database, not the knowledge graph
([rebuild.md](rebuild.md), step 8). This is the plan for the intake and reviewer agents and the
plugin skills. No agent has switched yet: `scripts/agents/intake.mjs`, `reviewer.mjs` and `kg.mjs`
still start the server.

## What ties them to the graph today

`scripts/agents/kg.mjs` starts rdf-kg-mcp v0.4.0 over stdio on the newest `kg/<id>` bundle
(`serve <bundle> --store memory`). The intake adds `--drafts --draft-dir <tmp> --draft-config
<draft block>`, and for an entity update `--draft-records data/entities`. The draft block comes
from `npm run kg -- draft-block` (`scripts/kg/draft-block.ts`), built from the code `records add`
uses. The first call is `dataset_info`, to prove the bundle loaded and to log its release.

| Tool | Used by | Replacement | State |
| --- | --- | --- | --- |
| `dataset_info` | both agents, at start | `kb/queries.py dataset_info` | Done: checkout commit, release ID when a discrepancies file is given, build time, counts by kind |
| `search` | intake (duplicate probes, link targets, verifier's `kg_search`), reviewer (duplicates), plugin | `kb/queries.py search` (`kb/search.py`) | Done: same index, scores and ranks as the graph on bundle 2026-11-26-36acdf5e0cfa |
| `describe_resource` | intake (verifier's `kg_describe`), plugin | `kb/queries.py describe_resource` | Done: returns the record itself, not statements; the caller changes |
| `draft_upsert` | intake (duplicate probes, the batch) | `kb/queries.py duplicates` (`kb/duplicates.py`), `intake-check --json` with the per-record checks, then `records add` | Tools done, not switched: `duplicates` gives the same answer as `draft_upsert` on all 1,176 single drafts and one batch of five compared on bundle 2026-11-26-36acdf5e0cfa; `intake-check` makes every per-record check listed below |
| `draft_change` | intake (entity update) | the intake's own changes file, which it already writes as the fallback | Exists as fallback |
| `draft_remove` | intake (probes, dropped records) | nothing: no overlay to clean | Goes away |
| `draft_export` | intake | `batchLines` in `intake.mjs`, already the fallback | Exists as fallback |
| `open_discrepancies`, `discrepancies_for_system`, `discrepancy_history`, `contested_results_for_use_case` | plugin | `kb/queries.py` queries of the same names | Done: equal rows on 89 parameter sets |
| `sparql_query` | plugin | read-only SQL on `kb.sqlite`, or the nightly bundle | Open |

## What each draft tool does today

All of it is in `src/rdf_kg_mcp/drafts.py` of rdf-kg-mcp. The overlay is in memory and is lost
when the process ends. Every check is advisory: `records add` and `records change` are the gate.

**`draft_upsert(record)`** takes a whole record as the store writes it. It refuses the call when
the ID is missing, cannot be part of an IRI, is one of the `--draft-records` lines, or is already
in the release. Otherwise it stores the record and returns `status` (added, replaced or unchanged),
`problems` (records add would refuse), `warnings` and `possible_duplicates`. Problems come from:

- the draft block's JSON Schema: the record fields in `recordSchema` order, the attribute keys
  each kind may carry and their types, and controlled values from the vocabularies;
- the kind: known, and draftable (not evaluation, result, claim or baseline);
- numbers beyond 2^53, non-finite numbers and lone surrogates;
- links: a pair listed twice, a link to itself, a target that is not a valid ID, an unknown
  relation, a relation the link rules do not allow from this kind or to the target's kind;
- `source_ids`: an ID listed twice or invalid, or a target that is not a source.

A link or source target found in neither the drafts, the store lines nor the release is a
warning, because the store may have gained it after the release was cut.

Only the name, kind and ID of a draft are read for its possible duplicates. They are three lists:

- `search`: the first 20 hits of a search for the name, limited to the class of the draft's kind
  (unfiltered for an unknown kind). A hit counts if it matched on its label or alias and the two
  names overlap by at least half: the larger of the share of the draft's words found in the hit's
  name and the share of the hit's words found in the draft's, where a word of four letters or more
  is also found as the start of a longer word. The first three that count are kept, with `rank`
  and `score`.
- `same name`: release records and discrepancies of any kind whose squashed name (letters and
  digits, case folded) equals the draft's, the draft's kind first, then by ID. At most ten;
  `same_name_omitted` counts the rest. A record found by both is `same name, search`.
- other drafts in the overlay with the same squashed name (`same name`) or an overlap of at least
  half (`near name`), with `in: draft`.

**`draft_change(id, changes, base_sha256)`** needs `--draft-records`. The record must be one of
those lines and of a draftable kind. `base_sha256` must equal the SHA-256 of the committed line,
and that line must be exactly `JSON.stringify` of itself parsed, so a change never rewrites fields
it does not touch. Changes are JSON Pointer `{path, value}` or `{path, remove: true}`; `id` and
`kind` cannot change, lists are replaced whole, and keys keep their committed order. The checks
above run on the line before and after; only problems the change brings in count. It returns the
new digest and a field-level diff.

**`draft_remove(id)`** drops a draft or a change.

**`draft_export()`** is refused while any draft has problems, and then deletes an earlier export.
Otherwise it writes, under `--draft-dir` and inline:

- `batch.jsonl`: new records sorted by ID, fields in schema order, keys sorted at every depth in
  `attributes` and `facets`, links sorted by relation, target and content, numbers as JavaScript
  writes them;
- `changes.jsonl` when there are changes: `{id, base_sha256, sha256, record}` per changed record;
- `summary.json`: the diff with every draft's problems, warnings and duplicates, and checksums.

The intake writes `batch.jsonl` to the batch folder and runs `scripts/agents/intake-check.ts`,
`npm run records -- add <batch.jsonl> <batch dir>` and `records -- check`; for an update,
`records -- change <review> <batch dir> --changes changes.jsonl`. It copies `summary` into the
batch's `kg.json`, where the reviewer reads `summary.added[].possible_duplicates`.

Two other checks run on the batch today, and they differ from the overlay in one way that
matters: the overlay reports problems per record, so the intake drops one record and keeps the
rest, while `records add` stops at the first problem and fails the whole batch.

- `scripts/agents/intake-check.ts` collected problems, prefixed with the record's ID (before the
  per-record checks below were added):
  the kind must be one the intake may add (model, method, benchmark, dataset, source), so a
  baseline is refused as the overlay refuses it; undeclared attributes and attribute values of the
  wrong type (`attributeIssues`); attributes `normalizeAttributes` would rewrite; the depth tier;
  a link to a store record that does not exist or that the relation rules do not allow; and the
  release's record schema (`validateSnapshot`). Two parts of it are not per record: a link to a
  store record that is missing or not allowed skips `validateSnapshot` for the whole batch, and
  `validateSnapshot` throws a plain error at the first record for some problems (a source that is
  not a source, a repeated ID, a link it cannot resolve), which names no record in its prefix.
- `records add` (`addBatch`, then `validateRecords` in `scripts/omics/schema.ts`) throws on the
  first problem: the record schema, an ID already in the store or twice in the batch, controlled
  vocabulary values (`validateVocabularies`), attributes, descriptions, derivations, concerns, a
  `source_ids` entry that is not a source record, a link target missing from the store and the
  batch, a relation the rules do not allow, then the SHACL shapes on the new records and their
  neighbours. It restores the store on any failure.
- `records change --changes` checks the base digest against provenance, that the record was not
  edited in place, that its ID and kind are unchanged, and that the bytes it writes have the digest
  in the file.

Server checks that nothing else made per record: controlled vocabulary values, a source that is
not a source record, an ID already in the store (all three only fail the whole batch in
`records add`); a link pair listed twice, a link to itself, a source listed twice, integers
beyond 2^53, non-finite numbers and lone surrogates in text or keys (none checked elsewhere).
And three things beyond checks: the possible duplicates, the drop-and-redraft loop that
per-record problems allow, and a fixed byte form for the batch.

## The smallest replacement

1. **A long-lived tool process over the database.** `kb/agent_tools.py serve` (to write) reads
   JSON lines on stdin, `{"name": ..., "arguments": {...}}`, and answers each with one JSON line,
   using `kb.queries.Records`. kg.mjs keeps `kgApi`, which wraps any object with `callTool`, so
   only `startKg` changes: build `kb.sqlite` with `python3 kb/migrate.py` (about 5 seconds), start
   the process, call `dataset_info`. The search index builds in about 3 seconds on the first call.
   One process per run, because each start rebuilds the index.
2. **`duplicates(records)`**, done: `python3 kb/queries.py duplicates --param records=<drafts>`
   (inline JSON, a file of JSON lines or a JSON list, or `-`), `Records.duplicates` in Python, the
   rules in `kb/duplicates.py`. The same three lists, from the same search and the same squashed
   names, over the public records of the database instead of the release, in the server's output
   shape (`in` stays `release`), so `kg.json` and the reviewer do not change. The other drafts are
   the other records of the same call, as in the export's summary. A draft whose ID is already in
   the database gets `error` instead, as the server refused it. Tests: `kb/tests/test_duplicates.py`
   checks the rules on 315 records of all 17 kinds of the current store; `kb/tools/compare_duplicates.py`
   runs the server's `DraftOverlay.upsert` (what `draft_upsert` calls, in process rather than over
   MCP) and the tool on the same drafts against bundle 2026-11-26-36acdf5e0cfa, a database built
   from its commit and the bundle's `discrepancies.json`: 1,176 single drafts from 315 records
   (each record under a new ID, its name squashed and upper-cased, two of its words among words no
   record has, and a name no record has) and one batch of five read back as the export summarises
   it. Every answer was equal, scores, ranks, order and `same_name_omitted` included. The answer
   gives only the duplicate lists: the rest of `kg.json` (release, `manifest_sha256`,
   `batch_sha256`, each record's links and warnings, from the export's summary) has to be built by
   the intake when it switches. Pass the agents' discrepancies file,
   or `--discrepancies none`, as for `search`: discrepancies are candidates of the `same name` list
   too.
3. **Checks before writing, per record.** Done in `intake-check.ts` (`recordChecks`): controlled
   values (the per-record form of `validateVocabularies`, which stops at 20), an ID already in the
   store (read from the provenance log, so evidence IDs count; a record from a changes line must
   instead be in the store) or twice in the batch, a source listed twice, not a source record, or
   in neither the batch nor the store, a repeated link pair, a link to itself, a link to another
   record of the batch that the relation rules do not allow (links to stored records were already
   checked), and numbers and
   text JSON does not carry exactly. The integer rule is JavaScript's: an integer beyond 2^53 is
   flagged when `JSON.stringify` would write it as digits (below 1e21), which is what the server
   would have read in the exported bytes. `--json` prints `{records: {<id>: [problems]}, batch:
   [problems]}`; `batch` holds what names no record of the batch. Still to do, in `draftThroughKg`:
   replace `upsert` with `intake-check --json` on the batch, then `duplicates`; drop records with
   problems or unruled duplicates, prune their links and unused sources, and repeat, as today. A
   problem under `batch` should stop the run, as a refused source does now, unless dropping the
   records with problems clears it in the next round; because a stored-link problem hides the
   release validation of the whole batch, a batch can need one more round than with the server.
   A link target missing from the store is an error, not the overlay's warning, since the
   database is the current checkout. These checks stay in TypeScript because they are the store's
   own code; the draft block's JSON Schema was derived from it.
4. **Export.** `batchLines` in `intake.mjs` writes the bytes `draft_export` writes (it is the
   fallback today, and a test checks it against a stand-in for the export). For an update, the
   intake's own changes line (the `own` branch of `draftChange`) is the replacement. The server's
   check that the committed line is its own `JSON.stringify` is covered by `records change`: the
   intake's `base_sha256` is the digest of the line's bytes and the provenance digest is that of
   the serialised record, so a line in any other form is refused there.
5. **`kg_describe`** reads `record.description`, `name`, `kind`, `sources` and `links_out` from
   `describe_resource` instead of parsing statements.

## Order to switch, and what to test

1. **Reviewer.** Read-only (`search`, `dataset_info`) and the smaller program. Replace the bundle
   step in `reviewer.yml` with building `kb.sqlite`. Test: `tests/agents-reviewer.test.ts`
   unchanged (it stubs `kg`); then replay `possibleDuplicates` on the last ten intake pull requests
   against the bundle and against the database. They should differ only by records added after the
   bundle's release.
2. **Intake, reading.** `kgCandidates` link-target search and the verifier's `kg_search` and
   `kg_describe`. Test: the dry run on `tests/agents-intake-kg-fixtures`. Its bundle is RDF, so
   add the same records as store lines (`data/entities/*.jsonl` in a fixture folder, written once
   from the records the bundle was exported from) and build the fixture database with
   `kb/migrate.py` run in that folder; the candidate text must be the same.
3. **Intake, drafting.** Duplicate probes and `draftThroughKg` on the new loop, `batchLines` for
   the export, the `own` changes file for updates. Test: on the fixtures, `batch.jsonl`,
   `changes.jsonl` and `kg.json` byte for byte against a run with the server; the dropped records
   and their reasons the same.
4. **Plugin skills** (other repository): the four discrepancy queries and `search` map one to one.
   `describe_resource` changes shape. Free-form SPARQL has no direct replacement: offer read-only
   SQL on `kb.sqlite`, or keep the nightly bundle for it.
5. **Workflows.** Remove the bundle download, `uv tool install rdf-kg-mcp` and the draft block from
   `intake.yml` and `reviewer.yml`.

Run each agent once on a real issue between steps and compare its pull request with the last one
made through the server.

## What could go wrong

- **Database against release.** The overlay checked against a release up to a day old; the
  database is the checkout. Records merged since the release now count as duplicates and link
  targets. That is better, but rulings in old `kg.json` files will not match exactly.
- **Public records only.** The graph, and so the search index, hold only public records. An
  excluded or not yet checked record is in the store but not searched, as today. Whether
  duplicates should include them is a decision to take once the switch works.
- **Discrepancy labels.** The graph's search also returns discrepancies. Without
  `discrepancies.json` the tool derives them (about six seconds). The agents should pass
  `--discrepancies none`: a kind filter never matches a discrepancy, but leaving them out changes
  the document count, so scores move slightly (2080.1 against 2080.2 for Evo 2) and ranks can.
- **Identity.** The bundle named its release. A database built from the checkout has none:
  `dataset_info` gives the checkout's commit, and `release_id` only when a discrepancies file is
  passed. The agents should log the commit. Recording the commit in `kb.sqlite` itself would need
  a change to `kb/migrate.py`.
- **Ranking drift.** `kb/search.py` copies rdf-kg-mcp v0.4.0. A later server version may rank
  differently. The gold pairs in `compare_queries.py` fail the run below 95 percent in the top 5
  (the graph gets 97.0), which catches a regression on our side only.
- **Lost safeguards.** If step 3 drops the duplicate check or the drop-and-redraft loop, bad
  batches reach a pull request. The fixture comparison in step 3 is the guard.

## What can be deleted afterwards, and what stays

Once both agents and the plugin have switched:

- `scripts/agents/kg.mjs`'s MCP start-up, `scripts/kg/draft-block.ts`, the `draft-block` command in
  `scripts/kg/export.ts`, `tests/kg-draft-block.test.ts`, the fixture bundle under
  `tests/agents-intake-kg-fixtures/bundle`, and the server tests in `tests/agents-intake-kg.test.ts`.
- The knowledge-graph steps and the `RDF_KG_MCP` setting in `intake.yml` and `reviewer.yml`.
- The `full_build` branch of `release.yml`, which builds a bundle during a release.

What must stay:

- `kg-release.yml` with `kg:bundle`, `kg:verify` and `kg:publish`: the nightly bundle is the
  cross-check on `kb/discrepancies.py` and the source of truth for `kb/tools/compare_queries.py`.
  That needs `scripts/kg/export.ts`, `build.py`, `contradictions.py`, `release_graph.py`,
  `product_queries.py`, `attribute-terms.ts`, `publish.ts` and `requirements.txt`.
- `scripts/kg/search-gold.rq`, the gold pairs for `kb/search.py`.
- The SHACL checks: `records add` and `records change` run `npm run kg -- subset` and
  `kg:build --shapes-only`, and `data.yml` runs the shapes on every record. They stay until the
  shapes are checked another way.
- `scripts/kg/extract_terms.py` and `migrate-discrepancy-ids.py` are not used by any workflow;
  deleting them is a separate question for the owner.
