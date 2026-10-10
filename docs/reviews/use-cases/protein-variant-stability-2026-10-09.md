# Protein variant stability: independent review of the 2026-10-09 batch

Batch: `data/omics/use-case-coverage-protein-stability-20261009/` (651 records). Use case: `use-case-protein-stability`.

Reviewer: a separate Claude review agent that did not extract the batch. No human review is claimed. Nothing was executed or reproduced. This review checks the transcription against the pinned sources and judges the relevance claims.

## Outcome

- All three article XMLs re-download to the pinned SHA-256, and the three archived `artifacts/*.gz` decompress to the same bytes.
- All 427 results match their table cells: Pancotti 231, Dieckhaus 147, Chu 49. No number was wrong, every printed footnote marker is kept, and every result links to the right configuration and protocol.
- One compiled value conflicts with the source it cites: the ACDC-NN S669 RMSE of 1.60 in Dieckhaus Table 3. That result is now `disputed`. The other 426 are `source_checked`.
- Four Pancotti evaluations are corrected to `author_reported`, and two Dieckhaus ProteinMPNN evaluations to `independent_paper`.
- Eight evaluations are excluded from three judgements, with reasons:
  - six homologue-inflated Fireprot rows;
  - ABYSSAL on filtered S669;
  - ESM therm on the mega-scale set.
- All 12 judgements hold with the grades the collector gave: 4 direct and 8 proxy. Each is `source_checked`, with `reviewed_evaluations` and a review filled in. Pins are left unset.
- Simulation: I added the reviewed batch to an in-memory copy of the store, applied the use-case changes below and computed pins. All 15 judgements on the use case then derive as active: the 12 new ones and the 3 existing ones.

## How the check was done

1. Downloaded each Europe PMC full-text XML into an empty directory and hashed it. Decompressed the archived copies and hashed them.
2. Parsed every `table-wrap` with a parser written for this review, keeping header spans, row labels and footnote markers. The extractor's script was not run.
3. Built the expected cell for every result from the table headers:
   - Pancotti: method row, and the group (total, direct, reverse or antisymmetry) and metric column;
   - Dieckhaus: method row, and dataset and metric column;
   - Chu: dataset row and method column.

   Then compared printed value, numeric value, footnote marker and warning, metric, unit, and the configuration and protocol of the linked evaluation. Every expected cell has exactly one result; the only cells without a result are the three blank ABYSSAL RMSE cells.
4. Read the cited Methods, Results and Discussion paragraphs and the reference lists to check origins, splits, comparator provenance and the collector's concerns.
5. Loaded the reviewed batch against the current store in memory with `recordSchema`, `validateVocabularies`, `validateAttributes` and `validateRecords`. Then ran `deriveUseCaseInputs` with the approved use-case text and computed pins. Nothing was written to the store.

## Sources and hashes

| Source | Pinned SHA-256 | Re-download | Archive |
| --- | --- | --- | --- |
| `protein-stability-20261009-source-pancotti2022` (PMC8921618) | `13203808...0024` | Match | Decompresses to it |
| `protein-stability-20261009-source-dieckhaus2024` (PMC10861915) | `ba9a763c...8010` | Match | Decompresses to it |
| `protein-stability-20261009-source-chu2024` (PMC11293664) | `bb9830cb...914f` | Match | Decompresses to it |

## Values checked

| Table | Cells | Matched | Notes |
| --- | --- | --- | --- |
| Pancotti Table 1 (21 methods by 11 columns) | 231 | 231 | Printed precision kept, for example MAESTRO reverse MAE `1.655` |
| Dieckhaus Table 2 (12 by 6) | 72 | 72 | 18 cells carry `*`, 12 cells (RaSP, PROSTATA rows) the `†` label |
| Dieckhaus Table 3 (13 by 6, three blank) | 75 | 75 | `*` on ThermoMPNN S669, `†` on ABYSSAL S669 |
| Chu Table 1 (7 datasets by 7 methods) | 49 | 49 | Length column and Table 2 used for dataset records |
| Total | 427 | 427 | |

