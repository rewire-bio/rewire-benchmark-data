"""RNAGym fitness leaderboard v0.1.1 (MarksLab-DasLab/RNAGym, leaderboard/fitness/README.md at commit
2828cf99316d75daaa8d832a2573cbb25bbd35fe).

Both Markdown tables of the leaderboard README: the main signed-Spearman leaderboard and the AIDO.RNA scaling
table. The AIDO.RNA-1.6B scaling row repeats the main-table AIDO.RNA (1.6B) row and is not extracted twice.
The two CSV files the README links to are pinned and cross-checked: each printed value must equal the CSV value
rounded to four decimals.

Usage: python3 -I extract_rnagym.py <README.md> <leaderboard_signed_3ncRNA.csv> <aido_rna_scaling.csv> <batch-folder>
"""
import sys, os, re, json, csv
from decimal import Decimal, ROUND_HALF_EVEN
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, finalise, sha256, slug, num

readme, csv_main, csv_scale, folder = sys.argv[1:5]
COMMIT = "2828cf99316d75daaa8d832a2573cbb25bbd35fe"
SHA = sha256(readme)
assert SHA == "c947a7a45a53cc4106323a3bcae1bb3fa84276bc07df89493cb501735711b891", SHA
assert sha256(csv_main) == "b72459e550a4daac53459b002b7f38246185dc50647656c104a56a98882f3a99"
assert sha256(csv_scale) == "c5b2e3f573a10036c2fb35118be363e5433af0150d00e8447ef534b2d36a7949"
RAW = f"https://raw.githubusercontent.com/MarksLab-DasLab/RNAGym/{COMMIT}/leaderboard/fitness/README.md"

P = "lit-rna-20261011-rnagym"
b = Batch(folder, P)
SRC = b.source(P + "-source-leaderboard-v0-1-1", "RNAGym fitness leaderboard (v0.1.1), leaderboard/fitness/README.md", {
    "url": f"https://github.com/MarksLab-DasLab/RNAGym/blob/{COMMIT}/leaderboard/fitness/README.md", "artifact_url": RAW,
    "version": f"Commit {COMMIT} (2026-08-14, 'Update fitness leaderboard v0.2 models'); leaderboard labelled v0.1.1",
    "retrieved_at": "2026-10-11T21:40:04Z", "artifact_sha256": SHA, "publication_status": "official_project_source",
    "licence": "MIT (repository LICENSE at the same commit)", "media_type": "text/markdown",
    "limitations": ["Mutable official repository; the hash describes the file at the pinned commit.",
                    "The README links mRNA/leaderboard_signed_mRNA.csv, which is not present at this commit; mRNA assay results were not extracted.",
                    "The table label 'RNA-ERNIE' and the CSV label 'RNAErnie' are mapped to RNAErnie (Wang et al., Nature Machine Intelligence 2024), the model the repository README lists; ERNIE-RNA is a different model.",
                    "Model checkpoints other than the AIDO.RNA scaling series and Evo 2 sizes are not named in the leaderboard."]})
SIDS = [SRC]

def review(loc):
    return extraction_review(["deterministic-table-parse"],
        f"Parsed the Markdown table rows of the pinned README with extract/extract_rnagym.py and checked each printed value against the linked CSV at the same commit rounded half-even to four decimals. {loc}", SHA, RAW)

text = open(readme, encoding="utf8").read()
def md_table(after_heading):
    i = text.index(after_heading)
    lines = text[i:].split("\n")
    start = next(k for k, l in enumerate(lines) if l.startswith("|"))
    rows = []
    for l in lines[start:]:
        if not l.startswith("|"):
            break
        rows.append([c.strip() for c in l.strip().strip("|").split("|")])
    return rows

main = md_table("## Leaderboard: signed Spearman, macro-mean over 3 ncRNA categories")
assert main[0] == ["Rank", "Model", "Ribozyme (n=26)", "tRNA (n=3)", "Aptamer (n=2)", "Macro (3 ncRNA)"], main[0]
scale = md_table("## AIDO.RNA across model sizes")
assert scale[0] == ["Checkpoint", "Params", "Ribozyme", "tRNA", "Aptamer", "Macro"], scale[0]

csvm = {r["model"]: r for r in csv.DictReader(open(csv_main))}
csvs = {r["checkpoint"]: r for r in csv.DictReader(open(csv_scale))}
CSVKEY = {"Evo 2 (40B)": "evo2_40b", "RNA-ERNIE": "RNAErnie", "Evo 2 (7B)": "evo2", "AIDO.RNA (1.6B)": "aido_rna", "RNAGenesis": "rnagenesis",
          "RiNALMo": "rinalmo", "Evo 1.5": "evo1.5", "Nucleotide Transformer": "NT", "RNA-FM": "RNA-FM", "Orthrus": "orthrus", "Evo 1": "evo1", "GenSLM": "GenSLM"}
def r4(x):
    return str(Decimal(x).quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN))

