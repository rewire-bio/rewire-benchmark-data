# Review: Feng et al. 2025 DNA foundation model tables, 2026-10-13

Independent review of batch `data/omics/feng-dna-fm-20261013/` (rewire-benchmark-data#19), which extends the stored Feng et al. 2025 records (prefix `amp-feng-20261007-`). Reviewer: an independent Claude (Opus 5.5) review agent; the batch was extracted by the Claude agent `feng-19`. No human review is claimed. Source transcription is not reproduction, and nothing was executed.

Feng H. et al. Benchmarking DNA foundation models for genomic and genetic tasks. Nature Communications 16, 10780 (2025). DOI 10.1038/s41467-025-65823-8.

## Outcome

Approved with corrections. No printed or numeric value was wrong. Four descriptive errors were fixed by the extractor in `extract/extract_feng.py` before sign-off (listed under Conflicts). The batch receipt is `data/omics/feng-dna-fm-20261013/review.json`; the sign-off script is `review/signoff.py` in that folder.

Counts checked: 126 results, 22 Table 1 datasets against Supplementary Data 6, 26 baseline-CNN claims against Supplementary Data 1 and 2, 4 descriptive claims, 2 relevance judgements, 118 configurations, 118 evaluations, 25 protocols, 3 new sources. Mismatches in values: 0.

## Sources and hashes

All artifacts were re-downloaded on 2026-10-13 and matched.

| Source record | Artifact | SHA-256 |
| --- | --- | --- |
| `evidence-expansion-dna-foundation-models-2025-5d8ca9bc` (existing) | Europe PMC fullTextXML, PMC12663285 | `5d8ca9bcf88cc1b38ad667906a2e4699b1aefa6d31c6f49259784930353f3202` |
| `feng-dna-fm-20261013-source-supplementary-data` | MOESM3_ESM.xlsm (Supplementary Data 1-6) | `4804c801e0e054eca5f776617c18a6a0cb31d6ce3d2a7a52f70e4dda5b3abd7a` |
| `feng-dna-fm-20261013-source-supplementary-information` | MOESM1_ESM.pdf (11 pages) | `373f59b825c9e2bc51a0f122a9e2653f427c492727fbf73768cc9af02d094a15` |
| `feng-dna-fm-20261013-source-gtex-hyena-script` | job_scripts/gtex_hyena.py at 3f4c81ce066f3c47422a83466b085aac1a6be902 | `a9ab37677da4340d3d5ea3b7516d71bf4e60d7cb2eab39eb954584d738ed2788` |
| `evidence-reported-dna-foundation-models-2025-readme-md` (existing) | README.md at the same commit | `e678c69a91fd0b709864d2c0b83f33e273b82e389dd07b6f380b76236631fac2` |

The archived `artifacts/MOESM3_ESM.xlsm.gz` (SHA-256 `7eab15accb189db3d4630476328606a25490314da45ef84a1229e46943810569`) decompresses to the workbook bytes.

## Method

- Tables 1 and 4 were parsed from the XML with a separate ElementTree parser (`review/signoff.py`, which does not import the extraction script). Every result's printed value, numeric value, metric, unit, direction, locator, bold marking, configuration name and protocol was compared. XML row labels use a thin space ("300 bps"); locators use a plain space.
- The workbook was read as a zip of sheet XML, with no macros run. Supplementary Data 1, 2 and 6 were compared with the CNN claims and dataset records.
- The Supplementary Information PDF was read in full with `pdftotext -layout`; pages 9 to 11 (Supplementary Table 8, Supplementary Figures 1 and 2) were also viewed rendered.
- Methods, Results, Data availability and the author script were read against every protocol, configuration, dataset and evaluation statement.
- Duplicates were checked against all of `data/entities/*.jsonl` and `data/evidence/*.jsonl`.
- `extract/extract_feng.py` was rerun on the pinned artifacts; its output is byte-identical to the batch that was signed off. The signed-off batch passed the store's record, vocabulary and attribute validators in a dry run.

## Table 1: human sequence classification, AUC

Bold as printed (higher than at least two other AUCs, p < 0.01, one-sided DeLong). Acceptor and Donor are already stored (`amp-feng-20261007-`) and are not repeated. Metric `auroc`, unit `unitless`, direction higher.

| Row | DNABERT-2 | NT-v2 | HyenaDNA | Caduceus-Ph | GROVER | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| DNase I Hypersensitive | 0.8666 | 0.8524 | 0.8295 | 0.8799 | 0.857 | match (5 of 5) |
| Human TFBS 1 | 0.8382 | 0.8315 | 0.8301 | **0.8796** | **0.8618** | match (5 of 5) |
| Human TFBS 2 | 0.821 | 0.809 | 0.8205 | **0.8687** | **0.8495** | match (5 of 5) |
| Human TFBS 3 | 0.7896 | 0.7974 | 0.7875 | **0.8249** | **0.8158** | match (5 of 5) |
| Human TFBS 4 | 0.726 | 0.7103 | 0.7149 | **0.7725** | **0.763** | match (5 of 5) |
| Human TFBS 5 | 0.9204 | 0.9149 | 0.9159 | **0.9294** | **0.931** | match (5 of 5) |
| Promoter GM12878 | 0.9856 | 0.9835 | 0.976 | **0.9865** | 0.9839 | match (5 of 5) |
| Promoter HUVEC | **0.9903** | 0.987 | 0.9817 | **0.9896** | 0.9885 | match (5 of 5) |
| Promoter Hela-S3 | **0.9886** | 0.9838 | 0.981 | **0.9871** | 0.9857 | match (5 of 5) |
| Promoter NHEK | **0.9501** | 0.9323 | 0.9271 | **0.9567** | **0.9507** | match (5 of 5) |
| Coding | **0.9438** | 0.9289 | 0.9406 | **0.9735** | **0.9594** | match (5 of 5) |
| Enhancer | **0.8717** | **0.8674** | 0.8339 | 0.8384 | 0.8554 | match (5 of 5) |
| Enhancer Cohn | **0.8223** | 0.7894 | 0.7754 | **0.821** | **0.8161** | match (5 of 5) |
| Enhancer Ensembl | 0.9369 | **0.9389** | 0.9356 | **0.9431** | 0.9382 | match (5 of 5) |
| Open chromatin region | **0.7253** | 0.7183 | 0.7191 | **0.765** | **0.7455** | match (5 of 5) |
| Promoter All 300 bps | 0.9426 | **0.9445** | 0.9394 | **0.9519** | 0.9402 | match (5 of 5) |
| Promoter All 70 bps | 0.8311 | **0.8527** | 0.832 | **0.8748** | **0.8506** | match (5 of 5) |
| Promoter NonTATA 251 bps | 0.9297 | 0.8905 | 0.928 | **0.9426** | **0.9395** | match (5 of 5) |
| Promoter NonTATA 300 bps | **0.9765** | **0.9758** | 0.9662 | **0.9834** | 0.9728 | match (5 of 5) |
| Promoter NonTATA 70 bps | 0.8531 | **0.8729** | 0.8516 | **0.8961** | **0.8704** | match (5 of 5) |
| Promoter TATA 300 bps | 0.7646 | 0.7791 | **0.8077** | 0.76 | 0.78 | match (5 of 5) |
| Promoter TATA 70 bps | 0.7781 | 0.7947 | 0.7827 | **0.8103** | 0.796 | match (5 of 5) |

Table 1 cells checked: 110.

## Table 4: GTEx whole-blood expression prediction

Pearson correlation: unit `unitless`, direction higher. MSE: unit `unit-unreported`, direction lower. Rows marked * use the 768-gene long-input protocol. No bold in Table 4.

| Model | Input | Average correlation | Average MSE | Protocol | Outcome |
| --- | --- | --- | --- | --- | --- |
| DNABERT-2 | 6000 bp | 0.121 | 0.236 | 6kb | match |
| NT-v2 | 6000 bp | 0.122 | 0.236 | 6kb | match |
| HyenaDNA | 6000 bp | 0.122 | 0.235 | 6kb | match |
| Caduceus-Ph | 6000 bp | 0.123 | 0.234 | 6kb | match |
| GROVER | 2048 bp | 0.114 | 0.233 | 6kb | match |
| HyenaDNA-450K* | 196K bp | 0.137 | 0.226 | long-768 | match |
| Caduceus-Ph Long Sequence Input* | 131K bp | 0.127 | 0.227 | long-768 | match |
| Enformer* | 196K bp | 0.129 | 0.227 | long-768 | match |

## Baseline CNN claims: Supplementary Data 1 and 2

| Claim | Workbook row | CNN better than (Data 1) | Better than CNN (Data 2) | Outcome |
| --- | --- | --- | --- | --- |
| `claim-cnn-acceptor` | Acceptors | Caduceus-Ph, GROVER, HyenaDNA, NT-v2 | None | match |
| `claim-cnn-coding` | Coding | DNABERT-2, HyenaDNA, NT-v2 | Caduceus-Ph, GROVER | match |
| `claim-cnn-dnase-i-hypersensitive` | DNase I Hypersensitive | None | Caduceus-Ph, DNABERT-2 | match |
| `claim-cnn-donor` | Donors | Caduceus-Ph, DNABERT-2, GROVER, HyenaDNA, NT-v2 | None | match |
| `claim-cnn-enhancer` | Enhancer | None | DNABERT-2, NT-v2 | match |
| `claim-cnn-enhancer-cohn` | Enhancer Cohn | HyenaDNA | None | match |
| `claim-cnn-enhancer-ensembl` | Enhancer Ensembl | None | None | match |
| `claim-cnn-human-tfbs-1` | Human TFBS 1 | None | Caduceus-Ph, GROVER | match |
| `claim-cnn-human-tfbs-2` | Human TFBS 2 | None | Caduceus-Ph, GROVER | match |
| `claim-cnn-human-tfbs-3` | Human TFBS 3 | Caduceus-Ph, DNABERT-2, GROVER, HyenaDNA, NT-v2 | None | match |
| `claim-cnn-human-tfbs-4` | Human TFBS 4 | DNABERT-2, HyenaDNA, NT-v2 | Caduceus-Ph, GROVER | match |
| `claim-cnn-human-tfbs-5` | Human TFBS 5 | None | Caduceus-Ph, GROVER | match |
| `claim-cnn-open-chromatin-region` | Open Chromatin Region | DNABERT-2, GROVER, HyenaDNA, NT-v2 | None | match |
| `claim-cnn-promoter-all-300-bps` | Promoter All 300bps | DNABERT-2, GROVER, HyenaDNA, NT-v2 | None | match |
| `claim-cnn-promoter-all-70-bps` | Promoter All 70bps | Caduceus-Ph, DNABERT-2, GROVER, HyenaDNA, NT-v2 | None | match |
| `claim-cnn-promoter-arabidopsis-nontata` | Promoter Arabidopsis NonTATA | Caduceus-Ph, DNABERT-2, GROVER, HyenaDNA, NT-v2 | None | match |
| `claim-cnn-promoter-arabidopsis-tata` | Promoter Arabidopsis TATA | Caduceus-Ph, DNABERT-2, GROVER, NT-v2 | None | match |
| `claim-cnn-promoter-gm12878` | Promoter GM12878 | None | Caduceus-Ph, DNABERT-2, GROVER, NT-v2 | match |
| `claim-cnn-promoter-hela-s3` | Promoter Hela-S3 | None | Caduceus-Ph, DNABERT-2, GROVER, NT-v2 | match |
| `claim-cnn-promoter-huvec` | Promoter HUVEC | None | Caduceus-Ph, DNABERT-2, GROVER, NT-v2 | match |
| `claim-cnn-promoter-nhek` | Promoter NHEK | HyenaDNA, NT-v2 | None | match |
| `claim-cnn-promoter-nontata-251-bps` | Promoter NonTATA 251bps | DNABERT-2, HyenaDNA, NT-v2 | None | match |
| `claim-cnn-promoter-nontata-300-bps` | Promoter NonTATA 300bps | Caduceus-Ph, DNABERT-2, GROVER, HyenaDNA, NT-v2 | None | match |
| `claim-cnn-promoter-nontata-70-bps` | Promoter NonTATA 70bps | DNABERT-2, GROVER, HyenaDNA, NT-v2 | None | match |
| `claim-cnn-promoter-tata-300-bps` | Promoter TATA 300bps | Caduceus-Ph, DNABERT-2, GROVER, HyenaDNA, NT-v2 | None | match |
| `claim-cnn-promoter-tata-70-bps` | Promoter TATA 70bps | Caduceus-Ph, DNABERT-2, GROVER, HyenaDNA, NT-v2 | None | match |

## Table 1 datasets: Supplementary Data 6

Labels are positive/negative counts, or class counts for Enhancer Ensembl.

| Dataset | Train | Test | Median (min-max) bp | Labels | Outcome |
| --- | --- | --- | --- | --- | --- |
| Coding | 75000 | 25000 | 200 (200-200) | 50000/50000 | match |
| DNase I Hypersensitive | 711 | 306 | 243 (220-275) | 280/737 | match |
| Enhancer | 14968 | 400 | 200 (200-200) | 7684/7684 | match |
| Enhancer Cohn | 123872 | 30970 | 267 (2-573) | 77421/77421 | match |
| Enhancer Ensembl | 14968 | 400 | 200 (200-200) | 7684/3842/3842 | match; three-class labels, noted |
| Human TFBS 1 | 24064 | 10314 | 101 (101-101) | 17189/17189 | match |
| Human TFBS 2 | 22870 | 9802 | 101 (101-101) | 16336/16336 | match |
| Human TFBS 3 | 14699 | 6301 | 101 (101-101) | 10500/10500 | match |
| Human TFBS 4 | 20505 | 8789 | 101 (101-101) | 14647/14647 | match |
| Human TFBS 5 | 14699 | 6301 | 101 (101-101) | 10500/10500 | match |
| Open Chromatin Region | 139804 | 34952 | 315 (84-593) | 87378/87378 | match |
| Promoter All 300bps | 41437 | 17759 | 300 (300-300) | 29598/29598 | match |
| Promoter All 70bps | 41437 | 17759 | 70 (70-70) | 29598/29598 | match |
| Promoter GM12878 | 10992 | 2750 | 1583 (102-2995) | 6871/6871 | match |
| Promoter Hela-S3 | 11736 | 2936 | 1109 (101-2998) | 7336/7336 | match |
| Promoter HUVEC | 11928 | 2982 | 1291 (108-2993) | 7455/7455 | match |
| Promoter NHEK | 8170 | 2044 | 400 (200-1800) | 5107/5107 | match |
| Promoter NonTATA 251bps | 27097 | 9034 | 251 (251-251) | 19657/19657 | match; label counts do not sum to train plus test, noted |
| Promoter NonTATA 300bps | 37146 | 15920 | 300 (300-300) | 26533/26333 | match; label counts do not sum to train plus test, noted |
| Promoter NonTATA 70bps | 37146 | 15920 | 70 (70-70) | 26533/26333 | match; label counts do not sum to train plus test, noted |
| Promoter TATA 300bps | 4290 | 1840 | 300 (300-300) | 3065/3065 | match |
| Promoter TATA 70bps | 4290 | 1840 | 70 (70-70) | 3065/3065 | match |

## Descriptive claims and judgements

| Record | Checked against | Outcome |
| --- | --- | --- |
| `feng-dna-fm-20261013-claim-gtex-short-finding` | Results, Gene expression prediction, paragraphs 2 and 3; Methods (paired Wilcoxon) | match |
| `feng-dna-fm-20261013-claim-gtex-long-finding` | Results paragraph 2; Supplementary Table 4 (0.122 vs 0.137, p 0.0005; 0.124 vs 0.127, p 0.975) | match |
| `feng-dna-fm-20261013-claim-tad-finding` | Results, TAD region recognition, paragraph 2; rendered Supplementary Fig. 2 (PDF page 11) | match after correction 1 |
| `feng-dna-fm-20261013-claim-not-extracted` | Article tables and figures, all 11 PDF pages, the six workbook sheets | match after correction 5 |
| `use-case-mapping-feng-dna-fm-20261013-gtex-wb-expression-6kb` | `use-case-regulatory-variant-gene-follow-up`; Table 4; Methods; Data availability | proxy confirmed; 5 evaluations reviewed |
| `use-case-mapping-feng-dna-fm-20261013-gtex-wb-expression-long-768` | Same | proxy confirmed; 3 evaluations reviewed |

Proxy is justified. The use case's output is variant, element and gene hypotheses for perturbation, and its setting treats allele-effect prediction, element-gene linking and shortlist selection as separate comparisons. Table 4 measures how well a frozen embedding plus a per-gene random forest predicts covariate-corrected whole-blood expression across GTEx subjects. That bears on allele-effect prediction only. It does not score single variants, link elements to genes or measure perturbations, and no loci or genes are held out.

Not mapped, correctly: the 22 Table 1 rows classify reference sequence windows into region types, which none of the use cases decides. The stored splice-site protocols stay on `use-case-splicing-follow-up` only; nothing maps to `use-case-patient-rna-splicing-validation`, because no patient RNA is used.

## Configurations, protocols and evaluations

- All 118 evaluations are `independent_paper`: Feng et al. did not develop the models they compare.
- Every protocol and configuration states frozen pretrained embeddings plus a supervised random forest fitted on the task's labels (Fig. 1 legend, Methods). Nothing claims label-free scoring. The TAD protocol trains nothing, reports no metric and has no evaluations.
- Checkpoints match Methods "Model configuration selection" and the bold rows of Supplementary Table 8: NT-v2-500M, Hyena-160K (Table 1), Hyena-450K (long-input expression), Caduceus-Ph-131K. The 6 kb HyenaDNA expression row is not tied to a checkpoint in the source and is recorded as unreported.
- GTEx access matches the Data availability statement: raw individual WGS by application through the GTEx Protected Data Access portal; the expression benchmark is not on Hugging Face.
- The reproduction note on the pinned `gtex_hyena.py` is accurate: it reads `long_seqs_by_gene`, centre-crops to 6,000 bp, writes to `cadph_long`, mean-pools tokens and averages the two allele embeddings.
- Missing-metadata reasons are honest: GTEx file versions, checkpoint revisions and the metric implementation are not stated; budgets were not extracted.

## Conflicts

Found in the first pass and fixed by the extractor in `extract/extract_feng.py` before sign-off:

1. The source record and research.md said Supplementary Fig. 2 and Supplementary Table 8 are not in the Supplementary Information PDF. The PDF has 11 pages and holds both (pages 9 and 11), plus Supplementary Fig. 1 (page 10). The TAD claim now cites Supplementary Fig. 2.
2. The eight GTEx configurations said the article does not state how the two allele embeddings are combined. Methods ("Gene expression prediction benchmark", paragraph 2) says they are averaged, and that Enformer's final hidden state is mean-pooled over regions.
3. "dbGaP" appeared in the access text and the judgement limitations. The source names only the GTEx Protected Data Access portal.
4. The TAD dataset said GRCh38. The TAD section says only "the human reference genome".
5. Recommended additions applied: the authors' "preliminary indicators" caveat, the lack of held-out loci or genes, distal elements outside the 6 kb window, the 131 kb versus 196 kb long inputs, Supplementary Tables 5 to 8 and Supplementary Fig. 1 in the not-extracted list, and checkpoint values for DNABERT-2 and GROVER.

Source discrepancies, kept as printed and recorded on the source records or datasets:

- The main text places the TAD region at about token positions 300 to 700; the Supplementary Fig. 2 caption says about 200 to 600.
- The main text cites the expression hyperparameter grid as Supplementary Table 6 and the classification grid as Supplementary Table 5; the PDF prints them the other way round.
- The main text refers to "the 4 mC detection tasks (Table 4)"; the 4mC results are in Table 3.
- Supplementary Data 6 gives Enhancer Ensembl the same sizes as Enhancer and a three-class label distribution, although Table 1 reports a binary AUC.
- Supplementary Data 6 label counts for Promoter NonTATA 251, 300 and 70 bps do not sum to training plus test size.
- Already recorded by the 7 October batch: the Results text quotes AlphaGenome "AUC = 0.80 for sQTLs"; Table 6 prints 0.7147 (0.8029 is eQTL).

## Remaining gaps

- The baseline CNN's AUC is not printed anywhere, so it has no result records; only the significance lists are recorded.
- Supplementary Data 4 (per-chromosome-group AUCs behind Tables 5 and 6), the rest of Tables 2 and 3, Supplementary Tables 1 to 4 and the figures are not extracted (see `feng-dna-fm-20261013-claim-not-extracted`).
- Table 4 prints no spread; per-gene correlations are shown only as a histogram (Fig. 3).
- The use case still needs `assessed_by` links to the two expression protocols and `use-cases:repin` for the two judgements, done at integration.
- No result was reproduced, and no human scientific review has been done.
