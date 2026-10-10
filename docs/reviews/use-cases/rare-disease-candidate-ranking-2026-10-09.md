# Rare-disease candidate ranking: independent review of the 2026-10-09 batch

Batch: `data/omics/use-case-coverage-rare-ranking-20261009/` (616 records). Use case: `use-case-rare-disease-candidate-ranking` ("Which methods recover causal variants and genes within a realistic laboratory review budget?").

Reviewer: a separate Claude review agent that did not collect or extract the batch. No human review is claimed. Nothing was executed or reproduced; this is a check of transcription and relevance against the pinned sources.

## Outcome

- All four pinned artifacts re-download to their SHA-256. The archived Kafkas et al. article decompresses to its pinned bytes.
- All 496 results match their source cells: printed value, numeric value, locator, metric, qualifier, unit, direction, evaluation, configuration, protocol and dataset. No number was wrong.
- Every top-k row is monotone from top 1 to top 50, and every printed percentage equals a whole number of cases out of the stated cohort size at the printed precision (305, 209 or 152 for Yuan et al.; 50, 100 or 500 for Kafkas et al.). The sources print rates only, so no rate could be recomputed from counts.
- Corrections, none of which changes a number:
  - the singleton mode of the 10 Yuan et al. 2024 AMELIE and LIRICAL evaluations;
  - the origin of the 6 Kafkas et al. GPT-4 evaluations;
  - one claim locator;
  - two dataset descriptions;
  - protocol and judgement limitations.
- One relevance change: Yuan et al. 2022 KMCGD is now proxy, not direct.
- Privacy: the archived Yuan et al. 2024 article was removed. Its Table 2 and Results name individual cases and their causal variants.
- The 7 judgements are `source_checked` with `reviewed_evaluations` and a review. Pins are not set. Every record in the batch is `source_checked`.

## How the check was done

1. Downloaded each artifact into its own empty directory. The first Europe PMC `supplementaryFiles` request for Yuan et al. 2022 timed out; the retry succeeded. From that zip, only `sm_table_3_r1_bbac019.docx` was extracted and hashed, and the zip was then deleted. SM Tables 1, 2 and 4 were not opened, because the collector describes SM Table 1 as cohort details.
2. Read SM Table 3 from `word/document.xml` with a stdlib reader written for this review. Read Yuan et al. 2024 Table 1 (`Tab1`) and Kafkas et al. Table 3 (`Tab3`) from the article XML, resolving row and column spans by position. The extractor's `extract/extract_rare_ranking.py` was not imported or run.
3. Built the expected identity of every cell from the table headers (cohort, tool, protocol, set size, metric) and compared each result. Checked that each expected cell has exactly one result: 496 expected, 496 matched.
4. Read the Methods, Results, Discussion, author lists and contribution statements of all three articles. Checked authorship against the author lists of the cited tool papers through Europe PMC metadata.
5. Searched `main` and every `rewire-benchmark-data-*` worktree for existing records of each tool and of GPT-4.
6. Dry run: `addBatch` into a scratch copy of the store, then `loadRecords` and `deriveUseCaseInputs` with the seven proposed `assessed_by` links added to the scratch use case.

## Sources and hashes

| Source ID | Artifact checked | SHA-256 (re-downloaded 2026-10-09) | Matches record |
| --- | --- | --- | --- |
| `rare-ranking-20261009-source-yuan2022` | PMC8921623 full-text XML | `a0e15e5a113ecbc1c8a3b17072a4028c55ae53c09ba0677d6fdb7601cfc8f1ca` | Yes |
| `rare-ranking-20261009-source-yuan2022-sm-table-3` | `sm_table_3_r1_bbac019.docx` in the supplementaryFiles zip | `5a49ff00fe9b6ed8a92786c83cee79da7b2c9b958a6784d41e496ef59f17e707` | Yes |
| `rare-ranking-20261009-source-yuan2024` | PMC10838329 full-text XML | `a5dbb24eb1e29ef8fde2832da1ff49a436464210d0e54d2a1fd10ad764a24b45` | Yes |
| `rare-ranking-20261009-source-kafkas2025` | PMC12041562 full-text XML | `75851f55d59fb0f194ca8bbcf10f47b6f593e8658239dc0fb85f5d2844236a3b` | Yes |

