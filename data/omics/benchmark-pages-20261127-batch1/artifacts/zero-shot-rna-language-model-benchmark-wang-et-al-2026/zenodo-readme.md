Please note that users must configure the Python environment for each RNA language model and set the model path themselves. This is merely an example provided for reference.

# Zero-shot secondary structure prediction
### Task_ss
```
    -- data: Datasets
    -- scripts: Attention Extraction Scripts for Each Model
    -- metric.py: Combine Evaluation Results
    -- run_only_msm.sh: Run Only RNA-MSM Model
    -- run.sh: Run Models (Except RNA-MSM)
```
### Datasets

Column | Describe
--- | ---
vl_40_key_seq_contact_idx.pkl | VL1 dataset (40 PDBs) from RNA-MSM^[1]^
ts_70_key_seq_contact_idx.pkl | TS dataset (70 PDBs) from RNA-MSM^[1]^
TS-Hard.id | TS-Hard IDs (15 PDBs), extracted from TS

### Command
```
bash run.sh
bash run_only_msm.sh
python metric.py
```

# Zero-shot RNA Classification
### Task_class
```
    -- data: Datasets
    -- scripts: Embedding Extraction Scripts for Each Model
    -- metric.py: Combine Evaluation Results
    -- run_ArchiveII.sh: Run on ArchiveII-Nr dataset
    -- run_RfamSample.sh: Run on RfamSample dataset
```
### Datasets

Column | Describe
--- | ---
RfamSample_s42_rf561_n5610.fa | RfamSample fasta (Sampled from Rfam 14.0^[2]^)
RfamSample_s42_rf561_n5610.pkl | RfamSample dataset
Archivell_n3864.fasta | Archivell fasta (Extracted from ^[3]^)
Archivell_n3864_dataset.pkl | Archivell dataset
Archivell_Nr.pkl | Archivell-Nr dataset (non-redundant subset of Archivell)

### Command
```
bash run_RfamSample.sh
bash run_ArchiveII.sh
python metric.py 
```

# Zero-shot RNA Fitness Prediction
### Task_fit
```
    -- assays: DMS assays
    -- scripts_logsoftmax: Logits Extraction Scripts for Each Model (Using Log_Softmax normalization)
    -- scripts_softmax: Logits Extraction Scripts for Each Model (Using Softmax normalization)
    -- metric.py: Combine Evaluation Results
    -- reference_sheet_final_ncRNA.csv: DMS assays summary
    -- run_logsoftmax.sh: Run with Log_Softmax normalization
    -- run_softmax.sh: Run with Softmax normalization
```
### Datasets
DMS assays were from RNAgym^[4]^

### Command
```
bash run_logsoftmax.sh
bash run_softmax.sh
python metric.py 
```

### Note
```
The “compute_scores_wt” and “compute_scores_lh” functions in each script correspond to the WT-LLR and PLL-D methods described in the paper, respectively.
```

# Cite
[1] Zhang, Y. et al. Multiple sequence alignment-based RNA language model and its application to structural inference. Nucleic Acids Research 52, e3–e3 (2024).
[2] Mathews, D. H. How to benchmark RNA secondary structure prediction accuracy. Methods 162–163, 60–67 (2019).
[3] Kalvari, I. et al. Rfam 14: expanded coverage of metagenomic, viral and microRNA families. Nucleic Acids Res 49, D192–D200 (2021).
[4] Arora, R. et al. RNAGym: Benchmarks for RNA fitness and structure prediction. in ICLR 2025 workshop on AI for nucleic acids (2025).
