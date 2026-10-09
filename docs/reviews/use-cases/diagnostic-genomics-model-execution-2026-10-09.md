# Diagnostic genomics model execution: independent review of the 2026-10-09 batch

Batch: `data/omics/use-case-coverage-model-execution-20261009/` (639 records). Use case: `use-case-diagnostic-genomics-model-execution`. `batch.jsonl` as extracted: SHA-256 `349345448697a7e592e8ab69d895f132b8318a847afe6f48c5b681e415890ee1`; as reviewed: `0ad04a2dbcc52bf453b489c0c3c7e23196161f24d14ae9c6d950db025c2e5183`. The receipt is `review.json` in the batch folder.

Reviewer: a separate Claude review agent that did not collect or extract the batch. No human review is claimed. Nothing was executed or reproduced; this is a check of transcription and judgement against the pinned sources.

## Outcome

- All five source artifacts re-download to the pinned SHA-256, and the six archived `artifacts/*.gz` decompress to the same bytes.
- All 488 results match their source cells in printed value, numeric value, metric, qualifier, unit, direction, locator, configuration and protocol. No transcription error was found.
- Three results are disputed because the printed value cannot be right: one Samarakoon Table S3c total and two Franzoso Table S2 WGS runtimes. They keep their printed values and are withheld from comparison through `status: disputed` and `source_warnings`. No source-wide evidence concern was raised.
- Descriptive corrections, none of which changes a number, are listed below. The largest is `comparison.budget` on all 91 evaluations.
- The six O'Connell judgements change from `direct` to `proxy`. The other seven stay `direct`. All 13 are now `source_checked` with `reviewed_evaluations` and a review; pins are left unset for the lead.
- The new vocabulary (three metrics, two units) is approved.
- The use-case changes below are approved with edits. They alter pinned fields of `use-case-mapping-amp-20261007-issue18`, which still holds and must be re-pinned in the same change.

## How the check was done

1. Downloaded each `artifact_url` into its own empty directory, unpacked the Europe PMC zips (and the Samarakoon publisher zip inside it) with a stdlib script kept outside those directories, and hashed the named member. Python ran with `-I`.
2. Wrote a new check script (`check.py` in the review scratch area). The extractor's `extract/*.py` were not imported or run.
   - Samarakoon: `pdftotext -layout` (poppler) on the pinned PDF. The script asserts the four S3 sub-table headings, the `Sample CPU L4 A100 H100 DRAGEN` header and ten sample rows per sub-table, reads Table S4 only between its heading and "Supplementary Figures", and reads the coverages in Table S1.
   - O'Connell: `table-wrap id="Tab1"` in the article XML. The script asserts the header and 66 body rows and carries the platform and caller labels down blank cells.
   - Franzoso: the cell XML of `CTS-18-e70416-s002.xlsx`. Number format 21 (`h:mm:ss`) was confirmed in `xl/styles.xml`; durations were converted from day fractions to seconds.
3. Built one expected cell per printed value (dash and `_` cells and the DRAGEN `NA` column in S3 b.2 give none) and matched each result to exactly one cell through its evaluation's configuration and protocol and its sample or column. For each match it compared printed value, numeric value, raw cell value (Franzoso), metric, unit, direction, the locator's row and column labels, and the coverage stated in the Samarakoon qualifier.
4. Recomputed derived values. Samarakoon: every S3c total against read mapping plus HC or GSVC. O'Connell: hours from minutes, fold acceleration as CPU minutes over GPU minutes, % cost-savings as (CPU cost minus GPU cost) over CPU cost, and the hourly rate each printed cost implies.
5. Read the Methods, Results, Discussion, competing-interest and funding statements of the three articles to check versions, hardware, datasets, `missing_metadata`, the two claims and the collector's concerns.
6. Ran the edited batch through `addBatch` from `scripts/omics/records.ts` against a scratch copy of the store (all 639 records accepted with vocabulary and attribute validation; the SHACL step was not run). In the same scratch store I applied the use-case changes below, pinned the claims with `claimPins` and ran `deriveUseCaseInputs`: all 14 judgements become active and the summary is published. Before pinning, issue18 is withheld with "pinned evidence changed since review".

## Sources and hashes

