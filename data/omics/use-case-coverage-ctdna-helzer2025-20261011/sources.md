# Sources: Helzer et al. 2025 (Nature Communications) panel fragmentomics metrics, 2026-10-11

The hash is SHA-256 of the exact bytes read; times are UTC.

| Source ID | What | Version | Retrieved | Artifact URL | Licence | SHA-256 |
| --- | --- | --- | --- | --- | --- | --- |
| `ctdnalit-20261011-helzer2025-source-article` | Analysis of cfDNA fragmentomics metrics and commercial targeted sequencing panels | Nature Communications 16, published online 2025-10-14; Europe PMC full-text JATS XML of PMC12521513 | 21:40:59 | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12521513/fullTextXML | CC-BY-4.0 | `48e63b9225dd6b4b8f67e25c58a026e9a7183eb790c5900e752a6d2f70ead835` |
| `ctdnalit-20261011-helzer2025-source-supplementary-information` | Helzer et al. 2025, Supplementary Information (Figures S1-S7, Tables S1-S2) | 41467_2025_64153_MOESM1_ESM.pdf, publisher supplementary file | 21:41:25 | https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-025-64153-z/MediaObjects/41467_2025_64153_MOESM1_ESM.pdf | CC-BY-4.0 | `3fe7690ed5d7227d4b0c51c5d70d69ca947a26da7d51928c45a209b88fe79b6e` |

The article XML is archived as `artifacts/helzer2025-article.xml.gz` (gzip -n -9, CC BY 4.0). The 4.5 MB supplementary PDF is not archived; the Springer copy and the Europe PMC bundle copy have the same bytes.

No evidence concern. The article text calls the UW table S1 and the GRAIL table S2, while the PDF captions say the reverse. Values quoted in the text match the tables as captioned in the PDF, so this is a labelling slip; it is recorded in the protocol limitations.

Origin: `author_reported` for first-exon and all-exon fragment-size entropy and the combined model (the authors' 2023 panel metric and its extensions); `independent_paper` for depth, motif diversity, small fragments, fragment bins, TFBS entropy, ATAC entropy and Griffin, which the authors re-implemented from other groups' publications. A reviewer should confirm this split.
