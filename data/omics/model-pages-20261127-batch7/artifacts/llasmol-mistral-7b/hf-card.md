---
language:
  - en
license: cc-by-4.0
tags:
  - instruction tuning
  - chemistry
  - molecule
  - small molecule
---

<p align="center">
<img style="width: 20%;" src="llasmol.png">
</p>

<h1 align="center">  LlaSMol  </h1>
<h3 align="center"> LlaSMol-Mistral-7B </h3>

**Paper**: [LlaSMol: Advancing Large Language Models for Chemistry with a Large-Scale, Comprehensive, High-Quality Instruction Tuning Dataset](https://arxiv.org/abs/2402.09391)

**Page**: [https://osu-nlp-group.github.io/LLM4Chem](https://osu-nlp-group.github.io/LLM4Chem)

**Code**: [https://github.com/OSU-NLP-Group/LLM4Chem](https://github.com/OSU-NLP-Group/LLM4Chem)

**Models**: 
- LlaSMol-Galactica-6.7B: [https://huggingface.co/osunlp/LlaSMol-Galactica-6.7B](https://huggingface.co/osunlp/LlaSMol-Galactica-6.7B)
- LlaSMol-Llama2-7B: [https://huggingface.co/osunlp/LlaSMol-Llama2-7B](https://huggingface.co/osunlp/LlaSMol-Llama2-7B)
- LlaSMol-CodeLlama-7B: [https://huggingface.co/osunlp/LlaSMol-CodeLlama-7B](https://huggingface.co/osunlp/LlaSMol-CodeLlama-7B)
- LlaSMol-Mistral-7B: [https://huggingface.co/osunlp/LlaSMol-Mistral-7B](https://huggingface.co/osunlp/LlaSMol-Mistral-7B)

LlaSMol-Mistral-7B is an LLM for chemistry. It is based on [mistralai/Mistral-7B-v0.1](https://huggingface.co/mistralai/Mistral-7B-v0.1) and tuned on our [SMolInstruct](https://huggingface.co/datasets/osunlp/SMolInstruct) dataset with LoRA. This repo contains the weight of the low-rank adapter.

## ⚔️ Usage

For instructions to run the model, please refer to our [repository](https://github.com/OSU-NLP-Group/LlaSMol).


## 🚨 Limitations

While the model is carefully trained, we do not guarantee its effectiveness. The model may output incorrect or inaccurate information. Please use it at your own risk.

Additionally, the model is built as a mature product but solely for research purpose. It may generate harmful or biased information. We emphatically urge all users to adhere to the highest ethical standards when using the model, including maintaining fairness, transparency, and responsibility in their research. Any usage of the dataset that may lead to harm or pose a detriment to society is strictly **forbidden**.

## 📚 Citation
If our paper or related resources prove valuable to your research, we kindly ask for citation. Please feel free to contact us with any inquiries.

```
@article{yu2024llasmol,
  title={LlaSMol: Advancing Large Language Models for Chemistry with a Large-Scale, Comprehensive, High-Quality Instruction Tuning Dataset},
  author={Botao Yu and Frazier N. Baker and Ziqi Chen and Xia Ning and Huan Sun},
  journal={arXiv preprint arXiv:2402.09391},
  year={2024}
}
```
