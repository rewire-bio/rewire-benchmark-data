# Model pages, batch 10, 2026-11-27

Prepared by Claude agents. No human review is claimed. One research agent fetched sources and wrote the content, one agent verified it, one applied the verifier's findings, and a separate session checked and applied the result.

## What changed

18 Tier 1 model records gain a `profile` and a `run_guide`, from ten researched pages. The new source records in `model-pages-20261127-batch10/batch.jsonl` pin the files the content was written from. No result, evaluation or claim was added or changed, and no existing attribute was edited.

## One page on two records

Eight of these models have two records each, entered from two different benchmarks: AIDO.RNA, BiRNA-BERT, DNABERT, DNABERT-S, MP-RNA, Omni-DNA, RiNALMo and SpliceBERT. The batch tool leaves out a name that sits on two records, which is why these Tier 1 models had no page.

The records are not merged here. A record's ID is a public address and each record carries its own benchmark's results. Each model was researched once, the page was written about the model and not from one benchmark's point of view (the verifier checked this), and the same `profile` and `run_guide` are placed on both records. The second set is `model-pages-20261127-batch10-twins`: it adds no source records, because the tool reuses a source that is already pinned at the same address and hash. A later correction to one of these pages must be made on both records.

GENERator and MirrorDNA have one record each.

## How statements were checked

Every copied passage was confirmed present in its saved file by `scripts/enrich/check_spec.py`. A verifier agent that had not written the content judged 409 statements and raised 23 findings (5.6%): 2 contradicted by a source, 16 that went partly beyond it and 5 with no support. All were applied (22 corrected, 1 removed). The verifier was asked to look in both directions, and the two contradictions were both understatements: a page said inference hardware was not stated when the paper's appendix gives it, and a gap said a file had not been read that the page quotes.

No page in this batch was read in full by the applying session before merge.

## Things a reader of these records should know

- AIDO.RNA: the Hugging Face repositories read are named GB.RNA, the developers call the code repository deprecated, and the model cards use a backbone name the pinned code does not accept. Code and weights are under a non-commercial licence.
- Omni-DNA: several checkpoints have fewer parameters than their names say. The checkpoint named 20M has 10,490,112.
- RiNALMo: the paper, the README and the Zenodo record give different parameter counts for the two smaller sizes.
- BiRNA-BERT: the README's example loads a different model, and no licence is stated for code or weights.
- DNABERT: no source read gives a parameter count; the paper gives two different minimum sequence lengths for training.
- GENERator: the paper gives two figures for the 1B model's pretraining compute. The record's ID says v2 and the page covers all six checkpoints.
- Three pages have no full text of a paper among their sources because the only open copy is on bioRxiv, which was rate limiting: AIDO.RNA, GENERator's v2 report and MirrorDNA.

## Sources

Every fetched file was kept, whatever its licence, and uploaded to the private archive bucket under the sha256 its source record pins.

## Structured facts

The content files in `specs/` carry a `structured` list: 40 entries, one per released checkpoint. They are not written to the records in this change.

## Run guides

All have status `source_reviewed_not_executed`. None was run.

## Per model

