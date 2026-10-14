# Retrieval log

1. 2026-10-14T17:01:23Z: downloaded the Europe PMC JATS XML for PMC12809598 with curl. SHA-256 matches the source record.
2. Read the Abstract, Table 1, the Results section 'Performance of ESMFold for monomer structure prediction' and the Discussion from the parsed XML.
3. Ran extract/build_claim.py (command in research.md). It wrote batch.jsonl and claims.csv.
4. Added the batch with `npm run records -- add`; the claim stays needs_review.
