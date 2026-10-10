# Retrieval log: genetic perturbation response use-case pass, 2026-10-09

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Each download went into its own scratch folder and was opened only as data (XML parse, XLSX cell XML parse, `pdftotext`). No model was run.

| Time (UTC) | Request | Status | Bytes | Result |
| --- | --- | --- | --- | --- |
| 20:53:06 | Europe PMC `PMC12328236/fullTextXML` | 200 | 141,399 | Ahlmann-Eltze et al. 2025. No tables in the article |
| 20:53:18 | Europe PMC `PMC12328236/supplementaryFiles` | 200 | 4,590,835 | Truncated zip (no end-of-central-directory record) |
| 20:58:26-27 | Springer ESM `41592_2025_2772_MOESM3_ESM.xlsx`, `MOESM4` | 200, 200 | 1,659,842; 1,837,063 | Fig. 1 and Fig. 2 Source Data: per-perturbation, per-seed rows |
| 20:58:48 | Europe PMC `PMC12016270/fullTextXML` | 200 | 83,076 | Csendes et al. 2025 article. Extracted |
| 20:58:56 | Europe PMC `PMC12016270/supplementaryFiles` | 200 | 5,821,018 | Bundle holding `12864_2025_11600_MOESM4_ESM.xlsx`. Extracted |
| 21:00:34 | Europe PMC `PMC13271886/fullTextXML` | 200 | 171,232 | Systema. Screened |
| 21:00:35 | Europe PMC `PMC13557097/fullTextXML` | 200 | 299,503 | Li et al. 2026. Screened |
| 21:00:43 | Springer ESM `41587_2025_2777_MOESM1_ESM.pdf` | 200 | 47,199,697 | Systema Supplementary Information; tables are gene-level |
| 21:00:54 | Europe PMC `PMC13557097/supplementaryFiles` | 200 | 112,251,239 | Li et al. supplement; tables describe datasets and models |
| 21:03:38-42 | Springer ESM `41592_2025_2772_MOESM5`-`MOESM12` | 200 each | 12,640 to 10,905,628 | Extended Data Source Data for Ahlmann-Eltze et al.: per-perturbation or per-gene rows, curve points and compute logs; no per-method summary table |

## How the tables were read

`extract/extract_perturbation.py` reads the XLSX cell XML with the standard library and asserts, before writing any record:

- the sheet names `Supplementary Table 1` to `3`;
- Supplementary Table 1 headers, dataset labels (adamson, norman, replogle_k562, replogle_rpe1) and the Norman subgroup labels and rows;
- the eight Supplementary Table 2 headers exactly as printed (including the trailing space in `Pearson Delta `);
- that rows 2-61 hold the 4 datasets by 15 models in the printed order, with nothing after row 61;
- that the 8 Wilcoxon cells for scGPT and scFoundation are blank;
- that the Train Mean, scGPT, scFoundation and RF_go Pearson Delta values round to the 16 values printed in Results paragraph 6.

`printed_value` is the shortest decimal that round-trips to the stored double (stored `0.71114800000000005` gives `0.711148`).

Run: `python3 -I extract/extract_perturbation.py <article.xml> <MOESM4.xlsx> <batch-dir>`.

## Dry run

`addBatch` from `scripts/omics/records.ts` on a scratch copy of `data/entities`, `data/evidence` and `data/provenance` added 447 records, and `loadRecords` then accepted the store (30,818 records). `deriveUseCaseInputs` produced 4 draft mappings with 15 evaluations each, alongside the 3 existing active mappings. SHACL (`npm run kg:shapes`) was not run.
