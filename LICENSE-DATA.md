# Data licence

This file covers the data in this repository and in its releases. The code and scripts are under the MIT licence in [LICENSE](LICENSE).

## The position in one sentence

The compilation and annotations made by Rewire in this release are offered under CC BY 4.0; values and text taken from cited sources stay under the terms of those sources and are not covered by this licence.

No single licence covers a release file. Most of what a release holds is values taken from cited sources.

## What is licensed

Licensor: Tim Richardson, who writes and maintains Rewire.

Licence: Creative Commons Attribution 4.0 International (`CC-BY-4.0`). The full text is at https://creativecommons.org/licenses/by/4.0/legalcode and a summary is at https://creativecommons.org/licenses/by/4.0/.

It covers:

> The selection and arrangement of the records, their identifiers and links, use-case definitions, relevance judgements, review statuses, origin labels, discrepancy findings and follow-up, summaries written for the database, and the results of runs Rewire carried out.

You may copy, share and adapt that material for any purpose, including commercially, if you give credit and say what you changed.

## What is not licensed

It does not cover:

> Values and text taken from cited sources, the licence text recorded for a model, and the source documents. Each stays under the terms of its source.

In this repository that means:

- **Cited values.** A score, a sample count or a fact about a model or dataset that a record takes from a publication is the source's. The record carries the citation and the place in the source it was read from. Credit the source for the value.
- **Quoted text, titles, names and trade marks.** They stay with their owners.
- **Stored copies of sources.** The repository and its release assets hold copies of some source files, so that a recorded value can be checked against the bytes it was read from. Each copy stays under the licence of its source, and so does a text layer extracted from a copy: it is the source's text in another format, not Rewire's work. Holding or publishing a copy here grants nothing in it. Some of those licences do not allow commercial use, and some do not allow changes. [docs/source-preservation.md](docs/source-preservation.md) says which copies are published, which are kept privately, and the licence each source was read as carrying.
- **Model licences.** The licence recorded for a model is the licence of that model's weights or code, as its developers state it. It is not a licence for this data.
- **Imported vocabularies.** The files under `data/ontology/imports/` are copies or subsets of other projects' ontologies. Each stays under its own terms. `data/ontology/imports/sources.json` gives the address and the licence of each.

If you reuse a value, cite the publication it came from as well as this database. If you reuse quoted text or a source file, check that source's terms first.

## Attribution

Name the release you used, because the data changes with each release:

> Rewire biological model benchmark database, release `<release id>`. https://benchmarks.rewirebio.io/

## Takedown

A rights holder who wants a stored copy of a source removed should write to tim@rewire.it. The procedure and its one limit, that a file committed to this public repository cannot be removed from its git history, are in [docs/source-preservation.md](docs/source-preservation.md#takedown).

## No warranty

The data is offered as it is, for research, with no warranty. It is not clinical advice.
