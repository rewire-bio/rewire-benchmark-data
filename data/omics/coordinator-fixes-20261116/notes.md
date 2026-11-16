# Cross-batch record fixes, 2026-11-16

Not an extraction. No new evidence, no new result, no new entity. Eighteen
`metadata-correction-*` claims that keep the previous value of eleven stored records changed in
this pass, each change justified by a dated review already in this repository.

The reasoning for every item, including the two things found along the way and the five
recommendations left open, is in `docs/reviews/2026-11-16-coordinator-fixes.md`. This file records
only what was run and how to reproduce it.

## Items and the review each comes from

| Item | Stored record(s) | Field(s) changed | From |
| --- | --- | --- | --- |
| 1 | `catalog-task-cell-perturbation` | `attributes.scope_note` | `docs/reviews/2026-11-15-perturbpfn.md`, ruling 7 |
| 2 | six `acquired-configuration-*` BEELINE entries | `links`, `description`, `attributes.provenance_note` | same review, closing note |
| 3 | `esmfold2-2026-runs-n-poses-method-openfold3-msa` | `links` | `docs/reviews/2026-11-16-poisk.md`, ruling 7 |
| 4 | `gfm-guides-20261014-gpnmsa-source-biorxiv-v2` | `attributes.hash_scope` | `docs/reviews/2026-11-16-gpn-msa-published.md`, ruling 5 |
| 5 | `reported-task-ed3dd3b83c4505` | `source_ids`, `attributes.benchmark_research.primary_sources` | `docs/reviews/2026-11-16-phylogpn.md`, ruling 3 |
| 6 | `vep-uc-20261014-model-gpn-star` | `source_ids` | `docs/reviews/2026-11-16-gpn-star.md`, ruling 9 |

## Artifacts retrieved for this pass

Two, both to check an identity or a hash rather than to read a value.

- `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7098173/fullTextXML`, the BEELINE paper, the
  artifact of `evidence-discovery-final-beeline`. 174,594 bytes, SHA-256
  `18986b6d4aae64c945146730f35acd5fd591366792a2b441879281b4f09e178e`. The source record pins
  `99b59a6941878779b34ab8eed9ea27c8d8967c24fb67b92fce418e7f512d3a11` and carries no `hash_scope`;
  Europe PMC regenerates this XML, so the pinned hash does not reproduce. Read for the Methods
  paragraphs on GRNBoost2 and PPCOR and their references 8 and 7.
- `https://www.biorxiv.org/content/10.1101/2023.10.10.561776v2.full.pdf`, the GPN-MSA preprint v2.
  HTTP 429 with the body `error code: 1015` on the first attempts, then 2,247,726 bytes and 37
  pages, PDF SHA-256 `688e3788e0555b0b1089f474c5cc7dfd22113fdaa168339c1b9f21490fa22646`. Its
  `pdftotext -layout` text layer is 137,403 bytes, SHA-256
  `c6e95eb807550bb97aa2b8991c013f28fe11742006582c25818fcf90cad30c79`, which is the hash item 4
  records.

## Reproducing this batch

`fixes/build-coordfix.py`, run from the repository root, both writes `batch.jsonl` and applies the
eleven record edits from the same constants, so the claim's `previous_value`, its `value` and the
stored record cannot drift apart. The edits assert the old value before writing and accept the new
one, so a second run is a no-op. `revert` undoes them if a store command has to be retried.

```sh
python3 -I data/omics/coordinator-fixes-20261116/fixes/build-coordfix.py build    # writes batch.jsonl, 18 claims
python3 -I data/omics/coordinator-fixes-20261116/fixes/build-coordfix.py plan     # prints the 11 edits, writes nothing
python3 -I data/omics/coordinator-fixes-20261116/fixes/build-coordfix.py apply    # applies them in place

# the text-layer check of item 4
curl -sL -o v2.pdf https://www.biorxiv.org/content/10.1101/2023.10.10.561776v2.full.pdf
pdftotext -layout v2.pdf layer.txt && shasum -a 256 layer.txt
```

## Store commands, in this order under one heavy lock

```sh
npm run records -- add data/omics/coordinator-fixes-20261116/batch.jsonl data/omics/coordinator-fixes-20261116
python3 -I data/omics/coordinator-fixes-20261116/fixes/build-coordfix.py apply
npm run records -- change docs/reviews/2026-11-16-coordinator-fixes.md data/omics/coordinator-fixes-20261116 <the 11 ids>
npm run records -- check
npm run check:task-links
```

`add` before the edits, because `addBatch` calls `loadRecords`, which fails if a stored record
differs from its provenance; the edits before `change`, because `change` hashes the record as it
then stands. Tests, typecheck and the data build were not run; the coordinator runs those.

## Not done

- Item 2's six entries stay `discovered`. The parent method is now known; the BEELINE run settings
  behind each label still are not.
- `reported-task-ed3dd3b83c4505` stays `needs_review`, and the other three legacy records behind
  `b2-phylogpn-2025` were not touched.
- Five of the six GPN-Star enrichments, and the GPN and GPN-MSA family edges, were not applied.
- No discrepancy check: this batch adds no result, so no discrepancy can name one of its records.
- No vocabulary concept was proposed and no file outside this folder and
  `docs/reviews/2026-11-16-coordinator-fixes.md` was edited, apart from the eleven stored records
  and their provenance lines.
