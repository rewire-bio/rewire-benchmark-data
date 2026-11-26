# Review of the slice grounding (ClinVar and BRCA1)

Reviewed against BRIEF.md, using only the input fields in clinvar-brca1.json and the output in grounding.jsonl. ground.py was not read or run.

## Counts

- Lines checked: 472 of 472. Every observation in the input has exactly one line in grounding.jsonl, and no extra lines.
- Method: the lines were grouped by study and by the full set of system fields (127 distinct combinations), then by study, setting and locator panel for subsets. I read every combination. Cross-tabs: system_key against adaptation and against root_name, and subset against study within each setting.
- Lines with an error: 48 (10.2%). No line has more than one error.

| Field | Lines with an error | Rate |
|---|---|---|
| system_key | 23 | 4.9% |
| adaptation | 6 | 1.3% |
| subset | 19 | 4.0% |

An error here means the value contradicts a field or a rule in the brief. Choices I would have made differently but that the brief allows are listed under "Policy issues" and are not counted. They affect a further 137 lines: the ClinGen strength-as-subset choice (108) and the Evo 2 paper baseline adaptations (29).

Every proposed change is in grounding-review.jsonl.

## Errors found

1. **AlphaGenome API keys without `-unspecified` (23 lines, Lu et al.).** parameters_text names only the "Official AlphaGenome API". It gives no model version or release. The scorer variant (quantile or raw, which outputs, maximum or composite) is pinned correctly, but the brief requires `-unspecified` when the version is not stated. The same agent gave the rewire AlphaGenome AVI rows `-unspecified` on the same kind of evidence, so the family is treated two ways. No comparison depends on this today.
2. **Brandes et al. subset `all` (19 lines).** The assessment name says "variants scored by all 19 eligible methods". That is an intersection, not the source's whole ClinVar missense set, and the agent's own subset_basis says "restricted to variants every...". Proposed: `scored-by-all-19-methods`. This change removes comparison 10.
3. **Rewire AlphaGenome AVI adaptation `zero-shot` (6 lines).** No field says zero-shot. The qualifier gives only the cohort, and the description says only "AlphaGenome Variant Impact PHRED-scaled (or raw) score across GRCh38 missense SNVs". A precomputed table is likely, since PHRED scaling needs a genome-wide score set and every other system in this run is a lookup, but the fields do not say so. Proposed: `unspecified`.

What checked out:
- Every pinned size, version and scoring variant (Evo 2 7B/40B and base, ESM checkpoints, Caduceus, HyenaDNA, NT v2 500M and 2.5B, DNABERT-2 117M, phyloP 100/241/447/470, CADD v1.3 and v1.7 with PHRED or raw, REVEL v1.3, GPN-Star m447 and v100, dbNSFP 4.3a) is stated in system_name, system_version, system_checkpoint or parameters_text.
- Every other `-unspecified` key matches a field that says "not stated" or names no release.
- The ablation keys keep apart the "Window size = 256" retraining and the inference-window rows correctly.
- No key spans two root families.
- The rewire cohort subsets match the JSON pointers, and the Lu et al. and PhyloGPN Table 1 subsets match their panel and row labels.

## Policy issues (not counted as errors)

