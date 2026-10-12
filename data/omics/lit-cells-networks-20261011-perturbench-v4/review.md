# Review: lit-cells-networks-20261011-perturbench-v4, 2026-10-12

Source: PerturBench arXiv v4 (NeurIPS 2025 Datasets and Benchmarks).

Reviewer: Claude review agent `reviewer-cn-2`, independent of the extractor `lit-cells-networks`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

The reviewer reported on this batch together with `lit-cells-networks-20261011-chen2026` and `lit-cells-networks-20261011-scmbench`. The common sections and this batch's corrections and answers follow, unchanged.

# Independent review: PerturBench v4, Chen 2026 and SCMBench batches

Reviewer: Claude review agent (reviewer-cn-2), independent of the collector; no human review claimed.
Date: 2026-10-12. Worktree reviewed: /Users/timrichardson/Documents/projects/personal/blog/rewire-benchmark-data-lit-cells-networks
(batch folders treated as the source of truth; no record was edited and nothing was committed).

## Verdicts

- `data/omics/lit-cells-networks-20261011-perturbench-v4` (340 results): approved with corrections P1 to P7.
- `data/omics/lit-cells-networks-20261011-chen2026` (378 results): approved with corrections C1 to C7.
- `data/omics/lit-cells-networks-20261011-scmbench` (241 results): approved with corrections S1 to S5.
- New metric concepts in `data/vocab/metric.ttl`: approved, with one definition change (P7).
- Use-case summaries: no summary text was proposed for either use case these batches touch, so none is approved. No use-case field change is approved; no exclusion or input change is needed (the Jiang24 scope issue is handled as a limitation, P5).

No printed value, numeric value, uncertainty value or cell locator is wrong in any of the three batches. The corrections concern one configuration mapping, metric qualifiers, evidence concerns and judgement wording.

## Corrections

### PerturBench v4

P1. Evaluation `lit-cells-networks-20261011-perturbench-v4-eval-srivatsan20-collapse-decoder`: change the `system` link target from `perturbench-method-decoder` to `perturbench-method-decoder-cov`. Also change the mapping in `extract/extract_perturbench_v4.py` line 58 to `"DecoderOnly": "perturbench-method-decoder-cov"` and delete the comment on line 57. Reason: Table 12 'DecoderOnly' is the decoder with only covariates as input. Appendix C.7.1: "1) our DecoderOnly with only cell line as input, 2) our DecoderOnly with cell line and perturbations as input"; Figure C.2 legend: "A) DecoderOnly model with only covariates as input. B) DecoderOnly model with covariates and perturbations as input". Section 5.1 names that covariates-only model 'Decoder (Cov)': "Our Decoder-Only baseline which does not leverage perturbation information, Decoder (Cov)". The values agree: Table 12 DecoderOnly RMSE mean rank 0.488, against Decoder (Cov) 0.50 and Decoder 0.14 in Table 5. Section 4.2 ("We leave DecoderOnly DEG recall empty") uses DecoderOnly for the whole class, so it does not support the collector's mapping. The four results of this evaluation keep their IDs and values.

P2. Configuration `lit-cells-networks-20261011-perturbench-v4-config-decoderonly-plus-perturbations`: replace `description` with: "PerturBench Decoder-only baseline with cell line and perturbations as input (Appendix C.7.1; Figure C.2B), as named in the mode-collapse Table 12. The source does not say whether this is the 'Decoder' row of Tables 2 and 5." Keep it as a separate configuration.

P3. Replace the second constraint ("Compare models only within one table column; MMD and RMSE are not printed for scGPT-input and some baseline rows.") in each judgement. RMSE is printed for every row; the statement is wrong.
- `use-case-mapping-lit-cells-networks-20261011-perturbench-v4-norman19`: "Compare models only within one table column; MMD, MMD PCA and DEG recall are not printed ('-') for the CPA* (scGPT), LA (scGPT) and GEARS rows, and DEG recall is not printed for the Decoder row."
- `use-case-mapping-lit-cells-networks-20261011-perturbench-v4-jiang24`: "Compare models only within one table column; DEG recall is not printed ('-') for the Decoder row."
- `use-case-mapping-lit-cells-networks-20261011-perturbench-v4-frangieh21`: "Compare models only within one table column; MMD, MMD PCA and DEG recall are not printed ('-') for the CPA* (scGPT) and LA (scGPT) rows, and DEG recall is not printed for the Decoder row."

P4. `use-case-mapping-lit-cells-networks-20261011-perturbench-v4-norman19`, `endpoint`: replace with "Cosine similarity and rank of predicted log fold change, RMSE and RMSE rank of the mean expression profile, MMD and DEG recall for held-out K562 CRISPRa dual-gene perturbations (Norman19), for CPA, SAMS-VAE, Biolord, GEARS, Latent Additive (with and without scGPT embeddings), Decoder and Linear models". Table 6 (RMSE) is part of the protocol and was left out of the endpoint.

