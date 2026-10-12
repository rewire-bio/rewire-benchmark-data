# Retrieval log

| Time (UTC) | Request | Outcome |
| --- | --- | --- |
| 20:50 | Europe PMC search `DOI:"10.1186/s12859-024-05760-3"` | PMC11022314, open access, CC BY |
| 20:50:20 | `GET europepmc/webservices/rest/PMC11022314/fullTextXML` | HTTP 200, 101,923 bytes. Pinned |
| 20:51:53 | `GET .../PMC11022314/supplementaryFiles` | HTTP 200 ZIP, 11 members, all figure or equation images; nothing pinned |
| 21:00 | `gh api repos/csb5/MetageNN` tree at d7c858c | code, settings, genome and SRA lists; no result files |

## How values were read

`extract/extract_metagenn.py` parses Table 1 from its `<table-wrap>` (caption, header and the six method labels asserted) and asserts the exact Results sentence before writing each prose value. It runs on the archived XML (`gzip -dc artifacts/PMC11022314.xml.gz`) and checks its SHA-256. No value was read from a figure.
