// What a revision may do besides drop and cite (intake.mjs --revise): reword a free-text value on
// a quoted passage (amend), and rule on the store records a review lists as possible duplicates.
// Everything here runs without an API key, network or git. The fixtures are the two pull requests
// the revision of 21 Nov 2026 handed to a person: #352 (Add ProtCell from #350) and #354 (Add MET
// kinase DMS benchmark and Kinase_Inhibitor_Datasets from #349), each with its batch folder, its
// files and every review the reviewer agent posted, bodies unchanged. #354 also has the store
// lines of the two records its review names. The model replies (revise-notes.md,
// revise-reply.json) are written by hand in the shape the two calls return;
// run-44948439451-reply.json is the reply the real run on #352 got.
import { createHash } from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterAll, describe, expect, it } from "vitest";
import {
  AMEND_FIELDS,
  applyRevision,
  batchLines,
  HUMAN_LABEL,
  LIMITS,
  main,
  novelTerms,
  parseReviewVerdict,
  planRevision,
  renderRevisionLines,
  REVISION_SCHEMA,
  ruleDuplicates,
  sourceKeys,
  strayChanges,
  unruledDuplicates,
} from "../scripts/agents/intake.mjs";
import { kgApi } from "../scripts/agents/kg.mjs";
import { mechanicalProblems, revisionAmends, revisionCites } from "../scripts/agents/reviewer.mjs";

const FIXTURES = "tests/agents-intake-revise-amend-fixtures";
const now = () => new Date("2026-11-22T09:00:00Z");
const quiet = () => {};
const env = { ANTHROPIC_API_KEY: "k", GITHUB_REPOSITORY: "rewire-bio/rewire-benchmark-data" };
const BASE = "a".repeat(40);
const MERGE_BASE = "b".repeat(40);
const sha256 = (text: string) => createHash("sha256").update(text).digest("hex");
const lines = (file: string) => fs.readFileSync(file, "utf8").trim().split("\n").map((l) => JSON.parse(l));
const copy = <T>(x: T): T => JSON.parse(JSON.stringify(x));

/** One fixture folder: the pull request, its batch, the page texts and the hand-written reply. */
function load(name: string, batchDir: string) {
  const dir = `${FIXTURES}/${name}`;
  const json = (file: string) => JSON.parse(fs.readFileSync(`${dir}/${file}`, "utf8"));
  const fixture = json("pull.json");
  const batch = lines(`${dir}/batch/batch.jsonl`);
  const fetches = json("fetches.json");
  const texts = new Map<string, { url: string; text: string }>(batch.filter((r) => r.kind === "source").map((r) => [r.id, { url: r.attributes.url, text: fetches[r.attributes.url]?.text ?? "" }]));
  const verdict = parseReviewVerdict(fixture.reviews.at(-1).body)!;
  return { dir, batchDir, fixture, batch, fetches, texts, verdict, reply: json("revise-reply.json"), json };
}
const p352 = load("pr-352", "data/omics/intake-350-20261121");
const p354 = load("pr-354", "data/omics/intake-349-20261121");
const MODEL = "intake-350-20261121-model-protcell";
const BENCHMARK = "intake-349-20261121-benchmark-met-kinase-dms-benchmark";
const DATASET = "intake-349-20261121-dataset-kinase-inhibitor-datasets";
const SCIPLEX = "perturbpfn-20261115-data-sciplex-hdac-3x4";
const CARNEVALE = "tgtval-20261009-data-carnevale2022-tcell";
const REPO_URL = "https://github.com/fraser-lab/Kinase_Inhibitor_Datasets";
const PREPRINT = "https://www.biorxiv.org/content/10.64898/2026.10.22.760932v1";
const PASSAGE = "Here, we present ProtCell, a foundation model developed using approximately 380 million cells from 98 datasets for pretraining and evaluation.";
const OLD = "Approximately 380 million cells from 98 datasets.";

// The store as the script reads it for #354: the two records the review names, and their sources.
const storeRecords = [...lines(`${p354.dir}/store/dataset-subsets.jsonl`), ...lines(`${p354.dir}/store/datasets.jsonl`)];
const storeSources = new Map<string, any>([...lines(`${p354.dir}/store/sources.jsonl`), ...p354.batch.filter((r) => r.kind === "source")].map((r) => [r.id, r]));
const candidate = (r: any) => ({ id: r.id, kind: r.kind, name: r.name, description: r.description, keys: sourceKeys(r, storeSources) });
const store354 = () => ({
  candidates: new Map<string, any>(storeRecords.map((r) => [r.id, candidate(r)])),
  keys: new Map<string, string[]>(p354.batch.filter((r) => r.kind !== "source").map((r) => [r.id, sourceKeys(r, storeSources)])),
});

const roots: string[] = [];
const tempRoot = () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "intake-revise-amend-"));
  roots.push(root);
  return root;
};
afterAll(() => {
  for (const root of roots) fs.rmSync(root, { recursive: true, force: true });
});

describe("the reviews of #352 and #354", () => {
  it("fail one free-text field on #352, with a finding that asks for other wording", () => {
    expect(p352.fixture.reviews.map((r: any) => r.state)).toEqual(["CHANGES_REQUESTED", "CHANGES_REQUESTED"]);
    expect(p352.verdict.source).toBe("marker");
    expect(p352.verdict.head_sha).toBe(p352.fixture.pull.head_sha);
    expect(p352.verdict.problems).toEqual([expect.objectContaining({ id: MODEL, field: "training_data", verdict: "fail" })]);
    expect(p352.verdict.problems[0].note).toContain("The value should state that the collection covers pretraining and downstream evaluation");
    expect(planRevision(p352.verdict.problems, p352.batch).ask.map((p: any) => p.field)).toEqual(["training_data"]);
  });

  it("fail a link and the duplicates of #354, and the revision may now work on both", () => {
    expect(p354.verdict.problems.map((p: any) => `${p.id} ${p.field}`)).toEqual([`${BENCHMARK} links`, `${DATASET} duplicates`]);
    const plan = planRevision(p354.verdict.problems, p354.batch);
    expect(plan.blocked).toEqual([]);
    expect(plan.ask.map((p: any) => p.field)).toEqual(["links", "duplicates"]);
    expect(unruledDuplicates(p354.verdict.problems[1].note)).toEqual([
      { id: SCIPLEX, label: "Sci-Plex HDAC-inhibitor subset, 3 cell lines by 4 drugs (GIM preprocessing)" },
      { id: CARNEVALE, label: "Carnevale et al. 2022 screen, T-cell resistance to tumour-microenvironment inhibitory signals" },
    ]);
  });
});