`research.md` gives 130 Dieckhaus results and 66 Chu results; the batch correctly holds 147 and 49.

## The collector's concerns

- **ACDC-NN S669 RMSE, 1.60 against 1.49.**
  - The original source is Pancotti et al. 2022: S669 is their dataset and they ran ACDC-NN on it. Their Table 1 prints ACDC-NN direct RMSE 1.49, total 1.5 and direct Pearson 0.46.
  - Dieckhaus Table 3 prints 1.60 and 0.46 and cites "(30, 36)". Reference 30 is Pancotti et al.; reference 36 is an unrelated 2006 paper on amino-acid pair frequencies.
  - The Pearson matches, and 1.60 is exactly the direct RMSE of DDGun3D on the next row of Pancotti Table 1. So 1.60 looks like a transcription slip in Dieckhaus.
  - Every other S669 value in Dieckhaus Table 3 matches the Pancotti direct-variant columns: Rosetta 2.70 and 0.39, ThermoNet 1.62 and 0.39, MAESTRO 1.44 and 0.50, FoldX 2.30 and 0.22, mCSM 1.54 and 0.36, MUPRO 1.61 and 0.25.
  - Decision: each value stays against its own source. The Pancotti 1.49 is `source_checked`. The Dieckhaus 1.60 is `disputed`, with a `source_warnings` entry giving the cited value and the DDGun3D match, so it is never shown as evidence. The Dieckhaus ACDC-NN S669 evaluation keeps its checked Pearson 0.46.
- **Footnote markers.**
  - Table 2 `*` (Fireprot columns of ACDC-NN, ACDC-NN-Seq, ThermoNet, MAESTRO, mCSM, MUPRO): "Score may be inflated due to the presence of close homologues (>25% sequence identity) of Fireprot proteins in the training dataset". These rows are not homologue-free results, so I excluded those six evaluations from the Fireprot homologue-free judgement with reasons. Their Megascale cells are unmarked and stay in.
  - Table 2 `†` (RaSP, PROSTATA): retrained on Megascale, which the configurations record.
  - Table 3 `*` (ThermoMPNN S669): trained on a homologue-filtered Megascale set. Kept, with the warning.
  - Table 3 `†` (ABYSSAL S669): scored on 420 of 669 variants. Excluded from the S669 judgement.
  - Every marked cell keeps the marker in `printed_source_cell` and its meaning in `source_warnings`.
- **Pancotti versions.** I did not fetch the supplement. Tool identity is clear from the names and the reference list, and versions are recorded as unextracted. No identity question depends on them.
- **Chu Table 1 mismatched row.** The caption says every method is scored on point mutations only, "except our pLM on the mega-scale dataset". So ESM therm's mega-scale 0.65 is not matched with the other six values. I excluded `eval-chu2024-esm-therm-mega-scale` from the mega-scale judgement with that reason. Its result stays recorded and checked.
- **MAESTRO's bias.** Confirmed: highest direct Pearson (0.5), reverse Pearson 0.2, bias -0.57. Pancotti et al. group it with the non-antisymmetric tools that perform "remarkably worse for the reverse variants". This is now a limitation on the Pancotti protocol and judgement: ranking by direct correlation alone misleads.
- **Origin per row.**
  - **ThermoMPNN, ESM therm:** `author_reported`. Correct.
  - **ACDC-NN, ACDC-NN-Seq, DDGun, DDGun3D (Pancotti):** `author_reported`. Correct; the authors developed them (references 31, 32, 33).
  - **INPS3D, INPS-Seq, I-Mutant3.0, I-Mutant3.0-Seq (Pancotti):** corrected from `independent_paper` to `author_reported`. Pancotti authors P. Fariselli and E. Capriotti are authors of INPS-MD (reference 47) and I-Mutant (references 20, 48).
  - **ProteinMPNN in Dieckhaus Table 3:** corrected from `author_reported` to `independent_paper`. Its developers (Dauparas et al.) are not among the Dieckhaus authors, and Table 2 already records it that way.
  - **Comparators in the two developer papers:** stay `independent_paper`. Each now carries the limitation "Run as a comparator by the ThermoMPNN developers" or "by the ESM therm developers".
  - **Pancotti's other comparator rows:** carry a note that the authors develop several competing tools.
  - **Dieckhaus Table 3 rows cited from other papers:** stay `paper_compilation`.