| Source ID | Artifact checked | SHA-256 (re-downloaded 2026-10-09) | Matches record |
| --- | --- | --- | --- |
| `model-execution-20261009-source-samarakoon2025` | PMC12092081 full-text XML | `07e69d06f103dffdc5183eaf63e3e6ca84838c9209117a42fb6b1f96982e43c4` | Yes |
| `model-execution-20261009-source-samarakoon2025-supplement` | `Publication-ready_Supplementary materials-20250404.pdf` in `vbaf085_supplementary_data.zip` | `5fbee07d1a14336e909daf2c6fdd3b26af4c252fae135c033a84c596b2a5d7db` | Yes; inner zip `a828608e...` also matches |
| `model-execution-20261009-source-oconnell2023` | PMC10230726 full-text XML | `1d9c27beb3780a153bc6d80817bf098539e5c605107da0e88f34d6e0d56f3e4f` | Yes |
| `model-execution-20261009-source-franzoso2025` | PMC12627752 full-text XML | `65ddebf128fb41ddf2c2d7d29094871bdeded0ae0c8c4c89acb29884c65f4d38` | Yes |
| `model-execution-20261009-source-franzoso2025-table-s2` | `CTS-18-e70416-s002.xlsx` (and `s001.xlsx`, `b221919e...`) | `0b32a6146536f820e547ed5ac458ae789477358dbfdf339a634a9b78e6c60bd7` | Yes |

Both Europe PMC `supplementaryFiles` requests returned HTTP 200 on the first try (261,303 and 1,698,865 bytes; `testzip` clean).

## Values checked

| Source table | Results | Metrics and units | Mismatches |
| --- | --- | --- | --- |
| Samarakoon S3 a, b.1, b.2, c | 190 | runtime, minute (50 + 50 + 40 + 50) | 0 |
| Samarakoon S4 | 6 | runtime, minute | 0 |
| O'Connell Table 1 | 252 | runtime minute 66, runtime hour 66, compute-cost us-dollar 48, speedup unitless 36, cost-saving percent 36 | 0 |
| Franzoso Table S2 | 40 | runtime second 20, compute-cost us-dollar 20 | 0 |
| Total | 488 | | 0 |

Derived values:

- Samarakoon S3c: 49 of 50 totals equal read mapping plus HC or GSVC within 0.01. The exception is NA12778 on L4 (below). S4's three DV.v4.1.0-1 values equal S3 b.2 H100 for the same samples.
- O'Connell: 186 recomputations. Hours, fold acceleration and % cost-savings agree to rounding except seven small cases, each noted on the result: GCP GPU4 HaplotypeCaller speedup printed 40 (recomputed 40.42); GCP GPU4 Mutect2 speedup 29.3 (29.20); DGX GPU4 LoFreq 1.18 h (1.17); the three AWS GPU LoFreq savings (printed -625.07, -445.68, -628.55; recomputed from the rounded 4.1 USD CPU cost as -622.2, -443.4, -625.6, consistent with the unrounded 4.08 USD); and GCP GPU8 LoFreq -271 (-271.6). None was disputed.
- O'Connell implied hourly rates: AWS CPU 1.36 and GCP CPU 1.75 USD per hour, as the text states. GCP GPU rows imply about 7.4, 14.7 and 29.4 USD per hour. AWS GPU rows imply 12.24 USD per hour for 2 and 4 GPUs and 31.22 for 8 GPUs (see concern 3).
- Franzoso: the eight WGS runtimes not disputed lie inside the Results ranges (Sentieon 3 to 3.8 h, Parabricks 4.1 to 4.7 h), and the exome runtimes and all costs match the Results ranges to rounding.

Observations kept as printed and noted on the results: Samarakoon S3 b.2 prints 465.07 for both NA12891 and NA12892 in the CPU column; O'Connell's AWS GPU2 LoFreq row (145.14 min, 2.42 h, 29.61 USD) nearly repeats the AWS GPU2 DeepVariant row (145.16 min, 2.42 h, 29.61 USD).

## Concerns raised by the collector

