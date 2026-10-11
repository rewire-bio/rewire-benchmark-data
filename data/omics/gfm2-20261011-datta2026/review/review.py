"""Independent review of the Datta et al. 2026 batch (2026-10-11).

Usage: python3 -I review/review.py <pdftotext -layout text of the pinned PDF>

Parses Table 1 and Table 4 from the text layer with its own matching (it does not import
extract/extract.py), checks every result against the printed cells, checks each Table 1 recovery
percentage against the two extracted scores, applies the corrections listed in review.md and writes
the reviewed records back to batch.jsonl. Run it once, after extract/extract.py; it refuses to run
on an already reviewed batch.
"""
import hashlib
import json
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
P = "gfm2-20261011-datta2026-"
PDF_SHA = "df36e4772562329550c924004a546812c8d76149a1b5238e4d0b0cfa8a82bb5c"
TEXT_SHA = "b2458cdb3a338c1ec39021610df8229050a8082065fbe5489f0e16a443e4f401"
URL = "https://arxiv.org/pdf/2608.05329v1"
DATE = "2026-10-11"
REVIEWER_NOTE = "Claude (Opus 5.5) review agent reviewer-gfm-a, independent of the extractor lit-gfm-2; no human review claimed"
METHOD_NOTE = ("Re-downloaded the arXiv PDF and matched the pinned SHA-256. Parsed Table 1 from the `pdftotext -layout` "
               "(poppler 26.08.0) text with a separate parser (review/review.py) and checked printed value, numeric value, "
               "spread, metric (Section 3.2), qualifier, unit, direction, locator and the linked configuration, protocol and "
               "dataset; recomputed each cell's printed recovery from the two scores as a transcription check.")

raw = Path(sys.argv[1]).read_bytes()
assert hashlib.sha256(raw).hexdigest() == TEXT_SHA, "text layer hash mismatch"
lines = raw.decode("utf-8").splitlines()
records = [json.loads(l) for l in (HERE / "batch.jsonl").read_text().splitlines()]
by_id = {r["id"]: r for r in records}
assert all(r["status"] == "needs_review" for r in records), "batch already reviewed"
assert len(records) == 303

# ---- Table 1 -------------------------------------------------------------------------------
start = next(i for i, l in enumerate(lines) if l.startswith("Table 1: Main NT benchmark evaluation"))
end = next(i for i in range(start, len(lines)) if lines[i].startswith("Table 2: Genomic Benchmark"))
CELL = r"(\.\d{4})±(\.\d{4}) / (\.\d{3})(?:±(\.\d{3}))? / (\d+)"
COLS = ["HyenaDNA", "NT", "GENERATOR-v2", "Omni-DNA"]
KEY = {"HyenaDNA": "hyenadna", "NT": "nt", "GENERATOR-v2": "generator-v2", "Omni-DNA": "omni-dna"}
table = {}
for l in lines[start:end]:
    m = re.match(r"^(H3\S*|H4\S*|Enhancer Types|Enhancer|Promoter All|Promoter Non-TATA|Promoter TATA|Splice All|Splice Acceptor|Splice Donor)\s+(.*)$", l)
    if not m:
        continue
    cells = re.findall(CELL, m.group(2))
    assert len(cells) == 4, l
    table[m.group(1)] = dict(zip(COLS, cells))
assert len(table) == 18

MCC_TASKS = {t for t in table if t.startswith(("H3", "H4", "Enhancer"))}
assert len(MCC_TASKS) == 12


def dec(s):
    return "0" + s


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


# Recovery check: printed recovery against frozen / FT x 100, rounded half up.
recovery_mismatch = []
for task, row in table.items():
    for col, (fz, fzsd, ft, ftsd, rec) in row.items():
        calc = (Decimal(dec(fz)) / Decimal(dec(ft)) * 100).quantize(Decimal("1"), ROUND_HALF_UP)
        if abs(int(calc) - int(rec)) > 1:
            recovery_mismatch.append((task, col, rec, str(calc)))
assert recovery_mismatch == [], recovery_mismatch

# ---- Table 4, HyenaDNA validation-selected versus diagnostic grid-best ----------------------
t4s = next(i for i, l in enumerate(lines) if l.startswith("Table 4: Validation-selected versus diagnostic"))
t4 = {}
for l in lines[t4s:t4s + 20]:
    m = re.match(r"^\s*(H3|H4ac|Enhancer|Promoter All|Splice All|Splice Acceptor|Splice Donor)\s+(0\.\d{4}) ± (0\.\d{4})\s+(\S+)\s+(0\.\d{4}) ± (0\.\d{4})\s+(\S+)\s*$", l)
    if m:
        t4[m.group(1)] = m.groups()[1:]
assert len(t4) == 7, t4
t4_vs_t1 = {}
for task, (vs, vssd, vcfg, gb, gbsd, gcfg) in t4.items():
    fz, fzsd = dec(table[task]["HyenaDNA"][0]), dec(table[task]["HyenaDNA"][1])
    t4_vs_t1[task] = "grid-best" if (fz, fzsd) == (gb, gbsd) else "val-selected" if (fz, fzsd) == (vs, vssd) else "neither"
