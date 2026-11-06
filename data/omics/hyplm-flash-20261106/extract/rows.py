"""Builders turning parsed HyPLM report cells into evaluations and results."""

import core
from core import B, clean, evaluation, page, result
from entities2 import ALL_TASKS, PROTEINGYM_DATA, data_id, protocols

_PROTOCOLS = protocols()
PROTO = {p["id"].replace(f"{B}-protocol-", ""): p["attributes"] for p in _PROTOCOLS}
PROTO_DATA = {p["id"].replace(f"{B}-protocol-", ""):
              next(l["target_id"] for l in p["links"] if l["relation"] == "uses_data")
              for p in _PROTOCOLS}
TASK = {t[0]: t for t in ALL_TASKS}
TIE = ("Not a win. Section 4.1 states HyPLM-Flash's ProteinGym differences to ESM-2 650M, "
       "ESM C 600M, DPLM-650M and E1-600M are not significant (each 95% interval includes zero), "
       "and neither are those to ESM-2 3B, ESM-2 15B and ESM C 6B; the order of these point "
       "estimates does not show that one model is better.")
TIED = {"HyPLM-Flash", "ESM-2 650M", "ESM C 600M", "DPLM-650M", "E1-600M", "ESM-2 3B",
        "ESM-2 15B", "ESM C 6B"}


def emit(out, seen, slug, data, label, printed, locator, rid_tail, uncertainty=None,
         overrides=None, **extra):
    eval_id, rec = evaluation(slug, data, label, locator, overrides)
    if eval_id not in seen:
        seen.add(eval_id)
        out.append(rec)
    p = PROTO[slug]
    name_label = label.rstrip("†")
    out.append(result(f"{B}-result-{slug}-{rid_tail}", f"{name_label}: {slug} (HyPLM report)",
                      eval_id, printed, p["metric"], p["unit"], p["metric_direction"],
                      p["metric_qualifier"], locator, uncertainty, **extra))


def tie_scope(slug, label):
    if slug == "proteingym-zero-shot" and label.rstrip("†") in TIED:
        return TIE
    return None


def build(parsed):
    core.PAGES.clear()
    core.PAGES.update(parsed["pages"])
    out, seen = [], set()
    # Tables 6 and 7: every printed task cell.
    for (task_label, model), cell in parsed["tasks"].items():
        task = TASK[task_label]
        table = "table6" if model in ("ESM-2 650M", "ESM-1b", "ESM C 600M", "E1-600M",
                                      "AMPLIFY-350M", "DPLM-650M", "HyPLM-Flash") else "table7"
        loc = (f"Table {table[-1]}, row '{task_label}', column '{model}' ({page(table)})")
        emit(out, seen, task[1], data_id(task), model, cell, loc, core.config(model)[1],
             claim_scope=tie_scope(task[1], model))
    # Table 3: perplexity for all ten rows; NLL only where Tables 6 and 7 lack the model.
    for model, row in parsed["table3"].items():
        for col, slug, task_label, header in [
                ("ppl_uniref", "ppl-held-out-uniref", None, "Held-out UniRef proteins, PPL"),
                ("ppl_pdb", "ppl-recent-pdb", None, "Recent PDB chains, PPL"),
                ("nll_uniref", "nll-held-out-uniref", "NLL, held-out UniRef panel",
                 "Held-out UniRef proteins, NLL"),
                ("nll_pdb", "nll-recent-pdb", "NLL, recent PDB chains", "Recent PDB chains, NLL")]:
            if task_label and (task_label, model) in parsed["tasks"]:
                continue
            data = PROTO_DATA[slug]
            loc = f"Table 3, row '{model}', column '{header}' ({page('table3')})"
            emit(out, seen, slug, data, model, row[col], loc, core.config(model)[1])
    # Table 5: the authors' own dagger rows only.
    for label, row in parsed["table5"].items():
        if "†" not in label:
            continue
        for sel in ["Activity", "Binding", "Expression", "Organismal fitness", "Stability"]:
            slug = "proteingym-" + sel.lower().replace(" ", "-")
            loc = f"Table 5, row '{label}', column '{sel}' ({page('table5')})"
            extra = {}
            if label == "HyPLM-Flash†" and sel == "Binding":
                extra["limitations"] = [
                    "The only ESM-2 650M binding value in the report is Table 5's undaggered "
                    "row 'ESM2 (650M)', 0.337, a published leaderboard value the authors did "
                    "not run. A difference against it mixes origins and has no interval, so "
                    "none is recorded."]
            emit(out, seen, slug, PROTEINGYM_DATA, label, row[sel], loc, core.config(label)[1],
                 overrides={"metric_implementation": None, "aggregation": None}, **extra)
        if ("ProteinGym zero-shot", label.rstrip("†")) not in parsed["tasks"]:
            loc = f"Table 5, row '{label}', column 'Average' ({page('table5')})"
            emit(out, seen, "proteingym-zero-shot", PROTEINGYM_DATA, label, row["Average"], loc,
                 core.config(label)[1], claim_scope=tie_scope("proteingym-zero-shot", label))
    # Figure 3a: bar labels for models no table prints.
    printed = {k.rstrip("†") for k in parsed["table5"] if "†" in k}
    for label, value in parsed["figure3a"].items():
        if ("ProteinGym zero-shot", label) in parsed["tasks"] or label in printed:
            continue
        loc = f"Figure 3a, bar '{label}', printed value label ({page('figure3')})"
        emit(out, seen, "proteingym-zero-shot", PROTEINGYM_DATA, label, value, loc,
             core.config(label)[1], claim_scope=tie_scope("proteingym-zero-shot", label))
    return out, seen
