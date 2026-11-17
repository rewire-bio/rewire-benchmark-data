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

Seven rulings, all dated 2026-11-17, all from
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
not after. The steps are in [Takedown](#takedown) below.

### 5. Restricted bytes live in Cloudflare R2. Dated 2026-11-17.

Four repository secrets are needed before CI can use it: account id, access key id, secret access
key, bucket name. None is present in this environment. Nothing in the fetch, verify, status or
import path needs one, and a fork pull request runs all of them without a credential.

### 6. No human review anywhere. Dated 2026-11-17.

Everything is automated. A receipt states that a claim is machine extracted, span verified and
unreviewed. The reviewer field carries a tool identity, never a person. This closed the review step
in [collection.md](collection.md) as it was written, and that document has been changed with it.

### 7. Scope is the documented use cases. Dated 2026-11-17.

The boundary of "biological foundation models" for this graph is the use-case set in
[docs/reviews/use-cases/](reviews/use-cases/) and rewire.it #365, not a modality list. A model family
outside those use cases is out of scope until a use case brings it in.

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
| `t0-public` | publish | publish | CC0, CC BY, CC BY-SA, MIT, Apache-2.0, BSD, ODbL | 263 |
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

Licence resolution runs inside the fetch, not as a separate chore. 1,082 determinations will never be
cleared on their own, and a resolver needs a capture anyway. A resolution writes a candidate to the
manifest as `observed_licence`; it never writes a record. Promoting it into `attributes.licence` is a
record change like any other and happens the next time someone touches that source.

## Takedown

**Contact: tim@rewire.it.** A rights holder who asks for an object to be removed gets it removed.
The steps below are the whole path. They work against the code as it stands today and need no
credential except the R2 one.

1. **Record the request.** Date, what was asked for, and who asked. It goes in the dated review that
   carries out the removal, under `docs/reviews/`.
2. **Find the objects.** Each manifest row lists the source records its bytes answer for:
   `grep -l '"<source-id>"' data/archive/objects/*.jsonl`. A source usually has two objects, the
   exact bytes and the text layer. Both go.
3. **Delete the local copy first.** `data/archive/cache/<first two hex digits>/<sha256>.gz`, on every
   machine that holds one. This has to come before step 4, because `npm run archive -- upload`
   uploads every cached object the manifest lists and would put it straight back.
4. **Delete the published copy.** The R2 key is the manifest key with `.gz` appended, which is what
   `archiveAssetName()` produces. Upload is append only and never replaces an object, so a key that
   is gone and uncached stays gone. If the object was also published as a GitHub release asset, it
   is on the tag `archive/objects-<first hex digit of the key>` under the same name
   (`archiveAssetUrl()`), and that asset is deleted too.
5. **Mark the manifest row.** Set `archive_tier` to `t5-no-store` and `visibility` to `restricted`. Keep the
   row. The key, the byte count, `first_seen_at` and `source_ids` stay exactly as they were, so the
   removal is a recorded fact and no later reader finds a silent hole.
6. **Leave the receipt and the record alone.** The fetch receipt is an observation log of what a
   transfer returned on a date, and the source record's URL, retrieval date and `artifact_sha256`
   are facts about the work rather than the work. Neither is edited.
7. **Verify.** `npm run archive -- verify` recomputes every cached object against the manifest. It
   lists the removed key under `missing`, because the manifest still has the row and the cache no
   longer has the bytes, and it exits non-zero on that. For a row at `t5-no-store` that is the
   correct state, not a fault. Record it in the dated review so the next operator does not chase
   it, and see the next section.

Two limits a requester has to be told about. Bytes already in this repository's git history cannot
be removed from history, which is the situation the seven sources in determination 3 are in; what
step 5 removes is the archive copy. And a manifest row records a removal only as `t5-no-store`
today, because `manifestRowSchema` is strict and has no field for when, why or at whose request. See
the next section.

## Where this policy is ahead of the code

Three gaps between this document and the archive code as it stands. They belong to
`shared/archive/schema.ts` and `scripts/archive/`, and they are named here so nobody has to
rediscover them.

The fourth is closed. `visibilityOf()` used to make only `t0-public` and `t1-public-nc` public,
which refused the publication determinations 1 and 2 settle for the 82 sources at `t2-verbatim-nd`
and `t3-verbatim-nd-nc`. It now makes four tiers public and restricts `t4-private` and
`t5-no-store`, so the code matches the tier table above. The tiers stay six: `t2-verbatim-nd` and
`t3-verbatim-nd-nc` record a different permission and a different premise from `t0-public` and
`t1-public-nc`, and determination 1 falls if its premise falls.

- **The manifest row has no takedown fields.** Step 5 above can set `t5-no-store` and nothing else.
  `removed_at`, a reason and a requester are needed before the first public upload, which is what
  determination 4 asks for.
- **`uploadObjects()` does not filter on visibility.** It puts every cached object the manifest
  lists into the bucket. That is safe while the only backend is a private R2 bucket. It stops being
  safe the moment a public backend exists.
- **`verify` does not know about `t5-no-store`.** A row whose bytes were removed by a takedown is
  reported as `missing` and the command exits 1, so every takedown leaves a standing failure. The
  fix is one condition: a `t5-no-store` row is expected to have no bytes.

## The measured numbers

Every figure in this document comes from one command:

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
