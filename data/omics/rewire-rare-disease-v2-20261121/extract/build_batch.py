#!/usr/bin/env python3
"""Build the batch for one finished Rewire study from its result files at a pinned commit.

  python3 build_batch.py evo2ops <checkout of rewire-bio/evo2-cloud-operations> <batch folder>
  python3 build_batch.py rdv2 <checkout of rewire-bio/amp-2026-studies> <batch folder>
  add --check to rebuild in memory and compare with the batch.jsonl already in the folder

The checkout must be at the pinned commit. Every stored value is the literal number token of a
JSON file in that checkout (floats are read as strings, so no digit passes through a float), and
every result's source_locator is the file path and the JSON pointer it was read from. The script
re-reads each pointer after building and fails if a stored value is not the token at its pointer.
It asserts the counts of records it expects. Nothing is taken from a README where a result file
holds the value.
"""
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

DAY = "2026-11-21"
NOW = "2026-11-21T14:00:00Z"
PINS = {
    "evo2ops": ("rewire-bio/evo2-cloud-operations", "f8ae11c9a1c45505487c978b4cb7e064c4e59905"),
    "rdv2": ("rewire-bio/amp-2026-studies", "3fbab97b0f437972a1a6e0f2171ebb5d9a3d9f19"),
}
REVIEWER_NOTE = ("Claude agent, automated. The same agent wrote the generator and ran its re-read check; "
                 "no independent second pass and no human review")


def load(root, rel):
    return json.loads((root / rel).read_text(), parse_float=str)


def pointer(doc, ptr):
    for part in ptr.split("/")[1:]:
        doc = doc[int(part)] if isinstance(doc, list) else doc[part]
    return doc


class Batch:
    def __init__(self, study, root):
        self.study, self.root = study, root
        self.repo, self.commit = PINS[study]
        head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        assert head == self.commit, f"checkout is at {head}, expected {self.commit}"
        self.records, self.checks, self.sources = [], [], {}

    def add(self, id, kind, name, description, status, facets, source_ids, links, attributes):
        assert id not in {r["id"] for r in self.records}, id
        self.records.append({"id": id, "kind": kind, "name": name, "description": description, "status": status,
                             "facets": facets, "source_ids": source_ids,
                             "links": [{"relation": r, "target_id": t} for r, t in links], "attributes": attributes})
        return id

    def source(self, id, rel, name, description, source_type, extra=None):
        data = (self.root / rel).read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        attrs = {
            "url": f"https://github.com/{self.repo}/blob/{self.commit}/{rel}",
            "artifact_url": f"https://raw.githubusercontent.com/{self.repo}/{self.commit}/{rel}",
            "artifact_sha256": sha,
            "hash_scope": "complete bytes of the file at the pinned commit",
            "version": self.commit,
            "retrieved_at": NOW,
            "source_type": source_type,
            "evidence_origin": "rewire_run",
            "publication_status": "official_project_source",
        }
        attrs.update(extra or {})
        self.sources[id] = (rel, sha)
        return self.add(id, "source", name, description, "source_checked", {"areas": ["dna-genomes"]}, [], [], attrs)

    def review(self, source_id, note):
        rel, sha = self.sources[source_id]
        return {
            "method": ["execution-evidence-review", "source-hash-verification"],
            "reviewer": ["claude"],
            "date": DAY,
            "artifact_sha256": sha,
            "retrieval_url": f"https://raw.githubusercontent.com/{self.repo}/{self.commit}/{rel}",
            "method_note": "Value read by build_batch.py as the literal JSON number token at the pointer in the "
                           "pinned file, then re-read from the same bytes and compared; file hash recomputed from "
                           "a fresh download of the raw URL",
            "reviewer_note": REVIEWER_NOTE,
            "note": note,
        }

    def result(self, id, name, status, source_ids, evaluation, value_source, ptr, metric, direction, unit,
               note, ci=None, resamples=None, ci_scope=None, extra=None):
        rel, _ = self.sources[value_source]
        doc = load(self.root, rel)
        value = pointer(doc, ptr)
        assert isinstance(value, str), (rel, ptr, value)
        attrs = {"printed_value": value, "numeric_value": value, "metric": metric, "metric_direction": direction,
                 "unit": unit}
        attrs.update(extra or {})
        self.checks.append((id, rel, ptr, "printed_value"))
        if ci:
            low, high = pointer(doc, ci)
            attrs["uncertainty"] = {"type": "confidence_interval", "lower": low, "upper": high, "level": 0.95,
                                    "method": "bootstrap", "resamples": resamples, "scope": ci_scope,
                                    "source_column": f"JSON pointer {ci}"}
            self.checks.append((id, rel, ci, "ci"))
        attrs["source_locator"] = f"{rel}, JSON pointer {ptr}"
        attrs["review"] = self.review(value_source, note)
        if not ci:
            attrs["missing_metadata"] = {"uncertainty": {"reason": "unreported", "note": "The file gives no interval at this pointer."}}
        return self.add(id, "result", name, "", status, {"areas": ["dna-genomes"]}, source_ids,
                        [("evaluation", evaluation)], attrs)

    def verify(self):
        by_id = {r["id"]: r for r in self.records}
        for id, rel, ptr, what in self.checks:
            token = pointer(load(self.root, rel), ptr)
            a = by_id[id]["attributes"]
            if what == "printed_value":
                assert a["printed_value"] == token == a["numeric_value"], (id, ptr)
                raw = (self.root / rel).read_text()
                assert token in raw, (id, token)
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


def slug(text):
    out = "".join(c if c.isalnum() else "-" for c in text.lower())
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


# ---------------------------------------------------------------------------------------------
# evo2-cloud-operations
# ---------------------------------------------------------------------------------------------

