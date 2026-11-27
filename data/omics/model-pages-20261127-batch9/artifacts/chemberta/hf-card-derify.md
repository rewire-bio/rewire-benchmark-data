---
license: apache-2.0
datasets:
- Derify/augmented_canonical_pubchem_13m
metrics:
- roc_auc
- rmse
library_name: transformers
tags:
- ChemBERTa
- cheminformatics
pipeline_tag: fill-mask
model-index:
- name: Derify/augmented_canonical_pubchem_13m
  results:
  - task:
      type: text-classification
      name: Classification (ROC AUC)
    dataset:
      name: BACE
      type: BACE
    metrics:
    - type: roc_auc
      value: 0.8008
  - task:
      type: text-classification
      name: Classification (ROC AUC)
    dataset:
      name: BBBP
      type: BBBP
    metrics:
    - type: roc_auc
      value: 0.7418
  - task:
      type: text-classification
      name: Classification (ROC AUC)
    dataset:
      name: TOX21
      type: TOX21
    metrics:
    - type: roc_auc
      value: 0.7548
  - task:
      type: text-classification
      name: Classification (ROC AUC)
    dataset:
      name: HIV
      type: HIV
    metrics:
    - type: roc_auc
      value: 0.7744
  - task:
      type: text-classification
      name: Classification (ROC AUC)
    dataset:
      name: SIDER
      type: SIDER
    metrics:
    - type: roc_auc
      value: 0.6313
  - task:
      type: text-classification
      name: Classification (ROC AUC)
    dataset:
      name: CLINTOX
      type: CLINTOX
    metrics:
    - type: roc_auc
      value: 0.9621
  - task:
      type: regression
      name: Regression (RMSE)
    dataset:
      name: ESOL
      type: ESOL
    metrics:
    - type: rmse
      value: 0.8798
  - task:
      type: regression
      name: Regression (RMSE)
    dataset:
      name: FREESOLV
      type: FREESOLV
    metrics:
    - type: rmse
      value: 0.5282
  - task:
      type: regression
      name: Regression (RMSE)
    dataset:
      name: LIPO
      type: LIPO
    metrics:
    - type: rmse
      value: 0.6853
  - task:
      type: regression
      name: Regression (RMSE)
    dataset:
      name: BACE
      type: BACE
    metrics:
    - type: rmse
      value: 0.9554
  - task:
      type: regression
      name: Regression (RMSE)
    dataset:
      name: CLEARANCE
      type: CLEARANCE
    metrics:
    - type: rmse
      value: 45.4362
---

This model is a ChemBERTa model trained on the augmented_canonical_pubchem_13m dataset.

The model was trained for 24 epochs using NVIDIA Apex's FusedAdam optimizer with a reduce-on-plateau learning rate scheduler. 
To improve performance, mixed precision (fp16), TF32, and torch.compile were enabled. Training used gradient accumulation (16 steps) and batch size of 128 for efficient resource utilization. 
Evaluation was performed at regular intervals, with the best model selected based on validation performance.

## Benchmarks
### Classification Datasets (ROC AUC - Higher is better)

| Model                     | BACE↑  | BBBP↑  | TOX21↑ | HIV↑   | SIDER↑ | CLINTOX↑ |
| ------------------------- | ------ | ------ | ------ | ------ | ------ | -------- |
| **Tasks**                 | 1      | 1      | 12     | 1      | 27     | 2        |
| Derify/ChemBERTa_augmented_pubchem_13m | 0.8008 | 0.7418 | 0.7548 | 0.7744 | 0.6313 | 0.9621   |

### Regression Datasets (RMSE - Lower is better)

| Model                     | ESOL↓  | FREESOLV↓ | LIPO↓  | BACE↓  | CLEARANCE↓ |
| ------------------------- | ------ | --------- | ------ | ------ | ---------- |
| **Tasks**                 | 1      | 1         | 1      | 1      | 1          |
| Derify/ChemBERTa_augmented_pubchem_13m | 0.8798 | 0.5282    | 0.6853 | 0.9554 | 45.4362    |

Benchmarks were conducted using the [chemberta3](https://github.com/deepforestsci/chemberta3) framework. 
Datasets were split with DeepChem’s scaffold splits and filtered to include only molecules with SMILES length ≤200, following MolFormer paper's recommendation. 
The model was fine-tuned for 100 epochs with a learning rate of 3e-5 and batch size of 32. 
Each task was run with 3 different random seeds, and the mean performance is reported.

## References
### ChemBERTa Series
```
@misc{chithrananda2020chembertalargescaleselfsupervisedpretraining,
      title={ChemBERTa: Large-Scale Self-Supervised Pretraining for Molecular Property Prediction}, 
      author={Seyone Chithrananda and Gabriel Grand and Bharath Ramsundar},
      year={2020},
      eprint={2010.09885},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/2010.09885}, 
}
```
```
@misc{ahmad2022chemberta2chemicalfoundationmodels,
      title={ChemBERTa-2: Towards Chemical Foundation Models}, 
      author={Walid Ahmad and Elana Simon and Seyone Chithrananda and Gabriel Grand and Bharath Ramsundar},
      year={2022},
      eprint={2209.01712},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/2209.01712}, 
}
```
```
@misc{singh2025chemberta3opensource,
  title={ChemBERTa-3: An Open Source Training Framework for Chemical Foundation Models},
  author={Singh, R. and Barsainyan, A. A. and Irfan, R. and Amorin, C. J. and He, S. and Davis, T. and others},
  year={2025},
  howpublished={ChemRxiv},
  doi={10.26434/chemrxiv-2025-4glrl-v2},
  note={This content is a preprint and has not been peer-reviewed},
  url={https://doi.org/10.26434/chemrxiv-2025-4glrl-v2}
}
```