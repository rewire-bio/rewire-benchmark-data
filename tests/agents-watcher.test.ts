import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import {
  ASSIGNEE, LEAD_LABELS, LIMITS, MARKERS, checkExplanation, diffReleases, explanationFacts, fmt, knownLeads, main, planRun, readRecords, idsNeeded, renderLead, renderOverflow,
} from "../scripts/agents/watcher.mjs";

// The disagreement watcher (#258). Everything here runs without an API key or network. The
// fixtures are real findings from release 2026-11-19-0528a0ffe3cb, trimmed, arranged so that one
// diff has two new medium findings (0311..., 44e5...), one new low finding, a finding re-keyed
// from discrepancy-4db3e5d24233e19b (#210) whose severity rose, one unchanged finding, and two
// findings that stop being live (one with an open watcher lead, one resolved with a closed lead).
const FIXTURES = "tests/agents-watcher-fixtures";
const read = (f: string) => JSON.parse(readFileSync(`${FIXTURES}/${f}`, "utf8"));
const previous = read("previous.json");
const current = read("current.json");
const issues = read("issues.json");
const quiet = () => {};
const RELEASE = "2026-11-19-bbbbbbbbbbbb";
const NEW1 = "discrepancy-0311356983b743d6";
const NEW2 = "discrepancy-44e5640b79522964";
const ROSE = "discrepancy-a2ed36d1ca54b5b9";
const GONE_OPEN = "discrepancy-067e36619b696306";
const GONE_RESOLVED = "discrepancy-0a837fd32465be56";

describe("diff", () => {
  const diff = diffReleases(previous, current);
  it("finds new findings, a rise through previous_ids, and findings that stopped", () => {
    expect(diff.added.map((f) => f.id).sort()).toEqual([NEW1, NEW2, "discrepancy-5079a7277df150f3"].sort());
    expect(diff.rose.map((r) => [r.finding.id, r.from])).toEqual([[ROSE, "low"]]);
    expect(diff.gone.map((g) => [g.finding.id, g.resolved])).toEqual([[GONE_OPEN, false], [GONE_RESOLVED, true]]);
    expect(diff.refired).toEqual([]);
    expect(diff.rulesChanged).toBeNull();
  });
  it("reports a rules change and a resolved finding that fires again", () => {
    const prev = { ...previous, rules: { version: "4" }, discrepancies: [{ ...current.discrepancies[0], resolved: true }] };
    const d = diffReleases(prev, current);
    expect(d.rulesChanged).toEqual({ from: "4", to: "5" });
    expect(d.refired.map((f) => f.id)).toEqual([NEW1]);
  });
  it("finds nothing between a release and itself", () => {
    const d = diffReleases(current, current);
    expect([d.added, d.rose, d.refired, d.gone].map((x) => x.length)).toEqual([0, 0, 0, 0]);
  });
  it("matches a finding whose ID changed but whose key did not, without previous_ids", () => {
    const old = { ...current.discrepancies[0], id: "discrepancy-1111111111111111" };
    const d = diffReleases({ ...previous, discrepancies: [old] }, { ...current, discrepancies: [current.discrepancies[0]] });
    expect(d.added).toEqual([]);
    expect(d.gone).toEqual([]);
    expect(d.priorIds.get(NEW1)).toEqual([old.id]);
    // Its lead issue, filed under the old ID, still counts, so a rise comments there.
    const rose = diffReleases({ ...previous, discrepancies: [{ ...old, severity: "low" }] }, { ...current, discrepancies: [current.discrepancies[0]] });
    const plan = planRun(rose, { issues: [{ number: 900, title: "Lead: x", body: `<!-- ${MARKERS.lead}: ${old.id} -->`, state: "open" }], release: RELEASE });
    expect(plan.file).toEqual([]);
    expect(plan.comments.map((c) => c.number)).toEqual([900]);
  });
  it("matches every earlier finding a merged finding covers, so none is reported gone", () => {
    const a = { ...previous.discrepancies[1], id: "discrepancy-aaaaaaaaaaaaaaaa", key: null };
    const b = { ...previous.discrepancies[1], id: "discrepancy-bbbbbbbbbbbbbbbb", key: null };
    const merged = { ...current.discrepancies[0], previous_ids: [a.id, b.id] };
    const d = diffReleases({ ...previous, discrepancies: [a, b] }, { ...current, discrepancies: [merged] });
    expect(d.gone).toEqual([]);
    expect(d.added).toEqual([]);
    expect(d.priorIds.get(merged.id)).toEqual([a.id, b.id]);
  });
  it("says a gone finding may have been re-keyed when the rules changed", () => {
    const d = diffReleases({ ...previous, rules: { version: "4" } }, current);
    const plan = planRun(d, { issues, release: RELEASE });
    const gone = plan.comments.find((c) => c.marker.startsWith(MARKERS.gone));
    expect(gone?.body).toContain("may continue under a new ID");
  });
});

