# Linked data

The canonical records can be read as RDF. Two files in `data/ontology/` define how, and one command exports the current release as N-Quads.

| File | Purpose |
| --- | --- |
| `data/ontology/mapping.json` | Maps each record kind to classes, each link relation to a property, and selected fields and attributes to properties. Each external term carries the reason it fits. Status: proposed. |
| `data/ontology/context.jsonld` | JSON-LD 1.1 context generated from the mapping. With it, every line of `data/entities/*.jsonl` and `data/evidence/*.jsonl` is a JSON-LD node. |

Identifiers are `https://benchmarks.rewire.it/id/<record id>`; the vocabulary is `https://benchmarks.rewire.it/vocab#`. External terms come from W3C ML Schema (`mls:`), DCAT, Dublin Core, PROV-O, schema.org and OBI, only where their meaning matches. Everything else stays in the rewire vocabulary.

## Rules

- Record IDs and values are never changed by the projection. Unmapped attributes are left out of the export, not renamed.
- `alias_of` maps to `rb:aliasOf`, not `owl:sameAs`, so a reasoner cannot merge records or their results without a review.
- An evaluation links to what was actually evaluated through `rb:evaluatedSubject`. `uses_model` (`rb:usesModel`) is not a subproperty of it and not transitive: a pipeline's result is never a result of a model it uses.
- Only public records are exported. Excluded, quarantined and private data never enter the graph.
- Mapping changes are reviewed like record changes. After editing `mapping.json`, run `npm run kg -- context` and commit the regenerated context.

## Commands

```sh
npm run kg -- context   # regenerate data/ontology/context.jsonld from the mapping
npm run kg -- export    # write public/kg/asserted.nq and public/kg/manifest.json
```

`npm run build` runs the export after the release. The output is sorted and deterministic: the same release and mapping give byte-identical files. The current release gives about 392,000 statements in one named graph, `https://benchmarks.rewire.it/graph/asserted`.

## Next steps

This is the asserted graph of the bundle described in the knowledge-graph and MCP server plan. Still to do: pinned ontology subsets, OWL 2 RL inference into a separate `inferred` graph, SHACL shapes, and publishing the bundle with each release.
