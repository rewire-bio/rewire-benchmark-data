# QA fixes for issues #88 (part b) and #89, 2026-10-10

Records were edited in place by replacing the exact JSON string of one field per record (`apply_fixes.py`, run from the repository root). No other byte of the store changed. Each changed field has a metadata-correction claim in `batch.jsonl` that keeps the previous text. Provenance has not been updated: `npm run records -- change` and `records -- add` have not been run.

## #88 (b): citation suffix removed from method and model descriptions

30 records (24 methods, 6 models) had a description ending in the suffix pattern `\((?:[A-Z][a-z]+ et al\.|[A-Z][a-z]+) \d{4}[a-z]? (?:Table|Supp)[^)]*\)\.?$`. The brief estimated about 32; the pattern matches 30 method and model records. No pipeline or service matches. Configurations were not checked or changed.

Every cited author and year in each suffix already had a matching record in `source_ids`, so no source was added.

| Record | Kind | Cited | New description |
| --- | --- | --- | --- |
| `rna-fusion-20261009-method-arriba` | method | Tamura 2026 | Short-read fusion caller using STAR alignments. |
| `rna-fusion-20261009-method-ericscript` | method | Tamura 2026 | Short-read fusion caller using BWA and BLAT alignments. |
| `rna-fusion-20261009-method-genomon` | method | Tamura 2026 | Fusion detection in the Genomon pipeline using STAR alignments. |
| `rna-fusion-20261009-method-infusion` | method | Tamura 2026 | Short-read fusion caller using Bowtie2 alignments. |
| `rna-fusion-20261009-method-pizzly` | method | Tamura 2026 | Short-read fusion caller using kallisto pseudoalignment. |
| `rna-fusion-20261009-method-star-fusion` | method | Tamura 2026 | Short-read fusion caller using STAR alignments. |
| `rna-fusion-20261009-method-starchip` | method | Tamura 2026 | Short-read fusion caller using STAR alignments. |
| `rna-fusion-20261009-method-trinityfusion` | method | Tamura 2026 | Fusion caller using de novo transcript assembly, alone (mode D) or with STAR alignments (modes UC and C). |
| `somatic-20261009-method-deepsomatic` | method | Guille 2025 | Neural-network somatic SNV and indel caller. |
| `somatic-20261009-method-freebayes` | method | Guille 2025 | Haplotype-based caller not designed for somatic calling, used here with tumour-normal filtering. |
| `somatic-20261009-method-lancet` | method | Guille 2025 | Somatic SNV and indel caller using joint genotype analysis. |
| `somatic-20261009-method-lofreq` | method | Guille 2025 | Somatic SNV and indel caller using allele-frequency analysis. |
| `somatic-20261009-method-muse` | method | Guille 2025 | Somatic SNV caller using a Markov chain model. |
| `somatic-20261009-method-mutect` | method | Guille 2025; Wang 2020 | Somatic SNV caller using haplotype analysis; MuTect version 1. |
| `somatic-20261009-method-mutect2` | method | Guille 2025; Wang 2020 | GATK somatic SNV and indel caller using haplotype analysis. |
| `somatic-20261009-method-pindel` | method | Guille 2025 | Indel caller using heuristic thresholds, not designed for somatic calling, used here with tumour-normal filtering. |
| `somatic-20261009-method-scalpel` | method | Guille 2025 | Indel caller using micro-assembly. |
| `somatic-20261009-method-seurat` | method | Guille 2025 | Somatic SNV and indel caller using joint genotype analysis. |
| `somatic-20261009-method-shimmer` | method | Guille 2025 | Somatic SNV caller using heuristic thresholds. |
| `somatic-20261009-method-somaticsniper` | method | Guille 2025 | Somatic SNV caller using joint genotype analysis. |
| `somatic-20261009-method-vardict` | method | Guille 2025 | SNV and indel caller using heuristic thresholds. |
| `somatic-20261009-method-varnet` | method | Guille 2025 | Neural-network somatic SNV and indel caller. |
| `somatic-20261009-method-varscan` | method | Guille 2025 | SNV and indel caller using heuristic thresholds; VarScan 2 releases. |
| `somatic-20261009-method-virmid` | method | Guille 2025 | Somatic SNV caller using joint genotype analysis. |
| `regulatory-variant-20261009-model-borzoi` | model | Manzo 2025 | Model trained to predict RNA-seq coverage from DNA sequence. |
| `regulatory-variant-20261009-model-caduceus` | model | Manzo 2025 | Self-supervised DNA language model pretrained on human genomic sequence. |
| `regulatory-variant-20261009-model-enformer` | model | Manzo 2025; Tang 2025 | Convolution and Transformer model trained to predict genomic tracks from sequences of up to about 200 kb. |
| `regulatory-variant-20261009-model-gena-lm` | model | Manzo 2025 | Transformer DNA language models in BERT-base, BERT-large and BigBird variants. |
| `regulatory-variant-20261009-model-hyenadna` | model | Manzo 2025 | DNA language model pretrained on the human reference genome with context lengths of 32 kb to 1 Mb. |
| `regulatory-variant-20261009-model-sei` | model | Manzo 2025 | Supervised sequence model pretrained on 21,907 chromatin profiling datasets (Tang et al. 2025 Results), built from residual dilated convolutions. |

