# Intake for issue #405

Add discovered model All-Atom Structure Tokenizer: AtomLM-9b for Biomolecular Structure Prediction: AtomLM-9b: all-atom structure tokenizer for biomolecular structure prediction

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-26. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-405-20261126-model-all-atom-structure-tokenizer` (model, depth tier 2)

## Sources

- https://www.biorxiv.org/content/10.64898/2026.11.03.763913v3: `intake-405-20261126-source-all-atom-structure-tokenizer-atomlm-9b-for-biomolecular-stru`, SHA-256 e6c45222f26485c5f24e1852cc8091e7cf6636de1fd5bf0f3f28a0bcff625c6a, text/html
- https://huggingface.co/Scinetics-ai/all-atom-structure-tokenizer: `intake-405-20261126-source-scinetics-ai-all-atom-structure-tokenizer-hugging-face`, SHA-256 e3ea58950513a3df4f5cf5f4870fc1dff98a89baabfb4c006cd9d124edff94a8, text/html
- https://arxiv.org/pdf/2610.23265: `intake-405-20261126-source-arxiv-org-pdf-2610-23265`, SHA-256 b85ed586ce6240373bbb27607011071271754cf69724bc4261a3107fa36c1ca4, application/pdf
- https://openreview.net/pdf/e42676bba18adf5798ad3a7fdd46bc756ad46b49.pdf: not opened (HTTP 403)

## Not added

- None.

## Links

- None.

## Possible duplicates in the store

- All-Atom Structure Tokenizer: AtomLM-9b for Biomolecular Structure Prediction against `lit-structure-20261011-lipp-model-rosettafold-aa` ("RoseTTAFold All-Atom"): distinct, The sources describe a tokenizer with a Qwen3.5-9B-based language model from Scinetics. RoseTTAFold All-Atom is a different, earlier model. The bioRxiv abstract names only AlphaFold 3 as the comparison. The two records share no address.

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| All-Atom Structure Tokenizer: AtomLM-9b for Biomolecular Structure Prediction | name | All-Atom Structure Tokenizer: AtomLM-9b for Biomolecular Structure Prediction | Yes |
| All-Atom Structure Tokenizer: AtomLM-9b for Biomolecular Structure Prediction | version |   | No |
| All-Atom Structure Tokenizer: AtomLM-9b for Biomolecular Structure Prediction | access | A Hugging Face repository (Scinetics-ai/all-atom-structure-tokenizer) holds a PyTorch reference implementation; per the  | Yes |
| All-Atom Structure Tokenizer: AtomLM-9b for Biomolecular Structure Prediction | licence |   | No |
| All-Atom Structure Tokenizer: AtomLM-9b for Biomolecular Structure Prediction | training_data |   | No |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 | 10510 | 3624 | 39621 | 7747 | 0 | 3 | $0.0058 |
| claude-sonnet-5-5 | 4 | 6728 | 10695 | 2160 | 0 | 0 | $0.0395 |
| Total | | | | | | | $0.0453 |