P5. `use-case-mapping-lit-cells-networks-20261011-perturbench-v4-jiang24`: append to `limitations`: "The use case lists cross-cell-type transfer as outside the cited GEARS usage scope; this protocol tests transfer to held-out cell line and cytokine states and does not include GEARS, so it bears only on the use case's open question about performance in a new cell system."

P6. `use-case-mapping-lit-cells-networks-20261011-perturbench-v4-frangieh21`, `endpoint`: replace "trained on mono-culture and 30% of co-culture perturbations (Frangieh21)" with "trained on all other perturbations, including the other culture conditions and the remaining 30% of co-culture perturbations (Frangieh21)". Appendix D.4 only says the remaining perturbations are used for training, and Table 1 lists three states, not one.

P7. `data/vocab/metric.ttl`, `:perturbench-energy-mmd`: replace the `skos:definition` with "Energy distance between the predicted and observed perturbed cell distributions, reported by PerturBench as MMD. Computed in gene expression space unless metric_qualifier names another space, such as PCA." Section 4.2.2 says "Our MMD metric computes the energy distance between predicted and the ground truth perturbed cells"; "averaged over perturbations" is not stated there.

## Answers to the collector's questions

PerturBench v4
- Reuse of the v1 configuration records for rows with the same printed name: approved. They are the same authors' reimplementations, and v4 has its own source, protocols and evaluations. Note for a later audit: the stored v1 evaluations record CPA*, SAMS-VAE* and Biolord* as `author_reported`, while v4 records them as `independent_paper`. The judgements already forbid combining v1 and v4.
- 'DecoderOnly' mapped to Decoder: rejected. It is Decoder (Cov) (P1, P2).
- Jiang24 held-out states: confirmed as stated. The Table 4 caption (30 states, 70% of perturbations from 9 states held out) and Appendix D.4 (70% held out in 12 combinations of IFNG, INS and TGFB with k562, mcf7, ht29 and hap1) disagree. A limitation is the right record; it does not affect within-table comparison.
- Origin split: approved. No PerturBench v4 author (Wu, Wershof, Schmon, Nassar, Osiński, Eksi, Yan, Stark, Zhang, Graepel) is an author of CPA, SAMS-VAE, Biolord or GEARS. Ablations and scGPT-input variants built by the authors (CPA* (noAdv), CPA* (scGPT), SAMS-VAE* (S)) are correctly `author_reported`.
- '-' cells: the 12 result tables have 369 cells; the 29 printed '-' are not recorded, and none is recorded as zero.

## Checks run and outcomes

Sources. I re-downloaded every artifact with curl and hashed it with shasum.

| Source | URL | SHA-256 | Match |
| --- | --- | --- | --- |
| perturbench-v4 source-wu2025 | https://arxiv.org/html/2408.10609v4 | b73f2644b129ca209b69812ad467d595e15c283f6cae5c3c9bbc5a4c5870996a | Yes |
| (reference only) PerturBench v4 PDF | https://arxiv.org/pdf/2408.10609v4 | 5922c95d24526b5b078887bdf2181e354ab3ddf05fd943c55041af1bea6caf96 | Yes, matches sources.md |
| chen2026 source-chen2026 | https://arxiv.org/pdf/2607.17227v2 | 8137338c6146f570a6546f30707d4244baca9dab848b32c51539665a5ba539da | Yes; archived .gz 1dd08b0d... decompresses to the same hash |
| scmbench source-article | Europe PMC PMC13342640 fullTextXML | 7aa2dbf1fc26bd602bf26e52c1061f91358a1c6cb389f57edc0ebfb0edc64f57 | Yes; archived .gz matches |
| scmbench source-sd2 | Springer MOESM4 xlsx | 77582bcc906fed343de12c2b2ed7443e94f5d11bf93b7f3862a37c5099015443 | Yes; archived .gz matches |
| scmbench source-sd1 | Springer MOESM3 xlsx | 7287a457b1e856742a90043e96dc57b667210b28a8228d4d9a6de5d7156ecfb9 | Yes; archived .gz matches |

Full automated comparison with my own parsers, not the collector's scripts:
- PerturBench: BeautifulSoup parse of the HTML `ltx_table` grids for Tables 2 to 13 (369 cells, 29 '-'). 340 of 340 results match the printed cell, numeric value and decimal standard deviation (n = 5), and each maps to exactly one cell. No cell missed, no duplicate.
- Chen: my own regex parse of `pdftotext -layout`, with model blocks assigned from the printed order and labels asserted where they share a line. 378 of 378 printed and numeric values match. No cell missed, no duplicate.
- SCMBench: openpyxl cached values plus my own read of the sheet XML. 241 of 241 match on raw XML string, numeric value and 15-significant-digit printed value. Row and column labels in every locator match. 39 Overall or column H cells are formulas (AVERAGE). I spot-checked per-dataset cells against the per-metric sheets (GLUE PBMC-10k, 0.676475 = mean of 0.8364, 0.8039, 0.5997, 0.4659). The article's printed overall scores (GLUE 0.599; Seurat4, scJoint and scMDC on PBMC-10k 0.7952, 0.7671 and 0.7391) agree with the sheet.