1. **Samarakoon S3c, NA12778 on L4, 117.59 min.** Confirmed. Stage values are 26.02 (S3a) and 5.92 (S3b.1), sum 31.94; Results 3.1 paragraph 2 defines the total as that sum, every other total matches, and the other low-coverage L4 totals are 24.68 to 54.29. The correct value cannot be derived, so `model-execution-20261009-result-samarakoon2025-parabricks-4xl4-total-na12778` is disputed with a `source_warnings` entry. Its evaluation keeps nine reviewed results and stays eligible; nothing is excluded from the judgement. The rest of the table is consistent, so no source concern.
2. **Parabricks version.** Confirmed, with a third string the collector missed. Methods 2.3 gives the pipeline as 4.3.0-1. Table S4 calls 4.1.0-1 "the version implemented in our Parabricks pipeline" and 4.3.0-1 "the updated version", and its 4.1.0-1 values equal S3 b.2 H100. The S4 introduction cites the 4.3.1-1 release notes, and Discussion paragraph 10 says the three comparison runs used DV.v4.3.1-1. The three Table S3 Parabricks configurations keep `version` as `conflicting`; the S4 updated configuration keeps `4.3.0-1` as printed in the table, with a `model_identity_note` naming 4.3.1-1. The version claim, the dv-version protocol and judgement limitations, and the summary state the conflict. No value is affected.
3. **O'Connell AWS GPU type.** Confirmed and unresolved. The Table 1 footnote says the AWS rows are p3 (V100) and A100 results are in Additional file 1 Table S1. Results paragraph 2 attributes the Table 1 AWS savings (63% HaplotypeCaller GPU4, 34% DeepVariant GPU4, 53% Mutect2 GPU4, which equal Table 1) to p4 (A100). New evidence from the costs: every AWS GPU cost equals runtime times 12.24 USD per hour (2 and 4 GPUs) or 31.22 (8 GPUs); none uses the 32.8 USD per hour p4d.24xlarge price given in Results paragraph 4, which suggests the costs at least were priced as p3 machines. The runtimes and costs are transcribed correctly, so the 90 AWS GPU results (18 rows, five columns) are not disputed. The three AWS GPU configurations now say the GPU model is unresolved in `hardware.description` and give the cost arithmetic in `model_identity_note`; every result on them carries the same note, and the six O'Connell judgements state it in their limitations. Excluding the AWS GPU evaluations was considered and not done: their values are correct and their identity conflict is stated wherever they are shown.
4. **O'Connell Mutect2 AWS CPU, 16.9 h in the text against 6.91 h in the table.** The table is internally consistent: 414.51 min is 6.91 h, 9.40 USD at 1.36 USD per hour, and the AWS GPU fold accelerations divide 414.51 (414.51 / 28.4 = 14.60). The text figure is likely a typo, but that is not proven. Not disputed; the limitation now gives the arithmetic, and the three AWS CPU Mutect2 results carry a note.
5. **Franzoso WGS cells C13 and C18.** Confirmed. They store 0.0023263889 and 0.0032523148 days, which number format 21 renders 0:03:21 and 0:04:41. Both samples have 44 and 47 GB FASTQ (Table S1); the other WGS runs of the same pipeline take 3:00:00 to 3:50:00 (Sentieon) and 4:06:00 to 4:40:00 (Parabricks); and the Results ranges are 3 to 3.8 h and 4.1 to 4.7 h. The C18 row's cost (10.6 USD) equals that of the 4:40:00 run. Read as hours and minutes, 3:21 and 4:41 fall inside the Results ranges, but that is an inference, so no corrected value is recorded. Both runtime results are disputed with `source_warnings`; the costs on the same rows are kept. Each evaluation keeps nine reviewed results.
6. **Source-wide concerns.** None raised. Each problem is confined to identified cells or to hardware labels, and the rest of each table checks out.
7. **Origin.** `independent_paper` is kept for all 91 evaluations. Samarakoon and Franzoso declare no competing interests and did not develop the platforms. O'Connell's authors are Deloitte Consulting employees, Deloitte funded all aspects of the work and is an NVIDIA, AWS and Google alliance partner; they did not develop Parabricks or the callers, so `author_reported` would be wrong, but the relationship is named in every O'Connell judgement and in the summary.

## Corrections made in the batch

The batch is not yet in the store, so fields were edited in place. Previous values are given here. No ID, link, source list, printed value, numeric value, metric, qualifier, unit, direction or locator of a result changed.

