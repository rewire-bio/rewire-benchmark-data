"""Engine source records, benchmark, datasets and protocols for the HyPLM-Flash batch."""

from entities import (AREAS, B, BENCHMARK, BLOB, COMMIT, RAW, RETRIEVED, SRC_REPORT, record)
from tasks import PROTEINGYM_DATA, ZERO_SHOT, TASKS
from tasks2 import TASKS2

ALL_TASKS = TASKS + TASKS2

ENGINE_FILES = {
    "model": ("model.py", "8bba607aaac45d7365ac011644fcee65157a1f29f306c646aaa29d4258fd4255",
              "Engine module that loads the weights and runs packed batches. Line 41 defaults "
              "quant_min_tokens to 1024; line 102 sets quant = (precision == 'int8' and tokens >= "
              "quant_min_tokens) for each packed batch; the module docstring states that below "
              "quant_min_tokens tokens per batch the projections run in BF16."),
    "packing": ("packing.py", "3eb213e8483bb09551b253aeea9f4ff5a0c5b2e7cd53d985f226f1cbf52c1828",
                "Padding-free packing. plan(lengths, batch_tokens) groups proteins whose token "
                "counts (residues + 2) fit batch_tokens; the budget is a parameter here, and its "
                "32,768 default is on the encode interface the package README documents."),
    "graphs": ("graphs.py", "29df2c0d012c6e2f03b2618efb1cc76e070097b531494e5553f548b0bdf3f1bc",
               "Whole-model CUDA graphs for small batches. Line 12 sets BUCKETS = range(64, 513, "
               "64), so every captured bucket is 64 to 512 tokens, below the 1,024-token INT8 "
               "threshold, and the low-latency path always runs BF16."),
}


def engine_sources():
    out = []
    for key, (name, sha, note) in ENGINE_FILES.items():
        path = f"AI4Science/hyplm_flash/hyplm/engine/{name}"
        out.append(record(
            f"{B}-source-engine-{key}", "source",
            f"HyPLM-Flash engine source hyplm/engine/{name} (commit 0dcc533c)",
            f"Released Python source of the HyPLM-Flash inference engine, file hyplm/engine/{name}.",
            {"url": f"{BLOB}/{path}", "artifact_url": f"{RAW}/{path}",
             "version": f"GitHub repository Tencent-Hunyuan/Hyra-results at commit {COMMIT}",
             "retrieved_at": "2026-11-06T11:52:00Z", "artifact_sha256": sha,
             "publication_status": "official_project_source", "licence": "MIT",
             "media_type": "text/x-python", "source_type": "released source code",
             "archive_note": f"Archived in the batch as artifacts/engine-{name}.",
             "archive_sha256": sha, "scope_note": note},
            links=[{"relation": "companion_of", "target_id": SRC_REPORT}], sources=[]))
    return out


def benchmark():
    return [record(
        BENCHMARK, "benchmark", "HyPLM technical report protein language model evaluation",
        "Compares protein language models on zero-shot fitness, masked-residue likelihood and "
        "frozen-representation probes for structure, function, localisation and fitness.",
        {"entity_level": "suite", "version": "HyPLM technical report, 2026-10-12",
         "task": "Protein representation learning: zero-shot variant scoring from the "
                 "masked-language-model head, masked-residue likelihood, and linear probes on "
                 "frozen representations.",
         "scope_note": "32 tasks run on 29 models (HyPLM-Flash and 28 public checkpoints from 13 "
                       "families), all in BF16 through the authors' own adapters. Assembled and run "
                       "by the developer of HyPLM-Flash, so every evaluation in it is "
                       "author-reported and none is independent of the developer.",
         "limitations": [
             "Developer-run: the authors chose the tasks, the adapters, the layer-selection rule "
             "and the statistics, and ran every baseline.",
             "Every accuracy number is a BF16 run. The released default is the INT8 engine, for "
             "which no accuracy value is printed.",
             "Per-task values are printed for 13 of the 29 models only.",
             "ProteinGym scores depend on the assays included, the aggregation, the checkpoint and "
             "the scoring code; this suite's ProteinGym protocol is its own and is not the "
             "leaderboard's, though the authors report reproducing eight leaderboard checkpoints "
             "to within 0.0025."],
         "source_locator": "Section 4; Appendix A; Table 4"},
        links=[{"relation": "evaluates_task", "target_id": "catalog-task-proteingym-effects"}])]


def new_dataset(slug, spec, label):
    name, description, sizes, origin = spec
    return record(
        f"{B}-data-{slug}", "dataset", name, description,
        {"reported_name": label, "version": "As used in the HyPLM technical report (2026-10-12)",
         "split": f"train / valid / test as printed: {sizes}",
         "scope_note": f"Source as printed in Table 4: {origin}.",
         "source_locator": f"Table 4 row for '{label}'",
         "missing_metadata": {"manifest": {
             "reason": "unavailable", "note": "No identifier list or split manifest is published."}}})