assert t4_vs_t1 == {"H3": "grid-best", "H4ac": "grid-best", "Enhancer": "grid-best", "Promoter All": "grid-best",
                    "Splice All": "grid-best", "Splice Acceptor": "neither", "Splice Donor": "val-selected"}, t4_vs_t1

# ---- Check every result ----------------------------------------------------------------------
checked = 0
for r in records:
    if r["kind"] != "result":
        continue
    a = r["attributes"]
    m = re.fullmatch(r"Table 1, row '(.+)', column '(.+)', (frozen|FT) value", a["source_locator"])
    task, col, which = m.groups()
    fz, fzsd, ft, ftsd, rec = table[task][col]
    printed, sd = (fz, fzsd) if which == "frozen" else (ft, ftsd)
    assert a["printed_value"] == printed and a["numeric_value"] == dec(printed), r["id"]
    mcc = task in MCC_TASKS
    assert a["metric"] == ("matthews-correlation-coefficient" if mcc else "f1-score"), r["id"]
    assert a["unit"] == ("unitless" if mcc else "fraction") and a["metric_direction"] == "higher", r["id"]
    assert a["metric_qualifier"] == ("frozen-embedding probe" if which == "frozen" else "reference fine-tuned score")
    if sd:
        u = a["uncertainty"]
        assert u["printed"] == "±" + sd and u["value"] == dec(sd), r["id"]
    else:
        assert a["missing_metadata"] == {"uncertainty": {"reason": "unreported"}}, r["id"]
    ev = by_id[r["links"][0]["target_id"]]
    kind = "frozen" if which == "frozen" else "ft"
    assert ev["id"] == f"{P}eval-{KEY[col]}-{slug(task)}-{kind}", (r["id"], ev["id"])
    el = {l["relation"]: l["target_id"] for l in ev["links"]}
    assert el["system"] == f"{P}config-{KEY[col]}-{kind}"
    assert el["assessment"] == P + ("protocol-frozen-probe" if kind == "frozen" else "protocol-fine-tuned-reference")
    assert el["data"] == P + "data-nt-benchmark"
    assert ev["attributes"]["comparison"]["metric_implementation"] == ("MCC" if mcc else "F1 score"), ev["id"]
    assert ev["attributes"]["origin"] == ("independent_paper" if kind == "frozen" else "unreported")
    checked += 1
assert checked == 144

# Section 2.2 model list.
body = " ".join(" ".join(lines).split())
for name in ["HyenaDNA (Nguyen et al., 2023)-436K", "GENERATOR-v2 (Wu et al., 2025)-1.2B", "Omni-DNA (Li et al., 2025)-116M"]:
    assert name in body, name
assert re.search(r"Nucleotide Transformer \(NT\) \(Dalla-Torre\s.*?et al\., 2025\)-500M", body)
assert "G = {mean, max, CLS, last, attn, top-k} ×" in body and "{LR, MLP}, with architecture-specific" in body  # two-column layout

# ---- Corrections ---------------------------------------------------------------------------
corrections = []

# 1. The FT spread is never defined. Section 3.3 defines only the frozen spread (SD over five
#    seeds); the FT values are benchmark- or model-reported.
for r in records:
    a = r["attributes"]
    if r["kind"] == "result" and a.get("uncertainty", {}).get("scope") == "As printed in the source":
        a["uncertainty"] = {"type": "unresolved_spread", "value": a["uncertainty"]["value"], "printed": a["uncertainty"]["printed"],
                            "note": "Table 1 does not define the spread on reference fine-tuned scores; Section 3.3 defines only the frozen-probe spread"}
        corrections.append((r["id"], "uncertainty type changed from standard_deviation to unresolved_spread"))

# 2. The qualifier did not name the task, so 18 tasks in one protocol shared one qualifier.
for r in records:
    a = r["attributes"]
    if r["kind"] == "result":
        task = re.fullmatch(r"Table 1, row '(.+?)', .*", a["source_locator"]).group(1)
        old = a["metric_qualifier"]
        a["metric_qualifier"] = f"NT benchmark {task}, {old}"
        corrections.append((r["id"], f"metric_qualifier changed from '{old}' to '{a['metric_qualifier']}'"))

# 3. The frozen protocol named an RBF-SVM probe, but the readout grid (Section 2.5) uses LR and MLP only.
pf = by_id[P + "protocol-frozen-probe"]["attributes"]
old = pf["protocol"]
pf["protocol"] = ("Extract a sequence embedding from the frozen backbone (gradients disabled), standardise with training-set "
                  "statistics, and train a logistic-regression or MLP probe on each readout of the grid {mean, max, CLS, last, "
                  "attn, top-k} x {LR, MLP} (Section 2.5); report the best configuration over the diagnostic test grid, as mean "
                  "and standard deviation over five seeds.")
