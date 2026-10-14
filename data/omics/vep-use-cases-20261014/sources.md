# Sources

All retrievals ran on 2026-10-14 (UTC) with curl or `gh api`. Hashes are of the downloaded bytes, except PMC article pages (`pmc.ncbi.nlm.nih.gov/articles/...`), whose `artifact_sha256` is taken after blanking two per-request tokens (`extract/pmc_html.py`); the raw hash of the retrieval is in each record's `hash_scope`. Only the CC BY Pejaver et al. 2022 XML is archived (`artifacts/PMC9748256.xml.gz`, `gzip -9 -n`, gzip SHA-256 `28bb3e751d79727adf066ff165597ee76eb8ff6e03f8ccd9aca6e419ff899d0c`); the other artifacts are not archived, because their licences do not allow it or because they are not needed to re-run the extraction.

## Calibration sources for use case #151

### Bergquist et al. 2025, Genet Med 27:101402 (PMC author manuscript)

- Record: `vep-uc-20261014-source-bergquist2025`
- Artifact: https://pmc.ncbi.nlm.nih.gov/articles/PMC12208618/
- Version: PMC12208618, NIH author manuscript of Genet Med 2025;27(6):101402
- DOI: 10.1016/j.gim.2025.101402
- Retrieved: 2026-10-14T14:44:51Z
- SHA-256: `4fe954451167b5a5717a4c37f4054432e1f02fb59862d0fb909edb525e6bb8e2`
- Licence: NIH author manuscript in PMC; publisher copyright, no open licence stated

### Pejaver et al. 2022, Am J Hum Genet 109:2163 (Europe PMC full text XML)

- Record: `vep-uc-20261014-source-pejaver2022`
- Artifact: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9748256/fullTextXML
- Version: PMC9748256 (Am J Hum Genet 2022;109(12):2163)
- DOI: 10.1016/j.ajhg.2022.10.013
- Retrieved: 2026-10-14T14:44:42Z
- SHA-256: `a78c7bcaacb0ccb72291264bbe7c1f9a16867b0c6207dcbb45c3c59a14af6b3b`
- Licence: CC BY 4.0

### Stenton et al. 2024, Genet Med 26:101213 (PMC author manuscript)

- Record: `vep-uc-20261014-source-stenton2024`
- Artifact: https://pmc.ncbi.nlm.nih.gov/articles/PMC11560577/
- Version: PMC11560577, NIH author manuscript of Genet Med 2024;26(11):101213
- DOI: 10.1016/j.gim.2024.101213
- Retrieved: 2026-10-14T14:49:14Z
- SHA-256: `debe1ae8e304ac0a6272c093bcf7874977e7b9b3921dbe7f5ba096701611ebe7`
- Licence: NIH author manuscript in PMC; publisher copyright, no open licence stated

### Tejura et al. 2024, Am J Hum Genet 111:2031 (PMC)

- Record: `vep-uc-20261014-source-tejura2024`
- Artifact: https://pmc.ncbi.nlm.nih.gov/articles/PMC11393694/
- Version: PMC11393694 (Am J Hum Genet 2024;111(9):2031)
- DOI: 10.1016/j.ajhg.2024.07.018
- Retrieved: 2026-10-14T14:49:15Z
- SHA-256: `e00fb418efba3924e47db1aba3be26835dbdbb9f0a4c14aca06a61215ca16ecf`
- Licence: Not stated on the retrieved page

## Primary sources for the #153-#155 predictors

### Pir and Timucin 2025, Protein Science 34:e70030 (PMC article page)

- Record: `vep-uc-20261014-source-affipred`
- Artifact: https://pmc.ncbi.nlm.nih.gov/articles/PMC11751861/
- Version: PMC11751861 (Protein Sci 2025;34:e70030, published version of the 2024 bioRxiv preprint)
- DOI: 10.1002/pro.70030
- Retrieved: 2026-10-14T14:48:55Z
- SHA-256: `b3ea9f1fbbfd16760ebff96c8829f401c5836ed861a0db53de3ef33aff44fca8`
- Licence: Not stated on the retrieved page

### Ramakrishnan et al. 2023, Frontiers in Molecular Biosciences 10:1204157 (Europe PMC full text XML)

