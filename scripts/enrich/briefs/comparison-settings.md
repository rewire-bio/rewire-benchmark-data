# Brief: find which evaluations in different papers are the same test

The Rewire benchmark database holds results extracted from papers. Each paper's evaluation was recorded as its
own "protocol" record, so two papers that ran the same benchmark almost never share a protocol: 1,984 of 2,012
protocols hold results from exactly one study. That hides every disagreement between papers. Your job is to work
out, for one cluster of protocols, which of them are the same test, so their results can be compared.

You are given one JSON file. It lists the protocols in a cluster (for example every protocol that mentions
ProteinGym), each with its description, attributes, links, datasets, sources, metrics and up to 400 of its
results (system name, the model it resolves to, metric, value, conditions, origin), plus the task and benchmark
records that already exist for the cluster.

Work only from that file. Do not use the network, do not touch any git repository, do not start sub-agents, and
write only the output file named below.

## What to produce

Write `<cluster>.proposal.json` next to the input file:

```json
{
  "cluster": "...",
  "settings": [
    {
      "key": "proteingym-substitutions-zero-shot-spearman",
      "name": "ProteinGym DMS substitutions, zero-shot, Spearman",
      "definition": "What data, what split or subset, what a model is given, what is scored, how it is aggregated.",
      "existing_task_id": "the id of an existing task that already means exactly this, or null",
      "protocols": [
        {"protocol_id": "...", "comparability": "same", "metric": "spearman", "why": "evidence from the file",
         "differences": "any difference a reader must know: assay count, aggregation, version, subset"}
      ]
    }
  ],
  "unassigned": [{"protocol_id": "...", "why": "why it belongs to no shared setting"}],
  "disagreements": [
    {"setting": "key", "model": "name", "model_id": "...", "metric": "...",
     "values": [{"protocol_id": "...", "source": "source name", "value": 0.44, "result_id": "..."}],
     "kind": "same_model_different_value | ranking_reversal",
     "note": "one sentence: what differs and the most likely innocent explanation, if the file suggests one"}
  ],
  "notes": "anything about the cluster a human should know"
}
```

Rules:

- A *setting* is one test that different papers could run and get comparable numbers on: the same data (and
  version), the same subset or split, the same input to the model, the same metric and the same aggregation.
  Make a setting only when at least the data and what is scored match. One protocol can belong to one setting
  per metric.
- `comparability` is `same` (numbers should agree up to rounding and run-to-run variation), `near` (same data and
  metric, a stated difference such as assay subset, version or aggregation that could move the number a little),
  or `related` (same benchmark family, not comparable number for number). Be strict: when the file does not show
  that two protocols match on a point, say so in `differences` and use `near` or `related`.
- Say what evidence in the file supports each assignment. Do not rely on what you know about the benchmark
  beyond what its name tells you; if the description is too thin to decide, put the protocol in `unassigned`.
- For `disagreements`, list every case inside a `same` or `near` setting where the same model (use `model_id`)
  has values from two different sources that differ by more than rounding, and every case where two sources
  order the same pair of models oppositely. Different checkpoints or sizes of a model are different systems:
  compare like with like, and say when you cannot tell.
- Plain English, no em dashes or arrows.

Finish by replying with: the number of settings, how many protocols and distinct sources they cover, the number
of protocols left unassigned, the number of disagreements, and the three disagreements most worth a human look.
