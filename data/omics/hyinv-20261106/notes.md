# HyInv extraction, 2026-11-06

Batch for issue #232: HyInv, the Tencent Hunyuan protein inverse-folding model released on
2026-11-02, and the evaluations of its technical report (dated 2026-10-14).

Extractor: Claude agent. This batch is not reviewed. No human review is claimed anywhere in it, and
`review-evidence` has not run. Every record carries status `needs_review`.

## Sources

All four artifacts are pinned to commit `0dcc533cc9f8f76c90ecbfe944df816b6672328a` of
`Tencent-Hunyuan/Hyra-results`, retrieved 2026-11-06T09:52:00Z.

| Record | Artifact | SHA-256 |
| --- | --- | --- |
| `hyra-results-20261106-source-repository-readme` | `README.md` | `da0c496f…a2bdb` |
| `hyinv-20261106-source-report` | `AI4Science/hyinv/HyInv_Technical_Report.pdf` | `0f10b390…46419` |
| `hyinv-20261106-source-model-readme` | `AI4Science/hyinv/README.md` | `b44c6d0c…d6891` |
| `hyinv-20261106-source-licence` | `AI4Science/hyinv/LICENSE` | `816fb3d7…ce350` |

The top-level README record has a deliberately neutral ID (`hyra-results-20261106-source-…`,
not `hyinv-…`) because the same artifact is the announcement for HyPLM-Flash and HyCell. The two
later batches must reuse this ID rather than create their own record for the same bytes.

`artifacts/` holds the three text artifacts verbatim and the gzipped `pdftotext -layout` text layer
of the report. The PDF itself is not committed: it is 2.9 MB, it can be refetched at the pinned
commit, and `extract/parse.py` refuses any file whose SHA-256 is not the pinned one. The repository
is Apache-2.0 and the package MIT, so archiving is permitted.

## How the values were extracted

`extract/parse.py` checks the PDF hash, runs `pdftotext -layout`, and parses each table by locating
its caption and then its rows in printed order, asserting every row label, the cell count of every
row and the printed number format of every cell. It also derives each locator's page number from the
form feeds rather than taking it from me, and cross-checks the figures the source prints twice:

- Table 2 (a three-method subset at 3 decimal places) is asserted to agree with Table 6 and with
  Figure 14's recovery and diversity blocks.
- Figure 14's scTM block is asserted to agree with Table 6's ESMFold2 columns at 3 decimal places.
- Figure 4a's five repeated bars are asserted to equal Table 1's 402-residue column.
- The values repeated in prose in Sections 3.2 and 4 are asserted to equal Tables 8 and 9.

`extract/build.py` turns the parsed cells into records. `extract/validate-batch.mts` runs the same
vocabulary, attribute, description, concern and schema checks as `records -- add` without writing to
the store; it reports 1,080 records passing against the 86,681 stored ones.

Rebuild with:

```
curl -sSLo /tmp/hyinv/HyInv_Technical_Report.pdf \
  https://raw.githubusercontent.com/Tencent-Hunyuan/Hyra-results/0dcc533cc9f8f76c90ecbfe944df816b6672328a/AI4Science/hyinv/HyInv_Technical_Report.pdf
python3 -I data/omics/hyinv-20261106/extract/build.py /tmp/hyinv/HyInv_Technical_Report.pdf \
  data/omics/hyinv-20261106/batch.jsonl
npx tsx data/omics/hyinv-20261106/extract/validate-batch.mts data/omics/hyinv-20261106/batch.jsonl
```

## Record counts

| Kind | Count |
| --- | --- |
| source | 4 |
| model | 6 |
| method | 1 |
| configuration | 23 |
| benchmark | 1 |
| dataset | 8 |
| dataset_subset | 3 |
| protocol | 19 |
| evaluation | 485 |
| result | 498 |
| claim | 32 |
| total | 1,080 |

## Tables extracted

