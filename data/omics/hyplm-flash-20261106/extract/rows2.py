"""Builders for the values the HyPLM report prints in prose."""

import core
from core import B, clean, page
from entities2 import PROTEINGYM_DATA
from rows import TIE, emit


def interval(lower, upper, note):
    return {"type": "confidence_interval", "lower": clean(lower), "upper": clean(upper),
            "level": 0.95, "method": "bootstrap_percentile", "resamples": 5000,
            "printed": f"[{lower}, {upper}]", "note": note}


def build(parsed, out, seen):
    prose = parsed["prose"]
    # Section 4.1: the four paired differences that make the ProteinGym tie checkable.
    for model, d in prose["paired"].items():
        printed = f"{d['value']} [{d['lower']}, {d['upper']}]"
        loc = (f"Section 4.1, sentence 'Its differences to ESM-2 650M ...', parenthesis for "
               f"{model} ({page('section41')})")
        emit(out, seen, "proteingym-paired-difference", PROTEINGYM_DATA, model, d["value"], loc,
             core.config(model)[1],
             uncertainty=interval(d["lower"], d["upper"],
                                  "Paired bootstrap over assays with identical resamples; the "
                                  "interval includes zero, which is the report's basis for "
                                  "calling the difference not significant."),
             claim_scope=TIE,
             printed_source_cell=printed)
    # Section 4.2: mean Spearman over the ten regression splits.
    for model, value in prose["regression_average"].items():
        loc = (f"Section 4.2, sentence 'Averaged over the ten regression splits ...', value for "
               f"{model} ({page('section42')})")
        extra = {}
        if model == "ESM-2 3B":
            extra["limitations"] = [
                "ESM-2 3B's per-split values are not printed anywhere in the report, so this "
                "average cannot be checked against its parts; the other four averages were checked "
                "against Table 6 and agree within rounding."]
        emit(out, seen, "regression-ten-split-average", f"{B}-data-regression-ten-splits", model,
             value, loc, core.config(model)[1], **extra)
    # Section 4.2: ESM C 6B's CB513 accuracy, printed only in prose.
    loc = (f"Section 4.2, sentence 'exceeded only by ESM3-open (0.896) and ESM C 6B (0.884)' "
           f"({page('section42')})")
    emit(out, seen, "secondary-structure-cb513",
         "lit-protein-20261011-deepprotein-data-secondary-structure", "ESM C 6B",
         prose["ss_esm_c_6b"], loc, core.config("ESM C 6B")[1])
    # Section 3: the measured throughput of the INT8 engine.
    loc = (f"Section 3, sentence 'On a common workload of 2,048 held-out proteins, the engine "
           f"embeds 131,000 residues per second on one H20' ({page('section3')})")
    emit(out, seen, "embedding-throughput-h20", f"{B}-data-throughput-workload", "INT8",
         prose["throughput_int8"], loc, "hyplm-flash-int8",
         unit_detail="Residues per second; printed as '131,000'",
         limitations=[
             "The README's precision table rounds this to 'about 130,000'. The BF16 mode's 90,000 "
             "residues per second is stated without a workload, so it is a claim, not a result.",
             "INT8 applies only to packed batches of at least 1,024 tokens, so this rate holds for "
             "batched workloads and not for single short proteins, which run BF16."])
    return out