- Record: `vep-uc-20261014-source-deeprank-mut`
- Artifact: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10354367/fullTextXML
- Version: PMC10354367 (Front Mol Biosci 2023;10:1204157)
- DOI: 10.3389/fmolb.2023.1204157
- Retrieved: 2026-10-14T14:48:10Z
- SHA-256: `1a438f5d2ccf14f52d04f02d81b74d18998ce1e9b84b51d3455d5202b08b8cc8`
- Licence: CC BY 4.0

### Chen et al. 2025, Briefings in Bioinformatics 26:bbaf119 (Europe PMC full text XML)

- Record: `vep-uc-20261014-source-ds-mvp`
- Artifact: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11932084/fullTextXML
- Version: PMC11932084 (Brief Bioinform 2025;26:bbaf119)
- DOI: 10.1093/bib/bbaf119
- Retrieved: 2026-10-14T14:48:15Z
- SHA-256: `9ade7e429d1b794724bfeaaff953cb07cd584963d42000c8a6e7326f5ddb9db6`
- Licence: CC BY-NC 4.0

### Wang et al. 2024, BMC Bioinformatics 25:100 (Europe PMC full text XML)

- Record: `vep-uc-20261014-source-dva`
- Artifact: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10916336/fullTextXML
- Version: PMC10916336 (BMC Bioinformatics 2024;25:100)
- DOI: 10.1186/s12859-024-05709-6
- Retrieved: 2026-10-14T14:48:12Z
- SHA-256: `4aa4bcad25636e2ff0f9ddc822ce958064e0832d8aec40e907ce9a078b1174c1`
- Licence: CC BY 4.0

### Katsonis and Lichtarge 2014, Genome Research 24:2050 (Europe PMC full text XML)

- Record: `vep-uc-20261014-source-ea`
- Artifact: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4248321/fullTextXML
- Version: PMC4248321 (Genome Res 2014;24:2050)
- DOI: 10.1101/gr.176214.114
- Retrieved: 2026-10-14T14:48:19Z
- SHA-256: `4838b3936b4e35a20d397ca3ce61081da94d68e38f7f7389de8bcfb4388bcc66`
- Licence: CC BY-NC 4.0

### Moyon et al. 2022, PLoS Genetics 18:e1010191 (Europe PMC full text XML)

- Record: `vep-uc-20261014-source-finsurf`
- Artifact: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9094564/fullTextXML
- Version: PMC9094564 (PLoS Genet 2022;18:e1010191)
- DOI: 10.1371/journal.pgen.1010191
- Retrieved: 2026-10-14T14:48:23Z
- SHA-256: `b7dec2c8b051d51299c180d49cc8719d4f0d41405da9cc7c99f02d43dd87e473`
- Licence: CC BY 4.0

### Li, Wu and Wang 2024, Briefings in Bioinformatics 25:bbae248 (Europe PMC full text XML)

- Record: `vep-uc-20261014-source-funuv`
- Artifact: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11116830/fullTextXML
- Version: PMC11116830 (Brief Bioinform 2024;25:bbae248)
- DOI: 10.1093/bib/bbae248
- Retrieved: 2026-10-14T14:48:23Z
- SHA-256: `14e8a965255446180906adcb5622b1e45f76d2e8eb9c0893d039c4a86aa8a970`
- Licence: CC BY-NC 4.0

### Danner et al. 2025, NAR Genomics and Bioinformatics 7:lqaf097 (Europe PMC full text XML)

- Record: `vep-uc-20261014-source-genoseer`
- Artifact: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12288871/fullTextXML
- Version: PMC12288871 (NAR Genom Bioinform 2025;7:lqaf097)
- DOI: 10.1093/nargab/lqaf097
- Retrieved: 2026-10-14T14:48:13Z
- SHA-256: `5fd34428ca090d36dfbd4bb291ef34fc308aa1087f59af0cfea89be67ee74491`
- Licence: CC BY 4.0

### Ye et al. 2026, Nature (publisher PDF)