## Extractor provenance

The collector reports two things about the extractor. It was interrupted while being written and finished in pieces. Despite that, rerunning `extract/extract_protein_stability.py` on the archived artifacts reproduces `batch.jsonl` and `claims.csv` byte for byte, and a separate check matched all 427 cells. Only the extractor's limitations prose for the Dieckhaus Ssym and S669 protocols was rewritten by hand.

This review did not rely on any of that. I did not run the script. Every one of the 427 cells was checked with this review's own parser (see How the check was done).

After this review's edits, rerunning the script no longer reproduces `batch.jsonl` or `claims.csv`. The receipt binds the reviewed bytes.

I checked the two rewritten limitations lists against Table 3, its footnotes and the Results text.

- **`protocol-dieckhaus2024-s669`:**
  - "Most rows are compiled from Pancotti et al. 2022 (reference 30)": correct. Seven of the eleven compiled S669 rows cite reference 30 (Rosetta, ThermoNet, ACDC-NN, MAESTRO, FoldX, mCSM, MUPRO), and each matches Pancotti's direct-variant columns except the ACDC-NN RMSE. RaSP, Stability Oracle, PROSTATA and ABYSSAL cite their own papers.
  - The footnote entry (ThermoMPNN trained on a filtered set; ABYSSAL on 420 variants): correct.
  - The ACDC-NN entry was correct. It is extended here with the DDGun3D match and the stray reference 36.
  - "No uncertainty is printed": correct.
- **`protocol-dieckhaus2024-ssym`:**
  - "Compiled from references 29 and 30 and the methods' own papers": correct as a description of the printed citations.
  - Reference 30, Pancotti et al., prints no Ssym values in its main tables, so the Ssym cells attributed to it could not be checked here.
  - "Variant counts are not printed in Table 3": correct. The 342 is in the Results text.
  - "No uncertainty is printed": correct.
  - One entry was missing and is now added to the protocol and the Ssym judgement. The Results text says homologues of both Ssym and S669 were removed from the Megascale training set before ThermoMPNN was retrained, but only the S669 ThermoMPNN cells carry footnote `*`. It is not stated whether the Ssym values use the filtered model.

## Other corrections

| Record | Change |
| --- | --- |
| 21 Pancotti antisymmetry correlations | `metric_direction` from `unknown` to `lower`. Perfect antisymmetry is -1, so lower is better; the qualifier says so. |
| Seven ESM therm results, `claims.csv` | Locator column name corrected to the printed `ESMtherm` |
| Datasets, protocols, judgements, qualifiers, `coverage.json` | XML subscript spacing removed: "(T m )" to "(Tm)", "(T 50 )" to "(T50)" |
| Chu protocols and judgements | The Rosetta limitation said Rosetta "was run on only six ProteinGym datasets plus BglB", but Table 1 prints Rosetta for all seven rows. It now says the larger-protein benchmark was limited to those seven datasets because of Rosetta's compute cost (Methods P25). |
| Chu single-protein judgements | Added: the Results text ranges (ELASPIC-2 0.42 to 0.58; Rosetta 0.33 to 0.48) do not match Table 1; the table is followed |
| `data-chu2024-bgl3` | Length conflict noted: Table 2 and Discussion 501, Table 1 510 |
| `data-chu2024-acetyltransferase`, `-lipase-esta` | Results P15 swaps their assay types relative to Table 2 and Methods P25; Table 2 followed |
| Chu mega-scale judgement | ESM therm removed from the endpoint text; added that the paper does not say who produced comparator scores on that set |
| Dieckhaus Fireprot protocol, dataset, judgement | The limitation "pooled metrics are dominated by a few proteins" was wrong for the homologue-free split, because the three proteins with more than 250 measurements were kept in training. Now states the split's 89 proteins and 2,578 mutations. |
| Dieckhaus Ssym judgement | Rationale copied the S669 text; rewritten |
| Pancotti protocol and judgement | Developer list extended; MAESTRO limitation added |

