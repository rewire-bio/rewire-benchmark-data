# Research notes

Batch for rewire-benchmark-data issue #163: record that Mahtha et al. 2026 (NAR Genomics and Bioinformatics, doi:10.1093/nargab/lqag002) print ESMFold monomer accuracy as 76% in the Abstract and 77% in the Discussion. The reviewed dimer claim `gfm-guides-20261014-mahtha2026-claim-dimer-accuracy-abstract-vs-table2` noted this difference and left it unrecorded.

## Decisions

- Same shape as the dimer claim: subject is the existing source record `lit-structure-20261011-afesmfold-source-mahtha2026`, field `printed_value_conflict`.
- What the source prints: Abstract sentence 4, "ESMFold accurately predicted 76% of the monomeric proteins"; Discussion paragraph 1, sentence 6, "while ESMFold achieved 77% accuracy"; Results 'Performance of ESMFold for monomer structure prediction' paragraph 1, "832 (50%) were classified as accurate ... while 430 (26%) showed domain-level movements"; Table 1, ESMFold 'Accurate prediction' 832 and 'Domain movement' 430 of 1,666.
- The sum 1,262 of 1,666 (75.75%) is computed here and marked as computed in the claim. That the paper's "accuracy" counts accurate plus domain-movement predictions is an inference from the AlphaFold rows (1,069 + 386 and 1,076 + 388 of 1,666 give 87.3% and 87.9%, the "87%–88%" of the Discussion); the claim's review note says so.
- No result records: the Table 1 class counts are already in the store from the afesmfold batch.
- Status `needs_review`. No review.json yet.

## Record counts

- claim: 1

## Extraction note for the reviewer

Method: the Europe PMC JATS XML was re-downloaded on 2026-10-14T17:01:23Z; its SHA-256 (`aae321d0...98b8`) matches the source record. `extract/build_claim.py` asserts the hash, the Abstract, Discussion and Results sentences, and the two Table 1 cells, then writes batch.jsonl and claims.csv:

```sh
curl -sS -o <scratch>/mahtha.xml https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12809598/fullTextXML
python3 -I data/omics/gfm-guides-20261014-mahtha2026-monomer-claim/extract/build_claim.py <scratch>/mahtha.xml data/omics/gfm-guides-20261014-mahtha2026-monomer-claim
```

Needs reviewer judgement: as for the dimer claim, whether this difference should also become an `evidence_concerns` entry on the source. The stored results are Table 1 counts, which agree with the Results text, so it probably need not block comparison.
