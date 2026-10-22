export const meta = {
  name: 'evidence-pass',
  description: 'Search, extract per source, review per source, then add one use-case evidence batch',
  whenToUse: 'A use-case evidence pass in rewire-benchmark-data (docs/collection.md). Pass args: issue, useCase, worktree, batch, cutoff, queryBudget, heavy, maxSources.',
  phases: [
    { title: 'Search', detail: 'literature-search skill, one agent' },
    { title: 'Extract', detail: 'extract-evaluations skill, one agent per source' },
    { title: 'Review', detail: 'review-evidence skill, one independent agent per source' },
    { title: 'Judge', detail: 'use-case record, relevance judgements and summary, then their review' },
    { title: 'Finalise', detail: 'merge parts, hash receipt, add to store, run checks, commit' },
  ],
}

// args: {issue: 178, useCase: 'lead-optimisation-affinity-ranking', lane: 'interactions',
//        worktree: '/abs/path', batch: 'data/omics/use-case-coverage-x-20261022',
//        cutoff: '2026-10-22', queryBudget: 25, heavy: '/abs/path/heavy.sh', maxSources: 4,
//        question: 'one paragraph on the decision and endpoint'}
const a = args || {}
for (const k of ['issue', 'useCase', 'worktree', 'batch', 'cutoff', 'heavy']) {
  if (!a[k]) throw new Error(`missing args.${k}`)
}
const MAX = a.maxSources || 4
const WT = a.worktree
const B = `${a.batch}`

const COMMON = `Repository worktree: ${WT} (work only here; do not touch other worktrees or the main checkout).
Issue: #${a.issue} in rewire-bio/rewire-benchmark-data (read it with gh issue view). Use case: ${a.useCase}.
Batch folder: ${B}. Follow docs/collection.md as it stands in the worktree, including "Running a pass with agents".
Do not spawn sub-agents. Do not run npm store, test, typecheck or build commands unless this brief says so; when it does, wrap each in ${a.heavy}.
Do not commit or push unless this brief says so. Name yourself honestly in reviewer fields ("Claude ... agent; no human review claimed").
Write long material to files in the batch folder; your final answer is the structured output only.`

const SEARCH = {
  type: 'object',
  properties: {
    candidates: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          key: { type: 'string', description: 'short slug, e.g. ross2023' },
          citation: { type: 'string' },
          url: { type: 'string' },
          tables: { type: 'array', items: { type: 'string' } },
          why: { type: 'string' },
          questions: { type: 'array', items: { type: 'string' }, description: 'ambiguities the extractor must decide from the source text' },
        },
        required: ['key', 'citation', 'url', 'tables', 'why', 'questions'],
      },
    },
    queries_used: { type: 'number' },
    gaps: { type: 'array', items: { type: 'string' } },
  },
  required: ['candidates', 'queries_used', 'gaps'],
}

const PART = {
  type: 'object',
  properties: {
    part: { type: 'string', description: 'path of the part file written' },
    source_id: { type: 'string' },
    artifact: { type: 'string', description: 'absolute path of the pinned artifact whose SHA-256 is on the source record (the PDF or XML as downloaded)' },
    text: { type: 'string', description: 'absolute path of what check-values reads: the XML itself, or the pdftotext -layout output of the PDF' },
    records: { type: 'number' },
    questions: { type: 'array', items: { type: 'string' }, description: 'what the reviewer must rule on' },
    gaps: { type: 'array', items: { type: 'string' } },
  },
  required: ['part', 'source_id', 'artifact', 'text', 'records', 'questions', 'gaps'],
}

const REVIEW = {
  type: 'object',
  properties: {
    value_check: { type: 'string', description: 'status counts from batch check-values' },
    rulings: {
      type: 'array',
      items: {
        type: 'object',
        properties: { question: { type: 'string' }, ruling: { type: 'string' }, source_text: { type: 'string' } },
        required: ['question', 'ruling', 'source_text'],
      },
    },
    changes: { type: 'array', items: { type: 'string' } },
    ready: { type: 'boolean', description: 'false if the part should go to pending-review' },
  },
  required: ['value_check', 'rulings', 'changes', 'ready'],
}

phase('Search')
const search = await agent(`${COMMON}

Run the literature-search skill (.agents/skills/literature-search/SKILL.md) for this use case.
Question: ${a.question || 'see the issue'}
Lane: ${a.lane || 'see the issue'}. Search window cutoff: ${a.cutoff}. Query budget: ${a.queryBudget || 25}, counting failures.
Read what the store already holds first and do not duplicate it.
Write one ledger entry for the pass, scope-audit decisions, and ${B}/notes.md. Do not write records.
Return the candidates worth extracting, best first. State open points as questions, not conclusions.`,
  { label: 'search', phase: 'Search', schema: SEARCH, effort: 'medium' })

if (!search || !search.candidates.length) {
  log('Search found no candidate to extract; recording the search pass only.')
  const recorded = await agent(`${COMMON}

The search found nothing to extract. You may run store commands under ${a.heavy}, and commit (house style, referencing #${a.issue}, no AI attribution). Do not push.
Write a short dated review docs/reviews/use-cases/<slug>-<date>.md saying what was searched and that nothing new was found, pointing to the ledger entry and ${B}/notes.md.
If ${a.useCase} already exists in the store, set its evidence_checked (docs/use-cases.md) and record it with npm run records -- change <dated review> ${B} <use-case id>.
Run npm run records -- check and npm run test:fast, then commit the ledger, scope-audit, notes and review.`,
    { label: 'record-search', phase: 'Finalise', effort: 'medium' })
  return { search, recorded }
}
const sources = search.candidates.slice(0, MAX)
if (search.candidates.length > MAX) {
  log(`Extracting ${MAX} of ${search.candidates.length} candidates; not reached: ${search.candidates.slice(MAX).map(c => c.key).join(', ')}`)
}