## Model reuse and links

- `discovery-model-esm-2` and `discovery-model-proteinmpnn` are family-level model records with status `discovered`. The store already links 24 configurations to `discovery-model-esm-2` with `configuration_of`.
- Linking the two unsupervised ESM-2 checkpoints (35M, 3B) and the ProteinMPNN baseline the same way is correct. Their results are results of those exact configurations.
- ESM therm (fine-tuned from ESM-2 35M) and ThermoMPNN (a stability head on ProteinMPNN embeddings) link `configuration_of` to their own method records and `uses_model` to the base family. That is correct: the record contract says `uses_model` records a dependency "and does not assign its result to the base model". So neither model's scores roll up to ESM-2 or ProteinMPNN.

## Metric concept `antisymmetry-bias`

Accepted:
- The definition matches Pancotti et al. section 2.3, where the bias is the average predicted ddG over the balanced direct and reverse set, zero for an unbiased antisymmetric predictor.
- The unit is kcal/mol, as the Table 1 caption states.
- `unknown` is the right default direction, because the ideal is zero, not an extreme.

Optional: a `skos:scopeNote` saying "Ideal value is zero; in Pancotti et al. 2022 negative values indicate bias towards destabilising predictions" would help readers. I did not edit the vocabulary file.

## Judgements

| Judgement | Grade | Fit | Reviewed | Excluded |
| --- | --- | --- | --- | --- |
| `pancotti2022-s669` | direct | Experimental ddG on proteins under 25% identity to the main training sets, with reverse variants | 21 | 0 |
| `dieckhaus2024-megascale` | direct | Held-out homology clusters of the proteolysis ddG set | 12 | 0 |
| `dieckhaus2024-fireprot` | direct | Experimental ddG on a homologue-free split | 6 | 6 (homologue-inflated, `*`) |
| `dieckhaus2024-ssym` | proxy | Mostly compiled values; Ssym direct and inverse | 13 | 0 |
| `dieckhaus2024-s669` | proxy | Mostly compiled from Pancotti; adds ThermoMPNN on S669 | 12 | 1 (ABYSSAL, 420 variants) |
| `chu2024-mega-scale` | direct | Held-out mega-scale domains, folding stability | 6 | 1 (ESM therm, unmatched variant set) |
| `chu2024-bglb`, `-bgl3`, `-acetyltransferase`, `-lipase-esta`, `-pten`, `-methyltransferase` | proxy | Single larger proteins; endpoints are Tm, T50, heat-shock activity, chemical stability or abundance, not folding ddG | 7 each | 0 |

- **Direct against proxy.** The use case asks which evidence supports ranking substitutions by folding stability.
  - The four direct strata measure folding ddG or proteolysis stability on proteins held out from training.
  - The two Dieckhaus Table 3 strata are proxy because most rows are compiled, not run on matched inputs.
  - The six Chu single-protein strata are proxy because their readouts are stability-related but not folding ddG, and each is one protein.
  - None of the Chu endpoints is organismal fitness or a clinical label, so the exclusion on whole-protein function still holds.
- **Grouping.** Three comparison groups (Pancotti S669; Dieckhaus; Chu transfer), with strata in a sensible order and headline metrics present among each group's results. The Pancotti group's `pearson-correlation` headline covers total, direct, reverse and antisymmetry values, which the qualifiers separate.

## Approved use-case changes

This is the exact text to apply to `use-case-protein-stability`. Fields not listed stay unchanged: `name`, `description`, `question`, `inputs`, `intended_users`, `facets`, `search_terms`, `collection_plan` and `planned_work`.

The current `exclusions` include "Generalisation to other proteins, other ESM-2 checkpoints or the full ProteinGym track", and `setting` says the evidence "is limited to the 47-residue AMFR... construct". Both contradict the 12 new judgements, so they must change.

### `decision`

```json
"Inspect per-method correlation and error on held-out or dissimilar proteins, the antisymmetry of predictions on reverse variants and the change from small domains to larger proteins, with the AMFR assay results as a narrow example, then identify the comparison and validation still required for the target protein and endpoint."
```

