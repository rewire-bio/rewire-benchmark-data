# Retrieval log

Extraction pass for the `hit-discovery-virtual-screening` use case (rewire-benchmark-data #177),
2026-10-22, by a Claude extraction agent. No human review claimed.

Every step below was run from the command line and is reproduced by
`extract/build_batch.py`, which re-downloads each artifact and asserts its SHA-256 before parsing.

## 1. Primary articles, Europe PMC full-text XML

```
curl -sS -o PMC12704515.xml https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12704515/fullTextXML
curl -sS -o PMC13657626.xml https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13657626/fullTextXML
curl -sS -o PMC12892310.xml https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12892310/fullTextXML
```

All three returned complete JATS XML at 2026-10-22T11:52:32Z. Hashes in `sources.md`.

- **Shen et al. (PMC12704515)** carries Tables 1 to 6 as `table-wrap` elements with their captions
  and footnotes. Tables 1 to 5 were parsed; Table 6 is pose analysis and is outside the endpoint.
- **Kim, Correy, Hall et al. (PMC13657626)** carries **no** `table-wrap` elements at all. The AUC
  values for the three docking hit lists are printed in the body text of the Results section, not in
  a table. They were taken from that text and the extractor asserts that each printed string
  (`AUC = 78.8`, `AUC = 56.1`, `AUC = 83.8`, `AUC ~ 71`, `AUC = 46.4`, `AUC = 76.5`, `AUC = 68.1`,
  `AUC = 60.5`) is present in the pinned body text before writing a record. No figure was read.
- **Herasymenko et al. (PMC12892310)** carries only Tables 1 and 2. Table 1 is a structure gallery of
  the ten best-scoring compounds with no extractable numeric grid; Table 2 is a count of successful
  strategies across CACHE #1 to #3 and is not a ranking result. The per-workflow numbers are in the
  Supporting Information workbook.

## 2. CACHE #3 Supporting Information

The publisher's direct supplement URL was tried first and refused:

```
curl -sS -L -o acs_si_002.xlsx https://pubs.acs.org/doi/suppl/10.1021/acs.jcim.5c02441/suppl_file/ci5c02441_si_002.xlsx
# HTTP 403, 5614 bytes of Cloudflare interstitial
```

The Europe PMC supplementary archive worked:

```
curl -sS -o cache3-supp.zip https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12892310/supplementaryFiles
unzip -l cache3-supp.zip     # 25 members, 17 MB
unzip cache3-supp.zip ci5c02441_si_002.xlsx ci5c02441_si_003.xlsx ci5c02441_si_001.pdf
```

Three members were kept:

| Member | SHA-256 | Used |
| --- | --- | --- |
| `ci5c02441_si_002.xlsx` | `5e655da5728da46c6a57882c5fef0643c057536d7897d16b9c98f6d55c12f5fe` | Yes, sheet `S8` only |
| `ci5c02441_si_003.xlsx` | `09ac4876e44e7a5fee60aae5d1cee10325a6c99c7be6c7a6c2ca5ac01f56554b` | No: crystallography and ligand modelling |
| `ci5c02441_si_001.pdf` | `f9457b0e14204cba21f57ba6a2ecabb882c4366f74dd4781384e4b70a38ca701` | No: chemical series figures |

`openpyxl` is not installed in this environment, so the workbook is read by unzipping it and parsing
`xl/worksheets/*.xml` and `xl/sharedStrings.xml` directly (`xlsx_sheet` in the extractor). Sheet `S8`
has a header row and 23 workflow rows in columns A to T. The extractor asserts every column header
in B to S by name and asserts that column T has no printed header, then refuses to run if any of
them differs.

The workbook stores its numbers as doubles, so a cell holding 19.4 appears in the XML as
`19.399999999999999`. For each cell `printed_value` is the shortest decimal that round-trips to the
stored double, which is what a spreadsheet displays, and `raw_xml_value` keeps the stored string.
The cell number formats were not read; every result says so in `workbook_number_format`.

Sheet `S7`, the per-compound scoring matrix, was opened and not extracted: it is a wide grid of two
judges' scores per topic per compound and needs a pass of its own.

## 3. LIT-PCBA leakage audit

```
curl -sS -L -o arxiv-2507.21404v2.html https://arxiv.org/abs/2507.21404v2
```

`https://export.arxiv.org/api/query?id_list=2507.21404v2` and the plain-HTTP form both timed out
after 25 seconds, the same failure the search pass recorded, so the abstract page was used. The
abstract gives the headline figures (323 active training-validation analogue pairs at ECFP4 Tanimoto
at or above 0.6 in ALDH1; 2,491 2D-identical inactives shared between training and validation across
targets; a parameter-free memorisation baseline matching or exceeding the state of the art). The
preprint's own tables were **not** retrieved, so no per-target value from the audit is recorded.

The repository `sievestack/LIT-PCBA-audit` at commit `de227b81e5bfd096935fba57c7e33f12bdfa35ea` was
confirmed reachable through the GitHub API (HTTP 200) but its contents were not retrieved and no
record is sourced to it.

## 4. Benchmark primaries

```
curl -sS -L -o litpcba-page.html https://drugdesign.unistra.fr/LIT-PCBA/
curl -sS -o PMC3405771.xml  https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3405771/fullTextXML
curl -sS -o PMC10170507.xml https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10170507/fullTextXML
curl -sS -o PMC6701836.xml  https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6701836/fullTextXML
```

The LIT-PCBA page's data-content table gives per-target actives and inactives for all 15 target sets.
Five of them (ESR_ago 13/4378, ESR_antago 88/3820, PPARG 24/4071, TP53 64/3345, MAPK1 308/61567) are
the targets Shen et al. screened and are recorded as `dataset_subset` records. The page's totals
(7,761 actives, 382,674 unique inactives) disagree with Shen et al.'s (10,030 actives, 2,798,737
inactives); the difference is recorded as an `evidence_concerns` entry on the page's source record
rather than resolved.

DUD-E, MF-PCBA and Chen et al. 2019 were read for their abstracts only and are registered as
`discovered` benchmarks or descriptive claims with no results.

## 5. Build

```
python3 extract/build_batch.py <cache_dir>
```

Writes `batch.jsonl` (1,366 records), `claims.csv` (1,091 rows, one per result) and `coverage.json`.
The script refuses to run on an artifact whose hash does not match, on a table whose row labels or
column headers differ from the ones asserted, on a row with the wrong number of cells, and on a
duplicate record ID.

Independently of the extractor, a separate checker was run over `batch.jsonl` to confirm that every
attribute key is declared for its kind in `shared/omics/attribute-registry.ts`, every concept key
exists in its `data/vocab/*.ttl` scheme, every link relation exists in `shared/omics/relations.ts`
and resolves to a record of an allowed kind in this batch or the store, every evaluation has exactly
one `system`, `assessment` and `data` link, every result has exactly one `evaluation` link and a
non-empty `printed_value`, no attribute is null except `numeric_value`, no field carries both a
value and a missing reason, and no description of a model, method, pipeline, service or configuration
trips the placeholder or provenance rules in `shared/omics/descriptions.ts`. It reported no
problems. That checker is not a review: it checks shape, not whether a value matches its source.