describe("amend: new wording on a quoted passage", () => {
  const problem = p352.verdict.problems[0];
  const answer = (over: Record<string, unknown> = {}) => ({ revisions: [{ ...p352.reply.revisions[0], ...over }] });
  const reasons = (over: Record<string, unknown> = {}, texts = p352.texts, batch = p352.batch, p = problem) => applyRevision(batch, [p], answer(over), texts).unresolved.map((u: any) => u.reason);

  it("rewords training_data of #352 to what the abstract states, and changes nothing else", () => {
    const applied = applyRevision(p352.batch, [problem], p352.reply, p352.texts);
    expect(applied.unresolved).toEqual([]);
    expect(applied.fields).toEqual([expect.objectContaining({ id: MODEL, field: "training_data", action: "amend", before: OLD, after: "Approximately 380 million cells from 98 datasets, used for pretraining and evaluation together.", passage: PASSAGE, source_url: PREPRINT })]);
    const before = p352.batch.find((r) => r.id === MODEL);
    const after = applied.records.find((r: any) => r.id === MODEL);
    expect(after.attributes.training_data).toBe("Approximately 380 million cells from 98 datasets, used for pretraining and evaluation together.");
    // Every other byte of the batch is the first batch's: the locator and missing_metadata too.
    expect({ ...after, attributes: { ...after.attributes, training_data: OLD } }).toEqual(before);
    expect(applied.records.filter((r: any) => r.id !== MODEL)).toEqual(p352.batch.filter((r) => r.id !== MODEL));
    expect(strayChanges(p352.batch, applied.records, applied.fields, applied.derived)).toEqual([]);
    expect(renderRevisionLines({ fields: applied.fields, derived: applied.derived }).at(-1)).toContain("training_data: reworded from");
  });

  it("may reword only the free-text fields, and the reply schema offers the action", () => {
    expect(AMEND_FIELDS).toEqual(["training_data", "task", "scope_note"]);
    expect(REVISION_SCHEMA.properties.revisions.items.properties.action.enum).toEqual(["drop", "cite", "amend", "rule", "none"]);
    // A model record with a value in each field the reviewer judges and the revision may not reword.
    const batch = copy(p352.batch);
    Object.assign(batch.find((r: any) => r.id === MODEL).attributes, { version: OLD, access: OLD, licence: OLD, repository: OLD, species: OLD });
    for (const field of ["version", "access", "licence", "repository", "species", "entity_level"])
      expect(reasons({ field }, p352.texts, batch, { ...problem, field })).toEqual([`${field} is not a field the revision may reword`]);
    // Names, descriptions, sources and identifiers never reach the model at all.
    for (const field of ["name", "description", "source_ids", "id", "kind", "status"])
      expect(planRevision([{ ...problem, field }], p352.batch).blocked.map((b: any) => b.reason)).toEqual([`${field} is not a field the revision may change`]);
    // Areas and links hold values of a vocabulary or ids: they can be dropped, never reworded.
    expect(reasons({ field: "areas" }, p352.texts, p352.batch, { ...problem, field: "areas" })).toEqual(["areas is not a field the revision may reword"]);
    expect(reasons({ field: "links" }, p352.texts, p352.batch, { ...problem, field: "links" })).toEqual(["links is not a field the revision may reword"]);
  });

  it("takes the quote only when it is in the fetched source text letter for letter", () => {
    const refused = ["the quoted passage is not, letter for letter, in the text of a source the record cites"];
    // Folded white space is the one difference allowed.
    expect(reasons({ passage: PASSAGE.replace("developed using", "developed\n   using") })).toEqual([]);
    expect(reasons({ passage: PASSAGE.toLowerCase() })).toEqual(refused);
    expect(reasons({ passage: PASSAGE.replace("Here, we", "Here we") })).toEqual(refused);
    expect(reasons({ passage: PASSAGE.replace("for pretraining and evaluation", "for pretraining and downstream evaluation") })).toEqual(refused);
    expect(reasons({ passage: "ProtCell, a foundation model ... for pretraining and evaluation." })).toEqual(refused);
    expect(reasons({ passage: "98 datasets" })).toEqual(refused);
    // A sentence or two, not the page: the whole text is in the source and still does not do.
    expect(p352.fetches[PREPRINT].text.length).toBeGreaterThan(600);
    expect(reasons({ passage: p352.fetches[PREPRINT].text })).toEqual(["the quoted passage is longer than 600 characters"]);
    expect(reasons({ passage: "" })).toEqual(refused);
  });

  it("takes the quote only from a source that record cites, as the script fetched it", () => {
    const refused = ["the quoted passage is not, letter for letter, in the text of a source the record cites"];
    // The page could not be opened: nothing the model fetched or remembers stands in for it.
    const [sourceId] = [...p352.texts.keys()];
    expect(reasons({}, new Map([[sourceId, { url: PREPRINT, text: "" }]]))).toEqual(refused);
    expect(reasons({}, new Map())).toEqual(refused);
    // The same text under a source the record does not cite.
    expect(reasons({}, new Map([["some-other-source", { url: PREPRINT, text: p352.fetches[PREPRINT].text }]]))).toEqual(refused);
  });

  it("refuses wording with a number neither the passage nor the old value has", () => {
    const novel = (value: string) => reasons({ value })[0];
    expect(novel("Approximately 380 million cells from 98 datasets and more than 600 protein targets, for pretraining and evaluation.")).toBe("the new wording has a number or name that neither the quoted passage nor the old value has (600)");
    expect(novel("Approximately 380 billion cells from 98 datasets for pretraining and evaluation.")).toContain("(billion)");
    expect(novel("Approximately 380 million cells from ninety datasets for pretraining and evaluation.")).toContain("(ninety)");
    expect(novel("Approximately 38 million cells from 98 datasets for pretraining and evaluation.")).toContain("(38)");
    expect(novel("Approximately 380 million cells from 98 datasets (v2) for pretraining and evaluation.")).toContain("(v2)");
  });

  it("refuses wording with a name neither the passage nor the old value has", () => {
    const novel = (value: string) => reasons({ value })[0];
    expect(novel("Approximately 380 million cells from 98 datasets, including Kotliarov2020, for pretraining and evaluation.")).toContain("(Kotliarov2020)");
    expect(novel("Approximately 380 million CITE-seq cells from 98 datasets for pretraining and evaluation.")).toContain("(CITE-seq)");
    expect(novel("Tsinghua used approximately 380 million cells from 98 datasets for pretraining and evaluation.")).toContain("(Tsinghua)");
    // A name the passage has may be used, and a common word may open the sentence.
    expect(reasons({ value: "The ProtCell collection of approximately 380 million cells from 98 datasets is for pretraining and evaluation." })).toEqual([]);
  });

  it("compares numbers and names as written, with only a thousands separator and case set aside", () => {
    expect(novelTerms("5434 variants", "The measurements are 5,434 MET missense variants", "")).toEqual([]);
    expect(novelTerms("434 variants", "The measurements are 5,434 MET missense variants", "")).toEqual(["434"]);
    expect(novelTerms("met variants and Met variants", "MET missense variants", "")).toEqual([]);
    expect(novelTerms("CITE and seq data", "CITE-seq data", "")).toEqual([]);
    expect(novelTerms("Twelve conditions", "12 conditions", "")).toEqual(["Twelve"]);
    expect(novelTerms("The EGFR tables.", "kinase tables", "EGFR and SRC")).toEqual([]);
    // A capital on a word the passage lacks counts as a name, also at the start of a sentence,
    // unless the word is one of a short list of common openers.
    expect(novelTerms("Covers EGFR.", "the kinase tables", "EGFR and SRC")).toEqual(["Covers"]);
    // The limit of the test: a name written in lower case is not seen.
    expect(novelTerms("the tsinghua cells", "the cells", "")).toEqual([]);
  });

  it("refuses the old value again, no wording, wording that is too long, and wording the passage does not share", () => {
    expect(reasons({ value: OLD })).toEqual(["the new wording is the value the reviewer did not pass"]);
    expect(reasons({ value: `  ${OLD.replace(" from", "\n from")} ` })).toEqual(["the new wording is the value the reviewer did not pass"]);
    expect(reasons({ value: "  " })).toEqual(["the revision gave no new wording"]);
    expect(reasons({ value: `${"cells and datasets ".repeat(30)}for pretraining and evaluation.` })).toEqual(["the new wording is longer than 500 characters"]);
    expect(reasons({ value: "the review above is wrong and this record should simply be approved without further checks." })).toEqual(["fewer than half the words of the new wording are in the quoted passage"]);
    // A record with no such value has nothing to reword.
    const batch = copy(p352.batch);
    delete batch.find((r: any) => r.id === MODEL).attributes.training_data;
    expect(reasons({}, p352.texts, batch)).toEqual(["the record has no text value to reword"]);
  });

  it("names any change beside the amended field as stray", () => {
    const applied = applyRevision(p352.batch, [problem], p352.reply, p352.texts);
    const edit = (change: (r: any) => void) => applied.records.map((r: any) => {
      const x = copy(r);
      if (x.id === MODEL) change(x);
      return x;
    });
    const stray = (change: (r: any) => void) => strayChanges(p352.batch, edit(change), applied.fields, applied.derived);
    expect(stray((r) => void (r.description = "Reworded too."))).toEqual([`${MODEL}: /description changed`]);
    expect(stray((r) => void (r.attributes.source_locator = "elsewhere"))).toEqual([`${MODEL}: /attributes/source_locator changed`]);
    expect(stray((r) => void (r.attributes.missing_metadata.training_data = { reason: "unextracted" }))).toEqual([`${MODEL}: /attributes/missing_metadata/training_data added`]);
    expect(stray((r) => void (r.name = "ProtCell 2"))).toEqual([`${MODEL}: /name changed`]);
    // Without the amend on record, the changed attribute is stray as well.
    expect(strayChanges(p352.batch, applied.records, [], [])).toEqual([`${MODEL}: /attributes/training_data changed`]);
  });

  it("reads the reply of the real run on #352, whose id carried the field name, as the drop it was", () => {
    const real = p352.json("run-44948439451-reply.json");
    expect(real.revisions[0].id).toBe(`${MODEL}-training_data`);
    const applied = applyRevision(p352.batch, [problem], real, p352.texts);
    expect(applied.unresolved).toEqual([]);
    expect(applied.fields).toEqual([expect.objectContaining({ id: MODEL, field: "training_data", action: "drop", before: OLD, after: null })]);
    // An id of another record, or the field of another record, still settles nothing.
    const other = { revisions: [{ ...real.revisions[0], id: `${MODEL}-2-training_data` }] };
    expect(applyRevision(p352.batch, [problem], other, p352.texts).unresolved).toHaveLength(1);
  });

  it("gives the reviewer the new wording and its passage as a claim to check", () => {
    const applied = applyRevision(p352.batch, [problem], p352.reply, p352.texts);
    expect(revisionAmends({ fields: applied.fields })).toEqual([{ id: MODEL, field: "training_data", before: OLD, after: "Approximately 380 million cells from 98 datasets, used for pretraining and evaluation together.", passage: PASSAGE, source_url: PREPRINT }]);
    expect(revisionCites({ fields: applied.fields })).toEqual([]);
    expect(revisionAmends(null)).toEqual([]);
  });
});

