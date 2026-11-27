# Intake for issue #467

Add discovered method Few-shot regulatory sequence design with a genomic language model: Design regulatory DNA from a few in-context examples in Evo 2

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-27. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-467-20261127-method-few-shot-regulatory-sequence-design-with-a-genomic-language` (method, depth tier 1)

## Sources

- https://www.biorxiv.org/content/10.64898/2026.10.28.762639v1: not opened (HTTP 429)
- https://www.biorxiv.org/content/10.64898/2026.10.28.762639v2: `intake-467-20261127-source-few-shot-regulatory-sequence-design-with-a-genomic-language`, SHA-256 2176f074eb42cd8fe352b9aaca9995f3ba92197a22e029d8cbebea5a4f63dac1, text/html
- https://arcinstitute.org/news/evo-2-in-context-learning: `intake-467-20261127-source-evo-2-uses-in-context-learning-to-design-de-novo-regulatory`, SHA-256 7558123a6c0622a1420ce73e1e01e654a9b2c8da4cc789bb7d8572a1ef580773, text/html
- https://github.com/evo-design/ICL: not opened (HTTP 404)
- https://github.com/evo-design/ICL_regulatory: `intake-467-20261127-source-github-evo-design-icl-regulatory-github`, SHA-256 a494b0f145b99d2ccaa8af04639b3936691f46c33428cb7aa34829b27ad174d6, text/html
- https://github.com/evo-design/evo2_flash: `intake-467-20261127-source-github-evo-design-evo2-flash-efficient-inference-for-evo-2-g`, SHA-256 32647918c82821ba1b7a5b55e350850ac2d254bafee4313ce25940c154ef4559, text/html
- https://proto.evodesign.org/tools/evo2-icl: `intake-467-20261127-source-evo-2-in-context-design-proto`, SHA-256 fc0501afdd8521ac6b01492e2d8cc97c7ac549883ee7a634bcfd2b309bc65c3e, text/html
- https://doi.org/10.64898/2026.10.28.762643: not opened (HTTP 429)

## Not added

- None.

## Links

- None.

## Possible duplicates in the store

- Few-shot regulatory sequence design with a genomic language model against `vep-lit-20261014-method-sequence-unet` ("Sequence UNET"): distinct, No source mentions Sequence UNET. The method here is Evo 2 in-context learning for regulatory sequence design, a different resource. The store record was not opened.

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| Few-shot regulatory sequence design with a genomic language model | source |   | Yes |
| Few-shot regulatory sequence design with a genomic language model | source |   | Yes |
| Few-shot regulatory sequence design with a genomic language model | version |   | No |
| Few-shot regulatory sequence design with a genomic language model | access |   | No |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 | 12052 | 4603 | 41836 | 7941 | 0 | 3 | $0.0062 |
| claude-sonnet-5-5 | 4 | 14665 | 10695 | 2346 | 0 | 0 | $0.0612 |
| Total | | | | | | | $0.0674 |