| Source location | Cells | Recorded as |
| --- | --- | --- |
| Table 1, inference time | 19 of 20 | runtime and speedup results. ProteinMPNN's speed-up cell is printed as a dash and is not recorded. |
| Figure 4a, bar labels | 8 | runtime results for the eight systems Table 1 omits; the five repeated bars are cross-checked, not duplicated. |
| Table 6, scTM | 84 | scTM results, 12 rows by 7 panel-predictor columns. |
| Table 7, paired scTM difference | 70 | scTM-difference results with their 95% intervals. |
| Table 8, gain at equal diversity | 12 | scTM-at-fixed-diversity-difference results with their intervals. |
| Table 9, BF16 against reference | 4 | scTM-at-fixed-diversity-difference results with their intervals. |
| Figure 14, recovery and diversity | 110 | sequence-recovery and sequence-diversity results. |
| Figure 15, pLDDT, scRMSD, CA-lDDT | 180 | plddt, scrmsd and lddt results. |
| Appendix D.3 prose | 2 | the two equal-diversity differences against the ProteinMPNN curve. |
| Section 5.4 prose | 3 | the two S@0.30 levels (0.839, 0.852) and the printed +0.0133 gain. |
| Section 6 prose | 6 | novel-and-foldable yield, both readings, for three systems. |

### Tables and figures deliberately not extracted as results

- **Table 2** is a three-method subset of Table 6 and Figure 14 printed to 3 decimal places. Its
  cells are asserted to agree with the 4-decimal and 3-decimal sources and are not stored a second
  time at lower precision.
- **Figure 14's scTM block** likewise duplicates Table 6's ESMFold2 columns at 3 decimal places.
- **Table 3** (panel composition), **Table 4** (training configuration), **Table 5** (baseline
  settings and the reproduction check) and **Table 10** (homology screen of the application panels)
  describe the setup rather than measuring a system on a panel. Their content is in the dataset and
  configuration records and in claims, with every number quoted.
- **Figures 1, 5, 6, 7, 8, 13, 16 and 17** carry no printed per-cell values that are not already in
  a table, or print only axis ticks. Figure 17's eleven optimisation-ladder latencies are an
  engineering account of HyInv's own implementation, not a comparison of systems.
- **Figure 9b** prints six bar values that Section 6 also states in prose; the prose is what was
  read, so the figure was not read by eye.
- **Figure 11c** prints nine median catalytic-site RMSD bars (three enzymes by HyInv, ProteinMPNN
  and the native sequence). The text layer gives the nine numbers but not which bar each belongs to,
  so they are a recorded gap, not a guess. The three displayed single-design values are in a claim.

## Decisions the brief asked me to make

### Which tables hold structural-consistency results with a stated diversity level

Only four places in the report read scTM at a stated diversity:

- **Table 8** (D = 0.30 development, 0.32 CATH4.3 test, 0.30 RecentPDB), comparing HyInv sampler
  settings with the unmodified sampler of the same checkpoint.
- **Table 9** (D = 0.30), comparing the BF16 path with the FP32 reference sampler.
- **Appendix D.3**, the only equal-diversity comparison against a baseline: HyInv above the
  ProteinMPNN curve at HyInv's own diversity, +0.0146 [+0.0058, +0.0242] on CATH4.3 test and
  +0.0187 [+0.0078, +0.0302] on RecentPDB.
- **Section 5.4's reinforcement-learning ablation** (D = 0.30 development), 0.839 to 0.852.

These carry the two new metric concepts `sctm-at-fixed-diversity` and
`sctm-at-fixed-diversity-difference`, whose qualifiers name the diversity level, the fit and the
reference setting. Tables 6 and 7, Figures 14 and 15 and everything else are at each method's own
single published setting, with diversity reported beside the score rather than held fixed; they use
`sctm` and the new `sctm-difference`.

### Whether the ProteinMPNN temperature-grid rows are separate configurations

The rows the tables name are three separate configurations, because each is a different published
setting of ProteinMPNN: `ProteinMPNN` (autoregressive, T 0.1), `ProteinMPNN grouped` (grouped
autoregressive, T 0.1) and `ProteinMPNN (low-noise, grouped)` (the same with the checkpoint trained
with less coordinate noise). All three appear as labelled rows with their own cells in Tables 5, 6
and 7 and Figures 14 and 15.

The temperature *grid* is different. Appendix D.3 says ProteinMPNN has three temperatures, two of
which were generated for this report, and the per-temperature points are printed only in Figure 16
as plotted markers. I did not create configurations for T 0.2 and T 0.3: there are no printed values
to attach to them, and a configuration with no result would assert an identity the source does not
pin down. What the report does print from that grid is the single fitted difference at HyInv's
diversity, which is recorded under
`hyinv-20261106-protocol-sctm-fixed-diversity-vs-proteinmpnn-curve` against the one `ProteinMPNN`
configuration, with the grid described in the protocol's `metric_implementation`. The individual
grid points are a recorded gap.