The zip itself hashed `b1c6092b3b199b1aa3c7e847e7e4cd2c1faef3c18d5db50be67104859afb86a0` in this retrieval, against `2477ed03...` for the collector's. Europe PMC assembles it per request, so only the member hash can be re-verified.

## Values checked

| Source table | Results | Metrics | Mismatches |
| --- | --- | --- | --- |
| Yuan et al. 2022 SM Table 3: 22 rows (11 configurations by 2 cohorts) by 7 top-k columns | 154 | top-1 to top-50 accuracy, percent | 0 |
| Yuan et al. 2024 Table 1: 26 rows by 7 top-k columns | 182 | top-1 to top-50 accuracy, percent | 0 |
| Kafkas et al. 2025 Table 3: 5 set sizes by 4 metrics by 8 columns | 160 | Hits@1 and Hits@10 (percent), ROC AUC, AUPR | 0 |
| Total | 496 | | 0 |

Configurations: all 27 match their sources. The 11 Yuan et al. 2022 versions match Table 2 (PhenIX 1.16, Exomiser 12.1.0, DeepPVP 2.1, Xrare "pub:2015", AMELIE "Oct 5, 2020", LIRICAL 1.3.0, Phenolyzer 0.4.0, HANRD printed as a dash, GADO 1.0.1, Phen2Gene 1.2.3). The 11 configurations are the 10 tools, with AMELIE run in both HPO plus VCF and HPO-only modes. The Yuan et al. 2024 versions match the Fig. 1 legend (Exomiser 13.1.0, PhenIX 1.16, AMELIE 3.1.0, LIRICAL 1.3.4). The Kafkas et al. GPT-4 version `gpt-4-1106-preview` is printed in the Introduction. Exomiser 12.1.0 with default settings and gene scores only is in Methods 'Baseline methods'.

Datasets checked against the text: DDD 305 cases (7.5 HPO terms and 100,033 variants on average; 156 in HGMD Pro-2021.2), KGD 152 trios (58 kept from the 2022 cohort plus 94 added), KMCGD 209, and the three Kafkas sets (GPCards 50, ClinVar 100, PAVS 500).

Claims: the Kafkas ClinVar-bias claim is verbatim. The Yuan et al. 2024 optimal-protocols claim matches. The Yuan et al. 2022 AMELIE claim had the wrong locator (correction 4).

Prose against tables, recorded but not raised as evidence concerns, since the table values are what is stored:
- Kafkas et al. say one-shot GPT-4 beat Exomiser on ClinVar below 25 genes and fell behind above 25. At 50 genes Table 3 still prints Hits@1 87.00 for GPT-4 against 84.00 for Exomiser.
- Kafkas et al. say GPT-4 "outperformed all other methods" on PAVS. Table 3 prints a higher Exomiser Hits@1 at 5 genes (97.60 against 94.80) and at 100 genes (58.60 against 57.80).

## Corrections made in the batch

The batch is not yet in the store, so fields were edited in place. A copy of the collector's `batch.jsonl` was diffed against the reviewed file. Apart from statuses and review blocks, only the fields below changed; no ID, link, printed or numeric value, metric, qualifier, unit, direction or endpoint changed.

