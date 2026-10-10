# Sources: structural hypotheses use-case pass, 2026-10-09

Hashes are SHA-256 of the exact bytes read. Times are UTC. Both sources are CC BY 4.0 JATS XML from the Europe PMC REST API. Gzip copies (`gzip -n -9`) are archived in `artifacts/`.

| Source ID | What | Version | Retrieved | Artifact URL | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `structural-20261009-source-fromm2026` | Fromm, Ludaic and Elofsson, Evaluating deep learning based structure prediction methods on antibody-antigen complexes | Bioinformatics 42(4):btag136, 2026; PMC13061134 | 21:21:58 | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13061134/fullTextXML | `a7320667ed6f7d8df440d90275d976b91d2fe98411172a79c6a304eb3f02275d` |
| `structural-20261009-source-smorodina2026` | Smorodina et al., Structural Plausibility Without Binding Specificity: Limits of AI-Based Antibody-Antigen Structure Prediction Confidence Scores | bioRxiv 10.64898/2026.03.02.709004 version 1, posted 2026-03-03; Europe PMC PPR1221387; not peer reviewed | 21:25:48 | https://www.ebi.ac.uk/europepmc/webservices/rest/PPR1221387/fullTextXML | `0ad24054d98fd1888fa8bf3120f76e22f7bf6b1965261b16f045986d72c50732` |

| Archive | SHA-256 of the gzip file |
| --- | --- |
| `artifacts/fromm2026-article.xml.gz` | `ca5a13544dfc5efbd48acdb8170cc1840ef8b932f3dcada068d4ad53b33b48e8` |
| `artifacts/smorodina2026-article.xml.gz` | `84551bd369c8aacc8164cc508c82d3e1e42725862c5771c5a82ab24d0d1e1191` |

Independence: neither group developed AlphaFold3, Boltz or Chai-1. Fromm et al. compare pDockQ2, which their group published (Zhu et al. 2023); that row's evaluation has origin `author_reported`, as do the four oracle rows the source defines. Smorodina et al. print advisory, consulting and employment roles for one author with antibody-discovery companies, none a developer of the tools compared; this is on the source's `scope_note`.

## No evidence concerns

Neither source carries an `evidence_concerns` entry. Four points are recorded on the records instead, because none is a conflict between printed values:

| Where | What |
| --- | --- |
| Smorodina protocols, `limitations` | The curation text calls Boltz-2's training cutoff the earliest of the three tools; the methods give Chai-1 about 12 January 2021, AF3 about 30 September 2021 and Boltz-2 about 1 June 2023. The per-tool train and test counts follow the methods. |
| `structural-20261009-protocol-fromm2026-abag-model-selection`, `limitations` | Figure 6 and the text give a per-target correlation of 0.28 for ranking confidence; Table 1 prints 0.214 under a Spearman caption. The figure does not state its correlation type, so the two may differ by method. |
| `structural-20261009-protocol-fromm2026-abag-model-selection`, `limitations` | Table 1 does not state how many models it ranks per target; its DockQ row matches the best-of-200 value in the text, so it is read as selection among 200. |
| AF3 N = 100 sampling result, `rounding_note` | Printed Δ=+0.43 while the printed medians (0.24 to 0.68) differ by 0.44; consistent with rounding. |

## Reused records

Model records `discovery-model-alphafold-3`, `catalog-model-boltz-2`, `discovery-model-boltz` (Boltz-1, as in the FoldBench configuration) and `catalog-model-chai-1`, by `configuration_of`. The two FoldBench judgements cite `ucc-research-source-foldbench-paper` and `ucc-research-source-foldbench-supp`, both clean, and add no records.
