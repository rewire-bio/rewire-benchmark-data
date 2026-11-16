"""Printed table contents of arXiv:2609.18745v1, transcribed by hand.

Every value here is a string exactly as the PDF prints it. `check_tables.py` asserts each row
label and each value against the pdftotext -layout text layer of the pinned PDF before
`build_batch.py` turns them into records, so a typo in this file fails the build.

Table 1's upper block ("ours") is not transcribed here: `check_tables.py` asserts that it is
cell-for-cell identical to the matching four columns of Table 2, so the values are stored once,
from Table 2, which prints all ten metrics.
"""

# ---------------------------------------------------------------- Table 2 (page 12, Appendix A)
# "EvoFlows' section 4.2 reproduced results, on all ten metrics, both seed families, one frame:
#  20 templates x 20 variants, holdout 200, agreement ceiling 300 real homologs."
TABLE2_COLUMNS = [
    "edits",
    "pairw. Lev.",
    "MMD",
    "KL pos.",
    "KL pool.",
    "JS pos.",
    "cov. agr.",
    "MIP agr.",
    "ΔH",
    "prof. LL",
]

# Printed direction row of Table 2, in column order.
TABLE2_DIRECTION_ROW = ["–", "≈", "↓", "↓", "↓", "↓", "↑", "↑", "→0", "↑"]

# Row labels in printed order, per family block.
TABLE2_ROWS = ["EditJumps", "rand. mut.", "rand. pair.", "EvoDiff", "Evotune", "Evotune-f", "BF-DiT", "BF-ESM"]

TABLE2 = {
    "ty1": {
        "EditJumps": ["4.58", "24.47", "0.98", "0.07", "0.50", "1.26", "0.91", "0.83", "0.07", "-64.01"],
        "rand. mut.": ["4.81", "30.01", "1.41", "0.16", "0.77", "2.23", "0.85", "0.66", "0.15", "–"],
        "rand. pair.": ["23.38", "23.53", "0.60", "0.03", "0.14", "0.54", "0.98", "0.94", "0.07", "–"],
        "EvoDiff": ["2.96", "22.85", "0.97", "0.07", "0.61", "1.38", "0.89", "0.78", "0.02", "-59.15"],
        "Evotune": ["4.47", "22.61", "0.98", "0.06", "0.54", "1.14", "0.91", "0.81", "0.01", "-57.49"],
        "Evotune-f": ["5.00", "25.22", "1.09", "0.09", "0.53", "1.40", "0.87", "0.74", "0.09", "-67.54"],
        "BF-DiT": ["19.77", "33.76", "1.58", "0.22", "0.91", "2.17", "0.38", "0.23", "0.25", "-95.28"],
        "BF-ESM": ["31.69", "44.28", "4.31", "0.76", "10.65", "6.28", "0.12", "0.15", "0.33", "-155.11"],
    },
    "her2vh": {
        "EditJumps": ["4.08", "24.73", "1.02", "0.05", "0.63", "1.03", "0.93", "0.87", "0.08", "-59.03"],
        "rand. mut.": ["3.89", "29.08", "1.38", "0.12", "0.79", "1.89", "0.90", "0.78", "0.15", "–"],
        "rand. pair.": ["23.25", "23.02", "0.47", "0.03", "0.10", "0.47", "0.98", "0.94", "0.10", "–"],
        "EvoDiff": ["2.61", "23.23", "1.11", "0.06", "0.42", "1.18", "0.91", "0.82", "0.04", "-55.03"],
        "Evotune": ["3.83", "22.77", "0.99", "0.05", "0.37", "1.02", "0.93", "0.83", "0.03", "-52.87"],
        "Evotune-f": ["4.00", "25.00", "1.15", "0.07", "0.59", "1.21", "0.91", "0.81", "0.10", "-62.17"],
        "BF-DiT": ["22.38", "37.54", "2.09", "0.26", "1.70", "2.67", "0.38", "0.23", "0.35", "-104.87"],
        "BF-ESM": ["33.29", "45.53", "4.69", "0.71", "14.47", "6.30", "0.14", "0.18", "0.40", "-153.82"],
    },
}

# Arms whose identity the source states. BF-DiT and BF-ESM are printed only in this table and
# are defined nowhere in the paper, the repository (including docs/findings.md) or the model
# card, so their 20 cells are not stored. See notes.md, "Gaps".
TABLE2_ARMS_STORED = ["EditJumps", "rand. mut.", "rand. pair.", "EvoDiff", "Evotune", "Evotune-f"]
TABLE2_ARMS_NOT_STORED = ["BF-DiT", "BF-ESM"]

