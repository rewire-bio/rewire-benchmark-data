# Brief: say which checkpoint and which subset each result is for

The Rewire knowledge base holds results as papers report them. To compare a result in one paper with a result
in another, two things must be known about each one that are today only in free text:

- **which released checkpoint or version was run.** The store links a result to a model family ("Evo 2",
  "CADD", "phyloP", "Nucleotide Transformer"), which merges things that score differently: Evo 2 40B, 7B and
  7B base; CADD v1.3 and v1.7; phyloP 100-way and 447-way.
- **which subset of the data the number is for.** One protocol often holds results for all variants, coding
  variants and noncoding variants, or for several cohorts, and only the free-text locator says which.

You are given `clinvar-brca1.json`: the results (observations) that fall in nine comparison settings around
ClinVar and BRCA1 variant classification, each with its system name and description, the model family it is
linked to, the protocol, the metric, the value, the locator that says where in the source it was read, the
conditions recorded, and the study it comes from. `checkpoints.json` lists checkpoints already known.

Work only from these two files. Do not use the network, do not touch any git repository, do not start
sub-agents. Write only the output files named below, in the same folder, using absolute paths.

## What to produce

`grounding.jsonl`, one line per observation:

```json
{"observation_id": "...", "system_key": "evo-2-7b", "system_label": "Evo 2 7B", "system_basis": "system name says 'Evo 2 7B'",
 "adaptation": "zero-shot", "subset": "all-snvs", "subset_basis": "locator: Supplementary Data 1, sheet BRCA1, row 'All SNVs'",
 "confidence": "high"}
```

- `system_key`: a short lower-case identifier for the exact thing that was run, as specific as the file
  allows: family, size, version, and scoring variant where one model is scored two ways (for example
  `gpn-msa-llr`, `cadd-v1-7`, `phylop-100way`, `nucleotide-transformer-v2-500m-multispecies-llr`). The same key
  must mean the same thing across studies. When the file does not say which version or size, end the key with
  `-unspecified` and say so in `system_basis`. Never guess a version.
- `adaptation`: `zero-shot`, `linear-probe`, `fine-tuned`, `supervised` (trained for this task), `precomputed-scores`,
  or `unspecified`.
- `subset`: a short lower-case identifier for the part of the data the number is for (`all`, `coding`,
  `noncoding`, `missense`, a cohort name such as `clinvar-2023-12-holdout`), consistent across studies within a
  setting. Use `all` only when the source reports the whole set of the setting. Use `unspecified` when the file
  does not say.
- `confidence`: `high` when name, locator or conditions state it outright; `medium` when it follows from two
  fields together; `low` when it is your best reading.

`grounding-notes.md`: a short plain-English note: the list of system keys you used with what each means, the
list of subsets per setting, and anything in the data that looks wrong or that a human must decide.

Write a script to do this systematically (rules over the fields, then a pass by eye over what the rules leave
as `unspecified`), run it with `python3 -I`, keep it in the folder as `ground.py`, and check before you finish
that every observation in the input has exactly one line in the output.

Then, in `comparisons.md`, list every case where the same `system_key`, in the same setting, the same metric and
the same `subset`, has values from two or more different `study_id` that differ by more than rounding: the
setting, the key, the subset, each study's value and its source name. This is the test of the grounding: with
checkpoints and subsets pinned, only real differences should remain.

Reply with: the number of observations grounded, how many have `unspecified` for the system and for the subset,
the number of distinct system keys, and the number of cases in `comparisons.md` with the three largest.