EXTRA_DATA = {
    "regression-ten-splits": record(
        f"{B}-data-regression-ten-splits", "dataset",
        "Ten regression splits for summary statistics (HyPLM report)",
        "The ten fitness and property regression splits the HyPLM report averages for its "
        "summary statistics.",
        {"reported_name": "the ten regression splits used for summary statistics",
         "version": "As used in the HyPLM technical report (2026-10-12)",
         "split": "union of ten test splits",
         "scope_note": "AAV two-vs-many, AAV low-vs-high, GB1 low-vs-high, Meltome human cell, "
                       "Meltome mixed, amylase one-to-many, amylase by mutation count, fluorescence, "
                       "stability and thermostability. Appendix A leaves out GB1 two-vs-rest, GB1 "
                       "three-vs-rest and the FLIP2 hydrolase split.",
         "source_locator": "Appendix A 'Statistics'; Section 4.2"}),
    "throughput-workload": record(
        f"{B}-data-throughput-workload", "dataset",
        "Throughput workload of 2,048 held-out proteins (HyPLM report)",
        "2,048 held-out proteins totalling 639,806 residues that every model embeds for the "
        "report's speed comparison.",
        {"reported_name": "2,048 held-out proteins (639,806 residues)",
         "version": "As used in the HyPLM technical report (2026-10-12)", "split": "timing input",
         "scope_note": "Embedded in length-sorted batches of at most 16,384 tokens on one H20.",
         "source_locator": "Appendix A 'Throughput'; Section 3",
         "missing_metadata": {"manifest": {
             "reason": "unavailable", "note": "The 2,048 proteins are not listed."}}}),
}


def datasets():
    out = [new_dataset(t[1], t[7], t[0]) for t in ALL_TASKS if t[7]]
    return out + list(EXTRA_DATA.values())


def data_id(task):
    return task[2] if task[2] else f"{B}-data-{task[1]}"


def protocol(slug, name, description, metric, unit, qualifier, implementation, data,
             limitations, locator, direction="higher"):
    links = [{"relation": "part_of", "target_id": BENCHMARK},
             {"relation": "uses_data", "target_id": data}]
    return record(
        f"{B}-protocol-{slug}", "protocol", f"{name} (HyPLM report)", description,
        {"metric": metric, "metric_direction": direction, "unit": unit,
         "metric_qualifier": qualifier, "metric_implementation": implementation,
         "protocol": description, "version": "HyPLM technical report, 2026-10-12",
         "aggregation": "One value per model on the test split",
         "source_locator": locator, "limitations": limitations,
         "publication_status": "official_project_source"},
        links=links)


BF16_ONLY = ("Every value under this protocol is a BF16 run. The released default is the INT8 "
             "engine, for which the report prints no value on this task.")
REGRESSION_GAP = ("The report's list of what INT8 preserves within 0.01 (zero-shot fitness, "
                  "structure, function annotation and likelihood) omits regression, and the "
                  "release recommends BF16 for regressors on near-identical variants such as AAV "
                  "and GB1. The INT8 cost on this task is not measured anywhere in the release.")
LOWER = {"log-loss"}


