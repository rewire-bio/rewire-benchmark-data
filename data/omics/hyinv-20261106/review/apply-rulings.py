"""Apply the coordinator's rulings to batch.jsonl, after review/apply-review.py.

Run order, which notes.md also records:

    python3 -I data/omics/hyinv-20261106/extract/build.py <report.pdf> batch.jsonl
    python3 -I data/omics/hyinv-20261106/review/apply-review.py batch.jsonl
    python3 -I data/omics/hyinv-20261106/review/apply-rulings.py batch.jsonl

Rulings 3, 6, 10, 11 and 12 of the HyInv review round. Rulings 1, 2, 5, 7 and 8 confirmed what the
batch and the first review pass already held, so they need no edit here. Ruling 4 is applied in
apply-review.py; where this script departs from a ruling, docs/reviews/2026-11-06-hyinv.md says so
and why.
"""
import copy
import json
import sys

PATH = sys.argv[1]
records = [json.loads(line) for line in open(PATH) if line.strip()]
by_id = {r["id"]: r for r in records}
log = []


def note(message):
    log.append(message)


def swap(attrs, key, old, new, where):
    """Replace `old` with `new` inside attrs[key], asserting it was there."""
    assert key in attrs, (where, key)
    assert old in attrs[key], (where, key, attrs[key][:120])
    attrs[key] = attrs[key].replace(old, new)


# Ruling 3. A value read off a fitted curve is not a measurement at a matched setting. Every record
# carrying one must say that the level is interpolated from a fit, and nothing may call it a
# measured matched-diversity result.
FIT = (" Both values are read from least-squares quadratic fits of scTM against design-set "
       "diversity over a rewrite-temperature grid, so the level is interpolated from a fit and is "
       "not a measurement at a matched sampling setting.")
CURVE = (" The baseline side is read off that fitted curve rather than measured at a matched "
         "setting, and two of ProteinMPNN's three grid temperatures were generated for this report "
         "rather than taken from its published setting.")
INTERP = (" The baselines are interpolated at the HyInv diversity from their own temperature grids, "
          "so 'at matched diversity' is the report's wording for an interpolated comparison and not "
          "a measurement of either baseline at HyInv's diversity.")

counts = {"table8": 0, "d3": 0, "s54": 0, "yield": 0}
for r in records:
    a = r["attributes"]
    if r["kind"] == "result":
        loc = a.get("source_locator", "")
        if loc.startswith("Table 8,"):
            a["metric_qualifier"] += FIT
            counts["table8"] += 1
        elif loc.startswith("Appendix D.3"):
            a["metric_qualifier"] += CURVE
            counts["d3"] += 1
        elif loc.startswith("Section 5.4") and a["metric"] == "sctm-at-fixed-diversity-difference":
            a["metric_qualifier"] += FIT
            counts["s54"] += 1
        elif loc.startswith("Section 6") and a["metric"] == "count":
            a["metric_qualifier"] += INTERP
            counts["yield"] += 1

by_id["hyinv-20261106-protocol-sctm-fixed-diversity-gain-vs-unmodified-sampler"]["attributes"]["metric_qualifier"] += FIT
by_id["hyinv-20261106-protocol-sctm-fixed-diversity-gain-vs-supervised-checkpoint"]["attributes"]["metric_qualifier"] += FIT
by_id["hyinv-20261106-protocol-sctm-fixed-diversity-vs-proteinmpnn-curve"]["attributes"]["metric_qualifier"] += CURVE
by_id["hyinv-20261106-protocol-novel-and-foldable-yield"]["attributes"]["metric_qualifier"] += INTERP

# The word "measured" where the quantity is read off a curve, and two conclusions that read as a
# matched measurement.
swap(by_id["hyinv-20261106-config-hyinv-unmodified-sampler-update288"]["attributes"], "parameters",
     "are measured at equal diversity",
     "are read at equal diversity, each from its own fitted scTM-against-diversity curve",
     "unmodified sampler configuration")
