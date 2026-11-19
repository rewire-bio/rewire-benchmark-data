/** The label stage, over a document built here rather than fetched, and never over a network.
 *
 * The propositions, each of which would be a defect if it failed.
 *
 * 1. No cell value reaches the question. The stage is given text and asked which record a
 *    table is about, so a wrong answer cannot be a wrong value. If a printed value ever
 *    appeared in the rendered question that would stop being true.
 * 2. The unit of work is the table. Every candidate of one table is one question.
 * 3. Every acceptance check refuses on its own, and a refusal leaves the table unlabelled with
 *    the reason recorded rather than weakening the answer.
 * 4. A field the deterministic pass decided is never asked about and never changed.
 * 5. The same table is never asked twice: a second run reads the cache and the transport is
 *    not called.
 * 6. Nothing calls out. Every test here answers from a recording, and the live path is
 *    exercised only far enough to prove it fails by name when the key is absent.
 */
import { describe, expect, it } from "vitest";
import { layerOf, readGrid } from "../shared/archive/layers/index";
import { indexLayer } from "../shared/omics/spans/offsets";
import { gridCandidates } from "../shared/omics/extract/grid-pass";
import { buildDecider } from "../shared/omics/extract/decide";
import type { Candidate } from "../shared/omics/extract/candidate";
import {
  ANCHOR_MINIMUM,
  KEY_VARIABLE,
  NONE,
  PER_TABLE_FILE,
  RECEIPT_STATEMENT,
  SHORTLIST_MAX,
  answerJsonSchema,
  answerSchema,
  buildShortlistIndex,
  cacheKey,
  checkAnswer,
  contentWords,
  labelCache,
  labelTables,
  labelsByCandidate,
  liveTransport,
  loadPrompt,
  readAnswer,
  recordedTransport,
  renderQuestion,
  requestDigest,
  shortlistFor,
  tablesOf,
  type AssessmentRecord,
  type LabelReply,
  type LabelRequest,
  type LabelTable,
} from "../shared/omics/extract/label/index";

const page = `<!doctype html><html><body>
<p>We report variant effect prediction on ClinVar, and a runtime comparison on ClinVar.</p>
<table>
<caption>Table 2. Variant effect prediction on ClinVar.</caption>
<thead><tr><th>Model</th><th>AUROC</th><th>Spearman</th></tr></thead>
<tbody>
<tr><td>Alpha-1</td><td>0.812</td><td>0.44</td></tr>
<tr><td>Beta-2</td><td>0.790</td><td>0.31</td></tr>
</tbody>
</table>
<table>
<caption>Table 3. Wall clock seconds per thousand variants.</caption>
<thead><tr><th>Model</th><th>Seconds</th></tr></thead>
<tbody>
<tr><td>Alpha-1</td><td>12.5</td></tr>
</tbody>
</table>
</body></html>`;

/** The store this run is measured against: small, written here, and nothing like the real one
 * except in shape. */
const records: AssessmentRecord[] = [
  { id: "clinvar-variant-effect", kind: "benchmark", name: "Variant effect prediction on ClinVar", source_ids: ["fixture-source"] },
  { id: "clinvar-runtime", kind: "task", name: "Runtime on ClinVar" },
  { id: "proteingym-dms", kind: "benchmark", name: "ProteinGym DMS substitutions" },
  { id: "alpha-1-model", kind: "model", name: "Alpha-1" },
];

function extract(): { candidates: Candidate[]; index: ReturnType<typeof indexLayer> } {
  const tree = layerOf(Buffer.from(page, "utf8"), { mediaType: "text/html" });
  const text = tree.layer;
  const grid = tree.grid;
  if (!text || !grid) throw new Error("the fixture produced no text layer or no grid");
  const index = indexLayer(text.bytes.toString("utf8"), text.output_sha256, text.normaliser);
  const read = gridCandidates({
    decider: buildDecider([]),
    sourceId: "fixture-source",
    index,
    grid: readGrid(grid.bytes.toString("utf8")),
    gridLayerSha256: grid.output_sha256,
    sanity: "pass",
  });
  return { candidates: read.candidates, index };
}

