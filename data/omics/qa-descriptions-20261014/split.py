"""Issue #88: descriptions whose functional text was already sourced but which also
carried provenance (a locator such as "(Table 1)", a citation such as "(Shu et al.
2021)", "Cited in the source as ref 18", "with task scores quoted from prior work in
MIMIC Table S11"). The functional part stays as the description, reworded only where
it did not stand on its own; the provenance part moves to attributes.provenance_note.

Writes systems-split.jsonl in the shape of the researched files (id, new_description,
provenance_note, evidence_*), which build.py turns into rows of corrections.csv.
  python3 -I data/omics/qa-descriptions-20261014/split.py
Run from the repository root.
"""
import json

HERE = "data/omics/qa-descriptions-20261014"
SAME = "Functional text kept from the reviewed description; only the provenance moved."

# id -> (new description, provenance note)
SPLIT = {
    "cell-type-20261009-model-langcell": ("Single-cell foundation model pretrained on cell-text pairs, initialised from Geneformer.", "Model details as given in the cell-type annotation comparison, Table 1."),
    "cell-type-20261009-model-sccello": ("Single-cell foundation model pretrained with cell-ontology alignment losses.", "Model details as given in the cell-type annotation comparison, Table 1."),
    "cell-type-20261009-model-uce": ("Single-cell foundation model producing cell embeddings from protein-embedded gene tokens.", "Model details as given in the cell-type annotation comparison, Table 1."),
    "discovery-model-tape-bepler": ("Protein language model with a two-layer bidirectional language model followed by three bidirectional LSTMs with 512 hidden units, trained by next-token prediction.", "Model of Bepler et al., as benchmarked in TAPE."),
    "discovery-model-tape-unirep": ("UniRep protein language model: a unidirectional multiplicative LSTM with 1,900 hidden units, trained by next-token prediction.", "Model of Alley et al. (UniRep), as benchmarked in TAPE."),
    "dna-pathogen-20261012-bertax-model-deepmicrobes": ("Taxonomic classifier using 12-mer embeddings, bidirectional LSTM layers and self-attention.", "Model of Liang et al., retrained by the BERTax authors on the BERTax training data."),
    "gfm2-20261011-buzkova2026-model-dnabert-s": ("Species-aware DNA embedding model contrastively fine-tuned from DNABERT-2.", "Described in Bůžková et al. 2026, Table 2."),
    "gfm2-20261011-you2026-model-dnabert": ("DNA language model with k-mer tokenisation.", "Described in You et al. 2026, Table 1."),
    "gfm2-20261011-you2026-model-rna-msm": ("RNA language model pre-trained on multiple sequence alignments.", "Described in You et al. 2026, Table 1."),
    "gfm2-20261011-you2026-model-rnabert": ("RNA language model pre-trained on small non-coding RNA.", "Described in You et al. 2026, Table 1."),
    "gfm2-20261011-you2026-model-rnaernie": ("RNA language model with motif-aware pre-training.", "Described in You et al. 2026, Table 1."),
    "gfm2-20261011-you2026-model-splicebert": ("Pre-trained language model of precursor mRNA sequence.", "Described in You et al. 2026, Table 1."),
    "gfm2-20261011-you2026-model-sptransformer": ("Task-specific transformer for tissue-specific splice site prediction.", "Described in You et al. 2026, Introduction."),
    "gfm2-20261011-you2026-model-utr-lm": ("Language model pre-trained on 5' untranslated region sequence.", "Described in You et al. 2026, Table 1."),
    "lit-cells-networks-20261011-chen2026-model-cellplm": ("Cell-level transformer foundation model pretrained on scRNA-seq and spatial transcriptomics.", "Primary reference: Wen et al., ICLR 2024."),
    "lit-cells-networks-20261011-chen2026-model-nicheformer": ("Transformer foundation model pretrained on dissociated and spatial transcriptomics.", "Primary reference: Schaub et al., Nature Methods 2025."),
    "lit-cells-networks-20261011-chen2026-model-novae": ("Graph attention foundation model for spatial transcriptomics domains.", "Primary reference: Blampey et al., Nature Methods 2025."),
    "lit-cells-networks-20261011-chen2026-model-scgpt-spatial": ("scGPT continually pretrained on spatial transcriptomics from the SpatialHuman30M corpus.", "Primary reference: Wang et al., bioRxiv 2025."),
    "lit-cells-networks-20261011-ye2026grn-model-scprint": ("Single-cell foundation model pretrained on CELLxGENE data for gene network inference and expression denoising.", "Primary reference: Kalfon et al."),
    "lit-interactions-20261011-leakctl-model-flowdock": ("FlowDock: conditional flow-matching docking and affinity model built on ESMFold and NeuralPLexer components.", "Model details as given in the PLABench paper, Table 1."),
    "lit-interactions-20261011-leakctl-model-flowr-root": ("FLOWR.ROOT: SE(3)-equivariant flow-matching model with joint structure, affinity and confidence heads.", "Model details as given in the PLABench paper, Table 1."),
    "lit-interactions-20261011-leakctl-model-graph-rg": ("Graph_RG: two-stream graph transformer, ligand pose-free structure-based affinity model.", "Model details as given in the PLABench paper, Table 1."),
    "lit-interactions-20261011-leakctl-model-lcdd-team": ("LCDD-team: three-stream GPS graph transformer affinity model from the CASP16 LCDD team.", "Model details as given in the PLABench paper, Table 1."),
    "lit-interactions-20261011-leakctl-model-llf": ("LLF: sequence-based protein-ligand affinity model with multi-stream GCN and CNN branches that keep local features.", "Model details as given in the PLABench paper, Table 1."),
    "lit-interactions-20261011-leakctl-model-mfe": ("MFE: multimodal extraction model combining 3D CNN, GVP-GNN and ProtTrans features.", "Model details as given in the PLABench paper, Table 1."),
    "lit-interactions-20261011-leakctl-model-mixingdta": ("MixingDTA: meta-ensemble affinity model using MolFormer and ESM3 features.", "Model details as given in the PLABench paper, Table 1."),
    "lit-interactions-20261011-mochibind-model-mochibind": ("MochiBind: sequence-only pairwise antibody-antigen binding predictor using ESM-2 (esm2_t36_3B_UR50D) embeddings and a pairwise scoring module.", "Introduced in the MochiBind paper."),
    "lit-interactions-20261011-plmdta-model-deepgraphdta": ("DeepGraphDTA: GraphDTA with a transposed-input 1D convolution protein encoder.", "Introduced in the PLM-GraphDTA paper."),
    "lit-interactions-20261011-plmdta-model-plm-graphdta": ("PLM-GraphDTA: GraphDTA drug encoders with frozen protein language model embeddings as the protein representation.", "Introduced in the PLM-GraphDTA paper."),
    "lit-rna-20261011-rna3d-model-deepfoldrna": ("DeepFoldRNA: RNA structure prediction from deep self-attention networks with gradient-based folding.", "Model details as given in the RNA 3D structure benchmark, Table 1."),
    "lit-rna-20261011-rna3d-model-drfold": ("DRfold: ab initio RNA structure prediction that combines end-to-end learning with deep geometrical potentials.", "Model details as given in the RNA 3D structure benchmark, Table 1."),
    "lit-rna-20261011-rna3d-model-nufold": ("NuFold: RNA 3D structure prediction method built on the AlphaFold architecture with RNA-specific inputs.", "Model details as given in the RNA 3D structure benchmark, Table 1."),
    "lit-rna-20261011-rna3d-model-rosettafoldna": ("RoseTTAFoldNA (RF2NA): three-track network that predicts protein and nucleic acid structures and complexes.", "Model details as given in the RNA 3D structure benchmark, Table 1."),
    "lit-rna-20261011-rna3d-model-trrosettarna": ("trRosettaRNA: MSA and pair representations fed into the RNAformer transformer, followed by 3D folding.", "Model details as given in the RNA 3D structure benchmark, Table 1."),
    "lit20261011-zhong2026-model-mass": ("MassFormer graph transformer spectrum predictor, used as the predictor head in FlexMS.", "The FlexMS paper labels it 'Mass' (Table 2 caption: 'Mass' denotes MassFormers)."),
    "ctdnafrag-20261009-method-delfi": ("Short-to-long fragment ratios in 5 Mb bins.", "The method record names the feature definition, not an implementation."),
    "ctdnafrag-20261009-method-end-motif": ("Proportions of the 256 5' end 4-mers per chromosome.", "Defined in Hou et al. ref 42; the method record names the feature definition, not an implementation."),
    "ctdnafrag-20261009-method-fragment-coverage": ("Number of fragment midpoints per region.", "Defined in Hou et al. ref 32; the method record names the feature definition, not an implementation."),
    "ctdnafrag-20261009-method-fragment-end-count": ("Number of fragment endpoints per region, counting preferred end coordinates.", "Defined in Hou et al. ref 59; the method record names the feature definition, not an implementation."),
    "ctdnafrag-20261009-method-fragment-length": ("Proportions of fragments in 10 bp length intervals.", "Defined in Hou et al. ref 34; the method record names the feature definition, not an implementation."),
    "ctdnafrag-20261009-method-fsd": ("Fragment proportions in 5 bp length intervals per chromosome arm or chromosome.", "Defined in Hou et al. ref 58; the method record names the feature definition, not an implementation."),
    "ctdnafrag-20261009-method-fsr": ("Short, medium and long fragment proportions per region.", "Defined in Hou et al. ref 58; the method record names the feature definition, not an implementation."),
    "ctdnafrag-20261009-method-ifs": ("Fragment count weighted by mean fragment length per region.", "Defined in Hou et al. ref 10; the method record names the feature definition, not an implementation."),
    "ctdnafrag-20261009-method-ocf": ("Difference in upstream and downstream fragment end counts around region centres.", "Defined in Hou et al. ref 32; the method record names the feature definition, not an implementation."),
    "ctdnafrag-20261009-method-pfe": ("Shannon entropy of fragment length proportions per region.", "Defined in Hou et al. ref 54; the method record names the feature definition, not an implementation."),
    "ctdnafrag-20261009-method-wps": ("Nucleosome protection score from fully and partially spanning fragments in a 120 bp window.", "Defined in Hou et al. ref 44; the method record names the feature definition, not an implementation."),
    "ctdnalit-20261011-helzer2025-method-all-combined": ("All of the panel fragmentomic metrics combined as features of one model.", "Cited in the source as a combination defined by the authors."),
    "ctdnalit-20261011-helzer2025-method-all-exons-depth": ("Reads per exon divided by exon length and total reads; one feature per exon.", "Cited in the source as ref 18 (Esfahani et al. 2022)."),
    "ctdnalit-20261011-helzer2025-method-all-exons-mds": ("Normalised Shannon entropy of 256 4-mer end motifs per exon.", "Cited in the source as ref 23 (Jiang et al. 2020)."),
    "ctdnalit-20261011-helzer2025-method-all-exons-se": ("Shannon entropy of fragment-length frequencies per exon.", "Cited in the source as refs 18 and 19 (the authors' 2023 panel study)."),
    "ctdnalit-20261011-helzer2025-method-all-exons-small-fragments": ("Proportion of fragments of 150 bp or less per exon.", "Cited in the source as ref 21."),
    "ctdnalit-20261011-helzer2025-method-atac-entropy": ("Shannon entropy of fragment lengths over TCGA ATAC-seq peaks of 23 cancer types.", "Cited in the source as ref 24 (Sun et al. 2019)."),
    "ctdnalit-20261011-helzer2025-method-e1-depth": ("Reads per exon divided by exon length and total reads, at the first coding exon of each gene only.", "Cited in the source as ref 18 (Esfahani et al. 2022)."),
    "ctdnalit-20261011-helzer2025-method-e1-mds": ("Motif diversity score at first exons only.", "Cited in the source as ref 23 (Jiang et al. 2020)."),
    "ctdnalit-20261011-helzer2025-method-e1-se": ("Shannon entropy of fragment-length frequencies at first exons.", "The authors' 2023 panel metric; cited in the source as ref 19 (the authors' 2023 panel study)."),
    "ctdnalit-20261011-helzer2025-method-e1-small-fragments": ("Proportion of fragments of 150 bp or less at first exons.", "Cited in the source as ref 21."),
    "ctdnalit-20261011-helzer2025-method-fragment-bins": ("Proportions of fragments in six length bins (0-100 to >300 bp) per exon.", "Cited in the source as refs 18 and 19."),
    "ctdnalit-20261011-helzer2025-method-full-gene-depth": ("Depth with all exons of a gene combined into one feature.", "Cited in the source as ref 18 (Esfahani et al. 2022)."),
    "ctdnalit-20261011-helzer2025-method-griffin": ("Nucleosome profiling of cfDNA fragment coverage around transcription factor binding sites (central coverage, mean coverage, amplitude), here at the binding sites of 808 transcription factors.", "The method record names the published tool, not an implementation. Cited in the source as ref 17 (Doebley et al. 2022)."),
    "ctdnalit-20261011-helzer2025-method-tfbs-entropy": ("Shannon entropy of fragment lengths over the top 5,000 GTRD sites of each of 808 transcription factors.", "Cited in the source as refs 16 and 17 (Ulz et al. 2019; Doebley et al. 2022)."),
    "lit-cells-networks-20261011-ye2026grn-method-deepsem": ("Deep generative structural equation model for GRN inference from scRNA-seq.", "Primary reference: Shu et al. 2021."),
    "lit-microbial-20261011-virobench-method-virobench-cnn-baseline": ("Residual 1D CNN trained from scratch as a non-pretrained baseline.", "The ViroBench baseline (Appendix Figure 4)."),
    "regulatory-variant-20261009-method-mprann": ("CNN that predicts lentiMPRA activity from sequence.", "From the lentiMPRA study (Tang et al. reference 73); Tang et al. retrained it with the published structure and training parameters."),
}