def protocols():
    out = []
    for task in ALL_TASKS:
        label, slug, _, metric, unit, qualifier, implementation, _spec = task
        limits = [BF16_ONLY]
        if metric == "spearman-correlation" and slug != "proteingym-zero-shot":
            limits.append(REGRESSION_GAP)
        out.append(protocol(
            slug, label, f"Score each model on {label} under the HyPLM report's protocol.",
            metric, unit, qualifier, implementation, data_id(task), limits,
            f"Table 4 row for '{label}'; Tables 6 and 7 row '{label}'; Appendix A",
            direction="lower" if metric in LOWER else "higher"))
    # Perplexity on the two likelihood panels (Table 3).
    for slug, panel, data in [("ppl-held-out-uniref", "held-out UniRef panel",
                               f"{B}-data-nll-held-out-uniref"),
                              ("ppl-recent-pdb", "recent PDB chains", f"{B}-data-nll-recent-pdb")]:
        out.append(protocol(
            slug, f"Masked-residue perplexity, {panel}",
            f"Score masked-residue perplexity on the {panel}.", "perplexity", "unitless",
            f"Masked-residue perplexity on the {panel}: the exponential of the mean negative "
            "log-likelihood of masked residues under the model itself, with identical masks and "
            "crops for every model", "Exponential of the masked-residue NLL of the same protocol.",
            data, [BF16_ONLY], "Table 3", direction="lower"))
    # ProteinGym by selection type (Table 5, the authors' own dagger rows).
    for selection in ["Activity", "Binding", "Expression", "Organismal fitness", "Stability"]:
        slug = "proteingym-" + selection.lower().replace(" ", "-")
        out.append(protocol(
            slug, f"ProteinGym zero-shot, {selection.lower()} assays",
            f"Score zero-shot Spearman correlation on the ProteinGym v1.3 {selection.lower()} "
            "assays.", "spearman-correlation", "unitless",
            f"Spearman correlation averaged over the ProteinGym v1.3 substitution assays of "
            f"selection type '{selection}', from masked-marginal zero-shot scores; only the "
            "authors' own runs (dagger rows of Table 5) are recorded", ZERO_SHOT, PROTEINGYM_DATA,
            [BF16_ONLY, "No per-category interval is printed. Table 5's rows without a dagger are "
             "published leaderboard values that the authors did not run, so no comparison "
             "between a dagger row and an undaggered row is recorded."], "Table 5"))
    out.append(protocol(
        "proteingym-paired-difference", "ProteinGym zero-shot paired difference from HyPLM-Flash",
        "Measure HyPLM-Flash's ProteinGym Spearman correlation minus a baseline's, with a paired "
        "bootstrap interval over assays.", "spearman-correlation-difference", "unitless",
        "HyPLM-Flash minus the baseline, Spearman correlation over the 217 ProteinGym v1.3 "
        "substitution assays with the official aggregation; 95% interval from 5,000 bootstrap "
        "replicates over assays, recomputing the official aggregation each time, with identical "
        "resamples for both models; the reference system is HyPLM-Flash",
        ZERO_SHOT + " Paired bootstrap over assays, 5,000 replicates.", PROTEINGYM_DATA,
        [BF16_ONLY, "Printed for four baselines only. The report states the differences to "
         "ESM-2 3B, ESM-2 15B and ESM C 6B are also not significant but prints no value for "
         "them."], "Section 4.1; Appendix A 'Statistics'"))
    out.append(protocol(
        "regression-ten-split-average", "Mean Spearman over ten regression splits",
        "Average a model's Spearman correlation over the ten regression splits the report uses "
        "for summary statistics.", "spearman-correlation", "unitless",
        "Unweighted mean of the test Spearman correlations on the ten regression splits Appendix A "
        "uses for summary statistics, excluding GB1 two-vs-rest, GB1 three-vs-rest and the FLIP2 "
        "hydrolase split", "Mean of the per-split ridge-probe Spearman correlations.",
        f"{B}-data-regression-ten-splits", [BF16_ONLY, REGRESSION_GAP],
        "Section 4.2; Appendix A 'Statistics'"))
    out.append(protocol(
        "embedding-throughput-h20", "Embedding throughput on one NVIDIA H20",
        "Measure how many residues per second a model embeds on one GPU for a fixed workload.",
        "inference-throughput", "sample-per-second",
        "Residues embedded per second on one NVIDIA H20 for 2,048 held-out proteins (639,806 "
        "residues) in length-sorted batches of at most 16,384 tokens; HyPLM-Flash on its INT8 "
        "engine, where INT8 applies only to packed batches of at least 1,024 tokens",
        "Each model uses the fastest attention kernel its implementation supports: FlashAttention-2 "
        "for ESM-1b, ESM-2 and DPLM, FlashAttention for ESM C and E1, xformers for AMPLIFY and "
        "PyTorch SDPA for ProtBERT and ESM3-open; HyPLM-Flash runs on its INT8 engine.",
        f"{B}-data-throughput-workload",
        ["One GPU model (NVIDIA H20) on one workload. HyPLM-Flash runs an optimised engine and "
         "the baselines their reference implementations, so the ratio is against those "
         "implementations, not against equally optimised baselines.",
         "The engine applies INT8 only to packed batches of at least 1,024 tokens (model.py line "
         "102), so batches under that size run BF16 even when precision is int8; a workload of "
         "short batches would not run at this rate.",
         "Only HyPLM-Flash's figure is printed. Baseline throughputs appear only as unlabelled "
         "points in Figure 1a and as ranges: Section 1 puts the reference implementations of "
         "recent 600M-class encoders at 48,000 to 69,000 residues per second, and Section 3 puts "
         "HyPLM-Flash 1.9 to 2.7 times faster than ESM C 600M, ESM-1b, ESM-2 650M, DPLM-650M and "
         "E1-600M."],
        "Section 3; Appendix A 'Throughput'"))
    return out


def entities2():
    return engine_sources() + benchmark() + datasets() + protocols()
