# Review: BEELINE protocol names (rewire-benchmark-data#92), 2026-10-10

Reviewer: a separate Claude review agent that did not make the fix. No human review is claimed.

## Verdict

The fix is correct and complete after one addition. All 54 changed protocols carry exactly the values of their old JSON objects, with nothing lost or added. All 196 original claims have the exact previous values. "log/gof" is printed as is in the archived source CSV. No pin, judgement or other record depends on the old names.

One problem was found and fixed in place. Each protocol's `description` still held the same raw sentence: `Input conditions: {...}.` on the 44 Figure 5 protocols, and `Input conditions: {}.` on the 10 others. It was not changed, and it shows as page text. I extended `build.py` to change it the same way as the caveats, which adds 54 claims (250 in total). All 250 claims are now `source_checked`, with a review.

## Checks

1. **Diff.** Against `origin/main` (commit `9997861`, the same as HEAD), exactly 54 of 599 lines of `data/entities/protocols.jsonl` change. No other store file changes. Within those records, only these fields differ:
   - `name`;
   - `description` (added in review);
   - `attributes.comparison_panels[].title` (71);
   - `attributes.comparison_panels[].caveats[]` (71).

   Every other top-level field, every other attribute and every other panel field is unchanged.
2. **Values.** For each protocol I parsed the old JSON object from the old name with my own script (not `build.py`) and rebuilt each new text.
   - **Names.** For the 44 Figure 5 protocols, `<prefix> · <reference_network> network, <gene_selection> genes`. For the 10 Figure 2 and 4 protocols, the prefix without ` · {}`.
   - **Panel titles.** `<new name>: <metric>`, with the metric suffix unchanged.
   - **Caveats and descriptions.** The object replaced by the readable text, or the empty-object sentence removed.

   All 250 new texts match. Each panel title and caveat in the old record carried the same object as its old name. Every new name is unique.
3. **Evaluations.** All 264 evaluations of the 44 Figure 5 protocols carry `attributes.conditions.reference_network` and `gene_selection` equal to the old object. The 120 evaluations of the 10 empty-object protocols keep their own conditions; nothing was taken from them.
4. **Claims.**
   - Each claim's `previous_value` equals the `origin/main` text exactly, and its `value` equals the new store text.
   - Field paths and subjects match, there is one claim per changed field and no duplicate.
   - The 196 original claims are byte-identical to the collector's apart from the review fields set now.
   - The full batch of 250 adds cleanly with `addBatch` to a scratch copy of the store at `origin/main`. SHACL was not run.
5. **"log/gof".** The archived `data/omics/acquisition/2026-09-19/cells-networks/sources/beeline-14_ESM.csv.gz` decompresses to SHA-256 `1f6a38649aa1fc1d90522e3d09f85f7e5714cc80c585ef679ed7603d7a1c7b70`, which equals `artifact_sha256` of `acquired-source-31344fb7e5e8ae6b9666`.
   - Read with Python's csv module, row 19 column 1 is `log/gof` (mESC). The five reference networks in column 1 are Cell-type specific ChIP-Seq, Non-specific ChIP-Seq, STRING and log/gof, with blanks for continued blocks.
   - The new names keep it as printed. That the paper means lof/gof is plausible but was not checked, so no change is made.
6. **Dependencies.** Across `data/entities` and `data/evidence`:
   - No record other than the 54 protocols contains an old name.
   - No use case links these protocols, and no `assessed_by` judgement or pin names them.
   - The only records that mention their IDs are the 54 `links:part_of:discovery-benchmark-beeline` membership claims, which use the ID only and carry no pins.

## For the integrator

- Run `npm run records -- change data/omics/qa-beeline-names-20261010/review.md data/omics/qa-beeline-names-20261010 <the 54 protocol IDs>`, then `npm run records -- add data/omics/qa-beeline-names-20261010/batch.jsonl data/omics/qa-beeline-names-20261010`.
- Until then the store does not match provenance, so `npm test` and `records -- check` are expected to fail on these 54 records.
- `python3 -I data/omics/qa-beeline-names-20261010/build.py --check` passes. Its batch comparison now ignores claim status and review, which the reviewer sets.
