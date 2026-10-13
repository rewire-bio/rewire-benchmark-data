# Sources: SpliceAI2, Jaganathan et al. 2026 (bioRxiv v1)

Values are extracted from the bioRxiv v1 PDF, which has a DOI and a licence. The Illumina-hosted PDF is the same manuscript and is recorded so the link in the README and announcement resolves to a pinned record. No journal version was found on 2026-10-13. Source bytes are not archived in this folder (CC BY-NC 4.0 and proprietary terms; hashes are enough to re-verify).

## `rna-splicing-20261013-spliceai2-source-article` (pinned version)

- URL: https://doi.org/10.64898/2026.10.08.757673
- Artifact: https://www.biorxiv.org/content/10.64898/2026.10.08.757673v1.full.pdf
- Version: bioRxiv preprint version 1, posted 2026-10-11; 57-page PDF
- Retrieved: 2026-10-13T12:40:34Z
- SHA-256: `f8f3db2c3943d4827b670bc2e962e0cec8fbe96e0b1acf9d4a9b9f0c7a78c06b`
- Licence: CC BY-NC 4.0

## `rna-splicing-20261013-spliceai2-source-supplementary-table-1`

- URL: https://www.biorxiv.org/content/biorxiv/early/2026/10/11/2026.10.08.757673/DC1/embed/media-1.tsv?download=true
- Version: bioRxiv v1 supplement DC1 (757673_file02.tsv), the only supplement
- Retrieved: 2026-10-13T12:40:34Z
- SHA-256: `f46bf8c10880cc2359b6070c1e85af8e5ae7768f75e2580970f6078b54415be7`
- Licence: CC BY-NC 4.0

## `rna-splicing-20261013-spliceai2-source-illumina-pdf`

- URL: https://assets.illumina.com/content/dam/illumina-marketing/images/genomics-research/articles/spliceai2/SpliceAI2.pdf
- Version: Illumina-hosted PDF, HTTP Last-Modified 2026-10-08T12:39:35Z (mutable location; the hash describes one retrieval)
- Retrieved: 2026-10-13T12:38:36Z
- SHA-256: `2a264f98acb30e9598a5525461080b9b2891f112ea48f2fb2f8129e605a93be9`
- Licence: not printed
- Text layer matches the bioRxiv PDF word for word apart from the bioRxiv licence header and the reading order of some rotated figure labels.

## `rna-splicing-20261013-spliceai2-source-github-readme`

- URL: https://github.com/Illumina/SpliceAI2/blob/1dcd2a1882a8223095e7529982ae70bcb658340a/README.md
- Version: commit `1dcd2a1882a8223095e7529982ae70bcb658340a` (main, 2026-10-11). Tag v2.0 is commit `aa634374bc8700414b1a5388729faed7c4f7ba07`; the two later commits change README.md only.
- Retrieved: 2026-10-13T12:41:22Z
- SHA-256: `7973d1c0620d40ee954d3434b645018dcdfffca3c6649b1c69169df745a4a433`

## `rna-splicing-20261013-spliceai2-source-github-licence`

- URL: https://github.com/Illumina/SpliceAI2/blob/1dcd2a1882a8223095e7529982ae70bcb658340a/LICENSE
- Version: same commit; unchanged since v2.0
- Retrieved: 2026-10-13T12:41:22Z
- SHA-256: `70298b77bd30d2ddfbe01d67b100363599b0b98ccb920e859abcf2a9d15a9c36`
- Licence: SpliceAI2 Model Terms of Use (non-commercial organisations only; research use only)

## Read but not recorded as sources

| Artifact | Retrieved | SHA-256 | Why not a source record |
| --- | --- | --- | --- |
| bioRxiv JATS XML, https://www.biorxiv.org/content/early/2026/10/11/2026.10.08.757673.source.xml | 2026-10-13T12:40:22Z | `b15a42024ef755cfab08d2f7e678957e5ac8a4efb63a61c7315b826f8bd69138` | Front matter only (14 KB); used to find the supplement and licence |
| Announcement, https://www.illumina.com/science/genomics-research/articles/introducing-spliceai2--the-next-generation-of-splicing-and-trans.html | 2026-10-13T12:41:32Z | `db4d6057816fd4a352617891986b18422e5248898bd94c564cd759299ee8a8a3` | Press page (lead only); no values beyond the paper |
| Hugging Face model metadata, https://huggingface.co/api/models/illumina-ai/SpliceAI2 | 2026-10-13T12:44:39Z | not hashed (API JSON) | Revision `55948bae9b3638009178aadbf9d9a51c1017814f`, gated; files `spliceai2_multispecies_13M_01/model.ckpt` and `_02/model.ckpt`. Weights not downloaded. |
| setup.py at commit 1dcd2a1 | 2026-10-13T12:41:22Z | `82cf103afd220e487e1f5cbcc634534eaaaa24e777ee38b9a54100dcaf439f2a` | Confirms package version 2.0 and licence name; nothing extracted |