| Record | Second record with the same page | Sources | Run guide | Notes for a later reader |
| --- | --- | --- | --- | --- |
| `lit-microbial-20261011-virobench-model-aido-rna` | `lit-rna-20261011-rnalm-zeroshot-model-aido-rna` | 20 (11 stored in the repository) | yes | This page is meant for both AIDO.RNA records (lit-microbial-20261011-virobench-model-aido-rna and lit-rna-20261011-rnalm-zeroshot-model-aido-rna). The saved API response artifacts/hf-api-aido-1.6b.json gives the GB.RNA-1.6B identifier; no saved file says when or why the name changed, so the page states both names without explaining it. The paper is on bioRxiv: https://www.biorxiv.org/content/10.1101/2024.11.28.625345v1.full.pdf (not fetched, per run rules). OpenReview (NeurIPS 2024 workshop) returned a challenge page and was not used. The 1.6B parameter count is the card's rounded figure; the API response gives no safetensors count for it. The 25M-MARS parameter field is null because its card says 300 million. The repository LICENSE and the cards are under the GenBio AI Community License, so store_bytes is false for them. The released field is null: the API createdAt values are repository creation dates and were not used. |
| `lit-microbial-20261011-virobench-model-birna-bert` | `lit-rna-20261011-rnalm-zeroshot-model-birna-bert` | 9 (6 stored in the repository) | yes | This page is meant for both BiRNA-BERT records (lit-microbial-20261011-virobench-model-birna-bert and lit-rna-20261011-rnalm-zeroshot-model-birna-bert). The paper was read in full from PMC (PMC12635123, CC BY 4.0). The record's existing bioRxiv citation is the preprint of the same paper. The README example loads Lancelot53/birnabert-2ep; its Hugging Face API response was saved as artifacts/hf-api-lancelot.json but nothing else about it was read. |
| `gfm2-20261011-you2026-model-dnabert` | `lit-genomics-20261011-gfmbench-model-dnabert` | 8 (7 stored in the repository) | yes | This page is meant for both DNABERT records (gfm2-20261011-you2026-model-dnabert and lit-genomics-20261011-gfmbench-model-dnabert). The PMC E-utilities XML (artifacts/paper-pmc.xml) holds only the abstract because the article is not in the open-access subset, so the full text was read from the PMC article page (artifacts/paper-pmc.html), which is all rights reserved: store_bytes is false. The DNA_bert_6 model card (artifacts/hf-card-6.md) holds only tags and was not cited. |
| `gfm2-20261011-buzkova2026-model-dnabert-s` | `lit-genomics-20261011-geneb-model-dnabert-s` | 9 (7 stored in the repository) | yes | This page is meant for both DNABERT-S records (gfm2-20261011-buzkova2026-model-dnabert-s and lit-genomics-20261011-geneb-model-dnabert-s). The README section 2.1 gives a gdown command for the model that unzips dnabert-s_train.zip, the same archive name as the training data, so it looks like a copy error; the Hugging Face checkpoint is used instead. The arXiv HTML full text was fetched without a version suffix; the abstract page lists three versions. |
| `lit-microbial-20261011-virobench-model-mp-rna` | `lit-rna-20261011-rnalm-zeroshot-model-mp-rna` | 8 (8 stored in the repository) | yes | This page is meant for both MP-RNA records (lit-microbial-20261011-virobench-model-mp-rna and lit-rna-20261011-rnalm-zeroshot-model-mp-rna). The paper source is the pdftotext text layer of the ACL Anthology PDF (CC BY 4.0); the PDF itself is kept as artifacts/paper.pdf. The README examples use yangheng/OmniGenome-186M; no saved source links OmniGenome models to MP-RNA, so they are not treated as MP-RNA checkpoints. The saved GitHub API response artifacts/gh-repo-omnigenomebench.json gives yangheng95/OmniGenBench; no saved file shows how it relates to the OmniGenomeBench address the paper gives. That repository is treated as the code source. The cited paper file is the pdftotext text layer, so its sha256 is not the PDF's. |
| `gfm2-20261011-datta2026-model-omni-dna` | `lit-genomics-20261011-geneb-model-omni-dna` | 16 (16 stored in the repository) | yes | This page is meant for both Omni-DNA records (gfm2-20261011-datta2026-model-omni-dna and lit-genomics-20261011-geneb-model-omni-dna). The README news line dates the Hugging Face release as 2024.02.10 while the arXiv preprint is v1 of 05 Feb 2025; the release date is left null. artifacts/sft_multitask.py is a two-line wrapper that calls inference_sft.py; it was saved but not cited. |
| `lit-microbial-20261011-virobench-model-rinalmo` | `lit-rna-20261011-rnalm-zeroshot-model-rinalmo` | 7 (6 stored in the repository) | yes | This page is meant for both RiNALMo records (lit-microbial-20261011-virobench-model-rinalmo and lit-rna-20261011-rnalm-zeroshot-model-rinalmo). The paper text from PMC is CC BY-NC-ND 4.0, so store_bytes is false for it. Structured parameter counts use the paper's figures. config.py also defines a nano configuration (6 blocks, 320 dimensions) with no published weights; it is not mentioned on the page. No Hugging Face repository from the authors was found or used. |
| `gfm2-20261011-you2026-model-splicebert` | `lit-genomics-20261011-geneb-model-splicebert` | 6 (6 stored in the repository) | yes | This page is meant for both SpliceBERT records (gfm2-20261011-you2026-model-splicebert and lit-genomics-20261011-geneb-model-splicebert). The README and Zenodo record point to github.com/biomed-AI/SpliceBERT, while the files read here come from chenkenbio/SpliceBERT, whose saved GitHub API response (artifacts/gh-repo.json) gives full_name chenkenbio/SpliceBERT and fork false; no saved file shows how the two addresses are related. The chenkenbio repository is cited. The structured released date is the Zenodo record's publication date. The paper gives about 19.4 million parameters for SpliceBERT without naming a checkpoint folder, so the structured parameter fields are null. |
| `gfm2-20261011-datta2026-model-generator-v2` | none | 20 (20 stored in the repository) | yes | The record ID ends in generator-v2 but the record name and description cover the whole GENERator family, so the page describes both generations. The v2 technical report is only on bioRxiv: https://www.biorxiv.org/content/10.64898/2026.01.27.702015v1.full.pdf (not fetched, per run rules). The README news item says the 2026-07-06 update applies to GENERator-prokaryote-1.2b-base and -3b-base but links to the v2 prokaryote repository; the page reports it as an update to the prokaryote weights without resolving the naming. |
| `intake-404-20261126-model-mirrordna` | none | 11 (11 stored in the repository) | yes | No twin record. The paper is a bioRxiv preprint: https://www.biorxiv.org/content/10.64898/2026.11.04.764207v1.full.pdf (not fetched, per run rules). Coverage is marked reviewed because the README and a model card were read, though the paper was not. artifacts/pretrain_info-chunker-rcaug.json was saved but not cited. |