const tableAbout = (candidates: Candidate[], word: string): LabelTable => {
  const found = tablesOf(candidates).find((table) => table.anchor_text.includes(word));
  if (!found) throw new Error(`no table whose caption holds ${word}`);
  return found;
};

/** A reply the recorded transport answers with, as a hand-written fixture would hold it. */
const reply = (answer: { record_id: string; quote: string; confidence?: string; reason?: string }): string =>
  JSON.stringify({ confidence: "high", reason: "the caption names it", ...answer });

describe("the unit of work", () => {
  it("makes one question of a table however many cells it holds", () => {
    const { candidates } = extract();
    const tables = tablesOf(candidates);
    expect(tables).toHaveLength(2);
    const effect = tableAbout(candidates, "Variant effect");
    // Two rows and two value columns in the first table, one row and one in the second.
    expect(effect.candidate_ids).toHaveLength(4);
    expect(effect.anchor_text).toBe("Table 2. Variant effect prediction on ClinVar.");
    expect(effect.anchor_text_from).toBe("caption");
    expect(effect.column_headers).toEqual(["AUROC", "Spearman"]);
    expect(effect.row_labels).toEqual(["Alpha-1", "Beta-2"]);
  });

  it("covers its own cells with the extent the cache is keyed on", () => {
    const { candidates, index } = extract();
    const effect = tableAbout(candidates, "Variant effect");
    const spans = candidates.filter((candidate) => effect.candidate_ids.includes(candidate.candidate_id)).map((candidate) => candidate.span);
    expect(effect.extent.start).toBe(Math.min(...spans.map((span) => span.start)));
    expect(effect.extent.end).toBe(Math.max(...spans.map((span) => span.end)));
    expect(effect.layer_sha256).toBe(index.layer_sha256);
  });

  it("keeps a row label or heading that prints no name out of the question, and counts it", () => {
    const { candidates } = extract();
    const numbered = candidates.map((candidate) =>
      candidate.row_label === "Beta-2" ? { ...candidate, row_label: "0.633980785512857" } : candidate,
    );
    const table = tableAbout(numbered, "Variant effect");
    expect(table.row_labels).toEqual(["Alpha-1"]);
    expect(table.held_back.numeric).toBe(1);
    const question = renderQuestion({ table, shortlist: shortlistFor(buildShortlistIndex(records, []), table), sourceTitle: "A fixture paper" });
    expect(question).not.toContain("0.633980785512857");
    expect(question).toContain("print no name");
  });

  it("is stable over reruns, ids and order alike", () => {
    expect(tablesOf(extract().candidates)).toEqual(tablesOf(extract().candidates));
  });
});

describe("the question", () => {
  it("prints no value from the table", () => {
    const { candidates } = extract();
    const index = buildShortlistIndex(records, []);
    const table = tableAbout(candidates, "Variant effect");
    const question = renderQuestion({ table, shortlist: shortlistFor(index, table), sourceTitle: "A fixture paper" });
    for (const value of ["0.812", "0.790", "0.44", "0.31"]) expect(question).not.toContain(value);
    expect(question).toContain("AUROC");
    expect(question).toContain("clinvar-variant-effect");
  });

  it("prints every shortlisted id and nothing the filter held back", () => {
    const { candidates } = extract();
    const index = buildShortlistIndex(records, []);
    const table = tableAbout(candidates, "Variant effect");
    const shortlist = shortlistFor(index, table);
    const question = renderQuestion({ table, shortlist, sourceTitle: "A fixture paper" });
    for (const id of shortlist.ids) expect(question).toContain(id);
    expect(question).not.toContain("alpha-1-model");
  });
});