1. **One key, two adaptations.** `phylop-100way`, `cadd-unspecified` and `alphamissense-unspecified` are `zero-shot` in the Evo 2 paper and `precomputed-scores` elsewhere. The agent's rule is defensible: it used `precomputed-scores` when a field names a score source (dbNSFP, UCSC, a lookup) and otherwise fell back to the paper's "zero-shot" qualifier. The Evo 2 paper rows name no source. The same applies to SpliceAI, Pangolin and GPN-MSA in that paper (29 lines in all). If adaptation should be a property of the system, a human should set non-learned conservation scores and score tables to `precomputed-scores` throughout.
2. **`-unspecified` keys are shared across studies.** `cadd-unspecified` covers the Evo 2 paper (whose description says v1.7, though parameters_text says not stated) and Pejaver et al. 2022. `alphamissense-unspecified` covers the Evo 2 paper, the rewire run and Bergquist et al. By construction, such a key can mean two different releases. No comparison uses one now, apart from the ClinGen reprints, which are the same calibration. The comparison rule should skip `-unspecified` keys, or those keys should be scoped to a study.
3. **ClinGen evidence strength stored as subset (108 lines).** The number is a threshold for a strength, computed on the whole calibration set. Strictly, the strength is part of the metric, not a part of the data. The choice is pragmatic, because it keeps strengths from being compared with each other. A related point: `pp3-moderate` and `bp4-moderate` name different intervals in the two papers. Pejaver's Moderate spans what Bergquist splits into 2 and 3 points, and BP4 Strong in Bergquist includes Very Strong. The stored threshold that reaches each level is the same concept in both, so the 22 agreements stand.
4. **Uneven class matching between PhyloGPN Table 1 and Lu et al.** 'Stop Lost' was merged with 'Stop loss', but 'Start Codon' was kept apart from 'Start loss' and 'Intronic' apart from 'Intron (Non-splice)'. Each choice can be argued; together they are inconsistent.
5. **BRCA1 strata stored as `all`.** This is correct by the setting definitions. But the rewire run defines coding as missense, nonsense and synonymous, and the Evo 2 paper's 'Coding' Genomic_Feature is undefined. The agent noted this, then still called comparisons 11 and 13 real disagreements.
6. **`varity-r-loo` and `phylogpn` carry no `-unspecified`.** Each is acceptable. VARITY_R names a specific leave-variant-out score set. PhyloGPN states its 481 bp receptive field and about 83M parameters, although the key does not carry the size.
7. **Evo 2 scoring variant.** The rewire rows state the scoring (mean log-likelihood difference over an 8,192 bp window). The Evo 2 paper rows do not. Every other scored model carries `-llr` or a similar suffix where it is stated, so `evo-2-7b` may join two scoring variants.

## Keys that mean two things, or one thing under two keys

- `cadd-unspecified`: the Evo 2 paper's CADD (possibly v1.7) and Pejaver et al.'s CADD (2022, so not v1.7). They may be two releases.
- `alphamissense-unspecified`: three studies with no release stated. They are probably one thing, but the fields do not show it.
- `evo-2-7b`: one checkpoint, but possibly two scoring procedures (see policy issue 7).
- `ablation-gpnstar-st3-gpn-msa-exclude-10-closest-species` and `ablation-gpnmsa-st4-default` may be one configuration under two keys. The agent flagged this; the fields do not settle it.
- `evee-covariance-probe-evo-2-7b-l27` and `evee-unspecified` (the rewire ClinVar-supervised control) may be the same deployed probe. The rewire description does not say, so separate keys are right.
- No case found where the fields prove that one released system sits under two keys.

## The 13 comparisons

A useful control: Lu et al. and the PhyloGPN paper both use the same published GPN-MSA hg38 precomputed score file. On identical variants, the same file must give the same AUROC, so any `gpn-msa-llr` gap measures the difference between the two cohorts and class definitions. GPN-MSA agrees on missense (0.906 against 0.91), is close on synonymous (0.882 against 0.87), and differs by 0.05 on 3' UTR and 0.22 on 5' UTR. On the Evo 2 rows, the rewire H100 and L40S runs differ by 0.002 to 0.003, which sets the noise floor for re-running.

