# Review: VEP use-case batch, 2026-10-14

Independent review of `data/omics/vep-use-cases-20261014/` (extraction head 9a1f0eb, branch `claude/vep-use-cases`), following `.agents/skills/review-evidence/SKILL.md` and `docs/collection.md` section 5. Reviewer: a Claude (Opus 5.5) review agent that did not extract this batch. Automated review only; no human review is claimed, and nothing was reproduced.

Outcome: the batch passes after corrections made before it entered the store. All 173 values match their sources. 274 records are `source_checked`; the 21 predictor records without results stay `discovered`. The 21 relevance judgements and 2 baseline claims are `source_checked` with pins.

## Sources and hashes

Every artifact was re-downloaded on 2026-10-14 from the URL on its source record. All 26 match.

- 21 artifacts (Europe PMC XML, the GPN-Star PDF, two README files at pinned commits) match their raw SHA-256.
- 5 PMC article pages (Bergquist 2025, Stenton 2024, Tejura 2024, AFFIPred, PrimateAI-3D) match after normalisation. Each was downloaded twice. The two downloads differed in exactly two lines, the `ncbi_phid` meta content and the `csrfmiddlewaretoken` value (100 bytes per page). A normaliser written for this review, separate from `extract/pmc_html.py`, blanks those two values and gives the recorded hash for both downloads of every page.
- `artifacts/PMC9748256.xml.gz` (gzip SHA-256 `28bb3e751d79727adf066ff165597ee76eb8ff6e03f8ccd9aca6e419ff899d0c`) decompresses to the Pejaver XML.

| Source record | Artifact | SHA-256 | Match |
| --- | --- | --- | --- |
| `vep-uc-20261014-source-pejaver2022` | Europe PMC XML, PMC9748256 | `a78c7bcaacb0ccb72291264bbe7c1f9a16867b0c6207dcbb45c3c59a14af6b3b` | Yes |
| `vep-uc-20261014-source-bergquist2025` | PMC page, PMC12208618 (normalised) | `4fe954451167b5a5717a4c37f4054432e1f02fb59862d0fb909edb525e6bb8e2` | Yes |
| `vep-uc-20261014-source-stenton2024` | PMC page, PMC11560577 (normalised) | `debe1ae8e304ac0a6272c093bcf7874977e7b9b3921dbe7f5ba096701611ebe7` | Yes |
| `vep-uc-20261014-source-tejura2024` | PMC page, PMC11393694 (normalised) | `e00fb418efba3924e47db1aba3be26835dbdbb9f0a4c14aca06a61215ca16ecf` | Yes |
| 22 predictor sources | see `data/omics/vep-use-cases-20261014/sources.md` | as recorded | Yes, all 22 |

Existing sources cited by the judgements were also re-downloaded: the Livesey and Marsh 2025 XML, the ProteinGym README, the two clinical summary CSVs and the ProteinGym paper XML match. The ENIGMA source `uc-clinical-20260930-source-enigma` (PMC11393667 page, retrieved 2026-09-30) does not: raw `cc20d885…`, normalised `cd0d10d7…`, recorded `21e7b079…`. That record has no hash scope and predates the normalisation, so its hash cannot be reproduced from a PMC page. It is outside this batch and is not changed here (see Remaining gaps). The text that the two ENIGMA judgements rely on was read in today's copy: generic Pejaver BayesDel thresholds assign BP4 to under 10% of the BRCA1 and BRCA2 benign reference variants, and PP3 to 29% and 36% of them.

## Values checked

`review/check_values.py` was written for this review and does not import or copy `extract/build_batch.py` or `extract/pmc_html.py`. It reads Pejaver Tables 2 and 3 from the XML table-wraps with ElementTree and Bergquist Table 1 with `html.parser`, asserts the header rows and row labels, and derives each expected value itself. For `numeric_value` it uses a different rule from the extractor: it reads each tool's score orientation from the row's one-sided cells and takes the interval end on the weaker side, where the extractor compares with the next-stronger cell. For every result it compares printed value, numeric value, locator, metric, qualifier, unit, unit detail, direction, the uncertainty or its missing reason, and the evaluation's configuration (by reported name), protocol and dataset. It also checks that each cell has exactly one result and that `claims.csv` agrees.

