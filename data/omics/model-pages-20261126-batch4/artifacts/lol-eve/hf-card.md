---
license: mit
tags:
- genomics
- dna
- language-model
- causal-lm
- biology
- sequence-modeling
- variant-prediction
- promoter
- indel
- eqtl
pipeline_tag: text-generation
library_name: transformers
---

# LOL-EVE: A Genomic Language Model for Zero-Shot Prediction of Promoter Variant Effects

## Model Description

LOL-EVE is a transformer-based model that processes DNA sequences with control codes to predict variant effects. The model was trained on 13.6 million mammalian promoter sequences and demonstrates state-of-the-art performance on promoter indel prediction tasks.

### Key Features

- **Large vocabulary**: 39,378 tokens including DNA bases, control codes, and special tokens
- **Control code integration**: Incorporates gene, species, and clade information
- **Protein context**: Uses pre-trained ESM embeddings for gene-specific understanding
- **Flexible input format**: Supports both basic DNA sequences and control code sequences
- **Zero-shot prediction**: Enables prediction of indel effects without task-specific training

## Usage

### Basic Usage

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained('Marks-lab/LOL-EVE')
model = AutoModelForCausalLM.from_pretrained('Marks-lab/LOL-EVE', trust_remote_code=True)

# Basic DNA sequence
sequence = "[MASK] [MASK] [MASK] [SOS]ATGCTAGCTAGCTAGCTAGCTA[EOS]"
inputs = tokenizer(sequence, return_tensors="pt")
outputs = model(**inputs)
```

### With Control Codes (Recommended)

```python
# Control code sequence (recommended)
control_sequence = "brca1 human primate [SOS] ATGCTAGCTAGCTAGCTAGCTA [EOS]"
inputs = tokenizer(control_sequence, return_tensors="pt")
outputs = model(**inputs)
```

### Variant Scoring

```python
import pandas as pd
import torch

def score_variants_hf(variants_df, gene, species, clade):
    """
    Score variants using the Hugging Face model.
    
    Args:
        variants_df: DataFrame with columns ['sequence', 'variant_sequence']
        gene: Gene name (e.g., 'brca1')
        species: Species name (e.g., 'human')
        clade: Clade information (e.g., 'primate')
    
    Returns:
        DataFrame with added 'score' column
    """
    scores = []
    
    for _, row in variants_df.iterrows():
        # Create control code sequences
        ref_seq = f"{gene} {species} {clade} [SOS] {row['sequence']} [EOS]"
        var_seq = f"{gene} {species} {clade} [SOS] {row['variant_sequence']} [EOS]"
        
        # Tokenize sequences
        ref_inputs = tokenizer(ref_seq, return_tensors="pt")
        var_inputs = tokenizer(var_seq, return_tensors="pt")
        
        # Get model outputs
        with torch.no_grad():
            ref_outputs = model(**ref_inputs)
            var_outputs = model(**var_inputs)
            
            # Calculate log-likelihood scores
            ref_logits = ref_outputs.logits[0, :-1]  # Exclude last token
            var_logits = var_outputs.logits[0, :-1]
            
            ref_tokens = ref_inputs['input_ids'][0, 1:]  # Exclude first token
            var_tokens = var_inputs['input_ids'][0, 1:]
            
            # Calculate sequence likelihood
            ref_score = torch.nn.functional.cross_entropy(ref_logits, ref_tokens, reduction='sum')
            var_score = torch.nn.functional.cross_entropy(var_logits, var_tokens, reduction='sum')
            
            # Score is the difference (higher = more deleterious)
            score = (var_score - ref_score).item()
            scores.append(score)
    
    variants_df['score'] = scores
    return variants_df

# Example usage
variants = pd.DataFrame({
    'sequence': ['ATGCTAGCTAGCTAGCTAGCTA', 'ATGCTAGCTAGCTAGCTAGCTA'],
    'variant_sequence': ['ATGCTAGCTAGCTAGCTAGCTA', 'ATGCTAGCTAGCTAGCTAGCTA']  # Example variants
})

scored_variants = score_variants_hf(variants, gene='brca1', species='human', clade='primate')
print(scored_variants)
```

### Input Format

The model expects sequences in the format:
```
gene species clade [SOS] sequence [EOS]
```

Where:
- `gene`: Gene name (e.g., "brca1", "tp53")
- `species`: Species name (e.g., "human", "mouse")
- `clade`: Clade information (e.g., "primate", "mammal")
- `[SOS]`: Start of sequence token
- `sequence`: DNA sequence (A, T, G, C)
- `[EOS]`: End of sequence token

## Model Architecture

- **Model type**: Causal Language Model (CTRL-based)
- **Layers**: 12 transformer layers
- **Hidden size**: 768 dimensions
- **Attention heads**: 12
- **Vocabulary size**: 39,378 tokens
- **Max sequence length**: 1,007 tokens
- **Position embeddings**: Adaptive local position embeddings

## Training Data

The model was trained on genomic sequences with:
- DNA sequences up to 1000 base pairs
- Gene-specific control codes
- Species and clade information
- Pre-trained ESM protein embeddings
- 13.6 million mammalian promoter sequences

## Performance

LOL-EVE demonstrates state-of-the-art performance on:

### Benchmarks
- **Ultra-rare variant prioritization**: Prioritizing ultra-rare variants in gnomAD
- **Causal eQTL identification**: Identifying causal expression quantitative trait loci
- **Transcription factor binding site disruption**: Analyzing TFBS disruption by indels


## Datasets

- **[LOL-EVE-UltraRare](https://huggingface.co/datasets/Marks-lab/LOL-EVE-UltraRare)** - Ultra-rare variant benchmark dataset
- **[LOL-EVE-eQTL_benchmark](https://huggingface.co/datasets/Marks-lab/LOL-EVE-eQTL_benchmark)** - eQTL benchmark dataset
- **[PromoterZoo Training Data](https://huggingface.co/datasets/Marks-lab/PromoterZoo/blob/main/README.md)** - PromoterZoo Training Data

## Citation

If you use LOL-EVE in your research, please cite:

```bibtex
@article{loleve2025,
  title={A Genomic Language Model for Zero-Shot Prediction of Promoter Variant Effects},
  author={[Authors]},
  journal={MLCB 2025},
  year={2025}
}
```

## License

This model is released under the MIT License. See the [LICENSE](https://github.com/Marks-lab/LOL-EVE/blob/main/LICENSE) file for more details.

## Repository

- **GitHub**: [https://github.com/debbiemarkslab/LOL-EVE](https://github.com/debbiemarkslab/LOL-EVE)
- **Paper**: [MLCB 2025 version coming end of month!](https://www.biorxiv.org/content/10.1101/2024.11.11.623015v1) (link to be updated)

## Contact

For questions or issues, please contact [your-email@domain.com] or open an issue on the [GitHub repository](https://github.com/Marks-lab/LOL-EVE).
