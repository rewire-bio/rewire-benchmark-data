"""Independent review of the Buzkova et al. 2026 batch (2026-10-11).

Usage: python3 -I review/review.py <pdftotext -layout text of the pinned PDF>

Parses Tables 2, 3, 7 and 10 from the text layer with its own row and column matching (it does
not import extract/extract.py), checks every result and claim against the printed cells, applies
the corrections listed in review.md, and writes the reviewed records back to batch.jsonl.
Run it once, after extract/extract.py; it refuses to run on an already reviewed batch.
"""
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
P = "gfm2-20261011-buzkova2026-"
TEXT_SHA = "e1a2027c0ac0f6ac14306635cc5f2301b248eecd1f5b0dcf24a142fed9a2f5ac"
PDF_SHA = "9a589a2088f8466502b1035228db3e594065e984e5755c25d907471225f75c19"
URL = "https://www.biorxiv.org/content/10.64898/2026.09.25.754388v1.full.pdf"
DATE = "2026-10-11"
REVIEWER_NOTE = "Claude (Opus 5.5) review agent reviewer-gfm-a, independent of the extractor lit-gfm-2; no human review claimed"
METHOD_NOTE = ("Re-downloaded the bioRxiv PDF (byte stream differs per request in the preprint banner; the text layer is "
               "identical) and matched the archived copy to the pinned SHA-256. Parsed the table from the "
               "`pdftotext -layout` text with a separate parser (review/review.py) and checked printed value, numeric value, "
               "metric, qualifier, unit, direction, locator and the linked configuration, protocol and dataset against the "
               "row and column headers and Sections 2 and 3.")

text_path = Path(sys.argv[1])
raw = text_path.read_bytes()
assert hashlib.sha256(raw).hexdigest() == TEXT_SHA, "text layer hash mismatch"
lines = raw.decode("utf-8").splitlines()


def block(start, end):
    i = next(n for n, l in enumerate(lines) if l.strip().startswith(start))
    j = next(n for n in range(i + 1, len(lines)) if lines[n].strip().startswith(end))
    return lines[i:j]


records = [json.loads(l) for l in (HERE / "batch.jsonl").read_text().splitlines()]
by_id = {r["id"]: r for r in records}
assert all(r["status"] == "needs_review" for r in records), "batch already reviewed"
assert len(records) == 192

# ---- Expected cells, parsed independently -------------------------------------------------
cells = {}  # (table, row, column) -> printed string

MODELS = ["NTv1", "NTv2-50M", "NTv2-250M", "NTv2-500M", "NTv3-8M", "NTv3-100M", "NTv3-650M", "DNABERT-2", "DNABERT-S"]
t3 = block("Table 3. Accuracy for all models", "3.2 Taxonomic ambiguity")
T3_ROWS = {"Mean, all": "Mean, all tokens", "Mean, special": "Mean, special tokens excluded",
           "Max, all": "Max, all tokens", "Max, special": "Max, special tokens excluded", "CLS token": "CLS token only"}
for l in t3:
    s = l.strip()
    for prefix, label in T3_ROWS.items():
        if s.startswith(prefix):
            vals = re.findall(r"⋆?0\.\d{4}|—", s)
            assert len(vals) == 9, s
            for m, v in zip(MODELS, vals):
                if v != "—":
                    cells[("Table 3", label, m)] = v
assert len(cells) == 36  # 6 models x 5 poolings + 3 NTv3 x 2

t7 = block("Table 7. Comparison of BLAST", "3.7 Robustness")
for l in t7:
    m = re.match(r"\s*(40|33) classes\s+(blastn|megablast|NTv3-650M \(max\))\s+(0\.\d{4})\s+(0\.\d{4})\s+(0\.\d{4})\s+(0\.\d{4})\s*$", l)
    if m:
        for col, v in zip(["Accuracy", "F1", "Precision", "Recall"], m.groups()[2:]):
            cells[("Table 7", f"{m.group(1)} classes / {m.group(2)}", col)] = v
assert sum(1 for k in cells if k[0] == "Table 7") == 24

t10 = block("Table 10. Classification results", "4. Discussion")
for l in t10:
    m = re.match(r"\s*(DNABERT-2ᵃ|NTv2-50Mᵃ|NTv2-250Mᵃ|NTv3-650M|BLAST \(blastn\))\s+" + r"\s+".join([r"(0\.\d{4})"] * 6) + r"\s*$", l)
    if m:
        for col, v in zip(["Accuracy", "Bal. Acc.", "MCC", "F1", "Precision", "Recall"], m.groups()[1:]):
            cells[("Table 10", m.group(1), col)] = v
assert sum(1 for k in cells if k[0] == "Table 10") == 30