1. **Singleton mode of AMELIE and LIRICAL in Yuan et al. 2024.** The 10 AMELIE and LIRICAL evaluations had `comparison.inputs` "Proband HPO terms and exome VCF; trio mode not stated for this row". Discussion paragraph 1, item 4 says AMELIE "was assessed only in singleton mode because trio mode was unavailable" and that LIRICAL's trio mode "was under development". `inputs` is now "Proband HPO terms and exome VCF; singleton", the same string as the Exomiser and PhenIX Protocol A and B rows. The five configurations note the mode with its locator. This is the central correction to the singleton against trio concern. The authors' own comparison of optimised settings sets trio-mode Exomiser and PhenIX against singleton AMELIE and LIRICAL, and the collector's draft summary repeated that comparison.
2. **Origin of the Kafkas et al. GPT-4 rows.** The 6 GPT-4 evaluations were `independent_paper`. The evaluated system is GPT-4 with prompts the authors wrote: Table 1 is titled "Prompts Crafted", Methods 'Prompt engineering' says "we designed structured prompts" and describes the one-shot chain-of-thought prompt "that we designed", and the Author contributions credit Ş. Kafkas and R. Hoehndorf with prompt design. Under the origin definition ("reported by the authors of the evaluated method") these are `author_reported`. The two Exomiser evaluations stay `independent_paper`. The limitation "Neither GPT-4 nor Exomiser was developed by the authors" was replaced in the three protocols and three judgements.
3. **Yuan et al. 2024 limitations.** "Rows mix singleton (A and B) and trio-mode (C and D) runs" now says only Exomiser and PhenIX C and D are trio mode and every other row is singleton. "Parameter protocols were optimised on the same cohorts" is narrowed to the chosen rows (correction text under Concerns). A limitation was added that what separates Exomiser and PhenIX C from D is shown only in the Figure 2 image.
4. **`claim-yuan2022-amelie-published-cases`.** The locator was "Discussion paragraph 1"; the text is in Discussions paragraph 3. The value now adds that AMELIE was slightly lower in the top-20 experiment on the unpublished subset, and that the subset results are shown only in Supplementary Figure 2. `claims.csv` was updated to match.
5. **`data-kmcgd-209`.** Population was "209 solved patients, mixed phenotypic abnormalities". It now gives the source's description: Chinese patients with a wide range of syndromes, diagnosed by WES at the authors' laboratory in 2018 to 2021, with a mean of 2.0 HPO terms (ambiguous terms removed) and 83,587 variants per case.
6. **`data-kafkas2025-gpcards`.** Now states the 50 variants, and that GPCards is also the set on which the prompts were developed (Methods 'Prompt engineering' paragraph 3).
7. **Kafkas et al. protocol limitations added:**
   - the zero-shot prompt is unstated;
   - the random-gene pool is described two ways;
   - Exomiser score is shown because it was the best Exomiser algorithm (others in Supplementary Tables S5 and S6, not read);
   - for GPCards, the values are in-sample for prompt choice.
8. **Judgement limitations, as listed under Judgements.**

## Privacy

`artifacts/yuan2024-article.xml.gz` contained Table 2 ("Information of causal variants of misjudged cases and missed diagnoses"), one row per case with case ID, gene, variant and zygosity, and case IDs in the Results prose. It was removed. Only that table's header was inspected, and no row was printed. `sources.md` now records the removal; the source record keeps the URL and hash. The Kafkas et al. article has no per-case tables and no case identifiers in its prose, so its archive stays. Yuan et al. 2022 was never archived (CC BY-NC). The Yuan et al. 2022 supplementary zip was deleted after extracting SM Table 3, and SM Tables 1, 2 and 4 were not opened. No file in the batch folder contains a case identifier.

## Origin per row

| Source | Rows | Origin | Basis |
| --- | --- | --- | --- |
| Yuan et al. 2022 | all 22 evaluations | `independent_paper` | No author of the paper is an author of any compared tool's cited paper |
| Yuan et al. 2024 | all 26 evaluations | `independent_paper` | Same check; the competing-interests statement lists KingMed and Genetalks employment, not tool development |
| Kafkas et al. 2025 | 6 GPT-4 evaluations | `author_reported` (corrected) | Authors designed the prompts |
| Kafkas et al. 2025 | 2 Exomiser evaluations | `independent_paper` | No Exomiser developer among the authors |