# label -> (family id or new family name, checkpoint/version text)
FAM = {"Evo 2 (40B)": ("discovery-model-evo-2", "40B"), "Evo 2 (7B)": ("discovery-model-evo-2", "7B"),
       "RNA-ERNIE": ("gfm2-20261011-you2026-model-rnaernie", None), "AIDO.RNA (1.6B)": ("lit-rna-20261011-rnalm-zeroshot-model-aido-rna", "AIDO.RNA-1.6B"),
       "RNAGenesis": ("RNAGenesis", None), "RiNALMo": ("lit-rna-20261011-rnalm-zeroshot-model-rinalmo", None),
       "Evo 1.5": ("lit-genomics-20261011-geneb-model-evo", "Evo 1.5"), "Nucleotide Transformer": ("discovery-model-nucleotide-transformer", None),
       "RNA-FM": ("discovery-model-rna-fm", None), "Orthrus": ("Orthrus", None), "Evo 1": ("lit-genomics-20261011-geneb-model-evo", "Evo 1"),
       "GenSLM": ("GenSLM", None)}
for ck in ("AIDO.RNA-1M-MARS", "AIDO.RNA-25M-MARS", "AIDO.RNA-300M-MARS", "AIDO.RNA-650M"):
    FAM[ck] = ("lit-rna-20261011-rnalm-zeroshot-model-aido-rna", ck)
NEW = {"RNAGenesis": "RNAGenesis RNA foundation model, as listed on the RNAGym fitness leaderboard.",
       "Orthrus": "Orthrus mature mRNA foundation model, as listed on the RNAGym fitness leaderboard.",
       "GenSLM": "GenSLM genome-scale language model, as listed on the RNAGym fitness leaderboard."}
fam_ids = {}
def family(f):
    if f not in NEW:
        return f
    if f not in fam_ids:
        fam_ids[f] = b.entity("model", b.rid("model", f), f, NEW[f], SIDS,
                              {"reported_name": f, "entity_level": "family", "source_locator": "Leaderboard table row '" + f + "'",
                               "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record"}}}, method_types=["foundation_model"])
    return fam_ids[f]

# Autoregressive (Evo, GenSLM) and contrastive (Orthrus) models: the README's scoring convention does not cover them.
NOT_MLM = {"lit-rna-20261011-rnagym-config-" + k + "-rnagym-v0-1-1" for k in ("evo-1", "evo-1-5", "evo-2-7b", "evo-2-40b", "genslm", "orthrus")}
cfgs = {}
def config(label, params=None):
    if label in cfgs:
        return cfgs[label]
    f, ver = FAM[label]
    attrs = {"reported_name": label, "foundation_model_eligible": True,
             "parameters": "Zero-shot. Masked language models scored by the masked-marginal log-likelihood ratio, each mutated position masked one at a time in the variant sequence and summed over mutated positions (leaderboard 'Scoring convention')",
             "access_reuse": "Scoring scripts on the RNAGym v0.2 branch (leaderboard README 'Scoring scripts')",
             "source_locator": "Leaderboard README row '" + label + "'" + ("; AIDO.RNA scaling table" if label.startswith("AIDO.RNA-") else "")}
    if ver:
        attrs["version"] = ver
    else:
        attrs["missing_metadata"] = {"version": {"reason": "unreported", "note": "The leaderboard does not name the checkpoint"}}
    if params:
        attrs["model_identity_note"] = f"Params column: {params}M"
    rid = b.rid("config", label, "rnagym-v0-1-1")
    if rid in NOT_MLM:  # review G1
        attrs["parameters"] = "Zero-shot. The leaderboard README states the scoring convention for masked language models only (masked-marginal log-likelihood ratio, 'Scoring convention'); the convention used for this model is not stated there."
    b.entity("configuration", rid, f"{label} (RNAGym fitness leaderboard v0.1.1)", f"{label} as scored zero-shot on the RNAGym fitness leaderboard v0.1.1.",
             SIDS, attrs, method_types=["foundation_model"], links=[{"relation": "configuration_of", "target_id": family(f)}])
    cfgs[label] = rid
    return rid

BENCH = b.entity("benchmark", b.rid("benchmark", "rnagym-fitness-leaderboard-v0-1-1"), "RNAGym fitness leaderboard v0.1.1",
    "Official RNAGym zero-shot fitness leaderboard: signed Spearman correlation between model scores and DMS fitness on 31 ncRNA assays (26 ribozyme, 3 tRNA, 2 aptamer), macro-averaged over the three categories.",
    SIDS, {"entity_level": "suite", "version": "v0.1.1 at commit " + COMMIT, "task": "Zero-shot ncRNA mutational fitness prediction",
           "scope_note": "mRNA coding (37) and splicing (2) assays are excluded from v0.1.1. Signed, not absolute, Spearman.",
           "source_locator": "leaderboard/fitness/README.md, metric note and 'Why we now exclude the mRNA assays'",
           "limitations": ["The leaderboard notes that ranks differing by less than about 0.01 should not be read as meaningful separations.",
                           "99.4% of ncRNA variants are multi-mutants; scores depend on the scoring convention."]})