# The mRNABench pipelines: the model clause is kept; "with task scores quoted from prior work in
# MIMIC Table S11" moves to the provenance note.
MIMIC_TAIL = ", with task scores quoted from prior work in MIMIC Table S11."
MIMIC_NOTE = "Task scores quoted from prior work in MIMIC Table S11; not a new execution."
MIMIC = ["aido-rna", "dnabert-s", "dnabert2", "ernie-rna", "evo2", "hyenadna", "nt-v2", "orthrus", "rinalmo", "splicebert"]


def main():
    store = {}
    for name in ("models", "methods", "pipelines"):
        for line in open(f"data/entities/{name}.jsonl"):
            r = json.loads(line)
            store[r["id"]] = r
    rows = []
    for rid, (new, note) in SPLIT.items():
        rows.append({"id": rid, "old_description": store[rid]["description"], "new_description": new,
                     "provenance_note": note, "evidence_url": "", "evidence_locator": "", "evidence_quote": SAME})
    for key in MIMIC:
        rid = f"mimic-2026-mrnabench-method-{key}"
        old = store[rid]["description"]
        assert old.endswith(MIMIC_TAIL) and old.startswith("mRNABench evaluation of mature mRNA embeddings from "), rid
        model = old[len("mRNABench evaluation of mature mRNA embeddings from "):-len(MIMIC_TAIL)]
        new = f"Embeds mature mRNA with {model}, for the mRNABench property prediction tasks."
        rows.append({"id": rid, "old_description": old, "new_description": new, "provenance_note": MIMIC_NOTE,
                     "evidence_url": "", "evidence_locator": "", "evidence_quote": SAME})
    with open(f"{HERE}/systems-split.jsonl", "w") as out:
        for row in sorted(rows, key=lambda r: r["id"]):
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"{len(rows)} rows")


if __name__ == "__main__":
    main()