describe("the pre-filter", () => {
  it("narrows by the two rules it states, and by nothing else", () => {
    const index = buildShortlistIndex(records, []);
    const { candidates } = extract();
    const shortlist = shortlistFor(index, tableAbout(candidates, "Variant effect"));
    expect(shortlist.ids).toContain("clinvar-variant-effect");
    // A model is not of a result-carrying kind, so it is never in the index at all.
    expect(shortlist.ids).not.toContain("alpha-1-model");
    // A benchmark whose name the table prints none of is not reachable.
    expect(shortlist.ids).not.toContain("proteingym-dms");
    const cited = shortlist.entries.find((entry) => entry.id === "clinvar-variant-effect");
    expect(cited?.why).toEqual(["cites_this_source", "name_in_table"]);
  });

  it("reaches a record the store does not yet cite, by its printed name alone", () => {
    const index = buildShortlistIndex(records.map((record) => ({ ...record, source_ids: [] })), []);
    const { candidates } = extract();
    const shortlist = shortlistFor(index, tableAbout(candidates, "Variant effect"));
    expect(shortlist.ids).toContain("clinvar-variant-effect");
    expect(shortlist.entries.find((entry) => entry.id === "clinvar-variant-effect")?.why).toEqual(["name_in_table"]);
  });

  it("follows companion_of, because a workbook and its paper are one study", () => {
    const index = buildShortlistIndex(
      [{ id: "only-here", kind: "benchmark", name: "Something else entirely", source_ids: ["fixture-paper"] }],
      [{ id: "fixture-source", links: [{ relation: "companion_of", target_id: "fixture-paper" }] }],
    );
    const { candidates } = extract();
    expect(shortlistFor(index, tableAbout(candidates, "Variant effect")).ids).toEqual(["only-here"]);
  });

  it("caps the list and says how many it held back", () => {
    const many: AssessmentRecord[] = Array.from({ length: SHORTLIST_MAX + 6 }, (unused, at) => ({
      id: `cited-${String(at).padStart(2, "0")}`,
      kind: "benchmark",
      name: `Cited benchmark ${at}`,
      source_ids: ["fixture-source"],
    }));
    const index = buildShortlistIndex(many, []);
    const { candidates } = extract();
    const shortlist = shortlistFor(index, tableAbout(candidates, "Variant effect"));
    expect(shortlist.ids).toHaveLength(SHORTLIST_MAX);
    expect(shortlist.held_back).toBe(6);
    expect([...shortlist.ids].sort()).toEqual(shortlist.ids);
  });

  it("gives the same bytes for the same store and the same table", () => {
    const { candidates } = extract();
    const table = tableAbout(candidates, "Variant effect");
    expect(JSON.stringify(shortlistFor(buildShortlistIndex(records, []), table))).toBe(
      JSON.stringify(shortlistFor(buildShortlistIndex(records, []), table)),
    );
  });

  it("drops the words that would match everything and keeps the ones that carry meaning", () => {
    expect(contentWords("Table 3. The accuracy of a benchmark")).toEqual(["accuracy", "benchmark"]);
    expect(contentWords("SupTable8_Tool_performance")).toEqual(["suptable8", "tool", "performance"]);
  });
});

/** Every check in turn, each on its own, each built by hand so the failure is the only thing
 * that differs from the passing case. */
