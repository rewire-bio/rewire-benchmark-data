"""Write coverage.json for the batch from batch.jsonl, tools.py and the first pass's coverage.json."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tools import GAPS, TOOLS  # noqa: E402

BATCH = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(BATCH, "..", "..", ".."))
P = "vep-uc-20261014"

# One availability probe per stated access URL, 2026-10-14 14:56:33Z to 14:58:28Z (curl -L, 20 s timeout).
# 000 means no HTTP response. A single probe is not evidence that a tool is withdrawn.
PROBE = {"papi": "000", "saappred": "200", "varipred": "200", "dampred": "000", "mlvar": "200", "entprise": "000", "vipur": "200", "lyrus": "200",
         "deeprank-mut": "200", "affipred": "502", "metaea": "200", "dva": "200", "genoseer": "200", "pon-p3": "000", "rhapsody-2": "200", "ds-mvp": "200",
         "homolvar": "200", "magpie": "200", "mutapheno": "200", "mtban": "000", "ea": "500", "umd-predictor": "000 (probed with an ASCII hyphen; the paper prints a non-ASCII hyphen)",
         "ssemb": "200", "primateai-3d": "200 (github.com/Illumina/PrimateAI-3D; the paper prints 'lllumina')", "funuv": "200", "finsurf": "000", "pepsi": "200", "dvar": "200",
         "expecto": "200", "shapegtb": "200", "cpgenie": "000", "gwava": "200", "gpn-star": "200", "esgmm": "no URL stated", "promoterai": "200", "lol-eve": "200"}
YEAR = {"papi": 2015, "saappred": 2013, "varipred": 2024, "dampred": 2019, "mlvar": 2022, "entprise": 2016, "vipur": 2016, "lyrus": 2022, "deeprank-mut": 2023,
        "affipred": 2025, "metaea": 2025, "dva": 2024, "genoseer": 2025, "pon-p3": 2025, "rhapsody-2": 2025, "ds-mvp": 2025, "homolvar": 2025, "magpie": 2024,
        "mutapheno": 2026, "mtban": 2021, "ea": 2014, "umd-predictor": 2016, "ssemb": 2024, "esgmm": 2024, "primateai-3d": 2023, "gpn-star": 2026,
        "promoterai": 2025, "lol-eve": 2025, "funuv": 2024, "finsurf": 2022, "pepsi": 2019, "dvar": 2019, "expecto": 2018, "shapegtb": 2018, "cpgenie": 2017, "gwava": 2014}


def main():
    recs = [json.loads(l) for l in open(os.path.join(BATCH, "batch.jsonl"))]
    counts = {}
    for r in recs:
        counts[r["kind"]] = counts.get(r["kind"], 0) + 1
    first = json.load(open(os.path.join(REPO, "data", "omics", "vep-literature-20261014", "coverage.json")))
    mine = {t["name"]: t for t in TOOLS}
    gaps = {g["name"]: g for g in GAPS}
    alias = {"MetaEA": "Meta-EA", "EA": "Evolutionary Action (EA)"}
    issue_cov = {}
    for issue, v in first["issue_predictor_coverage"].items():
        rows = []
        for p in v["predictors"]:
            name = alias.get(p["predictor"], p["predictor"])
            row = {"predictor": p["predictor"]}
            if p.get("method_id"):
                row.update(status="record and results from PR #160", record_id=p["method_id"], protocols_with_results=p["protocols_with_results"])
            elif name in mine:
                t = mine[name]
                row.update(status="discovered record added", record_id=f"{P}-{t['kind']}-{t['slug']}", source_id=f"{P}-source-{t['slug']}",
                           publication_year=YEAR[t["slug"]], access_probe=PROBE[t["slug"]])
                if t["slug"] == "ea":
                    row.update(status="discovered record added, with results", protocols_with_results=[f"{P}-protocol-pejaver2022-intervals"])
                if t.get("note"):
                    row["note"] = t["note"]
            elif p["predictor"] in gaps:
                g = gaps[p["predictor"]]
                row.update(status="gap: primary source not retrieved; no record", reference=g["reference"], reason=g["reason"])
            else:
                raise SystemExit(f"unaccounted predictor {p['predictor']}")
            rows.append(row)
        issue_cov[issue] = {"total": v["total"], "with_records": sum(1 for r in rows if "record_id" in r),
                            "with_results": sum(1 for r in rows if r.get("protocols_with_results")), "predictors": rows}
    judgements = [{"claim_id": r["id"], "use_case": r["links"][0]["target_id"], "protocol": r["attributes"]["value"], "relevance": r["attributes"]["relevance"]}
                  for r in recs if r["kind"] == "claim" and r["attributes"]["field"].startswith("links:assessed_by:")]
    out = {
        "schema_version": "1.0", "batch": "vep-use-cases-20261014",
        "issues": [f"https://github.com/rewire-bio/rewire-benchmark-data/issues/{n}" for n in (151, 152, 153, 154, 155)],
        "cutoff_date": "2026-10-14", "query_budget": 80, "queries_used": 21,
        "status": "extraction awaiting independent review; not in the store",
        "record_counts": dict(sorted(counts.items())),
        "use_cases_added": ["use-case-missense-pp3-bp4-calibrated-evidence", "use-case-protein-variant-effect-prediction"],
        "existing_ids_reused": {
            "methods_and_models": sorted({l["target_id"] for r in recs if r["kind"] == "configuration" for l in r["links"] if not l["target_id"].startswith(P)}),
            "protocols_judged": sorted({j["protocol"] for j in judgements if not j["protocol"].startswith(P)}),
            "sources_cited": sorted({s for r in recs if r["kind"] in ("claim", "use_case") for s in r["source_ids"] if not s.startswith(P)}),
        },
        "new_metric_concepts": ["evidence-strength-score-interval (data/vocab/metric.ttl)"],
        "relevance_judgements": judgements,
        "baseline_claims": [r["id"] for r in recs if r["kind"] == "claim" and r["attributes"]["field"] == "baseline"],
        "evidence_checked_plan": "evidence-checked.json (to apply with records -- change after review)",
        "issue_predictor_coverage": issue_cov,
        "table_coverage": [
            {"source": "Pejaver et al. 2022", "locator": "Table 2", "status": "complete", "this_batch": "13 tools x 8 strengths (104 results; '–' cells kept as not reached)"},
            {"source": "Pejaver et al. 2022", "locator": "Table 3", "status": "complete for values", "this_batch": "lr+ with 95% CI and gnomAD fraction for 3 tools (6 results); the threshold column is in each evaluation's adaptation and the 'not met' column in each lr+ result's criterion"},
            {"source": "Pejaver et al. 2022", "locator": "Tables 1 and 4", "status": "not extracted as results", "note": "Table 1 (likelihood-ratio cut-offs) is in the protocol's metric implementation; Table 4 is guidance"},
            {"source": "Pejaver et al. 2022", "locator": "Table S1, Data S1-S3", "status": "not retrieved"},
            {"source": "Bergquist et al. 2025", "locator": "Table 1", "status": "complete", "this_batch": "7 tools x 9 point levels (63 results)"},
            {"source": "Stenton et al. 2024", "locator": "Table 2", "status": "not extracted", "note": "Evidence yield per proband; cited only"},
            {"source": "Tejura et al. 2024", "locator": "Tables", "status": "not extracted", "note": "Cited for its summary finding only"},
        ],
        "gaps": [
            "Pejaver et al. 2022 Table S1 (point estimates and one-sided confidence bounds) and Data S1-S3 not retrieved.",
            "Genet Med 2026 calibration of machine-learning algorithms (doi:10.1016/j.gim.2026.102606) is closed access; not retrieved.",
            "BayesQuantify (J Med Genet 2025), P-KNN (bioRxiv 2025), INDELVAR (bioRxiv 2026), Dubé et al. 2026 and the regional 5' cis-regulatory calibration (AJHG 2024) not extracted.",
            "Tejura et al. 2024 gene-level tables and Stenton et al. 2024 Table 2 not extracted.",
            "Four #153 predictors have no record: PON-PS, EvoRator2, TransEFVP and VAMPP (reasons under issue_predictor_coverage).",
            "No benchmark result was extracted for any of the 36 newly recorded predictors except EA (Pejaver et al. 2022). Their developer papers print benchmark tables that were not extracted.",
            "PromoterAI and LOL-EVE records rest on repository READMEs; their papers were not retrieved (Science paywall; LOL-EVE paper not found).",
            "ESGMM record rests on the CC BY preprint; the published Discover Computing version was not retrieved.",
            "ProteinGym supervised DMS summaries and other zero-shot DMS metrics at 144fe22 remain unextracted (use case #152 gap).",
        ],
        "issue_153_comment": "timini commented on #153: 'please do not add anything too old or outdated or bad'. All retrievable tools were recorded as discovered; publication_year and access_probe are given per tool so the reviewer can exclude old or unavailable ones.",
    }
    json.dump(out, open(os.path.join(BATCH, "coverage.json"), "w"), indent=1, ensure_ascii=False)
    open(os.path.join(BATCH, "coverage.json"), "a").write("\n")
    print({k: (v["with_records"], v["with_results"], v["total"]) for k, v in issue_cov.items()})


if __name__ == "__main__":
    main()