t2 = block("Table 2. Overview of the evaluated models", "2.4 Embedding generation")
t2rows = {}
for l in t2:
    m = re.match(r"\s*(NTv1 \(Multispecies 2\.5B\)|NTv[23]-\d+M|DNABERT-[2S])\s{2,}(\S+)\s{2,}(.+?)\s{2,}(.+?)\s{2,}(.+?)\s*$", l)
    if m:
        t2rows[m.group(1)] = [g.strip() for g in m.groups()[1:]]
assert len(t2rows) == 9, t2rows.keys()

# Wilson intervals printed in the text (Sections 3.6 and 3.8).
para36 = " ".join(block("3.6 Comparison with BLAST", "Figure 5.")).split()
para38 = " ".join(block("3.8 Long sequences", "Figure 7.")).split()
p36, p38 = " ".join(para36), " ".join(para38)
assert "(blastn 0.962 to 0.972, NTv3-650M 0.919 to 0.933, megablast 0.891 to 0.907)" in p36
assert "(NTv3-650M 0.920 to 0.973, blastn 0.950 to 0.989)" in p38
assert "95% Wilson binomial confidence intervals" in " ".join(" ".join(block("2.9 Evaluation metrics", "2.10")).split())
CI = {
    "result-t7-33-blastn-accuracy": ("0.962", "0.972", "Section 3.6, paragraph 1"),
    "result-t7-33-ntv3-650m-max-accuracy": ("0.919", "0.933", "Section 3.6, paragraph 1"),
    "result-t7-33-megablast-accuracy": ("0.891", "0.907", "Section 3.6, paragraph 1"),
    "result-t10-ntv3-650m-accuracy": ("0.920", "0.973", "Section 3.8"),
    "result-t10-blastn-accuracy": ("0.950", "0.989", "Section 3.8"),
}

# The pooling used for the long-sequence experiment is not stated anywhere in the text.
long_text = " ".join(" ".join(block("2.5 Long-sequence handling", "2.6 Dimensionality")).split()) + " " + p38
assert not re.search(r"(mean|max|CLS)[- ]pool", long_text, re.I)

# ---- Check every result ----------------------------------------------------------------------
METRIC = {"Accuracy": "accuracy", "F1": "macro-f1", "Precision": "precision", "Recall": "recall",
          "Bal. Acc.": "balanced-accuracy", "MCC": "matthews-correlation-coefficient"}
POOL = {"Mean, all tokens": "mean-all", "Mean, special tokens excluded": "mean-excl", "Max, all tokens": "max-all",
        "Max, special tokens excluded": "max-excl", "CLS token only": "cls"}
T7SYS = {"blastn": "config-blastn", "megablast": "config-megablast", "NTv3-650M (max)": "config-ntv3-650m-max-all"}
T10KEY = {"DNABERT-2ᵃ": "dnabert-2", "NTv2-50Mᵃ": "ntv2-50m", "NTv2-250Mᵃ": "ntv2-250m", "NTv3-650M": "ntv3-650m", "BLAST (blastn)": "blastn"}


def links(r):
    return {l["relation"]: l["target_id"].removeprefix(P) for l in r["links"]}


checked = []
for r in records:
    if r["kind"] != "result":
        continue
    a = r["attributes"]
    loc = a["source_locator"]
    if loc.startswith("Table 3"):
        m = re.fullmatch(r"Table 3, column '(.+)', row '(.+)'", loc)
        key = ("Table 3", m.group(2), m.group(1))
        metric, qual = "accuracy", "33-class RVDB dataset, 1-NN over frozen embeddings"
        sysid = f"config-{m.group(1).lower()}-{POOL[m.group(2)]}"
        proto, data = "protocol-acc-33", "data-rvdb-33"
    else:
        m = re.fullmatch(r"(Table 7|Table 10), row '(.+)', column '(.+)'", loc)
        key = (m.group(1), m.group(2), m.group(3))
        metric = METRIC[m.group(3)]
        if m.group(1) == "Table 7":
            classes, label = m.group(2).split(" classes / ")
            qual = f"{classes}-class RVDB dataset"
            sysid, proto, data = T7SYS[label], "protocol-blast-compare", f"data-rvdb-{classes}"
        else:
            chunked = m.group(2).endswith("ᵃ")
            qual = "16-class long-sequence RVDB dataset" + (", chunk-scored" if chunked else "")
            k = T10KEY[m.group(2)]
            sysid = "config-blastn" if k == "blastn" else None  # FM configurations checked below
            proto, data = "protocol-long", "data-rvdb-long"
    printed = cells[key]
    assert a["printed_value"] == printed, (r["id"], a["printed_value"], printed)
    assert a["numeric_value"] == printed.replace("⋆", ""), r["id"]
    assert a["metric"] == metric, (r["id"], a["metric"])
    assert a["metric_direction"] == "higher"
    assert a["unit"] == ("unitless" if metric == "matthews-correlation-coefficient" else "fraction"), r["id"]
    ev = by_id[r["links"][0]["target_id"]]
    el = links(ev)
    assert el["assessment"] == proto and el["data"] == data, (r["id"], el)
    if sysid:
        assert el["system"] == sysid, (r["id"], el["system"], sysid)
    if metric in ("precision", "recall"):
        assert a["metric_qualifier"] == "macro-averaged over classes", r["id"]
    else:
        assert a["metric_qualifier"] == qual, (r["id"], a["metric_qualifier"], qual)
    assert a["missing_metadata"] == {"uncertainty": {"reason": "unreported"}}, r["id"]
    checked.append((r["id"], key, printed))
