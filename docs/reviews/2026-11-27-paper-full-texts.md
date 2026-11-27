# Paper full texts for 16 more models, 2026-11-27

Prepared by Claude agents. No human review is claimed.

## What changed

14 source records are added, one per paper, and each is appended to the `source_ids` of the model record or records it introduces (16 model records). No profile, result, evaluation or claim is changed.

## Why

This continues `docs/reviews/2026-11-26-paper-full-texts.md`. That pass left 19 bioRxiv PDFs, covering 22 model records, refused by the server's rate limit. They were requested again one at a time, eight to ten minutes apart, with curl's default identification. 14 have been served so far. Five are still refused: the papers for DeepGene, DeCodon and EnCodon (one preprint), RNA-km, ProGen3 and E1.

## Where the files are

Each file is stored in the private archive bucket under the sha256 its source record pins. None is committed to this repository. A bioRxiv PDF is stamped per download, so its hash identifies this download only; each record says so in `hash_scope`.

## The pages were not rewritten

The model pages still say what they said. A later pass should read each full text and fill what the abstract could not give.

## Per model

| Model record | Source record | Bytes |
| --- | --- | --- |
| `model-execution-20261011-model-deepvariant` | `paper-full-texts-20261127-source-deepvariant-paper` | 872876 |
| `lit-rna-20261011-rnalm-zeroshot-model-uni-rna` | `paper-full-texts-20261127-source-uni-rna-paper` | 3823239 |
| `lit-genomics-20261011-geneb-model-biofm` | `paper-full-texts-20261127-source-biofm-paper` | 1598882 |
| `lit-genomics-20261011-guanine-model-aido-dna` | `paper-full-texts-20261127-source-aido-dna-paper` | 8247089 |
| `traitgym-20261116-model-gpn-promoter` | `paper-full-texts-20261127-source-gpn-promoter-paper` | 1507472 |
| `lit-rna-20261011-rnalm-zeroshot-model-dgrna` | `paper-full-texts-20261127-source-dgrna-paper` | 395527 |
| `ladon-20261115-model-bulkformer` | `paper-full-texts-20261127-source-bulkformer-paper` | 4409669 |
| `lit-rna-20261011-rna3d-model-deepfoldrna` | `paper-full-texts-20261127-source-deepfoldrna-paper` | 1263363 |
| `lit-rna-20261011-rnagym-model-rnagenesis` | `paper-full-texts-20261127-source-rnagenesis-paper` | 10126772 |
| `intake-250-20261119-model-hevo` | `paper-full-texts-20261127-source-hevo-paper` | 1232706 |
| `intake-250-20261119-model-hevo-base-o` | `paper-full-texts-20261127-source-hevo-paper` | 1232706 |
| `intake-250-20261119-model-hevo-large-o` | `paper-full-texts-20261127-source-hevo-paper` | 1232706 |
| `intake-383-20261124-model-lncrfm` | `paper-full-texts-20261127-source-lncrfm-paper` | 3507265 |
| `uc20260930-model-carp` | `paper-full-texts-20261127-source-carp-paper` | 3614470 |
| `uc20260930-model-trancepteve` | `paper-full-texts-20261127-source-trancepteve-paper` | 585923 |
| `uc20260930-model-eve` | `paper-full-texts-20261127-source-eve-paper` | 6629664 |