1. All 91 evaluations: `comparison.budget` held each configuration's hardware description (identical to its `hardware.description`). The catalogue refuses a comparison whose evaluations differ in `budget`, so every panel in the batch would have been refused for the very thing being compared, and existing records use `budget` for the execution budget ("one frozen execution per condition"). New values, one per source: Samarakoon "One run per sample and configuration; no fixed hardware budget, hardware is part of each configuration (Supplementary Table S2)"; O'Connell "One recorded run per machine; no fixed hardware budget, machine type is part of each configuration (Table 1 VM-type)"; Franzoso "One run per sample on a GCP VM chosen for a baseline cost of about 1.65 to 1.79 USD per hour; hardware is part of each configuration". Comparison objects are now identical within each protocol. Automatic comparison stays blocked because `dataset_version` and `adaptation` are null on all of them, which is accurate.
2. Three results disputed with `source_warnings` (concerns 1 and 5).
3. `model-execution-20261009-data-franzoso2025-wes`: `population` printed float artefacts ("4.4000000000000004 GB", "4.9000000000000004 GB"); now "4.4 GB" and "4.9 GB", as Table S1 displays them.
4. `model-execution-20261009-protocol-samarakoon2025-mapping`: name ended "Table S3a) )"; the stray " )" is removed.
5. `model-execution-20261009-config-samarakoon2025-parabricks-4-3-0-1-8xh100`: added `model_identity_note` (concern 2).
6. `model-execution-20261009-config-samarakoon2025-parabricks-4xl4`: `hardware.description` now also says the Table S2 notes give 196 GB for G2 machines against 192 GB in the table.
7. `model-execution-20261009-config-oconnell2023-aws-gpu2`, `-gpu4`, `-gpu8`: `hardware.description` was "AWS GPU machine, N GPUs (Table 1 footnote: p3 family, NVIDIA Tesla V100)"; now states the model is unresolved between the footnote (V100) and the text (A100). `model_identity_note` gained the cost arithmetic.
8. `model-execution-20261009-claim-samarakoon2025-cost-summary`: the last sentence said "Disk costs are excluded." Supplementary Text 03 says only the GCP estimates exclude disks; now "The GCP estimates exclude disk costs." The rest of the claim matches Text 03 Table 2.
9. `model-execution-20261009-claim-samarakoon2025-parabricks-version`: value and locator extended with the Table S4 "updated version" wording, the 4.3.1-1 release-notes citation and Discussion paragraph 10. `claims.csv` row updated to match.
10. Protocol and judgement limitations (kept identical on each pair; one more limitation on each judgement, item 11):
    - O'Connell, all six: the single-run limitation now adds that DGX runs were repeated at least three times and only the final run is shown (Methods 'DGX configuration'); the AWS GPU limitation adds the cost arithmetic.
    - O'Connell Mutect2: the 16.9 h limitation adds the internal consistency of 6.91 h.
    - Samarakoon total: the NA12778 sentence adds the sum (31.94) and that the result is disputed and not shown.
    - Samarakoon DV: the hardware sentence named a DRAGEN server, which has no DV stage; now "CPU cluster, two GCP VMs and an HPC GPU node".
    - Samarakoon dv-version: added the version-identity conflict.
    - Franzoso WGS: the two-cell sentence now gives the cells, says both results are disputed and not shown, and that the hours-and-minutes reading is unconfirmed.
    - Franzoso WES and WGS: the VM sentence adds that the text says Parabricks used 16 CPUs on genomes while Methods give its VM 48 vCPUs.
11. All 13 judgements: added "No linked source repeats runs, measures run-to-run concordance of the calls, or reports accuracy next to runtime, so this evidence bears on the resource and throughput part of the question only, not on reproducibility."
12. Judgement rationales (and the matching `description`): the Samarakoon rationales said "CPU, GPU and FPGA execution set-ups". The sources do not describe the DRAGEN server as FPGA hardware, and the DV stage has no DRAGEN column; now "CPU-only, Parabricks GPU and DRAGEN server set-ups" (DV: "CPU-only and Parabricks GPU set-ups"). The dv-version rationale called a version change "a reproducibility and planning concern"; it now says it bears on version pinning and does not measure run-to-run reproducibility. O'Connell and Franzoso rationales are rewritten for the relevance decisions below. Franzoso "cost-matched" became "of similar hourly cost" (1.79 against 1.65 USD), also in `comparison_title`.
13. Statuses: 485 results, 91 evaluations, 19 configurations, 13 protocols, 5 datasets, 5 sources, 3 methods and 15 claims set to `source_checked`; 3 results `disputed`. Every result's `review` now records this review's method, reviewer, `reviewed_at` and notes; the extractor's text is kept in `note`.

`coverage.json` and `research.md` are the collector's record and were not edited; where they disagree with the batch (relevance, limitations, summary text), the batch and this review supersede them.

## Relevance judgements

Endpoint fit. The question asks about resource, throughput and reproducibility constraints. Wall-clock runtime and cost per sample on fixed inputs measure the resource and throughput part. None of the three sources measures reproducibility (no printed repeats, no run-to-run concordance) or reports accuracy beside runtime, which every judgement now says. None measures a foundation model; DeepVariant is a deep-learning caller inside conventional pipelines.

