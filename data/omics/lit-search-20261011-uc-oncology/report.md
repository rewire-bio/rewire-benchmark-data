# Literature search report: tumour somatic variant and fusion detection, 2026-10-11

Lane `uc-oncology`. Use cases `use-case-tumour-dna-somatic-variant-detection` and `use-case-tumour-rna-fusion-detection`. Window 2025-10-01 to 2026-10-11. Budget about 30 queries per use case; used 12 Europe PMC queries and 6 lookups for the somatic use case and 10 queries and 3 lookups for the fusion use case (`ledger.jsonl`, 31 entries; `scope-audit.jsonl`, 23 decisions). Bounded pass, not systematic coverage.

All records are `needs_review`. Nothing is in the store yet. Each batch validates against the current store with the vocabulary, attribute and record checks of `records -- add` (run in memory); the SHACL step of `records -- add` was not run.

## Candidates extracted

| Batch | Source | What | Records | Results | Judgements |
| --- | --- | --- | --- | --- | --- |
| `use-case-coverage-somatic-hg008-20261011` | Hasan 2026, Research Square preprint, plus the author's Zenodo tables (CC BY) | Mutect2 4.6.2.0, Strelka2 2.9.10, DeepSomatic 1.10.0 and union, majority and strict-intersection ensembles on the GIAB HG008 tumour-normal pair, draft HG008-T v0.3 truth | 185 | 144 | 4 (direct) |
| `use-case-coverage-somatic-clairs-to-20261011` | Chen et al. 2025, Nature Communications (ClairS-TO developers; CC BY-NC-ND) | Tumour-only calling on held-out COLO829 and HCC1395: ONT at 25x to 75x, PacBio and Illumina at 50x; ClairS-TO, Clair3, DeepSomatic, Mutect2, Octopus, Pisces | 508 | 434 | 8 (direct) |
| `use-case-coverage-somatic-varnet-t-20261011` | Krishnamachari et al. 2026, Nature Communications (VarNet-T developers; CC BY) | Tumour-only Illumina WGS AUPRC on SEQC2, COLO829, ten PCAWG primary tumours and three low-burden tumours; VarNet-T, five DeepSom models, DeepSomatic, Mutect2, ClairS-TO | 237 | 153 | 6 (direct) |
| `use-case-coverage-somatic-wes-synthetic-20261011` | López-Cade et al. 2025, Biomolecules (CC BY) | Mutect2, Strelka2 2.9.10 and FreeBayes 1.3.6 via nf-core/sarek on a BAMSurgeon synthetic WES pair | 28 | 18 | 1 (proxy) |
| `use-case-coverage-rna-fusion-longread-20261011` | Dorney et al. 2026, bioRxiv preprint (CC BY), plus the authors' repository tables (MIT) | Six long-read fusion callers on simulated reads (9 scenarios), SG-NEx K562 and MCF7 (3 ONT library types, several depths), and Huh7 on PacBio, ONT and Illumina | 645 | 597 | 4 (1 proxy, 3 direct) |
| `use-case-coverage-rna-fusion-leukaemia-20261011` | Kim et al. 2025, Annals of Laboratory Medicine (CC BY-NC) | STAR plus Arriba v2.4.0 with manual review against karyotyping, FISH and RT-PCR in 101 acute leukaemia patients | 89 | 83 | 1 (direct) |
| Total | 6 sources (14 source records) | | 1,692 | 1,429 | 24 |

Add order: `use-case-coverage-somatic-clairs-to-20261011` before `use-case-coverage-somatic-varnet-t-20261011` (the VarNet-T ClairS-TO configuration links to the ClairS-TO method created in the first). Each batch has `coverage.json` with reused IDs, new IDs, the judgements and their evaluations, the `assessed_by` links to add, proposed use-case changes and gaps. Extractors are in each batch's `extract/` and run with `python3 -I`.

## Candidates not extracted