assert len(checked) == 90 and len({c[1] for c in checked}) == 90

# Claims against Table 2.
for r in records:
    if r["kind"] != "claim":
        continue
    name = re.fullmatch(r"Table 2, row '(.+)'", r["attributes"]["source_locator"]).group(1)
    params, ctx, tok, data = t2rows[name]
    ctx = ctx.replace("flex.ᵃ", "flex.").replace("; flex.", "; flex.")
    data = data.rstrip("ᵇ")
    expect = f"{name}: {params} parameters; context {ctx}; tokenizer {tok}; training data {data}"
    assert r["attributes"]["value"] == expect, (r["id"], r["attributes"]["value"], expect)

# ---- Corrections ---------------------------------------------------------------------------
corrections = []

# 1. Printed 95% Wilson intervals were recorded as unreported.
for rid, (lo, hi, where) in CI.items():
    a = by_id[P + rid]["attributes"]
    del a["missing_metadata"]
    a["uncertainty"] = {"type": "confidence_interval", "printed": f"{lo} to {hi}", "lower": lo, "upper": hi,
                        "level": 0.95, "method": "analytic",
                        "note": f"Wilson binomial interval quoted in {where}; method stated in Section 2.9"}
    corrections.append((P + rid, f"uncertainty changed from unreported to the 95% Wilson interval {lo} to {hi} ({where})"))

# 2. Precision and recall qualifiers dropped the dataset and the chunk-scored marker that the
#    other four metrics of the same row carry.
for r in records:
    a = r.get("attributes", {})
    if r["kind"] == "result" and a.get("metric") in ("precision", "recall"):
        loc = a["source_locator"]
        if loc.startswith("Table 7"):
            ds = f"{loc.split(chr(39))[1].split(' classes')[0]}-class RVDB dataset"
        else:
            ds = "16-class long-sequence RVDB dataset" + (", chunk-scored" if "ᵃ" in loc else "")
        old = a["metric_qualifier"]
        a["metric_qualifier"] = f"{ds}, macro-averaged over classes"
        corrections.append((r["id"], f"metric_qualifier changed from '{old}' to '{a['metric_qualifier']}'"))

# 3. Table 10 foundation-model rows were linked to the Table 3 best-pooling configurations, but the
#    paper does not state which pooling the long-sequence runs used. Give them their own
#    configurations with pooling marked unreported.
LONG = {"dnabert-2": ("config-dnabert-2-mean-all", "DNABERT-2", "overlapping 1,200-token chunks with 250-token overlap, scored per chunk"),
        "ntv2-50m": ("config-ntv2-50m-mean-all", "NTv2-50M", "overlapping 2,046-token chunks with 250-token overlap, scored per chunk"),
        "ntv2-250m": ("config-ntv2-250m-mean-all", "NTv2-250M", "overlapping 2,046-token chunks with 250-token overlap, scored per chunk"),
        "ntv3-650m": ("config-ntv3-650m-max-all", "NTv3-650M", "whole sequence in one pass, no chunking")}
new_records = []
for key, (old_cfg, label, handling) in LONG.items():
    if key == "ntv3-650m":
        old_cfg = "config-ntv3-650m-mean-all"  # template only; parameters are shared across pooling
    tmpl = by_id[P + old_cfg]
    cfg = copy.deepcopy(tmpl)
    cfg["id"] = f"{P}config-{key}-long-pooling-unreported"
    cfg["name"] = f"{label}, frozen embeddings, pooling not stated, 1-NN, long-sequence run (Bůžková et al. 2026)"
    cfg["description"] = f"{cfg['name']}, as evaluated in the cited comparison."
    ca = cfg["attributes"]
    ca["source_locator"] = f"Table 2 row '{tmpl['attributes']['reported_name']}'; Sections 2.3 and 2.5; Table 10 row '{label}'"
    ca["parameters"] = re.sub(r"; [^;]*pooling;", ";", ca["parameters"]) + f"; {handling}"
    ca["missing_metadata"] = {"representation": {"reason": "unreported",
                                                 "note": "Sections 2.5 and 3.8 and Table 10 do not say which token pooling the long-sequence run used"},
                              **ca["missing_metadata"]}  # keys in sorted order, as the attribute normaliser writes them
    new_records.append(cfg)
    ev = by_id[f"{P}eval-t10-{key}"]
    ev["links"] = [l if l["relation"] != "system" else {"relation": "system", "target_id": cfg["id"]} for l in ev["links"]]
    ev["attributes"]["comparison"]["adaptation"] = "None: frozen weights, pooling not stated, 1-NN over the indexed training embeddings"
    corrections.append((ev["id"], f"system changed from {P}{LONG[key][0]} to the new record {cfg['id']}, because the pooling used for Table 10 is not stated"))

