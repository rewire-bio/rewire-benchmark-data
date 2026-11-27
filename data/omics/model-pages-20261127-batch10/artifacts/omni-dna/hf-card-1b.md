---
license: mit
---

# Model Card for Omni-DNA

## Requirement

```bash
pip install datasets ai2-olmo
```

## Overview

Omni-DNA is a **cross-modal, multi-task genomic foundation model** designed to generalize across diverse genomic tasks. Unlike previous Genomic Foundation Models (GFMs), which require separate fine-tuning for each task, Omni-DNA leverages **auto-regressive transformer-based training** and **multi-task fine-tuning**, enabling a single model to perform a wide range of genomic tasks with **state-of-the-art** performance.

Omni-DNA models range from **20M to 1B** parameters and support tasks such as **sequence annotation, regulatory element classification, acetylation/methylation prediction, and DNA2Function/DNA2Image mapping**.

## Base Model Details

| Size  | Training Tokens | Layers | Hidden Size | Attention Heads | Context Length |
|-------|----------------|--------|-------------|-----------------|----------------|
| Omni-DNA 20M  | 300B | 8   | 256  | 8  | 250  |
| Omni-DNA 60M  | 300B | 8  | 512  | 8 | 250  |
| Omni-DNA 116M | 300B | 12  | 768 | 16 | 250  |
| Omni-DNA 300M | 300B | 16  | 1024 | 16 | 250  |
| Omni-DNA 700M | 300B | 16  | 1536 | 16 | 250  |
| Omni-DNA 1B   | 300B | 16  | 2048 | 16 | 250  |

## Model Description

<!-- - **Developed by:** Anonymous Authors -->
- **Supported by:** Microsoft Research Asia
- **Model type:** Auto-regressive transformer-based genomic model
- **License:** mit
- **Date cutoff:** 2024
- **Contact:** Research inquiries at `zl6222@ic.ac.uk`

## Model Sources

- **Paper:** [Omni-DNA: Scaling Auto-Regressive Transformer to Multi-Tasking Genomic Foundation Model](https://arxiv.org/abs/2502.03499)
- **Codebase:** https://github.com/Zehui127/Omni-DNA
- **Dataset:** Pretrained on **300B nucleotides** from multi-species genome datasets

## Capabilities

Omni-DNA is trained to perform **multiple genomic tasks** including:

- **Regulatory Element Classification:** Enhancer/promoter/splice site detection
- **Histone Modification Prediction:** Acetylation and methylation state identification
- **Genomic Function Annotation:** DNA-to-text mapping (DNA2Function)
- **Cross-modal Learning:** DNA-to-image mapping (DNA2Image)
- **Multi-task Learning:** A single model can solve multiple tasks simultaneously

## Usage

### As a Generative AutoRegressive Model

```python

from transformers import AutoModelForCausalLM, AutoTokenizer

# Load tokenizer and model
model_tokenizer_path = "anon/Omni-DNA-1B"
tokenizer = AutoTokenizer.from_pretrained(model_tokenizer_path)
model = AutoModelForCausalLM.from_pretrained(model_tokenizer_path).to('cuda')

def generate(message, task_type, model=model, sample_num=1):
    """Generate an output sequence given an input message."""    
    # Tokenize the input
    tokenized_message = tokenizer(
        [message], return_tensors='pt', return_token_type_ids=False, add_special_tokens=True
    ).to('cuda')
    # Generate response (deterministic mode)
    response = model.generate(**tokenized_message, max_new_tokens=sample_num, do_sample=False)
    # Alternative: Use stochastic sampling with top-k and top-p filtering
    # response = model.generate(**tokenized_message, max_new_tokens=1, do_sample=True, top_k=300, top_p=0.95)
    # Decode the generated sequence
    reply = tokenizer.batch_decode(response, skip_special_tokens=False)[0]
    # Remove spaces and extract relevant output
    reply = reply.replace(" ", "")
    return reply

# Example usage:
task = "DNA sequence classification"
message = "ATGCGTACGTAGCTAGCTAGCTAGCTAGCTA"
output = generate(message, task)
print(f"Generated output: {output}")
```

### Attaching Classification Head

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Load the model with a classification head
model = AutoModelForSequenceClassification.from_pretrained("zehui127/Omni-DNA-1B", num_labels=2, trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained("zehui127/Omni-DNA-1B", trust_remote_code=True)

### Finetuning the loaded model on the target task ... ###
# Define train_dataset, compute_metrics ...
trainer = transformers.Trainer(model=model,
                                tokenizer=tokenizer,
                                args=training_args,
                                compute_metrics=compute_metrics,
                                train_dataset=train_data,
                                eval_dataset=val_data,
                                data_collator=collate_fn)

# ... After finetuning: Example DNA sequence
sequence = "ATGCGTACGTAGCTAGCTAGCTAGCTAGCTA"

# Tokenize input sequence
inputs = tokenizer(sequence, return_tensors="pt")

# Forward pass
outputs = model(**inputs)

# Extract classification logits and get the predicted label
logits = outputs.logits
predicted_class = logits.argmax(dim=-1).item()

print(f"Predicted class: {predicted_class}")
```

### Supervised Finetuning (Make Prediction in the Generative Manner)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTTrainer, SFTConfig, DataCollatorForCompletionOnlyLM
from datasets import load_dataset, concatenate_datasets

# Load the pre-trained model and tokenizer
model_name = "zehui127/Omni-DNA-1B"
model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

# Load and process dataset (assumes JSON format)
dataset = load_dataset("json", data_files={"train": "path/to/train.json"})
dataset = dataset["train"]

# Group dataset by task type (if necessary)
def group_by_task_type(dataset):
    task_types = set(dataset['task'])
    task_datasets = {}
    for task in task_types:
        task_datasets[task] = dataset.filter(lambda x: x['task'] == task)
    return task_datasets

# Example formatting function for generative fine-tuning
def formatting_prompts_func(example):
    return [f"{example['instruction']} {example['task']} [SEP] {example['output']}"]

response_template = "[SEP]"
collator = DataCollatorForCompletionOnlyLM(response_template, tokenizer=tokenizer)

# Fine-tuning configuration
training_args = SFTConfig(
    per_device_train_batch_size=6,
    per_device_eval_batch_size=8,
    save_total_limit=1,
    max_seq_length=512,
    output_dir="./finetuned_omni_dna",
    save_safetensors=False,
    num_train_epochs=10,
    save_strategy="epoch",
    neftune_noise_alpha=5,  # Apply NEFT for regularization
)

# Trainer setup
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    args=training_args,
    formatting_func=formatting_prompts_func,
    data_collator=collator,
)

# Train the model
trainer.train()
```
