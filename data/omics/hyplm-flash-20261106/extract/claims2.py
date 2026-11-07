"""Precision, evaluation and Figure 1b claims, and the claim builder."""

from claims import ENGINE, L, M, MODEL_CLAIMS, P, R
from core import REVIEW
from entities import B, BENCHMARK, MODEL, record

PRECISION_CLAIMS = [
    ("int8-default", M, "precision", "INT8 is the package default (precision=\"int8\"); "
     "precision=\"bf16\" is the alternative.", "README 'Usage' and 'Precision'"),
    ("int8-threshold", ENGINE, "precision", "The engine applies INT8 only to packed batches of at "
     "least 1,024 tokens (quant_min_tokens); smaller batches run BF16 even when precision is int8.",
     "hyplm/engine/model.py lines 7, 41 and 102"),
    ("graph-path-bf16", ENGINE, "precision", "The CUDA-graph low-latency path captures buckets of "
     "64 to 512 tokens, all under the INT8 threshold, so it always runs BF16.",
     "hyplm/engine/graphs.py line 12; hyplm/engine/model.py line 102"),
    ("int8-preservation", R, "precision", "Section 3 states INT8 keeps zero-shot fitness, "
     "structure, function annotation and likelihood within 0.01 of the BF16 results. Regression "
     "is not in that list, and no per-task INT8 value is printed.", "Section 3"),
    ("variant-similarity", R, "precision", "Representations of near-identical protein variants "
     "differ by only about 1%.", "Section 3; README 'Precision'"),
    ("bf16-recommendation", M, "precision", "The release recommends BF16 for training supervised "
     "regressors on near-identical variants (AAV and GB1 in FLIP are named). This is author "
     "guidance: no INT8-against-BF16 regression comparison is printed in the report or README.",
     "README 'Precision' table and paragraph; Section 3"),
    ("throughput-readme-int8", M, "throughput", "README gives INT8 H20 throughput as about "
     "130,000 residues per second, a rounding of the report's measured 131,000.",
     "README 'Precision' table, int8 row"),
    ("throughput-bf16", R, "throughput", "The engine's BF16 mode runs at 90,000 residues per "
     "second. No workload is stated for this figure, so it is not recorded as a result.",
     "Section 3, final sentence"),
    ("speed-range", R, "throughput", "The INT8 engine is 1.9 to 2.7 times faster than ESM C 600M, "
     "ESM-1b, ESM-2 650M, DPLM-650M and E1-600M in their reference implementations; the per-model "
     "ratios are not printed.", "Section 3; Abstract"),
    ("baseline-throughput-range", R, "throughput", "On an H20, reference implementations of recent "
     "600M-class encoders embed 48,000 to 69,000 residues per second.", "Section 1"),
    ("accuracy-in-bf16", R, "precision", "Every accuracy result in the report is evaluated with "
     "BF16 arithmetic, for HyPLM-Flash and for all baselines.", "Section 3; Section 4"),
]

BENCHMARK_CLAIMS = [
    ("model-count", R, "scope", "28 public checkpoints from 13 model families, 29 models with "
     "HyPLM-Flash, on 32 tasks. The 28 are never listed; only 20 baselines have a printed value.",
     "Section 4 opening paragraph; Abstract"),
    ("leaderboard-reproduction", R, "reproduction_check", "The authors' runs of eight published "
     "ESM-2 and ESM C checkpoints reproduce the ProteinGym leaderboard to within 0.0025.",
     "Section 4.1"),
    ("xtrimopglm-gap", R, "deviation", "The authors' xTrimoPGLM ProteinGym runs fall 0.07 to 0.09 "
     "below the leaderboard, so they withhold its zero-shot and likelihood results.",
     "Appendix A 'Deviations'"),
    ("sequence-only", R, "deviation", "ESM3-open and SaProt are evaluated from sequence alone, "
     "whereas their published ProteinGym results also use structure inputs; E1 runs without "
     "retrieved context sequences.", "Appendix A 'Models' and 'Deviations'; Section 4"),
    ("bootstrap", R, "statistics", "Confidence intervals use 5,000 bootstrap replicates over "
     "assays, proteins, queries or sequences, with identical resamples for paired differences.",
     "Appendix A 'Statistics'"),
    ("noisy-splits", R, "statistics", "On GB1 two-vs-rest, GB1 three-vs-rest and the FLIP2 "
     "hydrolase split, numerically equivalent runs of the same model differ by up to 0.2, so these "
     "splits are left out of all summary statistics.", "Appendix A 'Statistics'"),
    ("leaderboard-rank", R, "ranking", "Among the 55 single-sequence entries of the public "
     "ProteinGym leaderboard, HyPLM-Flash is tied for eighth place; the top two, VespaG and VESPA, "
     "are supervised predictors.", "Section 4.1; Table 5"),
    ("table5-provenance", R, "provenance", "Table 5's undaggered rows are published leaderboard "
     "values at ProteinGym commit 144fe22 that the authors did not run; only the dagger rows are "
     "the authors' evaluation, and only those are recorded as results here.", "Table 5 caption"),
    ("figure1-split-count", R, "scope", "Figure 1 summarises 35 task splits, but Tables 6 and 7 "
     "list 32 tasks and Appendix A removes 3 from summaries; the report does not define the 35.",
     "Figure 1 caption and axis; Tables 6 and 7; Appendix A"),
]

FIGURE1B = [("ESM-1b", 26, 9), ("ESM C 300M", 23, 12), ("ESM C 600M", 21, 14),
            ("ESM3-open", 21, 14), ("DPLM-650M", 21, 14), ("ESM-2 650M", 20, 14),
            ("E1-600M", 18, 17), ("ESM-2 3B", 15, 20)]


def figure1b_claims():
    out = []
    for model, won, lost in FIGURE1B:
        slug = model.lower().replace(" ", "-")
        for kind, n in [("won", won), ("lost", lost)]:
            note = ""
            if model == "ESM-2 650M":
                note = (f" This row's won and lost labels sum to 34 against the axis's 'of 35', "
                        "while every other row sums to 35; the figure does not say what the "
                        "remaining split is.")
            out.append((f"figure1b-{slug}-{kind}", R, "head_to_head",
                        f"Figure 1b prints {n} task splits {kind} by HyPLM-Flash against {model}, "
                        "on min-max normalised scores." + note,
                        f"Figure 1b, row '{model}', {kind} label (page 1)"))
    return out


def build_claims():
    out = []
    groups = [(MODEL, MODEL_CLAIMS + PRECISION_CLAIMS),
              (BENCHMARK, BENCHMARK_CLAIMS + figure1b_claims())]
    for subject, claims in groups:
        tag = "hyplm-flash" if subject == MODEL else "benchmark"
        for slug, sources, field, value, locator in claims:
            out.append(record(
                f"{B}-claim-{tag}-{slug}", "claim", f"HyPLM report: {slug.replace('-', ' ')}",
                "Descriptive fact read from the pinned sources at the locator given; not a "
                "measurement on a benchmark panel.",
                {"field": field, "value": value, "source_locator": locator, "review": dict(REVIEW)},
                links=[{"relation": "subject", "target_id": subject}], sources=sources))
    return out