describe("the acceptance checks", () => {
  const run = (over: Partial<Parameters<typeof checkAnswer>[0]>) => {
    const { candidates, index } = extract();
    const table = tableAbout(candidates, "Variant effect");
    const shortlist = shortlistFor(buildShortlistIndex(records, []), table);
    return checkAnswer({
      table,
      shortlist,
      answer: { record_id: "clinvar-variant-effect", quote: "Variant effect prediction on ClinVar", confidence: "high", reason: "the caption names it" },
      index,
      record: { id: "clinvar-variant-effect", kind: "benchmark" },
      names: ["variant effect prediction on clinvar"],
      ...over,
    });
  };

  it("accepts an answer that passes all of them, with a span in the source's own layer", () => {
    const checked = run({});
    expect(checked.outcome).toBe("labelled");
    if (checked.outcome !== "labelled") return;
    expect(checked.record_id).toBe("clinvar-variant-effect");
    expect(checked.span.exact).toBe("Variant effect prediction on ClinVar");
    expect(checked.span.layer_sha256).toHaveLength(64);
    expect(checked.checks.every((check) => check.passed)).toBe(true);
  });

  it("refuses an id the question never offered", () => {
    const checked = run({ answer: { record_id: "invented-benchmark", quote: "Variant effect prediction on ClinVar", confidence: "low", reason: "." } });
    expect(checked).toMatchObject({ outcome: "refused", reason: "not_in_shortlist" });
  });

  it("refuses an id the store does not hold", () => {
    const { candidates, index } = extract();
    const table = tableAbout(candidates, "Variant effect");
    const shortlist = shortlistFor(buildShortlistIndex(records, []), table);
    const checked = checkAnswer({
      table,
      shortlist,
      answer: { record_id: shortlist.ids[0], quote: "Variant effect prediction on ClinVar", confidence: "low", reason: "." },
      index,
      record: null,
      names: [],
    });
    expect(checked).toMatchObject({ outcome: "refused", reason: "record_not_found" });
  });

  it("refuses a record of a kind that cannot carry a result", () => {
    const checked = run({ record: { id: "clinvar-variant-effect", kind: "dataset" } });
    expect(checked).toMatchObject({ outcome: "refused", reason: "kind_cannot_carry_results" });
  });

  it("refuses a quote the caption does not print", () => {
    const checked = run({ answer: { record_id: "clinvar-variant-effect", quote: "pathogenicity classification", confidence: "low", reason: "." } });
    expect(checked).toMatchObject({ outcome: "refused", reason: "quote_not_in_caption" });
  });

  it("refuses a quote that is in the caption and in the layer twice", () => {
    // "ClinVar" is printed in the lead paragraph, in this caption and in the next one, so no
    // single span is the one the answer means.
    const checked = run({ answer: { record_id: "clinvar-variant-effect", quote: "ClinVar", confidence: "low", reason: "." } });
    expect(checked).toMatchObject({ outcome: "refused", reason: "quote_unresolved" });
    expect((checked as { detail: string }).detail).toContain("quote_ambiguous");
  });

  it("refuses a quote too short to address anything", () => {
    const checked = run({ answer: { record_id: "clinvar-variant-effect", quote: "on", confidence: "low", reason: "." } });
    expect(checked).toMatchObject({ outcome: "refused", reason: "quote_unresolved" });
  });

  it("refuses a high confidence the quote does not justify", () => {
    const checked = run({
      answer: { record_id: "clinvar-variant-effect", quote: "Table 2.", confidence: "high", reason: "." },
    });
    expect(checked).toMatchObject({ outcome: "refused", reason: "confidence_unjustified" });
  });

  it("accepts the same quote at a confidence it does justify", () => {
    expect(run({ answer: { record_id: "clinvar-variant-effect", quote: "Table 2.", confidence: "medium", reason: "." } }).outcome).toBe("labelled");
  });

  it("takes an explicit none as an answer, not a failure", () => {
    const checked = run({ answer: { record_id: NONE, quote: "", confidence: "low", reason: "two records fit and the caption does not separate them" } });
    expect(checked.outcome).toBe("abstained");
  });

  it("refuses to touch a field the deterministic pass decided", () => {
    const { candidates, index } = extract();
    const table = tableAbout(candidates, "Variant effect");
    const checked = checkAnswer({
      table: { ...table, decided: ["clinvar-runtime"] },
      shortlist: shortlistFor(buildShortlistIndex(records, []), table),
      answer: { record_id: "clinvar-variant-effect", quote: "Variant effect prediction on ClinVar", confidence: "high", reason: "." },
      index,
      record: { id: "clinvar-variant-effect", kind: "benchmark" },
      names: ["variant effect prediction on clinvar"],
    });
    expect(checked).toMatchObject({ outcome: "refused", reason: "already_decided" });
  });
});

