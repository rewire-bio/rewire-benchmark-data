# Sources

Three primary artifacts. Every hash below was computed on a fresh download made during this pass,
not carried over from the preceding literature search.

| Record | Artifact | Version | Retrieved (UTC) | SHA-256 | Licence |
| --- | --- | --- | --- | --- | --- |
| `uc-leadopt-20261022-source-boltz2-supplement` | `NIHPP2025.06.14.659707v1-supplement-1.pdf`, inside the ZIP served by `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12262699/supplementaryFiles` | bioRxiv v1 posted 2025-06-18, doi 10.1101/2025.06.14.659707 | 2026-10-22T11:52:00Z | `be867a5d92add8b223d47d882a4213ad489741f3e4d5081a0901a54370342569` | CC BY 4.0 (stated on each page of the PDF) |
| `uc-leadopt-20261022-source-ross2023` | `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10576784/fullTextXML` | *Communications Chemistry* 6:222 (2023), doi 10.1038/s42004-023-01019-9 | 2026-10-22T11:58:25Z | `f371d2e373306588d11b695b8de21b253a90293d6a15884f635bcf927bdebb1d` | CC BY 4.0 |
| `uc-leadopt-20261022-source-gilson2025` | `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12750038/fullTextXML` | *Proteins* 94(1), cover date January 2026, doi 10.1002/prot.70061 | 2026-10-22T11:58:25Z | `a1d7fdc52df61c4d75197f04be91b511b7d093d229d96a0815a11f95e350256b` | CC BY 4.0 |

## Derived artifacts used during extraction

| File | SHA-256 | How it was made |
| --- | --- | --- |
| Europe PMC supplementary-files ZIP | `25050dabd9c66fdb955704095023037f1bbabc3a93b7b61f00344c75df8bdb70` | `curl` of the `supplementaryFiles` endpoint on 2026-10-22. The endpoint rebuilds the ZIP per request, so this hash describes one retrieval and is **not** the pinned artifact hash; the PDF inside it is. |
| `supp-layout.txt` | `6e19c85a90c118fd5fd045981a7ebfa5559d9b0a2b4c700b2da0c7393a417c17` | `pdftotext -layout` (poppler 26.08.0) of the pinned supplement PDF. Every Boltz-2 result's locator names a line number in this file. |

## Access notes

- The direct bioRxiv PDF (`https://www.biorxiv.org/content/10.1101/2025.06.14.659707v2.full.pdf`) returns
  HTTP 403, and the Europe PMC `fulltextRepo` download link also returns HTTP 403. The
  `supplementaryFiles` endpoint works and yields the same appendix, so the pinned version is **v1** as
  deposited in PMC, not v2.
- No source bytes are archived under `artifacts/`. All three are CC BY, so archiving would be allowed;
  it was skipped because all three are reachable from stable Europe PMC endpoints and the supplement PDF
  is 6.5 MB.
- The existing source record `expansion-p3-boltz2` pins the Boltz-2 Europe PMC full-text XML
  (`20b1c6f0b64317b8585834a5513905e133806ccb4f2917595ce4252c8ee37515`). That snapshot holds the main
  text, figure captions and Table 1 only; Tables 11 to 16 are not in it. That is why this batch adds a
  separate source record for the supplement rather than reusing it.