# 4. Section 2.5 says chunk embeddings were pooled to one sequence-level representation, while
#    the Table 10 footnote and Section 4 say the chunked rows were scored per chunk.
CONFLICT = ("Section 2.5 says chunk embeddings were pooled to a sequence-level representation, but the Table 10 footnote "
            "and Section 4 (Methodological considerations) say these rows were scored over chunks; the scored unit is "
            "recorded as the footnote states.")
for key in ("dnabert-2", "ntv2-50m", "ntv2-250m"):
    ev = by_id[f"{P}eval-t10-{key}"]
    ev["attributes"]["limitations"].append(CONFLICT)
    corrections.append((ev["id"], "limitation added: Section 2.5 versus Table 10 footnote on chunk scoring"))
pl = by_id[P + "protocol-long"]["attributes"]["limitations"]
pl.append("Pooling for the long-sequence run is not stated; the foundation-model rows use configurations with pooling unreported.")
corrections.append((P + "protocol-long", "limitation added: pooling not stated"))
for pid in ("protocol-acc-33", "protocol-blast-compare"):
    by_id[P + pid]["attributes"]["limitations"].append(
        "ICTV reconciliation found one further redundant label pair still inside the 33-class dataset (Section 3.2; Section 4, Table 11).")
    corrections.append((P + pid, "limitation added: residual redundant label pair (Table 11)"))

# 5. Table 1 prints the long-sequence total as "about 320"; an exact integer overstates it.
dl = by_id[P + "data-rvdb-long"]["attributes"]
assert dl.pop("total") == 320
dl["missing_metadata"] = {"total": {"reason": "unreported", "note": "Table 1 prints 'about 320 (about 64 indexed, 256 queried)'"}}
corrections.append((P + "data-rvdb-long", "total 320 removed; Table 1 prints only 'about 320'"))

records.extend(new_records)
records.sort(key=lambda r: r["id"])

# ---- Review blocks and status --------------------------------------------------------------
NOTES = {
    P + "result-t3-ntv3-650m-max-all": "The printed cell carries the table's overall-best marker (⋆), kept in printed_value. "
    "Table 9's 0% mutation, 0% masking cell for NTv3-650M prints 0.9244, not 0.9265; Tables 3, 6 and 7 agree on 0.9265.",
    P + "result-t7-33-ntv3-650m-max-accuracy": "Tables 3, 6 (ratio 1.00) and 7 agree on 0.9265; Table 9's unperturbed cell prints 0.9244.",
    P + "result-t7-33-blastn-accuracy": "Matches Table 8's unperturbed cell (0.9677).",
}
for r in records:
    r["status"] = "source_checked"
    a = r["attributes"]
    if r["kind"] in ("result", "claim"):
        note = "Independent review 2026-10-11: value and identity match the source."
        if r["id"] in NOTES:
            note += " " + NOTES[r["id"]]
        fixes = [c[1] for c in corrections if c[0] == r["id"]]
        if fixes:
            note += " Corrected in review: " + "; ".join(fixes) + "."
        a["review"] = {"method": ["source-hash-verification", "pdf-text-parse", "independent-cell-check"],
                       "method_note": METHOD_NOTE, "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE,
                       "date": DATE, "artifact_sha256": PDF_SHA, "retrieval_url": URL,
                       "note": note}
    if r["kind"] == "source":
        a["review"] = {"method": ["source-hash-verification", "ai-assisted-source-review"], "reviewer": ["claude"],
                       "reviewer_note": REVIEWER_NOTE, "date": DATE,
                       "artifact_sha256": PDF_SHA, "retrieval_url": URL,
                       "note": "Archived copy matches the pinned SHA-256; licence CC BY 4.0 confirmed on the PDF banner."}

(HERE / "batch.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records))
(HERE / "review" / "corrections.json").write_text(json.dumps(corrections, ensure_ascii=False, indent=1) + "\n")
print(f"{len(checked)} results and 9 claims checked; {len(corrections)} corrections; {len(records)} records written")