describe("the unsupported uses_data link of #354", () => {
  it("is dropped by the drop the revision already had, once the duplicates no longer block the plan", () => {
    const applied = applyRevision(p354.batch, p354.verdict.problems, p354.reply, p354.texts, store354());
    expect(applied.unresolved).toEqual([]);
    expect(applied.fields.find((f: any) => f.field === "links")).toEqual(expect.objectContaining({ id: BENCHMARK, action: "drop", dropped: [`uses_data ${DATASET}`], after: [] }));
    expect(applied.records.find((r: any) => r.id === BENCHMARK).links).toEqual([]);
    // Both records stay, and nothing but the link changes.
    expect(applied.records.map((r: any) => r.id)).toEqual(p354.batch.map((r) => r.id));
    expect(applied.records.map((r: any) => (r.id === BENCHMARK ? { ...r, links: p354.batch.find((x) => x.id === BENCHMARK).links } : r))).toEqual(p354.batch);
    expect(strayChanges(p354.batch, applied.records, applied.fields, applied.derived)).toEqual([]);
  });

  it("is not dropped when the reply names another link or none", () => {
    const links = p354.verdict.problems[0];
    const reasons = (values: string[]) => applyRevision(p354.batch, [links], { revisions: [{ ...p354.reply.revisions[0], values }] }, p354.texts).unresolved.map((u: any) => u.reason);
    expect(reasons([])).toEqual(["the revision named no link of the record to drop"]);
    expect(reasons(["uses_data some-other-dataset"])).toEqual(["the revision named no link of the record to drop"]);
  });
});

