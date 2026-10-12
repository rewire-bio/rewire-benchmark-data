# Retrieval log

| Time (UTC) | Request | Outcome |
| --- | --- | --- |
| 20:50 | Europe PMC search `DOI:"10.1186/s13059-019-1842-9"` | PMC6802306, open access, CC BY |
| 20:53:32 | `GET europepmc/webservices/rest/PMC6802306/fullTextXML` | HTTP 200, 176,473 bytes. Pinned |
| 21:01 | `gh api repos/fusiontranscripts/FusionBenchmarking/git/trees/master?recursive=1` | scripts, truth sets, simulated-data inputs, run times; no AUC or accuracy tables |
| 21:01 | `GET data.broadinstitute.org/Trinity/CTAT_FUSIONTRANS_BENCHMARKING/on_cancer_cell_lines/` | directory index with README.txt only |

## How values were read

`extract/extract_haas2019.py` parses Table 1 from its `<table-wrap>` and asserts each quoted Discussion sentence, on the archived XML (`gzip -dc artifacts/PMC6802306.xml.gz`), checking its SHA-256. No result was extracted; no figure was read.
