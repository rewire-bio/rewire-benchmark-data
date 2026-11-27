# Moving the agents off the graph

The owner decided on 26 November 2026 that agents read the database, not the knowledge graph
([rebuild.md](rebuild.md), step 8). This is the plan for the intake and reviewer agents and the
plugin skills. Nothing in `scripts/agents/` has changed yet.

## What ties them to the graph today

`scripts/agents/kg.mjs` starts rdf-kg-mcp v0.4.0 over stdio on the newest `kg/<id>` bundle
(`serve <bundle> --store memory`). The intake adds `--drafts --draft-dir <tmp> --draft-config
<draft block>`, and for an entity update `--draft-records data/entities`. The draft block comes
from `npm run kg -- draft-block` (`scripts/kg/draft-block.ts`), built from the code `records add`
uses. The first call is `dataset_info`, to prove the bundle loaded and to log its release.

| Tool | Used by | Replacement | State |
| --- | --- | --- | --- |
| `dataset_info` | both agents, at start | `kb/queries.py dataset_info` | Done: release ID, build time, counts by kind |
| `search` | intake (duplicate probes, link targets, verifier's `kg_search`), reviewer (duplicates), plugin | `kb/queries.py search` (`kb/search.py`) | Done: same index, scores and ranks as the graph on bundle 2026-11-26-36acdf5e0cfa |
| `describe_resource` | intake (verifier's `kg_describe`), plugin | `kb/queries.py describe_resource` | Done: returns the record itself, not statements; the caller changes |
| `draft_upsert` | intake (duplicate probes, the batch) | `duplicates` check in kb, plus `intake-check` and `records add` | Not started |
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

Possible duplicates are three lists: up to three search hits of the same class on the name whose
label shares at least half its words with it (`match: search`), up to ten release records with the
same squashed name (letters and digits, case folded; `same name`), and other drafts with the same
squashed name or half their words in common.

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

`records add` already checks more than the overlay: the record schema, no duplicate IDs,
vocabularies, attributes, descriptions, derivations, concerns, links against the whole store, and
the SHACL shapes on the new records and their neighbours, restoring the store on any failure.
`records change --changes` checks the base digest against provenance, that the record was not
edited in place, that its ID and kind are unchanged, and that the bytes it writes have the digest
in the file.

So the overlay adds three things records add does not: the possible duplicates, earlier feedback
that lets the intake drop a bad record and draft the rest again, and a fixed byte form for the
batch.

## The smallest replacement

1. **A long-lived tool process over the database.** `kb/agent_tools.py serve` (to write) reads
   JSON lines on stdin, `{"name": ..., "arguments": {...}}`, and answers each with one JSON line,
   using `kb.queries.Records`. kg.mjs keeps `kgApi`, which wraps any object with `callTool`, so
   only `startKg` changes: build `kb.sqlite` with `python3 kb/migrate.py` (about 5 seconds), start
   the process, call `dataset_info`. The search index builds in about 3 seconds on the first call.
   One process per run, because each start rebuilds the index.
2. **`duplicates(records)`**, a new tool with the server's rules: the same three lists, from the
   same search and the same squashed names, over the database instead of the release. It is the
   only check the overlay made that nothing else makes, so it is ported exactly, with the same
   output shape, so `kg.json` and the reviewer do not change.
3. **Checks before writing.** In `draftThroughKg`, replace `upsert` with a local loop: for each
   record, link and source targets must exist in the database or in the batch (an error now, not a
   warning, since the database is the current checkout), then `duplicates`, then
   `intake-check.ts` on the batch. Drop and repeat as today. The schema, vocabulary and link rule
   checks are left to `intake-check` and `records add`, which already run and are the gate; the
   standard library has no JSON Schema validator, and the draft block is derived from those checks
   anyway.
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
   `kg_describe`. Test: the dry run on `tests/agents-intake-kg-fixtures` with a fixture database
   built from that bundle's records; the candidate text must be the same.
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
  `discrepancies.json` the tool derives them (about ten seconds); pass the release's file, or skip
  them for the agents, since they never match a record kind filter.
- **Ranking drift.** `kb/search.py` copies rdf-kg-mcp v0.4.0. A later server version may rank
  differently; the gold pairs in `compare_queries.py` catch a regression on our side only.
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
