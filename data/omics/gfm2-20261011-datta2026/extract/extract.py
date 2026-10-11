"""Build the Datta et al. 2026 batch (frozen genomic language model representations) from the pinned arXiv PDF.

Usage: python3 -I extract.py <article.txt from `pdftotext -layout article.pdf`>
Parses Table 1 (NT benchmark, frozen and reference fine-tuned scores) with row and column labels asserted.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "lit-search-20261011-gfm-2" / "extract"))
from gfm2lib import Batch, table_rows  # noqa: E402

P = "gfm2-20261011-datta2026"
SRC = f"{P}-source"
SHA = "df36e4772562329550c924004a546812c8d76149a1b5238e4d0b0cfa8a82bb5c"
URL = "https://arxiv.org/pdf/2608.05329v1"
NOTE = ("Deterministic parse of `pdftotext -layout` (poppler 26.08.0) text of the pinned PDF with task and model "
        "labels asserted (extract/extract.py). Pending independent review.")

lines = Path(sys.argv[1]).read_text().splitlines()

b = Batch(P, SRC)
b.source(
    "Frozen but Not Always Accessible: A Representation Analysis of Genomic Language Models",
    "arXiv preprint v1 probing frozen embeddings of five genomic language models against fine-tuned references on the Nucleotide Transformer benchmark, Genomic Benchmark and two Genomics Long-Range Benchmark variant-effect tasks.",
    {"url": "https://arxiv.org/abs/2608.05329v1", "artifact_url": URL, "artifact_sha256": SHA,
     "retrieved_at": "2026-10-11T00:51:27Z", "publication_status": "preprint",
     "version": "arXiv:2608.05329v1, submitted 2026-08-05",
     "licence": "arXiv.org perpetual non-exclusive license 1.0 (no redistribution of the bytes)",
     "media_type": "application/pdf", "source_locator": "Tables 1-9",
     "evidence_concerns": [{
         "source_id": SRC,
         "message": "Table 1 prints the same frozen value and spread (.5252+-.0262) for NT on both 'Enhancer' and 'Enhancer Types', while the fine-tuned references differ (.548 and .424). One of the two frozen cells is likely a transcription error in the source; both are kept as printed and should not support comparison until the authors clarify.",
         "source_locator": "Table 1, column 'NT', rows 'Enhancer' and 'Enhancer Types'",
         "artifact_sha256": SHA,
         "review_date": "2026-10-11"}]})

HYENA = "regulatory-variant-20261009-model-hyenadna"
NT = "discovery-model-nucleotide-transformer"
generator = b.model("generator-v2", "GENERATOR", "Long-context generative genomic foundation model family (Datta et al. 2026 Section 3, citing Wu et al. 2025).",
                    "Section 2.2, model list")
omni = b.model("omni-dna", "Omni-DNA", "Genomic foundation model family (Datta et al. 2026 Section 3, citing Li et al. 2025).",
               "Section 2.2, model list")

MODELS = {
    "HyenaDNA": ("HyenaDNA-436K", HYENA, "436K"),
    "NT": ("NT-500M", NT, "500M"),
    "GENERATOR-v2": ("GENERATOR-v2-1.2B", generator, "1.2B"),
    "Omni-DNA": ("Omni-DNA-116M", omni, "116M"),
}
VERSION_MISSING = {"reason": "unreported", "note": "Parameter count printed; no checkpoint revision or release version is given"}

TASKS = [("H3", "matthews-correlation-coefficient", "unitless", "histone mark"),
         ("H3K14ac", "matthews-correlation-coefficient", "unitless", "histone mark"),
         ("H3K36me3", "matthews-correlation-coefficient", "unitless", "histone mark"),
         ("H3K4me1", "matthews-correlation-coefficient", "unitless", "histone mark"),
         ("H3K4me2", "matthews-correlation-coefficient", "unitless", "histone mark"),
         ("H3K4me3", "matthews-correlation-coefficient", "unitless", "histone mark"),
         ("H3K79me3", "matthews-correlation-coefficient", "unitless", "histone mark"),
         ("H3K9ac", "matthews-correlation-coefficient", "unitless", "histone mark"),
         ("H4", "matthews-correlation-coefficient", "unitless", "histone mark"),
         ("H4ac", "matthews-correlation-coefficient", "unitless", "histone mark"),
         ("Enhancer", "matthews-correlation-coefficient", "unitless", "enhancer"),
         ("Enhancer Types", "matthews-correlation-coefficient", "unitless", "enhancer"),
         ("Promoter All", "f1-score", "fraction", "promoter"),
         ("Promoter Non-TATA", "f1-score", "fraction", "promoter"),
         ("Promoter TATA", "f1-score", "fraction", "promoter"),
         ("Splice All", "f1-score", "fraction", "splice site"),
         ("Splice Acceptor", "f1-score", "fraction", "splice site"),
         ("Splice Donor", "f1-score", "fraction", "splice site")]

data = b.dataset("nt-benchmark", "Nucleotide Transformer benchmark task data (Datta et al. 2026)",
                 "Enhancer, histone-mark, promoter and splice-site classification data from the Nucleotide Transformer benchmark, used under the authors' unified preprocessing and split loader.",
                 {"version": "As distributed with the Nucleotide Transformer benchmark (Dalla-Torre et al. 2025)",
                  "split": "Benchmark train/test split, loaded through one shared loader for frozen and adapted settings",
                  "source_locator": "Section 3.1, 'Nucleotide Transformer Benchmark'",
                  "missing_metadata": {"accession": {"reason": "unreported", "note": "No accession, revision or file list is printed"}}})

LIM = ["Frozen-probe scores come from the authors' unified protocol; the fine-tuned column is benchmark- or model-reported where available and the authors mark it as a reference value, not a matched head-to-head comparison (Sections 2.7 and 3.3).",
       "Frozen scores are mean and standard deviation over five seeds with the probe selected on the diagnostic test grid for most tables; the authors treat grid-best figures as readout-sensitivity analyses rather than unbiased model selection (Sections 2.5 and 3.3).",
       "Table 1 covers four of the five models in the study; DNABERT-2 appears only in the controlled LoRA comparison (Table 9)."]

p_frozen = b.protocol("frozen-probe", "Nucleotide Transformer benchmark under frozen-embedding probing (Datta et al. 2026 Table 1)",
                      "Lightweight probes trained on frozen sequence embeddings, with the backbone in inference mode and no parameter update.",
                      {"protocol": "Extract a sequence embedding from the frozen backbone (gradients disabled), standardise with training-set statistics, and train a logistic-regression, RBF-SVM or MLP probe; report the best pooling and probe configuration over the diagnostic grid, as mean and standard deviation over five seeds.",
                       "version": "Table 1, 'Frozen' value of each cell",
                       "metric_implementation": "MCC for enhancer and histone-mark tasks, F1 for promoter and splice-site tasks (Section 3.2)",
                       "aggregation": "Mean over five seeds",
                       "replicates": "Five seeds",
                       "limitations": LIM, "source_locator": "Table 1; Sections 2.3-2.5, 3.2 and 3.3"}, data_id=data)

p_ft = b.protocol("fine-tuned-reference", "Nucleotide Transformer benchmark, reference fine-tuned scores (Datta et al. 2026 Table 1)",
                  "Fine-tuned scores for the same tasks, taken from benchmark or model reports where available and marked by the authors as reference values.",
                  {"protocol": "Fine-tuned scores as printed in the 'FT' position of each Table 1 cell. The authors state these are benchmark- or model-reported where available and are provenance-marked reference values rather than fully matched head-to-head comparisons.",
                   "version": "Table 1, 'FT' value of each cell",
                   "metric_implementation": "MCC for enhancer and histone-mark tasks, F1 for promoter and splice-site tasks (Section 3.2)",
                   "aggregation": "As reported by the cited benchmark or model source",
                   "limitations": LIM + ["Who ran each fine-tuned score is not stated per cell, so these evaluations are recorded with origin 'unreported'.",
                                         "Fine-tuning protocol, epochs and selection are not printed for these reference values."],
                   "source_locator": "Table 1; Sections 2.7 and 3.3"}, data_id=data)

t1 = table_rows(lines, "Table 1: Main NT benchmark evaluation", "Table 2: Genomic Benchmark results")
header = next(l for l in t1 if "HyenaDNA" in l and "Omni-DNA" in l)
for key in MODELS:
    assert key in header, key
CELL = re.compile(r"(\.\d{4}|\d\.\d{4})(?:±(\.\d{4}))?\s*/\s*(\.\d{3})(?:±(\.\d{3}))?\s*/\s*(\d+)")

configs = {}
for task, metric, unit, family in TASKS:
    row = next(l for l in t1 if l.strip().startswith(task + " ") and "/" in l)
    cells = CELL.findall(row)
    assert len(cells) == 4, (task, row, cells)
    for (model_key, (printed_name, of, params)), (frozen, frozen_sd, ft, ft_sd, _recovery) in zip(MODELS.items(), cells):
        for setting in ("frozen", "ft"):
            ckey = (model_key, setting)
            if ckey not in configs:
                configs[ckey] = b.config(
                    f"{model_key}-{setting}",
                    f"{printed_name}, {'frozen embeddings with a lightweight probe' if setting == 'frozen' else 'fine-tuned reference score'} (Datta et al. 2026)",
                    of, "foundation_model", printed_name,
                    f"Section 2.2 model list; Table 1 column '{model_key}'",
                    version_missing=VERSION_MISSING,
                    parameters=(f"{params} parameters; backbone frozen in inference mode, gradients disabled; embeddings standardised with training-set statistics; best pooling and probe over the diagnostic grid"
                                if setting == "frozen" else
                                f"{params} parameters; fine-tuned score as reported by the benchmark or model source, protocol not printed"),
                    extra={"training_setting": "Frozen backbone, probe only" if setting == "frozen" else "Fine-tuned; protocol unreported in this source"})
        for setting, printed, sd, protocol, origin in (
                ("frozen", frozen, frozen_sd, p_frozen, "independent_paper"),
                ("ft", ft, ft_sd, p_ft, "unreported")):
            ev = b.evaluation(f"{model_key}-{task}-{setting}",
                              f"{printed_name} on NT benchmark {task} ({'frozen probe' if setting == 'frozen' else 'reference fine-tuned'})",
                              configs[(model_key, setting)], protocol, data, origin,
                              {"dataset_version": "Nucleotide Transformer benchmark as distributed",
                               "split": "Benchmark train/test split",
                               "inputs": f"DNA sequence for the {family} task",
                               "adaptation": "None: frozen backbone with a trained probe" if setting == "frozen" else "Fine-tuning; protocol not printed in this source",
                               "metric_implementation": "MCC" if metric == "matthews-correlation-coefficient" else "F1 score",
                               "aggregation": "Mean over five seeds" if setting == "frozen" else "As reported by the cited source"},
                              f"Table 1, row '{task}', column '{model_key}', {'first' if setting == 'frozen' else 'second'} value of the cell",
                              limitations=LIM)
            unc = ({"type": "standard_deviation", "value": sd.replace(".", "0.", 1), "printed": f"±{sd}",
                    "n": 5, "scope": "Five probe seeds"} if (setting == "frozen" and sd) else
                   {"type": "standard_deviation", "value": sd.replace(".", "0.", 1), "printed": f"±{sd}",
                    "scope": "As printed in the source"} if sd else None)
            b.result(f"{model_key}-{task}-{setting}", ev, metric, printed,
                     f"Table 1, row '{task}', column '{model_key}', {'frozen' if setting == 'frozen' else 'FT'} value",
                     unit=unit, qualifier="frozen-embedding probe" if setting == "frozen" else "reference fine-tuned score",
                     uncertainty=unc, method_note=NOTE,
                     note=("Extraction only; pending independent review."
                           + (" Source concern: this frozen cell duplicates the NT 'Enhancer' cell; see the source record's evidence_concerns."
                              if (model_key == "NT" and task in ("Enhancer", "Enhancer Types") and setting == "frozen") else "")))

b.claim("recovery-definition", p_frozen, "recovery_definition",
        "Recovery = (frozen probe score / fine tuned score) x 100 (Equation 7). The per-cell recovery percentages and the promoter and splice average recovery rows of Table 1 are not extracted as results; they are a ratio of the two extracted scores.",
        "Section 3.2, Equation 7; Table 1 recovery positions and the 'Promoter avg. recovery' and 'Splice avg. recovery' rows")

counts = b.write(HERE.parent)
print(counts, sum(counts.values()))