Before relying on it, five errors were seeded into a copy of the batch: the far end of a two-sided interval as `numeric_value` (VEST4 PP3 Supporting), a changed printed digit (ESM1b +1), a result moved to another tool's evaluation (CADD BP4 Moderate), a changed confidence bound (SIFT lr+) and a swapped qualifier (REVEL −3). It reported all five. The real batch was untouched.

| Source | Table | Results | Mismatches |
| --- | --- | --- | --- |
| Pejaver et al. 2022 | Table 2, 13 tools x 8 strengths | 104 | 0 |
| | Table 3, lr+ with 95% CI, and gnomAD fraction, 3 tools | 6 | 0 |
| Bergquist et al. 2025 | Table 1, 7 tools x 9 point levels | 63 | 0 |
| Total | | 173 | 0 |

Hand checks (seed 20261014, 12 results), each read beside the printed table: Pejaver PolyPhen2 PP3 Supporting `[0.978, 0.999)` to 0.978, MutPred2 PP3 Supporting `[0.737, 0.829)` to 0.737, REVEL BP4 Supporting `(0.183, 0.290]` to 0.290, EA PP3 Supporting `[0.685, 0.821)` to 0.685, PhyloP, SIFT, EA PP3 Strong and PolyPhen2 BP4 Strong `–` to null; Table 3 SIFT lr+ 0.048 and gnomAD fraction 0.504 (the Results text says 50.4%); Bergquist REVEL +4 `≥ 0.932` to 0.932 and −2 `[0.053, 0.183]` to 0.183. All agree.

Other fields: configuration facts match Pejaver Methods 'In silico tools considered' (dbNSFP scores for FATHMM, GERP++, MPC, PhyloP, PrimateAI, REVEL, SIFT and VEST4; scores generated by the authors for BayesDel without MAF, CADD, EA, MutPred2 and PolyPhen-2 HumVar; FATHMM and SIFT transformed for analysis while Table 2 prints them on their own scales). The denominators 11,834 and 363,894 are in the Methods text. Bergquist's tool selection, VARITY_R and the training-overlap statement match its Materials and Methods.

## Rulings on the extractor's open questions

1. **(a) Interval in `printed_value`, bound in `numeric_value`.** Accepted. The printed interval is kept exactly. The bound is the score a variant must reach for that strength, which is how the calibrations are used, and my independent rule gives the same value for all 108 numeric cells. It is safe in the catalogue: the metric's direction is `unknown`, and `shared/omics/catalogue-query.ts` refuses automatic comparison when direction is not known, so bounds on different tools' scales are never ranked. I added one sentence to the concept definition saying values are on each predictor's own scale and are not comparable between predictors.
2. **(b) Origin.** Accepted for Pejaver et al. 2022: the Declaration of interests states that V.P., B.-J.F., K.A.P., S.D.M., R.K., A.O'D.-L. and P.R. took part in developing some of the assessed tools, and references 13, 18, 19, 23 and 25 tie them to BayesDel, MPC, MutPred2, REVEL and VEST4. For Bergquist et al. 2025 the caption says all intervals of the non-bold rows (BayesDel, MutPred2, REVEL, VEST4) are those of the previous study, with the 3-point and indeterminate columns added. The same calibration should carry the same origin in both papers, so the BayesDel and VEST4 rows were changed to `author_reported` and their interpretation says why. AlphaMissense, ESM1b and VARITY_R stay `independent_paper`: none of their developers is among Bergquist's authors. I did not add `original_evaluation` links: the Bergquist rows are not pure copies (two columns are new) and the link would block the whole row from comparison.
3. **(c) PMC hash normalisation.** Accepted. Blanking two per-request tokens is the only way to give a PMC page a hash a later reviewer can reproduce, and the normalisation is narrow: each pattern must match exactly once, only the attribute value is blanked, and two raw downloads of each page differ only there. The raw hash of the collector's retrieval is kept in `hash_scope`. The wording was not consistent with `docs/collection.md` ("For a mutable website, record that it is mutable and that the hash describes one retrieval"): it said "a re-download hashes the same". It now says the page is a mutable website and the hash describes the 2026-10-14 retrievals.
4. **(d) Use-case count.** `docs/use-cases.md` said "There are 26". With these two the store has 28; the sentence now says 28. The later mention of 26 describes the October 2026 migration batch and is left as it is.
5. **(e) `evidence-strength-score-interval`.** Accepted, with the sentence added in ruling 1. No existing concept holds a calibrated score range; `likelihood-ratio` and `proportion` are correctly reused for Table 3.

