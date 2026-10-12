# Draft replacement summary: DNA pathogen identification

Reviewed and corrected in `dna-pathogen-summary-2026-10-12.md`; this file is the draft as submitted, moved here from `data/omics/use-case-coverage-dna-pathogen-20261012-bertax/`.

Claim: `use-case-summary-diagnostic-dna-pathogen-identification` (currently withheld because PR #134 added five reviewed judgements). Draft only; the claim is not edited. Needs independent review and repin (`npm run use-cases:repin -- <review.md> use-case-summary-diagnostic-dna-pathogen-identification`).

## Changes from the current text

1. First sentence: "mock communities or constructed metagenomes" becomes "mock communities, constructed metagenomes or simulated sequences", because the BERTax comparisons use simulated genome fragments, which are neither.
2. Three new sentences after the Hall and Coin 2024 sentence and before the closing sentence: one framing sentence, one on BERTax, one on MetageNN. The lead asked for one or two; the framing sentence is kept separate because folding it in made the BERTax sentence hard to read. A reviewer can merge it.
3. Everything else is unchanged. The closing sentence ("Each study used its own reference database and reporting rules, and none of these results is clinical validation") still holds for the new sources.

## Proposed text

Most workflow comparisons in the reviewed evidence use mock communities, constructed metagenomes or simulated sequences. Two compare workflows on patient specimens, and in both the reference standard draws partly on sequencing: in Hu et al. 2026 only the culture comparison is independent of the sequencing results, and in Huang et al. 2026 the reference was built mainly from BALF mNGS and the conventional tests that are themselves scored. Both are author-reported and have co-authors from sequencing companies (Genskey Medical Technology for Hu; Geneplus-Beijing, which supplies the targeted assay's probes, for Huang). For the Karius plasma cell-free DNA assay, the developers report 93.7% (59 of 63) agreement with initial blood culture in a sepsis-alert cohort, and blood culture does not detect every infection. A prospective study in children and young adults with high-risk leukaemia, with Karius taking part in sample processing and analysis, found every blood-culture organism in 81.3% (65 of 80) of evaluable bloodstream infection episodes on the day of or after onset and in 51.9% (42 of 81) during the three days before; 82.7% (134 of 162) of control samples from patients without fever or infection had no bacterium or yeast detected. In 62 bronchoalveolar lavage specimens (Hu et al. 2026), a short-read MGI workflow and a host-depleted nanopore workflow both had 95.2% positive agreement with culture but 44.6% and 46.4% negative agreement, because they found organisms culture did not; against a composite reference that adds organisms found by both workflows, positive agreement was 93.3% and 90.7%. In 122 intensive-care patients with pneumonia-associated sepsis (Huang et al. 2026), a targeted probe-capture assay on plasma had 63.46% sensitivity against the reference diagnosis, against 35.58% for untargeted blood mNGS, 49.04% for conventional tests and 9.62% for blood culture, with specificity of 44.44% and 61.11% for the two blood sequencing assays. In mock communities (Portik et al. 2022), Kraken2 and Bracken called 44 to 204 absent species at a 0.001% read threshold (precision 0.05 to 0.21), while long-read MEGAN-LR and BugSeq-V2 called 0 to 2; the first author is a PacBio employee. In seven pathogen-free libraries scored against one shared virus database by the EsViritu developers (preprint), the median number of false virus species was 0 for EsViritu, Centrifuger and Sylph, 6 for Kraken2 and 18 for Metabuli. For M. tuberculosis reads in constructed metagenomes (Hall and Coin 2024), kraken with its standard database classified 0.07 to 0.74 of the M. tuberculosis reads as M. tuberculosis, against 0.97 to 0.995 with a Mycobacterium database. Two papers by the developers of trained classifiers compare them with the baseline tools, on simulated or isolate-derived data rather than clinical specimens. On simulated 1,500-nt genome fragments (Mock et al. 2022, BERTax), Kraken2 and minimap2 assigned a superkingdom to 76.11% and 75.59% of fragments with 99.82% and 99.95% accuracy when relatives were in the reference, and to 21.56% and 19.88% with 90.71% and 94.42% accuracy when each fragment's genus was absent from it; BERTax assigned every fragment, with 94.78% and 88.95% accuracy. On in silico mixtures of nanopore isolate reads from species absent from the reference (Moreno et al. 2024, MetageNN), MetageNN assigned a genus to 93.26% of reads, Kraken2 to 64.90% and MEGAN-LR (on minimap2 alignments) to 53.06%; these shares count reads assigned, not reads assigned correctly. Each study used its own reference database and reporting rules, and none of these results is clinical validation.

## source_ids

Current eight, unchanged:

- `amp-20261007-dna-pathogens-source`
- `dna-pathogen-20261009-source-hall2024`
- `dna-pathogen-20261009-source-portik2022`
- `dna-pathogen-20261011-hu2026-source`
- `dna-pathogen-20261011-huang2026-source`
- `dna-pathogen-20261011-wolf2026-source`
- `rna-pathogen-20261011-tisza2026-source`
- `rna-pathogen-20261011-tisza2026-source-supp`

Added:

- `dna-pathogen-20261012-bertax-source` (article text: 1,500-nt fragments, closely and distantly related test sets)
- `dna-pathogen-20261012-bertax-source-si` (SI Table S2: every BERTax number)
- `dna-pathogen-20261012-metagenn-source` (Results text: every MetageNN number)

`dna-pathogen-20261012-bertax-source-pdf` is deliberately not added: no Table 1 (macro AveP) value is used, and its pinned hash was not re-verified at review (see `docs/reviews/use-cases/dna-pathogen-ml-baseline-2026-10-12.md`).

Proposed `source_locator` suffix: `; dna-pathogen-20261012-bertax-source-si: SI Table S2 (superkingdom acc. and prop.); dna-pathogen-20261012-metagenn-source: Results 'Read classification results' paragraph 1`

## Results behind each new number

All are `source_checked`, on reviewed evaluations of active judgements (`use-case-mapping-dna-pathogen-20261012-bertax-closely`, `-bertax-distantly`, `-metagenn-mocks`). The prefix `dna-pathogen-20261012-` is omitted below.

| Text | Value | Result ID | Judgement |
| --- | --- | --- | --- |
| Kraken2 assigned, relatives in reference | 76.11% | `bertax-result-kraken2-closely-superkingdom-proportion-classified` | bertax-closely |
| minimap2 assigned, relatives in reference | 75.59% | `bertax-result-minimap2-closely-superkingdom-proportion-classified` | bertax-closely |
| Kraken2 accuracy, relatives in reference | 99.82% | `bertax-result-kraken2-closely-superkingdom-accuracy` | bertax-closely |
| minimap2 accuracy, relatives in reference | 99.95% | `bertax-result-minimap2-closely-superkingdom-accuracy` | bertax-closely |
| Kraken2 assigned, genus absent | 21.56% | `bertax-result-kraken2-distantly-superkingdom-proportion-classified` | bertax-distantly |
| minimap2 assigned, genus absent | 19.88% | `bertax-result-minimap2-distantly-superkingdom-proportion-classified` | bertax-distantly |
| Kraken2 accuracy, genus absent | 90.71% | `bertax-result-kraken2-distantly-superkingdom-accuracy` | bertax-distantly |
| minimap2 accuracy, genus absent | 94.42% | `bertax-result-minimap2-distantly-superkingdom-accuracy` | bertax-distantly |
| BERTax assigned every fragment | 100 | `bertax-result-bertax-closely-superkingdom-proportion-classified`, `bertax-result-bertax-distantly-superkingdom-proportion-classified` | both |
| BERTax accuracy, relatives in reference | 94.78% | `bertax-result-bertax-closely-superkingdom-accuracy` | bertax-closely |
| BERTax accuracy, genus absent | 88.95% | `bertax-result-bertax-distantly-superkingdom-accuracy` | bertax-distantly |
| MetageNN reads assigned a genus | 93.26% | `metagenn-result-metagenn-mocks-reads-classified` | metagenn-mocks |
| Kraken2 reads assigned a genus | 64.90% | `metagenn-result-kraken2-mocks-reads-classified` | metagenn-mocks |
| MEGAN-LR reads assigned a genus | 53.06% | `metagenn-result-megan-lr-mocks-reads-classified` | metagenn-mocks |

"1,500-nt" is a dataset description, not a result: it is in the BERTax judgements' limitations and the article's dataset description.

Numbers in the unchanged text keep the results traced at the 2026-10-11 review (`docs/reviews/use-cases/pathogen-use-cases-2026-10-11.md`).

## Notes for the reviewer

- Accuracy in SI Table S2 is over the fragments each tool classified, which is why each accuracy is paired with its share assigned. Macro AveP (Table 1) is not used, because it scores unclassified fragments as random guesses and so mixes coverage with accuracy.
- The phylum-rank and genus-rank (final dataset) results are not cited, to keep the addition short. At phylum, genus absent, BERTax accuracy was 60.10% on all fragments against 68.26% (Kraken2, 21.08% assigned) and 77.12% (minimap2, 19.88% assigned); including these would not change the pattern described.
- MEGAN-LR is not compared in BERTax; minimap2 in MetageNN only supplies MEGAN-LR's alignments. The text says "the baseline tools", not all three in each paper.
- The MetageNN isolates judgement is not cited: it has no MetageNN evaluation (excluded at review), so it compares Kraken2 with MMseqs2, not a trained classifier with the baseline.
- MMseqs2, DeepMicrobes, sourmash and MetaMaps results are on these protocols but are not named, to keep the addition to the ML-versus-baseline question.
- The developer framing is in the text ("Two papers by the developers of trained classifiers"); both papers ran every tool themselves and print no uncertainty.