| Judgement | Relevance | Reasoning | reviewed_evaluations |
| --- | --- | --- | --- |
| `...-samarakoon2025-mapping`, `-hc`, `-total` | direct | Ten samples (four low, six high coverage), same inputs across five execution set-ups, academic group with no competing interests. Stage and total wall-clock are the throughput endpoint. | 5 each |
| `...-samarakoon2025-dv` | direct | As above; four set-ups (DRAGEN has no DV). | 4 |
| `...-samarakoon2025-dv-version-h100` | direct | Runtime of the same stage on fixed hardware before and after a version update. Narrow (three samples) and the updated version's label conflicts; both are in the limitations. | 2 |
| `...-franzoso2025-wes`, `-wgs` | direct | Five samples each, FASTQ to VCF, framed for hospital diagnostics, no declared conflicts. One run per sample. | 2 each |
| `...-oconnell2023-deepvariant`, `-haplotypecaller` | proxy (was direct) | One HG002 30x genome, one recorded run per machine, authors employed by and funded by an NVIDIA, AWS and Google alliance partner, and the AWS GPU type unresolved. | 11 each |
| `...-oconnell2023-lofreq`, `-muse`, `-mutect2`, `-somaticsniper` | proxy (was direct) | As above, on one synthetic tumour BAM made from that genome (198 added SNVs; the matched normal is not described). | 11 each |

No evaluation is excluded: each protocol's evaluations all apply, and the three disputed results leave every evaluation with at least nine reviewed results.

Grouping and presentation:

- `samarakoon2025-wgs-stages`: strata 1 read mapping, 2 HC or GSVC, 3 DV, 4 total; all runtime in minutes, results paired by sample through `metric_qualifier`. Correct.
- `samarakoon2025-dv-version`: one protocol, no stratum; minutes. Correct.
- `franzoso2025-gcp`: 1 WES, 2 WGS; runtime in seconds (printed h:mm:ss). Correct.
- `oconnell2023-germline` (1 DeepVariant, 2 HaplotypeCaller) and `oconnell2023-somatic` (alphabetical): correct. Each evaluation carries runtime twice, as printed: in minutes and in hours (qualifier "printed in minutes" or "printed in hours"). I checked that the hour column is the minute column divided by 60 to rounding (one 0.01 exception, noted). Comparisons will not mix them, because unit and qualifier differ, but `headline_metric: runtime` matches both series. The website should take the minute series as the headline; if it cannot choose by unit, the lead should decide whether that needs a code change. Within a group, minutes and hours are never mixed in one series.

## Vocabulary

Approved as written in `data/vocab/metric.ttl` and `data/vocab/unit.ttl`.

- `compute-cost` (lower), `cost-saving` (higher, negative when the configuration costs more) and `speedup` (higher, altLabel "fold acceleration") have clear definitions, do not respell an existing concept (`runtime` is time, not cost or ratio), and match how O'Connell and Samarakoon define fold acceleration (Samarakoon Methods 2.6) and cost savings. No STATO or QUDT match exists; none claimed.
- `minute` exactMatch `unit:MIN`: retrieved http://qudt.org/vocab/unit/MIN as Turtle (SHA-256 `d6476d09...`): `qudt:Unit`, label "Minute", conversion multiplier 60.0, quantity kind Time, symbol "min". Correct.
- `us-dollar` exactMatch `unit:USDollar`: retrieved http://qudt.org/vocab/unit/USDollar (SHA-256 `1cbad2f8...`): `qudt:CurrencyUnit`, label "US Dollar", currency code USD, symbols "$" and "US$". Correct. O'Connell and Franzoso print "$" only; their context (AWS and GCP list prices, northern Virginia pricing in O'Connell) supports US dollars.

## Approved use-case changes

Changes to `use-case-diagnostic-genomics-model-execution`. Fields not listed (name, description, question, intended users, inputs, exclusions, search terms, collection plan, planned work, review) stay as they are. The decision, output, setting and clinical scope all describe only the DRAGEN baseline today, so leaving them would misdescribe a page with 14 judgements; they are the minimum set to change.

