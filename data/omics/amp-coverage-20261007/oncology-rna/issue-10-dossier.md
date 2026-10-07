# AMP #10: Tumour DNA somatic small variant detection

Primary source: Genome-wide somatic variant calling using localized colored de Bruijn graphs. https://doi.org/10.1038/s42003-018-0023-9
Retrieved: 2026-10-07T12:24:27.822425+00:00; source-byte SHA256: 08fa271d01e0583f570c97dd0d260073caf8f48877fa9f6d6eabc858b6e518d5

Evidence scope: synthetic-tumour proxy using real reads

Separate SNV and indel virtual-tumor pairs; real germline-supporting reads swapped at reference-homozygous/alternate-homozygous loci; binomial VAF means 0.05, 0.1, 0.2, 0.3; insertion max 13 bp, deletion max 35 bp.

Population: 31,592 spiked SNVs; 4,945 spiked indels; NA12892 and NA12891 HapMap samples
Input: Illumina HiSeq X PCR-free WGS, 80× virtual tumor and 40× normal

## Numerical extraction

- Lancet: SNV F1-score = 0.85 fraction; Table 2, Lancet row (JATS Tab2). Uncertainty: None.
- Lancet: SNV recall = 0.75 fraction; Table 2, Lancet row (JATS Tab2). Uncertainty: None.
- Lancet: SNV precision = 0.98 fraction; Table 2, Lancet row (JATS Tab2). Uncertainty: None.
- Lancet: SNV true positives = 23,848 variants; Table 2, Lancet row (JATS Tab2). Uncertainty: None.
- Lancet: SNV false positives = 565 variants; Table 2, Lancet row (JATS Tab2). Uncertainty: None.
- Lancet: SNV false negatives = 7744 variants; Table 2, Lancet row (JATS Tab2). Uncertainty: None.
- Lancet: indel F1-score = 0.81 fraction; Table 1, Lancet row (JATS Tab1). Uncertainty: None.
- Lancet: indel recall = 0.72 fraction; Table 1, Lancet row (JATS Tab1). Uncertainty: None.
- Lancet: indel precision = 0.92 fraction; Table 1, Lancet row (JATS Tab1). Uncertainty: None.
- Lancet: indel true positives = 3586 variants; Table 1, Lancet row (JATS Tab1). Uncertainty: None.
- Lancet: indel false positives = 305 variants; Table 1, Lancet row (JATS Tab1). Uncertainty: None.
- Lancet: indel false negatives = 1359 variants; Table 1, Lancet row (JATS Tab1). Uncertainty: None.
- Strelka2: SNV F1-score = 0.85 fraction; Table 2, Strelka2 row (JATS Tab2). Uncertainty: None.
- Strelka2: SNV recall = 0.76 fraction; Table 2, Strelka2 row (JATS Tab2). Uncertainty: None.
- Strelka2: SNV precision = 0.96 fraction; Table 2, Strelka2 row (JATS Tab2). Uncertainty: None.
- Strelka2: SNV true positives = 24,132 variants; Table 2, Strelka2 row (JATS Tab2). Uncertainty: None.
- Strelka2: SNV false positives = 1117 variants; Table 2, Strelka2 row (JATS Tab2). Uncertainty: None.
- Strelka2: SNV false negatives = 7460 variants; Table 2, Strelka2 row (JATS Tab2). Uncertainty: None.
- Strelka2: indel F1-score = 0.77 fraction; Table 1, Strelka2 row (JATS Tab1). Uncertainty: None.
- Strelka2: indel recall = 0.73 fraction; Table 1, Strelka2 row (JATS Tab1). Uncertainty: None.
- Strelka2: indel precision = 0.81 fraction; Table 1, Strelka2 row (JATS Tab1). Uncertainty: None.
- Strelka2: indel true positives = 3647 variants; Table 1, Strelka2 row (JATS Tab1). Uncertainty: None.
- Strelka2: indel false positives = 867 variants; Table 1, Strelka2 row (JATS Tab1). Uncertainty: None.
- Strelka2: indel false negatives = 1298 variants; Table 1, Strelka2 row (JATS Tab1). Uncertainty: None.

## Baselines

- Strelka2 (same-table numeric rows provided)
- Strelka, MuTect, MuTect2, LoFreq (Tables 1–2; not all transcribed)

## Limits and unknowns

- Author-developed-caller evaluation, not independent reproduction.
- Virtual tumor endpoint does not establish sensitivity in clinical tumors, FFPE samples, panels, ctDNA, copy-number or structural variation.
- SNV printed counts agree with 31,592 truth variants. Do not repair MuTect table #calls=50,228 versus TP+FP=26,505; its row is not proposed for numerical ingestion.
- Indel Lancet and Strelka2 counts agree with 4,945 truth variants. Preserve Table 1 rounding and do not recompute percentages.
- Individual-condition confidence intervals unreported in Tables 1–2.

Missing metadata: {"version": "Caller releases require supplemental extraction", "metric_implementation": "Exact filtering/matching implementation not extracted", "budget": "Not extracted"}

Candidate status is needs_review. Main text/XML inspected by automated curator; no experimental reproduction or human scientific review. No clinical benefit claimed. See candidates.json for integration metadata.
