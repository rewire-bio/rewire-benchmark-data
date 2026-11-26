# Brief: verify model page content against its sources

Another agent wrote the page content for a set of biological AI models. Each model folder holds:
- `spec.json`: the content. Every statement (the summary, each section, fact, strength, limitation, the diagram,
  each run step, each `structured` entry if present) carries `quotes`: passages said to be copied from a saved source.
- `artifacts/`: the saved source files the quotes come from.

A checker has already confirmed every quote occurs in its file. It cannot tell whether the statement actually
follows from the quote. That is your job. You are an independent reviewer: assume nothing is right.

For each model folder you are given:

1. Read `spec.json`. For every statement, read its quotes, and where needed open the source file around the quote.
2. Judge the statement:
   - `supported`: everything it asserts is stated in, or follows directly from, the quoted passages or the text
     immediately around them in the same source.
   - `partly`: the core is supported but it adds a detail, number, name or qualifier the sources read do not give.
   - `unsupported`: the sources do not say it, say something different, or the statement comes from general
     knowledge of the model and not from the files.
   - `wrong`: the sources contradict it (a different number, a different licence, a different checkpoint).
   Numbers, licence names, parameter counts, context lengths, checkpoint names, URLs and commands must match the
   source exactly. A fact with status `unreported`, `unextracted` or `unavailable` is a claim that the sources read
   do not give the value: check that by searching the saved files for it, and mark it `wrong` if they do give it.
3. For each run step, check the commands appear in the sources as written, apart from the additions the step's
   `explanation` owns up to (a clone line, a heredoc wrapper, a pinned checkout). An undisclosed invented flag,
   path or model name is `unsupported`.
4. Write `verify.json` in the model folder:

```json
{
  "record_id": "...",
  "statements_checked": 31,
  "findings": [
    {"where": "fact Parameters", "verdict": "wrong", "statement": "the text as written",
     "source_says": "what the file says, quoted", "fix": "the corrected text, or 'remove'"}
  ],
  "summary": "one or two sentences on the overall reliability of this page"
}
```

List only statements that are `partly`, `unsupported` or `wrong`. `statements_checked` counts all statements you
judged. Give a concrete `fix` for every finding, written from the source text, in plain English with no em dashes
or arrows. Do not edit `spec.json` or anything under `artifacts/`. Do not fetch anything from the network: judge
only against the saved files. Do not start sub-agents. Write nothing outside the model folders.

When done, reply with: the number of models checked, the total statements checked, the totals for partly,
unsupported and wrong, and the five most serious findings in one line each.
