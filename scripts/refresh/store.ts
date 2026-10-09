import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import os from "node:os";
import { z } from "zod";
import { loadUseCaseReview } from "../omics/use-cases";

const iso = z.string().datetime({ offset: true });
const id = z.string().regex(/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,100}$/);
const unique = z
  .array(id)
  .refine((a) => new Set(a).size === a.length, "Duplicate IDs");
const url = z
  .string()
  .url()
  .refine((v) => new URL(v).protocol === "https:", "HTTPS required");
const sha = z.string().regex(/^[a-f0-9]{64}$/);
export const Schedule = z
  .object({
    status: z.enum(["planned", "active", "paused"]),
    timezone: z.literal("Europe/London"),
    description: z.string().min(1),
    configured_at: iso,
    next_due_at: iso,
    maintainer: z.string().nullable(),
    scientific_reviewer: z.string().nullable(),
    overlap_days: z.number().int().min(1).max(90),
    max_attempts: z.number().int().min(1).max(10),
    max_minutes: z.number().int().positive(),
    max_queries: z.number().int().positive(),
    required_scope: unique.min(1),
  })
  .strict();
export const Report = z
  .object({
    summary: z.string().min(1),
    coverage: z
      .object({ checked_ids: unique, gaps: z.array(z.string().min(1)) })
      .strict(),
    checks: z.array(
      z
        .object({
          scope_id: id,
          query: z.string().min(1),
          checked_at: iso,
          url,
          decision: z.enum([
            "included",
            "revised",
            "excluded",
            "unchanged",
            "blocked",
          ]),
          reason: z.string().min(1),
          record_ids: unique,
        })
        .strict(),
    ),
    use_case_review: z
      .object({
        reviewed_ids: unique,
        fingerprint_policy: z.enum(["preserved", "explicitly_reviewed"]),
        review_receipt: z.string().nullable(),
      })
      .strict(),
    limitations: z.array(z.string().min(1)),
    artifact_sha256: z.record(z.string(), sha).optional(),
  })
  .strict();
const Counts = z
  .object({
    added: z.number().int().nonnegative(),
    revised: z.number().int().nonnegative(),
    excluded: z.number().int().nonnegative(),
    blocked: z.number().int().nonnegative(),
  })
  .strict();
const Run = z
  .object({
    schema_version: z.literal("1.0"),
    id,
    cycle_id: id,
    attempt: z.number().int().positive(),
    retry_of: id.nullable(),
    scope_amendment: z.string().min(1).nullable().default(null),
    baseline_release_id: id,
    baseline_manifest_sha256: sha,
    required_scope: unique.min(1),
    window: z.object({ from: iso, to: iso }).strict(),
    status: z.enum(["running", "completed", "blocked", "failed"]),
    started_at: iso,
    finished_at: iso.nullable(),
    outcome: z.enum(["no_change", "review_required"]).nullable(),
    coverage: z
      .object({
        target_ids: unique,
        checked_ids: unique,
        gaps: z.array(z.string()),
      })
      .strict(),
    counts: Counts,
    report_sha256: sha.nullable(),
    use_case_sha256: sha,
    limits: z
      .object({
        max_minutes: z.number().positive(),
        max_queries: z.number().int().positive(),
      })
      .strict(),
  })
  .strict()
  .superRefine((r, ctx) => {
    if ((r.status === "running") !== (r.report_sha256 === null))
      ctx.addIssue({ code: "custom", message: "Terminal attempts require a retained report" });
    if ((r.status === "running") !== (r.finished_at === null))
      ctx.addIssue({ code: "custom", message: "Invalid finish time" });
    if ((r.status === "completed") !== (r.outcome !== null))
      ctx.addIssue({
        code: "custom",
        message: "Only completed runs have an outcome",
      });
  });
export const Update = z
  .object({
    release_id: id,
    manifest_sha256: sha,
    commit: z.string().regex(/^[a-f0-9]{40}$/),
    published_at: iso,
    time_basis: z.enum(["observed", "deployment"]),
    maintenance_run_id: id.nullable(),
    summary: z.array(z.string().min(1)).min(1),
    links: z.array(z.object({ label: z.string().min(1), url }).strict()),
    receipt_url: url,
    proof_sha256: sha,
  })
  .strict();