describe("dedupe", () => {
  it("knows watcher markers and IDs named in hand-written Lead issues, not other issues", () => {
    const known = knownLeads(issues);
    expect(known.get("discrepancy-4db3e5d24233e19b")?.[0].number).toBe(210);
    expect(known.get(GONE_OPEN)?.[0].how).toBe("lead");
    expect(known.has(NEW1)).toBe(false); // #402 names it but is not a lead issue
  });
  it("files each new medium finding once, comments on a rise and on a finding that stopped", () => {
    const plan = planRun(diffReleases(previous, current), { issues, release: RELEASE });
    expect(plan.file.map((l) => l.finding.id).sort()).toEqual([NEW1, NEW2].sort());
    expect(plan.comments.map((c) => [c.number, c.marker])).toEqual([
      [210, `${MARKERS.rose}: ${ROSE} ${RELEASE}`],
      [400, `${MARKERS.gone}: ${GONE_OPEN} ${RELEASE}`],
    ]);
    expect(plan.comments.every((c) => c.body.includes(`<!-- ${c.marker} -->`))).toBe(true);
  });
  it("does not file a finding again once a lead issue carries its marker", () => {
    const filed = [{ number: 500, title: "Lead: x", body: `<!-- ${MARKERS.lead}: ${NEW1} -->`, state: "closed" }];
    const plan = planRun(diffReleases(previous, current), { issues: [...issues, ...filed], release: RELEASE });
    expect(plan.file.map((l) => l.finding.id)).toEqual([NEW2]);
    expect(plan.skipped.map((s) => s.id)).toContain(NEW1);
  });
  it("comments on a closed lead issue when its finding's severity rises, without reopening it", () => {
    const closed = issues.map((i: { number: number }) => (i.number === 210 ? { ...i, state: "closed" } : i));
    const plan = planRun(diffReleases(previous, current), { issues: closed, release: RELEASE });
    const c = plan.comments.find((x) => x.number === 210)!;
    expect(c.body).toContain("does not reopen it");
  });
  it("puts leads over the cap into one summary issue whose markers stop them being filed later", () => {
    const plan = planRun(diffReleases(previous, current), { issues, release: RELEASE, maxIssues: 1 });
    expect(plan.file).toHaveLength(1);
    expect(plan.overflow).toHaveLength(1);
    const summary = renderOverflow(plan.overflow, { records: new Map(), release: RELEASE, previous: "p", filedCount: 1 });
    expect(summary.labels).toEqual(LEAD_LABELS);
    expect(summary.assignees).toEqual([ASSIGNEE]);
    const again = planRun(diffReleases(previous, current), { issues: [...issues, { number: 501, title: summary.title, body: summary.body, state: "open" }], release: RELEASE, maxIssues: 1 });
    expect(again.file.map((l) => l.finding.id)).toEqual([plan.file[0].finding.id]);
    expect(again.overflow).toEqual([]);
  });
});

describe("issue text", () => {
  it("builds the lead from the data: link, table, values, labels, assignee and marker", async () => {
    const lead = { finding: current.discrepancies.find((f: { id: string }) => f.id === NEW2), reason: "new" as const };
    const records = await readRecords(`${FIXTURES}/records.jsonl`, idsNeeded([lead.finding]));
    const issue = renderLead(lead, { records, release: RELEASE, previous: "2026-11-18-aaaaaaaaaaaa", explanation: null, explanationNote: "No explanation." });
    expect(issue.title).toMatch(/^Lead: PROVEAN and SIFT/);
    expect(issue.labels).toEqual(["lead", "needs-tim"]);
    expect(issue.assignees).toEqual(["timini"]);
    expect(issue.body).toContain(`https://benchmarks.rewirebio.io/contested/${NEW2}/`);
    expect(issue.body).toContain("| Study | Role | Verdict | PROVEAN higher | SIFT higher | Ties | Comparisons |");
    expect(issue.body).toContain("https://doi.org/10.1038/s41588-023-01465-0");
    expect(issue.body).toContain("| 0.8442 | 0.8725 |");
    expect(issue.body).toContain("depth tier 1");
    expect(issue.body).toContain("`discrepancy_review` claim revision");
    expect(issue.body).toContain(`<!-- ${MARKERS.lead}: ${NEW2} -->`);
    expect(issue.body).not.toMatch(/[\u2013\u2014]/);
  });
  it("rounds long values and keeps short ones as printed", () => {
    expect(fmt(0.844189980297173)).toBe("0.8442");
    expect(fmt(0.61)).toBe("0.61");
    expect(fmt(366)).toBe("366");
    expect(fmt(null)).toBe("");
  });
});

