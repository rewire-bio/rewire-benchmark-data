import { beforeEach, afterEach, describe, expect, it } from "vitest";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { RefreshStore, nextMonthly, digest } from "../scripts/refresh/store";
const writeUseCases = (cases: object[]) => {
  const file = store.file("data/entities/use-cases.jsonl");
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, cases.map((c) => JSON.stringify(c) + "\n").join(""));
};

let root: string, store: RefreshStore, now: string;
const baseline = "2026-09-30-aaaaaaaaaaaa";
const scope = ["genomics", "existing-sources", "use-cases"];
function report() {
  return {
    summary: "Bounded fixture sweep",
    coverage: { checked_ids: scope, gaps: [] as string[] },
    checks: scope.map((scope_id) => ({
      scope_id,
      query: "Inspect primary source",
      checked_at: now,
      url: "https://example.org/source",
      decision: "unchanged",
      reason: "No eligible changes in the declared scope",
      record_ids: [],
    })),
    use_case_review: {
      reviewed_ids: ["case-a"],
      fingerprint_policy: "preserved",
      review_receipt: null,
    },
    limitations: ["Synthetic test evidence"],
  };
}
function begin() {
  return store.begin("2026-10", scope, baseline);
}
function finish(
  runId: string,
  r = report(),
  status: "completed" | "blocked" | "failed" = "completed",
  outcome: "no_change" | "review_required" | undefined = status === "completed"
    ? "no_change"
    : undefined,
) {
  store.write("maintenance/test-report.json", r);
  return store.finish(runId, "maintenance/test-report.json", status, outcome);
}
beforeEach(() => {
  root = fs.mkdtempSync(path.join(os.tmpdir(), "refresh-"));
  now = "2026-10-01T08:00:00.000Z";
  store = new RefreshStore(root, () => now);
  store.write("maintenance/schedule.json", {
    status: "active",
    timezone: "Europe/London",
    description: "Monthly first day, 09:00 London",
    configured_at: now,
    next_due_at: now,
    maintainer: "operator",
    scientific_reviewer: null,
    overlap_days: 14,
    max_attempts: 3,
    max_minutes: 120,
    max_queries: 60,
    required_scope: scope,
  });
  store.write(`data/omics/releases/${baseline}.json`, { release_id: baseline });
  writeUseCases([{ id: "case-a" }]);
});
afterEach(() => fs.rmSync(root, { recursive: true, force: true }));
describe("durable refresh lifecycle", () => {
  it("resumes without replacing the running receipt and rejects concurrent work", () => {
    const r = begin();
    expect(store.get(r.id)).toEqual(r);
    expect(() => begin()).toThrow("running");
    expect(store.runs()).toHaveLength(1);
  });
  it("keeps completed no-change sweeps distinct from publication/release creation", () => {
    const r = begin();
    now = "2026-10-01T08:05:00.000Z";
    finish(r.id);
    const data = store.publicData();
    expect(data.updates).toEqual([]);
    expect(data.runs[0].outcome).toBe("no_change");
    expect(data.schedule.next_due_at).toBe("2026-11-01T09:00:00.000Z");
    expect(fs.readdirSync(store.file("data/omics/releases"))).toHaveLength(1);
    expect(() => finish(r.id)).toThrow("immutable");
    expect(() => begin()).toThrow("completed");
  });
  it("rejects partial coverage completion and preserves failed attempts across explicit retry", () => {
    const r = begin();
    const reportData = report();
    reportData.coverage.gaps = ["Missing source"];
    expect(() => finish(r.id, reportData)).toThrow("Incomplete");
    finish(r.id, reportData, "blocked", undefined);
    expect(store.publicData().schedule.next_due_at).toBe(now);
    expect(() => begin()).toThrow("explicitly");
    now = "2026-10-02T08:00:00.000Z";
    const next = store.begin("2026-10", scope, baseline, r.id);
    expect(next.window).toEqual(r.window);
    expect(next.attempt).toBe(2);
    expect(store.get(r.id).status).toBe("blocked");
  });
  it("requires every configured scope and every use case", () => {
    const r = begin();
    const incomplete = report();
    incomplete.use_case_review.reviewed_ids = [];
    expect(() => finish(r.id, incomplete)).toThrow("Every use case");
    incomplete.use_case_review.reviewed_ids = ["case-a"];
    incomplete.coverage.checked_ids = ["genomics"];
    expect(() => finish(r.id, incomplete)).toThrow("Incomplete");
  });
  it("rejects a purported checked scope with no evidence and future retrievals", () => {
    const r = begin(),
      data = report();
    data.checks = [];
    expect(() => finish(r.id, data)).toThrow("lacks evidence");
    data.checks = report().checks;
    data.checks[0].checked_at = "2026-10-02T00:00:00Z";
    expect(() => finish(r.id, data)).toThrow("retrieval time");
  });
  it("cannot clear stale fingerprints by changing use-case bytes", () => {
    const r = begin();
    writeUseCases([{ id: "case-a", hash: "regenerated" }]);
    expect(() => finish(r.id)).toThrow("without explicit review");
  });
  it("rejects false no-change outcomes", () => {
    const r = begin(),
      data = report();
    data.checks[0].decision = "included";
    expect(() => finish(r.id, data)).toThrow("Outcome");
    finish(r.id, data, "completed", "review_required");
    expect(store.publicData().runs[0].counts.added).toBe(1);
  });
  it("enforces effort limits and makes an exceeded running limit actionable", () => {
    const r = begin();
    now = "2026-10-01T11:00:00.000Z";
    expect(store.status().alerts.join()).toContain("runtime limit");
    expect(() => finish(r.id)).toThrow("Effort");
    finish(r.id, report(), "failed", undefined);
    expect(store.status().alerts.join()).toContain("failed");
  });
  it("enforces attempt limit", () => {
    let r = begin();
    for (let n = 0; n < 3; n++) {
      finish(r.id, report(), "failed", undefined);
      if (n < 2) r = store.begin("2026-10", scope, baseline, r.id);
    }
    expect(() => store.begin("2026-10", scope, baseline, r.id)).toThrow(
      "Attempt limit",
    );
  });
  it("prevents duplicate cycle PRs and directs retries to existing review", () => {
    const r = begin();
    finish(r.id, report(), "blocked", undefined);
    store.linkPr(
      r.id,
      "https://github.com/rewire-bio/rewire-benchmark-data/pull/1",
    );
    store.linkPr(
      r.id,
      "https://github.com/rewire-bio/rewire-benchmark-data/pull/1",
    );
    expect(() =>
      store.linkPr(
        r.id,
        "https://github.com/rewire-bio/rewire-benchmark-data/pull/2",
      ),
    ).toThrow("another PR");
    const retry = store.begin("2026-10", scope, baseline, r.id);
    expect(
      store.publicData().runs.find((run) => run.id === retry.id)?.pr_url,
    ).toBe("https://github.com/rewire-bio/rewire-benchmark-data/pull/1");
  });
  it("detects tampered or missing report bytes", () => {
    const r = begin();
    const done = finish(r.id);
    const p = store.file(
      `maintenance/reports/${r.id}/${done.report_sha256}.json`,
    );
    fs.appendFileSync(p, " ");
    expect(() => store.publicData()).toThrow("checksum");
    fs.unlinkSync(p);
    expect(() => store.publicData()).toThrow();
  });
  it("reports missed due dates at observation time", () => {
    now = "2026-10-02T08:00:00.000Z";
    expect(store.status().alerts).toContain("Monthly refresh is overdue");
  });
  it("keeps corrections from advancing monthly due dates or coverage windows", () => {
    const r = store.begin(
      "correction-2026-10-01-source",
      ["genomics"],
      baseline,
    );
    const data = report();
    data.coverage.checked_ids = ["genomics"];
    data.checks = data.checks.slice(0, 1);
    finish(r.id, data);
    expect(store.publicData().schedule.next_due_at).toBe(now);
    const monthly = begin();
    expect(monthly.window.from).toBe("2026-08-17T08:00:00.000Z");
  });
  it("produces deterministic exports while current time changes", () => {
    const r = begin();
    finish(r.id);
    const first = store.publicData();
    now = "2026-10-02T08:00:00.000Z";
    expect(store.publicData()).toEqual(first);
  });

  it("delayed retries remain overdue for the next uncovered monthly cycle", () => {
    const original = begin();
    finish(original.id, report(), "blocked", undefined);
    now = "2026-11-05T08:00:00.000Z";
    const retry = store.begin("2026-10", scope, baseline, original.id);
    finish(retry.id);
    expect(store.publicData().schedule.next_due_at).toBe(
      "2026-11-01T09:00:00.000Z",
    );
    expect(store.status().alerts).toContain("Monthly refresh is overdue");
  });
  it("rejects arbitrary files as re-review receipts", () => {
    const run = begin(),
      data = report();
    data.use_case_review.fingerprint_policy = "explicitly_reviewed";
    Object.assign(data.use_case_review, {
      review_receipt: "maintenance/schedule.json",
    });
    expect(() => finish(run.id, data)).toThrow(
      "native use-case review receipt",
    );
  });
  it("captures all source/receipt bytes, not just mapping fingerprints", () => {
    store.write("data/omics/use-cases/sources.json", { source: "before" });
    const run = begin();
    store.write("data/omics/use-cases/sources.json", { source: "after" });
    expect(() => finish(run.id)).toThrow("without explicit review");
  });
  it("rejects deleted or tampered publication proof", () => {
    const manifestSha = digest(
        fs.readFileSync(store.file(`data/omics/releases/${baseline}.json`)),
      ),
      commit = "a".repeat(40);
    const proof = {
      observed_at: now,
      deployment: {
        release_id: baseline,
        commit,
        manifest_sha256: manifestSha,
      },
      manifest_sha256: manifestSha,
    };
    const proofBytes = JSON.stringify(proof, null, 2) + "\n",
      proofSha = digest(proofBytes);
    store.write(`maintenance/publication-proofs/${proofSha}.json`, proof);
    store.write(`maintenance/updates/${baseline}.json`, {
      release_id: baseline,
      manifest_sha256: manifestSha,
      commit,
      published_at: now,
      time_basis: "observed",
      maintenance_run_id: null,
      summary: ["Initial observed release"],
      links: [],
      receipt_url: "https://rewire-it.web.app/deployment.json",
      proof_sha256: proofSha,
    });
    expect(store.publicData().updates).toHaveLength(1);
    fs.appendFileSync(
      store.file(`maintenance/publication-proofs/${proofSha}.json`),
      " ",
    );
    expect(() => store.publicData()).toThrow("proof checksum");
    fs.unlinkSync(
      store.file(`maintenance/publication-proofs/${proofSha}.json`),
    );
    expect(() => store.publicData()).toThrow();
  });
  it("rejects path traversal and live-lock recovery", () => {
    expect(() => store.get("../escape")).toThrow();
    expect(() => store.file("../escape")).toThrow();
    store.locked(() =>
      expect(() => store.unlock("manual recovery")).toThrow("still running"),
    );
  });
});
it("London calendar stays at 09:00 across DST changes", () => {
  expect(nextMonthly("2026-03-02T00:00:00Z")).toBe("2026-04-01T08:00:00.000Z");
  expect(nextMonthly("2026-10-02T00:00:00Z")).toBe("2026-11-01T09:00:00.000Z");
});