describe("the answer's shape", () => {
  it("refuses a reply that is not JSON, and one that is the wrong JSON", () => {
    expect(readAnswer("I think it is the ClinVar one.").ok).toBe(false);
    expect(readAnswer(JSON.stringify({ record_id: "x" })).ok).toBe(false);
    expect(readAnswer(JSON.stringify({ record_id: "x", quote: "", confidence: "sure", reason: "." })).ok).toBe(false);
  });

  it("declares the same four fields in zod and in the schema the request sends", () => {
    expect(Object.keys(answerJsonSchema.properties).sort()).toEqual(Object.keys(answerSchema.shape).sort());
    expect([...answerJsonSchema.required].sort()).toEqual(Object.keys(answerSchema.shape).sort());
    expect(answerJsonSchema.additionalProperties).toBe(false);
  });
});

describe("a run", () => {
  const setup = () => {
    const { candidates, index } = extract();
    const tables = tablesOf(candidates);
    const shortlistIndex = buildShortlistIndex(records, []);
    const prompt = loadPrompt();
    const requests: LabelRequest[] = [];
    const answers = new Map<string, string>([
      ["Table 2. Variant effect prediction on ClinVar.", reply({ record_id: "clinvar-variant-effect", quote: "Variant effect prediction on ClinVar" })],
      ["Table 3. Wall clock seconds per thousand variants.", reply({ record_id: NONE, quote: "", confidence: "low", reason: "this table reports timings, not an evaluation" })],
    ]);
    const transport = async (request: LabelRequest): Promise<LabelReply> => {
      requests.push(request);
      const caption = [...answers.keys()].find((key) => request.question.includes(key));
      if (!caption) throw new Error(`the fixture holds no answer for ${request.question.slice(0, 80)}`);
      return { text: answers.get(caption)!, model: request.model, input_tokens: 100, output_tokens: 20 };
    };
    return {
      candidates,
      run: {
        tables,
        shortlistIndex,
        sourceTitle: () => "A fixture paper",
        layerIndex: (sha: string) => (sha === index.layer_sha256 ? index : null),
        transport,
        prompt,
      },
      requests,
    };
  };

  it("labels what it can, abstains where it should, and says so on the receipt", async () => {
    const { run, candidates } = setup();
    const { outcomes, receipt } = await labelTables(run);
    expect(receipt.labelled).toBe(1);
    expect(receipt.abstained).toBe(1);
    expect(receipt.refused).toBe(0);
    expect(receipt.asked).toBe(2);
    expect(receipt.tokens).toEqual({ input: 200, output: 40 });
    expect(receipt.statement).toBe(RECEIPT_STATEMENT);
    expect(receipt.prompt.sha256).toMatch(/^[a-f0-9]{64}$/);
    expect(receipt.shortlist.considered).toBe(3);
    // The receipt totals the run and names the file that holds each table's shortlist, answer
    // and checks, rather than restating them where the two could disagree.
    expect(receipt.per_table).toBe(PER_TABLE_FILE);
    expect(receipt.candidates_labelled).toBe(4);

    const labelled = labelsByCandidate(outcomes);
    const effect = tableAbout(candidates, "Variant effect");
    expect([...labelled.keys()].sort()).toEqual(effect.candidate_ids);
    expect(labelled.get(effect.candidate_ids[0])?.record_id).toBe("clinvar-variant-effect");
  });

  it("asks nothing the second time, and answers the same", async () => {
    const { run, requests } = setup();
    const cache = labelCache();
    const first = await labelTables({ ...run, cache });
    expect(requests).toHaveLength(2);
    const second = await labelTables({ ...run, cache });
    expect(requests).toHaveLength(2);
    expect(second.receipt.asked).toBe(0);
    expect(second.receipt.from_cache).toBe(2);
    // Everything but the field whose job is to say where the answer came from.
    const same = (outcomes: { cached: boolean }[]) => JSON.stringify(outcomes.map(({ cached, ...rest }) => rest));
    expect(same(second.outcomes)).toBe(same(first.outcomes));
    expect(second.outcomes.every((outcome) => outcome.cached)).toBe(true);
    // A rerun spent nothing, so the receipt claims nothing.
    expect(first.receipt.tokens).toEqual({ input: 200, output: 40 });
    expect(second.receipt.tokens).toEqual({ input: 0, output: 0 });
  });

  it("keys the cache on the prompt as well as the place, so an edited prompt is a new question", () => {
    const place = { layer_sha256: "a".repeat(64), extent: { start: 10, end: 90 }, shortlist: ["one"], model: "m" };
    expect(cacheKey({ ...place, prompt_sha256: "b".repeat(64) })).not.toBe(cacheKey({ ...place, prompt_sha256: "c".repeat(64) }));
    expect(cacheKey({ ...place, prompt_sha256: "b".repeat(64) })).toBe(cacheKey({ ...place, prompt_sha256: "b".repeat(64) }));
    expect(cacheKey({ ...place, prompt_sha256: "b".repeat(64), shortlist: ["two"] })).not.toBe(cacheKey({ ...place, prompt_sha256: "b".repeat(64) }));
  });

  it("never asks about a table the document names in under four characters", async () => {
    const { run, requests } = setup();
    const blinded = run.tables.map((table) => ({ ...table, anchor_text: "T2", anchor: { ...table.anchor, caption: "T2" } }));
    const { receipt } = await labelTables({ ...run, tables: blinded });
    expect(requests).toHaveLength(0);
    expect(receipt.refusals_by_reason).toEqual({ no_anchor_text: 2 });
    expect(ANCHOR_MINIMUM).toBe(4);
  });

  it("records a transport failure as a refusal rather than throwing", async () => {
    const { run } = setup();
    const { receipt, outcomes } = await labelTables({
      ...run,
      transport: async () => {
        throw new Error("the service is unreachable");
      },
    });
    expect(receipt.refusals_by_reason).toEqual({ transport_failed: 2 });
    expect(outcomes.every((outcome) => outcome.record_id === null)).toBe(true);
  });

  it("refuses a reply that is not an answer", async () => {
    const { run } = setup();
    const { receipt } = await labelTables({ ...run, transport: async (request) => ({ text: "probably table 2", model: request.model, input_tokens: null, output_tokens: null }) });
    expect(receipt.refusals_by_reason).toEqual({ answer_malformed: 2 });
  });
});