describe("explanation check", () => {
  const facts = { systems: ["ESM-2", "ESM3"], studies: [{ metrics: ["spearman-correlation"], comparisons_total: 12 }] };
  it("keeps digits that are part of a name from the facts, and strips dashes", () => {
    const r = checkExplanation("ESM-2 and ESM3 differ \u2014 check the spearman-correlation definition first.", facts);
    expect(r).toEqual({ ok: true, text: "ESM-2 and ESM3 differ, check the spearman-correlation definition first." });
  });
  it("drops a paragraph with a link or any number of its own", () => {
    expect(checkExplanation("See https://example.org for details.", facts).ok).toBe(false);
    expect(checkExplanation("ESM3 scores 0.47 on ProteinGym.", facts).ok).toBe(false);
    // 12 is in the facts as a count, but the paragraph may not state counts either.
    expect(checkExplanation("Only 3 of 12 comparisons agree.", facts).ok).toBe(false);
    expect(checkExplanation("The gap is about 0.6.", facts).ok).toBe(false);
  });
  it("drops counts and fractions written in words", () => {
    expect(checkExplanation("The outlier study ranks SIFT above PROVEAN in nine of twelve comparisons, while three other studies disagree.", facts).ok).toBe(false);
    expect(checkExplanation("About half of the comparisons agree.", facts).ok).toBe(false);
    expect(checkExplanation("ESM3 wins twice as often.", facts).ok).toBe(false);
    expect(checkExplanation("One possibility is that the outlier study used a different subset.", facts).ok).toBe(true);
    expect(checkExplanation("The two systems may have been run at different sizes.", facts).ok).toBe(true);
    expect(checkExplanation("The two consensus studies agree.", facts).ok).toBe(false);
  });
  it("keeps a shortened name that carries digits, but not a bare number from a name", () => {
    const f = { systems: ["ESM-1b (650M)", "SIFT"], studies: [{ study: "Brandes 2023 genome-wide prediction of disease variant effects", metrics: ["AUC"], protocols: ["BEELINE 2020 Figure 2"] }] };
    expect(checkExplanation("ESM-1b style scoring may differ from SIFT.", f).ok).toBe(true);
    expect(checkExplanation("The study by Brandes et al. 2023 used a different metric.", f).ok).toBe(true);
    expect(checkExplanation("SIFT wins 2 comparisons.", f).ok).toBe(false);
  });
});

describe("dry run on the fixtures", () => {
  it("plans two leads and two comments, with no model or GitHub call", async () => {
    const r = await main(["--dry-run"], {}, { log: quiet });
    expect(r.filed.map((f: { id: string }) => f.id).sort()).toEqual([NEW1, NEW2].sort());
    expect(r.comments.map((c: { number: number }) => c.number)).toEqual([210, 400]);
    expect(r.usage.total()).toBe(0);
    expect(r.summary).toContain("records no `discrepancy_review` claim");
    expect(r.summary).not.toMatch(/[\u2013\u2014]/);
  });
});