fixed_adapt = 0
for r in records:
    if r["kind"] != "evaluation":
        continue
    comparison = r["attributes"].get("comparison") or {}
    text = comparison.get("adaptation")
    if not isinstance(text, str):
        continue
    if "so the comparison is at equal diversity by construction" in text:
        comparison["adaptation"] = text.replace(
            "so the comparison is at equal diversity by construction",
            "so the level is interpolated from a fit rather than measured at a matched sampling "
            "setting")
        fixed_adapt += 1
    elif "so the comparison is at matched diversity" in text:
        comparison["adaptation"] = text.replace(
            "so the comparison is at matched diversity",
            "so the baseline side is interpolated rather than measured at HyInv's diversity")
        fixed_adapt += 1
note(f"ruling 3: fit and interpolation wording added to {counts['table8']} Table 8, {counts['d3']} "
     f"Appendix D.3, {counts['s54']} Section 5.4 and {counts['yield']} Section 6 result qualifiers "
     f"and to 4 protocol qualifiers; 'measured at equal diversity' corrected on one configuration "
     f"and {fixed_adapt} evaluation adaptation fields")

# Rulings 6 and 10. A vocabulary concept must not encode one source's estimator, and
# sequence-diversity keeps direction unknown with the matched-not-ranked qualifier. The estimator
# already sits in the result qualifier; the matched-not-ranked sense was only in the definition.
diversity = 0
for r in records:
    a = r["attributes"]
    if r["kind"] == "result" and a["metric"] == "sequence-diversity":
        assert a["metric_direction"] == "unknown", r["id"]
        a["metric_qualifier"] += (" Matched rather than ranked when generators are compared: the "
                                  "value describes the design set, not its quality, so a higher "
                                  "value is not better and the direction is unknown.")
        diversity += 1
proto = by_id["hyinv-20261106-protocol-sequence-diversity"]["attributes"]
assert proto["metric_direction"] == "unknown"
proto["metric_qualifier"] += (" Matched rather than ranked when generators are compared: the value "
                              "describes the design set, not its quality, so a higher value is not "
                              "better and the direction is unknown.")
note(f"rulings 6 and 10: matched-not-ranked statement added to {diversity} sequence-diversity "
     f"result qualifiers and the protocol qualifier, direction unknown confirmed on all of them")