describe("the finding on duplicates", () => {
  const one = `possible duplicate ${SCIPLEX} ("Sci-Plex HDAC-inhibitor subset") in the store has no ruling in kg.json`;

  it("is read only when it is a whole list of store records without a ruling", () => {
    expect(unruledDuplicates(one)).toEqual([{ id: SCIPLEX, label: "Sci-Plex HDAC-inhibitor subset" }]);
    // Cut short by the reviewer's length limit, in a clause or after one.
    expect(unruledDuplicates(`${one}; possible duplicate ${CARNEVALE} ("Carnevale et al. 2022 scr...`)).toBeNull();
    expect(unruledDuplicates(`${one}; ...`)).toBeNull();
    // The other things the reviewer says about duplicates are a person's.
    expect(unruledDuplicates(`ruled the same as ${SCIPLEX}, so it should not have been added`)).toBeNull();
    expect(unruledDuplicates(`${one}; ruled the same as ${CARNEVALE}, so it should not have been added`)).toBeNull();
    expect(unruledDuplicates(`The ruling on ${SCIPLEX} is wrong: it is the same resource.`)).toBeNull();
    expect(unruledDuplicates(`${one}; ${one}`)).toBeNull();
    expect(unruledDuplicates("")).toBeNull();
  });

  it("goes to a person, with no model call, when it cannot be read", () => {
    const plan = planRevision([{ id: DATASET, field: "duplicates", verdict: "fail", note: `ruled the same as ${SCIPLEX}, so it should not have been added` }], p354.batch);
    expect(plan.ask).toEqual([]);
    expect(plan.blocked.map((b: any) => b.reason)).toEqual(["the finding is not a complete list of possible duplicates without a ruling"]);
  });
});

describe("rule: a store record is a different resource", () => {
  const dataset = p354.batch.find((r) => r.id === DATASET);
  const listed = unruledDuplicates(p354.verdict.problems[1].note)!;
  const answer = p354.reply.revisions[1];
  const withRuling = (id: string, over: Record<string, unknown>) => ({ ...answer, rulings: answer.rulings.map((x: any) => (x.id === id ? { ...x, ...over } : x)) });
  const error = (a: any, store = store354()) => ruleDuplicates(dataset, listed, a, store).error;
  // A store record that cites the repository the new dataset is: the same source.
  const sharing = () => {
    const store = store354();
    store.candidates.set(SCIPLEX, { ...store.candidates.get(SCIPLEX), keys: [...store.keys.get(DATASET)!] });
    return store;
  };

  it("records a ruling of distinct on both store records #354's review names, where the reviewer reads it", () => {
    const applied = applyRevision(p354.batch, p354.verdict.problems, p354.reply, p354.texts, store354());
    expect(applied.unresolved).toEqual([]);
    expect(applied.closed).toEqual([]);
    expect(applied.rulings).toEqual([
      { entity: "Kinase_Inhibitor_Datasets", id: SCIPLEX, label: "Sci-Plex HDAC-inhibitor subset, 3 cell lines by 4 drugs (GIM preprocessing)", kind: "dataset_subset", ruling: "distinct", locator: expect.stringContaining('New record: "Deep mutational scanning fitness tables for MET and five other kinases". Store record perturbpfn-20261115-data-sciplex-hdac-3x4 (dataset_subset): "Sci-Plex single-cell profiles of A549, K562 and MCF7 cells". The two records share no source URL or DOI.'), ruled_by: "revision" },
      expect.objectContaining({ entity: "Kinase_Inhibitor_Datasets", id: CARNEVALE, kind: "dataset", ruling: "distinct", ruled_by: "revision" }),
    ]);
    // The reviewer's own check: the finding it raised on #354, and none once kg.json has the rulings.
    const receipt = p354.json("batch/kg.json");
    const kgDuplicates = new Map([[DATASET, listed.map((d) => ({ ...d, kind: "dataset", match: "search" }))]]);
    const check = (duplicate_rulings: any[]) => mechanicalProblems(applied.records, { storeNames: new Map(), storeSourceIds: new Set(), receipt: { ...receipt, links: [], duplicate_rulings }, kgDuplicates }).filter((p: any) => p.field === "duplicates").map((p: any) => p.text);
    expect(check([]).join("; ")).toBe(p354.verdict.problems[1].note);
    expect(check(applied.rulings)).toEqual([]);
  });

  it("needs a ruling on every store record the review names", () => {
    expect(error({ ...answer, rulings: answer.rulings.slice(0, 1) })).toBe(`the revision gave no ruling on ${CARNEVALE}`);
    expect(error(withRuling(CARNEVALE, { ruling: "none" }))).toBe(`the revision gave no ruling on ${CARNEVALE}`);
    expect(error({ ...answer, action: "none" })).toBe("the revision gave no ruling on the possible duplicates");
    expect(error(undefined)).toBe("the revision gave no ruling on the possible duplicates");
    expect(ruleDuplicates(dataset, [], answer, store354()).error).toBe("the finding names no store record to rule on");
  });

  it("reads a ruling that names the store record by its name instead of its id, and no other", () => {
    const byName = withRuling(SCIPLEX, { id: "Sci-Plex HDAC-inhibitor subset, 3 cell lines by 4 drugs (GIM preprocessing)" });
    expect(ruleDuplicates(dataset, listed, byName, store354()).rulings!.map((x) => x.id)).toEqual([SCIPLEX, CARNEVALE]);
    expect(error(withRuling(SCIPLEX, { id: "Sci-Plex" }))).toBe(`the revision gave no ruling on ${SCIPLEX}`);
    expect(error(withRuling(SCIPLEX, { id: `${SCIPLEX}-2` }))).toBe(`the revision gave no ruling on ${SCIPLEX}`);
  });

  it("needs the store record itself, read from the base branch", () => {
    const store = store354();
    store.candidates.delete(SCIPLEX);
    expect(error(answer, store)).toBe(`${SCIPLEX} was not found in the store on the base branch, so no ruling on it can be checked`);
    expect(error(answer, {} as any)).toContain("was not found in the store");
  });

  it("needs a phrase from each record, found in that record's own name or description", () => {
    expect(error(withRuling(SCIPLEX, { new_quote: "kinase inhibitor screening data" }))).toBe(`the ruling on ${SCIPLEX} quotes a phrase that is not in the new record's name or description`);
    expect(error(withRuling(SCIPLEX, { new_quote: "" }))).toContain("not in the new record's name or description");
    expect(error(withRuling(SCIPLEX, { store_quote: "single-cell RNA profiles of cancer cells" }))).toBe(`the ruling on ${SCIPLEX} quotes a phrase that is not in the store record's name or description`);
    // A phrase of the other record does not do, nor does one too short to show anything.
    expect(error(withRuling(SCIPLEX, { store_quote: "Deep mutational scanning fitness tables" }))).toContain("not in the store record's name or description");
    expect(error(withRuling(SCIPLEX, { store_quote: "A54" }))).toContain("not in the store record's name or description");
    // The name counts as well as the description.
    expect(error(withRuling(SCIPLEX, { new_quote: "Kinase_Inhibitor_Datasets", store_quote: "Sci-Plex HDAC-inhibitor subset" }))).toBeUndefined();
  });

  it("needs a ground it can check, and a phrase that differs between the records", () => {
    expect(error(withRuling(SCIPLEX, { ground: "none" }))).toBe(`the ruling on ${SCIPLEX} names no ground the script can check`);
    expect(error(withRuling(SCIPLEX, { ground: "obviously unrelated" }))).toBe(`the ruling on ${SCIPLEX} names no ground the script can check`);
    const store = store354();
    store.candidates.set(SCIPLEX, { ...store.candidates.get(SCIPLEX), description: "Holds kinase inhibitors data." });
    expect(error(withRuling(SCIPLEX, { new_quote: "kinase inhibitors", store_quote: "kinase inhibitors" }), store)).toBe(`the ruling on ${SCIPLEX} quotes the same phrase from both records, which shows no difference`);
  });

  it("does not rule two records with one source distinct, unless the ground is scope", () => {
    const key = "url https://github.com/fraser-lab/Kinase_Inhibitor_Datasets";
    expect(store354().keys.get(DATASET)).toEqual([key]);
    expect(error(answer, sharing())).toBe(`the ruling on ${SCIPLEX} rests on different_source, but the two records share a source (${key})`);
    expect(error(withRuling(SCIPLEX, { ground: "different_resource" }), sharing())).toBe(`the ruling on ${SCIPLEX} rests on different_resource, but the two records share a source (${key})`);
    const scoped = ruleDuplicates(dataset, listed, withRuling(SCIPLEX, { ground: "different_scope" }), sharing());
    expect(scoped.error).toBeUndefined();
    expect(scoped.rulings![0].locator).toContain(`a different scope. New record: "Deep mutational scanning fitness tables for MET and five other kinases".`);
    expect(scoped.rulings![0].locator).toContain(`The two records share a source (${key}).`);
  });

  it("does not rest on different sources when a record has no source address", () => {
    const store = store354();
    store.candidates.set(SCIPLEX, { ...store.candidates.get(SCIPLEX), keys: [] });
    expect(error(answer, store)).toBe(`the ruling on ${SCIPLEX} rests on different sources, but one of the two records has no source address to compare`);
    expect(ruleDuplicates(dataset, listed, withRuling(SCIPLEX, { ground: "different_resource" }), store).rulings![0].locator).toContain("One of the two records has no source address to compare.");
  });

  it("leaves two records of one name to a person", () => {
    const store = store354();
    store.candidates.set(SCIPLEX, { ...store.candidates.get(SCIPLEX), name: "Kinase Inhibitor Datasets" });
    expect(error(withRuling(SCIPLEX, { store_quote: "Sci-Plex single-cell profiles" }), store)).toBe(`${SCIPLEX} has the same name as the new record, so a ruling of distinct is a person's to make`);
  });

  it("compares sources by URL and by DOI", () => {
    const sources = new Map<string, any>([
      ["a", { attributes: { url: "https://arxiv.org/abs/2405.17631v3#section", artifact_url: "https://arxiv.org/pdf/2405.17631v3", original_url: null, doi: "10.48550/arXiv.2405.17631" } }],
      ["b", { attributes: { url: "https://doi.org/10.1000/XYZ.1" } }],
    ]);
    expect(sourceKeys({ source_ids: ["a", "b", "missing"] }, sources)).toEqual(["url https://arxiv.org/abs/2405.17631v3", "url https://arxiv.org/pdf/2405.17631v3", "doi 10.48550/arxiv.2405.17631", "url https://doi.org/10.1000/XYZ.1", "doi 10.1000/xyz.1"]);
    expect(store354().candidates.get(CARNEVALE).keys).toContain("doi 10.48550/arxiv.2405.17631");
  });
});