Left as is: `regulatory-variant-20261009-model-sei` keeps an inner citation, '(Tang et al. 2025 Results)', in the middle of its sentence. Only the trailing suffix was removed, as briefed.

## #89: CNV judgement reasons rewritten

Only `attributes.reason` changed; a check confirmed every other field is byte-identical. None of the three claims has `pins`. All three still carry `reviewed_evaluations` from the earlier review, which was left unchanged.

### `use-case-mapping-cnv-20261009-delavega2025-coriell-panel`

Previous: Recorded from the CNV use-case pass 2026-10-09. Held as draft: the article source carries an evidence concern (Results 3.1 prose disagrees with Supplemental Table 3 on CNVnator 1-5 kb detection and on which caller has the lowest precision), which blocks active applicability.

New: Not shown: the article's Results text and its Supplemental Table 3 disagree on whether CNVnator detected 1-5 kb events and on which caller had the lowest precision. The conflict is in the HG002 table, not in this panel table, but it applies to the whole article, so these precision values are not shown until it is resolved.

### `use-case-mapping-cnv-20261009-delavega2025-hg002`

Previous: Recorded from the CNV use-case pass 2026-10-09. Held as draft: the article source carries an evidence concern (Results 3.1 prose disagrees with Supplemental Table 3 on CNVnator 1-5 kb detection and on which caller has the lowest precision), which blocks active applicability.

New: Not shown: the article's Results text and its Supplemental Table 3 disagree on whether CNVnator detected 1-5 kb events and on which caller had the lowest precision. The values here are recorded as printed in the tables, but they are not shown until that conflict is resolved.

### `use-case-mapping-cnv-20261009-nardone2025-hg002-deletions`

Previous: Recorded from the CNV use-case pass 2026-10-09. Held as draft: the source carries evidence concerns (input depth and aligner conflict; prose and table disagree), which block active applicability.

New: Not shown: the paper states the read depth and aligner behind Table S1 inconsistently (25x with bwa-mem2 in Methods, the DRAGEN pipeline in Results, 30x reads in Data Availability), and its text and Table S1 disagree for inGAP at 5,000-9,999 bp. The table values are recorded, but they are not compared with other HG002 tables until this is resolved.

The facts used are the evidence concerns on `cnv-20261009-source-delavega2025`, `cnv-20261009-source-nardone2025` and `cnv-20261009-source-nardone2025-table-s1`, and the claims' own endpoint and limitations.

## #88 (b) follow-up: 18 more author-year citations

The review (`review.md`, 'Not covered by this fix') listed 18 method and model descriptions with a trailing or mid-sentence author-year citation that the original pattern missed. `apply_fixes_18.py` edits only these 18 records; the 33 earlier changes and the reviewer's edits to them are untouched. Each old text was asserted equal to the working-tree description before the edit.

18 records changed (13 methods, 5 models). Only `description` changed, except one `source_ids` addition. 18 correction claims were appended to `batch.jsonl` (now 51 lines), each with `previous_value` equal to the working-tree text before this edit.

### Cited sources

- Added: `amp-20261007-ctdna-fragmentomics-source` (Cristiano et al. 2019) to `ctdnafrag-20261009-method-delfi`.
- No existing source record, so `source_ids` was left unchanged: Adalsteinsson et al. 2017 (ichorCNA), Houseman 2012 (Houseman CP), Boix et al. 2021 (EpiMap), Nurtdinov and Guigó 2025 (EPIraction), Rentzsch et al. 2019 (CADD). These are the methods' original papers; the citation text is kept in each correction claim's `previous_value`. Adding them would need new source records with retrieved artifacts.
- All other cited works were already in `source_ids`.

### Rewording where a fact went with the citation

- Fusilli: 'developed by the authors of Lin et al. 2026' became 'developed by the authors of the comparison that evaluated it'.
- TREDNet: 'from the group of the Manzo et al. senior author' became 'developed by the group of the senior author of the comparison that evaluated it'.
- NeuSomatic: 'run in ensemble mode over other callers' output by Wang et al. 2020' became 'in one linked comparison it was run in ensemble mode over other callers' output'.
- Strelka: 'versions 2.7.1 (Wang et al. 2020) and 2.9.2 (Guille et al. 2025)' became 'versions 2.7.1 and 2.9.2 were evaluated in the linked comparisons'. Which version each study used is on the configuration records.
- EPIraction: 'bioRxiv 2025' became 'released as a 2025 preprint'.
- GPT-4o, Llama 3.1 70B and Qwen 2.5 72B: 'as used by Lin et al. 2025' became 'the evaluated version' or 'in the evaluated runs'.

