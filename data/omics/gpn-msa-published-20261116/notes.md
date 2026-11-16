# GPN-MSA, published version: extraction notes

Batch `data/omics/gpn-msa-published-20261116`, lane genomics, search cutoff 2026-11-16, for the
second item of rewire-bio/rewire-benchmark-data issue #226: the peer-reviewed version of the
GPN-MSA paper, and whether its numbers differ from the bioRxiv v2 values already stored.

Extraction by a Claude (Opus 5) agent. Not reviewed; no human review claimed.

Frozen extraction hash: SHA-256 of `batch.jsonl` is `d00df69afbdb0e148e158a51f8f9cb6dfe8903b590baf68a8d10bf6dc5ea5e5d`.

## What the published version is

Benegas, Albors, Aw, Ye and Song, "A DNA language model based on multispecies alignment predicts
the effects of genome-wide variants", Nature Biotechnology 43, 1960-1965 (2025),
doi:10.1038/s41587-024-02511-w, published online 2 January 2025. It is a Brief Communication, and
it is retitled: the preprint is "GPN-MSA: an alignment-based DNA language model for genome-wide
variant effect prediction".

## Retrieval: what was and was not obtained

The article is not open access and the Results and Methods body could not be retrieved. Every
route was tried:

| Route | Outcome |
| --- | --- |
| Europe PMC REST | One hit, PMID 39747647. `isOpenAccess` N, `inPMC` N, `hasPDF` N; the only full-text link is the paywalled DOI |
| PMC ID converter, PubMed eLink | Not in PMC; no author manuscript deposit |
| Unpaywall | `is_oa` true, but every open location is the bioRxiv submitted version |
| OpenAlex | Same: bioRxiv, and PMC10592768, which is the NIH preprint pilot copy of bioRxiv v2 |
| bioRxiv API | Only v1 and v2; no accepted-version v3 |
| eScholarship | HTTP 403 to curl; not pursued, since the OA indexes list no repository copy |
| nature.com article page | HTTP 200, but Results and Methods are behind "Access through your institution" |

What the publisher does serve openly, and what this batch pins:

| Artifact | Source record | SHA-256 |
| --- | --- | --- |
| Article page (abstract, Extended Data captions, Data and Code availability, supplementary listing, citation) | `gpn-msa-published-20261116-source-nbt-2025` | `accc02ff43f84cf716d56a92b09664cb36506984162d0f5d45773db1c41c2d3f` |
| Extended Data Table 1 page (caption) | `gpn-msa-published-20261116-source-extended-data-table-1-page` | `abe7bcaf55b0354a7f50f8d2cd91b47c16bc189cfa45b8f2ac0c1fb99dd6491f` |
| Extended Data Table 1 image (the ablation values) | `gpn-msa-published-20261116-source-extended-data-table-1-image` | `b2673b8e14f8d0c4e12892600620ccd93c6de6f36a112473816057c9d7423387` |
| Figure 2 page (full caption, panels a to h, with sample sizes) | `gpn-msa-published-20261116-source-figure-2-page` | `d031178b99df61866b0a302fdfe35f37a18c4f3c3bdb31c5b232514dd7cbd5d6` |
| Supplementary Information PDF, 12 pages (Supplementary Tables 1 to 6, Figures 1 to 8) | `gpn-msa-published-20261116-source-supplementary-information` | `75874bda760405cb98d3712e9319a94fb73838b4a412fd3ba340ddf3b7d6fcb4` |

So this is a partial retrieval of the published version, not retrieval of its full text. Nothing
in this batch is taken from the preprint and labelled published, and nothing is taken from the
abstract.

Hash stability was tested by downloading each artifact twice. The Extended Data Table 1 image, the
Figure 2 page, the Extended Data Table 1 page and the Supplementary Information PDF give identical
bytes. The main article page does not: nature.com varies its advertising and session markup, so
that source record carries a `hash_scope` saying the hash describes one retrieval, and
`extract/build_gpn_msa_published.py` asserts the passages used verbatim instead of the hash.

Springer Nature holds exclusive rights to all five artifacts, so no copy is archived in the
repository. A reviewer re-downloads them; the four stable hashes will match.

## Check for a stale preview-PDF pin (GPN-Star pattern)

