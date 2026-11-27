---
license: mit
---


This is a model card for MULAN-small protein language model introduced in the paper [MULAN: Multimodal Protein Language Model for
Sequence and Structure Encoding](https://www.biorxiv.org/content/10.1101/2024.05.30.596565v1). 
It has 9M parameters.

It can be loaded using the [MULAN repository](https://github.com/DFrolova/MULAN):

```python
from mulan.model import StructEsmForMaskedLM

model = StructEsmForMaskedLM.from_pretrained(
    'DFrolova/MULAN-small',
    device_map="auto",
)
```