Author lists checked, with the cited paper for each tool from Europe PMC metadata:
- HANRD: Rao A, Vg S, Joseph T, Kotte S, Sivadasan N, Srinivasan R (TCS Research and Innovation, Hyderabad). No overlap with Yuan's group.
- Phen2Gene: Zhao M, Havrilla JM, Fang L, ..., Weng C, Wang K (CHOP, Columbia). Yuan et al. 2022 has a Fang Ping; Phen2Gene's Fang L is a different person.
- DeepPVP: Boudellioua I, Kulmanov M, Schofield PN, Gkoutos GV, Hoehndorf R (KAUST, Cambridge, Birmingham).
- Xrare: Li Q, Zhao K, Bustamante CD, Ma X, Wong WH (Stanford, GenomCan Chengdu). Not Genetalks.
- Phenolyzer: Yang H, Robinson PN, Wang K.
- AMELIE: Birgmeier J, Haeussler M, Deisseroth CA, et al.

None of the 17 Yuan et al. 2022 or 11 Yuan et al. 2024 authors appears. DeepPVP's developers Schofield and Hoehndorf are authors of Kafkas et al. 2025, but DeepPVP is not in Kafkas Table 3, and in Yuan et al. 2022 it was run by an independent group. So no extracted DeepPVP row is author_reported. The protocol limitation names the overlap.

## Reuse and duplicates

- `uc-clinical-20260930-method-exomiser` (`source_checked`, generic "phenotype-aware and variant-aware rare-disease prioritization method") is the right family record for all 7 Exomiser configurations. The only other Exomiser records anywhere are `uc-clinical-20260930-exomiser-v14` (the Talos comparison configuration) and the rare-reanalysis Vestito et al. configurations, which are flag rules and not ranking runs. Agree with not reusing either.
- GPT-4: the only existing record is `reported-model-91d4548437068f`. It is `excluded`, scoped to one cell-identification paper (`llm-cell-identification-2025`), at method level with its version unextracted. A new checkpoint-level record for `gpt-4-1106-preview` is correct.
- No existing record was found for LIRICAL, AMELIE, PhenIX, Xrare, Phen2Gene, DeepPVP, GADO, Phenolyzer or HANRD in `main` or any worktree. The nine new method records are not duplicates.

## Direct or proxy

The relevance scheme defines direct as "the protocol measures the use case's endpoint on inputs of the kind the use case describes". The endpoint is recovery of causal variants or genes within a review budget. The inputs are variant calls, phenotype terms and pedigree. The setting is initial ES/GS interpretation in a defined congenital-anomaly or developmental-disorder population, with singleton and family analyses compared separately.

- **Yuan et al. 2022 DDD and Yuan et al. 2024 DDD: direct.** Case-level rank of the known causal gene within a stated top k, on the original exome VCF and HPO terms of solved DDD cases (neurodevelopmental disorders and congenital anomalies), measures the endpoint on the described inputs. The top-k column is the review budget. In Yuan et al. 2024, singleton and trio rows carry different `comparison.inputs`, so they are not compared automatically.
- **Yuan et al. 2024 KGD: direct.** The Methods describe "cases with various congenital abnormalities", trio WES. 58 of its 152 families are carried over from the 2022 in-house cohort.
- **Yuan et al. 2022 KMCGD: changed to proxy.** The source describes "patients with a wide range of syndromes" and "Chinese with a wide range of genetic abnormalities", with a mean of 2.0 HPO terms. That is a mixed clinical-genetics population, not the defined congenital-anomaly or developmental-disorder population the use case sets, so the setting does not match.
- **Kafkas et al., all three: proxy, confirmed.** The candidate sets are synthetic: the causal gene plus random genes, not a case's variant list. ClinVar phenotypes are database annotations, and GPCards phenotypes are free text with no comparator.

Consistency with the existing proxy judgements: the six Talos protocols evaluate a reanalysis tool on reprocessed calls in a reanalysis study, and Talos returns an unranked set, so there is no rank budget. Both points differ from the Yuan design and justify proxy. The existing Exomiser ACG judgement is the closest case: rank-budget recovery of known diagnoses. Its proxy grade rests on the unresolved 194 against 190 denominator, the reprocessed calls of a reanalysis study and the critically ill infant cohort. I see no reason to change it in this batch, and its pins are not touched.

## Concerns, narrowed