def evo2ops(root):
    b = Batch("evo2ops", root)
    P = "rewire-local-20261121-evo2ops"
    run = "evidence/runs/recorded-b75c67aa"
    areas = {"areas": ["dna-genomes"], "contexts": ["research"]}
    no_licence = {"missing_metadata": {"licence": {"reason": "unreported", "note": "README.md, Licences: the study code licence is to be set at publication."}}}

    ops = load(root, f"{run}/operations.json")
    attempts = {p: ops["platforms"][p]["attempt"] for p in ("P2", "P3", "P5")}
    assert attempts == {"P2": "attempt-1", "P3": "attempt-1", "P5": "attempt-2"}, attempts

    S_RES = b.source(f"{P}-source-results", f"{run}/results.json",
                     "evo2-cloud-operations recorded run b75c67aa: results.json",
                     "Scientific outputs of the recorded run: W0 loss, W1 and W2 AUROCs, baseline AUROCs and cross-platform agreement.",
                     "rewire_execution_report", no_licence)
    S_CUR = b.source(f"{P}-source-current-predictors", "evidence/current-predictors/results.json",
                     "evo2-cloud-operations amendment 7: current predictors results.json",
                     "AUROCs of CADD v1.7, SpliceAI and REVEL against the recorded Evo 2 7B scores on the same BRCA1 variants, computed without a GPU.",
                     "rewire_execution_report", no_licence)
    S_OPS = b.source(f"{P}-source-operations", f"{run}/operations.json",
                     "evo2-cloud-operations recorded run b75c67aa: operations.json",
                     "Per-platform attempt used, instance, events, timings and cost of the recorded run.",
                     "rewire_execution_report", no_licence)
    S_PROTO = b.source(f"{P}-source-protocol", "protocol.md", "evo2-cloud-operations: protocol.md",
                       "Study protocol: workloads W0 to W4, labels, metric, bootstrap and limitations.",
                       "study_protocol", no_licence)
    S_AMD7 = b.source(f"{P}-source-amendment-7", "protocol/amendments/007-current-predictors.md",
                      "evo2-cloud-operations: protocol amendment 7, current predictors",
                      "Amendment adding CADD v1.7, SpliceAI and REVEL v1.3 to the BRCA1 comparison, with the origin of each score.",
                      "study_protocol", no_licence)
    amd7 = (root / "protocol/amendments/007-current-predictors.md").read_text()
    for needle in ("CADD v1.3: the column supplied with the Findlay et al. table, as in W1", "**CADD v1.7, GRCh37**",
                   "precomputed masked SpliceAI scores", "**REVEL v1.3**", "Google Cloud H100 (P2), score = -delta"):
        assert needle in amd7, needle
    S_README = b.source(f"{P}-source-readme", "README.md", "evo2-cloud-operations: README.md",
                        "Run instructions, hardware table and status of the study.", "reproduction_instructions", no_licence)
    platforms = {
        "P2": ("Google Cloud H100", "gcp-h100"),
        "P3": ("Runpod H100", "runpod-h100"),
        "P5": ("Runpod L40S", "runpod-l40s"),
    }
    receipts, receipt_doc = {}, {}
    for p, (label, pslug) in platforms.items():
        rel = f"{run}/platforms/{p}/{attempts[p]}/receipt-main.json"
        receipt_doc[p] = load(root, rel)
        assert receipt_doc[p]["status"] == "completed" and receipt_doc[p]["results"]["w1"]["variants"] == 3893, p
        assert receipt_doc[p]["environment"]["platform_id"] == p
        receipts[p] = b.source(
            f"{P}-receipt-{pslug}", rel,
            f"evo2-cloud-operations recorded run b75c67aa: run receipt, {label} ({p}, {attempts[p]})",
            f"Receipt written on the {label} machine for workloads W0 to W3 of the recorded run: environment, image digest, "
            "W0 loss, W1 variants scored, throughput and peak memory. A run by the project with its own code, not an independent reproduction.",
            "rewire_run_receipt",
            {**no_licence, "source_locator": "JSON pointers /status, /environment and /results/w1"})

    # The receipts hold throughput and counts, not the AUROC, and the study's repeat on another
    # L40S host gave a different throughput. The repeat's receipt and the run log are sources so
    # that the limitation on the L40S throughput is pinned to bytes.
    repro_rel = "evidence/runs/reproduction-30e7ae49/platforms/P5/attempt-1/receipt-main.json"
    repro = load(root, repro_rel)
    assert repro["status"] == "completed" and repro["environment"]["platform_id"] == "P5"
    assert repro["environment"]["gpu_name"] == receipt_doc["P5"]["environment"]["gpu_name"] == "NVIDIA L40S"
    for field in ("sequences_scored", "variants"):
        assert repro["results"]["w1"][field] == receipt_doc["P5"]["results"]["w1"][field], field
    l40s_recorded = receipt_doc["P5"]["results"]["w1"]["sequences_per_second"]
    l40s_repeat = repro["results"]["w1"]["sequences_per_second"]
    assert (l40s_recorded, l40s_repeat) == ("0.6117", "0.9081"), (l40s_recorded, l40s_repeat)
    for p in platforms:
        assert "auroc" not in json.dumps(receipt_doc[p]).lower(), p
    S_REPRO_P5 = b.source(
        f"{P}-receipt-reproduction-runpod-l40s", repro_rel,
        "evo2-cloud-operations reproduction run 30e7ae49: run receipt, Runpod L40S (P5, attempt-1)",
        "Receipt written on the Runpod L40S machine of the study's reproduction run. Cited only for its W1 throughput, "
        "which differs from the recorded run's on another L40S host. No result of this batch takes its value from it.",
        "rewire_run_receipt",
        {**no_licence, "source_locator": "JSON pointers /status, /environment/gpu_name and /results/w1"})
    log_rel = "evidence/run-log.md"
    log = (root / log_rel).read_text()
    slow_host = "P5 attempt 2 completed W0 to W4 on a slower L40S host\n  (0.61 windows per second, against 0.93 on the host used earlier the same day)."
    assert slow_host in log
    S_LOG = b.source(f"{P}-source-run-log", log_rel, "evo2-cloud-operations: run log",
                     "Dated log of every run and failed attempt of the study, including the host used for each L40S attempt.",
                     "rewire_execution_report",
                     {**no_licence, "source_locator": "Section '2026-10-09, clean recorded run'"})
    l40s_limit = (f"The Runpod L40S value of the recorded run, {l40s_recorded} sequences per second, was not repeated: the study's "
                  f"reproduction run 30e7ae49 measured {l40s_repeat} on another L40S host for the same "
                  f"{receipt_doc['P5']['results']['w1']['sequences_scored']} sequences, and the run log calls the recorded host a slower one.")
    prov = json.loads((root / f"{run}/provenance.json").read_text())
    run_rev = prov[0]["git_revision"]
    assert len(prov) == 1 and run_rev == "e93491ac66490ae30d052d2862eea0e37d27f011", prov
    ran_at = f"the recorded run used revision {run_rev[:7]} ({run}/provenance.json), an ancestor of the pinned commit"

    cur = load(root, "evidence/current-predictors/results.json")
    strata = {
        "all": ("all SNVs", int(cur["main"]["all"]["n"]), int(cur["main"]["all"]["lof"]), "/main/all"),
        "coding": ("coding SNVs (missense, nonsense, synonymous)", int(cur["main"]["coding"]["n"]), int(cur["main"]["coding"]["lof"]), "/main/coding"),
        "noncoding": ("noncoding SNVs (all other consequences)", int(cur["main"]["noncoding"]["n"]), int(cur["main"]["noncoding"]["lof"]), "/main/noncoding"),
        "missense": ("missense SNVs", int(cur["missense"]["n"]), int(cur["missense"]["lof"]), "/missense"),
    }
    assert strata["all"][1] == 3893

    limits = [
        "One gene and one checkpoint size (Evo 2 7B). The study says nothing about clinical validity, calibration or ancestry.",
        "A run by the project with its own code on public data. It is not an independent reproduction of a published score.",
        "The L40S gave different per-variant scores from the two H100s (results.json, /agreement_with_reference/P5), so the hardware is part of each result.",
        "Baseline scores need no GPU and are covered by no run receipt.",
        "No result is marked reproduced. The run receipts hold counts, timings and throughput but neither the AUROC nor a hash of the scores file, and AUROC is computed afterwards from the committed scores.",
    ]
    BENCH = b.add(f"{P}-benchmark", "benchmark",
                  "Evo 2 7B on BRCA1 saturation genome editing SNVs across cloud GPUs (Rewire, evo2-cloud-operations)",
                  "Rewire's own study: one pinned Evo 2 7B container scores 3,893 BRCA1 SNVs on three cloud GPUs and is compared with lookup predictors on the same variants.",
                  "source_checked", areas, [S_PROTO, S_README, S_RES, S_OPS, S_AMD7], [],
                  {"entity_level": "suite", "version": b.commit, "task": "Zero-shot classification of BRCA1 loss-of-function SNVs",
                   "scope_note": "Recorded run b75c67aa of 9 October 2026 and its amendment 7 analysis. W0, W2, W3, W4, the reproduction run, the follow-up runs and costs are not ingested.",
                   "depth_tier": 1, "limitations": limits, "source_locator": "protocol.md, Workloads and Analysis; README.md, Status"})

    subsets, protocols = {}, {}
    for key, (label, n, lof, ptr) in strata.items():
        subsets[key] = b.add(f"{P}-dataset-brca1-{key}", "dataset_subset",
                             f"BRCA1 saturation genome editing SNVs, {label} (evo2-cloud-operations W1)",
                             f"{n} BRCA1 SNVs from the Findlay et al. 2018 table as used by workload W1, of which {lof} are labelled loss of function.",
                             "source_checked", areas, [S_CUR, S_PROTO], [],
                             {"version": b.commit, "eligible_count": n, "positive_count": lof,
                              "source_dataset_label": "Findlay et al. 2018 BRCA1 saturation genome editing table, as copied in ArcInstitute/evo2",
                              "source_locator": f"evidence/current-predictors/results.json, JSON pointers {ptr}/n and {ptr}/lof"})
        attrs = {
            "protocol": f"AUROC for loss of function (LOF) against functional or intermediate (FUNC and INT) on {label}; scores are oriented so that higher means predicted loss of function.",
            "version": b.commit, "metric": "auroc", "metric_direction": "higher", "unit": "unitless",
            "bootstrap_replicates": 2000,
            "uncertainty_reporting": {"definition": "95% interval from 2,000 bootstrap resamples of positions (seed 7), keeping the three SNVs at a position together"},
            "limitations": limits + (["The missense subset was analysed in amendment 7, after the recorded run."] if key == "missense" else []),
            "source_locator": "protocol.md, Workloads (W1) and Analysis",
        }
        src = [S_PROTO, S_RES, S_CUR]
        pid = f"{P}-protocol-brca1-{key}-auroc"
        protocols[key] = b.add(pid, "protocol", f"Zero-shot BRCA1 loss-of-function classification, {label} (evo2-cloud-operations W1)",
                               f"AUROC of a variant score for BRCA1 loss of function on {n} SNVs.", "source_checked", areas, src,
                               [("part_of", BENCH), ("uses_data", subsets[key])], attrs)
    pid = f"{P}-protocol-brca1-scoring-throughput"
    protocols["throughput"] = b.add(
        pid, "protocol", "Evo 2 7B BRCA1 variant scoring throughput on one GPU (evo2-cloud-operations W1)",
        "Sequences scored per second while scoring 3,893 BRCA1 SNVs as paired 8,192 bp windows at batch size 1.",
        "source_checked", areas, [S_PROTO, S_README] + list(receipts.values()) + [S_REPRO_P5, S_LOG],
        [("part_of", BENCH), ("uses_data", subsets["all"])],
        {"protocol": "Workload W1: 8,192 bp windows centred on each SNV, variant and reference windows scored at batch size 1; throughput is sequences scored divided by scoring seconds as written by the run.",
         "version": b.commit, "metric": "inference-throughput", "metric_direction": "higher", "unit": "sample-per-second",
         "unit_detail": "8,192 bp sequences per second",
         "limitations": ["One run per platform. Throughput depends on the host as well as the GPU model.", l40s_limit, limits[1]],
         "source_locator": "protocol.md, Workloads (W1)"})

    # configurations
    cfg = {}
    for p, (label, pslug) in platforms.items():
        env = receipt_doc[p]["environment"]
        cfg[p] = b.add(f"{P}-configuration-evo2-7b-{pslug}", "configuration", f"Evo 2 7B zero-shot likelihood score on {label}",
                       "Evo 2 7B scores a variant as the mean log-likelihood of its 8,192 bp window minus that of the reference window, negated so that higher means more damaging.",
                       "source_checked", {**areas, "method_types": ["foundation_model"]}, [receipts[p], S_PROTO, S_OPS],
                       [("configuration_of", "discovery-model-evo-2")],
                       {"version": "evo2_7b", "checkpoint": "evo2_7b",
                        "hardware": {"gpu_name": env["gpu_name"], "platform_id": p, "nvidia_smi": env["nvidia_smi"]},
                        "environment": {k: env[k] for k in ("image", "code_sha256", "pip_freeze_sha256", "python", "torch", "torch_cuda", "kernel")},
                        "provenance_note": f"Run by Rewire in recorded run b75c67aa on {label} (platform {p}, {attempts[p]}).",
                        "source_locator": f"{b.sources[receipts[p]][0]}, JSON pointer /environment; protocol.md, Workloads (W1); {run}/operations.json, JSON pointer /platforms/{p}/attempt"})
    amd = "protocol/amendments/007-current-predictors.md, Inputs"
    lookups = {
        "cadd-v1-3": ("CADD v1.3 score from the Findlay et al. table", "CADD v1.3 score as supplied in the Findlay et al. BRCA1 table, higher meaning more deleterious.", "somatic-oncogenicity-20261009-method-cadd", "supervised_machine_learning", "1.3", [S_AMD7, S_PROTO], f"{amd}, 'CADD v1.3: the column supplied with the Findlay et al. table'; protocol.md, Workloads (W1), baselines"),
        "phylop": ("Mammalian phyloP from the Findlay et al. table", "Mammalian phyloP conservation score as supplied in the Findlay et al. BRCA1 table, higher meaning more conserved.", "somatic-oncogenicity-20261009-method-phylop", "conventional_pipeline", None, [S_PROTO], "protocol.md, Workloads (W1), baselines"),
        "consequence-rule": ("Consequence rule (nonsense and canonical splice, then splice region, then missense, then other)", "Ranks variants by annotated consequence: nonsense and canonical splice first, then splice region, then missense, then all others.", None, "conventional_pipeline", None, [S_PROTO], "protocol.md, Workloads (W1), baselines"),
        "cadd-v1-7": ("CADD v1.7 raw score, GRCh37", "CADD v1.7 raw score for each SNV, higher meaning more deleterious.", "somatic-oncogenicity-20261009-method-cadd", "supervised_machine_learning", "1.7", [S_AMD7], f"{amd}, 'CADD v1.7, GRCh37'"),
        "spliceai": ("SpliceAI precomputed masked score from the CADD v1.7 annotations", "Largest of the four precomputed masked SpliceAI delta scores on rows annotated to BRCA1, taken from the CADD v1.7 annotation file.", "discovery-model-spliceai", "supervised_machine_learning", None, [S_AMD7], f"{amd}, 'SpliceAI'"),
        "revel": ("REVEL v1.3 score", "REVEL v1.3 ensemble score for missense variants, maximum over rows for a variant.", "somatic-oncogenicity-20261009-method-revel", "supervised_machine_learning", "1.3", [S_AMD7], f"{amd}, 'REVEL v1.3'"),
    }
    for key, (name, desc, target, mtype, version, src, loc) in lookups.items():
        attrs = {"provenance_note": "Lookup score compared with Evo 2 7B by Rewire on the same BRCA1 variants; no GPU run and no run receipt.",
                 "source_locator": loc}
        if version:
            attrs = {"version": version, **attrs}
        else:
            attrs["missing_metadata"] = {"version": {"reason": "unextracted", "note": "Not read from the pinned files for this batch."}}
        cfg[key] = b.add(f"{P}-configuration-{key}", "configuration", name, desc, "source_checked",
                         {**areas, "method_types": [mtype]}, src, [("configuration_of", target)] if target else [], attrs)

    def comparison(key, n, adaptation):
        return {"protocol_id": protocols[key], "dataset_version": subsets[key if key in subsets else "all"],
                "split": "none; every variant of the subset is scored", "population": f"{n}/{n}",
                "inputs": "variant and reference sequence, or the lookup score for the variant",
                "adaptation": adaptation, "metric_implementation": f"src/study/analysis.py; {ran_at}",
                "aggregation": "one AUROC over all variants of the subset", "budget": "one run per platform"}

    count = {"source_checked": 0}

    def auroc(key, system_key, sysname, value_source, ptr, ci, status, sources, missing=0):
        label, n, lof, _ = strata[key]
        ev = b.add(f"{P}-evaluation-{slug(system_key)}-brca1-{key}", "evaluation", f"{sysname} on BRCA1 {label}",
                   f"AUROC for BRCA1 loss of function on {n} SNVs ({lof} loss of function).", status,
                   {"areas": ["dna-genomes"]}, sources,
                   [("system", cfg[system_key]), ("assessment", protocols[key]), ("data", subsets[key])],
                   {"origin": "rewire_run", "execution_scope": "complete_selected_evaluation",
                    "protocol": "LOF against FUNC and INT; AUROC of the score oriented so that higher means loss of function",
                    "version": b.commit, "eligible_count": n, "scored_count": n - missing,
                    "coverage": {"scored": n - missing, "eligible": n, "unit": "variants"}, "positive_count": lof,
                    "comparison": comparison(key, n, "zero-shot; no fitting on these variants"),
                    "source_locator": f"{b.sources[value_source][0]}, JSON pointer {ptr.rsplit('/', 1)[0]}"})
        b.result(f"{P}-result-{slug(system_key)}-brca1-{key}-auroc", f"{sysname} on BRCA1 {label}: AUROC", status, sources, ev,
                 value_source, ptr, "auroc", "higher", "unitless",
                 ("Computed by Rewire from the Evo 2 scores committed by the recorded run on this platform. The run receipt of the "
                  "platform holds neither the AUROC nor a hash of the scores file, so it is not cited and the value is not marked reproduced."
                  if system_key in platforms and key != "missense" else
                  "Computed by Rewire from a lookup score or from committed Evo 2 scores; no run receipt covers this value."),
                 ci=ci, resamples=2000 if ci else None,
                 ci_scope="bootstrap over positions, the three SNVs at a position kept together" if ci else None,
                 extra={"metric_qualifier": f"LOF against FUNC and INT, {label}"})
        count[status] += 1

    res = load(root, f"{run}/results.json")
    assert res["reference_platform"] == "P2"
    for key in ("all", "coding", "noncoding"):
        base = f"/brca1_evo2_vs_baselines/{key}"
        assert pointer(res, f"{base}/evo2_7b/auroc") == pointer(res, f"/platforms/P2/w1_auroc/{key}") == cur["main"][key]["auroc"]["evo2_7b"]["auroc"]
        auroc(key, "P2", "Evo 2 7B (Google Cloud H100)", S_RES, f"{base}/evo2_7b/auroc", f"{base}/evo2_7b/ci95", "source_checked", [S_RES])
        for p in ("P3", "P5"):
            auroc(key, p, f"Evo 2 7B ({platforms[p][0]})", S_RES, f"/platforms/{p}/w1_auroc/{key}", None, "source_checked", [S_RES])
        for name, system_key, sysname in (("cadd", "cadd-v1-3", "CADD v1.3"), ("phylop", "phylop", "Mammalian phyloP"), ("consequence_rule", "consequence-rule", "Consequence rule")):
            auroc(key, system_key, sysname, S_RES, f"{base}/{name}/auroc", f"{base}/{name}/ci95", "source_checked", [S_RES])
        for name, system_key, sysname in (("cadd_v1.7", "cadd-v1-7", "CADD v1.7"), ("spliceai", "spliceai", "SpliceAI")):
            assert int(cur["coverage_missing"][name][key]) == 0
            auroc(key, system_key, sysname, S_CUR, f"/main/{key}/auroc/{name}/auroc", f"/main/{key}/auroc/{name}/ci95", "source_checked", [S_CUR])
    # missense, amendment 7: Evo 2 scores are those of P2 in the recorded run (followup/current_predictors.py lines 115-116)
    text = (root / "followup/current_predictors.py").read_text()
    assert '["platforms"]["P2"]["attempt"]' in text and "w1_brca1_scores.tsv" in text
    auroc("missense", "P2", "Evo 2 7B (Google Cloud H100)", S_CUR, "/missense/auroc/evo2_7b/auroc", "/missense/auroc/evo2_7b/ci95", "source_checked", [S_CUR])
    for name, system_key, sysname in (("cadd_v1.3", "cadd-v1-3", "CADD v1.3"), ("cadd_v1.7", "cadd-v1-7", "CADD v1.7"), ("revel", "revel", "REVEL v1.3")):
        assert int(cur["coverage_missing"].get(name, {"missense": 0})["missense"]) == 0
        auroc("missense", system_key, sysname, S_CUR, f"/missense/auroc/{name}/auroc", f"/missense/auroc/{name}/ci95", "source_checked", [S_CUR])

    for p, (label, pslug) in platforms.items():
        w1 = receipt_doc[p]["results"]["w1"]
        tp_sources = [receipts[p]] + ([S_REPRO_P5, S_LOG] if p == "P5" else [])
        tp_limits = ["One run on one host. Throughput depends on the host as well as the GPU model."] + ([l40s_limit] if p == "P5" else [])
        ev = b.add(f"{P}-evaluation-evo2-7b-{pslug}-scoring-throughput", "evaluation", f"Evo 2 7B scoring throughput on {label}",
                   f"Throughput of workload W1 on {label}: {w1['sequences_scored']} sequences of 8,192 bp for 3,893 variants at batch size 1.",
                   "source_checked", {"areas": ["dna-genomes"]}, tp_sources,
                   [("system", cfg[p]), ("assessment", protocols["throughput"]), ("data", subsets["all"])],
                   {"origin": "rewire_run", "execution_scope": "complete_selected_evaluation", "protocol": "Workload W1, batch size 1",
                    "version": b.commit, "eligible_count": 3893, "scored_count": w1["variants"],
                    "coverage": {"scored": w1["variants"], "eligible": 3893, "unit": "variants"},
                    "timing_seconds": {"w1_scoring_seconds": w1["scoring_seconds"]},
                    "peak_memory": f"{w1['peak_memory_allocated_bytes']} bytes allocated (JSON pointer /results/w1/peak_memory_allocated_bytes)",
                    "inference_hardware": receipt_doc[p]["environment"]["gpu_name"],
                    "comparison": {**comparison("throughput", 3893, "zero-shot inference"), "metric_implementation": f"src/evo2ops/workloads.py; {ran_at}",
                                   "aggregation": "sequences scored divided by scoring seconds, one run"},
                    "limitations": tp_limits,
                    "source_locator": f"{b.sources[receipts[p]][0]}, JSON pointer /results/w1"})
        b.result(f"{P}-result-evo2-7b-{pslug}-scoring-throughput", f"Evo 2 7B on {label}: W1 sequences per second", "source_checked",
                 tp_sources, ev, receipts[p], "/results/w1/sequences_per_second", "inference-throughput", "higher", "sample-per-second",
                 "Read from the run receipt of this platform, which is the full W1 workload. One run; no interval. "
                 "Source checked, not marked reproduced: no run recipe names the receipt." +
                 (f" The study's repeat on another L40S host measured {l40s_repeat}." if p == "P5" else ""),
                 extra={"unit_detail": "8,192 bp sequences per second", "hardware": receipt_doc[p]["environment"]["gpu_name"],
                        "limitations": tp_limits})
        count["source_checked"] += 1

    kinds = {}
    for r in b.records:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    assert kinds == {"source": 11, "benchmark": 1, "dataset_subset": 4, "protocol": 5, "configuration": 9, "evaluation": 31, "result": 31}, kinds
    assert count == {"source_checked": 31}, count
    # No record is marked reproduced and none carries a run recipe, so no receipt is a recipe's
    # validation receipt and the board cannot badge a result of this batch as reproduced.
    assert all(r["status"] == "source_checked" and "run_recipes" not in r["attributes"] for r in b.records)
    all_receipts = set(receipts.values()) | {S_REPRO_P5}
    by_id = {r["id"]: r for r in b.records}
    for r in b.records:
        if r["kind"] == "result":
            ev = by_id[r["links"][0]["target_id"]]
            assert ev["status"] == r["status"] and ev["source_ids"] == r["source_ids"], r["id"]
            # A receipt is cited only by a result whose value is read from it (throughput).
            own = [s for s in r["source_ids"] if s in all_receipts and r["attributes"]["source_locator"].startswith(b.sources[s][0])]
            assert bool(own) == (r["attributes"]["metric"] == "inference-throughput"), r["id"]
            assert (S_REPRO_P5 in r["source_ids"]) == (r["id"] == f"{P}-result-evo2-7b-runpod-l40s-scoring-throughput"), r["id"]
            assert (S_REPRO_P5 not in r["source_ids"]) or any(l40s_repeat in t for t in r["attributes"]["limitations"]), r["id"]
    return b


