# Retrieval log: cell-type annotation transfer use-case pass, 2026-10-09

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Each download went into its own scratch folder and was opened only as data (XML parse, XLSX cell XML parse). No model was run.

| Time (UTC) | Request | Status | Bytes | Result |
| --- | --- | --- | --- | --- |
| 21:18:26 | Europe PMC `PMC8602772/fullTextXML` | 200 | 132,992 | Huang et al. 2021. Screened: figure-only results |
| 21:19:05 | Europe PMC `PMC8427961/fullTextXML` | 200 | 147,658 | Ma et al. 2021. Screened |
| 21:19:13 | Europe PMC `PMC8427961/supplementaryFiles` | 200 | 15,255,387 | Results summary workbook describes experiments; results are in an RDS file |
| 21:21:44 | bioRxiv `2023.10.19.563100.source.xml` | 200 | 113,099 | Boiarsky et al. preprint JATS; all five tables are images |
| 21:22:13-15 | Europe PMC `PMC12492631`, `PMC13170260`, `PMC12365531` full-text XML | 200 each | 354,140; 310,290; 122,266 | Wu et al. 2025 (extracted), scEval and BioLLM (screened) |
| 21:22:24 | Springer ESM `13059_2025_3781_MOESM3_ESM.xlsx` | 200 | 38,926 | Wu et al. Additional file 3. Extracted (Tables S2-S3) |

## How the tables were read

`extract/extract_cell_type.py` reads the XLSX cell XML with the standard library and asserts, for each of Supplementary Tables S2 and S3:

- the title text exactly as printed, and the header row (Model, Accuracy@1, Macro-F1);
- the three section labels in rows 3, 10 and 26 (Individual model, Pairwise ensemble, Full ensemble);
- that rows 4-9 hold exactly the six models, that rows 11-25 hold 15 distinct pairs of those six, that rows 27-28 are Logit aggregation and Majority voting, and that nothing follows row 28;
- two values quoted in the Results text (scGPT 0.674 and Geneformer + scGPT 0.756, Tabula Sapiens to HLCA);
- the direction of the full-ensemble comparison recorded in the evidence concern.

`printed_value` is the shortest decimal that round-trips to the stored number (for example `0.08`, `0.785`).

Run: `python3 -I extract/extract_cell_type.py <article.xml> <MOESM3.xlsx> <batch-dir>`.

## Dry run

`addBatch` from `scripts/omics/records.ts` on a scratch copy of `data/entities`, `data/evidence` and `data/provenance` added 175 records, and `loadRecords` then accepted the store (32,273 records). `deriveUseCaseInputs` produced 2 draft mappings with 23 evaluations each, alongside the 5 existing active mappings. SHACL (`npm run kg:shapes`) was not run.
