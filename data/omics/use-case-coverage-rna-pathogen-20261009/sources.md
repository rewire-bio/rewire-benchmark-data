# Sources: RNA pathogen-detection use-case pass, 2026-10-09

Three studies, each pinned as an article source and a supplementary-file source, because every table extracted here lives in a supplementary workbook. Hashes are SHA-256 of the exact bytes parsed.

| Source ID | Title or file | Version | Retrieved (UTC) | Artifact URL | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `rna-pathogen-20261009-source-carbo2022` | Performance of Five Metagenomic Classifiers for Virus Pathogen Detection Using Respiratory Samples from a Clinical Cohort | Pathogens 11(3):340, published 2022-03-11; PMC8953373 full-text XML | 2026-10-09T20:06:32Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8953373/fullTextXML | `e6683855ad278a555598295fdc4166e54ddb0e39e3d971878b898b20bc8ddf95` |
| `rna-pathogen-20261009-source-carbo2022-supp` | Carbo et al., Supplementary Tables 1 and 2 | medRxiv 2022.01.21.22269647 version 1 (2022-01-21), `media-1.xlsx` | 2026-10-09T20:16:56Z | https://www.medrxiv.org/content/medrxiv/early/2022/01/21/2022.01.21.22269647/DC1/embed/media-1.xlsx | `cd3a80d785b78377e79960d0280667f98cba3305d68426fdfaf8efeecd4542d7` |
| `rna-pathogen-20261009-source-devries2021` | Benchmark of thirteen bioinformatic pipelines for metagenomic virus diagnostics using datasets from clinical samples | medRxiv 2021.05.04.21256618 version 1 (2021-05-08), JATS XML; published as J Clin Virol 141:104908 | 2026-10-09T20:15:27Z | https://www.medrxiv.org/content/early/2021/05/08/2021.05.04.21256618.source.xml | `735ce2e42ae5fe6f5a198bdc14fd2e92ef27fc1d3734d2137a3c86d24480c718` |
| `rna-pathogen-20261009-source-devries2021-supp` | de Vries et al., Supplementary Tables 2-4 | medRxiv 2021.05.04.21256618 version 1, `media-1.xlsx` | 2026-10-09T20:15:56Z | https://www.medrxiv.org/content/medrxiv/early/2021/05/08/2021.05.04.21256618/DC1/embed/media-1.xlsx | `be0ea61fcffe8ea580077467ca19ef1ac39e88bbc82d916bc65b58a6683214f6` |
| `rna-pathogen-20261009-source-meyer2022` | Critical Assessment of Metagenome Interpretation: the second round of challenges | Nature Methods 19(4):429, published 2022-04-08; PMC9007738 full-text XML | 2026-10-09T20:21:44Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9007738/fullTextXML | `2532db9c9abd1f040047afdcc859cb83739a9cceb4dbd998cd550017da9bd7ba` |
| `rna-pathogen-20261009-source-meyer2022-supp` | Meyer et al., Supplementary Tables 1-40 | `41592_2022_1431_MOESM3_ESM.xlsx`, as linked from the article XML | 2026-10-09T20:18:45Z | https://static-content.springer.com/esm/art%3A10.1038%2Fs41592-022-01431-4/MediaObjects/41592_2022_1431_MOESM3_ESM.xlsx | `9a5ebd2364bb2660ea841227b9d04848b9c60b4d3c2a9f4939fc5994efc851ce` |

DOIs: 10.3390/pathogens11030340, 10.1101/2022.01.21.22269647, 10.1101/2021.05.04.21256618 (published 10.1016/j.jcv.2021.104908), 10.1038/s41592-022-01431-4.

## Licences and what is archived

| Source | Licence | Archived here |
| --- | --- | --- |
| Carbo et al. article | CC BY 4.0 (Europe PMC record and article XML) | `artifacts/carbo2022-article.xml.gz` |
| Carbo et al. supplement | CC BY-ND 4.0 (medRxiv API record for version 1) | No. The licence forbids derivative works, and the no-derivatives term makes redistribution of the file unsafe to assume. The hash and URL are recorded. |
| de Vries et al. preprint and supplement | CC BY-NC-ND 4.0 (JATS `<license>`) | No, for the same reason. |
| Meyer et al. article and supplement | CC BY 4.0 (article XML `<license>`; the article licence covers its supplementary information) | `artifacts/meyer2022-article.xml.gz`, `artifacts/meyer2022-supplementary-tables.xlsx.gz` |

| Archived file | SHA-256 of gzip |
| --- | --- |
| `artifacts/carbo2022-article.xml.gz` | `7c1c12cb42d9035926ff3f12186a86bb5ea3bdb486eadbef9aa6315345f3507a` |
| `artifacts/meyer2022-article.xml.gz` | `1fe06987d9ab6afd81e22428443a999e9b362beb57fe880df63022138bc18b4c` |
| `artifacts/meyer2022-supplementary-tables.xlsx.gz` | `4a6eb7b4b96bf8cf961214194263f040203ae2fdf8ef0e54596852bb86741ba8` |

## Why two sources use preprint versions

- **Carbo et al.**: the article is pinned from Europe PMC, but its own supplement could not be retrieved. Europe PMC returned a truncated zip twice (220,580 and 245,132 bytes, no end-of-central-directory record), MDPI returned HTTP 403, and the PMC file link returned a browser challenge page. The medRxiv preprint version 1 carries the same two supplementary tables with the same titles, so its workbook is pinned instead. Whether any value differs between the two is not known and is recorded as a gap.
- **de Vries et al.**: the published version (PMC7615111, CC BY) could not be retrieved at all. Europe PMC full-text XML returned HTTP 500 twice, and the Europe PMC PDF, the UCL repository copy, the Leiden repository copy and the medRxiv PDF all returned HTTP 403 or an access-blocked page. The preprint JATS XML and its supplementary workbook are pinned. Tables 1 and 2 of the preprint are images, so pipeline characteristics and read-count categories were not transcribed.

## Tables used

| Source | Tables | Cells extracted |
| --- | --- | --- |
| Carbo et al. supplement | Supplementary Table 1, all three sheets: species (cut-off 0 and cut-off 10), genus, family; each with three pre-processing blocks of five classifiers | 720 results (12 blocks x 5 rows x 12 value columns) |
| de Vries et al. supplement | Supplementary Table 2 (14 pipeline rows: 15 target read counts plus the two summary columns where printed) and Supplementary Table 4 (13 rows, columns O-T) | 210 + 78 results |
| Meyer et al. supplement | Supplementary Table 39, all ten submissions | 20 results |

Supplementary Table 2 of Carbo et al. (regression of read counts on Ct values) duplicates the LR slope, intercept and r2 columns of Supplementary Table 1 and was not extracted separately. Supplementary Table 3 of de Vries et al. (taxonomic level reported per pipeline) was read but not extracted; it is free-text taxon names rather than scored values.

## Authorship and origin

- **Carbo et al. 2022** declare no conflict of interest and evaluate third-party tools against their own cohort. All 60 evaluations are `independent_paper`. Genome Detective is a commercial web application used as a service.
- **de Vries et al. 2021**: the majority of pipelines were developed or adapted at a participating laboratory, whose staff co-author the paper, so those evaluations are `author_reported`. Centrifuge and the four commercial platforms (DNASTAR, Genome Detective, One Codex, Taxonomer) are `independent_paper`. DAMIAN is `unreported`: it is open source and the paper does not say whether the participants running it developed it.
- **Meyer et al. 2022**: challenge submissions came from participating teams whose relationship to each tool is not stated per submission, so all ten evaluations are `unreported`.
