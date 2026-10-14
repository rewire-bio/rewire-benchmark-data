"""Search-ledger and scope-audit entries for the 2026-10-14 VEP use-case pass.

Writes ledger.jsonl and scope-audit.jsonl in the batch folder; the same lines are appended
to data/omics/search-ledger.jsonl and data/omics/scope-audit.jsonl.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tools import GAPS, TOOLS  # noqa: E402

BATCH = os.path.dirname(HERE)
P = "vep-uc-20261014"
CUTOFF = "2026-10-14"
COVERAGE = ("VEP use-case pass for rewire-benchmark-data #151 and #152 and the remaining #153-#155 predictors, 21 of an 80-query budget "
            "used on 2026-10-14. Bounded pass, not systematic exhaustion of calibration studies or of predictor literature.")
REVIEWER = "Claude (Opus 5.5) research agent scope review for the 2026-10-14 VEP use-case pass; not a scientific validation"
T = {t["name"]: t for t in TOOLS}
tid = lambda t: f"{P}-{t['kind']}-{t['slug']}"
sid = lambda t: f"{P}-source-{t['slug']}"


def entry(n, lane, query, channels, at, status, decision, included=(), reviewed=(), gaps=(), excluded=(), failed=()):
    e = {"channels": channels, "coverage_claim": COVERAGE, "cutoff_date": CUTOFF, "decision": decision, "gaps": list(gaps),
         "id": f"search-{P}-q{n:02d}", "included_record_ids": list(included), "lane": lane, "query": query,
         "reviewed_source_ids": list(reviewed), "searched_at": at, "status": status}
    if excluded:
        e["excluded"] = list(excluded)
    if failed:
        e["failed_candidates"] = list(failed)
    return e


def main():
    L = []
    L.append(entry(1, "genomics", '(TITLE_ABS:"PP3" OR TITLE_ABS:"BP4") AND (TITLE_ABS:"calibration" OR TITLE_ABS:"calibrated" OR TITLE_ABS:"calibrating") AND PUB_YEAR:[2022 TO 2026]',
        ["europe_pmc_rest"], "2026-10-14T14:44:25Z", "included",
        "17 hits. Pejaver et al. 2022 (AJHG, PMC9748256) and Bergquist et al. 2025 (Genet Med, PMC12208618) extracted: Table 2 and Table 3 of Pejaver, Table 1 of Bergquist. Stenton et al. 2024 (evidence yield, PMC11560577) captured and cited, not extracted. Leads not extracted: 2026 Genet Med calibration of machine-learning algorithms (doi:10.1016/j.gim.2026.102606), BayesQuantify (J Med Genet 2025, doi:10.1136/jmg-2025-110863), INDELVAR preprint (in-frame indels), Dubé et al. 2026 reclassification (Genet Med Open, PMC13125162, captured and screened), 5' cis-regulatory calibration (AJHG 2024, PMC11267523; bears on regulatory follow-up, not missense).",
        included=[f"{P}-protocol-pejaver2022-intervals", f"{P}-protocol-pejaver2022-developer-threshold-lr", f"{P}-protocol-pejaver2022-developer-threshold-gnomad-fraction", f"{P}-protocol-bergquist2025-point-intervals", "use-case-missense-pp3-bp4-calibrated-evidence"],
        reviewed=[f"{P}-source-pejaver2022", f"{P}-source-bergquist2025", f"{P}-source-stenton2024"],
        gaps=["Genet Med 2026 calibration of machine-learning algorithms (doi:10.1016/j.gim.2026.102606): closed access; doi.org resolved to an Elsevier linking page and an open-access lookup found no copy (14:49:27Z). Not retrieved.",
              "Pejaver et al. 2022 Table S1 and Data S1-S3 (supplement) not retrieved.",
              "BayesQuantify (J Med Genet 2025) and the regional 5' cis-regulatory calibration (AJHG 2024) not retrieved or extracted."]))
    L.append(entry(2, "genomics", '(TITLE_ABS:"AlphaMissense" OR TITLE_ABS:"REVEL" OR TITLE_ABS:"BayesDel" OR TITLE_ABS:"MutPred2" OR TITLE_ABS:"VEST4" OR TITLE_ABS:"CADD") AND (TITLE_ABS:"evidence strength" OR TITLE_ABS:"likelihood ratio" OR TITLE_ABS:"ClinGen") AND (TITLE_ABS:"threshold" OR TITLE_ABS:"thresholds" OR TITLE_ABS:"calibration") AND PUB_YEAR:[2023 TO 2026]',
        ["europe_pmc_rest"], "2026-10-14T14:44:35Z", "screened",
        "21 hits. Tejura et al. 2024 (AJHG, PMC11393694, gene-level heterogeneity of REVEL and BayesDel calibration) captured and cited for limitations, not extracted. P-KNN joint calibration preprint (bioRxiv 2025), REVEL in ALS genes (Hum Mutat 2023), REVEL loss- versus gain-of-function (Hum Mutat 2023), cancer-gene panel study (Hum Mutat 2026) and PHOX2B gene-specific study noted as leads.",
        reviewed=[f"{P}-source-tejura2024"],
        gaps=["Gene-specific calibrations (Tejura et al. 2024 tables, REVEL in ALS genes, cancer-gene panel) not extracted; the use case records the gap."]))
    t153 = [t for t in TOOLS if t["issue"] == 153]
    L.append(entry(3, "source-resolution", 'TITLE:"PaPI" OR TITLE:"SAAP pipeline" OR TITLE:"VariPred" OR TITLE:"ENTPRISE" OR TITLE:"LYRUS" OR TITLE:"DeepRank-Mut" OR TITLE:"VAMPP" OR TITLE:"AFFIPred" OR TITLE:"Meta-EA" OR TITLE:"genoseer" OR TITLE:"PON-P3" OR TITLE:"Rhapsody-2" OR TITLE:"DS-MVP" OR TITLE:"MAGPIE" OR TITLE:"TransEFVP" OR TITLE:"EvoRator2" OR TITLE:"Predicting Severity of Disease-Causing Variants" OR TITLE:"Insights into disease-associated mutations in the human proteome through protein structural analysis" OR TITLE:"Robust classification of protein variation using structural modelling" OR TITLE:"machine learning approach based on ACMG/AMP guidelines for genomic variant classification" OR TITLE:"Missense variants pathogenicity annotation from homologous proteins" OR TITLE:"interpretable molecular framework for predicting cancer driver missense mutations" OR TITLE:"predicting the functional impact of single nucleotide missense variants"',
        ["europe_pmc_rest"], "2026-10-14T14:47:32Z", "included",
        "330 hits, most unrelated (MAGPIE, PAPi). Primary papers located for the #153 predictors without records after PR #160; full text retrieved from Europe PMC or PMC for each that has a PMC copy (see retrieval-log.md).",
        included=[tid(t) for t in t153], reviewed=[sid(t) for t in t153],
        gaps=["PON-PS (Hum Mutat 2017), TransEFVP (J Chem Inf Model 2024) and EvoRator2 (J Mol Biol 2023) have no PMC copy; not retrieved (see coverage.json).", "VAMPP is a bioRxiv preprint only; the JATS route was rate limited."]))
    rest = [t for t in TOOLS if t["issue"] in (154, 155)]
    L.append(entry(4, "source-resolution", 'DOI:"10.1186/s12859-015-0554-8" OR TITLE:"pseudo amino acid composition to score human protein-coding variants" OR TITLE:"SAAP pipeline and database" OR TITLE:"ENTPRISE" OR TITLE:"structure-guided variant effect predictions" OR TITLE:"protein structure graph embeddings to predict the pathogenicity" OR TITLE:"VAMPP" OR TITLE:"Born-Again Networks" OR TITLE:"formal perturbation equation between genotype and phenotype" OR TITLE:"UMD-Predictor" OR TITLE:"joint embedding of protein sequence and structure enables robust variant effect" OR TITLE:"ESGMM" OR TITLE:"Estimation of allele-specific fitness effects across human protein-coding sequences" OR TITLE:"landscape of tolerated genetic variation in humans and primates" OR TITLE:"Predicting genome-wide functional constraints with GPN-Star" OR TITLE:"Predicting expression-altering promoter mutations with deep learning" OR TITLE:"LOL-EVE" OR TITLE:"Predicting functional UTR variants" OR TITLE:"Classification of non-coding variants with high pathogenic impact" OR TITLE:"Using secondary structure to predict the effects of genetic variants on alternative splicing" OR TITLE:"De novo pattern discovery enables robust assessment of functional consequences of non-coding variants" OR TITLE:"Deep learning sequence-based ab initio prediction of variant effects on expression and disease risk" OR TITLE:"ShapeGTB" OR TITLE:"Predicting the impact of non-coding variants on DNA methylation" OR TITLE:"Functional annotation of noncoding sequence variants"',
        ["europe_pmc_rest"], "2026-10-14T14:47:44Z", "included",
        "40 hits. Primary papers located for the #154 and #155 predictors and several #153 ones; GPN-Star (Nature 2026) and PromoterAI (Science 2025) have no PMC copy; LOL-EVE not indexed by title.",
        included=[tid(t) for t in rest], reviewed=[sid(t) for t in rest],
        gaps=["PromoterAI Science paper not open access; the official repository README pinned to a commit is the captured source.", "LOL-EVE paper not found in Europe PMC; the official repository README is the captured source."]))
    L.append(entry(5, "source-resolution", "Open-access lookup for doi:10.1016/j.gim.2026.102606 (api.unpaywall.org/v2)", ["unpaywall_api"], "2026-10-14T14:49:27Z", "failed",
        "is_oa false, oa_status closed, no repository copy. Recorded as a gap for the #151 use case.",
        gaps=["Closed-access calibration paper not retrieved."]))
    gh = [("PromoterAI", "Illumina/PromoterAI pinned at ce9fcd0; README captured"), ("LOL-EVE", "debbiemarkslab/LOL-EVE pinned at deed3bd; README captured"),
          ("VAMPP", "No relevant repository (VampPrior projects only)"), ("TransEFVP", "yzh9607/TransEFVP: only an 11-byte README at 36f5e8c; authorship not shown; not used"),
          ("EvoRator2", "No repository found"), ("ESGMM", "No repository found"), ("GPN-Star", "songlab-cal/gpn is the code repository named in the paper; the Nature PDF is the captured source")]
    for i, (q, d) in enumerate(gh):
        L.append(entry(6 + i, "source-resolution", q, ["github_search_api"], "2026-10-14T14:49:41Z", "screened" if "captured" in d else "failed", d,
                       included=[tid(T[q])] if q in T and "captured" in d and q != "GPN-Star" else [], reviewed=[sid(T[q])] if q in ("PromoterAI", "LOL-EVE") else []))
    dois = [("10.1101/2024.07.11.602867", "VAMPP: preprint PPR880985, no full text in Europe PMC; bioRxiv API gives metadata only, JATS XML route rate limited (HTTP 429)", "failed"),
            ("10.21203/rs.3.rs-4380588/v1", "ESGMM: Research Square preprint, CC BY; full text page captured", "screened"),
            ("10.1016/j.jmb.2023.168155", "EvoRator2: no PMC copy; Elsevier linking page only", "failed"),
            ("10.1002/humu.23173", "PON-PS: no PMC copy; Wiley HTTP 403", "failed"),
            ("10.1021/acs.jcim.3c02019", "TransEFVP: no PMC copy; ACS HTTP 403", "failed"),
            ("10.1038/s41586-026-11005-5", "GPN-Star: no PMC copy; Nature page open access (CC BY), PDF captured", "screened"),
            ("10.1126/science.ads7373", "PromoterAI: no PMC copy; Science paywall; repository README used", "screened")]
    for i, (d, dec, st) in enumerate(dois):
        L.append(entry(13 + i, "source-resolution", f'DOI:"{d}"', ["europe_pmc_rest"], "2026-10-14T14:49:56Z", st, dec,
                       reviewed=[sid(T["ESGMM"])] if "ESGMM" in dec else [sid(T["GPN-Star"])] if "GPN-Star" in dec else []))
    L.append(entry(20, "source-resolution", "Crossref bibliographic query: Variant pathogenicity prediction based on the ESGMM algorithm", ["crossref_api"], "2026-10-14T14:50:08Z", "screened",
        "Published version Discover Computing, doi:10.1007/s10791-024-09487-w (CC BY-NC-ND); its Springer page and PDF returned a bot challenge, so the CC BY preprint is the captured source.",
        gaps=["ESGMM published version not retrieved."]))
    L.append(entry(21, "source-resolution", 'TITLE:"DAMpred" OR (TITLE:"VAMPP-Score") OR (TITLE:"EvoRator")', ["europe_pmc_rest"], "2026-10-14T14:52:02Z", "included",
        "3 hits. DAMpred is described in Quan et al. 2019 (J Mol Biol, PMC6589125), not in the Gao et al. 2015 Structure paper the AVE list cites; Quan et al. captured. The VAMPP preprint and EvoRator (2022, the predecessor of EvoRator2) noted.",
        included=[tid(T["DAMpred"])], reviewed=[sid(T["DAMpred"])], excluded=[{"paper_id": "doi:10.1016/j.str.2015.03.028", "reason": "Structural analysis of disease-associated mutations; does not describe DAMpred"}]))
    with open(os.path.join(BATCH, "ledger.jsonl"), "w") as f:
        for e in L:
            f.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n")

    S = []
    def scope(pid, decision, reason):
        S.append({"paper_id": pid, "decision": decision, "reason": reason, "reviewed_at": "2026-10-14T16:30:00Z", "reviewer": REVIEWER})
    scope("doi:10.1016/j.ajhg.2022.10.013", "included", "Pejaver et al. 2022 (AJHG, CC BY 4.0): ClinGen SVI calibration of 13 missense predictors to PP3/BP4 strengths. Tables 2 and 3 extracted (vep-use-cases-20261014).")
    scope("doi:10.1016/j.gim.2025.101402", "included", "Bergquist et al. 2025 (Genet Med, PMC author manuscript): calibration of AlphaMissense, ESM1b and VARITY_R and points-scale intervals for four earlier tools. Table 1 extracted (vep-use-cases-20261014).")
    scope("doi:10.1016/j.gim.2024.101213", "included", "Stenton et al. 2024 (Genet Med): guidance and evidence yield for the calibrated PP3/BP4 thresholds. Cited for limitations; Table 2 not extracted.")
    scope("doi:10.1016/j.ajhg.2024.07.018", "included", "Tejura et al. 2024 (AJHG): gene-level heterogeneity of REVEL and BayesDel calibration. Cited for limitations; not extracted.")
    scope("doi:10.1016/j.str.2015.03.028", "excluded", "Gao, Zhou and Skolnick 2015 (Structure), cited by the AVE list for DAMpred: a structural analysis that does not describe DAMpred. DAMpred's primary paper is Quan et al. 2019 (J Mol Biol).")
    for t in TOOLS:
        scope(f"doi:{t['doi']}" if t.get("doi") else t["url"], "included",
              f"Primary source for {t['name']} (rewire-benchmark-data #{t['issue']}): {t['kind']} record with status discovered (vep-use-cases-20261014). No results extracted.")
    with open(os.path.join(BATCH, "scope-audit.jsonl"), "w") as f:
        for e in S:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    print(len(L), len(S))


if __name__ == "__main__":
    main()
