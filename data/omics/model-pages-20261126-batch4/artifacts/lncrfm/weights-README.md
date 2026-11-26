# LncRFM pretrained weights

FP32 checkpoint at 300,000 steps. Maximum context: 2,050 tokens.
Use with the LncRFM source distribution and its environment.
Place this directory at `checkpoints/lncrfm_pretrained` in the source project.

```python
from pathlib import Path
import json
import torch
from lncrfm import get_lncrfm, get_tokenizer

checkpoint = Path("checkpoints/lncrfm_pretrained")
options = json.loads((checkpoint / "model_config.json").read_text())["factory_kwargs"]
tokenizer = get_tokenizer(
    tokenizer_file=str(checkpoint / "tokenizer.json"),
    max_length=options["max_length"],
)
model = get_lncrfm(
    **options,
    tokenizer=tokenizer,
    from_pretrained=str(checkpoint),
    dtype=torch.float32,
).to("cuda").eval()
```

For downstream runs, set `LNCRFM_CHECKPOINT` to this directory.

License: see `LICENSE`.