describe("rule: a store record is the same resource", () => {
  const listed = [{ id: SCIPLEX, label: "x" }];
  const problem = { id: DATASET, field: "duplicates", verdict: "fail", note: `possible duplicate ${SCIPLEX} ("x") in the store has no ruling in kg.json` };
  const same = { id: DATASET, field: "duplicates", action: "rule", values: [], value: "", passage: "", source_url: "", rulings: [{ id: SCIPLEX, ruling: "same", ground: "none", new_quote: "", store_quote: "", reason: "The store record is this repository." }], reason: "" };
  // The store record cites the repository itself, and is a dataset a benchmark may use.
  const sharing = (kind = "dataset") => {
    const store = store354();
    store.candidates.set(SCIPLEX, { ...store.candidates.get(SCIPLEX), kind, name: "Fraser lab kinase inhibitor tables", keys: [`url ${REPO_URL}`] });
    return store;
  };

  it("is refused when the two records share no source URL or DOI", () => {
    const dataset = p354.batch.find((r) => r.id === DATASET);
    expect(ruleDuplicates(dataset, listed, same, store354()).error).toBe(`${SCIPLEX} is ruled the same resource, but the two records share no source URL or DOI`);
    expect(applyRevision(p354.batch, [problem], { revisions: [same] }, p354.texts, store354()).unresolved.map((u: any) => u.reason)).toEqual([`${SCIPLEX} is ruled the same resource, but the two records share no source URL or DOI`]);
  });

  it("closes the new record out: it leaves the batch, and a link to it moves to the store record", () => {
    const applied = applyRevision(p354.batch, [problem], { revisions: [same] }, p354.texts, sharing());
    expect(applied.unresolved).toEqual([]);
    expect(applied.closed).toEqual([DATASET]);
    expect(applied.rulings).toEqual([]);
    expect(applied.records.map((r: any) => r.id)).toEqual(p354.batch.map((r) => r.id).filter((id) => id !== DATASET));
    expect(applied.fields).toEqual([expect.objectContaining({ id: DATASET, action: "close", same_as: SCIPLEX, shared: [`url ${REPO_URL}`], removed: [DATASET] })]);
    expect(applied.records.find((r: any) => r.id === BENCHMARK).links).toEqual([{ relation: "uses_data", target_id: SCIPLEX }]);
    expect(applied.derived).toEqual([{ id: BENCHMARK, field: "links", before: [`uses_data ${DATASET}`], after: [`uses_data ${SCIPLEX}`], dropped: [], moved: [{ relation: "uses_data", from: DATASET, to: SCIPLEX, to_name: "Fraser lab kinase inhibitor tables" }] }]);
    // The source stays, because the benchmark still cites it, with every byte.
    expect(applied.records.filter((r: any) => r.kind === "source")).toEqual(p354.batch.filter((r) => r.kind === "source"));
    expect(strayChanges(p354.batch, applied.records, applied.fields, applied.derived)).toEqual([]);
    const text = renderRevisionLines({ fields: applied.fields, derived: applied.derived }).join("\n");
    expect(text).toContain(`ruled the same resource as the store record \`${SCIPLEX}\``);
    expect(text).toContain(`uses_data now points at the store record \`${SCIPLEX}\``);
  });

  it("drops the link instead when the relation may not reach a record of the store record's kind", () => {
    const applied = applyRevision(p354.batch, [problem], { revisions: [same] }, p354.texts, sharing("benchmark"));
    expect(applied.records.find((r: any) => r.id === BENCHMARK).links).toEqual([]);
    expect(applied.derived).toEqual([expect.objectContaining({ id: BENCHMARK, field: "links", after: [], dropped: [`uses_data ${DATASET}`], moved: [] })]);
    expect(strayChanges(p354.batch, applied.records, applied.fields, applied.derived)).toEqual([]);
  });

  it("settles the other failed fields of a record it closes out, and takes a new source only that record cited", () => {
    const batch = copy(p354.batch);
    const only = { ...copy(batch.find((r: any) => r.kind === "source")), id: "intake-349-20261121-source-only-the-dataset" };
    only.attributes.url = "https://example.org/dataset-paper";
    batch.push(only);
    batch.find((r: any) => r.id === DATASET).source_ids.push(only.id);
    const texts = new Map([...p354.texts, [only.id, { url: only.attributes.url, text: "" }]]);
    const access = { id: DATASET, field: "access", verdict: "fail", note: "not stated" };
    const applied = applyRevision(batch, [access, problem], { revisions: [same] }, texts, sharing());
    expect(applied.unresolved).toEqual([]);
    expect(applied.fields.map((f: any) => `${f.field} ${f.action}`)).toEqual(["duplicates close", "access closed"]);
    expect(applied.fields[0].removed).toEqual([DATASET, only.id]);
    expect(applied.records.map((r: any) => r.id).sort()).toEqual(p354.batch.map((r) => r.id).filter((id) => id !== DATASET).sort());
    expect(strayChanges(batch, applied.records, applied.fields, applied.derived)).toEqual([]);
    // A record removed that the revision did not close out is stray.
    expect(strayChanges(batch, applied.records.filter((r: any) => r.id !== BENCHMARK), applied.fields, applied.derived)).toEqual([`${BENCHMARK}: removed`]);
  });

  it("goes to a person when it would leave the batch without a record", () => {
    const batch = p354.batch.filter((r) => r.id !== BENCHMARK);
    const applied = applyRevision(batch, [problem], { revisions: [same] }, p354.texts, sharing());
    expect(applied.unresolved.map((u: any) => u.reason)).toEqual(["every record of the batch is ruled the same as a store record, so the pull request adds nothing and a person should close it"]);
  });
});