| # | Case | Verdict |
|---|---|---|
| 1 | phylogpn, 5' UTR, 0.601 vs 0.94 | Artefact. GPN-MSA differs by 0.22 on the same class, so the two 5' UTR sets are different cohorts. Lu's set has N=2,471 with 2.38% pathogenic. The extra 0.12 cannot be separated from the cohort effect. |
| 2 | gpn-msa-llr, 5' UTR, 0.728 vs 0.95 | Artefact. The score file is the same, so the whole gap comes from the variant set or class definition, or from a misread value. It is not a model difference. |
| 3 | phylogpn, 3' UTR, 0.765 vs 0.94 | Mostly artefact. GPN-MSA differs by 0.05 on the same class, and Lu's set is 0.21% pathogenic (about 25 variants). The extra 0.12 is a lead on how Lu ran PhyloGPN, not a clean like-for-like result. |
| 4 | phylogpn, stop loss, 0.695 vs 0.81 | Artefact or noise. Lu's set has N=94. GPN-MSA moves 0.03 in the opposite direction. The class match ('Stop Lost' to 'Stop loss') is itself only medium confidence. |
| 5 | gpn-msa-llr, 3' UTR, 0.908 vs 0.96 | Artefact. Same score file, so cohort and class definition, and few pathogenic variants. |
| 6 | phylogpn, synonymous, 0.806 vs 0.85 | Plausibly genuine. The GPN-MSA control is within 0.012, in the opposite direction, so the cohorts look comparable. The remaining gap points to how PhyloGPN was run: Lu used the repository's example notebook. Lu's set is 0.66% pathogenic, so there is some noise. |
| 7 | phylogpn, missense, 0.799 vs 0.84 | Genuine, and the strongest case. The GPN-MSA control agrees within rounding on N=50,820. Same released model, comparable cohorts, so the 0.04 gap lies in the scoring pipeline (example code against the authors' own). |
| 8 | evo-2-7b, BRCA1 all SNVs, 0.904 vs 0.875 | Genuine difference, but probably between scoring procedures rather than checkpoints. The gap is ten times the platform noise. It is larger than in either stratum and changes sign between strata. That pattern fits a difference in score scale between coding and noncoding variants (window or normalisation), not a different checkpoint. The paper's scoring method is not in the fields. |
| 9 | gpn-msa-llr, stop loss, 0.888 vs 0.86 | Artefact. Same score file, and N=94 in Lu. |
| 10 | esm-1b-650m-llr, missense, 0.892 vs 0.919 | Artefact. Brandes reports the intersection of variants scored by all 19 methods; Lu reports its whole missense set (N=50,820) with the same pipeline. These are different variant sets. It disappears once the Brandes subset is corrected. |
| 11 | evo-2-7b, BRCA1 coding, 0.823 vs 0.840 | Unresolved. The rewire run is higher here, while it is lower overall. The rewire coding definition (missense, nonsense, synonymous) may differ from the paper's undefined 'Coding'. The fields give no N for either. Check the definitions before reading this as a model difference. |
| 12 | gpn-msa-llr, synonymous, 0.882 vs 0.87 | Artefact, and trivial. Same score file, and only 0.007 beyond rounding. |
| 13 | evo-2-7b, BRCA1 noncoding, 0.959 vs 0.953 | Effectively agreement. The gap is about twice the platform noise and well within what the definition or scoring differences could cause. |

Summary: 2 genuine like-for-like differences (7, and 6 more weakly), 1 genuine difference that is probably between scoring procedures (8), 8 artefacts (1, 2, 3, 4, 5, 9, 10, 12), and 2 unresolved or negligible (11, 13). The first agent concluded that "all 13 differences are real disagreements about the same checkpoint on similar data". That is wrong for the four GPN-MSA cases, where an identical score file cannot disagree with itself on the same data. It also conflicts with the agent's own note 11 on the BRCA1 strata.

## Data points for a human (not grounding errors)

- The rewire Google Cloud H100 observations (the `p2` result ids) point at `/brca1_evo2_vs_baselines/...`, and their values equal the Runpod H100 `/platforms/P3/...` values to 16 digits. The baselines block was probably produced by the P3 run, so the P2 rows may be mislabelled. In the comparisons table they also look like two independent values.
- Bergquist et al. ESM1b BP4 (minus 3 points) reads "≥ 8.8", next to Moderate "[−3.1, 8.7]". This is far above the other ESM1b thresholds. Check it against the source table.
