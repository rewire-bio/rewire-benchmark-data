---
license: apache-2.0
---

# MP-RNA: Multi-Species RNA Foundation Model

## Model Description

**MP-RNA** is a multi-species RNA foundation model designed to enhance the performance of in-silico RNA genomic tasks. This model addresses key challenges in RNA secondary structure prediction and single nucleotide resolution tasks by incorporating large-scale structure annotations and secondary structure prediction during pretraining. MP-RNA consistently outperforms existing RNA foundation models by achieving a 40% improvement in secondary structure prediction and demonstrating top-tier results on various RNA and DNA genomic benchmarks.

- **Model type**: Transformer-based (52M and 186M parameter versions)
- **Languages**: RNA sequences
- **Pretraining**: The model is pretrained using large-scale RNA sequence datasets, including the OneKP plant transcriptome data, filtered and segmented for optimal RNA understanding. It employs ViennaRNA for secondary structure prediction.
- **Key Features**: 
  - RNA secondary structure prediction 
  - Single nucleotide mutation detection and repair 
  - Generalizability to DNA genomic tasks despite being pretrained only on RNA sequences.

## Intended Use

This model is designed for:
- RNA secondary structure prediction
- Single nucleotide mutation detection and repair
- RNA modeling tasks like mRNA degradation rate prediction
- Transferability to DNA genomic tasks

It is a valuable tool for researchers working on RNA modeling, genomic sequence analysis, and functional genomics.

## Limitations

MP-RNA primarily relies on in-silico experiments, and in-vivo validation is yet to be confirmed. The model's pretraining scale is relatively small due to resource constraints.

## Training Data

The MP-RNA model was trained on large-scale RNA sequences from the OneKP initiative, containing transcriptome data from over 1,000 plant species. These sequences were curated, segmented, and preprocessed to reduce noise and bias. The pretraining process also included generating RNA secondary structures using ViennaRNA for enhanced structure modeling.

## Evaluation Results

MP-RNA was benchmarked on several genomic tasks, showing significant improvements over baseline models. It achieved the highest performance in RNA secondary structure prediction, single nucleotide mutation detection, and repair. Additionally, it demonstrated strong transferability to DNA genomic tasks like polyadenylation site classification and chromatin accessibility prediction.

## How to use

Here’s a sample code to load and use the model on Hugging Face:

```python
from transformers import AutoTokenizer, AutoModel

# Load pre-trained model tokenizer
tokenizer = AutoTokenizer.from_pretrained("yangheng/MP-RNA")

# Load pre-trained model
model = AutoModel.from_pretrained("yangheng/MP-RNA")

# Example input sequence
input_seq = "AUGGCUACUUUCG"

# Tokenize input
inputs = tokenizer(input_seq, return_tensors="pt")

# Perform inference
outputs = model(**inputs)
```

## Citation

If you use this model in your research, please cite the following:

Yang, H., Li, K. (2024). MP-RNA: Unleashing Multi-Species RNA Foundation Model via Calibrated Secondary Structure Prediction. *EMNLP 2024 Findings*. [Link to paper](https://github.com/yangheng95/OmniGenomeBench)

## License

This model is released under the Apache 2.0 License.