`links`: append `{"relation": "assessed_by", "target_id": ...}` for each of:
`model-execution-20261009-protocol-franzoso2025-wes-gcp`, `model-execution-20261009-protocol-franzoso2025-wgs-gcp`, `model-execution-20261009-protocol-oconnell2023-deepvariant`, `model-execution-20261009-protocol-oconnell2023-haplotypecaller`, `model-execution-20261009-protocol-oconnell2023-lofreq`, `model-execution-20261009-protocol-oconnell2023-muse`, `model-execution-20261009-protocol-oconnell2023-mutect2`, `model-execution-20261009-protocol-oconnell2023-somaticsniper`, `model-execution-20261009-protocol-samarakoon2025-dv`, `model-execution-20261009-protocol-samarakoon2025-dv-version-h100`, `model-execution-20261009-protocol-samarakoon2025-hc`, `model-execution-20261009-protocol-samarakoon2025-mapping`, `model-execution-20261009-protocol-samarakoon2025-total`.

`source_ids`: append `model-execution-20261009-source-samarakoon2025`, `model-execution-20261009-source-samarakoon2025-supplement`, `model-execution-20261009-source-oconnell2023`, `model-execution-20261009-source-franzoso2025`, `model-execution-20261009-source-franzoso2025-table-s2`. These must be in the store as `source_checked` with no `evidence_concerns`; otherwise every positive judgement on the use case is withheld.

`attributes.citation_locators`: append

- `model-execution-20261009-source-samarakoon2025`: "Methods 2.1-2.6; Results 3.1; Discussion paragraphs 10, 11 and 15"
- `model-execution-20261009-source-samarakoon2025-supplement`: "Supplementary Tables S1-S4 and Supplementary Text 03; see data/omics/use-case-coverage-model-execution-20261009/claims.csv"
- `model-execution-20261009-source-oconnell2023`: "Table 1; Methods; Competing interests; see data/omics/use-case-coverage-model-execution-20261009/claims.csv"
- `model-execution-20261009-source-franzoso2025`: "Methods; Results 'Software Runtimes' and 'Costs'; Discussion paragraph 10"
- `model-execution-20261009-source-franzoso2025-table-s2`: "Table S2; see data/omics/use-case-coverage-model-execution-20261009/claims.csv"

`attributes.decision`:

> Compare published per-sample runtime and cost of CPU, GPU and DRAGEN server execution set-ups that resemble the team's hardware and sequencing type when budgeting a workflow; these are conventional variant-calling pipelines, not foundation-model execution benchmarks, and none reports run-to-run variation or accuracy beside runtime.

`attributes.output`:

> Sourced per-sample runtime, cost, speedup and cost-saving values for exact pipeline, version and hardware configurations, with the limits of each comparison; no foundation-model execution benchmark, no reproducibility measurement and no clinical turnaround claim.

`attributes.setting`:

