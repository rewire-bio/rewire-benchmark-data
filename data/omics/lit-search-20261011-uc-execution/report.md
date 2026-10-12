# Diagnostic genomics execution: literature pass, 2026-10-11

Use case: `use-case-diagnostic-genomics-model-execution` ("Which eligible model configuration and execution workflow can meet a diagnostic genomics team's resource, throughput and reproducibility constraints?"). Window 2025-10-01 to 2026-10-11. Budget about 30 searches; 20 used (`ledger.jsonl`, `search-lit-20261011-uc-execution-q01` to `-q20`). Worker: Claude (Opus 5.5) research agent `uc-execution`. Nothing is reviewed; every record is `needs_review`. Branch `claude/lit-20261011-uc-execution`, worktree `../rewire-benchmark-data-lit-uc-execution`.

Before the pass the use case had 14 judgements, all on conventional variant-calling pipelines, and these open gaps: no foundation-model execution benchmark, no printed peak memory, no repeated runs or variance, no accuracy beside runtime. The pass targeted those gaps.

## Extracted

Five sources, five batches, 648 records (540 results, 10 draft relevance judgements). All batches pass the store's record, vocabulary and attribute validation when added to a scratch copy of the store, and the SHACL shapes (`npm run kg:shapes`, 116 s). `npx tsc --noEmit -p .` and `npx vitest run` (515 tests) pass on the branch with the vocabulary additions.

| Batch (`data/omics/use-case-coverage-model-execution-20261011-*`) | Source | Tables | Records | Results | Judgements | Gap it addresses |
| --- | --- | --- | --- | --- | --- | --- |
| `clair3gpu` | Zheng et al. 2026, accelerated Clair3, Bioinformatics 42(5) btag181 (CC BY) | Supplementary Tables 1-3 | 408 | 374 | 5 proxy | Peak memory; accuracy beside runtime; deep-learning caller in GPU mode |
| `fp8genomeocean` | Yu et al. 2026, FP8 inference on GenomeOcean, bioRxiv 10.64898/2026.08.09.743676 v1 (CC BY) | Tables 3-4 | 58 | 33 | 2 proxy | Foundation-model execution; peak GPU memory; spread over five trials; power |
| `moderngena` | Aspidova et al. 2026, ModernGENA, bioRxiv 10.64898/2026.04.21.719816 v1 (CC BY) | Appendix B Table 2 | 115 | 92 | 1 proxy | Foundation-model inference throughput and memory-bound batch size, four model families |
| `genepi` | Marangoni et al. 2026, GeNePi, Brief Bioinform 27(1) bbag001 (CC BY) | Supplementary Table S1 | 33 | 20 | 1 direct | Runtime scaling with read depth on stated CPU and GPU nodes |
| `dnascopehybrid` | Hu et al. 2026, DNAscope Hybrid, Front Bioinform 5:1691056 (CC BY) | Table 2 | 34 | 21 | 1 proxy | CPU time and cloud cost for long-read and hybrid pipelines |

Vocabulary additions (in `data/vocab/`, listed in `clair3gpu/coverage.json`): metrics `cpu-time`, `data-io-volume`, `energy-efficiency`, `maximum-batch-size`, `mean-memory`, `power-draw`, `throughput-change`; units `megabyte` (exactMatch QUDT MegaBYTE), `watt` (exactMatch QUDT W), `sample-per-joule`. Tokens per second are recorded under the existing `inference-throughput` metric and `sample-per-second` unit with a `unit_detail`, following its existing use for reads per second.

Records reused, not changed: `lit-genomics-20261011-geneb-model-genomeocean`, `regulatory-variant-20261009-model-gena-lm`, `discovery-model-dnabert-2`, `catalog-model-nt-v2`, `model-execution-20261009-method-gatk-best-practices-cpu`, `model-execution-20261009-method-parabricks`. New families: `model-execution-20261011-model-clair3`, `-model-deepvariant`, `-model-moderngena`, `-method-sentieon-dnascope`.

Archived bytes: article XMLs and the two bioRxiv PDFs (bioRxiv stamps every download, so the PDF hash describes one retrieval; each batch also records the text-layer hash). The two Europe PMC supplementary PDFs are not archived because Europe PMC returns the same bytes on every request.

## Not extracted