| Source | Reason |
| --- | --- |
| Bharne and Gaston 2026, bioRxiv 10.64898/2026.04.08.717310 (six callers, AmpliSeq Focus, HD789 tumour-only) | Prints per-variant detection and VAF only; no per-caller performance metric. Computing recall from Table 4 would be an aggregation the source does not state. Excluded in the scope audit. |
| ClairS, Nature Methods 2026 (long-read tumour-normal, developer) | Valuable for long-read tumour-normal calling; stopped at the source budget. First candidate for a follow-up. |
| DeepSomatic, Nature Biotechnology 2025-10-16 | Not open access through Europe PMC; not retrieved. |
| Synth4bench 2026, Frontiers in Bioinformatics (five tumour-only callers on synthetic data) | Results mostly in figures; synthetic only. |
| GigaScience 2026 long-read cancer genome standards (cell-line mixtures) | Benchmark resource; results mainly against short-read calls. Could be a `discovered` dataset. |
| VariantMedium 2026 (Genome Medicine), Lancet2 2026 (NAR Genomics and Bioinformatics) | Developer papers; lower priority than the tumour-only and HG008 evidence. |
| GFSeeker 2026, IFDlong 2026 (long-read fusion developers) | GFSeeker is covered independently by Dorney et al.; IFDlong is a developer comparison. |
| Fuzzion2 2025 (Cell Reports Methods) | Targeted fusion matching; developer dilution experiments. |
| Fusions4U 2025 (BMC Cancer) | Validated fusions for 328 cell lines; a possible truth set, not an evaluation. |
| Cells 2026 (Arriba depth subsampling, 301 acute leukaemia patients) | Single caller, overlaps with Kim et al.; stopped at budget. |
| SMaHT 2025 preprint, HG002 subclonal resource 2025, HG008 SV benchmark 2026, ctDNA mutation-calling benchmark 2025 | Outside these use cases (mosaicism, germline reference, structural variants, ctDNA). |

## Gaps

Somatic:

- No independent tumour-only comparison with printed per-caller values was found; both linked tumour-only sources are developer papers, and they disagree: ClairS-TO SSRS on Illumina COLO829 has SNV AUPRC 0.6500 in its own paper and 0.270 in the VarNet-T paper.
- FFPE tissue, targeted panels and ctDNA remain uncovered. The one panel study found prints no metric.
- The HG008 evidence is one unreviewed single-author preprint on a draft truth set.
- No foundation-model somatic caller was found; all deep-learning callers here are supervised.
- Not extracted from the chosen sources: Hasan Zenodo Tables 3, 5 to 7 and S1 to S3; ClairS-TO Supplementary Tables 3 to 6 and 8; VarNet-T best-F1, VAF, purity and TMB results (figures with Source Data); López-Cade real-tumour concordance.

Fusion:

- Long-read caller precision and recall exist only on simulated reads; on real cell lines only counts of known and other calls are available.
- Short- versus long-read on the same RNA is one cell line with callers pooled per platform.
- Only one workflow is scored against orthogonal clinical assays.
- Still no multi-caller comparison on adult solid tumours or FFPE with printed values, no single-cell fusion benchmark, no deep-learning fusion caller benchmark on RNA.
- Figure-only Dorney results (read-support curves, class recall, breakpoint accuracy, Huh7 per-library recovery for direct cDNA and direct RNA) are not recorded.

## What needs a reviewer's judgement

1. Tumour-only scope. The somatic use case excludes tumour-only calling and its inputs require a matched normal. The ClairS-TO and VarNet-T judgements are marked `direct` on the assumption that the exclusion is lifted (`coverage.json` `use_case_changes`). Changing `exclusions`, `inputs` or `setting` withholds every reviewed judgement on the use case until it is re-pinned by name. Alternative: mark these 14 judgements `proxy` and leave the use-case text alone.
2. Hasan 2026 source quality. Single-author preprint from the author's company; the original scoring code was not retained (the author says an internal reimplementation reproduced the numbers). Decide whether it supports `direct` judgements or needs an `evidence_concern`. Also check whether DeepSomatic's bundled WGS model saw HG008 data (not stated).
3. Repository and Source Data values. Dorney metrics come from the authors' repository tables behind the figures, recorded as stored (full precision). VarNet-T Supplementary Tables 1 and 4 are images; their values come from the authors' Source Data sheets at three decimals. Neither involves any computation, but neither is a printed table cell in the usual sense.
4. Conflicts kept as limitations, not evidence concerns:
   - López-Cade Table 1, FreeBayes row: TP 1,908 + FN 2,314 = 4,222, not 4,709; printed recall 0.4519 = 1,908/4,222. FreeBayes is excluded from the judgement.
   - Dorney Results false-call counts (632, 519, 106, 38) match no row of the repository table; the 1 Gb denominators (187 to 208) are unexplained.
   - VarNet-T prints indel AUPRC for DeepSom, an SNV method.
