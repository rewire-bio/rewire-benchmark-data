"""One-off: turn the comparison settings pilot into curation files.

Usage: python3 kb/tools/import_pilot.py

Reads data/omics/comparison-settings-pilot-20261126/*.proposal.json. Writes kb/curation/settings.jsonl,
protocol_settings.jsonl and leads.jsonl. After this the curation files are edited directly. The
structured checkpoint facts are loaded by kb/curate.py from the records.
"""
import glob
import json
import os
import re


def dump(path, rows):
    with open(path, "w") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"{path}: {len(rows)}")


def main():
    settings, memberships, leads = [], [], []
    for path in sorted(glob.glob("data/omics/comparison-settings-pilot-20261126/*.proposal.json")):
        proposal = json.load(open(path))
        cluster = proposal["cluster"]
        for s in proposal["settings"]:
            sid = "setting-" + re.sub(r"[^a-z0-9]+", "-", s["key"].lower()).strip("-")
            settings.append({"id": sid, "name": s["name"], "definition": s["definition"], "cluster": cluster,
                             "task_id": s.get("existing_task_id"), "basis": "agent proposal 2026-11-26, not reviewed"})
            for p in s["protocols"]:
                memberships.append({"protocol_id": p["protocol_id"], "setting_id": sid, "grade": p["comparability"], "metric": p.get("metric"),
                                    "differences": p.get("differences") or "", "why": p.get("why") or "", "basis": "agent proposal 2026-11-26, not reviewed"})
        for n, d in enumerate(proposal.get("disagreements", []), 1):
            leads.append({"id": f"lead-{cluster}-{n:02d}", "setting_id": "setting-" + re.sub(r"[^a-z0-9]+", "-", d["setting"].lower()).strip("-"),
                          "kind": d["kind"], "model": d.get("model"), "model_id": d.get("model_id"), "metric": d.get("metric"),
                          "values": d.get("values", []), "note": d.get("note", ""), "state": "open", "basis": "agent proposal 2026-11-26, not reviewed"})
    dump("kb/curation/settings.jsonl", settings)
    dump("kb/curation/protocol_settings.jsonl", memberships)
    dump("kb/curation/leads.jsonl", leads)


if __name__ == "__main__":
    main()