assert old != pf["protocol"] and "RBF-SVM" in old
corrections.append((P + "protocol-frozen-probe", "protocol text: probe set corrected from LR, RBF-SVM or MLP to the LR and MLP grid of Section 2.5"))
for cfg in ("hyenadna", "nt", "generator-v2", "omni-dna"):
    c = by_id[f"{P}config-{cfg}-frozen"]["attributes"]
    c["parameters"] = c["parameters"].replace("best pooling and probe over the diagnostic grid",
                                              "best readout and probe over the diagnostic test grid, chosen per task (Table 3)")
    corrections.append((f"{P}config-{cfg}-frozen", "parameters: selection stated as per task over the test grid (Table 3)"))

# 4. Table 4 shows that Table 1's frozen values are test-set grid-best values, and that two
#    HyenaDNA cells disagree with Table 4.
LIM = ("Table 4 shows that Table 1's frozen values are diagnostic test-set grid-best scores: five of seven HyenaDNA "
       "tasks match the grid-best column exactly. They are maxima over the test grid, not validation-selected estimates.")
for pid in ("protocol-frozen-probe", "protocol-fine-tuned-reference"):
    by_id[P + pid]["attributes"]["limitations"].append(LIM)
    corrections.append((P + pid, "limitation added: Table 1 frozen values are test-grid maxima (Table 4)"))
src = by_id[P + "source"]["attributes"]
src["evidence_concerns"].append({
    "source_id": P + "source",
    "message": ("Table 1 and Table 4 disagree for HyenaDNA Splice Acceptor: Table 1 prints .4752±.0108 (recovery 50), "
                "while Table 4 prints 0.7308 ± 0.0033 (validation-selected) and 0.7360 ± 0.0052 (diagnostic grid-best). "
                "Five other HyenaDNA cells of Table 1 equal Table 4's grid-best values, but Splice Donor (.7247±.0087) equals "
                "the validation-selected value instead. Table 3 and Table 4 also name different grid-best readouts for "
                "HyenaDNA Splice All (MLP+Mean against MLP+Attn). Table 1 values are kept as printed."),
    "source_locator": "Table 1, column 'HyenaDNA', rows 'Splice Acceptor' and 'Splice Donor'; Table 4; Table 3, row 'Splice All'",
    "artifact_sha256": PDF_SHA,
    "review_date": DATE})
corrections.append((P + "source", "evidence concern added: Table 1 versus Table 4 conflict for HyenaDNA Splice Acceptor"))

# 5. DNABERT-2 is not only in Table 9: Tables 2, 7 and 8 also report it.
OLD_LIM = "Table 1 covers four of the five models in the study; DNABERT-2 appears only in the controlled LoRA comparison (Table 9)."
NEW_LIM = "Table 1 covers four of the five models in the study; DNABERT-2 is absent from it and appears in Tables 2, 7, 8 and 9."
for r in records:
    lims = r["attributes"].get("limitations", [])
    if OLD_LIM in lims:
        lims[lims.index(OLD_LIM)] = NEW_LIM
        corrections.append((r["id"], "limitation corrected: DNABERT-2 appears in Tables 2, 7, 8 and 9, not only Table 9"))
assert sum(1 for c in corrections if c[1].startswith("limitation corrected")) == 146

# ---- Review blocks and status --------------------------------------------------------------
NOTES = {
    P + "result-nt-enhancer-frozen": "Same frozen value and spread as NT Enhancer Types; the printed recovery (96 and 124) is "
    "consistent with the duplicated value, so the duplication is in the authors' numbers, not only in typesetting. Source "
    "concern recorded.",
    P + "result-nt-enhancer-types-frozen": "Same frozen value and spread as NT Enhancer; printed recovery 124 follows from it. "
    "Source concern recorded.",
    P + "result-hyenadna-splice-acceptor-frozen": "Table 4 prints 0.7308 (validation-selected) and 0.7360 (grid-best) for this "
    "task; Table 1's .4752 matches neither. Source concern recorded.",
    P + "result-hyenadna-splice-donor-frozen": "Equals Table 4's validation-selected value, while the other matched HyenaDNA cells equal its "
    "grid-best values. Source concern recorded.",
}
for r in records:
    r["status"] = "source_checked"
    a = r["attributes"]
    if r["kind"] in ("result", "claim"):
        note = "Independent review 2026-10-11: value and identity match the source; printed recovery agrees with the two scores."
        if r["kind"] == "claim":
            note = "Independent review 2026-10-11: matches Equation 7 and the Table 1 recovery positions."
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
                       "note": "Fresh download matches the pinned SHA-256. arXiv non-exclusive distribution licence; no copy archived."}

(HERE / "batch.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records))
(HERE / "review" / "corrections.json").write_text(json.dumps(corrections, ensure_ascii=False, indent=1) + "\n")
print(f"{checked} results checked; recovery consistent in 72 cells; {len(corrections)} corrections; {len(records)} records written")
