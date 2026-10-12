# Use-case summary: DNA pathogen identification, 2026-10-12

Claim: `use-case-summary-diagnostic-dna-pathogen-identification`

Draft: `docs/reviews/use-cases/dna-pathogen-summary-draft-2026-10-12.md` (moved from the BERTax batch folder, so that batch's `review.json` receipt still matches its files). Reviewer: a separate Claude review agent that did not write the draft or extract the BERTax and MetageNN batches. No human review is claimed.

The draft holds after the corrections below. The claim's `value`, `source_ids` and `source_locator` now carry the corrected text, its review block names this review, and the claim is re-pinned.

## Method

- Rebuilt the use-case artifact with `deriveUseCaseInputs`. Before the change the summary was withheld, because the five judgements added in PR #134 changed its pins; all 26 judgements on the use case were active.
- For every new number, read the stored result and checked that it is `source_checked`, that its evaluation is listed in `reviewed_evaluations` of an active `source_checked` judgement on this use case, and that the number equals the stored `printed_value`. Then checked the SI Table S2 numbers against the reviewed text layer `data/omics/use-case-coverage-dna-pathogen-20261012-bertax/artifacts/si-tables-s2-s5-pdftotext.txt`, and the MetageNN numbers and design against the pinned article XML (`PMC11022314.xml.gz`, SHA-256 `ac4b1375...4e12`, matches the source record).
- Checked that all eleven cited sources are `source_checked` with no `evidence_concerns`, that the text uses no withheld judgement, that it does not recommend, and that it has no em or en dash.
- Re-read the unchanged sentences against the 2026-10-11 review (`pathogen-use-cases-2026-10-11.md`). Their records and pins are unchanged apart from the added judgements, so they still hold.

## Numbers

| Text | Stored result (prefix `dna-pathogen-20261012-`) | Outcome |
| --- | --- | --- |
| 76.11, 75.59 | `bertax-result-{kraken2,minimap2}-closely-superkingdom-proportion-classified` | Match |
| 99.82, 99.95 | `bertax-result-{kraken2,minimap2}-closely-superkingdom-accuracy` | Match |
| 21.56, 19.88 | `bertax-result-{kraken2,minimap2}-distantly-superkingdom-proportion-classified` | Match |
| 90.71, 94.42 | `bertax-result-{kraken2,minimap2}-distantly-superkingdom-accuracy` | Match |
| every fragment (100) | `bertax-result-bertax-{closely,distantly}-superkingdom-proportion-classified` | Match |
| 94.78, 88.95 | `bertax-result-bertax-{closely,distantly}-superkingdom-accuracy` | Match |
| 93.26, 64.90, 53.06 | `metagenn-result-{metagenn,kraken2,megan-lr}-mocks-reads-classified` | Match |
| 85.49 (added) | `metagenn-result-mmseqs2-mocks-reads-classified` | Match |
| 30 mixtures (added) | protocol `metagenn-protocol-mocks` and article Experimental setup | Match |

The BERTax judgements are `bertax-closely` and `bertax-distantly`; the MetageNN judgement is `metagenn-mocks`. Each accuracy is over the fragments the tool assigned (the reviewed reading of SI Table S2 "acc.") and the text pairs it with the share assigned.

Origins and data: the text says both papers come from the developers of the trained classifiers, and that the data are simulated fragments or in silico mixtures of isolate reads, not clinical specimens. Both match the judgements' limitations.

## Corrections

1. MetageNN first author. The draft cited "Moreno et al. 2024". The pinned XML names Rafael Peres da Silva, Chayaporn Suphavilai and Niranjan Nagarajan. The text now says "Peres da Silva et al. 2024". The same wrong name was in the MetageNN batch's stored records, including the judgement names and the use case's gap text. It is corrected there too and recorded in the Author-attribution correction section of `dna-pathogen-ml-baseline-2026-10-12.md`. That fix changed the comparison titles of the MetageNN evaluations, which this summary pins, so the summary was re-pinned after it. No value changed.
2. MetageNN shares are means. The paper reports the average percentage across the 30 pseudo-mocks. The text now says "on average across 30 mixtures".
3. MMseqs2 added to the MetageNN sentence. MMseqs2, a reference-based tool that is not in this use case's baseline, assigned 85.49% of reads on the same mixtures. Leaving it out made the gap between the trained classifier and reference-based tools look larger than the paper shows. It is a reviewed result on the active `metagenn-mocks` judgement.
4. BERTax accuracy denominator. "with 99.82% and 99.95% accuracy" became "with 99.82% and 99.95% accuracy on the fragments they assigned", so the reader does not take it as accuracy over all fragments. "in the two settings" was added to BERTax's pair of accuracies.
5. `source_locator`: added the BERTax article locator (it supports the 1,500-nt fragments and the two test sets) and the MetageNN pseudo-mock setup paragraph (30 mixtures of out-of-database species).

Not changed: the draft's three added sources and its choice not to cite `dna-pathogen-20261012-bertax-source-pdf` (no Table 1 value is used). Phylum-rank results, DeepMicrobes, sourmash, MetaMaps and the BERTax MMseqs2 rows are not described; that leaves the BERTax pattern as stated (MMseqs2 there assigned 87.45% and 52.78% of fragments, more than Kraken2 and minimap2 and fewer than BERTax, with 99.63% and 90.73% accuracy).

## State after the change

Checked with `deriveUseCaseInputs` against the store before this review: the summary publishes. The only other differences come from the author-name fix: the names and evidence hashes of the two MetageNN mappings, and the use case's two gap texts. Every mapping keeps its state and evaluations, and every other use case is identical.

## Remaining gaps

- The claim's `description` still says "Draft until reviewed."; it is unchanged, as in other summaries.
- No human scientific review.