Stratified hand checks against the rendered table:
- PerturBench: 48 values, 4 per table from Tables 2 to 13, checked by eye against the v4 PDF rendering (pdftotext -layout of the reference PDF). They cover every model family, including Biolord*, GEARS-adjacent Norman rows, SAMS-VAE* (S), LA, Linear, DecoderOnly and the matrix distances. All match.
- Chen: rendered PDF pages 46 to 48 (Tables 2 to 5 and S2) as images and checked by eye. 45 values cover every table and all six models: all Table 2 Nicheformer and GenePT-w rows, the Table 3 spatial rows across the page break, every Table 4 block including Novae SEAAD, the Table 5 GenePT-w and scELMo rows, and all of S2. All match, including the model block assignment around the Table 3 page break and the Table 4 labels between rows.
- SCMBench: 40 values (20 per sheet, random with a fixed seed) checked against the cell grid. All match, including the column H value for FM-scVI.

Mapping checks:
- Metric, qualifier, direction and unit were checked for every metric column. Wrong: C1, C2, C3 and S3. Units follow the store (PerturBench v1 units; unitless for Chen and SCMBench).
- Uncertainty is on PerturBench only and correct. Chen and SCMBench print no spread; `missing_metadata` says so correctly.
- Dataset, split and protocol links were checked for every result: each table maps to the right protocol and subset. Wrong: S4.
- Configuration mapping: one error (P1).

Duplicates:
- No batch ID exists on origin/main (bba147c, 54,592 IDs). Every external link target exists there.
- No other open branch (`claude/lit-20261011-*`, local and remote) or worktree (`../rewire-benchmark-data-lit-*`) holds these sources or the new model families (Nicheformer, CellPLM, scGPT-spatial, Novae).
- The store has GenePT and scELMo papers (`genept-2024`, `scelmo-2025`) and a GenePT-w configuration, but no GenePT or scELMo model record, so the new model records are not duplicates.
- PerturBench v1 is a separate source in the store; v4 is a new source with new protocols. That is correct, because the runs differ.
- None of the five new metric concepts respells an existing one (`scib-asw-label` is the rescaled ASW; there is no MMD, matrix distance or transposed-rank concept). No other branch or worktree adds them.

Relevance judgements:
- For all 10 judgements (3 PerturBench, 7 Chen), `reviewed_evaluations` equals the set of evaluations on the protocol. No `excluded_evaluations` were needed.
- `proxy` is justified for all 10, given corrections P3 to P6, C5 and C6.
- Not mapping the PerturBench chemical protocols (Srivatsan20, OP3) or the SCMBench integration protocols is correct. `use-case-phenotype-perturbation-selection` excludes transcriptome similarity alone, and no use case covers multi-omics integration.

Use-case summary: none proposed by the collector; nothing to approve. The existing summaries do not cite these batches and remain accurate. Optional evidence-gap wording for the integrator, not required: replace "PerturBench combination-prediction results are in the store as task records and need a protocol before they can be judged for this use case." with "PerturBench v1 combination-prediction results remain task records without a protocol; the PerturBench v4 reruns (arXiv v4, Tables 3 and 6) are judged as a separate protocol and are not combined with v1."

Other: `claims.csv` agrees with `batch.jsonl` (record IDs, printed values and locators) for all three batches. No batch has a `derivation`, so no recomputation was needed.

Not run: `npm test`, `npm run typecheck` and `npm run build`. I edited no records; those runs belong to the apply step after the corrections. No external API received an email or personal identifier.

## Corrections applied

Applied by the extractor in the `extract/` scripts, as the reviewer specified, before the batch was added to the store.

1. P1: the Srivatsan20 mode-collapse DecoderOnly evaluation links to `perturbench-method-decoder-cov`, set in `extract/extract_perturbench_v4.py`; its four results keep their IDs and values.
2. P2: the DecoderOnly (+ perturbations) configuration has the reviewer's description.
3. P3: the second constraint of each of the three judgements is the reviewer's text.
4. P4: the Norman19 judgement endpoint is the reviewer's text.
5. P5: the Jiang24 judgement has the reviewer's limitation appended.
6. P6: the Frangieh21 judgement endpoint uses the reviewer's wording for the training set.
7. P7: `:perturbench-energy-mmd` in `data/vocab/metric.ttl` has the reviewer's definition.
8. The three judgements are `source_checked`, linked from `use-case-genetic-perturbation-response` and pinned with `npm run use-cases:repin`.
9. The optional evidence-gap wording for the use case was not applied; the reviewer marked it not required.
10. Every record is `source_checked`; each result's and claim's `review` block names the reviewer and keeps the extraction note.

## Records after correction

- claim: 3
- configuration: 3
- dataset_subset: 5
- evaluation: 57
- protocol: 7
- result: 340
- source: 1