## Exclusions on #153

The rule applied: no record if the server or software is no longer available, a newer tool from the same group supersedes it, or it was published before about 2019 with no recent independent benchmark showing competitive performance. I re-probed the cited servers once at 15:34Z: PaPI, ENTPRISE, MTBAN, CpGenie, FINSURF and PON-P3 gave no response, PON-PS returned 404, AFFIPred 502 and DAMpred 200, matching the collector's log.

- PaPI, SAAPpred, ENTPRISE, VIPUR, UMD-Predictor, ShapeGTB, CpGenie, GWAVA (2013 to 2018, unavailable or never independently benchmarked since) and PON-PS (server gone, superseded by PON-P3): justified.
- DAMpred, PEPSI, DVAR (2019) and ExPecto (2018): borderline and marked as such. In practice every 2019 tool was excluded and every kept tool is from 2022 or later, or (EA) carries a clinical calibration, so the date line is applied consistently.
- ESGMM (2024): justified; the preprint states no code or server.
- **MTBAN (2021): I think this exclusion is inconsistent.** Its server did not respond, but its code repository exists (github.com/ha01994/MTBAN, last push 2024-02-13). FINSURF (2022) and AFFIPred (2025) were kept on exactly that basis. The other reason given, that Livesey and Marsh score its base model mutationTCN, is about coverage, not about the tool being old or bad. I did not reverse it; the repository owner should decide whether MTBAN gets a `discovered` record.
- Kept tools: EA (2014) is kept because Pejaver et al. 2022 calibrate it, which meets the rule. No kept tool looks to me like it should be excluded. LYRUS, MLVar and DeepRank-Mut have no independent benchmark, but the date rule does not apply to tools from 2022 and later.

## Predictor records

All 22 checked against their own sources. Every access URL appears in the source text; names, descriptions and method types agree with the abstracts and Methods (for example AFFIPred's 210 million predictions, LYRUS's 22,639 variants in 4,363 structures, MutaPheno's 67,791 training variants and 34 features with a random forest, Rhapsody-2's 117,525 variants, LOL-EVE's 13.6 million promoter sequences and 12-layer CTRL architecture, PromoterAI's −1 to 1 range and ±0.1, ±0.2, ±0.5 thresholds). No record cites the AVE list, and no fact in them is missing from the cited source. EA is `source_checked` because it carries results; the other 21 stay `discovered`.

## Use cases and judgements

Both use cases are well formed. Their questions, inputs and outputs fit the linked protocols; #151 excludes genes with an expert-panel specification and #152 excludes supervised models trained on the target assay, and the judgements respect both. Livesey and Marsh excluded the results of the five DMS-trained VEPs for the proteins they were trained on (Table S2), so no `excluded_evaluations` entry is needed on #152. No other evaluation on a linked protocol needs excluding.

Direct versus proxy: accepted as drafted. For #151 the two calibration tables answer the question (thresholds per strength) and Table 3 tests the developer thresholds against the PP3 cut-off, so they are direct; the gnomAD over-calling fraction, the discrimination rankings and the single-gene checks are proxy. For #152 the ProteinGym zero-shot DMS track and the five Livesey and Marsh DMS strata measure what the use case asks.

Changes to judgements:

- Pejaver intervals: training variants were removed only for seven tools and their constituents (Methods); calibration variants may not represent novel variants (Stenton et al. 2024, Table 1).
- Bergquist intervals: all four carried-over rows have developers among the Pejaver authors; some previously calibrated tools missed the 3-point likelihood ratios (Fig. 1B); the authors' own statement that the study shares the earlier limitations, including potential circularities; VARITY's per-variant held-out scores.
- Developer-threshold lr+: strength judged on the point estimate (Table 3 footnote); ClinVar label caveat.
- ProteinGym clinical (zero-shot and supervised): the circularity, cross-gene comparability and 2023-set caveats the earlier review gave the same protocols on other use cases.
- Ramadane and ENIGMA: BRCA1 and BRCA2 are themselves excluded from #151, so these show behaviour in one gene with a specification, not in genes without one.
- #152 Livesey (five judgements): the limitation said overlap between DMS-trained VEPs and the 36 sets "is not stated". The paper says the authors excluded those VEPs' results for their training proteins (Table S2), and names five such VEPs (Envision, CPT-1, DeMaSk, VARITY_R, VARITY_ER). Corrected, with the authors' remaining concern about tuning against DMS data (ESM-1v).
- #152 ProteinGym: some leaderboard models are by ProteinGym's authors; assays span many organisms.

