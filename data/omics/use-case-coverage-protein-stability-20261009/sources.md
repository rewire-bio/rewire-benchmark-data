# Sources: protein variant stability use-case pass, 2026-10-09

The four sources behind the existing judgements are not duplicated. All three new sources are Europe PMC full-text XML. Hashes are SHA-256 of the bytes read. Gzip copies (`gzip -n -9`) are in `artifacts/`.

| Source ID | Title | Version | Retrieved (UTC) | Artifact URL | SHA-256 | Licence |
| --- | --- | --- | --- | --- | --- | --- |
| `protein-stability-20261009-source-pancotti2022` | Predicting protein stability changes upon single-point mutation: a thorough comparison of the available tools on a new dataset | Briefings in Bioinformatics 23(2):bbab555, 2022-01-11; PMC8921618 XML | 2026-10-09T21:00:42Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8921618/fullTextXML | `132038084a57c060add54f152f68a69ccaf198337f86a5ec03d39496945c0024` | CC BY-NC 4.0 |
| `protein-stability-20261009-source-dieckhaus2024` | Transfer learning to leverage larger datasets for improved prediction of protein stability changes | PNAS 121(6):e2314853121, 2024-01-29; PMC10861915 XML | 2026-10-09T21:01:06Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10861915/fullTextXML | `ba9a763c388eeea47d70fd0d8e2fbf497f61fc8a88dc93d5dac261572daa8010` | CC BY-NC-ND 4.0 |
| `protein-stability-20261009-source-chu2024` | Protein stability prediction by fine-tuning a protein language model on a mega-scale dataset | PLOS Computational Biology 20(7):e1012248, 2024-07-22; PMC11293664 XML | 2026-10-09T21:01:08Z | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11293664/fullTextXML | `bb9830cbd6bab1b3e0ddbb52edb2a9afd4b06e427dbfeb19e6a07f843ebd914f` | CC BY 4.0 |

## Existing records reused, not changed

| Record | Use in this pass |
| --- | --- |
| `discovery-model-esm-2` | Model family for the two ESM-2 checkpoint configurations; ESM therm links `uses_model` to it |
| `discovery-model-proteinmpnn` | Model family for the ProteinMPNN configuration; ThermoMPNN links `uses_model` to it |

## Archived copies

| File | SHA-256 of gzip |
| --- | --- |
| `artifacts/chu2024-article.xml.gz` | `249fac22220dc82fc718524bf286e9142e4e34094c541a4ac8fac117b4c63758` |
| `artifacts/dieckhaus2024-article.xml.gz` | `925a164bc3cdaf4df852dc6800f0d98ef4ae066c06c8fdfe93543e480182bca4` |
| `artifacts/pancotti2022-article.xml.gz` | `25aff1c34bab07a3b0b21765e0391fc3741d45810b88431caf738e5a636f4f1b` |