CATS = {"Ribozyme": ("ribozyme", 26), "tRNA": ("trna", 3), "Aptamer": ("aptamer", 2)}
data_ids = {k: b.entity("dataset", b.rid("data", v[0]), f"RNAGym {k} DMS assays ({v[1]})", f"The {v[1]} RNAGym {k} deep mutational scanning assays used by the v0.1.1 fitness leaderboard.", SIDS,
                        {"version": "RNAGym v0.1.1", "split": "Whole assays (zero-shot)", "source_locator": "Leaderboard README 'Notes'"}) for k, v in CATS.items()}
data_ids["Macro"] = b.entity("dataset", b.rid("data", "ncrna-31"), "RNAGym ncRNA DMS assays (31)", "All 31 ncRNA DMS assays of the v0.1.1 fitness leaderboard (26 ribozyme, 3 tRNA, 2 aptamer).", SIDS,
                             {"version": "RNAGym v0.1.1", "split": "Whole assays (zero-shot)", "source_locator": "Leaderboard README 'Notes'"})
protos = {}
for k in list(CATS) + ["Macro"]:
    qual = "macro-mean over 3 ncRNA categories (equal category weights)" if k == "Macro" else f"mean signed Spearman over the {CATS[k][1]} {k} assays"
    protos[k] = b.entity("protocol", b.rid("protocol", "signed-spearman", k), f"RNAGym v0.1.1 fitness, signed Spearman, {k if k != 'Macro' else 'macro over 3 ncRNA categories'}",
        f"Zero-shot signed Spearman correlation between model score and measured DMS fitness; {qual}.", SIDS,
        {"protocol": f"Score every variant zero-shot, compute signed Spearman per assay, then {qual}.", "version": "RNAGym v0.1.1",
         "metric": "spearman-correlation", "metric_direction": "higher", "unit": "unitless", "metric_qualifier": qual,
         "source_locator": "Leaderboard README metric note and table column '" + k + "'",
         "limitations": ["Signed Spearman; not comparable with absolute Spearman values reported elsewhere, including Wang et al. 2026 on 31 RNAGym ncRNA assays."]},
        links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": data_ids[k]}])

def add(label, col, printed, csvval, loc, row_i, params=None):
    assert r4(csvval) == printed, (label, col, printed, csvval)
    c = config(label, params)
    e = b.rid("eval", label, col)
    b.evaluation(e, f"{label} on RNAGym v0.1.1 fitness ({col})", SIDS, c, protos[col], data_ids[col], "independent_paper",
                 {"protocol_id": protos[col], "dataset_version": "RNAGym v0.1.1", "split": "Whole assays (zero-shot)", "population": None,
                  "inputs": "Wild-type and variant RNA sequences", "adaptation": "Zero-shot; masked-marginal log-likelihood ratio for masked language models",
                  "metric_implementation": "Signed Spearman (performance_fitness.py --type ncRNA on branch v0.2)",
                  "aggregation": "Macro-mean of three category means" if col == "Macro" else "Mean over assays in the category", "budget": None}, loc,
                 extra={"limitations": ["Run by the RNAGym maintainers with their scoring scripts, not by the model developers."]})
    b.result(b.rid("result", label, col), f"{label} RNAGym {col} signed Spearman", SRC, SIDS, e, printed, "spearman-correlation", "higher", "unitless", loc,
             review(f"Row {row_i}."), qualifier=("macro-mean over 3 ncRNA categories (equal category weights)" if col == "Macro" else f"mean signed Spearman over the {CATS[col][1]} {col} assays"))

COLS = ["Ribozyme", "tRNA", "Aptamer", "Macro"]
CSVCOL = {"Ribozyme": "Ribozyme", "tRNA": "tRNA", "Aptamer": "Aptamer", "Macro": "macro_3ncRNA"}
assert len(main) == 14, len(main)
for i, row in enumerate(main[2:], 1):
    assert len(row) == 6 and row[0] == str(i), row
    label = row[1]
    for col, v in zip(COLS, row[2:]):
        add(label, col, v, csvm[CSVKEY[label]][CSVCOL[col]], f"leaderboard/fitness/README.md, main leaderboard table, row '{label}', column '{main[0][COLS.index(col) + 2]}'", i)
assert len(scale) == 7, len(scale)
for i, row in enumerate(scale[2:], 1):
    ck = row[0]
    if ck == "AIDO.RNA-1.6B":
        assert row[2:] == [r4(csvm["aido_rna"][CSVCOL[c]]) for c in COLS], row  # repeats the main-table row
        continue
    for col, v in zip(COLS, row[2:]):
        add(ck, col, v, csvs[ck][CSVCOL[col]], f"leaderboard/fitness/README.md, 'AIDO.RNA across model sizes' table, row '{ck}', column '{scale[0][COLS.index(col) + 2]}'", i, params=row[1])

assert NOT_MLM <= set(cfgs.values()), NOT_MLM - set(cfgs.values())
finalise(b.records, "reviewer-ro-1",
         "Re-fetched README, CSVs and LICENSE at commit 2828cf9 and matched their SHA-256. An independent Markdown table parse matched all 64 printed and numeric values and locators; all 64 were also read against the rendered table.")

counts = b.write()
print(json.dumps(counts))
