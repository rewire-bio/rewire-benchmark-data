"""The 32 tasks of the HyPLM report: dataset reuse, metric and method per task.

Each entry: (row label in Tables 6 and 7, slug, existing dataset id or None,
metric concept, unit, metric qualifier, implementation, new-dataset spec).
A new-dataset spec is (name, description, printed train/valid/test sizes, origin).
"""

PROTEINGYM_DATA = "vep-lit-20261014-data-proteingym-dms-substitutions-144fe22"

PROBE_SEQ = ("Linear probe on mean-pooled frozen representations (special tokens excluded), with "
             "the layer and regularisation chosen on the validation split among six relative "
             "depths (0.25, 0.5, 0.625, 0.75, 0.875, 1.0); features cached in FP16 (FP32 for Ankh).")
PROBE_RES = ("Linear per-residue probe on frozen residue representations, with the layer and "
             "regularisation chosen on the validation split among six relative depths.")
RIDGE = "Closed-form ridge regression probe. " + PROBE_SEQ
LOGIT = "L2-regularised logistic regression probe fitted with L-BFGS. " + PROBE_SEQ
MULTI = "One L2-regularised logistic output per term, fitted with L-BFGS. " + PROBE_SEQ
CONTACT = ("Contact head projecting residue features to 32 dimensions and scoring pairs with a "
           "symmetric bilinear form, trained with AdamW on up to 8,000 ProteinNet proteins. A "
           "contact is a residue pair whose CB atoms (CA for ProteinNet) are closer than 8 Angstrom; "
           "long range means a sequence separation of at least 24.")
ZERO_SHOT = ("Masked-marginal score: the sum over a variant's substitutions of log p(mutant) minus "
             "log p(wild type), each position masked on its own in the wild-type sequence and, for "
             "long targets, one window centred on the position. Per-assay Spearman correlations "
             "are rounded to three decimals and aggregated with the official ProteinGym procedure.")
NLL = ("Negative log-likelihood of masked residues with fixed masks (15% of the canonical "
       "residues, one seeded draw per protein) and identical crops for every model.")


def new(name, description, sizes, origin):
    return (name, description, sizes, origin)