describe("the transport", () => {
  const request: LabelRequest = { model: "m", effort: "low", max_tokens: 10, system: "s", question: "q", schema: {} };

  it("answers from a recording keyed on the whole request", async () => {
    const transport = recordedTransport({ [requestDigest(request)]: reply({ record_id: NONE, quote: "" }) });
    expect((await transport(request)).text).toContain(NONE);
    await expect(transport({ ...request, question: "a different question" })).rejects.toThrow(/No recorded reply/);
  });

  it("fails by name when the key is absent, at the call and not at the import", async () => {
    const transport = liveTransport({ env: {} });
    await expect(transport(request)).rejects.toThrow(new RegExp(KEY_VARIABLE));
  });

  it("sends the schema and the effort, and no sampling control the current API rejects", async () => {
    const sent: Record<string, unknown>[] = [];
    const client = {
      messages: {
        create: async (body: Record<string, unknown>) => {
          sent.push(body);
          return { content: [{ type: "text", text: reply({ record_id: NONE, quote: "" }) }], model: "m", usage: { input_tokens: 3, output_tokens: 4 } };
        },
      },
    };
    const answer = await liveTransport({ client })(request);
    expect(answer).toMatchObject({ model: "m", input_tokens: 3, output_tokens: 4 });
    expect(sent[0].output_config).toEqual({ effort: "low", format: { type: "json_schema", schema: {} } });
    expect(sent[0]).not.toHaveProperty("temperature");
  });
});
