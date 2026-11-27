# Structured facts on model and benchmark records, 2026-11-27

Prepared by Claude agents. No human review is claimed.

## What changed

Model and benchmark records may now carry two new attributes, each a list:

- `checkpoints`, on model records: one entry per released checkpoint, with its name, parameter count and context length as whole numbers, the context unit, the code and weights licences, the code and weights addresses, whether access is gated, and the release date.
- `benchmark_tasks`, on benchmark records: one entry per task or track, with the dataset, its size as a whole number and the unit, the split rule, the primary metric and whether higher or lower is better, the addresses of results, code and data, the data and code licences, and the release date.

A value the sources do not give is null. A release date is a full date, or a year and month where that is all the source gives (two MSA Transformer entries).

The schemas are in `shared/omics/structured-facts.ts`. The benchmark attribute is named `benchmark_tasks`, not `tasks`, because `tasks` is already the name of a facet and the two would share one term in the JSON-LD context.

The values are not new. Each page batch since batch 4 of 26 November, and the revision batch of 27 November (`model-pages-20261127-revision1`), wrote them as a `structured` list in its content files under `data/omics/model-pages-*/specs/` and `data/omics/benchmark-pages-*/specs/`, next to the profile. Every value was judged by a verifier agent when its page was checked. This change copies them onto the records so that the website can show them.

## Records and entries

| Kind | Tier | Records | Entries |
| --- | --- | --- | --- |
| Model | 1 | 55 | 158 |
| Model | 2 | 95 | 218 |
| Model | 3 | 49 | 89 |
| Benchmark | 1 | 49 | 308 |
| Benchmark | 2 | 24 | 122 |
| Benchmark | 3 | 25 | 105 |
| All | | 297 | 1000 |

The eight Tier 1 models that sit on two records each (batch `model-pages-20261127-batch10` and its `-twins` batch) have the list on both records.

Model batches 1, 2 and 3 of 26 November wrote no structured list, and the corrections batch that revised 28 of their pages did not add one. Revision 1 of 27 November revised 36 Tier 1 pages from the full text of their papers and gave each a list: 22 from batches 1 to 3, which had none, and 14 from batches 4 and 5, whose lists it replaces. The other 52 records of batches 1 to 3 get no `checkpoints` until their pages are revised. The corrections batch also revised three batch 4 pages that already had a list (GenSLM, RNAGenesis, TREDNet). Of the 316 model records with a profile, 199 now have `checkpoints`; the others are the 52 above, MSNovelist (below), and 64 pages written before the batch tools or outside them (among them LIMBER and GPN-MSA), which have no content file with a list.

## How each entry is tied to its sources

Each entry in a content file quotes passages from the files saved for that page, naming the source by its key in the file (`@paper`, `@hf-config`). On the record the quotes are replaced by:

- `source_ids`: the source records for the keys the entry quotes. When a batch was prepared, `scripts/enrich/enrich.py prepare` gave each source the id `<batch>-<page>-source-<key>`, or cited an existing source record that already held the same bytes from the same address, and wrote the ids it chose into the batch's `models.json` or `benchmarks.json`. `scripts/enrich/structured.py` reads those ids and accepts one only if it is a source record with the SHA-256 the content file gives and the record already cites it. All 874 cited sources were tied this way. 619 are source records made for the page itself; 109 were made by an earlier batch for the same model's page and cited again by revision 1; 101 were made for another page and reused because the bytes and address are the same; 39 are the sibling record's sources in batch 10, cited by the twins batch; 6 are batch 4 sources cited by the corrections batch.
- `source_locator`: which saved file holds each passage and which fields the passage states, for example `hf-api.json: parameters; hf-config.json: context length`. Which fields a passage states is found by matching the entry's values in the passage text (numbers in their written forms, addresses, licence names, most of the words of a text value). A passage in which no value is found this way is listed as a supporting passage; 263 of the 1000 entries have at least one. The passages themselves stay in the content files.

Where a record has content files in two batches, the later batch's list is used. A corrections or revision batch counts as later than the other batches of its date. Before this change `kb/curate.py` put the 26 November corrections batch before batches 2 to 4, so the knowledge base held the uncorrected RNAGenesis entry; its second checkpoint now has the release date the corrections found (2025-08-29).

## Left out

One record: `lit-otheromics-20261011-msgwild-model-msnovelist`. Its only entry quotes no passage, so it cannot be tied to a source. The knowledge base still reads it from the content file.

## How to repeat

```
python3 scripts/enrich/structured.py plan structured-facts-20261127
python3 scripts/enrich/structured.py apply structured-facts-20261127
```

The plan is in `data/omics/structured-facts-20261127/changes.json`, with the left-out record and the reason. `kb/curate.py` now reads the `checkpoint` and `benchmark_task` tables from the records and falls back to the content files only for records without the attribute.
