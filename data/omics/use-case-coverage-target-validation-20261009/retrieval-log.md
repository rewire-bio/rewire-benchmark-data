# Retrieval log: therapeutic target validation use-case pass, 2026-10-09

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Downloads went to a session scratch directory, one folder per source, and were read as data (PDF text layers via `pdftotext -layout`, XML and XLSX parses for screened candidates). No model, agent or screen was run.

Times are UTC; `~` marks times taken from command order rather than recorded.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| ~20:51:18 | `GET api.biorxiv.org/details/medrxiv/10.1101/2025.09.23.25336370` | 200 | | Ji et al. GWAS prioritisation benchmark; screened |
| ~20:51:20 | `GET export.arxiv.org/api/query?id_list=2405.17631` | 200 | | Resolved version 3 |
| 20:51:27 | `GET arxiv.org/pdf/2405.17631v3` | 200 | 3,953,768 | Roohani et al. 2025; pinned |
| ~20:52:00 | `GET europepmc .../search?query=DOI:"10.1101/2025.09.23.25336370"` | 200 | | PPR1090353, CC BY |
| ~20:52:10 | `GET medrxiv.org/content/10.1101/2025.09.23.25336370v1.full.pdf` | 403 | 4,551 | Blocked; the JATS source XML was taken instead |
| ~20:52:12 | `GET medrxiv.org/content/early/2025/09/25/2025.09.23.25336370.source.xml` | 200 | 58,125 | Ji et al. XML; screened, not extracted |
| ~20:52:20 | `GET medrxiv.org/.../DC1 and DC2/embed/media-{1,2}.xlsx` | 200, 200 | 41,703; 424,303 | Ji et al. supplementary data; screened |
| ~20:52:48 | `GET europepmc .../search?query=CRISPR screen* AND gene prioriti* ...` | 200 | | 18 hits, screened by title |
| ~20:53:30 | `GET api.biorxiv.org/details/biorxiv/10.1101/2025.05.11.653338`; `GET biorxiv .../653338.source.xml` | 200, 200 | ; 115,015 | Liu et al. in-silico perturbation evaluation; tables are page images, screened out |
| ~20:54:39 | `GET export.arxiv.org/api/query?id_list=2110.11875`; `GET arxiv.org/pdf/2110.11875` | 200, 200 | ; 6,851,075 | GeneDisco; no result tables in the text layer, screened out |
| ~20:55:20 | `GET export.arxiv.org/api/query?id_list=2509.21403` | 200 | | Resolved the Gupta preprint behind the ACL version |
| 20:55:36 | `GET aclanthology.org/2025.findings-emnlp.838.pdf` | 200 | 475,883 | Gupta et al. 2025; pinned |
| ~20:55:50 | `GET export.arxiv.org/api/query?id_list=2605.10876`; `GET arxiv.org/abs/2605.10876` | 200, 200 | | Version 1, CC BY 4.0 |
| 20:56:07 | `GET arxiv.org/pdf/2605.10876v1` | 200 | 2,889,050 | De Brouwer et al. 2026; pinned |
| ~20:56:30 | `GET arxiv.org/abs/2405.17631v3` | 200 | | Confirmed CC BY 4.0 |

## How each table was read

All parsing is in `extract/extract_target_validation.py`. Each PDF was converted once with `pdftotext -layout` and the text file is regenerated from the pinned PDF. The text layer sometimes leaves a single space between a row label and its first value, so `split_tail` splits every row from the end: it takes the last *n* whitespace-separated tokens, requires each to match the expected value pattern, and treats the remaining tokens as the label. Lines that do not match are section headings and are asserted against the expected set.

- **Roohani et al. Table 1**: locates the caption, then the header above it; asserts the dataset header (`Model Schmidt1 Schmidt2 CAR-T† Scharen.∗ Carnev. Sanchez`), the `All N/E` header repeated six times, the two section headings (`Baseline Models`, `BioDiscoveryAgent (No-Tools)`), the 20 row labels in order, and 12 values of the form `0.ddd` per row. 240 results. The caption's own mapping is honoured: `Schmidt1` is the interferon-gamma screen and `Schmidt2` the interleukin-2 screen.
- **Gupta et al. Tables 1 and 2**: asserts that four `Method IL2 IFNG Carnevale Sanchez Sanchez Down` headers exist (Tables 1, 2, 3 and the Table 5 ablation), takes the first two, and checks the caption number that follows each. Asserts the backbone section headings, the row labels in order, five values per row, and that the ground-truth row is identical in both tables. Table 2 repeats the `BDA` rows of Table 1; the script asserts the values are equal and lists them in `claims.csv` as `result-duplicate` instead of storing them twice. 55 results.
- **De Brouwer et al. Table 3**: asserts the column header, 48 rows, 16 distinct systems, all three cohorts present for every system, and that `dFDR@100` is `NA` only for the post-cutoff cohort. 144 results, of which 16 are the `NA` cells, stored with `numeric_value` null and an `inapplicable` missing reason.
- **Cross-check against Table 2 of the same preprint**: the 16 test-split rows of Table 2 are matched to Table 3 by system name (`+SFT` and `+SFT+GRPO` resolve to the `GPT-OSS-120B` variants) and all three metric values are asserted equal. Listed in `claims.csv` as `result-duplicate`.
- **Cross-check between sources**: Gupta's "BDA (Reported Numbers)" row divided by its printed ground-truth hit counts was compared with Roohani's all-gene hit ratios for Claude 3.5 Sonnet; the four shared screens agree to the printed rounding. Recorded as a claim.
- **Article text**: hit definitions, thresholds, candidate-pool sizes, batch sizes, run counts and curation steps were read from the sections cited in each record's locator.
