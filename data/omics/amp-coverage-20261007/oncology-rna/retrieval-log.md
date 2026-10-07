# Oncology/RNA evidence retrieval ledger

Three bounded primary-source selections support AMP issues #10, #11 and #12. All source bytes were obtained anonymously through Europe PMC fullTextXML. See artifact-manifest.json for actual request-start UTC times, exact URLs, decompressed SHA256, byte length, compressed SHA256 and path. Gzip uses mtime=0. XML and selected-extract JSON preserve author attribution/DOI and CC BY 4.0 licensing. This is automated transcription; independent parent review follows and human scientific review remains unassigned.

## Search

A confirming web search batch began at **2026-10-07 12:26:16 UTC**, as captured immediately before the call with the clock tool. Actual queries:

- `"Genome-wide somatic variant calling using localized colored de Bruijn graphs"` → https://pmc.ncbi.nlm.nih.gov/articles/PMC6123722/ and https://doi.org/gfcfr8
- `"Discovery of clinically relevant fusions in pediatric cancer"` → https://pmc.ncbi.nlm.nih.gov/articles/PMC8642973/ and https://pubmed.ncbi.nlm.nih.gov/34863095/
- `"Detection of aberrant splicing events in RNA-seq data using FRASER" 85% 13` → https://pmc.ncbi.nlm.nih.gov/articles/PMC7822922/ and https://doi.org/10.1038/S41467-020-20573-7

Earlier exploratory queries were run on 2026-10-07; exact search-call timestamps were not captured and remain unknown (source retrieval timestamps were captured):

- `Haas 2019 accuracy fusion transcript detection methods STAR Fusion 101 fusion cancer cell lines sensitivity precision`
- `Mertes 2021 FRASER 48 50 aberrant splicing RNA diagnosis rare disease`
- `Kim 2018 Strelka2 somatic SNV indel benchmark precision recall 30x 50x`
- `"s42003-018-0023-9" PMC`
- `"FRASER" "nine" "13" splicing Kremer`
- `"Comprehensive evaluation" "fusion" "Table 2" Liu 2016`
- `Arriba fusion detection paper sensitivity 2021 0.95 precision benchmark validated fusions PMC`
- `"Genome-wide somatic variant calling" Lancet 1.0 version`
- `"Detection of aberrant splicing" "FRASER" "version" 2021`

Other inspected search discoveries: https://pmc.ncbi.nlm.nih.gov/articles/PMC6802306/ (Haas et al. 2019 CC BY; archived background only); https://pmc.ncbi.nlm.nih.gov/articles/PMC4797269/ (older comparison, CC BY-NC; inspected then removed XML archive after selecting the permissively licensed EnFusion source); https://pmc.ncbi.nlm.nih.gov/articles/PMC7919457/ (Arriba; search-only); https://mediatum.ub.tum.de/doc/1795389/1795389.pdf (FRASER author correction; search-only).

The DOI→PMCID lookup was https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1038/s42003-018-0023-9&format=json, resolving to PMC6123722. Lookup bytes were not archived; primary XML was.

## Access limits

Nature main-page request for https://www.nature.com/articles/s42003-018-0023-9 returned a blocked cookie-authentication redirect in web. PMC direct web opens for PMC7822922 and PMC4797269 returned reCAPTCHA. Anonymous Europe PMC fullTextXML succeeded and full primary table/paragraph bytes were inspected locally.

Supplemental retrieval attempts at the following URLs failed with DNS resolution (`nodename nor servname provided, or not known`); no PDF bytes or supplement scores were invented:

- https://static-content.springer-cdn.com/esm/art%3A10.1038%2Fs42003-018-0023-9/MediaObjects/42003_2018_23_MOESM1_ESM.pdf
- https://static-content.springer-cdn.com/esm/art%3A10.1038%2Fs41467-020-20573-7/MediaObjects/41467_2020_20573_MOESM1_ESM.pdf

Exact failed-attempt timestamps were not captured. Main-text FRASER 85% is a printed numeric endpoint with a precise paragraph locator, even though its cited supplementary panel remains unavailable. Caller versions not specified in the inspected main article are explicitly null.

## Identity and duplicate checks

Scanned data/omics JSONL inputs and the parent's baseline catalogue snapshot at workbench/amp-supervision/baseline-catalogue.json. No matching Lancet, EnFusion, STAR-Fusion, Strelka2 or FRASER model/configuration or these primary source records were identified. baseline-identity-matches.json records the related existing AlphaGenome GTEx FRASER2.0-label entries, which must not be reused for the patient cohort or FRASER 2021 implementation. Existing global records were not edited.