export type RefreshRun = z.infer<typeof Run>;
export const digest = (bytes: Buffer | string) =>
  crypto.createHash("sha256").update(bytes).digest("hex");
const json = (v: unknown) => JSON.stringify(v, null, 2) + "\n";
export function nextMonthly(after: string) {
  const d = new Date(after);
  let year = d.getUTCFullYear(),
    month = d.getUTCMonth();
  for (let n = 0; n < 14; n++, month++) {
    const provisional = new Date(Date.UTC(year, month, 1, 9));
    const hour = Number(
      new Intl.DateTimeFormat("en-GB", {
        timeZone: "Europe/London",
        hour: "2-digit",
        hourCycle: "h23",
      }).format(provisional),
    );
    const instant = new Date(provisional.getTime() - (hour - 9) * 3600000);
    if (instant > d) return instant.toISOString();
  }
  throw Error("Cannot compute next monthly review");
}
export class RefreshStore {
  constructor(
    readonly root: string,
    readonly now = () => new Date().toISOString(),
  ) {}
  file(name: string) {
    const p = path.resolve(this.root, name);
    if (!p.startsWith(path.resolve(this.root) + path.sep))
      throw Error("Path escapes repository");
    return p;
  }
  read(name: string) {
    return JSON.parse(fs.readFileSync(this.file(name), "utf8"));
  }
  write(name: string, value: unknown, exclusive = false) {
    const p = this.file(name);
    fs.mkdirSync(path.dirname(p), { recursive: true });
    if (exclusive) fs.writeFileSync(p, json(value), { flag: "wx" });
    else {
      const tmp = p + ".tmp-" + crypto.randomUUID();
      fs.writeFileSync(tmp, json(value), { flag: "wx" });
      fs.renameSync(tmp, p);
    }
  }
  locked<T>(fn: () => T): T {
    const lock = this.file("maintenance/.refresh.lock");
    fs.mkdirSync(path.dirname(lock), { recursive: true });
    let fd: number;
    try {
      fd = fs.openSync(lock, "wx");
    } catch {
      throw Error(
        "Refresh store locked; inspect/resume before an explicit unlock",
      );
    }
    try {
      fs.writeFileSync(
        fd,
        json({ pid: process.pid, host: os.hostname(), at: this.now() }),
      );
      return fn();
    } finally {
      fs.closeSync(fd);
      fs.unlinkSync(lock);
    }
  }
  unlock(reason: string) {
    if (!reason.trim()) throw Error("Unlock requires a reason");
    const lock = this.read("maintenance/.refresh.lock");
    if (lock.host !== os.hostname())
      throw Error("Lock belongs to another host; recover on that host");
    try {
      process.kill(lock.pid, 0);
      throw Error("Lock owner is still running");
    } catch (e) {
      if ((e as NodeJS.ErrnoException).code !== "ESRCH") throw e;
    }
    this.write(
      `maintenance/recoveries/${crypto.randomUUID()}.json`,
      { ...lock, reason, recovered_at: this.now() },
      true,
    );
    fs.unlinkSync(this.file("maintenance/.refresh.lock"));
  }
  schedule() {
    return Schedule.parse(this.read("maintenance/schedule.json"));
  }
  runs() {
    const dir = this.file("maintenance/runs");
    if (!fs.existsSync(dir)) return [];
    return fs
      .readdirSync(dir)
      .filter((f) => f.endsWith(".json"))
      .map((f) => Run.parse(this.read("maintenance/runs/" + f)))
      .sort(
        (a, b) =>
          a.started_at.localeCompare(b.started_at) || a.attempt - b.attempt,
      );
  }
  get(runId: string) {
    id.parse(runId);
    return Run.parse(this.read(`maintenance/runs/${runId}.json`));
  }
  /** Use cases are store records; their judgements are claims citing links:assessed_by. */
  private useCaseLines() {
    const read = (p: string) =>
      fs.existsSync(this.file(p))
        ? fs.readFileSync(this.file(p), "utf8").split("\n").filter(Boolean)
        : [];
    return {
      cases: read("data/entities/use-cases.jsonl"),
      judgements: read("data/evidence/claims.jsonl").filter((line) =>
        line.includes('"field":"links:assessed_by:'),
      ),
    };
  }
  cases() {
    return this.useCaseLines().cases.map(
      (line) => (JSON.parse(line) as { id: string }).id,
    );
  }
  caseHash() {
    const base = this.file("data/omics/use-cases");
    const walk = (dir: string): string[] =>
      fs
        .readdirSync(dir, { withFileTypes: true })
        .sort((a, b) => a.name.localeCompare(b.name))
        .flatMap((entry) => {
          if (entry.isSymbolicLink())
            throw Error("Symlink use-case evidence rejected");
          const p = path.join(dir, entry.name);
          return entry.isDirectory() ? walk(p) : [p];
        });
    const { cases, judgements } = this.useCaseLines();
    return digest(
      JSON.stringify([
        ...(fs.existsSync(base) ? walk(base) : []).map((p) => [
          path.relative(base, p),
          digest(fs.readFileSync(p)),
        ]),
        ["records", digest(cases.join("\n"))],
        ["judgements", digest(judgements.join("\n"))],
      ]),
    );
  }
  link(runId: string) {
    const file = `maintenance/links/${runId}.json`;
    return fs.existsSync(this.file(file))
      ? z.object({ url, cycle_id: id }).strict().parse(this.read(file)).url
      : null;
  }
  begin(
    cycle: string,
    scope: string[],
    baseline: string,
    retryOf?: string,
    scopeAmendment?: string,
  ) {
    return this.locked(() => {
      if (
        !/^(\d{4}-(0[1-9]|1[0-2])|correction-\d{4}-\d{2}-\d{2}-[a-z0-9-]+)$/.test(
          cycle,
        )
      )
        throw Error("Use YYYY-MM or correction-YYYY-MM-DD-slug cycle");
      unique.min(1).parse(scope);
      id.parse(baseline);
      const schedule = this.schedule(),
        runs = this.runs(),
        prior = runs.filter((r) => r.cycle_id === cycle),
        now = this.now();
      if (runs.some((r) => r.status === "running"))
        throw Error("Another refresh is running; resume it");
      if (prior.some((r) => r.status === "completed"))
        throw Error("Cycle already completed; resume its review");
      if (prior.length >= schedule.max_attempts)
        throw Error("Attempt limit reached");
      const previous = prior.at(-1);
      if (previous && retryOf !== previous.id)
        throw Error(
          "Retry must explicitly reference the latest failed/blocked attempt",
        );
      if (!previous && retryOf) throw Error("Unknown retry");
      if (previous && previous.baseline_release_id !== baseline)
        throw Error("Retry must retain baseline");
      if (
        previous &&
        [...scope].sort().join() !==
          [...previous.coverage.target_ids].sort().join()
      ) {
        if (
          !scopeAmendment?.trim() ||
          previous.coverage.target_ids.some((s) => !scope.includes(s))
        )
          throw Error(
            "Scope may only expand with an explicit scope amendment reason",
          );
      } else if (scopeAmendment)
        throw Error("Scope amendment requires an expanded retry scope");
      const baselineBytes = fs.readFileSync(
        this.file(`data/omics/releases/${baseline}.json`),
      );
      if (JSON.parse(baselineBytes.toString()).release_id !== baseline)
        throw Error("Baseline receipt mismatch");
      if (
        previous &&
        digest(baselineBytes) !== previous.baseline_manifest_sha256
      )
        throw Error("Baseline changed");
      const last = runs
        .filter(
          (r) =>
            r.status === "completed" && !r.cycle_id.startsWith("correction-"),
        )
        .at(-1);
      const from = new Date(
        new Date(last?.window.to ?? now).getTime() -
          (schedule.overlap_days + (last ? 0 : 31)) * 86400000,
      ).toISOString();
      const run: RefreshRun = {
        schema_version: "1.0",
        id: crypto.randomUUID(),
        cycle_id: cycle,
        attempt: prior.length + 1,
        retry_of: retryOf ?? null,
        scope_amendment: scopeAmendment ?? null,
        baseline_release_id: baseline,
        baseline_manifest_sha256: digest(baselineBytes),
        required_scope: previous?.required_scope ?? schedule.required_scope,
        window: previous?.window ?? { from, to: now },
        status: "running",
        started_at: now,
        finished_at: null,
        outcome: null,
        coverage: { target_ids: scope, checked_ids: [], gaps: [] },
        counts: { added: 0, revised: 0, excluded: 0, blocked: 0 },
        report_sha256: null,
        use_case_sha256: this.caseHash(),
        limits: {
          max_minutes: schedule.max_minutes,
          max_queries: schedule.max_queries,
        },
      };
      this.write(`maintenance/runs/${run.id}.json`, Run.parse(run), true);
      return run;
    });
  }
  finish(
    runId: string,
    reportFile: string,
    status: "completed" | "blocked" | "failed",
    outcome?: "no_change" | "review_required",
  ) {
    return this.locked(() => {
      const run = this.get(runId);
      if (run.status !== "running")
        throw Error("Finished attempts are immutable");
      const report = Report.parse(this.read(reportFile)),
        now = this.now();
      for (const [file, hash] of Object.entries(report.artifact_sha256 ?? {}))
        if (digest(fs.readFileSync(this.file(file))) !== hash)
          throw Error("Evidence artifact checksum mismatch");
      if (
        report.coverage.checked_ids.some(
          (s) => !run.coverage.target_ids.includes(s),
        )
      )
        throw Error("Checked scope outside declared scope");
      if (
        report.checks.some(
          (c) =>
            !run.coverage.target_ids.includes(c.scope_id) ||
            new Date(c.checked_at) < new Date(run.window.from) ||
            new Date(c.checked_at) > new Date(now),
        )
      )
        throw Error("Check scope or retrieval time outside attempt");
      if (
        report.coverage.checked_ids.some(
          (s) => !report.checks.some((c) => c.scope_id === s),
        )
      )
        throw Error("Checked scope lacks evidence");
      if (
        report.use_case_review.fingerprint_policy === "preserved" &&
        run.use_case_sha256 !== this.caseHash()
      )
        throw Error("Use-case inputs changed without explicit review");
      let reviewHash: string | null = null;
      if (report.use_case_review.fingerprint_policy === "explicitly_reviewed") {
        if (!report.use_case_review.review_receipt)
          throw Error("Explicit re-review needs a receipt");
        if (
          report.use_case_review.review_receipt !==
          "data/omics/use-cases/review.json"
        )
          throw Error("Use the native use-case review receipt");
        const reviewed = loadUseCaseReview(this.file("data/omics/use-cases"));
        if (
          !reviewed ||
          Date.parse(reviewed.reviewed_at) < Date.parse(run.started_at) ||
          Date.parse(reviewed.reviewed_at) > Date.parse(now)
        )
          throw Error("Explicit re-review must be dated within this attempt");
        reviewHash = digest(
          fs.readFileSync(this.file(report.use_case_review.review_receipt)),
        );
      }
      const counts = { added: 0, revised: 0, excluded: 0, blocked: 0 };
      for (const c of report.checks) {
        if (c.decision === "included") counts.added++;
        else if (c.decision !== "unchanged") counts[c.decision]++;
      }
      if (status === "completed") {
        if (!outcome) throw Error("Completed run needs an outcome");
        const required = run.cycle_id.startsWith("correction-")
          ? run.coverage.target_ids
          : run.required_scope;
        if (
          required.some((s) => !run.coverage.target_ids.includes(s)) ||
          run.coverage.target_ids.some(
            (s) => !report.coverage.checked_ids.includes(s),
          ) ||
          report.coverage.gaps.length ||
          counts.blocked
        )
          throw Error("Incomplete coverage cannot complete a sweep");
        if (
          run.coverage.target_ids.includes("use-cases") &&
          this.cases().some(
            (c) => !report.use_case_review.reviewed_ids.includes(c),
          )
        )
          throw Error("Every use case requires review");
        if (
          report.checks.length > run.limits.max_queries ||
          (new Date(now).getTime() - new Date(run.started_at).getTime()) /
            60000 >
            run.limits.max_minutes
        )
          throw Error("Effort limit exceeded; record incomplete coverage");
        if ((outcome === "no_change") !== (counts.added + counts.revised === 0))
          throw Error("Outcome disagrees with findings");
      } else if (outcome)
        throw Error("Incomplete runs cannot have a completed outcome");
      const reportBytes = json({
        ...report,
        review_receipt_sha256: reviewHash,
      });
      // Report is content-addressed: retrying after a crash may reuse identical bytes, never overwrite evidence.
      const reportHash = digest(reportBytes),
        reportPath = `maintenance/reports/${runId}/${reportHash}.json`;
      if (!fs.existsSync(this.file(reportPath)))
        this.write(reportPath, JSON.parse(reportBytes), true);
      const finished = Run.parse({
        ...run,
        status,
        finished_at: now,
        outcome: outcome ?? null,
        coverage: { ...run.coverage, ...report.coverage },
        counts,
        report_sha256: reportHash,
      });
      this.write(`maintenance/runs/${runId}.json`, finished);
      return finished;
    });
  }
  linkPr(runId: string, prUrl: string) {
    return this.locked(() => {
      const run = this.get(runId);
      url.parse(prUrl);
      if (
        !/^https:\/\/github.com\/rewire-bio\/rewire-benchmark-data\/pull\/\d+$/.test(
          prUrl,
        )
      )
        throw Error("Expected producer review PR URL");
      const existing = this.runs()
        .filter((r) => r.cycle_id === run.cycle_id)
        .map((r) => this.link(r.id))
        .filter(Boolean);
      if (existing.some((u) => u !== prUrl))
        throw Error("Cycle already linked to another PR");
      const name = `maintenance/links/${runId}.json`;
      if (this.link(runId) === prUrl) return;
      this.write(name, { url: prUrl, cycle_id: run.cycle_id }, true);
    });
  }
  publicData() {
    const schedule = this.schedule(),
      runs = this.runs();
    // A correction must not advance the monthly search cursor or its due date.
    const last = runs
      .filter(
        (r) =>
          r.status === "completed" && !r.cycle_id.startsWith("correction-"),
      )
      .at(-1);
    const nextDue = last ? nextMonthly(last.window.to) : schedule.next_due_at;
    const updatesDir = this.file("maintenance/updates");
    const updates = fs.existsSync(updatesDir)
      ? fs
          .readdirSync(updatesDir)
          .filter((f) => f.endsWith(".json"))
          .map((f) => Update.parse(this.read(`maintenance/updates/${f}`)))
      : [];
    for (const update of updates) {
      if (update.maintenance_run_id) {
        const run = runs.find((r) => r.id === update.maintenance_run_id);
        if (
          !run ||
          run.status !== "completed" ||
          run.outcome !== "review_required"
        )
          throw Error("Invalid publication run attribution");
      }
      const proofBytes = fs.readFileSync(
        this.file(`maintenance/publication-proofs/${update.proof_sha256}.json`),
      );
      if (digest(proofBytes) !== update.proof_sha256)
        throw Error("Publication proof checksum mismatch");
      const proof = JSON.parse(proofBytes.toString());
      if (
        proof.deployment.release_id !== update.release_id ||
        proof.deployment.commit !== update.commit ||
        proof.deployment.manifest_sha256 !== update.manifest_sha256 ||
        proof.manifest_sha256 !== update.manifest_sha256 ||
        proof.observed_at !== update.published_at
      )
        throw Error("Publication proof does not match entry");
      if (
        digest(
          fs.readFileSync(
            this.file(`data/omics/releases/${update.release_id}.json`),
          ),
        ) !== update.manifest_sha256
      )
        throw Error("Published archive checksum mismatch");
    }
    for (const run of runs)
      if (run.report_sha256) {
        const p = `maintenance/reports/${run.id}/${run.report_sha256}.json`;
        const bytes = fs.readFileSync(this.file(p));
        if (digest(bytes) !== run.report_sha256)
          throw Error("Report checksum mismatch");
        const { review_receipt_sha256, ...report } = JSON.parse(
          bytes.toString(),
        );
        const checkedReport = Report.parse(report);
        // Receipts are reviewable repository data, so export must enforce the
        // same completion rules as finish(), even after a manual JSON edit.
        const counts = { added: 0, revised: 0, excluded: 0, blocked: 0 };
        for (const check of checkedReport.checks) {
          if (check.decision === "included") counts.added++;
          else if (check.decision !== "unchanged") counts[check.decision]++;
          if (!run.coverage.target_ids.includes(check.scope_id) ||
              Date.parse(check.checked_at) < Date.parse(run.window.from) ||
              Date.parse(check.checked_at) > Date.parse(run.finished_at!)) {
            throw Error("Retained check scope or retrieval time outside attempt");
          }
        }
        if (Object.keys(counts).some(key => counts[key as keyof typeof counts] !== run.counts[key as keyof typeof counts]))
          throw Error("Run counts differ from its report");
        if (checkedReport.coverage.checked_ids.some(scope =>
          !run.coverage.target_ids.includes(scope) || !checkedReport.checks.some(check => check.scope_id === scope)))
          throw Error("Retained checked scope lacks declared evidence");
        if (run.status === "completed") {
          const required = run.cycle_id.startsWith("correction-") ? run.coverage.target_ids : run.required_scope;
          if (required.some(scope => !run.coverage.target_ids.includes(scope)) ||
              run.coverage.target_ids.some(scope => !checkedReport.coverage.checked_ids.includes(scope)) ||
              checkedReport.coverage.gaps.length || counts.blocked)
            throw Error("Incomplete coverage cannot complete an exported sweep");
          if ((run.outcome === "no_change") !== (counts.added + counts.revised === 0))
            throw Error("Completed outcome disagrees with retained findings");
          if (checkedReport.checks.length > run.limits.max_queries ||
              (Date.parse(run.finished_at!) - Date.parse(run.started_at)) / 60000 > run.limits.max_minutes)
            throw Error("Completed retained sweep exceeds effort limits");
        }
        for (const [file, hash] of Object.entries(report.artifact_sha256 ?? {}))
          if (digest(fs.readFileSync(this.file(file))) !== hash)
            throw Error("Evidence artifact checksum mismatch");
        if (
          JSON.stringify(report.coverage.checked_ids) !==
            JSON.stringify(run.coverage.checked_ids) ||
          JSON.stringify(report.coverage.gaps) !==
            JSON.stringify(run.coverage.gaps)
        )
          throw Error("Run coverage differs from its report");
        const archive = fs.readFileSync(
          this.file(`data/omics/releases/${run.baseline_release_id}.json`),
        );
        if (digest(archive) !== run.baseline_manifest_sha256)
          throw Error("Run baseline changed");
      }
    const generatedAt = [
      schedule.configured_at,
      ...runs.map((r) => r.finished_at ?? r.started_at),
      ...updates.map((u) => u.published_at),
    ]
      .sort((a, b) => Date.parse(a) - Date.parse(b))
      .at(-1)!;
    return {
      schema_version: "1.0",
      generated_at: generatedAt,
      schedule: {
        status: schedule.status,
        timezone: schedule.timezone,
        description: schedule.description,
        next_due_at: nextDue,
        maintainer: schedule.maintainer,
      },
      runs: runs.map((r) => ({
        id: r.id,
        cycle_id: r.cycle_id,
        attempt: r.attempt,
        status: r.status,
        started_at: r.started_at,
        finished_at: r.finished_at,
        baseline_release_id: r.baseline_release_id,
        outcome: r.outcome,
        coverage: r.coverage,
        counts: r.counts,
        report_url: null,
        pr_url:
          this.link(r.id) ??
          runs
            .filter((other) => other.cycle_id === r.cycle_id)
            .map((other) => this.link(other.id))
            .find(Boolean) ??
          null,
      })),
      updates: updates
        .sort(
          (a, b) =>
            a.published_at.localeCompare(b.published_at) ||
            a.release_id.localeCompare(b.release_id),
        )
        .map(({ proof_sha256, ...u }) => ({
          ...u,
          receipt_url: `https://benchmarks.rewirebio.io/omics/publication-proofs/${proof_sha256}.json`,
        })),
    };
  }
  status() {
    const data = this.publicData(),
      alerts: string[] = [];
    if (
      data.schedule.status === "active" &&
      new Date(this.now()) > new Date(data.schedule.next_due_at)
    )
      alerts.push("Monthly refresh is overdue");
    for (const r of data.runs)
      if (
        ["failed", "blocked"].includes(r.status) &&
        !data.runs.some(
          (n) => n.cycle_id === r.cycle_id && n.attempt > r.attempt,
        )
      )
        alerts.push(`${r.cycle_id}: ${r.status}`);
    for (const r of this.runs())
      if (
        r.status === "running" &&
        new Date(this.now()).getTime() - new Date(r.started_at).getTime() >
          r.limits.max_minutes * 60000
      )
        alerts.push(
          `${r.cycle_id}: runtime limit exceeded; resume and record unfinished coverage`,
        );
    return { ...data, alerts };
  }
}