Every judgement lists all evaluations on its protocol in `reviewed_evaluations` (3 to 97 each). Evaluations already in the store were value-checked by their own independent reviews; I re-matched their source hashes but did not re-check their values.

Baselines: SIFT for #151 (conservation-based, in both Pejaver tables; Pejaver describe it as among the first and most used tools) and the site-independent alignment model for #152 (ProteinGym README lines 66 to 70, first row of the substitution baselines table, Hopf et al. 2017). Both are the best established pre-machine-learning method and both are scored beside machine-learning methods on a linked protocol. Accepted. The sentence "PolyPhen-2 and CADD are trained classifiers" in the SIFT rationale is not from the cited source; it is general knowledge and was left.

Summary claims: `docs/use-cases.md` makes a summary optional and unpublished until reviewed, so none was drafted. It is listed as a gap.

## Other corrections

- Bergquist uncertainty: `unreported` changed to `unextracted` on the 59 cells with a value. The main text prints no bounds, but the Supplementary Material was not read (its PMC link returned an HTML page, not the PDF), so "not reported" was not established.
- gnomAD fraction at developer thresholds: direction `lower` changed to `unknown` on the protocol and its 3 results. The authors compare the fraction with the 4.41% prior; a value below the prior would not mean a better tool. The protocol's limitation now says so.
- Bergquist protocol: added the source conflict that the caption says Very Strong was never reached, while Pejaver Table 2 has a REVEL BP4 Very Strong interval (≤0.003), which Bergquist's REVEL −4 interval (≤ 0.016) covers. This does not change a printed value, so it is a limitation, not an evidence concern.
- Review objects on every record (`reviewed_at`, no `date`), statuses, `coverage.json` status, and pointers to this review in `research.md` and the dossier.
- `missing_metadata` keys sorted. `npm test` failed after the batch entered the store because `normalizeAttributes` would reorder PromoterAI's `missing_metadata` (`version` before `training_data`). The sign-off script now sorts these keys; the stored record was changed to the same bytes and the change recorded with `records -- change`. Form only; no value changed.

All corrections were made by `review/signoff.py`, which refuses to run on anything but the extractor's `batch.jsonl` (SHA-256 `277d103f76bd9956f9d03bb902cb6ac27af99b88315050728d3cedc3c99c8f39`). No ID, printed value, numeric value, locator or source hash was changed.

## Integration

`evidence-checked.json` was checked: the "current" values equal the store's `evidence_checked` on all seven use cases, and the cited documents exist. It was applied with `records -- change` against this review.

## Store and validation

`records -- add` added the 295 records (SHACL shapes pass). The two new use cases already carried their `assessed_by` links. `use-cases:repin` pinned the 21 judgements and 2 baselines against this review. `records -- change` recorded the seven `evidence_checked` updates and the PromoterAI key-order fix. `records -- check`: 77,022 records match their provenance.

Run one at a time: `npm test` failed once (the key-order test above), then passed after the fix (50 files, 524 tests); `npm run test:python` passed (10 tests); `npm run typecheck` passed; `npm run build` exited 0. In the built use-case artifact all 21 new mappings are active, both baselines are published, and no mapping active in release 2026-10-14-53895165fa97 is withheld (347 active before, 381 after). The build's `data/omics/releases/` and `website/` output was reverted and is not committed.

## Remaining gaps

- MTBAN exclusion (above) needs the repository owner's decision.
- `uc-clinical-20260930-source-enigma` cannot be re-verified by hash; it needs an audit that re-pins it with the PMC normalisation and a mutable-website note. Adding an evidence concern here would withhold judgements on other use cases for a hashing problem, not a content problem, so I did not.
- Pejaver Table S1 and Data S1 and S2, and the Bergquist supplement, were not retrieved.
- The gaps the extractor recorded stand: the closed 2026 Genetics in Medicine calibration, BayesQuantify and P-KNN, Stenton Table 2, Dubé et al. 2026, and EvoRator2, TransEFVP and VAMPP without a retrievable primary source.
- No summary claim for either new use case.
- The existing ProteinGym leaderboard evaluations with `author_reported` (noted in the previous review) are still unaudited.
