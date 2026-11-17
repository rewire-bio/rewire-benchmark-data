# Preserving source bytes

Every claim in this store rests on a primary source. 45.2 percent of the evidence citations rest on
bytes nobody holds: 47,081 of 104,243, measured in ADR 0003 over this store. This document says how
a source is fetched and kept, what may be published from it, and how a licence decision is recorded
and revisited.

One rule covers everything below. A licence decides what may be published. It never decides what is
fetched and never decides what is stored. A source whose licence nobody has determined is fetched,
stored privately, and listed for determination later.

Design records: [ADR 0003](adr/0003-source-preservation.html) for the receipt and licence design and
[ADR 0004](adr/0004-storage-substrate.html) for the object store and manifest. Collection procedure:
[collection.md](collection.md). Record fields: [record-contract.md](record-contract.md).

## The owner determinations of 2026-11-17

Eight rulings, all dated 2026-11-17, all from
[issue 276](https://github.com/rewire-bio/rewire-benchmark-data/issues/276). They are decided. Each
is written here with what it rests on, because a ruling with an unstated premise cannot be revisited.

### 1. Non-commercial use: yes. Dated 2026-11-17.

Our use of this data is NonCommercial use under CC 4.0, so a CC BY-NC or CC BY-NC-ND work may be
stored and republished here under its licence.

**Premise, as stated by the owner:** the benchmark data and the graph will never be sold, licensed to
a partner or put behind a paywall, in whole or in part.

**This ruling falls if the premise changes.** It is not inherited. If any part of the data or the
graph is ever sold, licensed to a partner or paywalled, every tier that rests on the non-commercial
reading has to be determined again from the licence text, not carried forward from this document.
The tiers concerned are `t1-public-nc` and `t3-verbatim-nd-nc`, which together hold 102 sources
today. Both tier concepts in [data/vocab/archive-tier.ttl](../data/vocab/archive-tier.ttl) carry the
same warning in a `skos:scopeNote`, so the premise travels with the vocabulary.

### 2. A derived text layer of a no-derivatives work may be published. Dated 2026-11-17.

It follows the original's tier. CC 4.0 states that technical modifications across media and formats
never produce adapted material, and a `pdftotext -layout` layer is a format conversion, not an
adaptation. A text layer of a CC BY-NC-ND work therefore carries that work's tier and is published
wherever the verbatim original may be published.

This corrects the distribution implication of the 2026-11-16 GPN-MSA ruling.

**Rests on:** the text of CC 4.0 and on the text layer being a mechanical, re-runnable conversion.
If a normaliser ever selects, reorders or rewrites content rather than converting a format, its
output is adapted material and this ruling does not cover it.

### 3. The seven restrictively licensed originals already committed. Dated 2026-11-17.

Seven original artifacts under restrictive licences are already committed to this public repository:

    gpn-paper-20261116-source-biorxiv-v3
    gpn-paper-20261116-source-pnas-2023
    gpn-paper-20261116-source-pnas-2023-si-appendix
    phylogpn-2025
    phylogpn-20261116-source-supplement
    protein-stability-20261009-source-dieckhaus2024
    protein-stability-20261009-source-pancotti2022

They are removed from the tip tree for clone-cost reasons regardless, and their bytes cannot be
removed from git history either way. No separate ruling was needed. Their hashes stay in the
manifest with `exposure: pre-policy`, so the set stays enumerable rather than quietly disappearing.
The list is held in code at `prePolicySourceIds` in
[scripts/licence/map.ts](../scripts/licence/map.ts) and checked against the store by
[tests/licence-map.test.ts](../tests/licence-map.test.ts).

### 4. Takedown contact: tim@rewire.it. Dated 2026-11-17.

A path that removes an object and marks its manifest row must exist before the first public upload,
not after. The steps are in [Takedown](#takedown) below, and every one of them is a command or a
named function.

That order was not kept. The 195 objects under [What is public today](#what-is-public-today) went
public on 2026-11-17 while the manifest row still had no field for when an object was removed, why,
or at whose request. The three fields and the code that uses them were added the same day, after the
upload and not before it. No removal has been recorded under `docs/reviews/`, so nothing was
delayed by it.

### 5. Restricted bytes live in Cloudflare R2. Dated 2026-11-17.

Four repository secrets are needed before CI can use it: account id, access key id, secret access
key, bucket name. None is present in this environment. Nothing in the fetch, verify, status or
import path needs one, and a fork pull request runs all of them without a credential.

The ruling divides the two backends, and `npm run archive -- upload` keeps the division: R2 takes
the rows the manifest marks restricted and refuses the rest, because a public object is published as
a release asset instead (`npm run archive -- publish`).

### 6. No human review anywhere. Dated 2026-11-17.

Everything is automated. A receipt states that a claim is machine extracted, span verified and
unreviewed. The reviewer field carries a tool identity, never a person. This closed the review step
in [collection.md](collection.md) as it was written, and that document has been changed with it.

### 7. Scope is the documented use cases. Dated 2026-11-17.

The boundary of "biological foundation models" for this graph is the use-case set in
[docs/reviews/use-cases/](reviews/use-cases/) and rewire.it #365, not a modality list. A model family
outside those use cases is out of scope until a use case brings it in.

### 8. The copyleft code licences publish at `t0-public`. Dated 2026-11-17.

GPL-3.0, GPL-2.0 and AGPL-3.0 permit verbatim redistribution provided the licence text travels with
the work, which is exactly what this archive does. Their copyleft conditions govern distributing
modified work, not storing or redistributing an unmodified copy. AGPL's network clause concerns
running modified software as a service and does not reach an archived file.

The four strings the ruling covers are rows in [the licence map](../data/archive/licence-map.tsv),
at `t0-public`, with the counts the resolver measured: GPL-3.0 (27 sources), GPL-2.0 (7), AGPL-3.0
(3) and AFL-3.0 (2). The first three take the new `copyleft-code` family in
[licence-family.ttl](../data/vocab/licence-family.ttl). AFL-3.0 is permissive rather than copyleft,
so it takes the existing `permissive-code` family and is listed here only because it came up in the
same set.

No source record carries any of these strings. They are what GitHub's licence endpoint served for
repositories whose records carry no licence at all, so each is a third kind of licence-map row: not
a record's string, and not a spelling of a string an earlier row reads. A ruling row says so in its
note, naming the ruling and its date, and `tests/licence-map.test.ts` holds that form.

**Rests on:** the text of those licences and on the archived copy being unmodified. If this archive
ever published a modified copy of a work under one of them, the copyleft conditions would reach that
copy and this ruling would not cover it. The ruling says nothing about where the licence text sits
in a particular object: an object is often one file out of a repository rather than a tree, and the
owner's reading is about what the licence permits, not about which bytes a given fetch returned.

Nothing else from the resolver's unmapped list is ruled on here.
`http://www.elsevier.com/open-access/userlicense/1.0/` and the rest stay unmapped, so
`npm run licence:resolve` keeps exiting non-zero. That is the intended signal, not a defect.

## What is public today

195 objects are published as release assets of this repository, on the sixteen tags
`archive/objects-<0-f>`. Measured on 2026-11-17 by listing each tag's assets and reading each
asset's row out of the manifest:

    for s in 0 1 2 3 4 5 6 7 8 9 a b c d e f; do \
      gh release view "archive/objects-$s" --repo rewire-bio/rewire-benchmark-data \
        --json assets --jq '.assets[].name'; done

An asset is named `<sha256>.gz`, so its row is the line for that key in
`data/archive/objects/<first hex digit>.jsonl`.

| Tier | Published objects |
| --- | --- |
| `t0-public` | 147 |
| `t1-public-nc` | 2 |
| `t2-verbatim-nd` | 1 |
| `t3-verbatim-nd-nc` | 45 |

All 195 are `exact-bytes` rows: the verbatim original of one primary source, gzipped under the
sha256 of its expanded bytes. No text layer is published yet, so determination 2's permission for a
derivative of a no-derivatives work is recorded and not yet used.

These are objects, not source records. The 104 under [The measured numbers](#the-measured-numbers)
counts source records at the three tiers determinations 1 and 2 cover, whether the archive holds
their bytes or not.

The 48 publications outside `t0-public` rest on determinations 1 and 2, so they are reconsidered if
the premise behind determination 1 ever changes. If any part of this data or the graph is sold,
licensed to a partner or paywalled, the 47 objects at `t1-public-nc` and `t3-verbatim-nd-nc` have to
be determined again from their licence text rather than carried forward from this document, and an
object whose licence no longer permits publication goes down the [Takedown](#takedown) path.

One thing the manifest does not say. The publish run used `--no-mark`, because a fetch was running
and a fetch owns the shard files, so every manifest row still reads `store: local-cache` while 195
of them are release assets. The release listing is the record of what is public until a later
`npm run archive -- publish` marks those rows, which it does without uploading anything.

## What is not implemented, and why

ADR 0003 designs a drift and re-pinning apparatus: a second identity per capture, a re-retrieval
comparison against the hash a record already pins, a `content_match` classification, a tool-version
drift guard, Wayback and CDX recovery, and rescue waves ordered by citation weight. None of it is
built here, and none of it is planned as part of this work.

The reason is that the store is being recollected, not audited. Every claim in the evidence store is
being extracted again from the primary sources with new tooling. A comparison against an old pinned
hash answers a question nobody is asking: whether a value extracted under the previous tooling still
matches its source. The new extraction answers that directly, by reading the source again.

What is kept from ADR 0003 is the part that makes a stored source usable: the fetch receipt, the
licence tiering, the text layer and the manifest. Each stored object still carries a plain sha256,
because that is what lets a later claim cite a span in a specific file and what deduplicates the
store. That is bookkeeping, not forensics.

One consequence is worth stating plainly. We do not know, and will not find out from this work,
which of the 1,453 pinned hashes still reproduce. A 2026-09-19 re-retrieval of 859 of them found 175
returning different bytes, 20.4 percent, recorded in
`data/omics/audits/2026-09-19-source-access.receipts.jsonl`. Those hashes are left exactly as they are on every source record.
Nothing in this work rewrites a pin, and nothing in it treats a pin that no longer reproduces as an
error.

## The fetch receipt

One receipt per source per attempt, appended to
`data/omics/audits/<date>-archive-fetch.receipts.jsonl`. The shape is `fetchReceiptSchema` in
`shared/archive/schema.ts`, at `schema_version: 1`. A receipt is written whether the fetch worked or
not, because a source we could not get is a fact the recollection needs.

| Field | Holds |
| --- | --- |
| `schema_version` | `1` |
| `source_id` | the source record this attempt was for |
| `requested_url` | the URL asked for |
| `final_url` | the URL after redirects, or absent when nothing answered |
| `http_status` | the status of the response that ended the attempt |
| `fetched_at` | when the attempt ran, UTC to the second |
| `content_type` | the `Content-Type` header exactly as served |
| `bytes` | how many bytes arrived |
| `sha256` | the digest of the bytes as received |
| `route` | which route produced them: `direct`, `unpaywall`, `europepmc` or `preprint` |
| `routes_tried` | one entry per route attempted, in order, whether it worked or not |
| `outcome` | `stored`, `not_artifact` or `failed` |
| `reason` | why we do not hold the artifact, on anything but `stored` |
| `source_class` | the host-behaviour class the treatment was keyed on |

A receipt states only what one transfer returned on one date. It states no value and names no
entity, so it is an observation log and not a record. Receipts are never edited after merge. A
second attempt is a second line.

### A source we could not get

A failed fetch is a receipt with `outcome: failed` and a `reason` naming why no bytes arrived. The
whole vocabulary is the closed `reasons` list in `shared/archive/schema.ts`; these thirteen are the
ones a failure uses:

    http_error        network_error     timeout             empty_body
    too_large         not_found         rate_limited        host_stopped
    no_doi            no_open_copy      unpaywall_no_email  paywalled_not_held
    unsupported_url

`routes_tried` shows every route that was attempted and what each returned, so "we tried in this
order" is a checkable claim rather than a description.

Three things do not happen when a fetch fails. The source record is not edited. No
`evidence_concerns` entry is added: a source whose bytes we failed to retrieve is not a source whose
content is in doubt, and marking it would withhold every result resting on it. And nothing is
inferred from a summary, a mirror or a search result in place of the artifact.

`host_stopped` is the one reason that is about us rather than the source. A host that returns 429 or
503, or that blocks the fetcher, stops the run for that host. The remaining sources on it are
recorded as not attempted and the run reports it. We do not retry past a block.

### A source whose artifact we did not get

HTTP 200 does not mean we got the artifact. The 2026-11-17 pilot stored 38 of 40 sources and
reported all 38 as held; four of them were a cookie wall, a page that rendered to nothing, a table
landing page with the table absent, and a publisher's own HTML for an article Europe PMC held as
JATS XML the whole time. Those four are not failures, and calling them `stored` overstated what the
archive holds, so they get an outcome of their own.

`outcome: not_artifact` means bytes arrived, we kept them, and they are demonstrably not the source.
The bytes are stored and carry a manifest row, because what a host served is a fact worth holding,
but only `stored` counts as the source being held and `npm run archive -- status` reports the two on
separate lines. A `not_artifact` source is retried by a later run under `--retry-failed`: a cookie
wall or a missing Unpaywall address is a condition of the run, not a property of the source.

Three reasons are reserved for it, and `checkArtifact` in `shared/archive/artifact.ts` sets them:

    interstitial_body     text_below_threshold    publisher_html_only

The thresholds are measured over the 274 committed artifacts and the 38 pilot objects, not chosen.
That module carries each floor, what set it, and why the two phrase windows are where they are. One
rule in it is worth repeating here, because it changes what the route chain does rather than only
how a receipt reads: a publisher's HTML for a source carrying a DOI never ends the chain. The three
DOI routes run anyway, and the HTML is kept only when none of them reaches the artifact. On the
pilot that one rule replaced 657 KB of Nature HTML with the 237 KB JATS XML of PMC12022141.

## Licence tiers

A licence answers two separate questions, and this repository used to treat them as one.

1. May the verbatim original bytes be redistributed?
2. May a derivative be redistributed: a text layer, a canonical JSON, a WARC payload?

CC BY-NC-ND answers yes to the first, non-commercially and with attribution, and restricts the
second. The six tiers are the cross product of those two answers, plus the two cases where nothing
is published at all. The concepts are in
[data/vocab/archive-tier.ttl](../data/vocab/archive-tier.ttl) and the keys match the `tiers` union in
`shared/archive/schema.ts`.

| Tier | Verbatim original | Derivative | Licences | Sources |
| --- | --- | --- | --- | --- |
| `t0-public` | publish | publish | CC0, CC BY, CC BY-SA, MIT, Apache-2.0, BSD, AFL-3.0, ODbL, GPL-2.0, GPL-3.0, AGPL-3.0 | 263 |
| `t1-public-nc` | publish, non-commercially | publish, non-commercially | CC BY-NC, CC BY-NC-SA | 22 |
| `t2-verbatim-nd` | publish | see determination 2 | CC BY-ND | 2 |
| `t3-verbatim-nd-nc` | publish, non-commercially | see determination 2 | CC BY-NC-ND | 80 |
| `t4-private` | store only | store only | arXiv non-exclusive, publisher terms, bespoke restricted terms, all rights reserved, no licence determined | 1,116 |
| `t5-no-store` | no copy kept | no copy kept | a recorded decision not to store, and an object removed after a takedown | 0 |

Determination 2 settles the derivative column for `t2-verbatim-nd` and `t3-verbatim-nd-nc`: a text
layer is a format conversion, not adapted material, so it follows the original's tier and is
published with it. A derivative that selects or rewrites content rather than converting a format is
not covered and stays private.

Nothing lands below `t5-no-store`, and nothing needs to. A licence that forbids sharing the verbatim
work does not permit sharing a derivative of it either, so the "no verbatim, yes derivative" corner
is empty by construction.

Three rules are enforced in code, not by convention.

- **A licence never blocks a fetch.** The default for an unresolved licence is `t4-private`, set as
  `defaultTier` in `shared/archive/schema.ts`. Unknown never means public and never means unstored.
  Refusing to capture a source until someone determines its licence adds two to five minutes to
  every new source, and the predictable response is to mark everything unreported and private, which
  satisfies the gate and defeats it. ADR 0003 measures the result: 913 of the 1,153 sources with a
  pinned hash and no stored copy record no licence at all.
- **The policy restricts publication, not possession.** A private copy of a work the team lawfully
  accessed, made for computational analysis, is ordinary research practice. `t5-no-store` is the only
  tier that produces no bytes.
- **A string with no row fails the build, and never a fetch.** `tests/licence-map.test.ts` fails
  the build when the store carries a licence string the map does not cover. A fetch already running
  does not stop: `determineForSource` stores the object at `t4-private` and writes the unmapped
  string into `observed_licence`, so the manifest row shows exactly which string nobody has mapped.
  Widening the default in the map to absorb an unmapped string is the one change this design does
  not allow.

What stays public for a source in a private tier: the whole fetch receipt, which carries the
digest, the byte count, the media type, the requested and final URL, the status and the retrieval
time; and the manifest row, whose `derived_from` and `derivation` give the container digest and the
exact command that produced a text layer, so a reader with lawful access reproduces the evidence
themselves. Those are facts about the work, not the work.

## The licence map

[data/archive/licence-map.tsv](../data/archive/licence-map.tsv) holds one hand-reviewed row per
distinct value of `attributes.licence` on a source record. It is hand written, not generated: a
regular expression over these strings is what produced the nine-record discrepancy ADR 0003 records,
and the strings that matter most are prose. Determination 6 covers claim and value review, where no
person is in the loop; a licence determination is a legal call I make and sign under my own name, and
that is why the determinations at the top of this document exist.

Columns: `licence` exactly as the record carries it, `family`, `archive_tier`, `basis`, `note`. The three
controlled columns are concept keys in
[licence-family.ttl](../data/vocab/licence-family.ttl),
[archive-tier.ttl](../data/vocab/archive-tier.ttl) and
[licence-basis.ttl](../data/vocab/licence-basis.ttl).

`basis` records how the string was read. `identifier` means the string is a licence identifier and
nothing else. `prose` means prose, a URL or a quotation that names one licence without ambiguity.
`conflicting` means the source states two licences that disagree, in which case the row takes the
restrictive reading and the note records both statements. `unresolved` means no family could be
determined, which puts every source carrying that string in the triage queue.

A row can be one of three kinds, and the licence column is the lookup key for all three. A record
row is a distinct value of `attributes.licence`. A spelling row is a string a metadata service
serves that an earlier row already reads, and it carries that row's family and tier and names it in
its note. A ruling row is a string a metadata service serves that no record carries and no earlier
row reads, so the owner ruled on it directly and the note names the ruling and its date;
determination 8 above is the only one so far. `tests/licence-map.test.ts` checks each kind against
its note form, so an orphan row cannot hide among them.

Adding a licence string to the store means adding a row in the same pull request. Read the licence
text, pick the family, take the tier the family implies, and say in the note anything a later reader
needs: which bytes the licence covers, which version of a Creative Commons licence was stated, and
what the source said that the row does not carry.

`licenceClassifier()` in [scripts/licence/map.ts](../scripts/licence/map.ts) is what the fetcher
calls. It matches the `LicenceClassifier` type `shared/archive/schema.ts` declares. An object can
answer for more than one source record, because 206 of the 1,255 distinct URLs in the store are
carried by more than one (`npm run archive -- worklist`), so the classifier takes the most
restrictive tier of them. Ranked least to most restrictive: `t0-public`, `t2-verbatim-nd`,
`t1-public-nc`, `t3-verbatim-nd-nc`, `t4-private`, `t5-no-store`. No-derivatives sits below
non-commercial because determination 2 settles the derivative question, while determination 1 rests
on a premise that can change.

## The triage queue

[maintenance/reports/licence-triage-2026-11-17.tsv](../maintenance/reports/licence-triage-2026-11-17.tsv)
lists every source needing a licence determination. It is generated. Do not edit it.

    npx tsx scripts/licence/triage.ts

That writes `maintenance/reports/licence-triage-<date>.tsv` and prints the counts. `--stdout` writes
the rows instead, and `--date` names the file.

One row per source: `source_id`, `reason`, `resolver`, `host`, `publication_status`, `doi`, `url`,
`licence`. `resolver` says where to look for terms, keyed on the host class: Crossref for a
publisher, the arXiv API, a Europe PMC permissions statement, a preprint server's `license` field,
the repository LICENSE at the pinned commit, a model card's front matter, or a data repository's
rights field.

A source whose `missing_metadata.licence` reason is `inapplicable` is left out. A curator's factual
receipt is not a third party's work and no licence applies to it. A recorded `unreported` stays in
the queue: the source page stating nothing is not the end of the search, because Crossref, Unpaywall
and a repository LICENSE are still to ask.

Licence resolution is its own command. It does not run inside the fetch:

    npm run licence:resolve

It asks Crossref, GitHub, Hugging Face, a preprint server and Europe PMC what a source's licence is
and writes one candidate per answer to `data/archive/licence-candidates.jsonl`. It writes no source
record and no manifest row, and it takes no tier from anywhere but the licence map. The run of
2026-11-17 is reported in
[maintenance/reports/licence-resolve-2026-11-17.md](../maintenance/reports/licence-resolve-2026-11-17.md),
with the 39 strings the map has no row for. Promoting a candidate into `attributes.licence` is a
record change like any other and happens the next time someone touches that source.

What the fetch does carry is the licence map. `licenceClassifier()` is passed into `runFetch()`, so a
new object is recorded at the tier the map gives for the licence string the source record already
holds, and an unmapped string lands in the row's `observed_licence` at `t4-private`. That is a map
lookup over the store, not a resolution against a service.

ADR 0003 designed the other arrangement: a resolver inside the capture path, writing an
`observed_licence` candidate into the manifest row with its resolver and its date, each resolution
itself a capture. That is not what was built. A candidate nobody has reviewed is not a licence
determination, and a separate file keeps the manifest carrying only what the map decided. ADR 0003
is a dated design record and is left as it was written; this paragraph is the deviation.

## Making a resolved licence real

A manifest row carries the tier the classifier gave it when the bytes landed. Adding a row to the
licence map, or resolving a licence against a service, changes nothing on its own: the row still
says what it said at fetch time. One command closes that gap.

    npm run archive -- reclassify --dry-run
    npm run archive -- reclassify

It re-reads every manifest row against the licence map as it stands today and the candidates in
`data/archive/licence-candidates.jsonl`, and writes back `archive_tier`, `visibility` and
`observed_licence` through `updateRow()`. Nothing else on the row moves: not `sha256`, `bytes`,
`media_type`, `layer`, `origin`, `first_seen_at`, `store`, `exposure`, `source_ids` or the three
removal fields. No bytes are read and nothing is fetched, so it needs no credential and no network.

Three rules, held by `tests/archive-reclassify.test.ts`.

- **A row only moves to a tier the evidence justifies.** Evidence is a licence string with a row in
  the map, read off the source record or off what a service served. A row whose sources produce no
  evidence keeps the tier it has. Absence is not a determination, and reading it as one would
  quietly re-privatise rows an earlier reviewed map made public.
- **A human-recorded licence beats a candidate.** If a source record carries a licence string, that
  string decides, mapped or not, and no candidate is consulted for that source. A candidate is a
  service's statement nobody has reviewed; `attributes.licence` is a determination somebody signed.
  A recorded string the map has no row for keeps the source at `t4-private` with the string on the
  row, which is the same thing a fetch does with it.
- **A move from public to restricted is a takedown, not a reclassification.** Those bytes may
  already be a release asset, so the command lists every such row on its own and writes nothing at
  all, not even the safe moves, and exits 1. Removing a published object goes down
  [Takedown](#takedown), which records who asked and why.

A row at `t5-no-store` is skipped before any of that, so no licence reading lifts a row out of a
recorded decision not to hold bytes.

A move to a more restrictive tier that stays publishable, `t0-public` to `t3-verbatim-nd-nc` for
instance, is not a takedown and does not block the run. It is still listed on its own, because the
bytes may already be a release asset carrying the old tier and the tags want rereading after such a
run.

The candidates file is re-read against the current map rather than trusted. Its `status`, `family`
and `archive_tier` were written against the map as it stood when the resolver ran, and they are
stale the moment a row is added; the observations behind them are not. `buildCandidate()` in
`scripts/licence/resolve.ts` does the re-reading, so the resolver's own rules hold here too: a tier
comes from the map alone, and two services whose families disagree resolve to nothing.

### The 2026-11-17 run

Measured by `npm run archive -- reclassify --dry-run` and then the same command without it, over
1,167 manifest rows:

| Tier | Rows before | Rows after |
| --- | --- | --- |
| `t0-public` | 247 | 719 |
| `t1-public-nc` | 22 | 49 |
| `t2-verbatim-nd` | 2 | 3 |
| `t3-verbatim-nd-nc` | 71 | 100 |
| `t4-private` | 825 | 296 |
| `t5-no-store` | 0 | 0 |

529 rows moved, all of them out of `t4-private`: 472 to `t0-public`, 27 to `t1-public-nc`, 1 to
`t2-verbatim-nd` and 29 to `t3-verbatim-nd-nc`. No row moved in the restrictive direction, which is
why the run was allowed to write. 245 rows produced no evidence and were left exactly as they were.
Rows the manifest calls publishable went from 342 to 871.

These are objects, not source records. The resolver's 713 counts source records that leave
`t4-private` if their candidates are accepted; this counts manifest rows, and several records share
one set of bytes. Neither number stands in for the other.

Nothing is published by this. `store` still reads `local-cache` on every row, and
`npm run archive -- publish` is what puts bytes on a release tag and marks where they went.

## Takedown

**Contact: tim@rewire.it.** A rights holder who asks for an object to be removed gets it removed.
The steps below are the whole path, and each one is a command or a named function. Only step 4 needs
a credential: the gh token the publish path already uses, and the R2 secrets if the object ever
reached R2. Everything else runs offline. The path leaves `npm run archive -- verify` green.

Step 3 rewrites a manifest shard. Nothing locks that shard against a running fetch, which owns the
shard files while it runs, so run step 3 when no fetch is running. It is the same rule
`npm run archive -- publish --no-mark` exists for.

1. **Record the request.** Date, what was asked for, and who asked, in a dated file under
   `docs/reviews/`. That file's path is what step 3 writes as the requester, so the committed
   manifest names a review and never a person.

2. **Find the objects.** Each manifest row lists the source records its bytes answer for:

       grep -l '"<source-id>"' data/archive/objects/*.jsonl

   A source usually has two objects, the exact bytes and the text layer. Both go.

3. **Mark the manifest row.** `markRemoved()` in
   [scripts/archive/manifest.ts](../scripts/archive/manifest.ts) is the one write this path makes:

       npx tsx -e '
       import { markRemoved } from "./scripts/archive/manifest";
       markRemoved("<sha256>", {
         removed_reason: "<one line>",
         removed_requester: "docs/reviews/<the file from step 1>",
       }).then(console.log);
       '

   It sets `archive_tier` to `t5-no-store` and `visibility` to `restricted`, and it writes
   `removed_at` (UTC to the second, now, unless one is passed), `removed_reason` and
   `removed_requester`. It prints `true`, or `false` when the key is not in the manifest. The key,
   the byte count, the media type, the origin, `first_seen_at` and `source_ids` are not touched.
   `manifestRowSchema` refuses a row carrying `removed_at` without both other fields, and refuses
   one at any tier but `t5-no-store`.

4. **Delete the published copy.** A public object is a release asset on the tag
   `archive/objects-<first hex digit of the key>`, named `<sha256>.gz` by `archiveAssetName()`, at
   the URL `archiveAssetUrl()` builds:

       gh release delete-asset archive/objects-<first hex digit> <sha256>.gz \
         --repo rewire-bio/rewire-benchmark-data --yes

   If the object also reached Cloudflare R2, its key there is the same `<sha256>.gz`, and it is
   deleted from the bucket too.

5. **Delete the local copy.** `data/archive/cache/<first two hex digits>/<sha256>.gz`, which
   `objectPath()` builds, on every machine that holds one. The order of steps 3 to 5 does not
   matter to either publish path: both refuse a removed row, `publishObjects()` through
   `assertPublishable()` and `uploadObjects()` through `assertRestricted()`, so once step 3 is done
   neither sends the bytes anywhere.

   The fetch no longer brings them back. `planRun()` in `scripts/archive/fetch.ts` reads the
   manifest and asks `removedSources()` first, before the held check and before `--retry-failed` is
   consulted, so a source any row at `t5-no-store` answers for is never attempted again. That is
   every removed row, and also a row recording a decision to keep no copy, because re-fetching the
   bytes would undo either one. The run reports it on its own line, `skipped_removed`, rather than
   counting it as held: the archive holds nothing for that source and is not going to fetch it. `tests/archive-fetch.test.ts` proves it by marking
   a row removed, deleting the cached bytes and running the fetch again against the same host,
   which receives no second request.

6. **Leave the receipt and the record alone.** The fetch receipt is an observation log of what a
   transfer returned on a date, and the source record's URL, retrieval date and `artifact_sha256`
   are facts about the work rather than the work. Neither is edited.

7. **Verify.** `npm run archive -- verify` recomputes every cached object against the manifest and
   is the check the dated review records. It lists the key under `removed`, not under `missing`, and
   exits 0: a row at `t5-no-store` is expected to hold no bytes. If the bytes are still in the cache
   it prints a problem naming the key and its `removed_at` and exits 1, which means step 5 is
   unfinished.

What a reader of the manifest sees afterwards is the row, still in its shard, still sorted under its
own key, at `t5-no-store` and `restricted`, carrying `removed_at`, `removed_reason` and
`removed_requester`, with the key, the byte count, the media type, the origin, `first_seen_at` and
`source_ids` exactly as they were. `store` still names the backend the bytes were last recorded in,
because that is where they were; `removed_at` is what says they are no longer there. The bytes are
nowhere, and the row says they were held, when they were removed, why, and at whose request. No later reader finds a silent hole, and
`tests/archive-store.test.ts` holds that shape: a removed row is refused by the publish gate, and
the manifest's structural check and the hash check both pass with the row present and the bytes
gone.

One limit a requester has to be told about. Bytes already in this repository's git history cannot be
removed from history, which is the situation the seven sources in determination 3 are in. What this
path removes is the archive copy.

## Where this policy was ahead of the code

Five gaps between this document and the archive code. All five are closed, on 2026-11-17. Each one
was a sentence here that the code did not keep, so each is listed with what now keeps it.

- **`visibilityOf()` refused two tiers the determinations permit.** It used to make only `t0-public`
  and `t1-public-nc` public, which refused the publication determinations 1 and 2 settle for the 82
  sources at `t2-verbatim-nd` and `t3-verbatim-nd-nc`. It now makes four tiers public and restricts
  `t4-private` and `t5-no-store`, so the code matches the tier table above. The tiers stay six:
  `t2-verbatim-nd` and `t3-verbatim-nd-nc` record a different permission and a different premise
  from `t0-public` and `t1-public-nc`, and determination 1 falls if its premise falls.
- **The manifest row had no takedown fields.** `manifestRowSchema` now carries `removed_at`,
  `removed_reason` and `removed_requester`. They are optional, because a row that holds bytes
  carries none of them and because every row written before they existed carries none either. A row
  carrying `removed_at` must carry the other two, and must sit at `t5-no-store`. That last rule is
  what keeps a removed row unpublishable: `t5-no-store` is restricted, `visibility` follows the
  tier, and both publish paths select on visibility, so a removed row is never a candidate and the
  gate refuses it if it ever reaches one.
- **`uploadObjects()` did not filter on visibility.** It now selects the restricted rows and
  refuses the rest, which is the mirror image of the release path: determination 5 puts restricted
  bytes in R2, and a public object is published as a release asset by `publishObjects()`. It also
  refuses a row at `t5-no-store` outright, because that tier is restricted and a visibility filter
  on its own would have put a removed object's bytes back in the bucket. The sibling
  `publishObjects()` was already filtering and refusing anything the manifest does not call public,
  so the asymmetry the previous version of this section warned about is gone.
- **`verify` did not know about `t5-no-store`.** `verifyObjects()` in `scripts/archive/manifest.ts`
  is the whole check now, so a test can call it. A row at `t5-no-store` with no bytes is counted as
  `removed` and does not fail the command, and the check runs the other way instead: bytes still in
  the cache under such a row are a problem, because that is a takedown that stopped halfway.

- **The fetch did not know about a removed row.** `planRun()` decided a source was held from its
  latest receipt and the cache and never from the manifest, so a fetch after a takedown re-cached
  the bytes somebody had asked us to delete. It now reads the manifest, through `removedSources()`,
  and skips any source a removed row answers for before it looks at the receipt at all. The skip is
  reported as `skipped_removed` rather than folded into the held count, because the archive holds
  nothing for that source.

What is still ahead of the code, and is not a gap in this policy:

- **The R2 path has never run.** It needs the four secrets in determination 5, which do not exist
  in this environment, so `assertRestricted()` and the restricted selection above are written and
  unexercised against a live endpoint.
- **The manifest does not record where the published objects are.** See
  [What is public today](#what-is-public-today): the publish run used `--no-mark` because a fetch
  owned the shard files, so the release listing is the record until a later run marks the rows.

## The measured numbers

Every figure below comes from one command, and the published-object counts under
[What is public today](#what-is-public-today) come from the one printed there:

    npx tsx scripts/licence/counts.ts

Measured 2026-11-17 over `data/entities/sources.jsonl`:

| What | Count |
| --- | --- |
| source records | 1,483 |
| carrying a licence string | 408 |
| carrying none | 1,075 |
| distinct licence strings | 67 |
| sources at `t0-public` | 263 |
| sources at `t1-public-nc` | 22 |
| sources at `t2-verbatim-nd` | 2 |
| sources at `t3-verbatim-nd-nc` | 80 |
| sources at `t4-private` | 1,116 |
| sources at `t5-no-store` | 0 |
| publication resting on determinations 1 and 2 | 104 |
| sources in the licence triage queue | 1,082 |

Of the 408 licence strings, 317 are a bare identifier, 82 are prose naming one licence, 8 are
unresolved and 1 is conflicting.

The 1,116 at `t4-private` are not 1,116 sources whose licence forbids anything. 1,075 of them are
there because no licence has been determined. That is the number this work exists to bring down, and
it comes down by fetching, not by gating.

Issue 276 puts the set moving to publishable verbatim at about 97. The measurement over the map is
104: 22 at `t1-public-nc`, 2 at `t2-verbatim-nd` and 80 at `t3-verbatim-nd-nc`. The owner's figure
was approximate and the two are not in conflict.