### How the lower-diversity single-point baselines are kept from implying a matched comparison

Four mechanisms, so that nothing downstream has to re-derive the caveat:

1. The report source carries an `evidence_concerns` entry naming the mismatch with the printed
   diversity figures (HyInv 0.331 on CATH4.3 test against PiFold 0.093, CMLM 0.104, LM-Design 0.144
   and DPLM-2 3B 0.000) and stating that these results must not be read as a matched-diversity
   ranking. A source-level concern without `applies_to` covers every record the source supports,
   which is what is wanted here: the caveat is about the comparison as a whole.
2. Every scTM and scTM-difference protocol lists the mismatch in `limitations`, and the
   `metric_qualifier` of each result says the value is at the method's own single published setting.
   Because automatic comparison requires the same metric, qualifier, unit and direction, the
   single-setting results cannot silently be compared with the fixed-diversity ones, which carry
   different concepts and qualifiers.
3. All 156 results for the four worst-affected methods carry a `limitations` line quoting
   Appendix D.2's statement that they are single points at much lower diversity and that their
   differences are not at matched diversity.
4. `sequence-diversity` is recorded with `metric_direction: unknown` and a qualifier saying it is
   matched rather than ranked, so a higher diversity is not presented as better.

### What the report says about training and test sequence overlap

Appendix C states plainly: "We do not claim zero sequence overlap between the training data and the
evaluation panels." The reinforcement-learning pool was filtered against the benchmark panels with a
same-source MMseqs2 homology mask, and the supervised corpus by exact-sequence removal plus a
homology filter. For the application panels, Appendix G's screen is a coverage rule under which a hit
counts only at identity at least 0.3 *and* coverage at least 0.8, so partial hits remain: Table 10
records 28 of 74 de novo backbones and 7 of 12 pocket backbones with partial hits, and all four named
enzymes are homologous to training data by design. This is recorded three times over: in the model's
`training_evaluation_overlap` claim, in the report source's `limitations`, and in the first
`evidence_concerns` entry, which states that these results are not clean held-out measurements and
must not be compared with sources that do establish no overlap.

### Whether the speed results are in scope

I recorded them as results. Table 1 is a printed table of nine labelled cells per column with a
stated protocol (Appendix F), the quantity is a real measurement under conditions the source
describes, and leaving it in prose only would make the fastest-claim unauditable. What keeps it
honest is the qualifier and the caveats rather than exclusion:

- `protocol-design-latency-h20` and `protocol-design-speedup-vs-proteinmpnn-h20` state in
  `metric_implementation` and `limitations` that the measurement is on one NVIDIA H20, that the timed
  region excludes model loading, CUDA graph capture and kernel compilation, that HyInv's rows used
  the supervised-stage weights at rewrite temperature 0.23 rather than the released default, and that
  the baselines ran as released and unbatched where their adapter handles one structure per call, so
  Appendix F's own words are that the speed-ups are "against these implementations, not against the
  best achievable speed of the baseline models".
- The third `evidence_concerns` entry on the source says speed and quality in this report are
  measured on different weights and that the 57x figure compares an optimised path with a released
  implementation.
- The speed-up protocol records that the report does not state which request size its single printed
  ratio comes from. The arithmetic of the printed 402-residue times matches (2,907/50.6 = 57.5 and
  2,907/2,633 = 1.10), but the authors do not say so, so no derived value is recorded.

So the issue's instruction, not to present optimised-against-reference speed as a universal
ProteinMPNN speed-up, is carried by the records themselves, not only by these notes.

## Other decisions

- **Model level is `checkpoint`, not `family`.** The package README says the released weights are the
  structure-reward reinforcement-learning version and the report names the evaluated update (640),
  so the released artifact and the evaluated system are the same thing. No weights hash or revision
  is published, which is recorded in `missing_metadata.checkpoint_revision`.
- **Reused store records**: `catalog-model-proteinmpnn` (ProteinMPNN family, which already carries a
  profile and links to `discovery-model-proteinmpnn`), `lit-interactions-20261011-ppiemb-model-pifold`
  (PiFold) and `catalog-task-protein-design` (the task the benchmark evaluates). Five baseline
  families had no record and were created: ProteinZero V2, CMLM, LM-Design, DPLM-2 and LigandMPNN.