- Record: `vep-uc-20261014-source-gpn-star`
- Artifact: https://www.nature.com/articles/s41586-026-11005-5.pdf
- Version: Nature accelerated article preview PDF ('Published online: xx xx xxxx'; accepted 2026-08-07)
- DOI: 10.1038/s41586-026-11005-5
- Retrieved: 2026-10-14T14:55:07Z
- SHA-256: `97f61ec05d4ace41692549290db3faf019ce869459459d2c5694bf54e16d0996`
- Licence: CC BY 4.0

### Ruiz-Alías et al. 2025, Bioinformatics 41:btaf305 (Europe PMC full text XML)

- Record: `vep-uc-20261014-source-homolvar`
- Artifact: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12122210/fullTextXML
- Version: PMC12122210 (Bioinformatics 2025;41:btaf305)
- DOI: 10.1093/bioinformatics/btaf305
- Retrieved: 2026-10-14T14:48:16Z
- SHA-256: `a477b0d6208e258d0ea1d962576b615589611741cff19ac4906c9585de04fc6d`
- Licence: CC BY 4.0

### debbiemarkslab/LOL-EVE repository README ('accepted at MLCB 2025') (repository README at commit)

- Record: `vep-uc-20261014-source-lol-eve`
- Artifact: https://raw.githubusercontent.com/debbiemarkslab/LOL-EVE/deed3bd9e1203f5cdd7051105628360213eba5a2/README.md
- Version: debbiemarkslab/LOL-EVE README at commit deed3bd9e1203f5cdd7051105628360213eba5a2
- Retrieved: 2026-10-14T14:50:45Z
- SHA-256: `ffb668ed02ca9207c8f7c4737770ae05d4e5e8d76cc3fa2312c9bb26243d1d90`
- Licence: MIT (repository)

### Lai et al. 2022, Bioinformatics Advances 2:vbab045 (Europe PMC full text XML)

- Record: `vep-uc-20261014-source-lyrus`
- Artifact: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8754197/fullTextXML
- Version: PMC8754197 (Bioinformatics Advances 2022;2:vbab045)
- DOI: 10.1093/bioadv/vbab045
- Retrieved: 2026-10-14T14:48:09Z
- SHA-256: `73336d1bcfc7ecf023154c468f2e832935181c9af1bfeac90b12123fc00e5fdd`
- Licence: CC BY 4.0

### Liu et al. 2024, Genome Medicine 16:3 (Europe PMC full text XML)

- Record: `vep-uc-20261014-source-magpie`
- Artifact: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10773112/fullTextXML
- Version: PMC10773112 (Genome Med 2024;16:3)
- DOI: 10.1186/s13073-023-01274-4
- Retrieved: 2026-10-14T14:48:17Z
- SHA-256: `bfdb9eec264aee498e528540da69f1d6d9cf337e52be0d68df43e3a7beac5950`
- Licence: CC BY 4.0

### Katsonis and Lichtarge 2025, Nature Communications 16:159 (Europe PMC full text XML)

- Record: `vep-uc-20261014-source-metaea`
- Artifact: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11696468/fullTextXML
- Version: PMC11696468 (Nat Commun 2025;16:159)
- DOI: 10.1038/s41467-024-55066-4
- Retrieved: 2026-10-14T14:48:12Z
- SHA-256: `ebde9dec281e7cafc0899053fa093cc0f2e8cae82f3a4aa4fb6facfe3caba2c0`
- Licence: CC BY-NC-ND 4.0

### Nicora et al. 2022, Scientific Reports 12:2517 (Europe PMC full text XML)

- Record: `vep-uc-20261014-source-mlvar`
- Artifact: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8847497/fullTextXML
- Version: PMC8847497 (Sci Rep 2022;12:2517)
- DOI: 10.1038/s41598-022-06547-3
- Retrieved: 2026-10-14T14:48:06Z
- SHA-256: `3f94a08d3988197e56b1893dc034f677c8aa8ec29bbfe9838a5546c208cca245`
- Licence: CC BY 4.0

### Yang et al. 2026, PNAS 123:e2524289123 (Europe PMC full text XML)

