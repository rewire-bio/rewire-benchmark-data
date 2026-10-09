# Retrieval log: EGFR NSCLC evidence-retrieval use-case pass, 2026-10-09

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Downloads went to a session scratch directory, one folder per source; files were read as data (XML parse, PDF text layer with `pdftotext -layout`, Markdown). No system was run.

Times are UTC; `~` marks times taken from command order rather than recorded.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| ~20:37:40 | `GET europepmc/.../PMC12811686/fullTextXML` | 500 | 150 | Jun et al. 2026; read from the PMC open-data bucket instead |
| ~20:37:45 | `GET pmc-oa-opendata.s3.amazonaws.com/PMC12811686.1/PMC12811686.1.xml` | 200 | 156,018 | Author manuscript (licence code TDM); screened only |
| ~20:38:30 | `GET europepmc/.../PMC12078457, PMC7513637, PMC8574624, PMC7127986, PMC9048643 /fullTextXML` | 200 | | Screening copies |
| ~20:39:00 | `GET pmc-oa-opendata.../41588_2020_603_MOESM3_ESM.xlsx` | 200 | | VICC supplementary tables; screened |
| ~20:39:50 | `GET export.arxiv.org/api/query?id_list=2407.04466` and `arxiv.org/pdf/2407.04466v1` | 200 | ; 2,173,478 | Hisch and Wang 2024; screened |
| 20:40:57 | `GET trec.nist.gov/data/precmed/topics2020.xml` | 200 | 5,524 | Pinned |
| ~20:41:00 | `GET trec.nist.gov/results/trec29/pm/summary.evidence-eval.r1st` | 401 | | Participant-only |
| ~20:41:00 | `gh api repos/usnistgov/trec-browser/contents/.../trec29/pm/{data,overview,results,proceedings,runs,participants}.md?ref=75ec933...` | 200 | | Pinned runs.md; results.md used for cross-checks |
| ~20:41:20 | `GET trec.nist.gov/pubs/trec29/appendices/pm/r1st.pdf` | 200 | 16,808 | Per-topic scores shown only as figures |
| 20:41:38 | `GET trec.nist.gov/pubs/trec29/papers/OVERVIEW.PM.pdf` | 200 | 295,651 | Pinned |
| 20:43:36 | `GET europepmc/webservices/rest/PMC12078457/fullTextXML` | 200 | 98,701 | Pinned; identical to the screening copy |
| ~20:44:40 | `GET europepmc/.../PMC12017742/fullTextXML`; arXiv API 2503.24165 | 200 | | Screened, excluded |

## How each table was read

All parsing is in `extract/extract_egfr_nsclc.py`.

- **Lin et al. Table 1** (`table-wrap id="Tab1"`): asserts both header rows and the three dataset rows. Each mean accuracy is a result; the adjacent 95% CI is its uncertainty; the row's p value is kept in `reported_p_value`. 9 results.
- **Lin et al. Table 2** (`Tab2`): asserts the header and 11 rows. Four rows repeat Table 1 values for the same configuration and dataset; the script asserts equality and lists them in `claims.csv` as `result-duplicate` instead of recording them twice. 7 results.
- **TREC overview Tables 5 and 6**: `pdftotext -layout OVERVIEW.PM.pdf ov.txt` (the text file is regenerated from the pinned PDF). The script locates both captions, the header lines and the metric sub-headers, and asserts five rows per block (Table 5: infNDCG, R-prec, P@10; Table 6: std-gains, exp-gains). Run names printed with spaces are matched to TREC browser run IDs with underscores, and each team name to the run's listed participant. 25 results.
- **Cross-check**: every infNDCG and P@10 value in Table 5 equals the corresponding run summary in the TREC browser `results.md` at the same commit (for 'uog ufmg bg df5', the value of run uog_ufmg_sb_df5). The browser does not list R-prec, so those five cells were not cross-checked. Phase 2 cannot be checked that way: the browser lists `ndcg_cut_10` (evidence-eval), while Table 6 reports NDCG@30.
- **Topics**: asserts 40 topics and that exactly topics 15 and 16 are EGFR (non-small cell lung cancer; afatinib, osimertinib).