The GPN-Star extractor found that `vep-uc-20261014-source-gpn-star`, from the same 2026-10-14
collection pass, pins the right DOI but hashes the publisher's accelerated article preview PDF,
which the live URL no longer serves. That pattern does not occur here, and the checks that rule it
out are below. None of them relies on the bioRxiv API's `published` field.

**There is no stored publisher artifact for GPN-MSA to be stale.** Grepping the whole store for
both DOIs, `10.1038/s41587-024-02511-w` and `10.1101/2023.10.10.561776`, returns exactly one source
record, `gfm-guides-20261014-gpnmsa-source-biorxiv-v2`, plus the 138 results that cite it. The
published DOI appears only inside that record's `limitations` prose. Grepping for both titles finds
no other source. So the store holds a bioRxiv PDF and two GitHub files, and nothing from Springer.
The five Springer artifacts this batch pins are new.

**The published side is the version of record, not a preview.** The article page prints "Received:
31 October 2023, Accepted: 20 November 2024, Published: 02 January 2025, Version of record: 02
January 2025, Issue date: December 2025", volume 43, pages 1960-1965. Version of record and first
online publication are the same day, so this paper had no accelerated preview stage, and nothing on
either side of the comparison is a preview. Every row of the comparison table is therefore
preprint versus version of record. No row is a preview-to-final change, and no row is called a
correction, because none differs.

**The stored preprint hash does not reproduce, and that is expected and already documented.** The
record's own `hash_scope` says bioRxiv rewrites the XMP dates, document IDs, Info ModDate and
trailer `/ID` on every download, so the pinned SHA-256 cannot be reproduced by anyone. Three
downloads of the same URL now have distinct hashes at the identical length of 2,247,726 bytes:

| Download | SHA-256 | Length |
| --- | --- | --- |
| Pinned, 2026-10-14T12:02:16Z | `10411077df1ae59614f9a9a9f85384103d54127ba67a9b3c469a4a2d6c33cee4` | 2,247,726 |
| Re-download by the 2026-10-14 reviewer | `c066dab122b359b90059a81f325fa2cd83122df14a700eae8d35021471c10978` | 2,247,726 |
| Re-download for this batch, 2026-11-16T00:28Z | `9cd3c86d3945474e351e9592df11cbc0185d660fe23576e6aa0e2abcbc43df36` | 2,247,726 |

The content is stable even though the bytes are not. Supplementary Table 4 was re-parsed from the
2026-11-16 copy's `pdftotext -layout` text layer with its 17 row labels asserted: all 136 cells
reproduce the stored `printed_value` exactly, 0 mismatches. That is the same check the comparison
with Extended Data Table 1 rests on, run against a copy downloaded 13 months after the batch was
made.

A second same-session download to show the differing bytes directly was refused by Cloudflare
(error 1015, rate limit). The 51-byte figure in the record's review note is the earlier reviewer's
measurement, not re-measured here.

**Recommendation for the reviewer.** No record was edited and no hash changed. The stored hash is
not stale in the GPN-Star sense: it names the right artifact at the right version, and the
mismatch is bioRxiv's per-download stamping, which the record already declares. What a reviewer
should not do is treat a fresh-download mismatch on this source as evidence of a problem, or
"repair" it by repinning to a new hash, since the next download would not match that one either.
The reproducible check on this source is the text layer, and it passes. If the store wants a
reproducible byte check, the fix is to archive the pinned bytes under the batch folder, which the
CC BY-NC-ND licence permits for the preprint, unlike the Springer artifacts in this batch.

## How the published ablation values were read

The ablation study is published only as a raster image, `41587_2024_2511_Tab1_ESM.jpg`, 1594 by
949 pixels. It has no text layer, so `npm run batch -- check-values` cannot read it and no
deterministic parse is possible. Its 136 values were read by eye and written into
`extract/build_gpn_msa_published.py` as the literal `TAB1`; the script then compares them with the
stored values and writes `extract/comparison.tsv`.

Every row was then read a second time from the image resampled to twice its size and cropped into
three overlapping bands, which covers all 17 rows. The second reading agreed with `TAB1` in every
cell.

