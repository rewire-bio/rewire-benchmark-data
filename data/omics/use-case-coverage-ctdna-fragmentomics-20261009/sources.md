# Sources: plasma ctDNA fragmentomics use-case pass, 2026-10-09

Hashes are SHA-256 of the exact bytes read. Times are UTC. All four sources are CC BY 4.0 (stated in each article's `license` element). The three small artifacts are archived (`gzip -n -9`, in `artifacts/`). The 7.1 MB UNITE data zip is a stable PMC open-access object and is pinned by hash only, to keep the batch small.

| Source ID | What | Version | Retrieved | Artifact URL | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `ctdnafrag-20261009-source-hou2024` | Hou, Meng and Zhou, Systematically Evaluating Cell-Free DNA Fragmentation Patterns for Cancer Diagnosis and Enhanced Cancer Detection via Integrating Multiple Fragmentation Patterns | Advanced Science 11(30):e2308243, 2024-06-17; PMC11321639 full-text XML | 20:27:02 | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11321639/fullTextXML | `d029fc9d593a70fc350fa86cf1c6393ab5121479396b448ea2c0cdd87b6ace70` |
| `ctdnafrag-20261009-source-hou2024-supporting-information` | Hou et al., Supporting Information workbook (Tables S1-S15) | ADVS-11-2308243-s001.xlsx, PMC11321639.1 | 20:20:39 | https://pmc-oa-opendata.s3.amazonaws.com/PMC11321639.1/ADVS-11-2308243-s001.xlsx | `41b24f7e6bcb9bea6127a249127a4c4d53e8ea42b50e95242054791511695fb0` |
| `ctdnafrag-20261009-source-wang2026` | Wang et al., A scalable deep-learning framework for cancer detection using cell-free DNA shallow whole-genome sequencing (UNITE) | Science Advances 12(28):eady9432, 2026-07-10; PMC13353424 full-text XML | 20:27:02 | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13353424/fullTextXML | `61464a274501bb9529b2250eb4c112071b8768fa640e87cf13f14d7df9f6fb23` |
| `ctdnafrag-20261009-source-wang2026-data-file-s2` | Wang et al., Data files S1 and S2 (zip); member `ady9432_data_file_s2.xlsx` read | PMC13353424.1 | 20:23:13 | https://pmc-oa-opendata.s3.amazonaws.com/PMC13353424.1/sciadv.ady9432_data_files_s1_and_s2.zip | zip `d28e1dbf64df93fdefd7dd239ab773088b4f27000807c81dd84b0511c64efe12`; member `32ae4ff3b7e1c85fa8662a57b45f77330e56e475f996f6489f25e36a81de65aa` |

## Evidence concern recorded on a source

| Source | Concern |
| --- | --- |
| `ctdnafrag-20261009-source-hou2024-supporting-information` | For all ten PANCAN patterns, Table S9's SVM "Sensitivity @95% specificity" equals Table S2's "Sensitivity @85% specificity", and S9's 85% values appear nowhere in S2. SVM is the stated primary classifier, so the two tables cannot both be right. AUC columns agree with each other and with article Table 1. Also: S2 LIHC rows print identical 95% and 85% sensitivities for nine of ten patterns, and the S9 WPS logistic-regression row repeats the OCF row. |

Article Table 1 is read from the article XML, a separate source without a concern, so the Table 1 judgement is not withheld by the supplement's concern.

## Reused record

`amp-20261007-ctdna-fragmentomics-dataset` (DELFI 2019 cohort, 208 cancers and 215 healthy individuals) is the data of the Hou et al. Cristiano-cohort evaluations. Its source `amp-20261007-ctdna-fragmentomics-source` is `source_checked` with no evidence concerns.

## Archived copies

| File | SHA-256 of gzip |
| --- | --- |
| `artifacts/hou2024-article.xml.gz` | `cac58f7aa06ffe301b4c4a7e6e7fb04ad85880ceba25bbc5b7d32e15cb0ec7a2` |
| `artifacts/hou2024-supporting-information.xlsx.gz` | `e004099899c3f7e96be8cd011410dd94dc69c624bc12b776cbeb736d42de652a` |
| `artifacts/wang2026-article.xml.gz` | `7ac25165b4eb001a58f41272aa4d5b706edbcf5d8df65cc6ca41753b29630713` |