| Candidate | Why not |
| --- | --- |
| Sentieon DNAscope LongRead and Hybrid on ONT, bioRxiv 10.1101/2025.11.14.688541 | Compute Table 2 is an image and overlaps the extracted DNAscope Hybrid article by the same vendor authors |
| Monozygotic-twin pipeline comparison, Brief Bioinform bbaf652 (CC BY-NC) | Runtimes only as mean and SD in running text; one caller given only as a ratio; hardware unstated; the figure legend restricts calling runtime to chromosome 20 |
| Layer pruning of DNABERT-2 and NT, Genes 16:1358 (2025) | Fine-tuning and evaluation time over three seeds on older GPUs; training cost, not deployment. Its Tables A1-A3 show identical metrics across seeds, which bears on reproducibility; candidate for a later pass |
| Evo 2 deployment benchmark, bioRxiv 10.1101/2025.09.10.675279 | Posted 2025-09-12, before the window; the strongest foundation-model execution lead if the window is widened |
| Homomorphic inference for a genomic foundation model, arXiv 2609.16211 | One model and one encrypted input; a privacy protocol, not a workflow choice |
| Rethinking DeepVariant, IJMS 27:513 (2026) | Only training time printed |
| OmniReg-GPT 2025; G-VEP 2026; Lancet2 2026; Nallo 2026; CBIcall 2026; long-read SV evaluation bbag530 | Not opened within budget; listed in the ledger gaps |

## Gaps that remain

- No source in the window reruns the same pipeline on the same input and prints concordance of the calls. Run-to-run reproducibility of variant calls is still unmeasured. The only spread now available is over trials of a foundation-model throughput benchmark (Yu et al.) and timing runs (Aspidova et al., mean only).
- No source measures a genomic foundation model inside a diagnostic workflow on human data. The two foundation-model sources are microbial or synthetic timing benchmarks.
- Peak memory is now printed for Clair3 and DeepVariant (Zheng et al.) and for GenomeOcean (Yu et al.), but not for short-read germline pipelines.
- Accuracy beside runtime exists only for Clair3 against DeepVariant on one GIAB sample, in two tables not stated to come from the same runs.
- Costs remain list prices; no source includes licences.

## What needs a reviewer's judgement

1. **Clair3, text against tables.** Results 3.1 give runtimes for apparently the same comparisons that differ from Supplementary Table 2 (for example DeepVariant GPU on ONT: 106 to 128 minutes in the text, 48 to 82 in the table) and call DeepVariant v1.8, while the table and command lines say v1.10-beta. Results 3.2 DeepVariant accuracy at ONT 10x and 20x differs from Supplementary Table 3. Recorded as protocol limitations and a version claim; decide whether a source-level `evidence_concerns` entry is needed (it would withhold all five Clair3 judgements).
2. **Clair3 Tables 2 and 3 are images.** 350 cells were hand-transcribed from 300 dpi renders and read a second time. Every cell needs re-reading from a render of the pinned PDF.
3. **ModernGENA throughput scale.** The printed tokens/s values (for example 552.44 at a batch of 3,631 sequences of 256 tokens) are far below what the batch sizes and the stated pretraining throughput (1.33M tokens/s on eight A100s) imply. The unit may be a scaled rate. Values kept as printed; decide whether this is a source concern.
4. **Units for tokens.** Whether tokens per second may sit under `sample-per-second` (and tokens per watt under the new `sample-per-joule`), or whether token units are needed.
5. **Relevance.** Nine judgements are drafted `proxy` and GeNePi `direct`. Check in particular the Clair3 resource protocols (hardware unstated in the table) and GeNePi (one unnamed sample per depth).
6. **Origin.** Clair3, GenomeOcean, ModernGENA, GENA-LM, GeNePi's Parabricks module and DNAscope are `author_reported`; DeepVariant, DNABERT-2, NTv2 and GeNePi's CPU baseline are `independent_paper`.
7. **New vocabulary** (ten concepts above).
8. **GenomeOcean checkpoints.** The paper names scales only (100M, 500M, 4B); configurations do not name Hugging Face revisions.

## Proposed use-case changes (apply only after review, per docs/use-cases.md)

`links`: append `assessed_by` for the ten new protocols: `model-execution-20261011-protocol-zheng2026-hg003-resource-ont`, `-zheng2026-hg003-resource-pacbio`, `-zheng2026-hg003-clair3-stage-runtime`, `-zheng2026-hg003-accuracy-ont`, `-zheng2026-hg003-accuracy-pacbio`, `-yu2026-genomeocean-embedding-fp8`, `-yu2026-genomeocean-generation-fp8`, `-aspidova2026-a100-inference-throughput`, `-marangoni2026-germline-runtime-by-depth`, `-hu2026-dnascope-azure-compute`.

`source_ids` and `citation_locators`: append the seven new source records with the locators used in each judgement.

`exclusions`: the first two entries ("Any foundation-model inference runtime or throughput benchmark (none is ingested in this bounded intake)" and "Peak memory usage ...") are no longer true once the batches are in; replace with "Foundation-model execution inside a diagnostic workflow on human data (none found in the 2026-10-11 pass)" and keep "Clinical-reporting turnaround time".

