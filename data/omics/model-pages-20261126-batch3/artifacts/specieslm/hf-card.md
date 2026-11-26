---
license: mit
---

Load each model using:

```python
from transformers import AutoTokenizer, AutoModelForMaskedLM

tokenizer = AutoTokenizer.from_pretrained("gagneurlab/SpeciesLM", revision = "<<choose model type>>")
model = AutoModelForMaskedLM.from_pretrained("gagneurlab/SpeciesLM", revision = "<<choose model type>>")
```

Model type:  
- Species LM, 3' region: `downstream_species_lm`  
- Agnostic LM, 3' region: `downstream_agnostic_lm`  
- Species LM, 5' region: `upstream_species_lm`  
- Agnostic LM, 5' region: `upstream_agnostic_lm`  