### `output`

```json
"Per-method correlation, error and antisymmetry values from the linked comparisons, each with its dataset, split and origin, and the exact existing AMFR configurations with their assay scope; unresolved comparisons are listed. No universal model ranking or pathogenicity prediction."
```

### `setting`

```json
"The AMFR evidence is the 47-residue AMFR_HUMAN_Tsuboyama_2023_4G3O construct in ProteinGym v1.3. Its cDNA-display proteolysis assay infers folding stability. Completed evaluations cover 2,972 variants: 820 single and 2,152 double substitutions. Published comparisons add single-point stability benchmarks on held-out or dissimilar proteins (S669, homology-split mega-scale and FireProtDB sets, held-out mega-scale domains) and six single-protein stability datasets of 177 to 501 residues."
```

### `exclusions`

Replace the whole list with:

```json
[
  "Whole-protein function, cellular activity, organismal fitness and clinical pathogenicity",
  "Transfer of a benchmark result to a different target protein, protein size or assay without validation on that protein",
  "Treating the existing mixed cohort as a completed matched single-substitution comparison"
]
```

### `clinical_scope`

```json
"Clinical applicability is not established. Stability prediction on benchmark proteins or on a short experimental construct is not evidence of clinical pathogenicity or suitability for diagnosis or treatment."
```

### `evidence_gaps`

Keep the ten existing entries and append these seven, which are the collector's list corrected. PROSTATA was rerun in Dieckhaus Table 2, so it is not "compiled only".

```json
[
  "Both mega-scale comparisons are developer papers (ThermoMPNN, Dieckhaus et al. 2024; ESM therm, Chu et al. 2024); no independent comparison on the mega-scale proteolysis set with printed per-method values was found.",
  "None of the new comparisons reports a result for the AMFR construct of the existing judgements.",
  "Only Pancotti et al. 2022 tests antisymmetry across many tools, and its authors developed several of them; Dieckhaus et al. 2024 report Ssym inverse variants from compiled values, and Chu et al. 2024 do not test it.",
  "Transfer to larger proteins is tested only by Chu et al. 2024, on six single proteins of 177 to 501 residues with Spearman correlation only.",
  "No linked comparison reports uncertainty intervals for per-method values; Dieckhaus et al. 2024 Table 1 gives seed standard deviations for ThermoMPNN and ProteinMPNN only.",
  "Stability Oracle and ABYSSAL appear only as values compiled from their own preprints (Dieckhaus et al. 2024 Table 3), not as reruns.",
  "Dieckhaus et al. 2024 compile an ACDC-NN S669 RMSE (1.60) that disagrees with the source they cite (Pancotti et al. 2022: 1.49); the compiled value is not shown."
]
```

### `links`, `source_ids` and `citation_locators`

- Add the 12 `assessed_by` links listed in `coverage.json` `use_case_changes.add_links`, keeping the three existing links.
- Add the three source IDs. All are clean and hash-verified.
- Add these citation locators:

```json
[
  {"source_id": "protein-stability-20261009-source-pancotti2022", "locator": "Section 2 (S669, reverse variants, antisymmetry indices); Table 1"},
  {"source_id": "protein-stability-20261009-source-dieckhaus2024", "locator": "Results on data splits and literature comparison; Tables 2 and 3 with footnotes"},
  {"source_id": "protein-stability-20261009-source-chu2024", "locator": "Results on larger proteins; Methods P25; Tables 1 and 2"}
]
```

### The three existing judgements under the new text

All three still hold:
- `use-case-mapping-20260930-337-fa51fe46268a` is the official AMFR assay-level Spearman.
- `use-case-mapping-protein-stability-amfr-esm2` is ESM-2 8M on the mixed AMFR cohort.
- `use-case-mapping-protein-stability-amfr-random` is the fixed-seed random control.