# Ruling 11. A claim holding many numbers under one locator is split so each number has its own
# locator. The gain exists where the source prints the numbers in separate rows that the claim
# collapses; for a claim quoting one prose passage the passage is the locator and splitting gives
# no number a locator of its own. Three claims print per row: Table 5, Table 10 and Table 3.
TABLE5_ROWS = [
    ("proteinmpnn", "ProteinMPNN", "not regenerated: the table prints a dash for both columns, so "
     "no absolute scTM difference and no identical-sequence fraction is reported for it"),
    ("proteinmpnn-grouped", "ProteinMPNN grouped", "regenerated on CATH4.3 test, absolute scTM "
     "difference 0.0009, 100.0% of sequences identical to the released ones"),
    ("proteinmpnn-low-noise-grouped", "ProteinMPNN (low-noise, grouped)", "regenerated on four "
     "panels, absolute scTM difference 0.0007, 100.0% of sequences identical"),
    ("proteinzero-v2-esm1", "ProteinZero V2 (ESM1)", "regenerated on CATH4.3 test, absolute scTM "
     "difference 0.0006, 100.0% of sequences identical"),
    ("proteinzero-v2-esm2", "ProteinZero V2 (ESM2)", "not regenerated: the table prints a dash for "
     "both columns"),
    ("pifold", "PiFold", "regenerated on four panels, absolute scTM difference 0.0004, 100.0% of "
     "sequences identical"),
    ("cmlm", "CMLM", "regenerated on four panels, absolute scTM difference 0.0022, the largest in "
     "the table, 100.0% of sequences identical"),
    ("lm-design-650m", "LM-Design 650M", "regenerated on four panels, absolute scTM difference "
     "0.0005, 100.0% of sequences identical"),
    ("dplm-2-3b", "DPLM-2 3B", "regenerated on four panels, absolute scTM difference 0.0001, 99.2% "
     "of sequences identical, the only baseline below 100%"),
    ("ligandmpnn", "LigandMPNN", "regenerated on four panels, absolute scTM difference 0.0005, "
     "100.0% of sequences identical"),
]
TABLE10_ROWS = [
    ("de-novo-backbones", "De novo backbones", "74 backbones, 0 with a hit that passes the rule, 28 "
     "with partial hits only"),
    ("pocket-library", "Pocket library", "12 backbones, 0 passing hits, 7 with partial hits only"),
    ("loop-window-strict", "Loop and window, strict", "2 backbones, 0 passing hits, 2 with partial "
     "hits only"),
    ("loop-window-relaxed", "Loop and window, relaxed", "6 backbones, 0 passing hits, 4 with partial "
     "hits only"),
    ("named-enzymes", "Named enzymes", "4 backbones, all 4 with a passing hit and 0 with partial "
     "hits only; the named enzymes are homologous to training data by design"),
]
TABLE3_ROWS = [
    ("cath43-test", "CATH4.3 test", "1,882 chains in 103 CATH topology clusters, folded by "
     "ESMFold2, used for the comparison and as a sampler check"),
    ("cath42-test", "CATH4.2 test", "1,120 chains in 109 clusters, folded by ESMFold2, used for the "
     "comparison"),
    ("ts500", "TS500", "500 chains in 500 clusters, folded by ESMFold2, used for the comparison"),
    ("ts50", "TS50", "50 chains in 50 clusters, folded by ESMFold2, used for the comparison"),
    ("recentpdb", "RecentPDB", "121 chains in 121 clusters, folded by ESMFold2, Boltz2 and "
     "Protenix2, used for the comparison and as a sampler check"),
    ("cath43-validation", "CATH4.3 validation", "1,529 chains in 91 clusters, folded by ESMFold2, "
     "the development panel: it fixed the sampler setting and the checkpoint and monitored "
     "training, and each test panel was evaluated once"),
]
SPLITS = [
    ("hyinv-20261106-claim-benchmark-baseline-reproduction-check", "baseline_reproduction_check",
     TABLE5_ROWS, "Table 5 'Baseline settings, weights and reproduction check', row '{row}'",
     "HyInv report: reproduction check for {row}",
     "The reproduction check regenerates the baseline on RecentPDB, folds it with ESMFold2 and "
     "compares the target-averaged scTM with the released value. {row}: {detail}. All baselines use "
     "the released weights and a temperature of 0.1.",
     "Regenerated baseline cells are used only where the same procedure reproduces the released "
     "score on RecentPDB; the printed absolute differences run from 0.0001 to 0.0022, all within "
     "0.003. All RecentPDB cells under the three predictors are released values, and the "
     "ProteinMPNN temperatures other than the published one were generated for this report. The "
     "per-baseline figures are in the claims for each row of Table 5.",
     "Table 5 'Baseline settings, weights and reproduction check', the paragraph after the table"),
    ("hyinv-20261106-claim-benchmark-application-homology-screen", "application_homology_screen",
     TABLE10_ROWS, "Table 10 'Homology screen of the application panels', row '{row}'",
     "HyInv report: homology screen of {row}",
     "Homology screen of the application panels. {row}: {detail}.",
     "A hit passes the rule if its sequence identity to the pretraining library or to the benchmark "
     "reference set is at least 0.3 and it covers at least 0.8 of the query or of the target; "
     "partial hits stay below the coverage limit. Strict backbones have no passing hit; relaxed "
     "backbones relax one criterion of the strict rule, fixed before any design was made. The "
     "report states the table documents the panel rule only. The per-panel counts are in the claims "
     "for each row of Table 10.",
     "Table 10 'Homology screen of the application panels', its footnote; Appendix G 'Homology of "
     "the panels'"),
    ("hyinv-20261106-claim-benchmark-panels", "panels",
     TABLE3_ROWS, "Table 3 'Evaluation panels', row '{row}'",
     "HyInv report: evaluation panel {row}",
     "{row}: {detail}.",
     "Six panels: five test panels and one development panel, whose chain counts, cluster counts, "
     "structure predictors and use are in the claims for each row of Table 3. The resampling unit "
     "is the CATH topology cluster on the two CATH panels and the single chain elsewhere.",
     "Table 3 'Evaluation panels'; Section 5.1 'Panels'; Appendix A 'Panels'"),
]
added = 0
for claim_id, field, rows, loc_tpl, name_tpl, value_tpl, rule_value, rule_loc in SPLITS:
    parent = by_id.pop(claim_id)
    records.remove(parent)
    for slug, row, detail in rows:
        child = copy.deepcopy(parent)
        child["id"] = f"{claim_id}-{slug}"
        child["name"] = name_tpl.format(row=row)
        child["attributes"]["field"] = f"{field}_{slug.replace('-', '_')}"
        child["attributes"]["source_locator"] = loc_tpl.format(row=row)
        child["attributes"]["value"] = value_tpl.format(row=row, detail=detail)
        records.append(child)
        by_id[child["id"]] = child
        added += 1
    # The table's footnote or rule is not a row, so it keeps a claim of its own.
    rule = copy.deepcopy(parent)
    rule["id"] = f"{claim_id}-rule"
    rule["attributes"]["field"] = f"{field}_rule"
    rule["attributes"]["source_locator"] = rule_loc
    rule["attributes"]["value"] = rule_value
    records.append(rule)
    by_id[rule["id"]] = rule
    added += 1
