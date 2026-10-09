# Retrieval log: RNA pathogen-detection use-case pass, 2026-10-09

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Each download went into its own folder in a session scratch directory and was opened only as data (XML parse, XLSX cell XML parse). No classifier or pipeline was executed.

Times are UTC request starts. Every request is recorded, including the failures.

| Time | Request | Status | Bytes | Result |
| --- | --- | --- | --- | --- |
| 20:06:32 | `europepmc/.../PMC8953373/fullTextXML` | 200 | 115,810 | Carbo et al. 2022 article XML. Extracted |
| 20:06:39 | `europepmc/.../PMC8953373/supplementaryFiles` | 200 | 220,580 | Truncated zip: no end-of-central-directory record |
| 20:08:48 | same, retried | 200 | 245,132 | Truncated again at a different length |
| 20:14:01 | `mdpi.com/2076-0817/11/3/340/s1` | 403 | 407 | Publisher refused |
| 20:14:08 | `pmc.ncbi.nlm.nih.gov/articles/instance/8953373/bin/pathogens-11-00340-s001.zip` | 200 | 1,817 | Browser challenge page, not the file |
| 20:14:14 | `ncbi.nlm.nih.gov/pmc/articles/PMC8953373/bin/...s001.zip` | 404 | 48,716 | Not found |
| 20:14:42 | `europepmc/.../PMC7615111/fullTextXML` (de Vries published) | 500 | 150 | Server error |
| 20:14:52 | `europepmc.org/articles/PMC7615111?pdf=render` | 403 | 5,551 | Refused |
| 20:14:52 | UCL repository version-of-record PDF | 403 | 4,545 | Refused |
| 20:14:59 | Leiden repository download | 200 | 21,994 | Page titled "Access Blocked" |
| 20:14:59 | `europepmc/.../PMC7615111/fullTextXML`, retried | 500 | 150 | Server error |
| 20:15:12 | `medrxiv.org/.../2021.05.04.21256618v1.full.pdf` | 403 | 4,551 | Refused |
| 20:15:27 | `medrxiv.org/content/early/2021/05/08/2021.05.04.21256618.source.xml` | 200 | 102,148 | de Vries et al. preprint JATS XML (URL from the medRxiv API `jatsxml` field). Extracted |
| 20:15:56 | `medrxiv.org/.../2021.05.04.21256618/DC1/embed/media-1.xlsx` | 200 | 43,106 | de Vries et al. Supplementary Tables 2-4. Extracted |
| 20:16:48 | `medrxiv.org/content/early/2022/01/21/2022.01.21.22269647.source.xml` | 200 | 98,414 | Carbo et al. preprint JATS, to confirm the supplement belongs to the same tables |
| 20:16:56 | `medrxiv.org/.../2022.01.21.22269647/DC1/embed/media-1.xlsx` | 200 | 30,875 | Carbo et al. Supplementary Tables 1-2. Extracted |
| 20:17:31 | `europepmc/.../PMC9007738/supplementaryFiles` | 500 | 10,135 | Server error |
| 20:18:45 | `static-content.springer.com/esm/.../41592_2022_1431_MOESM3_ESM.xlsx` | 200 | 391,621 | CAMI II Supplementary Tables 1-40 (filename from the article XML `<supplementary-material id="MOESM3">`). Extracted |
| 20:19:55 | `europepmc/.../PMC6663916/fullTextXML` | 200 | 143,820 | Brinkmann et al. 2019. Screened, not extracted |
| 20:21:44 | `europepmc/.../PMC9007738/fullTextXML` | 200 | 219,228 | CAMI II article XML. Extracted |

Metadata (DOI, licence, authors, abstract) came from the Europe PMC `search?query=PMCID:...&resultType=core` endpoint for each PMC article, and from `api.biorxiv.org/details/medrxiv/<doi>` for the two preprints (which also gave the licence and the JATS XML URL). `ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi` returned HTTP 404 and was not used again.

## How each table was read

`extract/extract_rna_pathogen.py` reads XLSX cell XML and article XML with the standard library only, and asserts every label it relies on before writing a record. A failed assertion stops the run.

- **Carbo et al. Supplementary Table 1** (sheets `Suppl table 1-Species`, `-Genus`, `-Family`): asserts the sheet names and order, the table title in A1, the level and cut-off headings, each block's pre-processing label (`incl. human reads`, `excl. human reads`, `excl. human reads and normalized`), the thirteen header labels of every block, and that each block's five rows carry the tool labels Centrifuge, CLARK, Kaiju, Kraken2 and GD. The species sheet holds two side-by-side block sets (columns A-M for cut-off 0, P-AB for cut-off 10), handled as separate column maps. Locators give the sheet, block, cell, row label and column label.
- **de Vries et al. Supplementary Table 2**: asserts the title, the two summary column headers (R3, S3), the sample numbers in row 4, the fifteen PCR target labels in row 8, and the pipeline label and "Read count" sub-label of each of the fourteen pipeline rows. Columns N and Q are the second target of the two mixed infections and take their specimen and sample number from the merged cells M and P.
- **de Vries et al. Supplementary Table 4**: asserts the title, the six summary column headers in row 5, the thirteen pipeline rows, and the negative-run-control footnote in C44.
- **Meyer et al. Supplementary Table 39**: asserts the title, the four column headers, the ten submission labels in order, and that every scored cell is exactly `yes` or `no`.

`printed_value` is the cell text for text cells, and for numeric cells the shortest decimal that round-trips to the stored IEEE double (so a stored `76.923076923076934` prints as `76.92307692307693`). Spreadsheet display formatting was not applied. `numeric_value` is the same number as a decimal string, and is null for text cells such as `10, below reporting threshold`, `0**`, `NR`, `partial` and the CAMI `yes`/`no` outcomes.

Run: `python3 -I extract/extract_rna_pathogen.py <download-dir> <batch-dir>`, where the download directory holds the folders named in the table above.

## Checks run after extraction

- Carbo et al.: for each of the 60 rows, the value printed under `Informedness` was compared with sqrt((1 - SN)^2 + (1 - SL)^2) from the same row. All 56 rows whose sensitivity and selectivity are in range agree within 0.0006, which is what identifies that column as the ROC distance. The other 4 rows contain the `10000` cells and were not checked.
- Eight cells across the three sheets print `10000` for quantities bounded by 0 and 1. Each keeps `printed_value` `10000`, has a null `numeric_value` and carries `source_anomaly`.
- Dry run: `addBatch` from `scripts/omics/records.ts` on a scratch copy of `data/entities`, `data/evidence` and `data/provenance` added 1,177 records, and `loadRecords` then accepted the store (30,621 records). `deriveUseCaseInputs` produced 7 draft mappings for this use case alongside the existing active UCSF mapping. SHACL (`npm run kg:shapes`) was not run.
