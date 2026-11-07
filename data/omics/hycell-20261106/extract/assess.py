"""Benchmark, datasets and protocols for the HyCell batch."""

from sources import AREAS, B, record

BENCHMARK = f"{B}-benchmark-held-out-atlases"
SUITE = f"{B}-data-seven-held-out-atlases"
ATLAS = {  # label -> (slug, name, description text, cells, batches, cell types)
    "Immune": ("immune", "scIB human immune atlas, integer-count part (HyCell report)",
               "bone marrow and blood from 5 studies; the integer-count part of the scIB human immune "
               "integration task", "32,484", "9", "16"),
    "Pancreas": ("pancreas", "scIB human pancreas atlas, integer-count part (HyCell report)",
                 "inDrop and Smart-seq2; the integer-count part of the scIB pancreas task",
                 "10,963", "5", "14"),
    "Lung": ("lung", "scIB human lung atlas, integer-count part (HyCell report)",
             "Drop-seq; the integer-count part of the scIB lung task", "9,701", "4", "11"),
    "PBMC": ("pbmc", "PBMC from two 10x Genomics runs (HyCell report)",
             "blood, 10x Chromium: the 10x Genomics pbmc4k and pbmc8k datasets (2017)", "12,039",
             "2", "9"),
    "Brain": ("brain", "MultiVINE brain vasculature, healthy donors (HyCell report)",
              "prefrontal cortex, vascular-enriched: the healthy donors of the MultiVINE atlas "
              "(Reid et al., 2025)", "21,155", "10 donors", "14"),
    "Cross-tissue immune": ("cross-tissue-immune",
                            "Cross-tissue immune atlas, stratified sample (HyCell report)",
                            "17 tissue sites and three 10x chemistries: a stratified 40,322-cell "
                            "sample of the atlas of Dominguez Conde et al. (2022)", "40,322",
                            "12 donors", "45"),
    "AIDA": ("aida", "Asian Immune Diversity Atlas, sample (HyCell report)",
             "blood from 5 sites: a 41,140-cell sample of the Asian Immune Diversity Atlas (Kock et "
             "al., 2025)", "41,140", "5 sites", "32"),
}
CELL_LEVEL = ("The benchmark measures cell-level tasks only: it excludes donor- and sample-level "
              "tasks, such as predicting a donor's disease state, which the report says Stack's use "
              "of the other cells of a sample helps.")
INPUTS = ("Raw integer counts of human genes with all measured genes; genes outside HyCell's "
          "36,495-gene vocabulary are dropped, and measured zeros are drawn from the genes the "
          "dataset measures, so a preselected highly-variable-gene matrix is not a valid input.")
NO_INTERVAL = "No uncertainty is printed for any value under this protocol."
UNEQUAL = ("Systems run under different conditions: Stack uses batch labels at inference, "
           "SCimilarity and scPRINT were trained with cell-type labels, and PCA is fitted to each "
           "atlas. Each evaluation's comparison.adaptation states its system's condition, so results "
           "from different conditions are not compared automatically.")


def benchmark():
    return [record(
        BENCHMARK, "benchmark", "HyCell report benchmark on seven held-out atlases",
        "Scores frozen single-cell embeddings on seven atlases excluded from pretraining, for "
        "biological conservation, batch correction and annotation transfer.",
        {"entity_level": "suite", "version": "HyCell technical report, 2026-11-01",
         "task": "Zero-shot cell embedding for integration and annotation transfer",
         "scope_note": "Eleven pretrained models and PCA, every one rerun by the HyCell authors on "
                       "the same cells and scored by one implementation built on scib-metrics on the "
                       "absolute scale. Atlases are weighted equally in all averages. " + CELL_LEVEL,
         "limitations": [CELL_LEVEL, UNEQUAL, NO_INTERVAL, INPUTS,
                         "Developer-run: the authors chose the atlases, the metrics, the composite "
                         "weights and ran every comparator."],
         "source_locator": "Section 3.1; Tables 2 to 4"},
        links=[{"relation": "evaluates_task", "target_id": "catalog-task-cell-reference-mapping"}])]


def datasets():
    out = []
    for label, (slug, name, text, cells, batches, types) in ATLAS.items():
        out.append(record(
            f"{B}-data-{slug}", "dataset", name,
            f"Held-out evaluation atlas of the HyCell report: {text}.",
            {"reported_name": label, "version": "As assembled for the HyCell report (2026-11-01)",
             "split": f"whole atlas; {batches} batches held out in turn for annotation transfer",
             "total_targets": int(cells.replace(",", "")),
             "scope_note": f"{cells} cells, {batches} batches, {types} cell types (Table 2). Every "
                           "dataset and collection contributing cells to it was excluded from "
                           "HyCell's pretraining corpus. Raw integer counts with curated cell-type "
                           "labels.",
             "source_locator": f"Table 2 row '{label}'; Section 3.1 'Atlases'",
             "missing_metadata": {"manifest": {"reason": "unavailable",
                                               "note": "No cell list or sampling seed is published."}}}))
    out.append(record(
        SUITE, "dataset", "Seven held-out atlases of the HyCell report",
        "The seven held-out atlases taken together, for scores averaged over atlases.",
        {"reported_name": "seven held-out atlases", "version": "As assembled for the HyCell report",
         "split": "seven whole atlases, weighted equally", "total_targets": 167804,
         "scope_note": "Immune, pancreas and lung from scIB, PBMC, brain (prefrontal cortex), the "
                       "cross-tissue immune atlas and AIDA; 167,804 cells in all.",
         "source_locator": "Table 2; Section 3.1"}))
    return out


def protocol(slug, name, description, metric, unit, qualifier, implementation, limits,
             locator, direction="higher", data=None):
    links = [{"relation": "part_of", "target_id": BENCHMARK}]
    if data:
        links.append({"relation": "uses_data", "target_id": data})
    return record(f"{B}-protocol-{slug}", "protocol", f"{name} (HyCell report)", description,
                  {"metric": metric, "metric_direction": direction, "unit": unit,
                   "metric_qualifier": qualifier, "metric_implementation": implementation,
                   "protocol": description, "version": "HyCell technical report, 2026-11-01",
                   "aggregation": "Per atlas, or the unweighted mean over the seven atlases",
                   "source_locator": locator, "limitations": limits,
                   "publication_status": "official_project_source"}, links=links)
