# AMP issue #14: UCSF respiratory RNA mNGS original-testing sensitivity

Candidate only. Tan et al., Nature Communications 15, 9016 (2024). DOI 10.1038/s41467-024-51470-y

Endpoint: 93.6% (103 of 110) percent; uncertainty: null (not extracted/reported). Numerator 103; denominator 110.

Locator: PMC11558004 Results paragraph Par15; Table 1 Tab1 Accuracy / Original testing; Fig. 6A. Methods Par34 and Par38 define reference assays and mixed-target weighting.

Population: 191 residual UCSF clinical samples: 110 RVP-virus-positive, 81 negative. Results says positive 104 upper respiratory swabs + 6 BAL; Methods instead 103 + 7, retained unresolved.

Workflow: RNA isolation with DNase, rRNA depletion and cDNA synthesis; Tecan MagicPrep NGS; Illumina MiniSeq/NextSeq; SURPI+ container v1.0.0, SNAP edit distance 16 against March 2019 NCBI NT viral reference augmented by SARS-CoV-2 NC_045512.

Split: Residual clinical accuracy cohort; no model training/test split reported

Conventional baseline: Original clinical RVP assays: GenMark ePlex, Luminex NxTAG and/or Verigene RP Flex. Same cohort specificity 93.8% (76/81), accuracy 93.7% (179/191). DTCA agreements are separate endpoints and excluded.

Retrieval: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11558004/fullTextXML at 2026-10-07T12:24:59.206377+00:00; SHA-256 4b701cdeaf16c948591a34576390dbaed033a123ea9c8bace661b6822889abf6.

Limitations:

- RNA-only specimen preparation supports RNA pathogen-detection workflow; tested target mix includes adenovirus, a DNA virus detected via transcription. Do not describe the 93.6% as a pure RNA-virus-only subgroup score.

- Multiple detected targets are weighted so each specimen contributes one observation; out-of-panel mNGS positive calls are not counted as false positives.

- Positive-specimen BAL/swab count disagreement in Results vs Methods remains unresolved; total 110 positives and 81 negatives agree.

- No confidence interval extracted for original sensitivity. After selective discrepancy adjudication, report PPA/NPA rather than sensitivity; DTCA measurements must remain separate.

- No foundation model or independent external replication; clinical residual-sample validation study supplies conventional baseline evidence.

No matching DOI/workflow found in baseline-catalogue.json or both 2026-10-07 archived record bundles; no existing identity reused.

Candidates remain needs_review pending parent source check.