# ----------------------------------------------------- Table 1, lower block (page 5), published
# "the original - the same two families, its own reported values"
TABLE1_LOWER_COLUMNS = ["edits/seq", "diversity", "MMD", "KL x10^3"]
TABLE1_LOWER_ROWS = [
    "random pairing",
    "EvoFlows",
    "evotuning",
    "evotuning (forced)",
    "EvoDiff-MSA",
    "random mutations",
]
# Printed as pairs: Ty1 then HER2 for each of the four metric groups.
TABLE1_LOWER = {
    "random pairing": {"edits/seq": ["30.52", "93.86"], "diversity": ["30.28", "93.27"], "MMD": ["0.38", "0.61"], "KL x10^3": ["9.84", "8.72"]},
    "EvoFlows": {"edits/seq": ["14.64", "35.27"], "diversity": ["35.59", "90.86"], "MMD": ["1.03", "1.57"], "KL x10^3": ["21.49", "23.17"]},
    "evotuning": {"edits/seq": ["2.54", "11.75"], "diversity": ["30.99", "96.14"], "MMD": ["0.40", "0.66"], "KL x10^3": ["10.40", "10.66"]},
    "evotuning (forced)": {"edits/seq": ["15.30", "38.67"], "diversity": ["41.07", "114.67"], "MMD": ["1.88", "2.65"], "KL x10^3": ["54.79", "36.48"]},
    "EvoDiff-MSA": {"edits/seq": ["4.43", "13.80"], "diversity": ["30.01", "93.06"], "MMD": ["0.42", "0.66"], "KL x10^3": ["11.63", "10.16"]},
    "random mutations": {"edits/seq": ["13.94", "35.09"], "diversity": ["48.79", "133.34"], "MMD": ["2.35", "3.70"], "KL x10^3": ["80.05", "86.68"]},
}

# ------------------------------------------------- Table 1, upper block (page 5), ours; checked
# Transcribed only so that check_tables.py can assert it duplicates Table 2. Not stored.
TABLE1_UPPER = {
    "random pairing": {"edits/seq": ["23.38", "23.25"], "diversity": ["23.53", "23.02"], "MMD": ["0.60", "0.47"], "KL x10^3": ["0.14", "0.10"]},
    "EditJumps": {"edits/seq": ["4.58", "4.08"], "diversity": ["24.47", "24.73"], "MMD": ["0.98", "1.02"], "KL x10^3": ["0.50", "0.63"]},
    "evotuning": {"edits/seq": ["4.47", "3.83"], "diversity": ["22.61", "22.77"], "MMD": ["0.98", "0.99"], "KL x10^3": ["0.54", "0.37"]},
    "evotuning (forced)": {"edits/seq": ["5.00", "4.00"], "diversity": ["25.22", "25.00"], "MMD": ["1.09", "1.15"], "KL x10^3": ["0.53", "0.59"]},
    "EvoDiff-MSA": {"edits/seq": ["2.96", "2.61"], "diversity": ["22.85", "23.23"], "MMD": ["0.97", "1.11"], "KL x10^3": ["0.61", "0.42"]},
    "random mutations": {"edits/seq": ["4.81", "3.89"], "diversity": ["30.01", "29.08"], "MMD": ["1.41", "1.38"], "KL x10^3": ["0.77", "0.79"]},
}

# The Table 1 upper-block row label that names the same arm as a Table 2 row label.
TABLE1_TO_TABLE2_ROW = {
    "random pairing": "rand. pair.",
    "EditJumps": "EditJumps",
    "evotuning": "Evotune",
    "evotuning (forced)": "Evotune-f",
    "EvoDiff-MSA": "EvoDiff",
    "random mutations": "rand. mut.",
}
# The Table 1 column that holds the same metric as a Table 2 column.
TABLE1_TO_TABLE2_COLUMN = {
    "edits/seq": "edits",
    "diversity": "pairw. Lev.",
    "MMD": "MMD",
    "KL x10^3": "KL pool.",
}

# ------------------------------------------------------------ Table 4 (page 16), ceiling-normal
# "Ceiling-normalized performance of EditJumps against EvoFlows."
TABLE4_ROWS = [
    "Covariance (% of ceiling)",
    "MIP (% of ceiling)",
    "Positional JS† (× floor)",
    "Pairwise Distance‡",
]
TABLE4 = {
    "Covariance (% of ceiling)": {"EditJumps (Ours)": "84.3", "EvoFlows (Published)": "98.4"},
    "MIP (% of ceiling)": {"EditJumps (Ours)": "78.8", "EvoFlows (Published)": "95.5"},
    "Positional JS† (× floor)": {"EditJumps (Ours)": "2.68 ± 0.10", "EvoFlows (Published)": "1.80"},
    "Pairwise Distance‡": {"EditJumps (Ours)": "1.070 ± 0.011", "EvoFlows (Published)": "1.00"},
}

# --------------------------------------- Appendix E prose, "Sample-Size Dependency" (page 16)
# "Scoring real homologs against real homologs yields covariance scores of 0.790 at N = 20,
#  0.921 at N = 100, and saturates at 0.985 at N = 800."
COVARIANCE_BY_REFERENCE_SIZE = [("20", "0.790"), ("100", "0.921"), ("800", "0.985")]