note(f"ruling 11: 3 claims whose numbers the source prints per row split into {added}, one per "
     f"printed row plus one for each table's rule or footnote")

# Ruling 12. The speed-ups against HyInv's own reference sampler are recorded as claims beside the
# ones against ProteinMPNN, because they are the numbers most easily confused with them.
template = by_id["hyinv-20261106-claim-hyinv-inference-speed-conditions"]
for slug, field, name, locator, value in [
    ("reference-sampler-speedup-bf16", "reference_sampler_speedup_bf16",
     "HyInv report: BF16 speed-up against the reference sampler",
     "Section 4 'Efficient inference', first sentence; abstract",
     "Section 4 states HyInv designs 128 sequences for a 402-residue backbone in 50.6 ms on one "
     "NVIDIA H20, '52.1x faster than the reference implementation of the sampler and 57x faster "
     "than ProteinMPNN'; the abstract gives the same figure as 'about 52x faster than the reference "
     "sampler'. This is HyInv's optimised BF16 path against HyInv's own FP32 reference sampler, not "
     "against a baseline model, and it is the printed ratio of the two Table 1 times for the "
     "402-residue request (2,633 and 50.6 ms). The 57x recorded as a result is the ratio against "
     "ProteinMPNN's released implementation. Both were timed with the supervised-stage weights at "
     "rewrite temperature 0.23, not the released checkpoint."),
    ("reference-sampler-speedup-exact-fp32", "reference_sampler_speedup_exact_fp32",
     "HyInv report: exact FP32 speed-up against the reference sampler",
     "Abstract, final speed sentence",
     "The abstract states 'an exact FP32 path that returns the reference sequences is 8.7x faster', "
     "against HyInv's own FP32 reference sampler. Table 1's printed times for the 402-residue "
     "request give the same ratio (2,633 and 303 ms). The 9.6x recorded as a result is the ratio "
     "against ProteinMPNN's released implementation, so the two figures describe different "
     "comparisons and neither is a speed-up of HyInv over a baseline at equal optimisation."),
]:
    claim = copy.deepcopy(template)
    claim["id"] = f"hyinv-20261106-claim-hyinv-{slug}"
    claim["name"] = name
    claim["attributes"]["field"] = field
    claim["attributes"]["source_locator"] = locator
    claim["attributes"]["value"] = value
    records.append(claim)
    by_id[claim["id"]] = claim
note("ruling 12: 2 claims added for the 52.1x and 8.7x speed-ups against HyInv's own reference "
     "sampler, beside the 57x and 9.6x results against ProteinMPNN")

records.sort(key=lambda r: r["id"])
with open(PATH, "w") as out:
    for r in records:
        out.write(json.dumps(r, sort_keys=True) + "\n")
for line in log:
    print(line)
print(f"{len(records)} records")