1. **Singleton against trio in one Yuan et al. 2024 table.** Resolved by correction 1. Only Exomiser and PhenIX Protocols C and D (8 evaluations, 56 results) are trio. The other 18 evaluations are singleton and now say so. The comparison fields keep the two modes apart, and the summary below compares within mode only.
2. **Option sets that exist only in a figure.** Narrowed to Exomiser and PhenIX Protocols C and D: 8 evaluations on the two cohorts. The text says only that both are trio mode, so what separates C from D (probably the pathogenicity source) is visible only in the Figure 2 image, which was not read. Protocols A and B are described in the text (PolyPhen, MutationTaster and SIFT; REVEL and MVP). All four AMELIE protocols are fully described in the text (alfqCutoff 0.5% or 2.0%, filterByCount off or on), as is LIRICAL. No value is affected.
3. **Protocols tuned in-sample.** Narrowed to the rows the authors chose on these same cohorts: Exomiser Protocol D, PhenIX Protocol D and AMELIE Protocol B on DDD and KGD (6 evaluations). Read as expected performance on new cases, these rows are optimistic. Every row is still a measured value as printed. Yuan et al. 2022 used default parameters and is not affected.
4. **AMELIE literature bias.** Narrowed to the AMELIE rows on DDD: `yuan2022-ddd-amelie`, `yuan2022-ddd-amelie-hpo` and the four `yuan2024-ddd-amelie-protocol-*`. 156 of the 305 DDD cases are in HGMD. The authors report an almost unchanged trend on the 149 unpublished cases, with AMELIE slightly lower at top 20, but that result is only in Supplementary Figure 2, which is not extracted. The KMCGD and KGD in-house cohorts are unpublished. Beyond the source: every knowledge-based tool whose gene-disease data postdate a DDD diagnosis may benefit from the same publication effect, and the source tests this for AMELIE only.
5. **Kafkas: ClinVar phenotypes match Exomiser's database.** Confirmed verbatim (Results paragraph 4). Narrowed to the ClinVar Exomiser evaluation (20 results). Its input phenotypes are the HPO annotations of the causal OMIM disease, which Exomiser's phenotype data contain, so it favours Exomiser. PAVS uses clinically reported phenotypes and is not affected by this bias. GPCards has no Exomiser row. A separate point the source does not address: ClinVar variants were limited to those added after GPT-4's cutoff, but the gene-disease associations behind them may be older.
6. **Kafkas: unstated zero-shot prompt.** Confirmed. Table 1 lists three zero-shot prompts (Q1 to Q3), Table 2 also tests Q2Q3, and Table 3 does not say which produced its "Zero shot" columns. Narrowed to the 3 zero-shot GPT-4 evaluations (60 results). It matters because the GPT-3.5 prompts in Table 2 range from 30% to 80% Hits@1. The one-shot rows are Q4, the only one-shot prompt. A further point: the prompts were developed on GPCards, so the GPCards GPT-4 values are in-sample for prompt choice.

## Vocabulary

`top-30-accuracy` and `top-40-accuracy` follow `top-50-accuracy`: same scheme, same definition pattern ("Fraction of queries whose correct answer is among the N highest-ranked candidates"), broader `accuracy`, direction `higher`, and matching `Retrieval accuracy@N` and `accuracy_at_N` alt labels. They correctly leave out the molecule-specific scope note on `top-50-accuracy`. No other branch defines them, and neither respells an existing concept. No external match exists for the siblings either. Approved as written.

## Judgements

| Judgement | Relevance | Evaluations reviewed | Outcome |
| --- | --- | --- | --- |
| `...-yuan2022-ddd` | direct | 11 | Pass. Limitations added: truth-set selection, HPO-only configurations, authorship |
| `...-yuan2022-kmcgd` | proxy (was direct) | 11 | Pass as proxy. Setting is not a defined congenital-anomaly or developmental-disorder population |
| `...-yuan2024-ddd` | direct | 13 | Pass. Mode, tuning and figure limitations corrected |
| `...-yuan2024-kgd` | direct | 13 | Pass. As above, plus overlap with the 2022 cohort |
| `...-kafkas2025-clinvar` | proxy | 3 | Pass. Origin, zero-shot prompt and ClinVar bias narrowed |
| `...-kafkas2025-pavs` | proxy | 3 | Pass. Origin and zero-shot prompt |
| `...-kafkas2025-gpcards` | proxy | 2 | Pass. Origin, zero-shot prompt, in-sample prompt choice, no comparator |

