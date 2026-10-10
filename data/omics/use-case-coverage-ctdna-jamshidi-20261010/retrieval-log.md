# Retrieval log: CCGA substudy 1 follow-up pass, 2026-10-10

Worker: Claude (Opus 5.5) research agent in Claude Code. No human review claimed. Downloads went to a session scratch directory, one folder per artifact, and were read as data (`pdftotext -layout`, Python under `-I`). No classifier was run. Times are UTC.

| Time | Request | HTTP | Bytes | Result |
| --- | --- | --- | --- | --- |
| 06:04:01 | Europe PMC search `DOI:"10.1016/j.ccell.2022.10.022"` | 200 | | MED 36400018; licence CC BY-NC-ND; not in PMC; no full text in Europe PMC |
| 06:04:11 | Europe PMC `MED/36400018/fullTextXML` | 404 | 140 | No full text |
| 06:04:11 | Europe PMC render API `fulltextRepo?pprId=36400018` | 500 | 55 | No preprint render |
| 06:04:11 | `europepmc.org/article/MED/36400018` | 403 | 5,720 | Browser challenge |
| 06:04:12 | Europe PMC `MED/36400018/supplementaryFiles` | 404 | 147 | No supplementary files |
| 06:04:12 | `doi.org/10.1016/j.ccell.2022.10.022` | 200 | 2,980 | Redirect page to linkinghub (PII S153561082200513X) |
| 06:04:12 | `cell.com` full text and `showPdf` | 403, 403 | | Publisher refused |
| 06:04:13 | Elsevier article API by DOI | 200 | 1,932 | Body not kept; a retry at 06:04:27 returned 429 |
| ~06:04:15 | Crossref works record | 200 | | Licences include CC BY-NC-ND 4.0 |
| ~06:04:20 | PMC ID converter for PMID 36400018 | 200 | | "Identifier not found in PMC" |
| 06:04:21 | Elsevier article API by PII | 429 | 180 | Rate limited |
| 06:04:21 | ScienceDirect article and `pdfft` | 403, 403 | | Refused |
| 06:04:34 | Europe PMC preprint search (title, or Jamshidi with CCGA) | 200 | | 0 hits; no bioRxiv or medRxiv preprint found |
| 06:04:50 | Web search for open copies (ledger q3) | | | UCL Discovery and Crick records named |
| 06:04:50 | `discovery.ucl.ac.uk/id/eprint/10162940/` | 403 | 5,744 | Browser challenge |
| 06:04:56 | UCL staging record and export | 403, 401 | | Refused |
| 06:04:56 | OpenAlex work record | 200 | 60,976 | Lists the Crick figshare deposit |
| 06:04:57 | Unpaywall record (with the required email parameter) | 200 | 11,247 | Lists the same figshare deposit, CC BY-NC-ND |
| 06:05:11 | figshare API `articles/21731870` | 200 | 13,314 | One file, `1-s2.0-S153561082200513X-main.pdf`, 2,459,162 bytes, MD5 given |
| 06:05:17 | `ndownloader.figshare.com/files/38559380` | 200 | 2,459,162 | Publisher PDF; MD5 matches; extracted |
| 06:07:04 | Elsevier supplement `mmc1.pdf` (probe, then download at 06:07:12) | 200 | 494,308 | Tables S1 and S2, Figures S1 to S8; read, not extracted |
| 06:07:12 | Elsevier supplement `mmc2.pdf` (probe only) | 200 | 2,970,693 | Not kept |
| 06:07:13 | Elsevier supplement `mmc3.pdf` | 404 | 189 | None |

No secondary summary was used: every value comes from the article PDF.

## How each value was read

All parsing is in `extract/extract_ctdna_jamshidi.py`.

- **Table 3**: locates the caption and the footnote block, matches each row with one regular expression (assay, classifier, training sensitivity with CI or `N/A`, training TP/total, validation sensitivity with optional significance mark and CI, validation TP/total), and asserts the ten classifier labels and assay column in order, that only the pan-feature row lacks training values, the denominators (833 and 464; 815 and 457 for the clinical classifier), and that every printed percentage equals TP/total rounded to its printed precision. Footnote sentences giving observed specificity and the McNemar marks are asserted. 19 results.
- **Cancer signal origin**: asserts the Results lines giving 75% (95/127), 41% (52/127) and 35% (44/127), the sentences defining the jointly detected set in Results and Methods, and the sentence counting "other" as correct; each percentage is checked against its count. 3 results.
- **Methods sentences** (post hoc 98% threshold in both sets, Clopper-Pearson intervals, post-unblinding development of four classifiers, 10-fold cross-validation) are asserted on the text with line breaks collapsed.
