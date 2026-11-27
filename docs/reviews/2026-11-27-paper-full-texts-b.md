# Paper full texts for five more papers, 2026-11-27

Prepared by Claude agents. No human review is claimed.

## What changed

10 source records are added, two per paper: the PDF as saved, and its text layer. No model record is changed. The records are not yet on any model's `source_ids`; a page revision adds them when it is applied.

## Why

Five papers were still missing after `docs/reviews/2026-11-27-paper-full-texts.md`: four bioRxiv preprints refused by the rate limit and one Science paper behind a paywall. The owner downloaded them in a browser on 2026-11-27. Each record says so in its description.

## How the files were checked

- Text layers were made with `pdftotext -layout -enc UTF-8` reading the PDF from stdin, the arguments of `scripts/omics/extract/pdf.ts`, with poppler pdftotext 26.08.0. They are unedited.
- No PDF prints a downloader's IP address, name or institution, or a "Downloaded from ... by" line. The text layers, the raw text and the XMP metadata were searched. The first and last pages of the Science PDF were also checked by eye for a margin stamp. The bioRxiv PDFs carry a download time in their XMP ModifyDate, which is why a bioRxiv PDF's hash identifies one download only (`hash_scope`).
- Licences are as the papers state them. The RNA-km PDF has no bioRxiv banner and states no licence. Its licence is the one the bioRxiv details API gives (`cc_by_nd`), and the record says so. The Science paper is under publisher copyright with AAAS as exclusive licensee. That decides what may be published, not what is stored.

## Where the files are

Nothing is committed beyond the records. The archive objects are staged, gzipped under the sha256 of their bytes, for upload to the private archive bucket.

## Per paper

| Paper | Model records | Text layer record | PDF record | Licence |
| --- | --- | --- | --- | --- |
| bioRxiv 10.1101/2024.10.10.617568 v1 | DeCodon, EnCodon | `paper-full-texts-20261127b-source-cdsfm-paper-text` | `paper-full-texts-20261127b-source-cdsfm-paper` | CC-BY-NC-ND-4.0 |
| bioRxiv 10.1101/2024.01.27.577533 v1 | RNA-km | `paper-full-texts-20261127b-source-rna-km-paper-text` | `paper-full-texts-20261127b-source-rna-km-paper` | CC-BY-ND-4.0 (bioRxiv API) |
| bioRxiv 10.1101/2025.04.15.649055 v2 | ProGen3 | `paper-full-texts-20261127b-source-progen3-paper-text` | `paper-full-texts-20261127b-source-progen3-paper` | CC-BY-NC-ND-4.0 |
| bioRxiv 10.1101/2025.11.12.688125 v1 | E1 | `paper-full-texts-20261127b-source-e1-paper-text` | `paper-full-texts-20261127b-source-e1-paper` | CC-BY-NC-ND-4.0 |
| Science 10.1126/science.ads7373, First Release 29 May 2025 | PromoterAI | `paper-full-texts-20261127b-source-promoterai-paper-text` | `paper-full-texts-20261127b-source-promoterai-paper` | Science reuse terms, not open |
