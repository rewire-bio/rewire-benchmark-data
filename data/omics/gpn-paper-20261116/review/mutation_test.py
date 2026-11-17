"""Mutation test: confirm review/recheck_values.py fails when a value is wrong."""
import importlib.util, json, sys, copy

spec = importlib.util.spec_from_file_location("rv", "review/recheck_values.py")
MUTATIONS = [
    ("printed_value swap, Table S2 chromosome-wide 2.90 -> 2.92",
     "gpn-paper-20261116-result-perplexity-chromosome-wide-repeat-weight-0-1", "printed_value", "2.92"),
    ("printed_value swap, Table S2 non-repeat 2.99 -> 2.92",
     "gpn-paper-20261116-result-perplexity-non-repeat-repeat-weight-1", "printed_value", "2.92"),
    ("locator column swap on a Table S2 cell",
     "gpn-paper-20261116-result-perplexity-chromosome-wide-repeat-weight-1", "source_locator",
     'Table S2 (SI Appendix), row "Repeat weight 1", column "Non-repeat regions"'),
    ("prose value changed, 96% -> 95%",
     "gpn-paper-20261116-result-gene-region-accuracy-cds", "printed_value", "95%"),
    ("prose value changed, 10.3-fold -> 10.5-fold",
     "gpn-paper-20261116-result-gwas-hit-odds-ratio-gpn-x-ld", "printed_value", "10.5-fold"),
    ("prose value changed, 2.8 -> 2.81 (the bioRxiv v3 value)",
     "gpn-paper-20261116-result-positional-perplexity-stop-codon", "printed_value", "2.81"),
]
base = [json.loads(l) for l in open("batch.jsonl")]

for label, rid, field, value in MUTATIONS:
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    recs = copy.deepcopy(base)
    hit = False
    for r in recs:
        if r["id"] == rid:
            r["attributes"][field] = value
            hit = True
    assert hit, rid
    mod.records = lambda recs=recs: recs
    mod.PROBLEMS, mod.CHECKS = [], []
    try:
        rc = mod.main()
    except SystemExit as e:
        rc = e.code
    status = "caught" if mod.PROBLEMS else "MISSED"
    print(f"{status}: {label} -> {len(mod.PROBLEMS)} failure(s)")
    for p in mod.PROBLEMS:
        print("      ", p)
