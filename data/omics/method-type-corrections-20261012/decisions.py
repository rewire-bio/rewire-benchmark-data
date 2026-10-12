# Rows the review made conditional on a source check, or "per named method". Executed by prepare.py.
# The checks are recorded in report.md ("Source checks").
LSHVEC_SRC = "method-type-corrections-20261012-source-shi2019-lshvec"
NOTE_S1_SRC = "method-type-corrections-20261012-source-cppc-note-s1"

group(MSALIGN_IDS, [FM],
      "MSAlign arXiv 2605.19752v2 abstract and Section 3 \"Foundation model alignment\" (p.4): aligns \"two frozen foundation models (DreaMS for mass spectra and MolDeBERTa for molecules)\" through trained MLP adapters",
      ["uc20260930-source-msalign-v2"], 1,
      "Checked as the review required. Score fusion (Section 3, \"Late score fusion\") combines four alignment scorers and three mass scores with weights fitted on validation data; two of the scorers use both foundation encoders.")
group(HECTOR_IDS, [CP],
      "HECTOR medRxiv v1, Materials and Methods, \"Engine Design and ENIGMA V1.2 Implementation\": evidence codes assigned against VCEP-defined thresholds and combined by ACMG/AMP rules and a point-based system; BayesDel and SpliceAI scores are inputs, HECTOR itself is not trained",
      ["uc-clinical-20261005-source-hector-preprint"],
      note="Checked as the review required.")
group(LSHVEC_IDS, [SML],
      "Shi and Chen 2019 bioRxiv 10.1101/726729v1, Section 3.3 Taxonomy Classification (p.3): \"taxonomy classification is supervised learning\"; a one-layer softmax network trained on labelled reads over fastText skip-gram k-mer embeddings (Section 3.2)",
      [LSHVEC_SRC],
      note="Read in the authors' 2019 preprint; the ACM BCB 2021 version (10.1145/3459930.3469521) returned HTTP 403 and was not read. Section 3 calls the read classifier \"(unsupervised)\", which Section 3.3 contradicts.")

CPPC = "ucc-research-config-cppc-submission-row-"
NOTE_S1 = "CPPC Supplementary Note S1"
TWO_STEP = ("Note S1 describes the authors' reimplementation of this submission from its write-up and code (Table S2 column I). The method maps each gene "
            "to features, then a predictor is fitted on Screen 1 (main-text Methods, \"Implementation of top methods\"; Figure 2A). The submitted write-ups "
            "(Document S1, Google Drive) were not read, so the submission's own predictor is not known.")
group([CPPC + "18"], [CP], f"{NOTE_S1}, GO_knn: the weighted average of the cell state proportions of the three most similar training perturbations; main-text Methods: \"does not use an explicit predictor\"", [NOTE_S1_SRC])
group([CPPC + "19"], [CP], f"{NOTE_S1}, LowExp: proportions taken from the state annotations of the 5,000 training cells with the lowest expression of the gene", [NOTE_S1_SRC])
group([CPPC + "5"], [FM], f"{NOTE_S1}, scBERT: \"extracts pretrained human gene embeddings from scBERT\", reference 7 is titled \"scBERT as a large-scale pretrained deep language model\"", [NOTE_S1_SRC],
      note="A supervised regressor is fitted on the embeddings. " + TWO_STEP)
for row, label, why in [
        ("2", "PPI_Weighted", "features averaged over STRING-network neighbours"),
        ("4", "14Features", "seven expression statistics on control and perturbed cells"),
        ("6", "scVI", "gene embeddings from an LDVAE trained on the challenge data"),
        ("7", "Expression_Conditioned", "each gene represented by its expression across training conditions"),
        ("8", "Exon", "exon-length summary statistics"),
        ("9", "Gene2Vec", "pretrained gene2vec gene embeddings"),
        ("12", "5Features", "expression summary statistics and cell-state marker expression"),
        ("16", "scETM", "gene embeddings from scETM trained on the challenge data"),
        ("22", "GO-node2vec", "Node2Vec embeddings of the gene ontology"),
        ("24", "GeneVector", "pretrained GeneVector gene embeddings")]:
    group([CPPC + row], [SML], f"{NOTE_S1}, {label}: {why}, then a fitted predictor", [NOTE_S1_SRC],
          note=TWO_STEP + (" Table S2 column K: different methods were used for challenges 1 and 2." if row == "24" else ""))
group([CPPC + "3"], [SML], f"{NOTE_S1}, GWPS_K562_H2M: \"An MLP regressor with a single hidden layer of latent dimension 10 is then trained\"", [NOTE_S1_SRC])
group([CPPC + "17"], [SML], f"{NOTE_S1}, \"Implementation of additional methods\": scTenifoldNet virtual knockout, then \"trains a random forest classifier\" to select genes", [NOTE_S1_SRC],
      note="Mixed: the random forest only selects genes; proportions come from normalised fold changes.")
group([CPPC + "21"], [SML], f"{NOTE_S1}, Interv: LASSO cell-state classification and local LiNGAM regression", [NOTE_S1_SRC])
# Row 23 is withheld. Its only stored result is the Challenge 2 score (Table S2 cell D23), and the Table S2 footnote "*" says
# "an alternative method was used for challenge 2". Note S1 describes Matrix_Completion, not that alternative method.