# ---------------------------------------------------------------------------------------------
# amp-2026-studies / rare-disease-v2
# ---------------------------------------------------------------------------------------------

def rdv2(root):
    b = Batch("rdv2", root)
    P = "rewire-local-20261121-rdv2"
    D = "rare-disease-v2"
    areas = {"areas": ["dna-genomes"], "contexts": ["clinical_research"]}
    mit = {"licence": "MIT (repository LICENSE)"}
    studies = {
        "replication": ("500 replication SNV cases, 50 new people", "replication-500"),
        "snv": ("200 SNV cases, the first run's 50 people", "snv-200"),
        "indel": ("120 indel cases, the first run's 50 people", "indel-120"),
    }
    docs = {s: load(root, f"{D}/results/{s}_main.json") for s in studies}
    S = {s: b.source(f"{P}-source-results-{slug_}", f"{D}/results/{s}_main.json",
                     f"rare-disease-v2: results/{s}_main.json",
                     f"Result file of case_benchmark.py for the {label} under the main filters: top 1, top 5 and top 10 per score with bootstrap intervals, contrasts and checks.",
                     "rewire_execution_report", mit) for s, (label, slug_) in studies.items()}
    S_PROTO = b.source(f"{P}-source-protocol", f"{D}/PROTOCOL.md", "rare-disease-v2: PROTOCOL.md",
                       "Study protocol: case design, filters, scores, baselines, analysis rule, Evo 2 section and deviation log.",
                       "study_protocol", mit)
    S_ALL1KG = b.source(f"{P}-source-results-snv-all1kg", f"{D}/results/snv_all1kg.json", "rare-disease-v2: results/snv_all1kg.json",
                        "Result file for the 200 SNV cases with all of 1000 Genomes left out of the background frequencies; holds the one gnomAD split check that flags a gain.",
                        "rewire_execution_report", mit)
    readme_rel = f"{D}/README.md"
    readme = (root / readme_rel).read_text()
    limit_text = "**gnomAD presence is only partly fixed.**"
    assert limit_text in readme
    flag = pointer(load(root, f"{D}/results/snv_all1kg.json"), "/gnomad_split/difference/Rule + AVI minus Rule-based/possibly_gnomad_presence")
    assert flag is True
    for s in studies:
        for contrast in docs[s]["gnomad_split"]["difference"].values():
            assert contrast["possibly_gnomad_presence"] is False
    # The split check tests two contrasts per SNV analysis, both gains from AVI, and none on the indels.
    assert set(docs["replication"]["gnomad_split"]["difference"]) == {"Lookups + AVI (locked) minus Lookups combined (locked)", "Rule + AVI minus Rule-based"}
    assert set(docs["snv"]["gnomad_split"]["difference"]) == {"Lookups + AVI minus Lookups combined", "Rule + AVI minus Rule-based"}
    assert set(load(root, f"{D}/results/snv_all1kg.json")["gnomad_split"]["difference"]) == set(docs["snv"]["gnomad_split"]["difference"])
    assert docs["indel"]["gnomad_split"]["difference"] == {}
    S_ANALYSIS = b.source(f"{P}-source-analysis-snv-indel", f"{D}/results/analysis_snv_indel.md", "rare-disease-v2: results/analysis_snv_indel.md",
                          "Write-up of the 200 SNV and 120 indel cases, including the gnomAD split check in each analysis.", "study_report", mit)
    analysis_needle = "On the 200, the all1kg check flags the key secondary gain as possibly due to gnomAD presence"
    assert analysis_needle in (root / f"{D}/results/analysis_snv_indel.md").read_text()
    S_README = b.source(f"{P}-source-readme", readme_rel, "rare-disease-v2: README.md",
                        "Study README: status, findings, limits and how to rerun.", "study_readme", mit)

    # Evo 2 scores: which run produced the score each case set uses (evo2/select_variants.py and case_benchmark.py:
    # a reused first-run score wins, and among the first run's files the first in sorted order with the key wins).
    def table(rel):
        with open(root / rel) as handle:
            return list(csv.DictReader(handle, delimiter="\t"))

    def key(row):
        return (row["chrom"], row["pos"], row["ref"], row["alt"])

    runs = {
        "run2": (f"{D}/evo2/run2/scores.tsv", f"{D}/evo2/run2/receipt.json", "this study's run of 2 November 2026 (rare-disease-v2/evo2/run2)"),
        "run": ("rare-disease/evo2/run/scores.tsv", "rare-disease/evo2/run/receipt.json", "the first study's run of 16 to 17 October 2026 (rare-disease/evo2/run)"),
        "run-extra": ("rare-disease/evo2/run/scores_extra.tsv", "rare-disease/evo2/run/receipt_extra.json", "the first study's second job of 16 October 2026 (rare-disease/evo2/run, scores_extra.tsv)"),
        "run3": ("rare-disease/evo2/run3/scores.tsv", "rare-disease/evo2/run3/receipt.json", "the first study's run of 19 October 2026 (rare-disease/evo2/run3)"),
    }
    scores = {name: {key(r): r for r in table(rel)} for name, (rel, _, _) in runs.items()}
    reused = {key(r): r for r in table(f"{D}/evo2/run1_v1/scores.tsv")}
    RECEIPTS = {}
    for name, (rel, receipt_rel, label) in runs.items():
        doc = load(root, receipt_rel)
        assert doc["status"] == "completed" and doc["variant_windows"] == len(scores[name]), name
        RECEIPTS[name] = b.source(
            f"{P}-receipt-evo2-{name}", receipt_rel, f"Evo 2 7B scoring run receipt: {label}",
            f"Receipt written on the pod for an Evo 2 7B scoring run on one {doc['gpu_name']}: numerics, {doc['windows_scored_this_run']} windows scored "
            f"for {doc['variant_windows']} variants, timings and peak memory. It covers the scoring of those variants, not the ranking analysis.",
            "rewire_run_receipt", {**mit, "source_locator": "JSON pointers /status, /gpu_name, /variant_windows and /windows_scored_this_run"})
    origin = {}
    for s in studies:
        diagnostics = {key(r) for r in table(f"{D}/data/{s}/cases.tsv") if r["diagnostic"] == "1"}
        assert len(diagnostics) == docs[s]["cases"], s
        tally = {name: [0, 0] for name in runs}
        # case_benchmark.py ranks a diagnostic among variants of its own type only: SNVs on the 500 and
        # the 200, indels on the 120 (variants_after_dropping_other_type). A run that scored only the
        # other type supplied no ranked score, so its receipt is not cited on that case set.
        ranked_snv = s != "indel"
        assert all((len(k[2]) == 1 and len(k[3]) == 1) == ranked_snv for k in diagnostics), s
        for k in {key(r) for r in table(f"{D}/data/{s}/case_variants.tsv")}:
            if (len(k[2]) == 1 and len(k[3]) == 1) != ranked_snv:
                continue
            if k in reused:
                name = next(n for n in ("run", "run-extra", "run3") if k in scores[n])
                assert scores[name][k]["evo2_delta"] == reused[k]["evo2_delta"], k
            else:
                name = "run2"
                assert k in scores["run2"], k
            tally[name][0] += 1
            tally[name][1] += k in diagnostics
        assert sum(v[1] for v in tally.values()) == len(diagnostics), s
        origin[s] = tally
    assert origin == {"replication": {"run2": [6513, 481], "run": [700, 11], "run-extra": [0, 0], "run3": [8, 8]},
                      "snv": {"run2": [188, 188], "run": [7497, 0], "run-extra": [9, 9], "run3": [3, 3]},
                      "indel": {"run2": [107, 107], "run": [0, 0], "run-extra": [0, 0], "run3": [1064, 13]}}, origin
    assert docs["indel"]["filter"]["background_snvs_in_inheritance_count"] > 0 and "background_indels_in_inheritance_count" in docs["snv"]["filter"]

    def evo2_receipts(s):
        return [RECEIPTS[name] for name in runs if origin[s][name][0]]

    def evo2_note(s):
        parts = "; ".join(f"{runs[name][2]}: {n} case variants, {d} of them diagnostic" for name, (n, d) in origin[s].items() if n)
        return ("Evo 2 scores of this case set by the run that produced the score used (a reused first-run score wins over a rescored one): " + parts +
                ". Counts are over the case set's case variants of the type the analysis ranks (SNVs on the 500 and the 200, indels on the 120), "
                "before the frequency and inheritance filters; every diagnostic variant is ranked. "
                "Each cited receipt covers the scoring in its own run. No receipt covers the ranking analysis.")

    design_limit = ("gnomAD presence is only partly fixed (README.md, Limits): diagnostics keep their full gnomAD frequency by design and most are absent "
                    "from gnomAD, while background variants rarely are, so a score that learned gnomAD presence could pick the diagnostic for that reason.")
    limits = [
        design_limit,
        "Simulated cases: a ClinVar pathogenic variant is inserted into the rare variants of a 1000 Genomes person in the panel's genes. Lists are short and the people are not patients.",
        "One panel (PanelApp 285, intellectual disability). Consequence is taken over MANE Select transcripts only.",
        "ClinVar diagnostics were partly classified with the same lookup scores, which favours the lookups and both baselines.",
        "A run by the project with its own code. Evo 2 was added after every other result had been seen and is exploratory.",
    ]
    for needle in ("**Short lists.**", "**1000 Genomes people are not patients.**", "**Consequence over MANE Select only.**",
                   "**ClinVar diagnostics were partly classified with the same lookups.**", "**Evo 2 is exploratory.**"):
        assert needle in readme, needle

    BENCH = b.add(f"{P}-benchmark", "benchmark", "Rare-disease case tests, second run (Rewire, amp-2026-studies rare-disease-v2)",
                  "Rewire's own study: simulated rare-disease cases on the intellectual disability panel, ranking the inserted diagnostic variant among a person's rare variants by each score, baseline and combined model.",
                  "source_checked", areas, [S_PROTO, S_README, S_ANALYSIS, S_ALL1KG] + list(S.values()), [],
                  {"entity_level": "suite", "version": "amp-2026-v7", "task": "Rank the diagnostic variant first among a case's rare candidate variants",
                   "scope_note": "Main analyses of the three studies, stratum all. The filter checks (bg1pct, nomoi, all1kg, heldout, evee), the frequency sweep, the diagnostic-group strata and the paired contrasts are not ingested.",
                   "depth_tier": 1, "limitations": limits, "source_locator": f"{D}/PROTOCOL.md; {D}/README.md, Limits"})

    subsets, protocols = {}, {}
    for s, (label, slug_) in studies.items():
        d = docs[s]
        assert d["analysis"] == "main" and d["filter"]["max_af"] == "0.001" and d["filter"]["inheritance_filter"] is True
        assert d["strata"]["all"]["cases"] == d["cases"] and d["filter"]["cases_lost_diagnostic"] == 0
        assert "1000 resamples of people per stratum" in d["intervals"]
        rel = b.sources[S[s]][0]
        subsets[s] = b.add(f"{P}-dataset-{slug_}", "dataset_subset", f"rare-disease-v2 cases: {label}",
                           f"{d['cases']} simulated cases in {d['people']} people; median list of {d['median_variants_per_case']} variants per case after the main filters, diagnostic included.",
                           "source_checked", areas, [S[s], S_PROTO, S_README], [],
                           {"version": "amp-2026-v7", "eligible_count": d["cases"], "independent_groups": d["people"],
                            "limitations": limits[:4], "source_locator": f"{rel}, JSON pointers /cases, /people and /median_variants_per_case; {readme_rel}, Limits"})
        fitted = {"replication": "Combined models are either locked (fitted on the 200 SNV cases) or cross-validated on the 500, 5-fold by person.",
                  "snv": "Combined models are cross-validated, 5-fold by person.",
                  "indel": "Combined models are cross-validated, 5-fold by person."}[s]
        protocols[s] = b.add(f"{P}-protocol-{slug_}-main", "protocol", f"Diagnostic variant ranking, {label}, main filters (rare-disease-v2)",
                             "Share of cases in which the inserted diagnostic variant ranks first, in the top 5 or in the top 10 of the case's candidate list.",
                             "source_checked", areas, [S[s], S_PROTO, S_README], [("part_of", BENCH), ("uses_data", subsets[s])],
                             {"protocol": "Background and diagnostic grpmax below 0.1% (background with the person and family left out of gnomAD) and the background inheritance filter. "
                                          "A missing score ranks last. " + fitted,
                              "version": "amp-2026-v7", "bootstrap_replicates": 1000,
                              "uncertainty_reporting": {"definition": d["intervals"]},
                              "limitations": limits + (["The 200 and 120 results are cross-validated and descriptive; folds move a few points when lists change."] if s != "replication" else []),
                              "source_locator": f"{D}/PROTOCOL.md; {rel}, JSON pointers /filter, /fits and /intervals; {readme_rel}, Limits"})

    single = {
        "CADD": ("CADD v1.7 PHRED lookup", "CADD v1.7 PHRED score looked up for each variant.", "somatic-oncogenicity-20261009-method-cadd", "supervised_machine_learning", "1.7"),
        "SpliceAI": ("SpliceAI maximum delta score", "Largest of the four SpliceAI delta scores for each variant, from CADD's annotation for SNVs and from a SpliceAI 1.3.1 run for indels.", "discovery-model-spliceai", "supervised_machine_learning", None),
        "REVEL": ("REVEL v1.3 lookup", "REVEL v1.3 score for missense variants, maximum over transcripts.", "somatic-oncogenicity-20261009-method-revel", "supervised_machine_learning", "1.3"),
        "AlphaMissense": ("AlphaMissense lookup", "AlphaMissense pathogenicity for missense variants, maximum over transcripts.", "somatic-oncogenicity-20261009-method-alphamissense", "supervised_machine_learning", None),
        "AVI": ("AlphaGenome AVI lookup", "AlphaGenome Variant Impact score looked up for each SNV in the all-SNV table.", "ag-atlas-20261019-pipeline-avi", "foundation_model", None),
        "GPN-MSA": ("GPN-MSA lookup", "GPN-MSA hg38 score for each SNV, negated log-likelihood ratio.", "gfm-guides-20261014-gpnmsa-model-gpn-msa", "foundation_model", None),
        "GPN-Star-V": ("GPN-Star vertebrate lookup", "GPN-Star vertebrate (v100) score for each SNV, negated calibrated log-likelihood ratio.", "vep-uc-20261014-model-gpn-star", "foundation_model", "v100"),
        "GPN-Star-M": ("GPN-Star mammal lookup", "GPN-Star mammal (m447) score for each SNV, negated calibrated log-likelihood ratio.", "vep-uc-20261014-model-gpn-star", "foundation_model", "m447"),
        "Evo 2": ("Evo 2 7B zero-shot likelihood score, 8,192 bp window", "Evo 2 7B scores a variant as the mean log-likelihood of its 8,192 bp window minus that of the reference window, negated so that higher means more damaging.", "discovery-model-evo-2", "foundation_model", "evo2_7b"),
        "Rule-based": ("Rule-based ranking from ClinGen-calibrated thresholds", "Ranks variants by ACMG points assigned from ClinGen-calibrated thresholds of the lookup scores and the consequence, with ties broken by the tool for each level.", None, "conventional_pipeline", None),
        "Rule + AVI": ("Rule-based ranking with AVI as tie-breaker", "Ranks variants by the same ACMG points as the rule-based ranking, then by AVI, then by the rule's own tie-break.", None, "conventional_pipeline", None),
    }
    data_readme = (root / f"{D}/data/README.md").read_text()
    for needle in ("GPN-Star vertebrate (v100) and mammal (m447)", "SpliceAI 1.3.1", "`evo2_delta`"):
        assert needle in data_readme, needle
    proto = (root / f"{D}/PROTOCOL.md").read_text()
    for needle in ("CADD v1.7 PHRED", "REVEL v1.3", "Evo 2 7B scores every case variant"):
        assert needle in proto, needle
    evo2_scores = {"Evo 2"}
    cfg = {}

    def config(study, score):
        base = score.replace(" (locked)", "")
        locked = score.endswith("(locked)")
        if base in single:
            key = base
            if key in cfg:
                return cfg[key]
            name, desc, target, mtype, version = single[base]
            attrs = {"provenance_note": "Score as used by Rewire in the rare-disease-v2 case tests.",
                     "source_locator": f"{D}/PROTOCOL.md, section 6 (Scores), section 7 (rule-based baseline) and section 12 (Evo 2); {D}/data/README.md, Scores"}
            if version:
                attrs = {"version": version, **attrs}
            else:
                attrs["missing_metadata"] = {"version": {"reason": "unextracted", "note": "Not read from the pinned files for this batch."}}
            src = [S_PROTO] + (list(RECEIPTS.values()) if base == "Evo 2" else [])
            cfg[key] = b.add(f"{P}-configuration-{slug(base)}", "configuration", name, desc, "source_checked",
                             {**areas, "method_types": [mtype]}, src, [("configuration_of", target)] if target else [], attrs)
            return cfg[key]
        fit = "locked" if locked else f"cv-{studies[study][1]}"
        key = (base, fit)
        if key in cfg:
            return cfg[key]
        added = base.replace("Lookups combined", "").replace("Lookups + ", "")
        what = "the lookup scores" + (f" and {added}" if added else "")
        how = ("fitted once on the 200 SNV cases under the main filters and then locked" if locked else
               f"fitted by 5-fold cross-validation grouped by person on the {studies[study][0]}")
        mtypes = ["supervised_machine_learning"] + (["foundation_model"] if added else [])
        src = [S[study], S_PROTO] + ((evo2_receipts("snv") if locked else evo2_receipts(study)) if added == "Evo 2" else [])
        if added == "Evo 2":
            evo2_scores.add(score)
        cfg[key] = b.add(f"{P}-configuration-{slug(base)}-{fit}", "configuration",
                         f"{base}, {'locked' if locked else 'cross-validated on the ' + studies[study][0]}",
                         f"Combined model over {what} within each variant class, {how}.", "source_checked",
                         {**areas, "method_types": mtypes}, src, [],
                         {"training_setting": how, "provenance_note": "Combined model built by Rewire for the rare-disease-v2 case tests.",
                          "source_locator": f"{b.sources[S[study]][0]}, JSON pointers /fits and /model_classes; {D}/PROTOCOL.md, section 7",
                          "missing_metadata": {"version": {"reason": "inapplicable", "note": "A model fitted inside the study; it has no released version."}}})
        return cfg[key]

    expected = {"replication": 23, "snv": 17, "indel": 5}
    evaluations = {}
    for s, (label, slug_) in studies.items():
        d = docs[s]
        rel = b.sources[S[s]][0]
        scores = d["strata"]["all"]["scores"]
        assert len(scores) == expected[s], (s, len(scores))
        for score in scores:
            c = config(s, score)
            is_evo2 = score.replace(" (locked)", "") in ("Evo 2", "Lookups + Evo 2")
            sources = [S[s]] + (evo2_receipts(s) if is_evo2 else [])
            cases = d["cases"]
            attrs = {"origin": "rewire_run", "execution_scope": "complete_selected_evaluation",
                     "protocol": "Main filters; stratum all; top 1, top 5 and top 10 of the diagnostic variant in each case's list",
                     "version": "amp-2026-v7", "eligible_count": cases, "independent_groups": d["people"]}
            if score in d["coverage"]:
                attrs["coverage"] = {"scored": d["coverage"][score]["diagnostics"], "eligible": cases, "unit": "cases whose diagnostic variant has a score",
                                     "note": "A missing score ranks last; every case is counted in the result."}
            locked, fitted_here = score.endswith("(locked)"), score.startswith("Lookups") and not score.endswith("(locked)")
            assert "cross-validated (5-fold by person)" in d["fits"]
            assert ("locked: fitted on the 200 SNV cases under the main filters" in d["fits"]) == (s == "replication")
            assert not locked or s == "replication"
            split = ("locked: fitted on the 200 SNV cases under the main filters and applied unchanged to these cases; no fitting on these cases" if locked else
                     "cross-validated on these cases, 5-fold by person" if fitted_here else
                     "none; nothing is fitted on these cases")
            attrs["comparison"] = {"protocol_id": protocols[s], "dataset_version": subsets[s], "split": split,
                                   "population": f"{cases}/{cases}", "inputs": "the lookup or model score of each candidate variant",
                                   "adaptation": ("locked model fitted on the 200 SNV cases" if score.endswith("(locked)") else
                                                  "cross-validated combined model" if score.startswith("Lookups") else "none; score used as published"),
                                   "metric_implementation": "rare-disease-v2/case_benchmark.py at the pinned commit",
                                   "aggregation": "share of cases; stratum all", "budget": "one analysis run"}
            if is_evo2:
                attrs["reproduction_note"] = evo2_note(s)
            attrs["source_locator"] = f"{rel}, JSON pointer /strata/all/scores/{score}"
            ev = b.add(f"{P}-evaluation-{slug(score)}-{slug_}", "evaluation", f"{score} on the {label} (rare-disease-v2, main filters)",
                       f"Rank of the inserted diagnostic variant in each of {cases} simulated cases.", "source_checked",
                       {"areas": ["dna-genomes"]}, sources, [("system", c), ("assessment", protocols[s]), ("data", subsets[s])], attrs)
            evaluations[(s, score)] = ev
            for k in (1, 5, 10):
                base = f"/strata/all/scores/{score}/top_{k}"
                b.result(f"{P}-result-{slug(score)}-{slug_}-top-{k}", f"{score} on the {label}: top {k}", "source_checked", sources, ev,
                         S[s], base, f"top-{k}-accuracy", "higher", "fraction",
                         "Computed by Rewire's case_benchmark.py. No full-protocol run receipt exists for this analysis." +
                         (" The cited Evo 2 receipts cover the scoring runs only; see the evaluation's reproduction_note." if is_evo2 else ""),
                         ci=base + "_ci95", resamples=1000, ci_scope="bootstrap over people",
                         extra={"metric_qualifier": "diagnostic variant rank, stratum all, main filters",
                                "unit_detail": "fraction of cases", "eligible_count": cases})

    # The README's limit, as a concern scoped to the one evaluation whose gain a gnomAD split check flags.
    readme_source = S_README
    sha = b.sources[readme_source][1]
    split = docs["snv"]["gnomad_split"]
    name = "Rule + AVI minus Rule-based"
    absent, found, diff = split["gnomad: absent"]["contrasts"][name], split["gnomad: found"]["contrasts"][name], split["difference"][name]
    assert (absent["top_1"], absent["top_1_ci95"], found["top_1"], diff["top_1_absent_minus_found"], diff["top_1_ci95"]) == \
        ("0.0608", ["0.0195", "0.1149"], "0.0", "0.0608", ["-0.0063", "0.1377"])
    by_id = {r["id"]: r for r in b.records}
    by_id[readme_source]["attributes"]["evidence_concerns"] = [{
        "source_id": readme_source,
        "message": ("gnomAD presence is only partly fixed. Diagnostics keep their full gnomAD frequency and most are absent from gnomAD (148 of the 200, 386 of the 500), "
                    "while background variants rarely are. The study's split check flags the gain of Rule + AVI over the rule-based ranking on the 200 SNV cases as possibly "
                    "due to gnomAD presence in the all1kg check (results/snv_all1kg.json). In the main analysis the same gain is 0.0608 (0.0195 to 0.1149) in cases whose "
                    "diagnostic is absent from gnomAD and 0.0 in cases where it is found; the difference, 0.0608 (-0.0063 to 0.1377), is not flagged. The split check tests two "
                    "gains per SNV analysis, both from adding AVI (to the rule-based ranking and to the combined lookups), and none on the indel cases. The other "
                    "tested gain is not flagged on the 200 or the 500. No other score was tested, so for GPN-MSA, GPN-Star, Evo 2, the single lookups and the "
                    "combined models the limit is untested, not cleared. It is recorded in each protocol's limitations."),
        "source_locator": (f"{readme_rel}, Limits, bullet 'gnomAD presence is only partly fixed'; {D}/results/snv_all1kg.json, "
                           "JSON pointer /gnomad_split/difference/Rule + AVI minus Rule-based/possibly_gnomad_presence (true); "
                           f"{D}/results/snv_main.json, JSON pointers /gnomad_split/gnomad: absent/contrasts/Rule + AVI minus Rule-based, "
                           "/gnomad_split/gnomad: found/contrasts/Rule + AVI minus Rule-based and /gnomad_split/difference/Rule + AVI minus Rule-based; "
                           f"{D}/results/analysis_snv_indel.md, gnomAD split, bullet 'Key secondary'"),
        "artifact_sha256": sha,
        "review_date": DAY,
        "applies_to": [evaluations[("snv", "Rule + AVI")]],
    }]
    assert docs["snv"]["gnomad_split"]["diagnostics_absent"] == 148 and docs["replication"]["gnomad_split"]["diagnostics_absent"] == 386

    kinds = {}
    for r in b.records:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    assert kinds == {"source": 11, "benchmark": 1, "dataset_subset": 3, "protocol": 3, "configuration": 31, "evaluation": 45, "result": 135}, kinds
    assert all(r["status"] == "source_checked" for r in b.records)
    cites = {name: sum(1 for r in b.records if r["kind"] in ("evaluation", "result") and RECEIPTS[name] in r["source_ids"]) for name in runs}
    # 7 Evo 2 evaluations and their 21 results: 3 on the 500 (one locked), 2 on the 200, 2 on the 120
    # The first study's run scored SNVs only, so it is not cited on the 120 indel cases (5 evaluations, 20 records).
    assert cites == {"run2": 28, "run": 20, "run-extra": 8, "run3": 28}, cites
    indel_ids = [r for r in b.records if r["id"].endswith("-indel-120") or "-indel-120-top-" in r["id"]]
    assert indel_ids and not any(RECEIPTS["run"] in r["source_ids"] for r in indel_ids)
    return b


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--check"]
    study, root, out = args[0], Path(args[1]), Path(args[2])
    batch = {"evo2ops": evo2ops, "rdv2": rdv2}[study](root)
    batch.verify()
    text = batch.lines()
    target = out / "batch.jsonl"
    if "--check" in sys.argv:
        assert target.read_text() == text, "batch.jsonl differs from a rebuild"
        print(f"{len(batch.records)} records rebuilt and equal to {target}")
    else:
        out.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        print(f"{len(batch.records)} records written to {target}")