The new `setting` keeps the AMFR description word for word. The new `decision` keeps AMFR "as a narrow example", and the new `output` keeps "the exact existing AMFR configurations with their assay scope". The third exclusion, which their limitations rely on, is unchanged. Their own rationales already say the AMFR cohort does not establish transfer to another protein, which matches the new second exclusion. None of their endpoints, constraints or limitations depends on the removed wording.

These fields are pinned, so applying the text withholds all three until they are re-pinned. In the simulation the only changed pin was the use case's, and after re-pinning all three derive as active. Re-pin them with the 12 new judgements and the summary claim against this review.

## Final summary text

> Three published comparisons add evidence beyond the AMFR assay. Each uses its own dataset, split and metric, so values cannot be pooled. Pancotti et al. 2022 ran 21 predictors on S669, 669 experimental ddG variants in proteins dissimilar to the main training sets, plus their reverse variants; several of the tools, including ACDC-NN, DDGun, INPS and I-Mutant, were developed by the paper's own authors. The highest Pearson correlation on direct variants was 0.5 (MAESTRO), but MAESTRO fell to 0.2 on reverse variants with a bias of -0.57, while tools built to be antisymmetric, such as INPS-Seq, kept 0.43 in both directions with a bias of 0. On all 1,338 variants the highest correlations were 0.62 (PremPS) and 0.61 (ACDC-NN and INPS-Seq). Dieckhaus et al. 2024, the ThermoMPNN developers, held out proteins clustered at 25% identity in the mega-scale proteolysis set: ThermoMPNN reached Pearson 0.75 and RMSE 0.71 kcal/mol, retrained RaSP 0.71 and Rosetta 0.53 with RMSE 5.18. On a homologue-free FireProtDB split ThermoMPNN reached 0.65 against 0.59 for retrained PROSTATA and 0.47 for retrained RaSP. Chu et al. 2024, the ESM therm developers, show the limit of transfer: on held-out mega-scale domains of 40 to 72 residues RaSP and ELASPIC-2 reached Spearman 0.64 and Rosetta 0.61, but on six single proteins of 177 to 501 residues their fine-tuned model scored between -0.11 and 0.06, while ELASPIC-2 scored 0.47 to 0.58 on five of them and Rosetta 0.33 to 0.49. Before choosing a method, a user still needs to validate transfer to proteins larger than the small domains these models were trained on, and to check antisymmetry on reverse variants, which only one of these comparisons tests across many tools. None of the comparisons covers the AMFR construct, and none establishes whole-protein function, fitness or pathogenicity.

Every number is a `source_checked` result in this batch, or a dataset count printed in a source:

- **Pancotti Table 1:**
  - MAESTRO direct r, reverse r and bias;
  - INPS-Seq direct r, reverse r and bias;
  - PremPS, ACDC-NN and INPS-Seq total r.

  The 669, 1,338 and 25% figures are from Section 2.
- **Dieckhaus Table 2:**
  - Megascale ThermoMPNN PCC and RMSE, RaSP PCC, Rosetta PCC and RMSE;
  - Fireprot ThermoMPNN, PROSTATA and RaSP PCC (unmarked cells).
- **Chu Table 1:**
  - mega-scale RaSP, ELASPIC-2 and Rosetta;
  - ESM therm, ELASPIC-2 and Rosetta on the six single-protein rows.

  The protein lengths are from Table 2.

The collector's proposal had two numerical errors, corrected above:
- It gave ESM therm's six-protein range as -0.11 to 0.03; Bgl3 is 0.06.
- It said ELASPIC-2 "stayed at 0.47 to 0.58" on six proteins; on BglB it scored -0.11.

## Checks run

- In memory: the reviewed batch (651 records) passes the schema, vocabulary (including `antisymmetry-bias`), attribute and record checks against the current store.
- `npm run typecheck`: exit 0.
- `npm run records -- check`: 30,859 records match their provenance (the batch is not in the store).
- `npm test`: 499 of 499 pass.
- `npm run build`: not run. The batch is not in the store, and the build writes release files outside this review's scope.

## Remaining gaps

- No independent mega-scale comparison was found.
- Pancotti versions and the supplements of all three papers are unread.
- Stability Oracle and ABYSSAL are compiled only.
- No source gives per-method uncertainty.