- Record: `vep-uc-20261014-source-mutapheno`
- Artifact: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12890849/fullTextXML
- Version: PMC12890849 (PNAS 2026;123(6):e2524289123; published version of the 2025 bioRxiv preprint 10.1101/2025.09.03.674130)
- DOI: 10.1073/pnas.2524289123
- Retrieved: 2026-10-14T14:48:18Z
- SHA-256: `54c16ac9a0da2607496a7a464d0186c12f2de0f885c40d739f83fe17f6d1a3d1`
- Licence: CC BY-NC-ND 4.0

### Kabir et al. 2025, International Journal of Molecular Sciences 26:2004 (Europe PMC full text XML)

- Record: `vep-uc-20261014-source-pon-p3`
- Artifact: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11899954/fullTextXML
- Version: PMC11899954 (Int J Mol Sci 2025;26:2004)
- DOI: 10.3390/ijms26052004
- Retrieved: 2026-10-14T14:48:14Z
- SHA-256: `95fe055f3463d40caef9cdf97971cacfecbe2f7f34ee6835583288546841f8f9`
- Licence: CC BY 4.0

### Gao et al. 2023, Science 380(6648) (PMC article page)

- Record: `vep-uc-20261014-source-primateai-3d`
- Artifact: https://pmc.ncbi.nlm.nih.gov/articles/PMC10713091/
- Version: PMC10713091, NIH author manuscript of Science 2023;380(6648):eabn8153 as printed in the page metadata
- DOI: 10.1126/science.abn8197
- Retrieved: 2026-10-14T14:48:57Z
- SHA-256: `34a641a6fe9b14d8ca40854061ef62047c974873456ba6419a60b34379e2351a`
- Licence: NIH author manuscript in PMC; publisher copyright (AAAS)

### Illumina/PromoterAI repository README (paper: Jaganathan et al. 2025, Science 389:eads7373, not retrieved) (repository README at commit)

- Record: `vep-uc-20261014-source-promoterai`
- Artifact: https://raw.githubusercontent.com/Illumina/PromoterAI/ce9fcd080556d7e962a5946327fe8fd1a04e272b/README.md
- Version: Illumina/PromoterAI README at commit ce9fcd080556d7e962a5946327fe8fd1a04e272b
- Retrieved: 2026-10-14T14:50:44Z
- SHA-256: `1446b5732ea0aaa243d930ff5d13873b275d63fca3e6c1dbfcedd23a334e9519`
- Licence: Repository licence not asserted by GitHub; precomputed scores for academic and non-commercial use under a licence agreement (README)

### Banerjee, Bogetti and Bahar 2025, PNAS 122:e2418100122 (Europe PMC full text XML)

- Record: `vep-uc-20261014-source-rhapsody-2`
- Artifact: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12067267/fullTextXML
- Version: PMC12067267 (PNAS 2025;122:e2418100122)
- DOI: 10.1073/pnas.2418100122
- Retrieved: 2026-10-14T14:48:14Z
- SHA-256: `acaa8e8e17ae2f382ef34589186f9f8c80f8e104acc097fd956d36f024d5cc15`
- Licence: CC BY-NC-ND 4.0

### Blaabjerg et al. 2024, Nature Communications 15:9646 (Europe PMC full text XML)

- Record: `vep-uc-20261014-source-ssemb`
- Artifact: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11544099/fullTextXML
- Version: PMC11544099 (Nat Commun 2024;15:9646)
- DOI: 10.1038/s41467-024-53982-z
- Retrieved: 2026-10-14T14:48:21Z
- SHA-256: `fd067a71c6980508086f4215db9eb7d84283670fd23534b70b9b29062719b69f`
- Licence: CC BY-NC-ND 4.0

### Lin et al. 2024, Scientific Reports 14:8136 (Europe PMC full text XML)

- Record: `vep-uc-20261014-source-varipred`
- Artifact: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10999449/fullTextXML
- Version: PMC10999449 (Sci Rep 2024;14:8136, published version of the 2023 bioRxiv preprint)
- DOI: 10.1038/s41598-024-51489-7
- Retrieved: 2026-10-14T14:48:05Z
- SHA-256: `556dac407f6fe6d7dc36e61b32554039824f26e4bd34f44ac66bfb48e86427b9`
- Licence: CC BY 4.0