5. Training overlap. DeepSomatic is excluded from the VarNet-T SEQC2 judgements (trained on SEQC2). ClairS-TO's authors omit DeepSomatic on HCC1395 for the same reason. ClairS-TO's precision, recall and F1 are at a threshold chosen on the test data.
6. Headline metrics. F1 for HG008 and ClairS-TO, AUPRC for VarNet-T, recall for López-Cade and Kim, true-positive count for the Dorney cell-line protocols. Clair3 (a germline caller) is included in the ClairS-TO judgements; consider excluding it.

## Proposed summary updates

Not applied. The reviewer approves the text, and it is applied after review following docs/use-cases.md. Every number below is a stored result in these batches or already in the summary.

### Tumour DNA somatic variant detection

Replace the first sentence with "Eight studies are linked, and their values cannot be pooled: truth sets, sequencing, caller versions and scoring scripts differ." Keep the existing text through the Sahraeian paragraph, then replace the final sentence with:

> Hasan 2026, a single-author preprint by someone who developed none of the callers, scored Mutect2, Strelka2, DeepSomatic and three ensembles on the GIAB HG008 tumour-normal pair against a draft truth set (14,014 variants in the primary region). F1 was 0.91 for a two-of-three majority vote, 0.90 for Mutect2 and DeepSomatic and 0.78 for Strelka2; for indels Mutect2 reached 0.82 and DeepSomatic and Strelka2 0.69. Two developer papers tested tumour-only calling, without the matched normal. On Illumina COLO829 at 50x, ClairS-TO's developers report SNV F1 0.77 for ClairS-TO against 0.62 for DeepSomatic, 0.58 for Mutect2, 0.40 for Octopus and 0.22 for Pisces, with indel F1 at most 0.29, all at a threshold chosen on the test data. The VarNet-T developers report SNV AUPRC 0.773 for VarNet-T on SEQC2 and 0.656 on COLO829, against 0.543 and 0.270 for ClairS-TO and 0.078 and 0.072 for Mutect2; on three low-burden tumours every tumour-only caller had AUPRC at most 0.112. The same tool scores differently in different developers' hands (ClairS-TO COLO829 SNV AUPRC 0.6500 in its own paper, 0.270 in the VarNet-T paper). On a synthetic WES pair, Mutect2 recalled 0.63 of inserted SNVs and Strelka2 0.46 with default nf-core/sarek settings. Only the HG008 preprint reports interval estimates; no linked study covers FFPE tissue, ctDNA or targeted panels, and none establishes clinical performance.

### Tumour RNA fusion detection

Replace the first sentence with "Four comparisons join the Seraseq reference and paediatric NCH cohort evidence; values cannot be pooled across studies." Keep the Tamura and Lin text, then replace the last sentence with:

> In an independent long-read benchmark (Dorney et al. 2026 preprint), no caller exceeded F1 0.35 on 400 simulated fusions at 100 Gb and 95% read identity: CTAT-LR-Fusion 0.35 (recall 0.28, precision 0.46), JAFFAL 0.29, Genion 0.20, FusionSeeker 0.14, GFSeeker 0.07 and LongGF 0.04. On ONT PCR-cDNA reads of the MCF7 cell line, CTAT-LR-Fusion recovered 20 of 53 known fusions with 51 other calls, JAFFAL 19 with 38 and FusionSeeker 11 with 359. On the Huh7 cell line, with callers pooled, PacBio Kinnex recovered 20 of 34 known fusions, ONT PCR-cDNA 17 and Illumina 15. Against karyotyping, FISH and RT-PCR in 101 acute leukaemia patients (Kim et al. 2025), an Arriba workflow with manual review detected 40 of 48 fusions (sensitivity 83.3%) and found 12 further fusions in 56 conventionally negative results, several confirmed by RT-PCR. These are cell lines, simulations and leukaemia samples: no linked comparison covers adult or solid tumours or FFPE tissue, only Kim et al. use orthogonal clinical truth, none reports interval estimates, and none establishes clinical performance.
