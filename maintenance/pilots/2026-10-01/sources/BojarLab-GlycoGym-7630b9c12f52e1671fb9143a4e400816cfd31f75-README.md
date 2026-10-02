<p align="center">
  <img src="/docs/imgs/glycogym_banner.svg" style="height:100%;width:100%;">
</p>

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17313055.svg)](https://doi.org/10.5281/zenodo.17313055)
![testing](https://github.com/bojarlab/glycogym/actions/workflows/test.yaml/badge.svg)

Glycan property prediction is an increasingly popular area of machine learning research. Supervised learning approaches have shown promise in glycan modeling; however, the current literature is fragmented regarding datasets and standardized evaluation techniques, hampering progress in understanding these complex, branched carbohydrates that play crucial roles in biological processes. To facilitate progress, we introduce GlycoGym, a comprehensive benchmark suite containing seven biologically relevant supervised learning tasks spanning different domains of glycobiology: glycosylation linkage identification, tissue expression prediction, taxonomy classification, tandem mass spectrometry fragmentation prediction, lectin-glycan interaction modeling, structural property estimation, and nuclear magnetic resonance shift prediction. We additionally publish GlyVerse, a corpus for self-supervised pre-training. We curate tasks into specific training, validation, and test splits using multi-class stratification to ensure that each task tests biologically relevant generalization that transfers to real-life glycan property prediction scenarios. GlycoGym will help the machine learning community to focus their efforts on scientifically relevant glycan prediction problems.

## Installation

You can install GlycoGym via pip:

```bash
pip install glycogym
```

## Usage

The main intention of this package is to build the benchmark for the upload to Zenodo, everytime the datasets with `glycowork` or `GlyContact` get significantly updated.

But one can also use it to build local versions of the benchmark during the update cycles of the Zenodo repository.

```python
from glycogym import build_glycosylation, build_taxonomy, build_tissue, build_lgi

df, mapping = build_glycosylation()
df_taxonomy = build_taxonomy("Kingdom")
df_tissue = build_tissue()
df_r, df_cl, df_cg = build_lgi()
```

Every builder accepts `seed` (default 42) and `top_k`. Pass `top_k` for a fast smoke test, and keep `seed` fixed to reproduce the published splits exactly.

### Tandem Mass Spectrometry Fragmentation Prediction

One special dataset is the MS fragmentation prediction dataset, which can be built as follows:

```python
from glycogym import build_spectrum

df_ms = build_spectrum(root="path/to/folder/with/pkl/files")
```

Here, the root argument defined the path to the folder containing the `.pkl` files comprising the MS fragmentation prediction dataset by CandyCrunch, which can be downloaded from [here](https://zenodo.org/record/7940047).

### NMR Shift Prediction

Unlike the other tasks, the NMR dataset ships with the package as a compact parquet, so no download is needed:

```python
from glycogym import load_nmr, nmr_baselines

df_nmr = load_nmr()
print(nmr_baselines(df_nmr))
```

The result is one row per input atom. The boolean `is_target` column marks the measured C and H atoms whose `shift_ppm` values contribute to training and evaluation; all other atoms remain as molecular context. The isotope is given by `element` (`H` for 1H, `C` for 13C) rather than by a separate column. Splits are assigned per glycan, not per structure, so all structures of a glycan share a split, and are stratified over {experimental, simulated, both} to preserve the origin ratio. The bundle contains 376,397 input atoms, including 200,308 targets, over 2,073 glycans and 2,497 structures.

The benchmark runners fit normalization statistics, losses, validation selection, predictions, and RMSEs on target atoms only while forwarding every atom through the model. The GCN uses the deterministic `covalent-v1` atom graph audited by `scripts/audit_nmr_covalent_graphs.py`; SchNet, DimeNet, DimeNet++, and ComENet construct their geometric neighborhoods from all atomic coordinates. A train/validation-only smoke (which never constructs test graphs) can be run with:

```bash
python scripts/smoke_nmr_train_validation.py \
  --config configs/nmr_fixed_test_pilot.toml --model schnet --device cpu
```

The fixed-split and leakage-safe experimental cross-validation runners are `scripts/run_nmr_fixed_test_pilot.py` and `scripts/run_nmr_experimental_cv.py`. Experimental folds are grouped by canonical IUPAC; simulated counterparts of validation and test glycans are excluded from training.

The audited GCN, SchNet, DimeNet, DimeNet++, and ComENet baseline table and its
frozen evaluation artifacts are documented in
[`results/nmr_final_benchmark/`](results/nmr_final_benchmark/README.md).

To regenerate the bundle after an upstream update, download the raw GlycoNMR release of Chen et al. and rebuild:

```python
from glycogym import build_nmr, export_nmr

export_nmr(build_nmr(root="path/to/GlycoNMR"))
```

`root` must contain `GlycoNMR.Exp_processed/`, `GlycoNMR.Sim_processed/`, and `GODESS_Chemical_formula.csv`. Note that 110 of the 299 experimental files are named by DrugBank accession rather than by sequence and are currently dropped; resolving them would recover about a third of the experimental half.

To convert the result into PyG data objects, rename `IUPAC` to `clean_glycan` and pass it to `glycontact.learning.nmr_df_to_training_data`.

### Structural Property Estimation

The second dataset that requires special handling is the structural property estimation dataset. Currently, it needs to be build from the GlyContact package. That can be installed with the following command:

```bash
pip install glycontact[ml]
```

Then, the dataset can be built as follows:

```python
from glycontact.learning import create_dataset

train, val, test = create_dataset(splits=[0.7, 0.2, 0.1])
```

## Zenodo

The latest version of the GlycoGym benchmark can be found on Zenodo: https://doi.org/10.5281/zenodo.17313055

## Citation

tbd