None has `excluded_evaluations`. The five HPO-only Yuan et al. 2022 configurations are kept on the DDD and KMCGD judgements. They show what ranking without variant calls achieves, their `comparison.inputs` keep them apart, and a limitation names them.

Exclusions: each Yuan judgement's first limitation states that ranking does not establish pathogenicity or a diagnosis (first exclusion), and the Kafkas judgements state that ranking within synthetic candidate sets is not case-level performance on real exomes. None of these protocols is balanced pathogenic-benign classification (second exclusion), and none is reanalysis (third).

In the dry run, each judgement derives exactly its `reviewed_evaluations` (11, 11, 13, 13, 3, 3, 2), each is withheld only because its pins are unset, and the eight existing judgements on the use case stay active.

## Approved use-case changes

Links and gaps only. No pinned field changes, so the eight existing judgements are not affected; the dry run with the links added shows them active.

Add to `use-case-rare-disease-candidate-ranking` `links`, each with relation `assessed_by`:

- `rare-ranking-20261009-protocol-yuan2022-ddd-singleton-default`
- `rare-ranking-20261009-protocol-yuan2022-kmcgd-singleton-default`
- `rare-ranking-20261009-protocol-yuan2024-ddd-parameter-protocols`
- `rare-ranking-20261009-protocol-yuan2024-kgd-parameter-protocols`
- `rare-ranking-20261009-protocol-kafkas2025-clinvar-gene-sets`
- `rare-ranking-20261009-protocol-kafkas2025-gpcards-gene-sets`
- `rare-ranking-20261009-protocol-kafkas2025-pavs-gene-sets`

Append to `evidence_gaps`, keeping the existing entries:

> No multi-tool comparison on 100kGP, UDN or CAGI cohorts with printed top-k values was found in this pass. The direct evidence comes from one laboratory group (Yuan et al. 2022 and 2024) on the DDD cohort and on its own in-house cohort.

> Top-k recovery is measured only on solved cases with a single causal gene; no added source reports ranking on an unselected or unsolved cohort, so the recovery rates are likely higher than in routine use.

> Candidates per case (review workload) is not reported by the added sources; only top-k recovery of a known causal gene.

> Yuan et al. 2024 chose its Exomiser, PhenIX and AMELIE settings on the same cohorts it reports, and shows what separates Exomiser and PhenIX Protocols C and D only in a figure.

> LLM evidence is limited to GPT-4 on synthetic candidate gene sets (Kafkas et al. 2025), and that study does not state which zero-shot prompt produced its table; no LLM was evaluated on real exome candidate lists.

> Reese et al. 2026 (EJHG) compares seven LLMs with Exomiser on 5,213 phenopackets, but reports per-model values only in text and figures, and ranks diseases rather than genes or variants.

## Evidence summary

Final text for the use case's `summary` claim (source IDs `rare-ranking-20261009-source-yuan2022-sm-table-3`, `rare-ranking-20261009-source-yuan2024`, `rare-ranking-20261009-source-kafkas2025`). This is reviewed text for a later claim; no summary record was added in this batch.