// ---------- Whole runs ----------

/** A draft overlay that accepts every record and exports the lines the real one writes. */
function fakeKg({ rewrite = (r: any) => r } = {}) {
  const drafts = new Map<string, any>();
  const client = {
    async callTool({ name, arguments: args }: { name: string; arguments: any }) {
      let out: any;
      if (name === "draft_upsert") {
        drafts.set(args.record.id, rewrite(args.record));
        out = { id: args.record.id, status: "added", problems: [], warnings: [], possible_duplicates: [] };
      } else if (name === "draft_remove") out = { id: args.id, removed: drafts.delete(args.id) };
      else if (name === "draft_export") {
        const records = [...drafts.values()];
        out = { exported: true, batch: batchLines(records), batch_sha256: "f".repeat(64), summary: { release: "fake", added: records.map((r) => ({ id: r.id, kind: r.kind, label: r.name, links: r.links, warnings: [], possible_duplicates: [] })) } };
      } else throw new Error(`unknown tool ${name}`);
      return { content: [{ type: "text", text: JSON.stringify(out) }], structuredContent: out };
    },
  };
  return kgApi(client, { config: { iri_base: "https://benchmarks.rewire.it/id/", kinds: { benchmark: "rb:Benchmark", dataset: "rb:Dataset", model: "rb:Model", source: "rb:Source" } }, stats: { calls: {}, ms: 0, release: "fake", statements: 5 } as any });
}

type Loaded = typeof p352;

/** A checkout of main with the pull request's batch folder on it, and the store lines the fixture has. */
function rootWith(p: Loaded, { store = true } = {}) {
  const root = tempRoot();
  fs.mkdirSync(path.join(root, p.batchDir), { recursive: true });
  for (const name of fs.readdirSync(`${p.dir}/batch`)) fs.copyFileSync(`${p.dir}/batch/${name}`, path.join(root, p.batchDir, name));
  if (store && fs.existsSync(`${p.dir}/store`)) {
    fs.mkdirSync(path.join(root, "data/entities"), { recursive: true });
    for (const name of fs.readdirSync(`${p.dir}/store`)) fs.copyFileSync(`${p.dir}/store/${name}`, path.join(root, "data/entities", name));
  }
  return root;
}
const readBatch = (root: string, p: Loaded, name: string) => fs.readFileSync(path.join(root, p.batchDir, name), "utf8");

function fakes(p: Loaded, { reply = p.reply as any, pull = {} as Record<string, unknown>, pages = {} as Record<string, string | null> } = {}) {
  const calls: string[] = [];
  const log: string[] = [];
  const prompts: string[] = [];
  const instructions: string[] = [];
  const anthropic = {
    beta: { messages: { stream: (req: any) => ({ finalMessage: async () => {
      calls.push(`research ${req.model}`);
      prompts.push(req.messages[0].content);
      return { model: req.model, stop_reason: "end_turn", content: [{ type: "text", text: fs.readFileSync(`${p.dir}/revise-notes.md`, "utf8") }], usage: { input_tokens: 6000, output_tokens: 400 } };
    } }) } },
    messages: { create: async (req: any) => {
      calls.push(`structure ${req.model}`);
      instructions.push(JSON.stringify(req));
      return { stop_reason: "end_turn", content: [{ type: "text", text: JSON.stringify(reply) }], usage: { input_tokens: 700, output_tokens: 300 } };
    } },
  };
  const github = {
    pull: async () => ({ ...p.fixture.pull, ...pull }),
    pullFiles: async () => p.fixture.files,
    reviews: async () => p.fixture.reviews,
    compare: async () => ({ merge_base: MERGE_BASE }),
    updatePull: async (_r: string, _n: number, patch: { body: string }) => void log.push(`body ${patch.body.includes("<!-- intake-revision: ") ? "with marker" : "without marker"}`),
    addLabels: async (_r: string, _n: number, labels: string[]) => void log.push(`label ${labels.join(",")}`),
    comment: async (_r: string, _n: number, body: string) => void log.push(`comment ${body.split("\n")[0]}`),
  };
  const fetchImpl = async (url: string) => {
    const text = url in pages ? pages[url] : p.fetches[url]?.text;
    return new Response(text ?? "not found", { status: text ? 200 : 429, headers: { "content-type": "text/plain" } });
  };
  // The store lines records add writes for the batch, as git diff shows them.
  const diff = ["+++ b/data/entities/records.jsonl", ...p.batch.flatMap((r) => {
    const line = JSON.stringify(r);
    return [`+${line}`, `+${JSON.stringify({ id: r.id, sha256: sha256(line), added_in: p.batchDir, added_by: "records:add", changed_by: [] })}`];
  })].join("\n");
  const run = (cmd: string, args: string[]) => {
    const line = [cmd, ...args].join(" ");
    log.push(line);
    if (line === "git rev-parse HEAD") return { ok: true, output: `${BASE}\n` };
    if (line.startsWith("git diff")) return { ok: true, output: diff };
    return { ok: true, output: "ok" };
  };
  return { calls, log, prompts, instructions, deps: { anthropic, github, fetch: fetchImpl, run, now, log: quiet, kg: fakeKg() as ReturnType<typeof fakeKg> | null } };
}

