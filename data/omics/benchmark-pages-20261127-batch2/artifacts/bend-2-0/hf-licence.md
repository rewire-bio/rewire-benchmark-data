# Data sources and terms

This collection contains data from several sources. Each file retains the terms
listed below; this notice does not replace those terms. The BEND 2.0 software
license does not apply to third-party data.

The three larger source files (`opensplice.tsv.gz`, `siraj.zip` and `hg38.2bit`)
are unchanged copies. The remaining files are benchmark selections, prepared
measurements or BEND 2.0 metadata. Their preparation is described in [FILES.md](FILES.md)
and the original [asset manifest](assets.json).

| Files under `data/` | Source and applicable terms |
| --- | --- |
| `opensplice.tsv.gz` | OpenSplice experimental master table, [Figshare version 5](https://doi.org/10.6084/m9.figshare.32337414.v5). [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). |
| `siraj.zip`, `siraj-numeric-reference.npz`, `siraj_selective.parquet` | Siraj et al., *Functional dissection of complex and molecular trait variants at single nucleotide resolution*, [Zenodo 15297965](https://doi.org/10.5281/zenodo.15297965). [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). |
| `atlas-population.parquet`, `atlas-programs.csv`, `atlas-source-activities.parquet`, `atlas-candidate-activities.parquet` | Castillo-Hair et al., *Programming human cell type-specific gene expression via an atlas of AI-designed enhancers*, [Zenodo 17410822](https://doi.org/10.5281/zenodo.17410822). [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). |
| `hg38.2bit`, `prior-panel.parquet` | Genome Reference Consortium GRCh38, distributed by UCSC. [Assembly-specific use and distribution terms](https://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips/README.txt) and [UCSC data terms](https://www.genome.ucsc.edu/license/). |
| `gtex-targets.npz` | GTEx v10 public median-expression summary, under the [GTEx Portal data license](https://gtexportal.org/home/license). |
| `gtex-genes.tsv` | GTEx's GENCODE v39 gene annotation. [GENCODE data access and attribution](https://www.gencodegenes.org/pages/data_access.html), [EMBL-EBI terms](https://www.ebi.ac.uk/about/terms-of-use/) and [GTEx terms](https://gtexportal.org/home/license). |
| `prior-query-seeds.json` | BEND 2.0 reproducibility metadata, under the project [MIT license](licenses/MIT.txt). |

## Attribution and changes

CC BY 4.0 permits sharing and adaptation with attribution, a license link and an
indication of changes. CC BY-NC 4.0 provides those permissions for noncommercial
purposes. Rehosting the Siraj files here does not grant commercial-use rights.
Retain the original source credits and notices with redistributed copies.

**Siraj and ENCODE.** The cell-selective measurements were derived from ENCODE
files [ENCFF769XOF](https://www.encodeproject.org/files/ENCFF769XOF/) and
[ENCFF526SMM](https://www.encodeproject.org/files/ENCFF526SMM/), produced by Ryan
Tewhey's laboratory. We acknowledge the ENCODE Consortium and the producing
laboratory. Follow [ENCODE's attribution guidance](https://www.encodeproject.org/help/citing-encode/)
and [data-use policy](https://www.encodeproject.org/about/data-use-policy/).
The combined Siraj-derived table retains the Siraj release's noncommercial terms.

**GTEx.** We acknowledge the GTEx Project and GTEx Portal as the source of the
public expression summaries. The GTEx files are a frozen BEND 2.0 subset of
**GTEx v10** and do not necessarily reflect the most current or accurate data
available from the GTEx Portal. They contain public aggregate expression, not
individual-level genotype or donor data. No endorsement by GTEx is implied.
The exact input URLs are recorded in `assets.json`:

- [GTEx v10 median TPM](https://storage.googleapis.com/adult-gtex/bulk-gex/v10/rna-seq/GTEx_Analysis_v10_RNASeQCv2.4.2_gene_median_tpm.gct.gz)
- [GENCODE v39 annotation distributed with GTEx v10](https://storage.googleapis.com/adult-gtex/references/v10/reference-tables/gencode.v39.GRCh38.genes.gtf)

**Reference genome.** We acknowledge the Genome Reference Consortium and UCSC
Genome Browser. This release contains GRCh38 reference sequence and fixed
benchmark windows, not personal genomes. The download-directory README records
the assembly's upstream use and distribution terms.

The dataset title, preparation and benchmark organization do not imply endorsement
by any of the original data producers. Please cite the original studies as well
as BEND 2.0 when using their data.
