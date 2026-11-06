"""The remaining 19 of the HyPLM report's 32 tasks. Same tuple shape as tasks.TASKS."""

from tasks import LOGIT, MULTI, PROBE_SEQ, RIDGE, new

FLIP = ("Closed-form ridge regression probe on a FLIP split. " + PROBE_SEQ + " The released engine "
        "recommends BF16 rather than INT8 for regressors on near-identical variants such as AAV and "
        "GB1, and the report prints no INT8 value for any regression task.")
SHIFTED = (" Appendix A leaves this split out of every summary statistic: its validation data come "
           "from the training distribution while the test set is strongly shifted, so probe "
           "selection is dominated by noise and numerically equivalent runs of the same model "
           "differ by up to 0.2.")
SPEARMAN = ("spearman-correlation", "unitless")


def flip(label, slug, data_id, split_name, shifted=False):
    return (label, slug, data_id, *SPEARMAN,
            f"Spearman correlation on the FLIP {split_name} split",
            FLIP + (SHIFTED if shifted else ""), None)


TASKS2 = [
    ("EC classification (DGEB)", "ec-classification-dgeb", None, "macro-f1", "fraction",
     "Macro-averaged F1 of Enzyme Commission classification on DGEB, with the layer and "
     "regularisation chosen by 5-fold cross-validation on the training split because this task has "
     "no validation split",
     "Logistic regression probe on mean-pooled frozen representations, selected by 5-fold "
     "cross-validation on the training split.",
     new("DGEB EC classification (HyPLM report)",
         "Enzyme Commission classification task of the DGEB benchmark.", "512 / - / 128",
         "DGEB (West-Roberts et al., 2024)")),
    ("Arch retrieval (DGEB)", "arch-retrieval-dgeb", None, "mean-average-precision-at-5", "fraction",
     "Zero-shot retrieval mean average precision at 5 on DGEB Arch, ranked by cosine similarity "
     "between mean-pooled representations",
     "Zero-shot retrieval by cosine similarity between mean-pooled representations; no probe is "
     "trained.",
     new("DGEB Arch retrieval (HyPLM report)",
         "Archaeal protein retrieval task of the DGEB benchmark.", "2,343 queries", "DGEB")),
    ("Localization, 10-class", "localization-10-class", None, "accuracy", "fraction",
     "Ten-class subcellular localisation accuracy on DeepLoc 1.0 via PEER", LOGIT,
     new("DeepLoc ten-class localisation via PEER (HyPLM report)",
         "DeepLoc 1.0 ten-class subcellular localisation as distributed by PEER.",
         "8,743 / 2,190 / 2,745", "DeepLoc 1.0 via PEER (Xu et al., 2022)")),
    ("Localization, binary", "localization-binary", None, "accuracy", "fraction",
     "Binary localisation accuracy on DeepLoc 1.0 via PEER", LOGIT,
     new("DeepLoc binary localisation via PEER (HyPLM report)",
         "DeepLoc 1.0 binary localisation as distributed by PEER.",
         "not printed (Table 4 prints the ten-class split's sizes)", "DeepLoc 1.0 via PEER")),
    ("Metal-ion binding", "metal-ion-binding", None, "accuracy", "fraction",
     "Metal-ion binding classification accuracy on the split packaged by SaProt", LOGIT,
     new("Metal-ion binding, SaProt packaging (HyPLM report)",
         "Metal-ion binding classification as packaged by SaProt.", "5,068 / 662 / 665",
         "as packaged by SaProt")),
    ("HumanPPI", "humanppi", None, "accuracy", "fraction",
     "Human protein-protein interaction classification accuracy on PEER HumanPPI, with pair "
     "features [a, b, a*b, |a-b|]",
     "L2-regularised logistic regression on the pair features [a, b, a*b, |a-b|] of mean-pooled "
     "frozen representations. " + PROBE_SEQ,
     new("HumanPPI via PEER (HyPLM report)",
         "Human protein-protein interaction pairs as distributed by PEER.", "26,319 / 234 / 180",
         "PEER (Xu et al., 2022)")),
    flip("AAV two-vs-many", "aav-two-vs-many", "flip-dataset-flip-aav-2-vs-rest-split",
         "AAV two-vs-many"),
    flip("AAV low-vs-high", "aav-low-vs-high", "flip-dataset-flip-aav-low-vs-high-split",
         "AAV low-vs-high"),
    flip("GB1 two-vs-rest", "gb1-two-vs-rest", "flip-dataset-flip-gb1-2-vs-rest-split",
         "GB1 two-vs-rest", shifted=True),
    flip("GB1 three-vs-rest", "gb1-three-vs-rest", "flip-dataset-flip-gb1-3-vs-rest-split",
         "GB1 three-vs-rest", shifted=True),
    flip("GB1 low-vs-high", "gb1-low-vs-high", "flip-dataset-flip-gb1-low-vs-high-split",
         "GB1 low-vs-high"),
    flip("Meltome human cell", "meltome-human-cell",
         "flip-dataset-flip-thermostability-human-cell-split", "Meltome human-cell"),
    flip("Meltome mixed", "meltome-mixed", "flip-dataset-flip-thermostability-mixed-split",
         "Meltome mixed"),
    ("Amylase one-to-many", "amylase-one-to-many", None, *SPEARMAN,
     "Spearman correlation on the FLIP2 amylase one-to-many split", FLIP,
     new("Amylase one-to-many (FLIP2, HyPLM report)",
         "Amylase activity regression on the FLIP2 one-to-many split.", "2,574 / 644 / 488",
         "FLIP2")),
    ("Amylase by mutation count", "amylase-by-mutation-count", None, *SPEARMAN,
     "Spearman correlation on the FLIP2 amylase split partitioned by mutation count", FLIP,
     new("Amylase by mutation count (FLIP2, HyPLM report)",
         "Amylase activity regression on the FLIP2 split partitioned by mutation count.",
         "not printed (Table 4 prints the one-to-many split's sizes)", "FLIP2")),
    ("Hydrolase to P06241", "hydrolase-to-p06241", None, *SPEARMAN,
     "Spearman correlation on the FLIP2 cross-protein hydrolase split, training on other "
     "hydrolases and testing on P06241",
     FLIP + SHIFTED,
     new("Hydrolase to P06241 (FLIP2 cross-protein, HyPLM report)",
         "Cross-protein hydrolase regression split of FLIP2, tested on P06241.",
         "11,970 / 2,993 / 9,972", "FLIP2 (cross-protein)")),
    ("Fluorescence", "fluorescence", "lit-protein-20261011-deepprotein-data-fluorescence",
     *SPEARMAN, "Spearman correlation on the TAPE fluorescence regression split",
     "Closed-form ridge regression probe. " + PROBE_SEQ, None),
    ("Stability", "stability", None, *SPEARMAN,
     "Spearman correlation on the TAPE stability regression split",
     "Closed-form ridge regression probe. " + PROBE_SEQ,
     new("Stability (TAPE, HyPLM report)",
         "Protein stability regression as distributed with TAPE.", "21,446 / 5,362 / 27,217",
         "TAPE; Table 4 groups it with fluorescence and prints one set of sizes for both")),
    ("Thermostability", "thermostability", None, *SPEARMAN,
     "Spearman correlation on the Meltome human-cell split as packaged by SaProt, which the report "
     "lists separately from its own FLIP Meltome human-cell row",
     "Closed-form ridge regression probe. " + PROBE_SEQ,
     new("Thermostability, Meltome human cell via SaProt (HyPLM report)",
         "Meltome human-cell thermostability regression as packaged by SaProt.",
         "5,056 / 639 / 1,336",
         "Meltome human cell as packaged by SaProt; kept separate from the FLIP Meltome human-cell "
         "split because the report prints both rows with different values")),
]
