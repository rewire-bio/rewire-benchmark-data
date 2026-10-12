# Sources

| Record | Artifact | Version | Retrieved (UTC) | SHA-256 | Licence |
| --- | --- | --- | --- | --- | --- |
| `dna-pathogen-20261012-bertax-source` | Europe PMC full-text XML, https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9436379/fullTextXML | PNAS 119(35):e2122636119, PMC9436379 | 2026-10-12T20:51:54Z | `c0bb2f1bba8680b300076292389b39346ae58bea4bdf28647dd9462333b3bcd7` | CC BY-NC-ND 4.0 |
| `dna-pathogen-20261012-bertax-source-pdf` | PNAS version-of-record PDF, https://www.pnas.org/doi/pdf/10.1073/pnas.2122636119 | 10-page PDF, 1,271,730 bytes | 2026-10-12T20:56:37Z | `7977424613ab5e5f4986745b527a270fd2c0427dbab40471813903eda85dcaec` | CC BY-NC-ND 4.0 |
| `dna-pathogen-20261012-bertax-source-si` | SI Appendix `pnas.2122636119.sapp.pdf`, member of https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9436379/supplementaryFiles | as distributed with PMC9436379, 3,395,065 bytes | 2026-10-12T20:55:54Z | `89a2f86f66cbb2ff17886d413cd89577285086fedd1009e1d9daf87b29fbc1c0` (PDF member) | CC BY-NC-ND 4.0 |

DOI 10.1073/pnas.2122636119. Peer reviewed.

The licence forbids derivatives and commercial use, so no full text is archived. `artifacts/` holds two factual excerpts: the Table 1 text layer as read from the PDF (`table1-pdf-text-layer.txt`, SHA-256 `7be6943e577af1ef383e3b21c835451f93f1e41aac488b1dbc25fce9a053d681`) and the `pdftotext -layout` lines of SI Tables S2 and S5 (`si-tables-s2-s5-pdftotext.txt`, SHA-256 `d5ba7c4b68462e228de514949ad4357ae4e0c6f932dfc79b86cee2ab2b64ee8b`). `extract/extract_bertax.py` runs on these excerpts and reproduces `batch.jsonl` byte for byte.

Not used: the bioRxiv preprint (10.1101/2021.07.09.451778, July 2021) is an earlier version; Dataset S1 (`pnas.2122636119.sd01.xlsx`, SHA-256 `82c3e4f4edaee401689825f50e32848e4b710ab22fdc536b8f1a684dd55a1731`) lists genomes only.