**The transcription is not independent of the stored values.** The image was viewed before the
stored grid was loaded, but the reading was written out into digits afterwards, with the stored
values in view. The agreement between the two is therefore evidence, not verification. No OCR tool
was available in this environment (`tesseract` is not installed), so there is no machine reading
either. **A reviewer must re-read the image without the stored values to hand.** That is the one
check this batch cannot make for itself, and it is recorded as such on the image source record and
on the comparison claim, as `rendered-source-visual-check` plus `transcription` and never as a
parse.

## The central question: does any published value differ?

No. All 136 cells of Extended Data Table 1 carry exactly the value, and the same number of decimal
places, as the corresponding stored result from bioRxiv v2 Supplementary Table 4. The two
remaining stored preprint results, the DMS TADBP AUROCs quoted in the Results text, sit in the
paywalled body and could not be compared.

- 138 stored results cite `gfm-guides-20261014-gpnmsa-source-biorxiv-v2`
- 136 compared, 0 differ
- 2 not compared (published Results text not retrieved)

No correction claim was written, because there is nothing to correct.

### Protocol sameness

The protocols are the same in both versions. Extended Data Table 1 and preprint Supplementary
Table 4 carry the same caption word for word apart from which Figure 2 panels they cite, and the
Figure 2 panel captions describe the same four comparisons. The caption change is a renumbering,
not a change of method:

| Comparison | Preprint Fig. 2 panel | Published Fig. 2 panel | Cited by the preprint caption | Cited by the published caption |
| --- | --- | --- | --- | --- |
| ClinVar pathogenic vs gnomAD common missense, AUROC | c | c | 2a | 2c |
| COSMIC frequent vs gnomAD common missense, AUPRC | d | e | 2b | 2e |
| OMIM pathogenic vs gnomAD common regulatory, AUPRC | e | f | 2c | 2f |
| gnomAD rare vs common enrichment, odds ratio | f | g | 2d | 2g |

Published Figure 2 has eight panels against the preprint's seven: a new panel d, ClinVar
pathogenic versus ClinVar benign missense variants, is inserted, which shifts COSMIC, OMIM, gnomAD
and DepMap down one letter. The preprint caption's pointers (2a, 2b, 2c, 2d) were wrong in that
version; the published ones are right. This settles the question the earlier batch
(`data/omics/gfm-guides-20261014-gpnmsa`) left for its reviewer, and the finding is claim
`gpn-msa-published-20261116-claim-figure-2-panels`.

### Cell by cell

`extract/comparison.tsv` holds the same table in machine-readable form.