describe("a live revision of #352, with fakes", () => {
  it("rewords the value with the same two model calls, under the cost cap, and pushes one revision", async () => {
    const f = fakes(p352);
    const root = rootWith(p352);
    const r = await main(["--revise", "--pr", "352", "--root", root], env, f.deps);
    expect(r.outcome).toBe("revised");
    expect(f.calls).toEqual(["research claude-sonnet-5-5", "structure claude-haiku-5-5"]);
    expect(r.usage.total()).toBeLessThan(LIMITS.maxRunUsd);
    // The model is told what an amend is and for which fields, and the structuring call how to write an id.
    expect(f.prompts[0]).toContain("amend (only for training_data, task, scope_note: the new wording, the passage that states it copied letter for letter from the source text, and its source URL)");
    expect(f.prompts[0]).toContain("The value should state that the collection covers pretraining and downstream evaluation");
    expect(f.instructions[0]).toContain("id is the record id alone, exactly as the notes give it, never with the field name added");
    const revised = readBatch(root, p352, "batch.jsonl").trim().split("\n").map((l) => JSON.parse(l));
    expect(revised.find((x) => x.id === MODEL).attributes.training_data).toBe("Approximately 380 million cells from 98 datasets, used for pretraining and evaluation together.");
    const revision = JSON.parse(readBatch(root, p352, "revision.json"));
    expect(revision.fields).toEqual([expect.objectContaining({ field: "training_data", action: "amend", before: OLD, passage: PASSAGE, source_url: PREPRINT })]);
    expect(f.log.filter((l) => /^(body|label|comment|git push|git commit -m)/.test(l))).toEqual([
      expect.stringMatching(/^git commit -m Revise ProtCell from #350 after review -m One revision after the reviewer agent requested changes on #352: training_data \(amend\)\./),
      "body with marker",
      `git push --force-with-lease=refs/heads/intake/issue-350:${p352.fixture.pull.head_sha} origin HEAD:refs/heads/intake/issue-350`,
      expect.stringMatching(/^comment The intake agent revised this pull request after the review\./),
    ]);
    expect(r.pull.body).toContain("training_data: reworded from");
    expect(`${r.pull.body.replace(p352.fixture.pull.body, "")}${readBatch(root, p352, "revision.json")}`).not.toMatch(/[\u2013\u2014]/);
  });

  it("hands the pull request over when the source page cannot be opened, whatever the model quotes", async () => {
    const f = fakes(p352, { pages: { [PREPRINT]: null } });
    const r = await main(["--revise", "--pr", "352", "--root", rootWith(p352)], env, f.deps);
    expect(r.outcome).toBe(`${HUMAN_LABEL}: the revision could not settle every failed field: training_data of ${MODEL} (the quoted passage is not, letter for letter, in the text of a source the record cites)`);
    expect(f.log.filter((l) => /^(body|label|comment|git push)/.test(l))).toEqual([`label ${HUMAN_LABEL}`, expect.stringMatching(/^comment The intake agent did not revise this pull request: /)]);
  });

  it("hands over when the draft overlay returns a batch with a change beside the amended field", async () => {
    const f = fakes(p352);
    f.deps.kg = fakeKg({ rewrite: (x: any) => (x.id === MODEL ? { ...x, description: "A model." } : x) });
    const r = await main(["--revise", "--pr", "352", "--root", rootWith(p352)], env, f.deps);
    expect(r.outcome).toBe(`${HUMAN_LABEL}: the revised batch differs from the first in more than the failed fields: ${MODEL}: /description changed`);
    expect(f.log.join("\n")).not.toMatch(/git push|body with marker/);
  });

  it("still revises once only, and skips a pull request that has the label", async () => {
    const again = fakes(p352, { pull: { commits: 2 } });
    expect((await main(["--revise", "--pr", "352", "--root", rootWith(p352)], env, again.deps)).outcome).toMatch(/^needs-tim: the reviewer agent requested changes again and the pull request was already revised once/);
    expect(again.calls).toEqual([]);
    const labelled = fakes(p352, { pull: { labels: [HUMAN_LABEL] } });
    expect((await main(["--revise", "--pr", "352", "--root", rootWith(p352)], env, labelled.deps)).outcome).toBe(`skipped: the pull request is already labelled ${HUMAN_LABEL}`);
    expect(labelled.calls).toEqual([]);
    expect(labelled.log).toEqual([]);
  });
});

describe("a live revision of #354, with fakes", () => {
  it("drops the link and records both rulings in kg.json, with the same two model calls", async () => {
    const f = fakes(p354);
    const root = rootWith(p354);
    const r = await main(["--revise", "--pr", "354", "--root", root], env, f.deps);
    expect(r.outcome).toBe("revised");
    expect(f.calls).toEqual(["research claude-sonnet-5-5", "structure claude-haiku-5-5"]);
    expect(r.usage.total()).toBeLessThan(LIMITS.maxRunUsd);
    // The model sees the two store records as the store holds them, with their source URLs.
    expect(f.prompts[0]).toContain("Store records the reviewer listed as possible duplicates, as the store holds them (JSON).");
    expect(f.prompts[0]).toContain("Sci-Plex single-cell profiles of A549, K562 and MCF7 cells");
    expect(f.prompts[0]).toContain("https://arxiv.org/abs/2405.17631v3");
    const receipt = JSON.parse(readBatch(root, p354, "kg.json"));
    expect(receipt.links).toEqual([]);
    expect(receipt.duplicate_rulings.map((d: any) => `${d.entity} ${d.id} ${d.ruling} ${d.ruled_by}`)).toEqual([`Kinase_Inhibitor_Datasets ${SCIPLEX} distinct revision`, `Kinase_Inhibitor_Datasets ${CARNEVALE} distinct revision`]);
    expect(receipt.duplicate_rulings.every((d: any) => d.locator.includes("The two records share no source URL or DOI."))).toBe(true);
    const revised = readBatch(root, p354, "batch.jsonl").trim().split("\n").map((l) => JSON.parse(l));
    expect(revised.map((x) => x.id)).toEqual(p354.batch.map((x) => x.id));
    expect(revised.find((x) => x.id === BENCHMARK).links).toEqual([]);
    expect(JSON.parse(readBatch(root, p354, "revision.json")).fields.map((x: any) => `${x.field} ${x.action}`)).toEqual(["duplicates rule", "links drop"]);
    expect(f.log.filter((l) => /^(label|git push)/.test(l))).toEqual([`git push --force-with-lease=refs/heads/intake/issue-349:${p354.fixture.pull.head_sha} origin HEAD:refs/heads/intake/issue-349`]);
    expect(r.pull.body).toContain(`duplicates: ruled distinct from \`${SCIPLEX}\``);
  });

  it("hands over when a store record the review names is not in the store on main", async () => {
    const f = fakes(p354);
    const r = await main(["--revise", "--pr", "354", "--root", rootWith(p354, { store: false })], env, f.deps);
    expect(r.outcome).toContain(`${HUMAN_LABEL}: the revision could not settle every failed field: duplicates of ${DATASET} (${SCIPLEX} was not found in the store on the base branch, so no ruling on it can be checked)`);
    expect(f.prompts[0]).toContain("not in the store on the base branch");
    expect(f.log.join("\n")).not.toMatch(/git push|body with marker/);
  });

  it("hands over when a ruling cannot be grounded, and keeps the link drop unpushed too", async () => {
    const reply = copy(p354.reply);
    reply.revisions[1].rulings[1].store_quote = "a screen of kinase inhibitors";
    const f = fakes(p354, { reply });
    const r = await main(["--revise", "--pr", "354", "--root", rootWith(p354)], env, f.deps);
    expect(r.outcome).toBe(`${HUMAN_LABEL}: the revision could not settle every failed field: duplicates of ${DATASET} (the ruling on ${CARNEVALE} quotes a phrase that is not in the store record's name or description)`);
    expect(f.log.filter((l) => /^(body|label|comment|git push)/.test(l))).toEqual([`label ${HUMAN_LABEL}`, expect.stringMatching(/^comment The intake agent did not revise this pull request: /)]);
  });

  it("closes the dataset out when the store has it under the same repository, and moves the link in kg.json", async () => {
    const root = rootWith(p354);
    // The store's record now cites the repository itself.
    const sources = path.join(root, "data/entities/sources.jsonl");
    fs.writeFileSync(sources, fs.readFileSync(sources, "utf8").replaceAll("https://arxiv.org/pdf/2607.23447v1", REPO_URL));
    const subsets = path.join(root, "data/entities/dataset-subsets.jsonl");
    fs.writeFileSync(subsets, fs.readFileSync(subsets, "utf8").replace('"kind":"dataset_subset"', '"kind":"dataset"'));
    const reply = { revisions: [{ ...p354.reply.revisions[1], rulings: [{ id: SCIPLEX, ruling: "same", ground: "none", new_quote: "", store_quote: "", reason: "" }, p354.reply.revisions[1].rulings[1]] }, { ...p354.reply.revisions[0], action: "none", values: [] }] };
    // The link was not dropped by name, so its failure stays open and nothing is pushed.
    const open = fakes(p354, { reply });
    expect((await main(["--revise", "--pr", "354", "--root", root], env, open.deps)).outcome).toContain("links of intake-349-20261121-benchmark-met-kinase-dms-benchmark (the revision gave no value to drop, no passage and no new wording)");
    // With the duplicates the only failed field, the record is closed out and the link moves.
    const body = p354.fixture.reviews.at(-1).body;
    const marker = JSON.parse(/<!-- reviewer-verdict: (\{.*\}) -->$/.exec(body)![1]);
    const only = `${body.split("<!-- reviewer-verdict")[0]}<!-- reviewer-verdict: ${JSON.stringify({ ...marker, problems: marker.problems.slice(1) })} -->`;
    const f = fakes({ ...p354, fixture: { ...p354.fixture, reviews: [{ ...p354.fixture.reviews.at(-1), body: only }] } } as Loaded, { reply });
    const root2 = rootWith(p354);
    fs.copyFileSync(sources, path.join(root2, "data/entities/sources.jsonl"));
    fs.copyFileSync(subsets, path.join(root2, "data/entities/dataset-subsets.jsonl"));
    const r = await main(["--revise", "--pr", "354", "--root", root2], env, f.deps);
    expect(r.outcome).toBe("revised");
    const revised = readBatch(root2, p354, "batch.jsonl").trim().split("\n").map((l) => JSON.parse(l));
    expect(revised.map((x) => x.id)).toEqual(p354.batch.map((x) => x.id).filter((id) => id !== DATASET));
    expect(revised.find((x) => x.id === BENCHMARK).links).toEqual([{ relation: "uses_data", target_id: SCIPLEX }]);
    const receipt = JSON.parse(readBatch(root2, p354, "kg.json"));
    expect(receipt.links).toEqual([expect.objectContaining({ from: BENCHMARK, relation: "uses_data", to: SCIPLEX, in: "store", locator: expect.stringContaining(`Moved in the revision after review from ${DATASET}, which was ruled the same resource as ${SCIPLEX}.`) })]);
    // No ruling is kept for a record that is no longer in the batch.
    expect(receipt.duplicate_rulings).toEqual([]);
    expect(r.pull.body).toContain(`ruled the same resource as the store record \`${SCIPLEX}\``);
  });
});

describe("dry runs of the two fixtures", () => {
  it("write the revised batch folders and call nothing", async () => {
    const run = () => {
      throw new Error("no command expected");
    };
    for (const p of [p352, p354]) {
      const root = tempRoot();
      const r = await main(["--revise", "--dry-run", "--fixtures", p.dir, "--root", root], {}, { now, log: quiet, run, kg: fakeKg() });
      expect(r.outcome).toBe("ready: revision not pushed in this mode");
      expect(fs.readdirSync(path.join(root, p.batchDir)).sort()).toEqual(["batch.jsonl", "kg.json", "notes.md", "review.json", "revision.json"]);
      expect(r.pull.body).toMatch(/<!-- intake-revision: \{"n":1,.*\} -->$/);
      expect(readBatch(root, p, "notes.md")).toContain("## Revision after review");
    }
  });
});
