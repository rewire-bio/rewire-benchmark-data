# Linked data

The canonical records can be read as RDF. Each release also produces a knowledge-graph bundle: the records as RDF, the facts that follow from the vocabulary (OWL 2 RL inference) in a separate graph, and the vocabulary itself. Claude and other MCP clients can query the bundle through [rdf-kg-mcp](https://github.com/rewire-bio/rdf-kg-mcp).

| File | Purpose |
| --- | --- |
| `data/ontology/mapping.json` | Maps each record kind to classes, each link relation to a property, and selected fields and attributes to properties. Each external term carries the reason it fits. Status: proposed. |
| `data/ontology/context.jsonld` | JSON-LD 1.1 context generated from the mapping. With it, every line of `data/entities/*.jsonl` and `data/evidence/*.jsonl` is a JSON-LD node. |
| `data/ontology/rb.ttl` | The rewire vocabulary: every `rb:` class and property, with labels, definitions and the axioms the build reasons over. |
| `data/ontology/imports/` | Pinned copies of ML Schema, PROV-O and DCAT, and extracted subsets of OBI and schema.org. `sources.json` records where each came from, its version, licence and checksum. |
| `data/ontology/shapes.ttl` | SHACL shapes the build validates against. |

Identifiers are `https://benchmarks.rewire.it/id/<record id>`; the vocabulary is `https://benchmarks.rewire.it/vocab#`. External terms come from W3C ML Schema (`mls:`), DCAT, Dublin Core, PROV-O, schema.org and OBI, only where their meaning matches. Everything else stays in the rewire vocabulary.

## Rules

- Record IDs and values are never changed by the projection. Unmapped attributes are left out of the export, not renamed.
- `alias_of` maps to `rb:aliasOf`, not `owl:sameAs`, so a reasoner cannot merge records or their results without a review.
- An evaluation links to what was actually evaluated through `rb:evaluatedSubject`. `uses_model` (`rb:usesModel`) is not a subproperty of it and not transitive: a pipeline's result is never a result of a model it uses.
- Some relations mean something different depending on the record kind. `by_kind` in the mapping gives those links their own property: on a baseline, `evaluation` is `rb:measuredIn` and `model` or `configuration` is `rb:implementedBy`; on a dataset subset, `benchmark` is `rb:usedIn`. The JSON-LD context keeps the relation name for these links.
- Only public records are exported. Excluded, quarantined and private data never enter the graph.
- Mapping and vocabulary changes are reviewed like record changes. After editing `mapping.json`, run `npm run kg -- context` and commit the regenerated context.

## Inference

The build runs the OWL 2 RL rules over the asserted graph and the vocabulary, and keeps the new statements whose subject is a record. Statements about blank nodes, `owl:Thing` typing and reflexive `owl:sameAs` are dropped. For the current release this adds about 220,000 statements to the 392,000 asserted ones.

| Inferred property | Meaning | From |
| --- | --- | --- |
| `rb:testedSystem` | Evaluation to the system it tested, whichever link style the record uses | `rb:evaluatedSubject`, or the typed `rb:configuration`, `rb:method`, `rb:pipeline`, `rb:service` links |
| `rb:testedOn` | Evaluation to the task or protocol it used | `rb:evaluatedOn`, `rb:protocol`, `rb:task` |
| `rb:dataset` | Evaluation to its dataset, including subsets | `rb:datasetSubset` |
| `rb:within`, `rb:contains` | Task or protocol inside a benchmark or suite, transitively, and the reverse | `dcterms:isPartOf`, `rb:parent` |
| `rb:resultFor`, `rb:resultOn`, `rb:resultOnDataset` | Result to the system, assessment and dataset of its evaluation | chains through `rb:evaluation` |
| `rb:testedWithin`, `rb:resultWithin` | Evaluation or result to every benchmark containing its task or protocol | chains through `rb:within` |
| `rb:hasResult`, `rb:testedIn` | The reverse of `rb:evaluation` and `rb:testedSystem` | inverses |
| `rdf:type` | Superclasses, such as `rb:System`, `rb:Assessment`, `rb:Dataset` for subsets, `mls:Run`, `prov:Entity` | the class hierarchy and PROV-O |
| `prov:wasInfluencedBy`, `prov:influenced` | PROV-O generalisations of `prov:wasDerivedFrom` | PROV-O |

The build fails, and nothing is published, if:

- the reasoner finds an inconsistency, or a record is typed `owl:Nothing`;
- `owl:sameAs` is inferred between records;
- a protected link is inferred: `rb:evaluation`, `rb:evaluatedSubject`, the typed subject links, `rb:family`, `rb:variantOf`, `rb:aliasOf`, `rb:usesModel`, `rb:status` or `mls:hasValue`;
- a result's inferred `rb:resultFor` is not what its evaluation tested;
- SHACL validation fails. Among other checks, every evaluation has exactly one tested system, assessment and dataset, and every result exactly one evaluation, system, assessment and dataset.

`scripts/kg/tests` checks these rules on the vocabulary itself and on a small fixture, including a pipeline that uses a model and a configuration in a family, so a vocabulary change that would let results move between records fails the tests.

## Commands

```sh
npm run kg -- context   # regenerate data/ontology/context.jsonld from the mapping
npm run kg -- export    # write public/kg/asserted.nq and an export manifest
npm run kg:build        # inference, checks and SHACL; writes inferred.nq, ontology/ and the bundle manifest
npm run test:kg         # vocabulary and inference tests
```

`npm run build` runs the export and the KG build after the release. The KG build needs [uv](https://docs.astral.sh/uv/), which installs the pinned Python dependencies in `scripts/kg/requirements.txt`. It takes about three minutes and 1.5 GB of memory. The output is sorted and deterministic: the same release, mapping and vocabulary give byte-identical files.

To update a pinned vocabulary, download it, re-run the extraction command in `data/ontology/imports/sources.json` where one is listed, update the checksum there, and review the change in the inferred graph.

## Bundle

`public/kg/` holds a bundle in [rdf-kg-mcp format 1.0](https://github.com/rewire-bio/rdf-kg-mcp/blob/main/docs/bundle-format.md):

| Path | Graph | Contents |
| --- | --- | --- |
| `asserted.nq` | `https://benchmarks.rewire.it/graph/asserted` | The public records |
| `inferred.nq` | `https://benchmarks.rewire.it/graph/inferred` | Inferred statements about records |
| `ontology/` | `https://benchmarks.rewire.it/graph/ontology` | `rb.ttl` and the pinned imports |
| `manifest.json` | | Checksums, counts, graph roles, prefixes, reasoner and SHACL details, example queries |

When a push to `main` builds a release that has no bundle yet, CI publishes it as `kg-bundle.tar.gz` on a GitHub release tagged `kg-<release id>`. An existing release is never replaced. To query it from Claude Code:

```sh
claude mcp add rewire-benchmarks -- uvx --from git+https://github.com/rewire-bio/rdf-kg-mcp@v0.1.0 \
  rdf-kg-mcp serve https://github.com/rewire-bio/rewire-benchmark-data/releases/download/kg-<release id>/kg-bundle.tar.gz
```

Or serve a local build with `rdf-kg-mcp serve public/kg`.