TASKS = [
    ("ProteinGym zero-shot", "proteingym-zero-shot", PROTEINGYM_DATA, "spearman-correlation",
     "unitless",
     "Spearman correlation averaged over the 217 substitution assays of ProteinGym v1.3 with the "
     "benchmark's official aggregation, from masked-marginal zero-shot scores; per-assay values "
     "rounded to three decimals before aggregation",
     ZERO_SHOT, None),
    ("NLL, held-out UniRef panel", "nll-held-out-uniref", None, "log-loss", "unitless",
     "Mean negative log-likelihood of masked residues in nats on the report's held-out UniRef "
     "panel, identical masks and crops for every model",
     NLL, new("Held-out UniRef panel (479 proteins, HyPLM report)",
              "Proteins from the HyPLM report's held-out UniRef split, used to score masked-residue "
              "likelihood.", "test 479", "held-out UniRef split of the HyPLM training data")),
    ("NLL, recent PDB chains", "nll-recent-pdb", None, "log-loss", "unitless",
     "Mean negative log-likelihood of masked residues in nats on the report's recent-PDB panel, "
     "identical masks and crops for every model",
     NLL, new("Recent PDB chains (887, HyPLM report)",
              "Recently released PDB chains clustered at 50% identity with MMseqs2 after removing "
              "exact matches to the HyPLM training corpus, used to score masked-residue likelihood.",
              "test 887", "RCSB PDB; the release window is printed two ways (see evidence_concerns)")),
    ("Secondary structure (CB513)", "secondary-structure-cb513",
     "lit-protein-20261011-deepprotein-data-secondary-structure", "accuracy", "fraction",
     "Three-state (Q3) per-residue secondary-structure accuracy on the CB513 test set",
     PROBE_RES, None),
    ("Contacts, ProteinNet", "contacts-proteinnet", "paper-dataset-b2114365a5517543b7",
     "precision-at-l-5", "fraction",
     "Long-range contact precision of the top L/5 predictions (sequence separation at least 24) "
     "on the ProteinNet CASP12 test set of 40 proteins",
     CONTACT, None),
    ("Contacts, CASP14", "contacts-casp14", None, "precision-at-l-5", "fraction",
     "Long-range contact precision of the top L/5 predictions (sequence separation at least 24) "
     "on 82 CASP14 evaluation domains",
     CONTACT, new("CASP14 evaluation domains (82, HyPLM report)",
                  "CASP14 evaluation domains used as a contact-prediction test set.",
                  "test 82 domains", "CASP14 evaluation domains")),
    ("Contacts, CASP15", "contacts-casp15", None, "precision-at-l-5", "fraction",
     "Long-range contact precision of the top L/5 predictions (sequence separation at least 24) "
     "on 95 CASP15 evaluation domains",
     CONTACT, new("CASP15 evaluation domains (95, HyPLM report)",
                  "CASP15 evaluation domains used as a contact-prediction test set.",
                  "test 95 domains", "CASP15 evaluation domains")),
    ("Remote homology (fold)", "remote-homology-fold", "lit-protein-20261011-deepprotein-data-fold",
     "accuracy", "fraction",
     "Fold-level classification accuracy on the TAPE remote-homology (SCOP) test set",
     LOGIT, None),
    ("EC, SaProt split", "ec-saprot-split", None, "f1-max", "fraction",
     "Protein-centric Fmax over Enzyme Commission numbers on the SaProt EC split",
     MULTI, new("EC annotation, SaProt split (HyPLM report)",
                "Enzyme Commission annotation split as packaged by SaProt.",
                "13,090 / 1,465 / 1,604", "SaProt EC split")),
    ("EC, DeepFRI split", "ec-deepfri-split", None, "f1-max", "fraction",
     "Protein-centric Fmax over Enzyme Commission numbers on the DeepFRI EC split",
     MULTI, new("EC annotation, DeepFRI split (HyPLM report)",
                "Enzyme Commission annotation split of DeepFRI.",
                "not printed (Table 4 prints the SaProt split's sizes)", "DeepFRI EC split")),
    ("GO-MF", "go-mf", None, "f1-max", "fraction",
     "Protein-centric Fmax over Gene Ontology molecular-function terms on the DeepFRI GO split as "
     "packaged by SaProt",
     MULTI, new("GO molecular function, DeepFRI split via SaProt (HyPLM report)",
                "Gene Ontology molecular-function annotation on the DeepFRI GO split as packaged "
                "by SaProt.", "26,225 / 2,904 / 3,350", "DeepFRI GO split as packaged by SaProt")),
    ("GO-BP", "go-bp", None, "f1-max", "fraction",
     "Protein-centric Fmax over Gene Ontology biological-process terms on the DeepFRI GO split as "
     "packaged by SaProt",
     MULTI, new("GO biological process, DeepFRI split via SaProt (HyPLM report)",
                "Gene Ontology biological-process annotation on the DeepFRI GO split as packaged "
                "by SaProt.", "not printed (Table 4 prints GO-MF's sizes)",
                "DeepFRI GO split as packaged by SaProt")),
    ("GO-CC", "go-cc", None, "f1-max", "fraction",
     "Protein-centric Fmax over Gene Ontology cellular-component terms on the DeepFRI GO split as "
     "packaged by SaProt",
     MULTI, new("GO cellular component, DeepFRI split via SaProt (HyPLM report)",
                "Gene Ontology cellular-component annotation on the DeepFRI GO split as packaged "
                "by SaProt.", "not printed (Table 4 prints GO-MF's sizes)",
                "DeepFRI GO split as packaged by SaProt")),
]
