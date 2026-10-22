# Sources

Nine artifacts, all pinned by SHA-256. Every hash in this table was computed by
`extract/build_batch.py`, which re-downloads each artifact and refuses to run if a hash differs.
Nothing is archived under `artifacts/`: each artifact can be re-fetched from the URL below, and the
Shen et al. article is licensed CC BY-NC, which this repository does not redistribute.

| Source record | URL | Version | Retrieved (UTC) | SHA-256 |
| --- | --- | --- | --- | --- |
| `hitdisc-20261022-source-shen2025` | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12704515/fullTextXML | PMC12704515, Chem Sci, published 2025-12-11, doi 10.1039/d5sc06481c | 2026-10-22T11:52:32Z | `11a4cee97057d9e72f9393024d22fdd169e3134f493367eee2f7869facf9ccf8` |
| `hitdisc-20261022-source-kim2026` | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13657626/fullTextXML | PMC13657626, eLife 2026;15:RP110475, published 2026-10-12, doi 10.7554/eLife.110475 | 2026-10-22T11:52:32Z | `9be510b7b0cc152ff56a03c96877bf06b6a6bdeffdb4baecf8e999a6bf155aa6` |
| `hitdisc-20261022-source-cache3` | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12892310/fullTextXML | PMC12892310, J Chem Inf Model, published 2026-01-21, doi 10.1021/acs.jcim.5c02441 | 2026-10-22T11:52:32Z | `43b920ac9f67fac3560bcf7d24a79f76b9a0d0d962088dfe4081742ec7b9b071` |
| `hitdisc-20261022-source-cache3-si002` | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12892310/supplementaryFiles (member `ci5c02441_si_002.xlsx`) | Supporting Information workbook of the same article | 2026-10-22T11:55:00Z | `5e655da5728da46c6a57882c5fef0643c057536d7897d16b9c98f6d55c12f5fe` |
| `hitdisc-20261022-source-litpcba-audit` | https://arxiv.org/abs/2507.21404v2 | arXiv:2507.21404v2, submitted 2025-07-29, this version 2025-08-07 | 2026-10-22T11:59:20Z | `e766c8aa4f94287672b2b1bacab2480a41ec7c806ecbaf5e2d1bf8773781310f` |
| `hitdisc-20261022-source-litpcba-page` | https://drugdesign.unistra.fr/LIT-PCBA/ | Mutable page, no version printed | 2026-10-22T12:01:54Z | `a2203612b553236d7f01da5573389d439d2f7aa0436080412f27da882e086e5e` |
| `hitdisc-20261022-source-dude2012` | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3405771/fullTextXML | PMC3405771, J Med Chem 2012, doi 10.1021/jm300687e | 2026-10-22T12:01:54Z | `8f20c3adec704671ea668742622567a7c6aec9b38f6d804f977c175209fa500d` |
| `hitdisc-20261022-source-mfpcba2023` | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10170507/fullTextXML | PMC10170507, J Chem Inf Model 2023, doi 10.1021/acs.jcim.2c01569 | 2026-10-22T12:01:54Z | `628c94a973118410ec616f9342237c141a139ca4f56c34c698c6d9dcb6d82241` |
| `hitdisc-20261022-source-chen2019` | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6701836/fullTextXML | PMC6701836, PLoS ONE 2019, doi 10.1371/journal.pone.0220113 | 2026-10-22T12:01:54Z | `b845c78815bb0c4eabb3e05e65212b343269c91292fedf00fae9ac00c7840f09` |

## Licences

- Shen et al. 2025: Creative Commons Attribution-Non Commercial 3.0 Unported.
- Kim, Correy, Hall et al. 2026: Creative Commons Attribution.
- Herasymenko et al. 2026 and its Supporting Information workbook: CC-BY 4.0.
- Huang, Knight and Naprienko 2025 (arXiv abstract page): CC BY 4.0, as stated on the page.
- LIT-PCBA official page: no licence stated.
- Mysinger et al. 2012: ACS AuthorChoice open-access terms.
- Buterez et al. 2023: CC-BY 4.0.
- Chen et al. 2019: Creative Commons Attribution.

## Hash scope notes

- **CACHE #3 workbook.** The Europe PMC `supplementaryFiles` endpoint assembles a zip per request, so
  the archive's own bytes are not stable. The pinned hash is of the member file
  `ci5c02441_si_002.xlsx`, which is stable. The publisher's direct supplement URL
  (`https://pubs.acs.org/doi/suppl/10.1021/acs.jcim.5c02441/suppl_file/ci5c02441_si_002.xlsx`)
  returned HTTP 403 on 2026-10-22, so it is not usable as the retrieval path.
- **arXiv abstract page and the LIT-PCBA project page.** Both are mutable web pages. Their hashes
  describe the single retrieval recorded above; a later edit to either page changes the hash without
  changing the facts extracted from it. Both source records carry a `hash_scope` note saying so.
- **arXiv API.** `export.arxiv.org/api/query` timed out on 2026-10-22, as it did in the search pass,
  so the abstract page was used instead of the API record.

## Sources recorded as gaps, not as records

Closed-access or unretrieved primaries. No record in this batch is sourced to any of them; where the
batch needed their content it is recorded as another source describes it, with a `missing_metadata`
reason saying so.

| Source | DOI | Why |
| --- | --- | --- |
| DEKOIS 2.0, Bauer et al. 2013 | 10.1021/ci400115b | Closed access. The benchmark's composition is recorded as Shen et al. 2025 describe it. |
| DEKOIS 1.0, Vogel et al. 2011 | 10.1021/ci2001549 | Closed access, not retrieved. |
| LIT-PCBA, Tran-Nguyen et al. 2020 | 10.1021/acs.jcim.0c00155 | Closed access. Composition taken from the official project page. |
| TocoDecoy, Zhang et al. 2022 | 10.1021/acs.jmedchem.2c00460 | Closed access. Recorded as Shen et al. 2025 describe it. |
| CACHE #1 results | 10.1021/acs.jcim.4c01267 | Not open access in Europe PMC. |
| CACHE #2 results | 10.1021/acs.jcim.5c00535 | Not open access in Europe PMC. |
| Library size and scale of testing in virtual screening | 10.1038/s41589-024-01797-w | Not open access. This is the paper that would set the relationship between library size, number tested and hit rate. |
| Shen et al. refs 34, 35, 36, 38 and 39 | not resolved | The five papers whose DEKOIS 2.0 values Shen et al. Table 1 quotes. None was resolved to a primary artifact, so eight of that table's 24 arms rest on the compilation alone. |
