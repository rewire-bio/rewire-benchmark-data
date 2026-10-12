# Retrieval log

| Time (UTC) | Request | Outcome |
| --- | --- | --- |
| 20:50 | Europe PMC search `DOI:"10.1073/pnas.2122636119"` | PMC9436379, open access, licence cc by-nc-nd |
| 20:51:54 | `GET europepmc/webservices/rest/PMC9436379/fullTextXML` | HTTP 200, 121,636 bytes. Pinned. Table 1 is a `<graphic>` (`table1.jpg`), not a table |
| 20:51 | `GET .../PMC9436379/supplementaryFiles` with a 120 s limit | timed out |
| 20:52-20:53 | `europepmc.org/articles/PMC9436379/bin/...`, `pmc.ncbi.nlm.nih.gov/articles/instance/9436379/bin/...`, PMC CDN, `europepmc.org/backend/ptpmcrender.fcgi` | HTML challenge pages or HTTP 403/404; nothing pinned |
| 20:53 | `api.unpaywall.org/v2/10.1073/pnas.2122636119?email=research-agent@example.invalid` | publisher (CC BY-NC-ND), bioRxiv preprint (earlier version), PMC |
| 20:54 | `GET www.pnas.org/doi/pdf/10.1073/pnas.2122636119` with curl | HTTP 403 |
| 20:55:54 | `GET .../PMC9436379/supplementaryFiles` with a 500 s limit | HTTP 200 ZIP, 3,685,907 bytes, 12 members. SI PDF member pinned |
| 20:56 | Claude in Chrome: opened https://www.pnas.org/doi/full/10.1073/pnas.2122636119; the HTML Table 1 is also an image | |
| 20:56:37 | In the same page, `fetch('/doi/pdf/10.1073/pnas.2122636119')` | HTTP 200, `%PDF-1.4`, 1,271,730 bytes; SHA-256 computed with `crypto.subtle`. Text layer read with pdf.js 4.0.379 (cdnjs). Table 1 is text on page 4. Bytes not saved to disk |

## How values were read

- Table 1: the page-4 text layer from pdf.js, copied to `artifacts/table1-pdf-text-layer.txt`. The extractor asserts the title, the dataset and rank header lines, the nine tool labels (with the two `MMseqs2+` rows split over lines) and seven two-decimal values per row. The `random` row is a chance reference and was not extracted.
- SI Tables S2 and S5: `pdftotext -layout` (poppler 26.08.0) of the pinned SI PDF; the extractor asserts captions, header lines, tool labels and field counts.
- No value was read from an image.

A reviewer cannot re-fetch the PNAS PDF with curl. Use a browser and compare the SHA-256 above, or check Table 1 against the archived excerpt and Table S7 (its BERTax row repeats Table 1's BERTax values on the distantly related and final datasets).
