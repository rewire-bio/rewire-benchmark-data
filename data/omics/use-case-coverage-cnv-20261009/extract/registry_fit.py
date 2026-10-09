"""Fit the reviewed CNV batch to the declared attribute registry (issue #42, stage 3).

Usage: python3 -I registry_fit.py <batch.store.jsonl>   (rewrites the file in place)

Run after normalizeRecords and `attributes:migrate -- --batch`. Every move is to an
existing declared key; nothing is dropped except pmcid, which is already in the
source's version and artifact_url. Each change is printed for the log.
"""
import json
import sys

path = sys.argv[1]
rows = [json.loads(line) for line in open(path)]
log = []


def note(rec, what):
    log.append(f"- `{rec['id']}`: {what}")


def append(attrs, key, text):
    attrs[key] = (attrs.get(key) or []) + [text]


def scope(attrs, text):
    attrs["scope_note"] = f"{attrs['scope_note']} {text}" if attrs.get("scope_note") else text


for r in rows:
    a, mm = r["attributes"], r["attributes"].get("missing_metadata", {})
    if r["kind"] == "result" and "source_cell_text" in a:
        a["raw_xml_value"] = a.pop("source_cell_text")
    if r["kind"] == "source":
        if "pmcid" in a:
            note(r, f"dropped pmcid {a.pop('pmcid')} (already in version and artifact_url)")
        if "container_sha256" in a:
            c = a.pop("container_sha256")
            a["hash_scope"] = ("artifact_sha256 is the inner supplementary file. Containers: "
                               + "; ".join(f"{k} {v}" for k, v in c.items())
                               + ". The Europe PMC zip is rebuilt per request, so its hash describes one retrieval only.")
            note(r, "container_sha256 moved to hash_scope")
    if r["kind"] == "configuration" and "version_note" in a:
        a["model_identity_note"] = a.pop("version_note")
        note(r, "version_note moved to model_identity_note")
    if r["kind"] == "protocol" and "printed_label_note" in a:
        scope(a, a.pop("printed_label_note"))
        note(r, "printed_label_note moved to scope_note")
    if r["kind"] == "dataset" and "related_dataset" in a:
        scope(a, f"Same sample and truth set as {a.pop('related_dataset')}, which covers only the 1-5 kb bin.")
        note(r, "related_dataset moved to scope_note")
    moves = {
        "truth_counts": "denominator", "per_stratum_counts": "denominator",
        "scored_truth_count": "scored_count", "exact_depth": "population_detail",
        "inputs": "comparison.inputs", "dosage_direction": "metric_definition",
        "matching_parameters": "metric_implementation",
    }
    for old, new in moves.items():
        if old in mm:
            entry = mm.pop(old)
            if old == "inputs":
                entry = {**entry, "reason": "conflicting"}
            if old == "matching_parameters":
                entry = {**entry, "note": "witty.er v0.5.2 is named (Methods 2.4); its matching parameters are unreported"}
            mm[new] = entry
            note(r, f"missing_metadata.{old} moved to missing_metadata.{new}")
    if "aligner" in mm or "depth" in mm:
        parts = [mm.pop(k)["note"] for k in ("depth", "aligner") if k in mm]
        mm["population_detail"] = {"reason": "conflicting", "note": " ".join(x if x.endswith(".") else x + "." for x in parts)}
        note(r, "missing_metadata.depth and .aligner merged into population_detail (reason conflicting)")
    for old in ("origin_note", "sensitivity", "tool_versions", "printed_results"):
        if old in mm:
            append(a, "limitations", mm.pop(old)["note"])
            note(r, f"missing_metadata.{old} moved to limitations")
    if "per_caller_values" in mm:
        scope(a, mm.pop("per_caller_values")["note"] + ".")
        note(r, "missing_metadata.per_caller_values moved to scope_note")
    if "missing_metadata" in a:
        if a["missing_metadata"]:
            a["missing_metadata"] = dict(sorted(a["missing_metadata"].items()))
        else:
            del a["missing_metadata"]

open(path, "w").write("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in rows))
print("\n".join(log))
print(f"{len(log)} moves; results renamed source_cell_text to raw_xml_value")