| Record | Kind | Cited | New description |
| --- | --- | --- | --- |
| `ctdnafrag-20261009-method-delfi` | method | Cristiano et al. 2019; Hou et al. reference 45 | Short-to-long fragment ratios in 5 Mb bins. The method record names the feature definition, not an implementation. |
| `ctdnafrag-20261009-method-ichorcna` | method | Adalsteinsson et al. 2017 | Copy-number-based tumour fraction estimation from ultra-low-pass WGS. |
| `ctdnameth-20261009-method-houseman-cp` | method | Houseman 2012 | Constrained projection least-squares deconvolution, run through the EpiDISH R package. |
| `regulatory-variant-20261009-method-epimap` | method | Boix et al. 2021; Gschwind et al. reference 8 | Enhancer-gene links from the EpiMap integrative epigenomics resource. |
| `regulatory-variant-20261009-method-epiraction` | method | Nurtdinov and Guigó, bioRxiv 2025; Gschwind et al. reference 27 | Atlas of candidate enhancer-gene interactions, released as a 2025 preprint. |
| `rna-fusion-20261009-method-fusilli` | method | Lin et al. 2026 | Long-read fusion caller that keeps reads spanning two genes from a B-ALL gene list and fusions on a B-ALL fusion list, with distance, overlap, breakpoint and two-read filters; developed by the authors of the comparison that evaluated it. |
| `rna-fusion-20261009-method-fusioncatcher` | method | Tamura et al. 2026 | Short-read fusion caller using several aligners (STAR, Bowtie and BLAT). |
| `rna-fusion-20261009-method-fusionseeker` | method | Lin et al. 2026 | Long-read fusion caller that clusters candidate fusions from BAM alignments and filters them by supporting reads. |
| `rna-fusion-20261009-method-jaffa` | method | Tamura et al. 2026; Lin et al. 2026 | Fusion caller using alignment to a transcriptomic reference: JAFFA-direct for short reads (BLAT, Bowtie2 and BLAST+) and JAFFAL for long reads, which filters candidates by alignment to the genome. |
| `rna-fusion-20261009-method-longgf` | method | Lin et al. 2026 | Long-read fusion caller that compares reads mapped to a reference against a GTF and filters supporting reads. |
| `somatic-20261009-method-neusomatic` | method | Guille et al. 2025; Wang et al. 2020 | Neural-network somatic SNV and indel caller; in one linked comparison it was run in ensemble mode over other callers' output. |
| `somatic-20261009-method-strelka` | method | Guille et al. 2025; Wang et al. 2020 | Somatic SNV and indel caller using allele-frequency analysis; versions 2.7.1 and 2.9.2 were evaluated in the linked comparisons. |
| `somatic-oncogenicity-20261009-method-cadd` | method | Rentzsch et al. 2019, Nucleic Acids Research 47:D886 | Combined Annotation-Dependent Depletion: a genome-wide variant deleteriousness score that integrates more than 60 genomic features in a machine learning model trained to separate simulated de novo variants from variants fixed in human populations since the human-chimpanzee split. It scores single nucleotide variants and short insertions and deletions anywhere in the reference assembly, not only missense variants. |
| `egfrnsclc-20261009-model-gpt-4o` | model | Lin et al. 2025 | Proprietary model; the evaluated version, 2024-05-13, was used through the Azure OpenAI API. |
| `egfrnsclc-20261009-model-llama-3-1-70b` | model | Lin et al. 2025 | Open-weight model; in the evaluated runs it was served with Ollama. |
| `egfrnsclc-20261009-model-qwen-2-5-72b` | model | Lin et al. 2025 | Open-weight model; in the evaluated runs it was served with Ollama. |
| `regulatory-variant-20261009-model-gpn` | model | Tang et al. 2025 | Masked DNA language model; variant effects scored by single-nucleotide masking. |
| `regulatory-variant-20261009-model-trednet` | model | Manzo et al. 2025 | Two-phase CNN for enhancer prediction and variant prioritisation, developed by the group of the senior author of the comparison that evaluated it. |

### Still carrying a citation (outside this brief, not changed)

A looser scan after this edit finds author-year text in 7 more method descriptions: `dna-pathogen-20261009-method-kraken` ('cited as Wood and Salzberg 2014'), `regulatory-variant-20261009-method-distance-to-tss`, `regulatory-variant-20261009-method-ep-dnase-correlation` ('computed by Gschwind et al. 2026 ...'), `regulatory-variant-20261009-method-residualbind` ('defined by Tang et al. 2025 ...'), and three `ucc-research-method-abdelaal-*` records ('Method identity used in the Abdelaal et al. 2019 comparison', which is also placeholder text). Nine TREC 2020 records match the scan only because of the track name; they carry no citation.
