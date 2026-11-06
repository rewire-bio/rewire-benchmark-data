"""The sixteen HyCell protocols, one per metric."""

from assess import CELL_LEVEL, INPUTS, NO_INTERVAL, UNEQUAL, protocol
from sources import B

CT = f"{B}-data-cross-tissue-immune"
BIO = ("isolated-label score, NMI and ARI of k-means and of Leiden clusters against the cell "
       "types, cell-type silhouette and cLISI")
BATCH = "batch silhouette, iLISI, kBET, graph connectivity and principal-component regression"
SCIB = "One implementation built on scib-metrics, on the absolute scale without rescaling across methods."
LOO = ("Each batch is held out in turn; the classifier is trained on the remaining batches and "
       "macro-F1 over the cell types of the held-out batch is averaged over held-out batches.")
DOWN = ("A single downstream analysis on the cross-tissue immune atlas, chosen and run by the "
        "authors; one atlas, so it does not establish a general property.")


def protocols():
    base = [CELL_LEVEL, UNEQUAL, NO_INTERVAL]
    p = [
        protocol("composite-score", "Composite score S",
                 "Combine biological conservation, batch correction and annotation transfer into "
                 "one weighted score per atlas.", "weighted-composite-score", "unitless",
                 "S = 0.3 Bio + 0.2 Batch + 0.25 LR + 0.25 kNN, the authors' weighting, which gives "
                 "the scIB total (0.6 Bio + 0.4 Batch) and annotation transfer equal weight; per "
                 "atlas or averaged over the seven atlases",
                 "Weighted sum of the four component scores of this benchmark. " + SCIB,
                 base + ["A chosen weighting, not a measured quantity: another choice of weights "
                         "can reorder models whose components differ, as HyCell and Stack's do "
                         "(Bio 0.700 against 0.657, Batch 0.527 against 0.596).",
                         "Table 4 prints S per atlas without its four components, so the per-atlas "
                         "weighting cannot be checked from the report.", INPUTS],
                 "Section 3.1 'Metrics'; Tables 3 and 4"),
        protocol("bio-conservation", "scIB biological conservation",
                 "Score how well a cell embedding preserves cell-type structure.",
                 "scib-bio-conservation-score", "unitless",
                 f"Mean of seven scIB biological-conservation metrics ({BIO}), per atlas or averaged "
                 "over the seven atlases", SCIB, base + [INPUTS],
                 "Section 3.1 'Metrics'; Table 3; Figure 1b"),
        protocol("batch-correction", "scIB batch correction",
                 "Score how well a cell embedding mixes batches.", "scib-batch-correction-score",
                 "unitless", f"Mean of five scIB batch-correction metrics ({BATCH}), per atlas or "
                 "averaged over the seven atlases", SCIB,
                 base + ["Removing batch and donor structure is what this score rewards; the "
                         "report notes that properties shared by all cells of a donor, such as sex "
                         "or disease state, are better read from embeddings aggregated per donor.",
                         INPUTS], "Section 3.1 'Metrics'; Table 3; Section 3.2"),
        protocol("annotation-transfer-lr", "Annotation transfer with logistic regression",
                 "Transfer cell-type labels to a held-out batch with a logistic-regression "
                 "classifier on the embedding.", "macro-f1", "fraction",
                 "Macro-F1 of a logistic-regression classifier trained on the other batches, over "
                 "the cell types of the held-out batch, averaged over held-out batches; per atlas "
                 "or averaged over the seven atlases", LOO, base + [INPUTS],
                 "Section 3.1 'Metrics'; Tables 3 and 5"),
        protocol("annotation-transfer-knn", "Annotation transfer with 15-nearest neighbours",
                 "Transfer cell-type labels to a held-out batch with a 15-nearest-neighbour "
                 "classifier on the embedding.", "macro-f1", "fraction",
                 "Macro-F1 of a 15-nearest-neighbour classifier trained on the other batches, over "
                 "the cell types of the held-out batch, averaged over held-out batches; per atlas "
                 "or averaged over the seven atlases", LOO, base + [INPUTS],
                 "Section 3.1 'Metrics'; Tables 3 and 5"),
        protocol("annotation-finetuned", "Annotation of a held-out batch after fine-tuning",
                 "Fine-tune the model on the labelled other batches and predict the cell types of "
                 "the held-out batch.", "macro-f1", "fraction",
                 "Macro-F1 over the cell types of the held-out batch after fine-tuning on the other "
                 "batches, averaged over held-out batches", LOO + " The system is fine-tuned rather "
                 "than frozen.", [NO_INTERVAL, "HyCell only, on four of the seven atlases; no other "
                 "model was fine-tuned, so this compares HyCell with its own frozen embeddings."],
                 "Section 5; Table 5"),
    ]
    down = [
        ("cd4-split-ari", "Naive against effector CD4 T-cell split, ARI",
         "adjusted-rand-index", "higher",
         "ARI between a two-group k-means split of the embeddings of the atlas's 2,778 CD4 T cells "
         "(1,343 naive or central-memory, 1,435 effector or effector-memory) and the naive-effector "
         "annotation, over all cells"),
        ("cd4-split-ari-within-donor", "Naive against effector CD4 T-cell split within donors, ARI",
         "adjusted-rand-index", "higher",
         "The same two-group split made within each donor, where chemistry no longer varies; mean "
         "ARI over the 12 donors"),
        ("cd4-split-nmi-chemistry", "CD4 T-cell split against sequencing chemistry, NMI",
         "normalized-mutual-information", "lower",
         "NMI between the two-group k-means split of the CD4 T cells and their sequencing chemistry; "
         "lower means the split ignores chemistry, which is what the analysis seeks"),
        ("gd-t-split-ari", "gamma-delta T against tissue-resident CD8 T split, ARI",
         "adjusted-rand-index", "higher",
         "ARI between a two-group split of gamma-delta T cells and tissue-resident CD8 T cells and "
         "their annotation"),
        ("pseudotime-stage-spearman", "B-cell to plasma-cell pseudotime ordering, all cells",
         "spearman-correlation", "higher",
         "Spearman correlation between diffusion pseudotime and differentiation stage (naive B, "
         "germinal-centre B, plasmablast, plasma cell) over the 3,751 cells of these states, rooted "
         "at the medoid of the 50 cells with the highest naive-B marker score (TCL1A, IGHD, FCER2)"),
        ("pseudotime-stage-spearman-donor-mean", "B-cell to plasma-cell pseudotime ordering, donor mean",
         "spearman-correlation", "higher",
         "The same Spearman correlation between pseudotime and stage computed per donor and "
         "averaged over the 12 donors"),
        ("decoder-fold-change-spearman", "Decoded against counted fold change, plasma against naive B",
         "spearman-correlation", "higher",
         "Spearman correlation between the decoder's fold change and the counted pseudobulk fold "
         "change from naive B to plasma cells over the 12,879 genes detected in at least 1% of either "
         "state"),
    ]
    for slug, name, metric, direction, qualifier in down:
        p.append(protocol(slug, name, f"Measure: {name.lower()} on the cross-tissue immune atlas.",
                          metric, "unitless", qualifier, "Frozen embeddings of every model; "
                          "Scanpy diffusion pseudotime where pseudotime is used.",
                          [DOWN, NO_INTERVAL, UNEQUAL], "Section 4; Figure 4",
                          direction=direction, data=CT))
    for slug, pair in [("donor-consistency-plasma", "naive B to plasma cells"),
                       ("donor-consistency-monocyte", "classical to nonclassical monocytes"),
                       ("donor-consistency-cd4", "naive to effector CD4 T cells")]:
        p.append(protocol(slug, f"Gene-program consistency across donors, {pair}",
                          f"Compare each donor's gene program for {pair} with the program of the "
                          "other donors.", "spearman-correlation", "unitless",
                          f"Mean over donors of the Spearman correlation between one donor's "
                          f"program for {pair} and the program of all other donors, from the HyCell "
                          "decoder or from pseudobulk counts",
                          "Programs from the decoder use the unknown-dataset code; counted programs "
                          "use pseudobulk counts.", [DOWN, NO_INTERVAL],
                          "Section 4.3; Figure 5c", data=CT))
    return p