| Stored result ID | Row | Column | Seeds | Stored (bioRxiv v2) | Published (Ext. Data Table 1) | Same protocol | Differs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `gfm-guides-20261014-gpnmsa-result-ablation-default-clinvar-mean` | Default | ClinVar | mean | 0.969 | 0.969 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-default-clinvar-max` | Default | ClinVar | max | 0.969 | 0.969 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-default-cosmic-mean` | Default | COSMIC | mean | 0.348 | 0.348 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-default-cosmic-max` | Default | COSMIC | max | 0.355 | 0.355 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-default-omim-mean` | Default | OMIM | mean | 0.124 | 0.124 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-default-omim-max` | Default | OMIM | max | 0.133 | 0.133 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-default-gnomad-mean` | Default | gnomAD | mean | 41.377 | 41.377 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-default-gnomad-max` | Default | gnomAD | max | 43.118 | 43.118 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-without-msa-clinvar-mean` | w/o MSA | ClinVar | mean | 0.584 | 0.584 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-without-msa-clinvar-max` | w/o MSA | ClinVar | max | 0.585 | 0.585 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-without-msa-cosmic-mean` | w/o MSA | COSMIC | mean | 0.012 | 0.012 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-without-msa-cosmic-max` | w/o MSA | COSMIC | max | 0.012 | 0.012 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-without-msa-omim-mean` | w/o MSA | OMIM | mean | 0.000 | 0.000 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-without-msa-omim-max` | w/o MSA | OMIM | max | 0.000 | 0.000 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-without-msa-gnomad-mean` | w/o MSA | gnomAD | mean | 2.773 | 2.773 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-without-msa-gnomad-max` | w/o MSA | gnomAD | max | 3.093 | 3.093 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-msa-frequency-clinvar-mean` | MSA frequency (no neural net) | ClinVar | mean | 0.950 | 0.950 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-msa-frequency-clinvar-max` | MSA frequency (no neural net) | ClinVar | max | 0.950 | 0.950 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-msa-frequency-cosmic-mean` | MSA frequency (no neural net) | COSMIC | mean | 0.270 | 0.270 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-msa-frequency-cosmic-max` | MSA frequency (no neural net) | COSMIC | max | 0.270 | 0.270 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-msa-frequency-omim-mean` | MSA frequency (no neural net) | OMIM | mean | 0.031 | 0.031 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-msa-frequency-omim-max` | MSA frequency (no neural net) | OMIM | max | 0.031 | 0.031 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-msa-frequency-gnomad-mean` | MSA frequency (no neural net) | gnomAD | mean | 15.122 | 15.122 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-msa-frequency-gnomad-max` | MSA frequency (no neural net) | gnomAD | max | 15.122 | 15.122 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-phylop-phastcons-combined-clinvar-mean` | Combined phyloP and phastCons | ClinVar | mean | 0.928 | 0.928 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-phylop-phastcons-combined-clinvar-max` | Combined phyloP and phastCons | ClinVar | max | 0.928 | 0.928 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-phylop-phastcons-combined-cosmic-mean` | Combined phyloP and phastCons | COSMIC | mean | 0.141 | 0.141 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-phylop-phastcons-combined-cosmic-max` | Combined phyloP and phastCons | COSMIC | max | 0.141 | 0.141 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-phylop-phastcons-combined-omim-mean` | Combined phyloP and phastCons | OMIM | mean | 0.039 | 0.039 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-phylop-phastcons-combined-omim-max` | Combined phyloP and phastCons | OMIM | max | 0.039 | 0.039 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-phylop-phastcons-combined-gnomad-mean` | Combined phyloP and phastCons | gnomAD | mean | 13.919 | 13.919 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-phylop-phastcons-combined-gnomad-max` | Combined phyloP and phastCons | gnomAD | max | 13.919 | 13.919 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-train-50pct-conserved-clinvar-mean` | Train on 50% most conserved | ClinVar | mean | 0.963 | 0.963 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-train-50pct-conserved-clinvar-max` | Train on 50% most conserved | ClinVar | max | 0.963 | 0.963 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-train-50pct-conserved-cosmic-mean` | Train on 50% most conserved | COSMIC | mean | 0.241 | 0.241 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-train-50pct-conserved-cosmic-max` | Train on 50% most conserved | COSMIC | max | 0.257 | 0.257 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-train-50pct-conserved-omim-mean` | Train on 50% most conserved | OMIM | mean | 0.125 | 0.125 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-train-50pct-conserved-omim-max` | Train on 50% most conserved | OMIM | max | 0.139 | 0.139 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-train-50pct-conserved-gnomad-mean` | Train on 50% most conserved | gnomAD | mean | 32.116 | 32.116 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-train-50pct-conserved-gnomad-max` | Train on 50% most conserved | gnomAD | max | 35.286 | 35.286 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-train-100pct-genome-clinvar-mean` | Train on 100% of genome | ClinVar | mean | 0.960 | 0.960 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-train-100pct-genome-clinvar-max` | Train on 100% of genome | ClinVar | max | 0.961 | 0.961 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-train-100pct-genome-cosmic-mean` | Train on 100% of genome | COSMIC | mean | 0.210 | 0.210 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-train-100pct-genome-cosmic-max` | Train on 100% of genome | COSMIC | max | 0.224 | 0.224 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-train-100pct-genome-omim-mean` | Train on 100% of genome | OMIM | mean | 0.120 | 0.120 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-train-100pct-genome-omim-max` | Train on 100% of genome | OMIM | max | 0.122 | 0.122 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-train-100pct-genome-gnomad-mean` | Train on 100% of genome | gnomAD | mean | 27.964 | 27.964 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-train-100pct-genome-gnomad-max` | Train on 100% of genome | gnomAD | max | 30.717 | 30.717 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-include-closest-primates-clinvar-mean` | Include closest primates | ClinVar | mean | 0.954 | 0.954 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-include-closest-primates-clinvar-max` | Include closest primates | ClinVar | max | 0.956 | 0.956 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-include-closest-primates-cosmic-mean` | Include closest primates | COSMIC | mean | 0.214 | 0.214 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-include-closest-primates-cosmic-max` | Include closest primates | COSMIC | max | 0.219 | 0.219 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-include-closest-primates-omim-mean` | Include closest primates | OMIM | mean | 0.139 | 0.139 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-include-closest-primates-omim-max` | Include closest primates | OMIM | max | 0.156 | 0.156 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-include-closest-primates-gnomad-mean` | Include closest primates | gnomAD | mean | 24.674 | 24.674 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-include-closest-primates-gnomad-max` | Include closest primates | gnomAD | max | 26.721 | 26.721 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-51-mammals-clinvar-mean` | 51 mammals | ClinVar | mean | 0.964 | 0.964 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-51-mammals-clinvar-max` | 51 mammals | ClinVar | max | 0.965 | 0.965 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-51-mammals-cosmic-mean` | 51 mammals | COSMIC | mean | 0.323 | 0.323 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-51-mammals-cosmic-max` | 51 mammals | COSMIC | max | 0.325 | 0.325 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-51-mammals-omim-mean` | 51 mammals | OMIM | mean | 0.073 | 0.073 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-51-mammals-omim-max` | 51 mammals | OMIM | max | 0.076 | 0.076 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-51-mammals-gnomad-mean` | 51 mammals | gnomAD | mean | 41.381 | 41.381 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-51-mammals-gnomad-max` | 51 mammals | gnomAD | max | 43.408 | 43.408 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-51-vertebrates-clinvar-mean` | 51 vertebrates | ClinVar | mean | 0.967 | 0.967 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-51-vertebrates-clinvar-max` | 51 vertebrates | ClinVar | max | 0.967 | 0.967 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-51-vertebrates-cosmic-mean` | 51 vertebrates | COSMIC | mean | 0.342 | 0.342 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-51-vertebrates-cosmic-max` | 51 vertebrates | COSMIC | max | 0.347 | 0.347 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-51-vertebrates-omim-mean` | 51 vertebrates | OMIM | mean | 0.101 | 0.101 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-51-vertebrates-omim-max` | 51 vertebrates | OMIM | max | 0.108 | 0.108 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-51-vertebrates-gnomad-mean` | 51 vertebrates | gnomAD | mean | 41.624 | 41.624 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-51-vertebrates-gnomad-max` | 51 vertebrates | gnomAD | max | 46.792 | 46.792 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-no-upweight-conserved-clinvar-mean` | Don’t upweight conserved | ClinVar | mean | 0.967 | 0.967 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-no-upweight-conserved-clinvar-max` | Don’t upweight conserved | ClinVar | max | 0.967 | 0.967 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-no-upweight-conserved-cosmic-mean` | Don’t upweight conserved | COSMIC | mean | 0.303 | 0.303 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-no-upweight-conserved-cosmic-max` | Don’t upweight conserved | COSMIC | max | 0.309 | 0.309 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-no-upweight-conserved-omim-mean` | Don’t upweight conserved | OMIM | mean | 0.133 | 0.133 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-no-upweight-conserved-omim-max` | Don’t upweight conserved | OMIM | max | 0.152 | 0.152 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-no-upweight-conserved-gnomad-mean` | Don’t upweight conserved | gnomAD | mean | 37.094 | 37.094 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-no-upweight-conserved-gnomad-max` | Don’t upweight conserved | gnomAD | max | 39.991 | 39.991 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-no-replace-nonconserved-clinvar-mean` | Don’t replace non-conserved | ClinVar | mean | 0.966 | 0.966 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-no-replace-nonconserved-clinvar-max` | Don’t replace non-conserved | ClinVar | max | 0.967 | 0.967 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-no-replace-nonconserved-cosmic-mean` | Don’t replace non-conserved | COSMIC | mean | 0.333 | 0.333 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-no-replace-nonconserved-cosmic-max` | Don’t replace non-conserved | COSMIC | max | 0.340 | 0.340 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-no-replace-nonconserved-omim-mean` | Don’t replace non-conserved | OMIM | mean | 0.111 | 0.111 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-no-replace-nonconserved-omim-max` | Don’t replace non-conserved | OMIM | max | 0.112 | 0.112 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-no-replace-nonconserved-gnomad-mean` | Don’t replace non-conserved | gnomAD | mean | 41.853 | 41.853 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-no-replace-nonconserved-gnomad-max` | Don’t replace non-conserved | gnomAD | max | 45.213 | 45.213 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-256-clinvar-mean` | Window size = 256 | ClinVar | mean | 0.969 | 0.969 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-256-clinvar-max` | Window size = 256 | ClinVar | max | 0.969 | 0.969 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-256-cosmic-mean` | Window size = 256 | COSMIC | mean | 0.366 | 0.366 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-256-cosmic-max` | Window size = 256 | COSMIC | max | 0.376 | 0.376 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-256-omim-mean` | Window size = 256 | OMIM | mean | 0.119 | 0.119 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-256-omim-max` | Window size = 256 | OMIM | max | 0.128 | 0.128 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-256-gnomad-mean` | Window size = 256 | gnomAD | mean | 37.908 | 37.908 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-256-gnomad-max` | Window size = 256 | gnomAD | max | 42.957 | 42.957 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-64-clinvar-mean` | Window size = 64 | ClinVar | mean | 0.968 | 0.968 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-64-clinvar-max` | Window size = 64 | ClinVar | max | 0.968 | 0.968 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-64-cosmic-mean` | Window size = 64 | COSMIC | mean | 0.340 | 0.340 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-64-cosmic-max` | Window size = 64 | COSMIC | max | 0.348 | 0.348 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-64-omim-mean` | Window size = 64 | OMIM | mean | 0.111 | 0.111 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-64-omim-max` | Window size = 64 | OMIM | max | 0.119 | 0.119 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-64-gnomad-mean` | Window size = 64 | gnomAD | mean | 37.478 | 37.478 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-64-gnomad-max` | Window size = 64 | gnomAD | max | 39.522 | 39.522 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-32-clinvar-mean` | Window size = 32 | ClinVar | mean | 0.967 | 0.967 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-32-clinvar-max` | Window size = 32 | ClinVar | max | 0.967 | 0.967 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-32-cosmic-mean` | Window size = 32 | COSMIC | mean | 0.323 | 0.323 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-32-cosmic-max` | Window size = 32 | COSMIC | max | 0.328 | 0.328 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-32-omim-mean` | Window size = 32 | OMIM | mean | 0.108 | 0.108 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-32-omim-max` | Window size = 32 | OMIM | max | 0.121 | 0.121 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-32-gnomad-mean` | Window size = 32 | gnomAD | mean | 36.664 | 36.664 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-32-gnomad-max` | Window size = 32 | gnomAD | max | 38.866 | 38.866 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-16-clinvar-mean` | Window size = 16 | ClinVar | mean | 0.964 | 0.964 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-16-clinvar-max` | Window size = 16 | ClinVar | max | 0.965 | 0.965 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-16-cosmic-mean` | Window size = 16 | COSMIC | mean | 0.246 | 0.246 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-16-cosmic-max` | Window size = 16 | COSMIC | max | 0.250 | 0.250 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-16-omim-mean` | Window size = 16 | OMIM | mean | 0.095 | 0.095 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-16-omim-max` | Window size = 16 | OMIM | max | 0.106 | 0.106 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-16-gnomad-mean` | Window size = 16 | gnomAD | mean | 29.203 | 29.203 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-16-gnomad-max` | Window size = 16 | gnomAD | max | 31.623 | 31.623 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-8-clinvar-mean` | Window size = 8 | ClinVar | mean | 0.961 | 0.961 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-8-clinvar-max` | Window size = 8 | ClinVar | max | 0.961 | 0.961 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-8-cosmic-mean` | Window size = 8 | COSMIC | mean | 0.188 | 0.188 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-8-cosmic-max` | Window size = 8 | COSMIC | max | 0.209 | 0.209 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-8-omim-mean` | Window size = 8 | OMIM | mean | 0.080 | 0.080 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-8-omim-max` | Window size = 8 | OMIM | max | 0.086 | 0.086 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-8-gnomad-mean` | Window size = 8 | gnomAD | mean | 21.159 | 21.159 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-8-gnomad-max` | Window size = 8 | gnomAD | max | 21.943 | 21.943 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-4-clinvar-mean` | Window size = 4 | ClinVar | mean | 0.942 | 0.942 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-4-clinvar-max` | Window size = 4 | ClinVar | max | 0.943 | 0.943 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-4-cosmic-mean` | Window size = 4 | COSMIC | mean | 0.131 | 0.131 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-4-cosmic-max` | Window size = 4 | COSMIC | max | 0.155 | 0.155 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-4-omim-mean` | Window size = 4 | OMIM | mean | 0.052 | 0.052 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-4-omim-max` | Window size = 4 | OMIM | max | 0.053 | 0.053 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-4-gnomad-mean` | Window size = 4 | gnomAD | mean | 13.457 | 13.457 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-ablation-window-4-gnomad-max` | Window size = 4 | gnomAD | max | 14.789 | 14.789 | yes | no |
| `gfm-guides-20261014-gpnmsa-result-dms-tadbp-esm-1b-auroc` | DMS TADBP (Results text) | - | - | 0.75 | not retrieved | unknown | not compared |
| `gfm-guides-20261014-gpnmsa-result-dms-tadbp-gpn-msa-auroc` | DMS TADBP (Results text) | - | - | 0.83 | not retrieved | unknown | not compared |

## What else the published version changes

- **Table numbering.** Preprint Supplementary Tables 1, 2 and 3 keep their numbers. The ablation
  study moves from preprint Supplementary Table 4 to Extended Data Table 1. Preprint Supplementary
  Table 5 (training hyperparameters) becomes published Supplementary Table 4. Preprint
  Supplementary Table 6 (functional annotations) stays Supplementary Table 6. A stored locator
  reading "Supplementary Table 4" therefore names the ablation study in the preprint and the
  hyperparameter table in the published version. Claim
  `gpn-msa-published-20261116-claim-table-numbering`.
- **Sample sizes.** The published Figure 2 caption prints the exact size of each comparison, which
  the preprint does not: ClinVar 21,273 versus 15,402; COSMIC 183 versus 15,399; OMIM 406 versus
  2,573,918; gnomAD (full set) 252,706,195 versus 5,894,721. The four stored dataset records carry
  `missing_metadata.denominator` with reason `unreported` on the strength of the preprint. The
  counts are recorded as four `denominator` claims. The gnomAD one says explicitly that the
  252,706,195 versus 5,894,721 figures are the full set and not the ablation set, which subsets
  the rare variants to the common count and whose size neither version prints.
- **New table.** Published Supplementary Table 5, best score quantiles for summarising variant
  scores into gene-level scores, has no counterpart in the preprint. It is a chosen setting, not a
  measured result, and the store holds no GPN-MSA gene-essentiality protocol to attach it to, so
  it is recorded in the numbering claim and not extracted.
- **New figure panel.** Figure 2d, ClinVar pathogenic versus ClinVar benign missense variants, is
  new. It is figure-only, so it carries no extractable value.
- **Reporting Summary.** The published version has one, the preprint does not. It is a two-page
  Nature Portfolio form with no text layer and no measured values, so it is not registered as a
  source. Its "Data analysis" box names Ensembl VEP Release 109 and Hugging Face Transformers
  4.29.2, which the store does not hold for GPN-MSA. Left as a lead in `scope-audit.jsonl` rather
  than extracted, because registering a sixth source for a software-stack fact is outside this
  batch's question.
- **Unchanged values elsewhere.** Published Supplementary Tables 1 and 2 (held-out accuracy and
  median perplexity on chromosome 22, 16 cells over CDS, 5' UTR, 3' UTR and non-exonic, with the
  same stated 39M and 245K position counts) print the same values as the preprint. Those 16 cells
  are in neither version's stored records: the earlier batch left them out as language-model
  metrics. Recorded as claim
  `gpn-msa-published-20261116-claim-held-out-accuracy-unchanged`.

## Decisions and why

- **No duplicate results.** The 136 published values are identical to the stored ones from the
  same study. Writing them again as results under the published source would put two records with
  the same number, the same system and the same protocol into the graph from one piece of work,
  which reads downstream as two independent agreeing measurements. The batch records the agreement
  as a claim instead.
- **Reused identities only.** No new model, configuration, benchmark, protocol, dataset or
  comparator was created. The batch's claims point at the existing
  `gfm-guides-20261014-gpnmsa-*` records and at the preprint source.
- **No stored record edited.** No `records -- change` was run. The recommendations below are for
  the reviewer.
- **`companion_of` direction.** The published article source links `companion_of` to the preprint
  source. The natural reading is the other way round, the preprint belonging with the version of
  record, but that link would have to be added to the stored preprint record, which an extractor
  must not edit. See the reviewer questions.
- **No `supersedes` link.** The published version supersedes the preprint as a citation, but the
  preprint is still the artifact the 138 stored results were read from, and marking it superseded
  could withhold them. Left for the reviewer.
- **No `coverage.json`.** This is not use-case work; no relevance judgement or use-case summary was
  written.
- **No `value-check.tsv`.** `npm run batch -- check-values` needs result records and a readable
  text layer. This batch has no results, and the one published values table is an image.

## Gaps

1. The peer-reviewed Results and Methods body was not retrieved. It is paywalled at nature.com and
   absent from PMC, Europe PMC, Unpaywall and OpenAlex.
2. Because of 1, the two stored DMS TADBP AUROCs (GPN-MSA 0.83, ESM-1b 0.75,
   `gfm-guides-20261014-gpnmsa-result-dms-tadbp-gpn-msa-auroc` and
   `...-esm-1b-auroc`) could not be compared with the published version.
3. Extended Data Table 1 has no text layer, so the published values rest on a visual
   transcription with no parser and no OCR cross-check.
4. Figure 1, Figure 2 and Extended Data Figures 1 to 8 print no numbers beyond the Figure 2 sample
   sizes. No Source Data file is published, so the figure values cannot be computed under the
   derivation rule either. The main comparisons with CADD, phyloP, phastCons, ESM-1b, Nucleotide
   Transformer, HyenaDNA, Enformer and SpliceAI stay unextracted in both versions.
5. The published version's Methods may define the ablations differently from the preprint's; the
   caption says "Ablations are detailed in Methods" and that section was not retrieved. The values
   being identical is evidence the settings did not change, not proof.

## Recommendations for the reviewer, not applied here

1. **Do not add the published source to the 136 stored results' `source_ids`.** Their
   `source_locator` reads "Supplementary Table 4 (PDF page 23)", which is false for the published
   artifact: there the table is Extended Data Table 1 and page 23 is a supplementary figure. The
   alternative, 136 `records -- change` calls rewriting each locator to name both versions, buys
   little and rewrites a large block of reviewed provenance. The `companion_of` edge, the
   comparison claim and the dated review already make the published version traceable.
2. **Consider updating the preprint source record's limitations.** Its first entry says the
   published Extended Data Table 1 "was not read, so the printed values here may differ from the
   journal version". That is now answered: they do not differ. Its fourth entry, about the
   caption's Figure 2 pointers, can cite the published caption as the resolution.
3. **Consider the three `denominator` claims against the dataset records.** The ClinVar, COSMIC and
   OMIM dataset records carry `missing_metadata.denominator` with reason `unreported`. The
   published version prints the counts, so the reviewer may want to move them onto the records
   through `records -- change` and keep the claims as the evidence.

## Questions the reviewer must rule on

1. **Is the visual transcription of Extended Data Table 1 accepted as the published reading?** The
   table is published only as an image. The skill forbids reading numbers from pixels and names
   page render as an extraction method; this sits between the two. The reviewer must re-read the
   image, without the stored values to hand, before accepting the "no difference" finding: the
   extractor's reading was written with the stored values in view and no parser or OCR checked it.
2. **Should the published source `supersede` the preprint source?** It is the version of record,
   but the stored results were read from the preprint and marking that source superseded may
   withhold them. Not applied.
3. **Is `companion_of` pointing the right way?** The published record points at the preprint
   because the extractor cannot edit the preprint record. If the store prefers the preprint to
   point at the version of record, that is a `records -- change` on
   `gfm-guides-20261014-gpnmsa-source-biorxiv-v2`.
4. **Should the 16 held-out accuracy cells be extracted?** They are identical in both versions and
   currently in neither. They are language-model metrics rather than variant-effect results, which
   is why the earlier batch left them out. If they belong in the store, they are a small separate
   batch.
5. **Is the comparison claim's subject right?** The three comparison claims take the preprint
   source as subject, so that a reader of that source sees what the published version does with its
   values. The benchmark record carries the numbering and panel claims instead. Either could move.
