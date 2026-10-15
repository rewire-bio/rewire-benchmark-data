# Research notes

Batch for rewire-benchmark-data issue #129: record that Mahtha et al. 2026 print one dimer accuracy (77%) for both AlphaFold2 and AlphaFold3 in the Abstract, while the body gives 76.8% and 75%.

## Decisions

- Subject: the existing source record `lit-structure-20261011-afesmfold-source-mahtha2026`. `shared/omics/relations.ts` allows `subject` from a claim to any record kind, and an existing claim of the same type targets a source (`dna-pathogen-20261012-bertax-claim-final-phylum-discrepancy`).
- Field: `printed_value_conflict`, the name existing claims use for a value printed differently in two places of one source (same example). `abstract_table_difference` was suggested in the task; `printed_value_conflict` was chosen to follow the store's existing naming. The attribute registry places no restriction on the `field` text.
- What the source prints: the Abstract says "AlphaFold2 and AlphaFold3 correctly predicted ... 77% of dimeric proteins". Table 2 prints the class counts (AlphaFold2 361, 297, 105; AlphaFold3 346, 306, 93); the sums 763 and 745 and the percentages 76.8% and 75% are printed in the Results and Discussion, not in Table 2. The task brief's "Table 2 gives 763/994 (76.8%) and 745/994 (74.9%)" is therefore partly computed: 74.9% is not printed anywhere (the paper prints 75%). The claim says which numbers are printed where and marks 74.9% as computed.
- No result records were added: the class counts are already in the store from the afesmfold batch (`lit-structure-20261011-afesmfold-eval-2-alphafold2-no`, `...-eval-2-alphafold3-no`).

## Should this also be an evidence concern?

`docs/collection.md` ("Corrections and concerns") says a problem that should block comparison, including when the abstract and body disagree, goes in the source record's `attributes.evidence_concerns`. The source already carries five concerns about Tables 1 and 2. This difference is in the Abstract's summary, not in a table cell, and the stored results come from Table 2, whose AlphaFold3 counts agree with the Results text (745 accurate, 249 incorrect). So it probably does not need to block comparison of the stored results. The store owner should still consider adding it as a sixth concern, since the collection guide names abstract and body disagreement as a case for one. A claim was written because that is what was requested, and this batch cannot edit the existing source record.

## Record counts

- claim: 1 (status `needs_review`)

Reused IDs: `lit-structure-20261011-afesmfold-source-mahtha2026`.

## Extraction note for the reviewer

Passages read: Abstract (sentence 3), Table 2 (all 12 rows; the six accurate-class cells for AlphaFold2 and AlphaFold3 in column 'No.' are used), Results section 'Performance of AlphaFold for dimeric structure prediction' paragraphs 1 and 3, Discussion paragraph 3. Method: re-retrieval of the pinned XML with a hash match, then transcription from the parsed text.

Gaps: none for this claim. Not checked: whether the Abstract's monomer figure (88% for both tools) has the same issue; the Discussion gives a range of 87% to 88%.

Needs reviewer judgement: field name (`printed_value_conflict` versus `abstract_table_difference`), and whether to also add an `evidence_concerns` entry on the source.