- **Structure predictors are named in the protocols, not given records.** ESMFold2, Boltz2 and
  Protenix2 are scoring tools here, not evaluated systems, and a protocol cannot link to a model, so
  creating version records for them would add graph weight without connecting anything. Existing
  records (`discovery-model-esmfold2`, `catalog-model-boltz-2`, `ucc-research-model-protenix`) are
  left untouched; note that Protenix2 is a later version than the stored Protenix record.
- **The `Native` row needs a system**, so there is one `method` record for the native-sequence
  refold control. It is a control, not a design method, which its description and `reference_kind`
  say.
- **Three configurations exist only to be timed** (reference sampler, exact FP32 path, BF16 path at
  the supervised-stage weights and rewrite temperature 0.23) and are kept separate from the quality
  configurations, because the report measured speed and quality on different weights.
- **One protocol per metric.** Each protocol carries a single `metric` concept, so a system's scTM,
  recovery, diversity, pLDDT, scRMSD and lDDT on one panel are six evaluations rather than one. This
  follows the `lit-structure-20261011-scaffoldlab-*` precedent and keeps the comparison checks
  meaningful, at the cost of 485 evaluations for 498 results. See the open questions.
- **Table 9's "Lower end >= -0.002" column** is the report's own pass verdict derived from the
  interval, not a measurement, so it is recorded in the result's `metric_qualifier` and in the
  uncertainty note rather than as a value of its own.
- **Table 5's reproduction check** (`|dscTM|` and the fraction of identical sequences) measures the
  report's own regeneration of baseline samples, not a system's performance on a panel, so it is one
  claim with all eight printed pairs quoted.
- Four metric concepts were added to `data/vocab/metric.ttl`: `sequence-diversity`,
  `sctm-difference`, `sctm-at-fixed-diversity` and `sctm-at-fixed-diversity-difference`. Each has a
  definition, a `skos:broader` where one applies, and a default direction. No existing concept
  covered a design-set diversity, a paired scTM difference or a curve-fitted score at a fixed
  diversity.

## Gaps

1. **Figure 11c**: nine median catalytic-site RMSD values whose bar-to-series mapping the text layer
   does not give. Not read by eye.
2. **Figure 16**: the per-temperature scTM and diversity points of every method on every panel,
   including ProteinMPNN's three temperatures. Plotted markers only; only the fitted differences of
   Appendix D.3 are printed.
3. **Figure 8b**: the per-schedule scTM change for the six shorter round schedules. Only the range
   (0.0028 to 0.0074 lower than the 16-pass default) is printed, which is in a claim.
4. **Figure 7**: the plain-against-decoupled sampler curves on three panels. The one printed number
   (+0.007 at equal diversity on the development panel) is Table 8's development cell to three
   decimal places.
5. **Figure 13**: the development scTM trace during reinforcement learning and the per-checkpoint
   gain bars. No printed cells.
6. **Panel manifests**: no chain list or split manifest is published for any of the six panels or the
   three development subsets, so no panel can be rebuilt and no cell can be recomputed. Recorded in
   `missing_metadata.manifest` on every dataset and `missing_metadata.exact_manifest` on every
   subset.
7. **Baseline checkpoint revisions**: Table 5 states the released weights were used but prints no
   revision or hash for any of the ten baselines.
8. **Weights hash**: no hash or revision is published for `weights/model.safetensors`.
9. **Result files and scripts**: Appendix H says every number in the report is generated by scripts
   from result files, but neither is published, so nothing in the report can be recomputed from the
   released artifacts.
10. **The launch post** (hy.tencent.com/research/hyra) was not retrieved; nothing in this batch rests
    on it. The issue also records that no announcement URL has been verified, so no announcement
    comment is authorised.
11. **Uncertainty** is unreported for every cell of Tables 1 and 6, Figures 14 and 15, the two
    Section 5.4 levels and the six de novo yields. Recorded as `missing_metadata.uncertainty`
    throughout, never as zero.

## For the reviewer

The open questions are in the handover message. The ones that would change many records are the
evaluation granularity (one protocol per metric, hence 485 evaluations) and whether the printed
numeric matrices inside Figures 14 and 15 should be results at all.