> Published execution benchmarks of conventional variant-calling pipelines, each on fixed public inputs: CPU-only GATK, Parabricks on L4, A100 and H100 GPUs and DRAGEN v4.2 on ten germline WGS samples (Samarakoon et al. 2025); two germline and four somatic callers on CPU and 2, 4 and 8 GPU cloud and DGX machines on one HG002 30x genome (O'Connell et al. 2023); Sentieon DNASeq and Parabricks Germline on Google Cloud machines of similar hourly cost, five exomes and five genomes (Franzoso et al. 2025); and the DRAGEN 4.2 developer total runtime for HG002, 1,838.5 seconds on one hardware configuration and 5,521.21 seconds on an AWS f1.4xlarge configuration, whose stage times cannot be summed because of concurrency. Hardware differs within each comparison, so differences mix software and hardware.

`attributes.clinical_scope`:

> Clinical applicability is not established: the linked evidence is published runtime and cost of conventional variant-calling pipelines on a few public samples, not a foundation-model execution benchmark, a reproducibility study or a clinical validation.

`attributes.evidence_gaps` (replaces the list; the first two replace "No peak-memory endpoint is reported." and "No runtime repeat/variance (CI) is reported.", which they restate, and the last is kept unchanged):

1. No linked study prints measured peak host or GPU memory; Samarakoon et al. 2025 and Franzoso et al. 2025 show memory use only in figures.
2. No linked study prints repeated runs or runtime variance, so run-to-run variation of runtime or of variant calls is not measured; Samarakoon et al. 2025 compare Parabricks on two A100 clusters only in a figure, and O'Connell et al. 2023 repeated DGX runs but print only the final run.
3. No linked study reports accuracy in the same printed table as runtime; Samarakoon et al. 2025 show accuracy and CPU concordance in Figure 5 only.
4. No study of a genomic foundation model's inference runtime, memory or cost was found in this pass.
5. Costs are cloud list prices or authors' estimates at the time of each study and exclude storage and software licences unless stated.
6. A separate ~2-hour joint-aggregation figure over 3,202 genomes at concurrency 200 is a different operation and is not assigned to this single-sample runtime.

Changes from the collector's proposal: the setting no longer says "Germline" for O'Connell, which includes four somatic callers, and keeps the DRAGEN baseline numbers from the current text; "FPGA" is replaced by "DRAGEN server" because no source describes the hardware that way; the decision and output name the missing reproducibility measurement; `clinical_scope` is added because its current text describes only the DRAGEN baseline; the two duplicated gaps are merged; and citation locators are added for the two article sources the use case will cite.

`use-case-mapping-amp-20261007-issue18` under the changed text: re-reviewed and it still holds. Its endpoint (DRAGEN 4.2 total single-sample runtime on HG002) is a throughput measurement; `proxy` remains right because it is one developer-reported sample with no repeats; its limitations still apply; and its rationale, that a conventional pipeline's runtime is not a foundation-model execution benchmark, agrees with the new decision and clinical scope. Because decision, output, setting and clinical scope are pinned, it is withheld until re-pinned, and the release guard refuses a release that withholds a judgement the previous release served. Re-pin it in the same change as the use-case edit:

```sh
npm run use-cases:repin -- docs/reviews/use-cases/diagnostic-genomics-model-execution-2026-10-09.md use-case-mapping-amp-20261007-issue18 <the 13 new judgement IDs> use-case-summary-diagnostic-genomics-model-execution
```

## Evidence summary

Final text for `use-case-summary-diagnostic-genomics-model-execution` (`field` `summary`). Its `source_ids` should be `amp-source-dragen-supplementary-tables`, `model-execution-20261009-source-franzoso2025`, `model-execution-20261009-source-franzoso2025-table-s2`, `model-execution-20261009-source-oconnell2023`, `model-execution-20261009-source-samarakoon2025` and `model-execution-20261009-source-samarakoon2025-supplement`. It is descriptive and recommends nothing.

> Three published execution benchmarks are linked, alongside the DRAGEN 4.2 developer total runtime for HG002 (1,838.5 seconds). All measure conventional variant-calling pipelines; none measures a genomic foundation model. None prints repeated runs, measured peak memory or accuracy next to runtime, so they do not show reproducibility, and hardware differs within each comparison, so differences mix software and hardware. On ten WGS samples run by a University of Oslo and Oslo University Hospital group with no declared competing interests (Samarakoon et al. 2025), read mapping plus HaplotypeCaller for NA12878 (47.55x) took 2,317.7 minutes on a CPU-only GATK pipeline, 123.45 minutes with Parabricks on four L4 GPUs, 78.12 on four A100 GPUs, 54.22 on eight H100 GPUs and 60.29 with DRAGEN v4.2. On the same H100 machine, Parabricks DeepVariant took 14.58 minutes for NA12878 with the version the pipeline used (printed 4.1.0-1; Methods say 4.3.0-1) and 16.05 minutes with the updated version (printed 4.3.0-1; Discussion says 4.3.1-1). On one HG002 30x genome on Google Cloud (O'Connell et al. 2023; the authors' employer funded the study and is an NVIDIA, AWS and Google alliance partner), HaplotypeCaller took 38.8 hours and cost 67.9 USD on a 32-vCPU machine and 0.59 hours and 17.5 USD on eight A100 GPUs, while the somatic caller LoFreq cost 8.1 USD on the CPU machine and 19 to 30.1 USD on 2 to 8 A100 GPUs. On Google Cloud machines of similar hourly cost (Franzoso et al. 2025, no declared conflicts), Sentieon DNASeq took 0:14:00 to 0:16:00 per exome at 0.82 to 1.03 USD and 3:00:00 to 3:50:00 per genome at 8.02 to 10.7 USD, and Parabricks Germline on one T4 GPU took 0:10:00 to 0:14:00 per exome at 0.71 to 0.93 USD and 4:06:00 to 4:40:00 per genome at 8.13 to 10.6 USD; costs exclude the Sentieon licence, and two genome runtime cells that cannot be genome runtimes are disputed and left out of these ranges. Each comparison is one run per sample on at most ten public samples, and costs are list prices at the time of each study.

Traceability (all `source_checked`; prefix `model-execution-20261009-result-` unless stated):

| Statement | Record(s) | Printed |
| --- | --- | --- |
| DRAGEN developer baseline | `amp-result-dragen-hg002-phase4-runtime` | 1838.5 |
| NA12878 coverage | Supplementary Table S1, in the qualifier of each NA12878 result | 47.55 |
| CPU, L4, A100, H100, DRAGEN totals for NA12878 | `samarakoon2025-cpu-epyc7702-total-na12878`, `-parabricks-4xl4-total-na12878`, `-parabricks-4xa100-total-na12878`, `-parabricks-8xh100-total-na12878`, `-dragen42-server-v2-total-na12878` | 2317.7, 123.45, 78.12, 54.22, 60.29 |
| DV versions on H100, NA12878 | `samarakoon2025-parabricks-8xh100-dv-version-na12878`, `samarakoon2025-parabricks-4-3-0-1-8xh100-dv-version-na12878` | 14.58, 16.05 |
| HaplotypeCaller GCP CPU | `oconnell2023-gcp-n2-standard-32-haplotypecaller-runtime-hours`, `-compute-cost` | 38.8, 67.9 |
| HaplotypeCaller GCP 8 A100 | `oconnell2023-gcp-a2-gpu8-haplotypecaller-runtime-hours`, `-compute-cost` | 0.59, 17.5 |
| LoFreq GCP CPU and GPU costs | `oconnell2023-gcp-n2-standard-32-lofreq-compute-cost`; `oconnell2023-gcp-a2-gpu2-`, `-gpu4-`, `-gpu8-lofreq-compute-cost` | 8.1; 19, 27.1, 30.1 |
| Sentieon exome runtimes | `franzoso2025-sentieon-dnaseq-202308-gcp-64vcpu-srr11012403-runtime` (min), `-srr11012408-runtime` (max) | 0:14:00, 0:16:00 |
| Sentieon exome costs | `...-64vcpu-srr11012403-compute-cost` (min), `...-64vcpu-srr11012405-compute-cost` (max) | 0.82, 1.03 |
| Sentieon genome runtimes | `...-64vcpu-err1955536-runtime` (min), `...-64vcpu-err1955541-runtime` (max); ERR1955532 disputed | 3:00:00, 3:50:00 |
| Sentieon genome costs | `...-64vcpu-err1955540-compute-cost` (min), `...-64vcpu-err1955536-compute-cost` (max) | 8.02, 10.7 |
| Parabricks exome runtimes | `franzoso2025-parabricks-germline-4-0-1-1-gcp-t4-srr11012406-runtime` (min), `-srr11012408-runtime` (max) | 0:10:00, 0:14:00 |
| Parabricks exome costs | `...-t4-srr11012404-compute-cost` (min), `...-t4-srr11012408-compute-cost` (max) | 0.71, 0.93 |
| Parabricks genome runtimes | `...-t4-err1955540-runtime` (min), `...-t4-err1955541-runtime` (max); ERR1955539 disputed | 4:06:00, 4:40:00 |
| Parabricks genome costs | `...-t4-err1955540-compute-cost` (min), `...-t4-err1955539-compute-cost` and `...-t4-err1955541-compute-cost` (max) | 8.13, 10.6 |

Non-numeric statements trace to: Samarakoon Conflict of interest and affiliations; Methods 2.3 and Discussion paragraph 10 (versions); O'Connell Funding and Competing interests; Franzoso Conflicts of Interest and Discussion paragraph 10 (licence).

## Remaining gaps

- Figures were not read, so the memory, accuracy, concordance and Polaris comparisons in Samarakoon and the CPU and memory profiles in Franzoso are unchecked.
- O'Connell Additional file 1 (Table S1, the other AWS GPU family) was not retrieved, so the AWS GPU identity cannot be settled from this pass.
- Samarakoon Supplementary Text 01 tables (run-partition and NF-optimised HaplotypeCaller) and the Text 03 per-sample cost table are not extracted as results; Discussion paragraph 15 totals (83.42 and 448.01 USD for ten samples on L4 and H100) are not recorded.
- Franzoso prints the Parabricks version with a dash character other than a hyphen between "4.0.1" and "1"; it is recorded as "v4.0.1-1".
- `tests/omics-data.test.ts` line 142 expects 106 rows in `data/omics/scope-audit.jsonl`; the collector's six new rows make 112, so `npm test` fails that one test (498 of 499 pass). The count needs updating when the batch is integrated. `npm run typecheck` passes. `npm run build` was not run, by instruction.