describe("live run, with fakes", () => {
  function fakes(existingComments: Record<number, string[]> = {}) {
    const created: { title: string; body: string; labels: string[]; assignees: string[] }[] = [];
    const posted: { number: number; body: string }[] = [];
    let labels: string[] = [];
    const github = {
      listIssues: async () => [...issues, ...created.map((c, i) => ({ number: 900 + i, title: c.title, body: c.body, state: "open" }))],
      ensureLabels: async (_repo: string, names: string[]) => { labels = names; },
      createIssue: async (_repo: string, issue: (typeof created)[number]) => { created.push(issue); return { html_url: `https://github.com/rewire-bio/x/issues/${900 + created.length - 1}`, number: 900 + created.length - 1 }; },
      commentBodies: async (_repo: string, n: number) => existingComments[n] ?? [],
      comment: async (_repo: string, number: number, body: string) => { posted.push({ number, body }); },
    };
    const anthropic = {
      beta: { messages: { create: async () => ({ model: "claude-sonnet-5-5", stop_reason: "end_turn", content: [{ type: "text", text: "The studies use different metrics. Check the metric definitions first." }], usage: { input_tokens: 3000, output_tokens: 300 } }) } },
    };
    return { github, anthropic, created, posted, labels: () => labels };
  }
  const args = ["--previous", `${FIXTURES}/previous.json`, "--current", `${FIXTURES}/current.json`, "--records", `${FIXTURES}/records.jsonl`];
  const env = { GITHUB_REPOSITORY: "rewire-bio/rewire-benchmark-data" };

  it("files the leads with the explanation, posts each comment once, and is idempotent", async () => {
    const f = fakes({ 400: [`<!-- ${MARKERS.gone}: ${GONE_OPEN} ${RELEASE} -->`] });
    const r = await main(args, env, { github: f.github, anthropic: f.anthropic, log: quiet });
    expect(f.labels()).toEqual(LEAD_LABELS);
    expect(f.created).toHaveLength(2);
    expect(f.created.every((c) => c.assignees[0] === "timini" && c.body.includes("The studies use different metrics."))).toBe(true);
    expect(f.posted.map((p) => p.number)).toEqual([210]);
    expect(r.comments.find((c: { number: number }) => c.number === 400).status).toBe("already posted");
    expect(r.usage.total()).toBeGreaterThan(0);
    expect(r.usage.total()).toBeLessThan(LIMITS.maxRunUsd);
    const again = await main(args, env, { github: f.github, anthropic: f.anthropic, log: quiet });
    expect(again.filed).toEqual([]);
    expect(f.created).toHaveLength(2);
  });

  it("files without the paragraph when the model's text fails the check", async () => {
    const f = fakes();
    f.anthropic.beta.messages.create = async () => ({ model: "claude-sonnet-5-5", stop_reason: "end_turn", content: [{ type: "text", text: "PROVEAN scores 0.91 here." }], usage: { input_tokens: 10, output_tokens: 10 } });
    const r = await main([...args, "--report-only"], env, { github: f.github, anthropic: f.anthropic, log: quiet });
    expect(f.created).toEqual([]);
    expect(r.filed[0].explanationNote).toMatch(/stated numbers/);
    expect(r.filed[0].issue.body).not.toContain("0.91");
  });

  it("files without the paragraph when the model stops early", async () => {
    const f = fakes();
    f.anthropic.beta.messages.create = async () => ({ model: "claude-sonnet-5-5", stop_reason: "max_tokens", content: [{ type: "text", text: "The studies use" }], usage: { input_tokens: 10, output_tokens: 2000 } });
    const r = await main([...args, "--report-only"], env, { github: f.github, anthropic: f.anthropic, log: quiet });
    expect(r.filed[0].explanationNote).toMatch(/stopped early/);
  });

  it("refuses a repository outside rewire-bio", async () => {
    await expect(main(args, { GITHUB_REPOSITORY: "someone/else" }, { log: quiet })).rejects.toThrow(/rewire-bio/);
  });

  it("gives the model only facts from the data", async () => {
    const finding = current.discrepancies.find((x: { id: string }) => x.id === NEW1);
    const records = await readRecords(`${FIXTURES}/records.jsonl`, idsNeeded([finding]));
    const facts = explanationFacts(finding, records);
    expect(facts.systems).toEqual(["GRNBoost2", "PPCOR (partial Pearson correlation)"]);
    expect(facts.studies[0].role).toBe("outlier");
  });
});

describe("workflow", () => {
  const wf = readFileSync(".github/workflows/watcher.yml", "utf8");
  const nameOf = (file: string) => /^name:\s*(.+)$/m.exec(readFileSync(`.github/workflows/${file}`, "utf8"))?.[1].trim().replace(/^["']|["']$/g, "");
  it("runs after the release workflow, by its exact name", () => {
    expect(wf).toContain(`- "${nameOf("release.yml")}"`);
  });
  it("has no schedule, so it cannot collide with discovery or the pipeline alert", () => {
    expect(wf).not.toMatch(/^\s*schedule:/m);
  });
  it("takes the repository from the run, not a fixed name", () => {
    expect(wf).not.toContain("rewire-benchmark-data");
  });
});
