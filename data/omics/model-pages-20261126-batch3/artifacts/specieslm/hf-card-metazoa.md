---
license: mit
---
```python
# Load the model
from transformers import AutoModelForMaskedLM, AutoTokenizer
model_name = "johahi/specieslm-metazoa-upstream-k6"
model = AutoModelForMaskedLM.from_pretrained(model_name, trust_remote_code=True)
# Load the corresponding tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)
```