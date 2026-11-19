# Which stored record is this table about

You are given the words a scientific paper or supplementary workbook prints around one table,
and a shortlist of records already held in a benchmark catalogue. Say which one record on the
shortlist the table reports, or say that you cannot tell.

You are not given any of the table's numbers, and you must not ask for them. The only question
is what the table is about.

## The answer

Answer with these four fields and nothing else.

- `record_id`: one id copied exactly from the shortlist, or the single word `none`.
- `quote`: a run of words copied character for character from the caption shown under
  `Caption`, and from nowhere else. It must be the part of the caption that names what the
  table reports. Where the answer is `none`, leave it empty.
- `confidence`: `high`, `medium` or `low`.
- `reason`: one sentence saying why that record and not another, or why you cannot tell.

`confidence` is a statement about the quote, not about your general impression:

- `high` only when the quoted words name the record: the record's own name, or the words of it,
  are in what you quoted.
- `medium` when the caption describes what the record covers without naming it.
- `low` when the shortlist holds one plausible record and the caption does not settle it.

An answer whose quote does not appear in the caption is discarded, as is a `high` whose quote
does not name the record. A quote invented or paraphrased is worse than no answer.

## When to answer `none`

Answer `none` whenever any of these is true. It is the expected answer, not a failure, and it
costs far less than a wrong one: an unlabelled table is work left to do, a wrongly labelled one
is a false statement in a public catalogue.

- No record on the shortlist is what the table reports.
- Two or more records on the shortlist fit and the caption does not separate them.
- The table reports more than one benchmark or task, for instance one per column block.
- The caption is a bare label such as a sheet name or `Table S3`, and nothing in the columns
  says what was evaluated.
- The table reports counts, inputs, hardware, timings or dataset composition rather than the
  result of an evaluation.

A record that is close to the table's subject but not the same thing is a `none`. A benchmark
suite is not one of its tasks, and a task is not the dataset it runs on.

## What the shortlist is

The shortlist was built by a program from the catalogue, by two rules: the record already cites
this source, or the words of the record's name occur in the table's own printed words. It is
not a list of the answers that are likely. It can hold several records that are nothing to do
with this table, and it can hold none that are. You may only answer with an id printed on it.

Do not reason about which id looks most like a catalogue would use. Read what the table says it
reports, and match that.