> Two studies from one clinical laboratory group measured how often each tool ranks the known causal gene of a solved exome case within the top 1 to top 50 genes; the values are transcribed, not reproduced, and none of these authors developed a compared tool. With default settings in singleton mode on 305 solved DDD cases (Yuan et al. 2022), the causal gene was within the top 10 for 86.2% of cases with AMELIE, 83% with LIRICAL, 73.1% with Xrare, 53.1% with Exomiser 12.1.0 and 41.6% with PhenIX; tools given phenotype terms without the variant calls reached at most 14.4%. In the later study on the same cases (Yuan et al. 2024), singleton runs with newer versions reached 87.9% with Exomiser 13.1.0 using REVEL and MVP, 85.9% with AMELIE and 83.3% with LIRICAL. Adding the parents' data (trio mode) gave 91.1% with Exomiser and 91.8% with PhenIX, and Exomiser ranked the causal gene first in 61.6% of cases. The authors chose the trio and AMELIE settings on these same cases, and only solved cases with a single causal gene were scored, so these rates are likely higher than for new or unsolved cases. AMELIE draws on the published literature, and 156 of the 305 DDD cases are published. In Kafkas et al. 2025 the causative gene was hidden among randomly chosen genes rather than a real exome variant list: in the PAVS set with 25 candidates, GPT-4 with the authors' prompts ranked it first in 75.4% (zero-shot) and 77.8% (one-shot) of cases, against 65.6% for Exomiser gene scores, and with 100 candidates in 56.4%, 57.8% and 58.6%. Ranking does not establish pathogenicity or a diagnosis, singleton and trio results must be compared separately, results from different studies must not be pooled, and none of these figures is clinical validation.

| Number in the text | Record ID (prefix `rare-ranking-20261009-`) |
| --- | --- |
| 305 | `data-ddd-305-solved` (`patient_count`) |
| 86.2, 83, 73.1, 53.1, 41.6 | `result-yuan2022-ddd-amelie-top10`, `-lirical-top10`, `-xrare-top10`, `-exomiser-top10`, `-phenix-top10` |
| 14.4 | `result-yuan2022-ddd-amelie-hpo-top10` (the highest of the five HPO-only top-10 values: 7.9, 6.9, 2.3, 8.5, 14.4) |
| 12.1.0, 13.1.0 | `config-yuan2022-exomiser`, `config-yuan2024-exomiser-protocol-b` (`version`) |
| 87.9, 85.9, 83.3 | `result-yuan2024-ddd-exomiser-protocol-b-top10`, `-amelie-protocol-b-top10`, `-lirical-top10` |
| 91.1, 91.8, 61.6 | `result-yuan2024-ddd-exomiser-protocol-d-top10`, `-phenix-protocol-d-top10`, `-exomiser-protocol-d-top1` |
| 156 of the 305 | `claim-yuan2022-amelie-published-cases` |
| 25 candidates: 75.4, 77.8, 65.6 | `result-kafkas2025-pavs-gpt-4-zero-shot-size25-hits1`, `-gpt-4-one-shot-size25-hits1`, `-exomiser-12-1-0-size25-hits1` |
| 100 candidates: 56.4, 57.8, 58.6 | `result-kafkas2025-pavs-gpt-4-zero-shot-size100-hits1`, `-gpt-4-one-shot-size100-hits1`, `-exomiser-12-1-0-size100-hits1` |
| 2022, 2024, 2025; top 1 to top 50; top 10; 1 | Publication years and the stated rank range, not measurements |

Changes from the collector's draft in `coverage.json`:
- The draft compared trio-mode Exomiser and PhenIX Protocol D with singleton AMELIE and LIRICAL in one sentence. They are now in separate sentences by mode.
- The draft said "none of the compared tools was developed by the authors". That does not hold for the GPT-4 prompts.
- The draft gave KMCGD values, but KMCGD is now proxy and is left out.
- The draft did not say that only solved single-gene cases were scored.

## Remaining gaps

- No top-k ranking on unselected or unsolved cohorts, no review workload per case, and no LLM on real exome candidate lists.
- Figures were not read: Yuan et al. 2024 Figure 2 (the C and D option tables) and Yuan et al. 2022 Supplementary Figure 2 (the unpublished DDD subset).
- Supplementary tables were not read: Kafkas et al. S5 and S6 (other Exomiser algorithms) and Yuan et al. 2022 SM Tables 1, 2 and 4.
- Leads not screened for tables: PhEval, Kim et al. 2024, the Genome Med 2025 Exomiser optimisation, and Front Genet 2026.
- `npm test` (499 passed) and `npm run typecheck` passed. `npm run build` was not run, by instruction; the dry run stands in for the store checks.
