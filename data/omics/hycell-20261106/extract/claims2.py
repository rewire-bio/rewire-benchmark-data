"""Benchmark claims for HyCell and the claim builder."""

from assess import BENCHMARK
from claims import M, MODEL_CLAIMS, R
from evidence import REVIEW
from models import MODEL
from sources import B, record

BENCHMARK_CLAIMS = [
    ("excluded-atlases", R + M, "training_evaluation_overlap", "The seven atlases excluded from "
     "pretraining are the scIB human immune, pancreas and lung atlases (integer-count parts), PBMC "
     "from 10x Genomics pbmc4k and pbmc8k, the healthy donors of the MultiVINE brain vasculature "
     "atlas, a 40,322-cell sample of the cross-tissue immune atlas of Dominguez Conde et al. and a "
     "41,140-cell sample of the Asian Immune Diversity Atlas. Every contributing dataset and "
     "collection was removed from the corpus.", "Section 3.1 'Atlases'; Table 2; Section 2.5"),
    ("composite-weights", R, "scoring", "S = 0.3 Bio + 0.2 Batch + 0.25 LR + 0.25 kNN, which weights "
     "the scIB total (0.6 Bio + 0.4 Batch) and annotation transfer equally; atlases are weighted "
     "equally in all averages.", "Section 3.1 'Metrics'"),
    ("headline-level", R, "headline", "The report calls HyCell's S of 0.735 'level with' Stack's "
     "0.736 and does not claim a win; it prints no uncertainty for either.",
     "Abstract; Section 3.2 'Overall score'"),
    ("readme-best-s", M, "headline", "The README's results table marks Stack's S of 0.736 in bold "
     "as the best value of the column.", "README 'Recorded result' table, column S"),
    ("stack-condition", R, "comparison_condition", "Stack encodes sets of 256 cells; its released "
     "tutorial orders cells by donor, and the authors encode the cells of each batch together, so "
     "Stack uses batch labels at inference.", "Section 3.1 'Models'"),
    ("label-trained", R, "comparison_condition", "SCimilarity and scPRINT are trained with "
     "cell-type labels.", "Section 3.1 'Models'"),
    ("pca-condition", R, "comparison_condition", "PCA is fitted to each atlas on 2,000 highly "
     "variable genes of the log-normalised counts with 50 components, as a reference without "
     "pretraining.", "Section 3.1 'Models'"),
    ("cell-level-scope", R + M, "scope", "The benchmark measures cell-level tasks; sample-level "
     "tasks such as predicting a donor's disease state, which Stack's use of the other cells of a "
     "sample helps, are not part of it.", "Section 3.2 'Overall score'; README 'Recorded result'"),
    ("bio-first-atlases", R, "ranking", "Among self-supervised models HyCell ranks first on "
     "biological conservation on five of the seven atlases and shares first place on the brain "
     "atlas.", "Section 3.2 'Cell identity'; Figure 1b"),
    ("lr-gap", R, "ranking", "In annotation transfer HyCell is second on logistic regression, "
     "0.002 behind scFoundation.", "Section 3.2 'Overall score'"),
    ("knn-gap", R, "ranking", "In annotation transfer HyCell is second on kNN, 0.006 behind "
     "batch-grouped Stack.", "Section 3.2 'Overall score'"),
    ("size-range", R, "scope", "The models within 0.03 of HyCell in S have 2 to 14 times more "
     "parameters.", "Section 3.2 'Size'"),
    ("cd4-others-bound", R, "downstream", "On the naive-effector CD4 split every other embedding, "
     "Stack and PCA included, reaches ARI at most 0.031.", "Section 4.1"),
    ("cd4-chemistry-range", R, "downstream", "For seven of the other embeddings the CD4 split "
     "follows sequencing chemistry instead, with NMI between 0.31 and 0.55.", "Section 4.1"),
    ("gd-published-bound", R, "downstream", "On the gamma-delta T against tissue-resident CD8 T "
     "split the published models reach ARI at most 0.06.", "Section 4.1"),
    ("pseudotime-vs-pca", R, "downstream", "Eight of the ten published models order the B-cell "
     "stages less faithfully than PCA of the counts.", "Section 4.2"),
    ("median-pt-naive", R, "downstream", "In HyCell the median pseudotime of naive B cells is "
     "0.04.", "Section 4.2"),
    ("median-pt-gc", R, "downstream", "In HyCell the median pseudotime of germinal-centre B cells "
     "is 0.55.", "Section 4.2"),
    ("median-pt-plasmablast", R, "downstream", "In HyCell the median pseudotime of plasmablasts is "
     "0.84.", "Section 4.2"),
    ("median-pt-plasma", R, "downstream", "In HyCell the median pseudotime of plasma cells is "
     "0.92.", "Section 4.2"),
    ("finetune-lr-batches", R, "fine_tuning", "The fine-tuned annotator is ahead of logistic "
     "regression on 19 of the 20 held-out batches.", "Section 5"),
    ("finetune-knn-batches", R, "fine_tuning", "The fine-tuned annotator is ahead of kNN on 17 of "
     "the 20 held-out batches.", "Section 5"),
]


def build_claims():
    out = []
    for subject, tag, claims in [(MODEL, "hycell", MODEL_CLAIMS),
                                 (BENCHMARK, "benchmark", BENCHMARK_CLAIMS)]:
        for slug, sources, field, value, locator in claims:
            out.append(record(
                f"{B}-claim-{tag}-{slug}", "claim", f"HyCell report: {slug.replace('-', ' ')}",
                "Descriptive fact read from the pinned sources at the locator given; not a "
                "measurement on a benchmark panel.",
                {"field": field, "value": value, "source_locator": locator, "review": dict(REVIEW)},
                links=[{"relation": "subject", "target_id": subject}], sources=sources))
    return out
