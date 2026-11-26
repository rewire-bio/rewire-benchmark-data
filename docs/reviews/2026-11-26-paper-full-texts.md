# Paper full texts for 21 models, 2026-11-26

Prepared by Claude agents. No human review is claimed.

## What changed

19 source records are added, one per paper, and each is appended to the `source_ids` of the model record it introduces (19 model records). Two of the 21 saved files were already pinned by a source record on their model, so nothing is added for them. No profile, result, evaluation or claim is changed.

## Why

A count on 26 November found that 47 of the 110 model pages written that day rested on a paper's abstract or landing page, or on no paper at all, because Europe PMC and bioRxiv refused the full text at the time. One agent then fetched the primary paper for each through open routes only, one request at a time: arXiv, NCBI PMC, open-access publisher pages, conference proceedings and bioRxiv. 21 full texts were saved. 22 more were refused by bioRxiv's rate limit and will be retried. RFamLlama (robot check at OpenReview) and PromoterAI (paywalled) could not be fetched. Mistral-DNA and Carbon-X have no paper.

## Where the files are

Each file is stored in the private archive bucket under the sha256 its source record pins. None is committed to this repository: several are not openly licensed (author manuscripts with a text-mining-only licence, preprints with no reuse licence), and the rest are large PDFs. The archive workflow fetches each address again and records it in the manifest. A bioRxiv PDF is stamped per download, so its hash identifies this download only; the record says so in `hash_scope`.

## The pages were not rewritten

The model pages still say what they said. A later pass should read each full text and fill what the abstract could not give: parameter counts, training data and cutoffs, evaluation settings.

## Per model

| Model record | Source record | Format | Bytes | Licence as stated in the file |
| --- | --- | --- | --- | --- |
| `lit-genomics-20261011-geneb-model-lucaone` | `paper-full-texts-20261126-source-lucaone-paper` | application/pdf | 14881482 | CC-BY-4.0 |
| `lit-genomics-20261011-geneb-model-grover` | `paper-full-texts-20261126-source-grover-paper` | application/pdf | 3484612 | CC-BY-4.0 |
| `gfm2-20261011-you2026-model-rnaernie` | `paper-full-texts-20261126-source-rnaernie-paper` | application/pdf | 1749406 | CC-BY-4.0 |
| `gfm2-20261011-you2026-model-utr-lm` | `paper-full-texts-20261126-source-utr-lm-paper` | text/xml | 110525 | Not an open licence: 'This file is available for text mining |
| `lit-genomics-20261011-guanine-model-phylogpn` | `paper-full-texts-20261126-source-phylogpn-paper` | application/pdf | 1573791 | CC-BY-NC-ND-4.0 (from the arXiv abstract page; the PDF itsel |
| `model-execution-20261011-model-moderngena` | `paper-full-texts-20261126-source-moderngena-paper` | application/pdf | 1293252 | (which was not certified by peer review) is the author/funde |
| `lit-genomics-20261011-geneb-model-genomics-fm` | `paper-full-texts-20261126-source-genomics-fm-paper` | application/pdf | 8259576 | was not certified by peer review) is the author/funder, who  |
| `ladon-20261115-model-ladon` | `ladon-20261115-source-zenodo-pdf` | application/pdf | 5807005 | not stated |
| `lit-rna-20261011-rnalm-zeroshot-model-protrna` | `paper-full-texts-20261126-source-protrna-paper` | application/pdf | 1926946 | was not certified by peer review) is the author/funder, who  |
| `rna-splicing-20261013-spliceai2-model-spliceai2` | `paper-full-texts-20261126-source-spliceai2-paper` | application/pdf | 2679664 | (which was not certified by peer review) is the author/funde |
| `bacformer-20261115-model-glm2` | `paper-full-texts-20261126-source-glm2-paper` | application/pdf | 39184027 | (which was not certified by peer review) is the author/funde |
| `lit-genomics-20261011-dnalongbench-model-akita` | `paper-full-texts-20261126-source-akita-paper` | text/xml | 132576 | Nature author manuscript terms (view, print, copy, download  |
| `ladon-20261115-model-bulkrnabert` | `paper-full-texts-20261126-source-bulkrnabert-paper` | application/pdf | 3921366 | not stated (page 1 says only: (c) 2024 M. Gelard, G. Richard |
| `lit-genomics-20261011-dnalongbench-model-puffin-d` | `paper-full-texts-20261126-source-puffin-d-paper` | text/xml | 197848 | Not an open licence: 'This file is available for text mining |
| `lit-rna-20261011-rnagym-model-orthrus` | `paper-full-texts-20261126-source-orthrus-paper` | application/pdf | 9673091 | (which was not certified by peer review) is the author/funde |
| `lit-genomics-20261011-genbench-model-deepstarr` | `paper-full-texts-20261126-source-deepstarr-paper` | application/pdf | 18378943 | (which was not certified by peer review) is the author/funde |
| `vep-uc-20261014-model-lol-eve` | `paper-full-texts-20261126-source-lol-eve-paper` | application/pdf | 3063694 | (which was not certified by peer review) is the author/funde |
| `uc20260930-model-tranception` | `paper-full-texts-20261126-source-tranception-paper` | application/pdf | 1191703 | CC-BY-4.0 (from the arXiv abstract page; the PDF itself does |
| `uc20260930-model-prosst` | `paper-full-texts-20261126-source-prosst-paper` | application/pdf | 9898475 | not stated in the PDF |
| `hyinv-20261106-model-hyinv` | `hyinv-20261106-source-report` | application/pdf | 2980024 | not stated |
| `lit-protein-20261011-deepprotein-model-protbert` | `paper-full-texts-20261126-source-protbert-paper` | application/pdf | 12922025 | arXiv non-exclusive distribution licence 1.0 (from the arXiv |
