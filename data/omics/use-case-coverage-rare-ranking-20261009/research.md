# Research: rare-disease candidate ranking use-case pass, 2026-10-09

Use case: `use-case-rare-disease-candidate-ranking` ("Which methods recover causal variants and genes within a realistic laboratory review budget?"). Existing judgements, all `proxy`: seven Talos and Exomiser protocols from the Talos study and the Feng pathogenic/common variant classification. Their sources are not reused. Exclusions: ranking does not establish pathogenicity or diagnosis; balanced pathogenic/benign classification is not case-level performance; reanalysis, risk and treatment are separate.

Bounds: cutoff 2026-10-09; budget 25 queries, 4 used; at most 3 sources extracted. Lane `genomics`.

## Queries

| # | Time (UTC) | Query | Channel | Outcome |
| --- | --- | --- | --- | --- |
| 1 | 21:17:54 | `(Exomiser OR LIRICAL OR AMELIE OR Xrare OR Phen2Gene OR CADA OR GADO OR PhenIX) AND (benchmark OR comparison OR "head-to-head") AND ("top 1" OR "top-1" OR "top 10" OR "top-10" OR "top 5" OR rank) AND (rare disease OR diagnos*) AND PUB_YEAR:[2019 TO 2026]` | Europe PMC REST | 1,031 hits; Yuan et al. 2022 (PMC8921623), Yuan et al. 2024 (PMC10838329), Reese et al. 2026, PhEval |
| 2 | 21:20:19 | `("large language model" OR GPT-4 OR LLM) AND ("gene prioritization" OR "gene prioritisation" OR "causal gene") AND (Phen2Gene OR Exomiser OR LIRICAL OR AMELIE) AND (top OR rank) AND PUB_YEAR:[2023 TO 2026]` | Europe PMC REST | 15 hits; Kafkas et al. 2025 (PMC12041562), Kim et al. 2024 (PMC11480789) |
| 3 | 21:25:01 | `("100,000 Genomes" OR "100000 Genomes" OR "Undiagnosed Diseases Network" OR UDN OR CAGI) AND (Exomiser OR LIRICAL OR AMELIE OR Xrare OR "variant prioritization" OR "variant prioritisation") AND (comparison OR benchmark) AND ("top 10" OR "top-10" OR "top 1" OR "top-1" OR rank) AND PUB_YEAR:[2019 TO 2026]` | Europe PMC REST | 93 hits; Exomiser/Genomiser optimisation (Genome Med 2025), patient-to-patient matching preprint; no new multi-tool table screened |
| 4 | 21:25:01 | `(Jacobsen OR Robinson) AND (Exomiser) AND (LIRICAL OR PhEval) AND (benchmark) AND PUB_YEAR:[2021 TO 2026]` | Europe PMC REST | 13 hits; Jacobsen et al. 2022 Hum Mutat (review), PhEval |

## Decisions

| Source | Decision | Reason |
| --- | --- | --- |
| Yuan et al. 2022, Brief Bioinform, SM Table 3 | Extract all cells | Independent comparison of 10 prioritisers (11 configurations) on 305 solved DDD exomes and 209 in-house exomes, top-1 to top-50 causal-gene recovery |
| Yuan et al. 2024, Sci Rep, Table 1 | Extract all cells | Same group: Exomiser, PhenIX and AMELIE under four parameter and trio-mode protocols, plus LIRICAL, on 305 DDD trios and 152 in-house trios |
| Kafkas et al. 2025, Sci Rep, Table 3 | Extract all cells; proxy | GPT-4 versus Exomiser gene scores on synthetic candidate sets of 5 to 100 genes; the only printed LLM-versus-tool table found |
| Reese et al. 2026, EJHG | Not extracted | Seven LLMs versus Exomiser on 5,213 phenopackets; per-model values in text and figures only; ranks diseases, not genes |
| Kim et al. 2024, AJHG | Not extracted; lead | LLM gene prioritisation; values in supplementary tables; Phen2Gene developers among the authors |
| PhEval, BMC Bioinformatics 2025 | Not extracted; lead | Developer benchmark framework (Monarch, Exomiser group) |
| Talos study (Nat Med 2026) | Not reused | Already behind the existing judgements |

## Modelling choices

- One protocol per source and cohort (4 direct, 3 proxy). In Yuan 2024 the protocol letter and trio mode are on the configuration and in `comparison.inputs`; singleton and trio rows share a protocol but must be compared within mode, as recorded in the limitations.
- Top-30 and top-40 columns needed two new metric concepts (`top-30-accuracy`, `top-40-accuracy`), modelled on `top-50-accuracy`.
- The DDD dataset record is shared by both Yuan papers (same 305 probands; 2024 adds parents).
- Relevance: the Yuan protocols are `direct` because they measure case-level top-k recovery on solved real exomes, which the brief names as the endpoint. The existing Talos and Exomiser judgements are `proxy`; a reviewer should check that this difference is justified. Kafkas is `proxy` (synthetic candidate sets).

## Things a reviewer should judge

1. Yuan 2024 Exomiser and PhenIX Protocols C and D are defined in a Figure 2 table (image). The text states that B uses REVEL and MVP and that C and D use trio mode, but not which pathogenicity source C and D use.
2. Exomiser values differ between the two Yuan papers on the same DDD cases (top-1 15.1% with 12.1.0 default versus 31.8% with 13.1.0 Protocol A), as do the LIRICAL versions (1.3.0 versus 1.3.4). These are different runs, not a conflict.
3. Kafkas Table 3 does not say which zero-shot prompt was used.
4. Both Yuan in-house cohorts come from the authors' laboratory and are not public.

## Coverage

Bounded pass. Not systematic. Not covered: 100kGP, UDN or CAGI multi-tool comparisons with printed tables, candidates-per-case workload, LLMs on real exome candidate lists, and the leads listed above.
