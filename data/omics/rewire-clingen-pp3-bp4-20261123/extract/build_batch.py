#!/usr/bin/env python3
"""Build the Rewire-run batch for ClinGen PP3/BP4 missense calibration from a pinned checkout.

  python3 build_batch.py <checkout of rewire-bio/rewire-benchmarks> <batch folder>
  add --check to rebuild in memory and compare byte for byte with batch.jsonl

Every stored numeric result is the literal JSON number token at its pointer in
benchmarks/clingen-pp3-bp4/results/calibration_summary.json at the pinned commit.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

DAY = "2026-11-23"
NOW = "2026-11-23T16:15:00Z"
PIN_REPO = "rewire-bio/rewire-benchmarks"
PIN_COMMIT = "fbf4fd5df880ee685fa276dfa6a5bb46da4bcf73"
BENCH_DIR = "benchmarks/clingen-pp3-bp4"
PREFIX = "rewire-local-20261123-clingen"
USE_CASE_ID = "use-case-missense-pp3-bp4-calibrated-evidence"

REVIEWER_NOTE = (
    "Deterministic script verification (build_batch.py re-reads every JSON pointer from the "
    "pinned checkout and verifies raw GitHub SHA-256 digests). No human scientific review."
)

# Canonical model/method/pipeline targets in data/entities/
PREDICTOR_SPECS = [
    (
        "gpn_msa",
        "GPN-MSA (-LLR)",
        "GPN-MSA hg38 precomputed negated log-likelihood ratio lookup for GRCh38 missense SNVs.",
        "gfm-guides-20261014-gpnmsa-model-gpn-msa",
        ["foundation_model"],
        None,
        "GPN-MSA hg38 precomputed tabix scores negated so higher values indicate pathogenicity.",
    ),
    (
        "gpnstar_v",
        "GPN-Star vertebrate v100 (-LLR)",
        "GPN-Star 200M vertebrate multiple-sequence alignment negated calibrated log-likelihood ratio lookup.",
        "vep-uc-20261014-model-gpn-star",
        ["foundation_model"],
        "v100",
        "GPN-Star vertebrate v100 200M precomputed scores negated so higher values indicate pathogenicity.",
    ),
    (
        "gpnstar_m",
        "GPN-Star mammal m447 (-LLR)",
        "GPN-Star 200M mammal multiple-sequence alignment negated calibrated log-likelihood ratio lookup.",
        "vep-uc-20261014-model-gpn-star",
        ["foundation_model"],
        "m447",
        "GPN-Star mammal m447 200M precomputed scores negated so higher values indicate pathogenicity.",
    ),
    (
        "avi",
        "AlphaGenome AVI (raw)",
        "AlphaGenome Variant Impact raw multimodal score across GRCh38 missense SNVs.",
        "ag-atlas-20261019-pipeline-avi",
        ["foundation_model"],
        None,
        "Precomputed raw AlphaGenome Variant Impact (AVI) SNV score table.",
    ),
    (
        "avi_phred",
        "AlphaGenome AVI (PHRED)",
        "AlphaGenome Variant Impact PHRED-scaled score across GRCh38 missense SNVs.",
        "ag-atlas-20261019-pipeline-avi",
        ["foundation_model"],
        None,
        "Precomputed PHRED-scaled AlphaGenome Variant Impact (AVI) SNV score table.",
    ),
    (
        "alphamissense",
        "AlphaMissense lookup",
        "AlphaMissense pathogenicity score taken as the maximum across overlapping transcripts for a missense SNV.",
        "somatic-oncogenicity-20261009-method-alphamissense",
        ["supervised_machine_learning"],
        None,
        "AlphaMissense hg38 precomputed score table aggregated by maximum over transcripts.",
    ),
    (
        "revel",
        "REVEL v1.3 lookup",
        "REVEL v1.3 ensemble missense pathogenicity score taken as the maximum across transcripts.",
        "somatic-oncogenicity-20261009-method-revel",
        ["supervised_machine_learning"],
        "1.3",
        "REVEL v1.3 precomputed transcript score table aggregated by maximum over transcripts.",
    ),
    (
        "cadd_phred",
        "CADD v1.7 (PHRED)",
        "CADD v1.7 GRCh38 PHRED-scaled deleteriousness score for missense SNVs.",
        "somatic-oncogenicity-20261009-method-cadd",
        ["supervised_machine_learning"],
        "1.7",
        "CADD v1.7 GRCh38 whole_genome_SNVs.tsv.gz PHRED lookup.",
    ),
    (
        "evee",
        "EVEE (ClinVar-supervised control)",
        "EVEE Evo-2-feature pathogenicity classifier trained with ClinVar labels and evaluated as a leaked control.",
        "gfm-guide-20261014-method-evee",
        ["supervised_machine_learning"],
        None,
        "EVEE precomputed table (Zenodo 19701997) with ClinVar label supervision through 2026-03-20.",
    ),
]

STRATA_SPECS = [
    (
        "post_2023_12",
        "post-2023-12",
        "ClinVar >=2-star missense SNVs held out from Dec 2023 (9,450 variants)",
        "Post-Dec-2023 (9,450 SNVs: 5,508 P/LP, 3,942 B/LB)",
        1,
        "9,450 ClinVar 2026-11-08 >=2-star clean missense SNVs (5,508 P/LP, 3,942 B/LB; 4,188 novel) not classified P/LP or B/LB in clinvar_20231226.vcf.gz, calibrated with 6,312 gnomAD missense reference SNVs.",
        "Excluded variants with any prior P/LP or B/LB assertion in clinvar_20231226.vcf.gz; unfiltered for allele frequency; calibrated against 6,312 population missense SNVs (gft = 0.03).",
        "No AF cap applied; includes common benign variants removed in the post_2023_12_af001 stratum.",
    ),
    (
        "post_2023_12_af001",
        "post-2023-12-af001",
        "AF-controlled ClinVar >=2-star missense SNVs held out from Dec 2023 (gnomAD grpmax < 0.1%, 8,141 variants)",
        "Post-Dec-2023 gnomAD grpmax < 0.1% (8,141 SNVs: 5,454 P/LP, 2,687 B/LB)",
        2,
        "8,141 ClinVar 2026-11-08 >=2-star clean missense SNVs held out from 2023-12-26 restricted to gnomAD v3.1.2 non-1000G genome grpmax < 0.1% (5,454 P/LP, 2,687 B/LB).",
        "Temporal holdout from clinvar_20231226.vcf.gz filtered to gnomAD v3.1.2 genome grpmax < 0.001 following rewire-benchmarks #53 and #54, calibrated against 6,312 population missense SNVs (gft = 0.03).",
        "Controls common-benign AF inflation; AlphaGenome AVI loses PP3 Strong (+4) and AlphaMissense loses BP4 tiers under this filter.",
    ),
    (
        "post_2025_03",
        "post-2025-03",
        "Sensitivity ClinVar >=2-star missense SNVs held out from Mar 2025 (3,818 variants)",
        "Post-Mar-2025 sensitivity (3,818 SNVs: 2,306 P/LP, 1,512 B/LB)",
        3,
        "3,818 ClinVar 2026-11-08 >=2-star clean missense SNVs (2,306 P/LP, 1,512 B/LB; 1,134 novel) not classified P/LP or B/LB in clinvar_20250330.vcf.gz.",
        "Shorter-window temporal holdout from clinvar_20250330.vcf.gz preserving release dates after pre-2025 predictors were frozen, calibrated with 6,312 population missense SNVs (gft = 0.03).",
        "Smaller B/LB count (1,512) widens bootstrap bounds; only REVEL and leaked EVEE reach PP3 Strong (+4).",
    ),
]

PP3_TIERS = [
    ("VeryStrong_8", "Very Strong (+8)", "+8", 8),
    ("Strong_4", "Strong (+4)", "+4", 4),
    ("Intermediate_3", "Intermediate (+3)", "+3", 3),
    ("Moderate_2", "Moderate (+2)", "+2", 2),
    ("Supporting_1", "Supporting (+1)", "+1", 1),
]
BP4_TIERS = [
    ("Supporting_1", "Supporting (-1)", "-1", -1),
    ("Moderate_2", "Moderate (-2)", "-2", -2),
    ("Intermediate_3", "Intermediate (-3)", "-3", -3),
    ("Strong_4", "Strong (-4)", "-4", -4),
    ("VeryStrong_8", "Very Strong (-8)", "-8", -8),
]


def load(root: Path, rel: str):
    return json.loads((root / rel).read_text(), parse_float=str, parse_int=str)


def pointer(doc, ptr: str):
    for part in ptr.split("/")[1:]:
        doc = doc[int(part)] if isinstance(doc, list) else doc[part]
    return doc


def slug(text: str) -> str:
    return text.replace("_", "-")


class Batch:
    def __init__(self, root: Path):
        self.root = root
        head = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        assert head == PIN_COMMIT, f"checkout is at {head}, expected {PIN_COMMIT}"
        self.records, self.checks, self.sources, self.ids = [], [], {}, set()

    def add(self, id: str, kind: str, name: str, description: str, status: str, facets, source_ids, links, attributes):
        assert id not in self.ids, id
        self.ids.add(id)
        self.records.append({
            "id": id,
            "kind": kind,
            "name": name,
            "description": description,
            "status": status,
            "facets": facets,
            "source_ids": source_ids,
            "links": [{"relation": r, "target_id": t} for r, t in links],
            "attributes": attributes,
        })
        return id

    def source(self, id: str, rel: str, name: str, description: str, source_type: str, extra=None):
        data = (self.root / rel).read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        attrs = {
            "url": f"https://github.com/{PIN_REPO}/blob/{PIN_COMMIT}/{rel}",
            "artifact_url": f"https://raw.githubusercontent.com/{PIN_REPO}/{PIN_COMMIT}/{rel}",
            "artifact_sha256": sha,
            "hash_scope": "complete bytes of the file at the pinned commit",
            "version": PIN_COMMIT,
            "retrieved_at": NOW,
            "source_type": source_type,
            "evidence_origin": "rewire_run",
            "publication_status": "official_project_source",
            "licence": "MIT",
        }
        attrs.update(extra or {})
        self.sources[id] = (rel, sha)
        return self.add(id, "source", name, description, "source_checked", {"areas": ["dna-genomes"]}, [], [], attrs)

    def review(self, source_id: str, note: str, methods=None):
        rel, sha = self.sources[source_id]
        return {
            "method": methods or ["execution-evidence-review", "source-hash-verification"],
            "reviewer": ["rewire-deterministic-table-checker"],
            "date": DAY,
            "artifact_sha256": sha,
            "retrieval_url": f"https://raw.githubusercontent.com/{PIN_REPO}/{PIN_COMMIT}/{rel}",
            "method_note": (
                "Value read by build_batch.py as the literal JSON number token at the pointer in "
                "the pinned file, then re-read from the same bytes and verified against SHA-256."
            ),
            "reviewer_note": REVIEWER_NOTE,
            "note": note,
        }

    def result(self, id: str, name: str, source_ids, evaluation: str, value_source: str, ptr: str,
               metric: str, direction: str, unit: str, note: str, ci=None, ci_scope=None, extra=None):
        rel, _ = self.sources[value_source]
        doc = load(self.root, rel)
        value = pointer(doc, ptr)
        assert isinstance(value, str), (rel, ptr, value)
        attrs = {
            "printed_value": value,
            "numeric_value": value,
            "metric": metric,
            "metric_direction": direction,
            "unit": unit,
        }
        attrs.update(extra or {})
        self.checks.append((id, rel, ptr, "printed_value"))
        if ci:
            bounds = pointer(doc, ci)
            if isinstance(bounds, list) and len(bounds) == 2 and all(isinstance(x, str) for x in bounds):
                attrs["uncertainty"] = {
                    "type": "confidence_interval",
                    "lower": bounds[0],
                    "upper": bounds[1],
                    "level": 0.95,
                    "method": "bootstrap",
                    "resamples": 1000,
                    "scope": ci_scope or "1,000 stratified bootstrap resamples (seed 20261123)",
                    "source_column": f"JSON pointer {ci}",
                }
                self.checks.append((id, rel, ci, "ci"))
            else:
                attrs["missing_metadata"] = {
                    "uncertainty": {
                        "reason": "unreported",
                        "note": "More than 5% of 1,000 stratified bootstrap resamples failed to reach this tier.",
                    }
                }
        else:
            attrs["missing_metadata"] = {
                "uncertainty": {
                    "reason": "unreported",
                    "note": "Point proportion computed across all held-out variants in the stratum.",
                }
            }
        attrs["source_locator"] = f"{rel}, JSON pointer {ptr}"
        attrs["review"] = self.review(value_source, note)
        return self.add(id, "result", name, "", "source_checked", {"areas": ["dna-genomes"]}, source_ids,
                        [("evaluation", evaluation)], attrs)

    def verify(self):
        by_id = {r["id"]: r for r in self.records}
        for id, rel, ptr, what in self.checks:
            token = pointer(load(self.root, rel), ptr)
            a = by_id[id]["attributes"]
            if what == "printed_value":
                assert a["printed_value"] == token == a["numeric_value"], (id, ptr)
                assert token in (self.root / rel).read_text(), (id, token)
            else:
                assert [a["uncertainty"]["lower"], a["uncertainty"]["upper"]] == token, (id, ptr)
        cited = set()
        for r in self.records:
            for s in r["source_ids"]:
                assert s in self.sources, (r["id"], s)
                cited.add(s)
        assert cited == set(self.sources), set(self.sources) - cited

    def lines(self):
        return "".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in self.records)


def build(root: Path) -> Batch:
    b = Batch(root)
    areas = {"areas": ["dna-genomes"], "contexts": ["clinical_research"]}

    S_README = b.source(
        f"{PREFIX}-source-readme", f"{BENCH_DIR}/README.md",
        "clingen-pp3-bp4 benchmark README.md",
        "Cohort definitions, ClinGen local posterior calibration setup, results tables and EVEE leakage caveat.",
        "reproduction_instructions",
    )
    S_SUMMARY = b.source(
        f"{PREFIX}-source-summary", f"{BENCH_DIR}/results/calibration_summary.json",
        "clingen-pp3-bp4 calibration_summary.json",
        "Strict-JSON output of 1,000-bootstrap ClinGen PP3/BP4 local posterior calibration across three held-out ClinVar missense cohorts and nine score tracks.",
        "rewire_execution_report",
    )
    S_TABLES = b.source(
        f"{PREFIX}-source-tables", f"{BENCH_DIR}/results/calibration_tables.tsv",
        "clingen-pp3-bp4 calibration_tables.tsv",
        "Tabulated AUROC, AUPRC, discounted PP3/BP4 score thresholds and tier reach shares per cohort and predictor.",
        "rewire_execution_report",
    )
    S_RECEIPT = b.source(
        f"{PREFIX}-source-receipt", f"{BENCH_DIR}/results/receipt.json",
        "clingen-pp3-bp4 CPU execution receipt.json",
        "CPU run receipt covering runtime (170.79 s), random seed (20261123), environment metadata, 16 hashed inputs and 4 output artifacts.",
        "rewire_run_receipt",
        {"source_locator": f"{BENCH_DIR}/results/receipt.json, JSON pointers /kind, /seed, /parameters, /inputs and /outputs"},
    )
    S_COHORTS = b.source(
        f"{PREFIX}-source-cohorts", f"{BENCH_DIR}/cohorts/cohort_summary.json",
        "clingen-pp3-bp4 cohort_summary.json",
        "Exact variant counts by ClinVar archive holdout cutoff, clinical assertion class, novelty and gnomAD v3.1.2 grpmax < 0.1% filter.",
        "rewire_execution_report",
    )
    S_MANIFEST = b.source(
        f"{PREFIX}-source-manifest", f"{BENCH_DIR}/raw/download_manifest.json",
        "clingen-pp3-bp4 ClinVar download_manifest.json",
        "Archived NCBI ClinVar GRCh38 VCF URLs (2023-12-26, 2025-03-30, 2026-11-08), byte sizes and SHA-256 digests.",
        "study_protocol",
    )

    receipt_doc = load(root, f"{BENCH_DIR}/results/receipt.json")
    cohort_doc = load(root, f"{BENCH_DIR}/cohorts/cohort_summary.json")
    summary_doc = load(root, f"{BENCH_DIR}/results/calibration_summary.json")
    assert receipt_doc["seed"] == "20261123"
    assert receipt_doc["cost"]["paid_compute"] is False
    assert cohort_doc["post_2023_12"]["total"] == "9450"
    assert cohort_doc["post_2025_03"]["total"] == "3818"

    limitations = [
        "Precomputed score tables on temporally held-out ClinVar >=2-star missense SNVs; does not evaluate indels, noncoding variants or predictors absent from public lookup tables.",
        "EVEE (Zenodo 19701997) incorporates ClinVar supervision through 2026-03-20 and has direct target exposure on post_2023_12 and post_2025_03; withheld as a leaked descriptive control.",
        "Earlier predictors (REVEL v1.3, CADD v1.7, AlphaMissense) predate or partially overlap older ClinVar releases; only variants without prior P/LP or B/LB assertions at the cutoff date enter each holdout.",
        "gnomAD reference calibration uses 6,312 missense SNVs (5,155 ClinVar VUS with population AF and 1,157 gnomAD missense background SNVs) to solve the prior-matched local posterior equation with gft = 0.03.",
    ]

    BENCH = b.add(
        f"{PREFIX}-benchmark",
        "benchmark",
        "ClinGen PP3/BP4 local posterior score calibration on held-out ClinVar missense SNVs (Rewire)",
        "Rewire-designed CPU calibration benchmark applying Pejaver et al. 2022 and Bergquist et al. 2025 local posterior calibration across temporally held-out ClinVar missense SNVs and non-1000G allele-frequency controls.",
        "source_checked",
        areas,
        [S_README, S_SUMMARY, S_TABLES, S_RECEIPT, S_COHORTS, S_MANIFEST],
        [],
        {
            "entity_level": "suite",
            "depth_tier": 1,
            "version": "0.1.0",
            "task": "Calibrate computational variant predictor scores to ACMG/AMP PP3 and BP4 evidence strength thresholds",
            "scope_note": "Nine score tracks across eight predictors calibrated on CPU from committed variant cohorts and score tables with 1,000 stratified bootstrap resamples.",
            "limitations": limitations,
            "source_locator": f"{BENCH_DIR}/README.md",
        },
    )

    subsets, protocols = {}, {}
    for skey, sslug, label, slabel, sorder, sdesc, ptext, plimit in STRATA_SPECS:
        first_model = next(iter(summary_doc["strata"][skey].values()))
        eligible = int(first_model["n_pos"]) + int(first_model["n_neg"])
        subsets[skey] = b.add(
            f"{PREFIX}-dataset-{sslug}",
            "dataset_subset",
            f"clingen-pp3-bp4 cohort: {skey} ({eligible} missense SNVs)",
            sdesc,
            "source_checked",
            areas,
            [S_COHORTS, S_MANIFEST, S_README],
            [],
            {
                "version": "clinvar-2026-11-08",
                "eligible_count": eligible,
                "limitations": [plimit, limitations[3]],
                "source_locator": f"{BENCH_DIR}/cohorts/cohort_summary.json; {BENCH_DIR}/raw/download_manifest.json",
            },
        )
        protocols[skey] = b.add(
            f"{PREFIX}-protocol-{sslug}",
            "protocol",
            label,
            sdesc,
            "source_checked",
            areas,
            [S_README, S_SUMMARY, S_RECEIPT],
            [("part_of", BENCH), ("uses_data", subsets[skey])],
            {
                "protocol": (
                    f"{ptext} Calibrated with alpha = 0.0441, c = 1124, minpoints = 100 and "
                    "1,000-bootstrap one-sided 95% conservative bounds (seed 20261123)."
                ),
                "version": "0.1.0",
                "bootstrap_replicates": 1000,
                "uncertainty_reporting": {
                    "definition": "One-sided 95% conservative bootstrap discounted thresholds (Bergquist et al. 2025) and two-sided 95% percentile intervals for AUROC/AUPRC."
                },
                "limitations": [plimit] + limitations[:2],
                "source_locator": f"{BENCH_DIR}/README.md; {BENCH_DIR}/results/calibration_summary.json, JSON pointers /parameters and /strata/{skey}",
            },
        )

    configs = {}
    for mkey, label, desc, target, mtypes, version, prov_note in PREDICTOR_SPECS:
        attrs = {
            "provenance_note": prov_note,
            "source_locator": f"{BENCH_DIR}/src/clingen_pp3_bp4/calibrate.py, PREDICTORS entry '{mkey}'",
        }
        if version:
            attrs = {"version": version, **attrs}
        else:
            attrs["missing_metadata"] = {
                "version": {"reason": "unreported", "note": "Unversioned release or raw/PHRED track table at retrieval."}
            }
        configs[mkey] = b.add(
            f"{PREFIX}-configuration-{slug(mkey)}",
            "configuration",
            label,
            desc,
            "source_checked",
            {**areas, "method_types": mtypes},
            [S_README],
            [("configuration_of", target)],
            attrs,
        )

    evals_by_stratum = {skey: [] for skey, *_ in STRATA_SPECS}
    evee_evals = []

    for skey, sslug, _, _, _, _, _, _ in STRATA_SPECS:
        for mkey, label, _, _, _, _, _ in PREDICTOR_SPECS:
            cal = summary_doc["strata"][skey][mkey]
            n_pos = int(cal["n_pos"])
            n_neg = int(cal["n_neg"])
            scored = n_pos + n_neg
            total_eligible = int(summary_doc["strata"][skey]["gpn_msa"]["n_pos"]) + int(summary_doc["strata"][skey]["gpn_msa"]["n_neg"])
            ev_id = b.add(
                f"{PREFIX}-evaluation-{slug(mkey)}-{sslug}",
                "evaluation",
                f"{label} calibrated on {skey} ({n_pos} P/LP, {n_neg} B/LB)",
                f"ClinGen PP3/BP4 local posterior calibration and discrimination evaluation on {skey}.",
                "source_checked",
                {"areas": ["dna-genomes"]},
                [S_SUMMARY, S_TABLES, S_RECEIPT],
                [("system", configs[mkey]), ("assessment", protocols[skey]), ("data", subsets[skey])],
                {
                    "origin": "rewire_run",
                    "execution_scope": "complete_selected_evaluation",
                    "protocol": f"Pejaver et al. 2022 and Bergquist et al. 2025 local posterior calibration on {skey}",
                    "version": "0.1.0",
                    "eligible_count": total_eligible,
                    "coverage": {
                        "scored": scored,
                        "eligible": total_eligible,
                        "unit": "missense SNVs",
                        "note": f"Scored {n_pos} P/LP and {n_neg} B/LB variants in {skey} against 6,312 gnomAD reference missense SNVs.",
                    },
                    "comparison": {
                        "protocol_id": protocols[skey],
                        "dataset_version": subsets[skey],
                        "split": f"Temporal ClinVar holdout ({skey})",
                        "population": f"{n_pos} pathogenic/likely pathogenic and {n_neg} benign/likely benign missense SNVs",
                        "inputs": "Precomputed genomic predictor score lookup",
                        "adaptation": "none; precomputed scores calibrated post hoc via Pejaver sliding-window local posterior",
                        "metric_implementation": f"{BENCH_DIR}/src/clingen_pp3_bp4/calibrate.py at {PIN_COMMIT[:7]}",
                        "aggregation": "Binary classification discrimination and local-posterior evidence strength cutoffs",
                        "budget": "CPU-only lookup calibration (170.79 s total batch)",
                    },
                    "source_locator": f"{BENCH_DIR}/results/calibration_summary.json, JSON pointer /strata/{skey}/{mkey}",
                },
            )
            if mkey == "evee":
                evee_evals.append(ev_id)
            else:
                evals_by_stratum[skey].append(ev_id)

            res_src = [S_SUMMARY, S_RECEIPT]
            base_ptr = f"/strata/{skey}/{mkey}"
            b.result(
                f"{PREFIX}-result-{slug(mkey)}-{sslug}-auroc",
                f"{label} on {skey}: AUROC",
                res_src, ev_id, S_SUMMARY, f"{base_ptr}/auroc",
                "auroc", "higher", "unitless",
                f"AUROC over {n_pos} P/LP and {n_neg} B/LB variants in {skey}.",
                ci=f"{base_ptr}/auroc_ci95",
                extra={"metric_qualifier": f"ClinVar >=2-star missense SNVs ({skey})", "eligible_count": scored},
            )
            b.result(
                f"{PREFIX}-result-{slug(mkey)}-{sslug}-auprc",
                f"{label} on {skey}: AUPRC",
                res_src, ev_id, S_SUMMARY, f"{base_ptr}/auprc",
                "auprc", "higher", "unitless",
                f"AUPRC over {n_pos} P/LP and {n_neg} B/LB variants in {skey}.",
                ci=f"{base_ptr}/auprc_ci95",
                extra={"metric_qualifier": f"ClinVar >=2-star missense SNVs ({skey})", "eligible_count": scored},
            )

            # Discounted PP3 and BP4 score thresholds (only emit tiers reached by conservative bootstrap bound)
            for lvl, tlabel, tshort, pts in PP3_TIERS:
                val = cal["discounted_thresholds"]["PP3"][lvl]
                if val is not None:
                    b.result(
                        f"{PREFIX}-result-{slug(mkey)}-{sslug}-pp3-{slug(lvl).lower()}-thr",
                        f"{label} on {skey}: PP3 {tlabel} threshold",
                        res_src, ev_id, S_SUMMARY, f"{base_ptr}/discounted_thresholds/PP3/{lvl}",
                        "evidence-strength-score-interval", "unknown", "unitless",
                        f"Conservative one-sided 95% bootstrap PP3 {tlabel} score threshold on {skey}.",
                        ci=f"{base_ptr}/bootstrap_intervals_95/PP3/{lvl}",
                        extra={
                            "unit_detail": f"{label} score",
                            "metric_qualifier": f"PP3 {tlabel}, ClinGen local posterior calibration ({skey}, +{pts} pts)",
                            "numeric_representation": "numeric_value is the lower-bound score required to reach this pathogenic strength tier.",
                        },
                    )
                    b.result(
                        f"{PREFIX}-result-{slug(mkey)}-{sslug}-pp3-{slug(lvl).lower()}-plp-share",
                        f"{label} on {skey}: P/LP share reaching PP3 {tshort}",
                        res_src, ev_id, S_SUMMARY, f"{base_ptr}/pathogenic_reach/PP3_{lvl}/share",
                        "proportion", "unknown", "fraction",
                        f"Share of {n_pos} held-out P/LP variants falling in non-overlapping PP3 {tlabel} tier on {skey}.",
                        extra={
                            "metric_qualifier": f"held-out P/LP fraction in PP3 {tlabel} ({skey})",
                            "denominator": n_pos,
                        },
                    )

            for lvl, tlabel, tshort, pts in BP4_TIERS:
                val = cal["discounted_thresholds"]["BP4"][lvl]
                if val is not None:
                    b.result(
                        f"{PREFIX}-result-{slug(mkey)}-{sslug}-bp4-{slug(lvl).lower()}-thr",
                        f"{label} on {skey}: BP4 {tlabel} threshold",
                        res_src, ev_id, S_SUMMARY, f"{base_ptr}/discounted_thresholds/BP4/{lvl}",
                        "evidence-strength-score-interval", "unknown", "unitless",
                        f"Conservative one-sided 95% bootstrap BP4 {tlabel} score threshold on {skey}.",
                        ci=f"{base_ptr}/bootstrap_intervals_95/BP4/{lvl}",
                        extra={
                            "unit_detail": f"{label} score",
                            "metric_qualifier": f"BP4 {tlabel}, ClinGen local posterior calibration ({skey}, {pts} pts)",
                            "numeric_representation": "numeric_value is the upper-bound score required to reach this benign strength tier.",
                        },
                    )
                    b.result(
                        f"{PREFIX}-result-{slug(mkey)}-{sslug}-bp4-{slug(lvl).lower()}-blb-share",
                        f"{label} on {skey}: B/LB share reaching BP4 {tshort}",
                        res_src, ev_id, S_SUMMARY, f"{base_ptr}/benign_reach/BP4_{lvl}/share",
                        "proportion", "unknown", "fraction",
                        f"Share of {n_neg} held-out B/LB variants falling in non-overlapping BP4 {tlabel} tier on {skey}.",
                        extra={
                            "metric_qualifier": f"held-out B/LB fraction in BP4 {tlabel} ({skey})",
                            "denominator": n_neg,
                        },
                    )

    # Withhold EVEE evaluations from unconfounded model comparisons due to ClinVar label leakage
    by_id = {r["id"]: r for r in b.records}
    by_id[S_README]["attributes"]["evidence_concerns"] = [{
        "source_id": S_README,
        "message": (
            "EVEE (Zenodo 19701997) incorporates ClinVar supervision through 2026-03-20 and therefore "
            "has direct target exposure on the post_2023_12 and post_2025_03 held-out cohorts. Its three "
            "evaluations are kept strictly as descriptive leaked controls and withheld from unconfounded comparisons."
        ),
        "source_locator": f"{BENCH_DIR}/README.md, EVEE leakage caveat",
        "artifact_sha256": b.sources[S_README][1],
        "review_date": DAY,
        "applies_to": evee_evals,
    }]

    # Relevance judgements linking the three protocols to use-case-missense-pp3-bp4-calibrated-evidence
    rationales = {
        "post_2023_12": (
            "Direct ClinGen PP3/BP4 local posterior calibration on 9,450 held-out ClinVar >=2-star missense SNVs "
            "spanning GPN-MSA, GPN-Star, AlphaGenome AVI, AlphaMissense, REVEL v1.3 and CADD v1.7. Unfiltered baseline stratum "
            "prior to rare-variant grpmax restriction."
        ),
        "post_2023_12_af001": (
            "Primary allele-frequency controlled ClinGen PP3/BP4 calibration on 8,141 held-out ClinVar >=2-star missense SNVs "
            "(gnomAD v3.1.2 grpmax < 0.1%). Shows AlphaGenome AVI loses PP3 Strong (+4) under rare-variant control while REVEL (0.916) "
            "and AlphaMissense (0.987) retain PP3 Strong."
        ),
        "post_2025_03": (
            "Sensitivity ClinGen PP3/BP4 calibration on 3,818 post-Mar-2025 ClinVar >=2-star missense SNVs verifying "
            "threshold behavior after pre-2025 predictors were frozen."
        ),
    }

    for skey, sslug, label, slabel, sorder, _, _, plimit in STRATA_SPECS:
        claim_review = b.review(
            S_SUMMARY,
            f"Judgement pinned to eight non-leaked evaluations on {protocols[skey]}; leaked EVEE control excluded.",
            methods=["scope-review", "source-hash-verification"],
        )
        claim_review.pop("date", None)
        claim_review["reviewed_at"] = NOW
        b.add(
            f"use-case-mapping-{PREFIX}-{sslug}",
            "claim",
            f"Relevance of {protocols[skey]} to {USE_CASE_ID}",
            f"Direct ClinGen PP3/BP4 calibration protocol ({skey}) evaluated across unconfounded predictors and clinical baselines.",
            "source_checked",
            {},
            [S_SUMMARY, S_RECEIPT, S_README],
            [("subject", USE_CASE_ID)],
            {
                "field": f"links:assessed_by:{protocols[skey]}",
                "value": protocols[skey],
                "relevance": "direct",
                "endpoint": "Calibrated ACMG/AMP PP3 and BP4 score thresholds (Pejaver/Bergquist points scale), tier reach shares, AUROC and AUPRC",
                "rationale": rationales[skey],
                "constraints": [
                    "Withhold EVEE evaluations from unconfounded model comparisons due to ClinVar supervision through 2026-03-20.",
                    "Prefer post_2023_12_af001 over unfiltered post_2023_12 for rare-disease missense interpretation where benign variants are rare.",
                ],
                "limitations": [plimit] + limitations[:2],
                "citation_locators": [{"source_id": S_SUMMARY, "locator": f"{BENCH_DIR}/results/calibration_summary.json, JSON pointer /strata/{skey}"}],
                "source_locator": f"{BENCH_DIR}/README.md; {BENCH_DIR}/results/calibration_summary.json",
                "headline_metric": "evidence-strength-score-interval",
                "comparison_group": PREFIX,
                "comparison_title": "ClinGen PP3/BP4 local posterior calibration on held-out ClinVar missense SNVs",
                "stratum_label": slabel,
                "stratum_order": sorder,
                "reason": "First Rewire-designed CPU calibration benchmark (rewire-benchmarks #65 and #63).",
                "review": claim_review,
                "reviewed_evaluations": evals_by_stratum[skey],
            },
        )

    assert len(evee_evals) == 3
    assert all(len(v) == 8 for v in evals_by_stratum.values())
    return b


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--check"]
    bench_root, out_dir = Path(args[0]), Path(args[1])
    batch = build(bench_root)
    batch.verify()
    text = batch.lines()
    target = out_dir / "batch.jsonl"
    if "--check" in sys.argv:
        assert target.read_text() == text, "batch.jsonl differs from a rebuild"
        print(f"{len(batch.records)} records rebuilt and equal to {target}")
    else:
        out_dir.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        print(f"{len(batch.records)} records written to {target}")