const reviewed = await pipeline(
  sources,
  (c) => agent(`${COMMON}

Run the extract-evaluations skill for ONE source: ${c.citation} (${c.url}).
Tables to extract in full: ${c.tables.join('; ')}.
Why it matters: ${c.why}
Decide these from the source text and record your reasoning in ${B}/notes/${c.key}.md:
${c.questions.map((q) => `- ${q}`).join('\n') || '- none raised'}
Retrieve and hash the artifact; keep it, and the pdftotext -layout output you read for a PDF, under the scratchpad, not the repo. Write locators in the documented form, with double quotes: Table 2, row "X", column "Y".
Before returning, run python3 scripts/omics/batch.py check-values on a temporary folder holding your part as batch.jsonl, and fix any row it cannot confirm that is your error.
Search the store and reuse existing IDs. Write ONLY your records to ${B}/parts/${c.key}.jsonl (other agents are writing other parts).
Do not create the use_case record, relevance judgements or the summary; a later stage does that.
Keep any table spec or parse script in ${B}/extract/${c.key}.*`,
    { label: `extract:${c.key}`, phase: 'Extract', schema: PART, effort: 'medium' }),
  (part, c) => part && agent(`${COMMON}

You are the independent reviewer for ${part.part} (source ${part.source_id}). You did not extract it.
Run the review-evidence skill on this part only, but do NOT write review.json, do NOT add anything to the store and do NOT run repin: a later stage does those once.
First run: python3 scripts/omics/batch.py check-values <a temporary folder holding this part as batch.jsonl> ${part.source_id}=${part.text}
and investigate every row that is not in_cell or in_row. Then a sampled manual check, including column assignment for text-layer tables.
Rule on each of these with the deciding source text:
${part.questions.map((q) => `- ${q}`).join('\n') || '- none raised'}
Make corrections in ${part.part} itself and fill each record's review block. Add your rulings to ${B}/notes/${c.key}.md under a Review heading.`,
    { label: `review:${c.key}`, phase: 'Review', schema: REVIEW, effort: 'high' })
      .then((r) => r && { key: c.key, part, review: r }),
)

const done = reviewed.filter(Boolean)
const ready = done.filter((d) => d.review.ready)
const notReady = done.filter((d) => !d.review.ready)
if (notReady.length) log(`Not ready, to pending-review: ${notReady.map((d) => d.key).join(', ')}`)
if (!ready.length) return { search, reviewed: done }

phase('Judge')
const parts = ready.map((d) => d.part.part).join(', ')
const judged = await agent(`${COMMON}

Parts reviewed and ready: ${parts}.
Create the use_case record ${a.useCase} with every field docs/use-cases.md requires, or, if it already exists in the store, write the updated copy (keep its ID; add assessed_by links, gaps and evidence_checked), one relevance judgement claim per protocol in these parts that bears on the use case, and a descriptive summary claim (no recommendation; every number traceable to a result). Status needs_review. Write them to ${B}/parts/use-case.jsonl.
Questions to put to the judgement reviewer go in your answer.`,
  { label: 'judge', phase: 'Judge', schema: PART, effort: 'high' })

const judgeReview = judged && await agent(`${COMMON}

You are the independent reviewer of the use-case record, relevance judgements and summary in ${judged.part}. You did not write them.
Follow review-evidence step 4. Check each judgement's endpoint, direct/proxy call and limitations against the parts it rests on (${parts}).
Rule on: ${judged.questions.join(' | ') || 'none raised'}.
Fill reviewed_evaluations and review blocks in ${judged.part}; do not run repin yet.`,
  { label: 'review:judgements', phase: 'Judge', schema: REVIEW, effort: 'high' })

phase('Finalise')
const final = await agent(`${COMMON}

Finalise the batch. You may run store commands under ${a.heavy}, and commit (house style, referencing #${a.issue}, no AI attribution). Do not push.
1. Merge ${parts}${judgeReview && judgeReview.ready ? `, ${judged.part}` : ''} into ${B}/batch.jsonl, sorted by id. Move any part not listed to data/omics/pending-review/ with a README.
2. Append ${B}/notes/*.md to ${B}/notes.md under one heading per source, then delete ${B}/notes/ and ${B}/parts/. Write the dated review docs/reviews/use-cases/<slug>-<date>.md from those rulings and the value-check counts below. No per-value table.
3. Fill review.json's descriptive fields, then: python3 scripts/omics/batch.py hash ${B} ${ready.map((d) => `${d.part.source_id}=${d.part.artifact}`).join(' ')}
4. Records whose ID already exists in the store (an existing use_case record, existing judgements) are not added: take them out of batch.jsonl, edit them in their canonical file and record them with npm run records -- change <dated review> ${B} <ids>. Then npm run records -- add ${B}/batch.jsonl ${B} for the new records; npm run use-cases:repin -- <dated review> <reviewed claim ids>; npm run release:fetch (once, so the release-dependent tests can load); npm run records -- check; npm run test:fast; npm run typecheck.
5. Commit. Report failures as they are; do not regenerate the receipt to clear one.
Value checks: ${ready.map((d) => `${d.key}: ${d.review.value_check}`).join('; ')}`,
  { label: 'finalise', phase: 'Finalise', effort: 'medium' })

return { search, reviewed: done, judged, judgeReview, final }