`evidence_gaps`: replace the first four entries with:

1. Peak memory is printed only for two long-read callers (Zheng et al. 2026) and for GenomeOcean inference (Yu et al. 2026); no linked short-read germline pipeline prints it.
2. No linked study reruns the same pipeline on the same input and prints concordance of the calls, so run-to-run reproducibility of variant calls is not measured; Yu et al. 2026 print spread over five trials of throughput, and Aspidova et al. 2026 average ten timing runs without spread.
3. Accuracy beside runtime is available only for Clair3 against DeepVariant on HG003 (Zheng et al. 2026), in two tables not stated to come from the same runs.
4. The linked foundation-model execution benchmarks use microbial genomes or fixed-length timing inputs; none measures a genomic foundation model inside a diagnostic workflow on human data.

Keep the cost and joint-aggregation gaps.

`setting`: append "; Clair3 and DeepVariant in GPU mode on HG003 long reads at 10x to 50x (Zheng et al. 2026); Parabricks v4.3.0 on V100 and A100 nodes against CPU GATK at five read depths (Marangoni et al. 2026); three Sentieon DNAscope pipelines on one Azure instance (Hu et al. 2026); and two genomic foundation model inference benchmarks: GenomeOcean in BF16 and FP8 on one H100 (Yu et al. 2026) and ModernGENA, GENA-LM, DNABERT-2 and NTv2 on one A100 (Aspidova et al. 2026)."

`decision`: replace "these are conventional variant-calling pipelines, not foundation-model execution benchmarks, and none reports run-to-run variation or accuracy beside runtime" with "most are conventional variant-calling pipelines; two foundation-model inference benchmarks are outside diagnostic workflows, and none measures run-to-run concordance of variant calls".

`output`, `clinical_scope`: change "no foundation-model execution benchmark" to "no foundation-model execution benchmark inside a diagnostic workflow".

These alter pinned fields, so the existing 14 judgements must be re-pinned in the same change.

## Proposed summary text (draft, for the reviewer; every number is a result in these batches or already in the store)

Replace the second and third sentences of the current summary with: "Most measure conventional variant-calling pipelines; two measure genomic foundation model inference outside any diagnostic workflow. None reruns a pipeline to measure concordance of the calls, and hardware differs within most comparisons, so differences mix software and hardware." Keep the Samarakoon, O'Connell and Franzoso sentences. Then append:

"On HG003 long reads at 30x (Zheng et al. 2026, Clair3 developers, hardware not stated in the table), Clair3 v1.2.0 in GPU mode took 17 minutes on ONT and 12 on PacBio Revio with peak memory of 57,901 and 49,319 MB, and DeepVariant v1.10-beta in GPU mode took 48 and 40 minutes with 60,245 and 57,350 MB; at the same coverage, SNP F1 against GIAB v4.2.1 was 99.58% for Clair3 and 99.70% for DeepVariant on ONT, and 99.85% and 99.88% on PacBio. The Results text gives different runtimes for DeepVariant and names another version. On a regional genomics centre's HPC nodes (Marangoni et al. 2026), a 30x genome took 17h with the CPU GATK equivalent and 1h 36m, 42 m and 30m with Parabricks v4.3.0 on two V100, two A100 and four A100 GPUs, and a 100x genome 60h and 6h 30m, 2h 30m and 2h 06m. On one 120-vCPU Azure instance (Hu et al. 2026, Sentieon authors), DNAscope took 18.9 minutes for 30x Illumina, DNAscope LongRead 41.2 minutes for 30x PacBio and DNAscope Hybrid 85.8 minutes for 10x PacBio plus 35x Illumina, at 1.1, 2.5 and 5.2 USD on demand, excluding the licence. For genomic foundation models on one H100 (Yu et al. 2026, microbial genomes, five trials), GenomeOcean-4B embedding extraction ran at 21,386 ± 126 tokens per second with 72.14 GB peak GPU memory in BF16 and 22,401 ± 204 with 67.91 GB in FP8. On one A100 (Aspidova et al. 2026, ModernGENA and GENA-LM developers), the largest batch of 8,192-token inputs that fit was 92 for ModernGENA base and 5 for DNABERT-2 and NTv2 100M; the printed throughput scale needs checking."

Source locator for the summary: append `model-execution-20261011-source-zheng2026-clair3-supplement: Supplementary Tables 2 and 3; model-execution-20261011-source-marangoni2026-genepi-supplement: Table S1; model-execution-20261011-source-hu2026-dnascope-hybrid: Table 2; model-execution-20261011-source-yu2026-fp8-genomeocean: Table 3; model-execution-20261011-source-aspidova2026-moderngena: Appendix B Table 2`.
