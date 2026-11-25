# Intake for issue #385

Add discovered benchmark ELIXIR - Protein-Protein Interface Benchmark - OpenEBench Experiment: Physiological vs crystallographic protein homodimer interface classification benchmark

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-24. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-385-20261124-benchmark-elixir-protein-protein-interface-benchmark-openebench-experi` (benchmark, depth tier 2)

## Sources

- https://zenodo.org/records/24323530: `intake-385-20261124-source-elixir-protein-protein-interface-benchmark-openebench-experi`, SHA-256 43089d5188e8b54a5890b85bab980afe136e9d4db8ea5733f399182c2d64de43, text/html
- https://github.com/elixir-unibo/oeb_3dbioinfo_ppi_benchmark: `intake-385-20261124-source-github-elixir-unibo-oeb-3dbioinfo-ppi-benchmark-implementing`, SHA-256 f2ca8b5c67fa16660468f5b81aae22f8240d1d4091d0263bd0514dfe559883f4, text/html
- https://doi.org/10.1002/pmic.202200323: not opened (HTTP 403)

## Not added

- None.

## Links

- None.

Proposed but not written:

- ELIXIR - Protein-Protein Interface Benchmark - OpenEBench Experiment evaluates_task atom3d-task-pip: not supported at a location in a source

## Possible duplicates in the store

- None.

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| ELIXIR - Protein-Protein Interface Benchmark - OpenEBench Experiment | version |   | Yes |
| ELIXIR - Protein-Protein Interface Benchmark - OpenEBench Experiment | task | Classify a protein homodimer interface as physiological (a real biological assembly) or crystallographic (a crystal-pack | Yes |
| ELIXIR - Protein-Protein Interface Benchmark - OpenEBench Experiment | scope_note | Protein homodimer interfaces. The original study is Schweke et al., Proteomics 2023. | Yes |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 | 10438 | 4283 | 40752 | 7711 | 0 | 3 | $0.0058 |
| claude-sonnet-5-5 | 4 | 8032 | 10695 | 2165 | 0 | 0 | $0.0428 |
| Total | | | | | | | $0.0486 |

## Revision after review

- `intake-385-20261124-benchmark-elixir-protein-protein-interface-benchmark-openebench-experi` entity_level: changed `suite` to `challenge` (Zenodo Description defines one OpenEBench Challenge on one homodimer classification task).
- `intake-385-20261124-benchmark-elixir-protein-protein-interface-benchmark-openebench-experi` limitations: clarified the random-forest consensus leave-one-out upper-estimate note from the README 'Random-forest consensus' section and removed the clause concerning the separate FAIR dataset.
