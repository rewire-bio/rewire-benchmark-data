import { afterEach, beforeEach, describe, expect, it } from "vitest";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { RefreshStore, digest } from "../scripts/refresh/store";

const repository = process.cwd();
const baseline = "2026-09-30-bbbbbbbbbbbb";
const requiredScope = ["genomics", "existing-sources", "use-cases"];
let root: string;
let store: RefreshStore;
let now: string;

function report(scope: string[], artifacts: Record<string, string> = {}) {
  return {
    summary: "Synthetic bounded source review",
    coverage: { checked_ids: scope, gaps: [] },
    checks: scope.map((scope_id) => ({
      scope_id,
      query: "Inspect the pinned source for changes",
      checked_at: now,
      url: "https://example.org/source",
      decision: "unchanged",
      reason: "Fixture evidence contains no candidate change",
      record_ids: [],
    })),
    use_case_review: {
      reviewed_ids: ["case-a"],
      fingerprint_policy: "preserved",
      review_receipt: null,
    },
    limitations: ["Synthetic test evidence, not a real source sweep"],
    artifact_sha256: artifacts,
  };
}

beforeEach(() => {
  root = fs.mkdtempSync(path.join(os.tmpdir(), "refresh-additional-"));
  now = "2026-10-01T08:00:00.000Z";
  store = new RefreshStore(root, () => now);
  store.write("maintenance/schedule.json", {
    status: "active",
    timezone: "Europe/London",
    description: "First day of each month at 09:00 Europe/London",
    configured_at: "2026-09-01T08:00:00.000Z",
    next_due_at: "2026-09-01T08:00:00.000Z",
    maintainer: "test-operator",
    scientific_reviewer: null,
    overlap_days: 14,
    max_attempts: 3,
    max_minutes: 120,
    max_queries: 60,
    required_scope: requiredScope,
  });
  store.write(`data/omics/releases/${baseline}.json`, {
    release_id: baseline,
  });
  store.write("data/omics/use-cases/inputs.json", {
    use_cases: [{ id: "case-a" }],
  });
});

afterEach(() => fs.rmSync(root, { recursive: true, force: true }));

describe("refresh scope amendments and retained evidence", () => {
  it("expands a blocked pilot explicitly while retaining its frozen window and receipt", () => {
    const pilot = store.begin("2026-10", ["genomics"], baseline);
    store.write("maintenance/report.json", report(["genomics"]));
    store.finish(pilot.id, "maintenance/report.json", "blocked");
    const firstReceipt = fs.readFileSync(
      store.file(`maintenance/runs/${pilot.id}.json`),
    );

    now = "2026-10-02T08:00:00.000Z";
    const reason = "Expand the bounded pilot to every required monthly scope";
    const retry = store.begin(
      "2026-10",
      requiredScope,
      baseline,
      pilot.id,
      reason,
    );
    expect(retry.window).toEqual(pilot.window);
    expect(retry.baseline_manifest_sha256).toBe(pilot.baseline_manifest_sha256);
    expect(retry.required_scope).toEqual(pilot.required_scope);
    expect(retry.scope_amendment).toBe(reason);
    expect(retry.attempt).toBe(2);
    expect(retry.retry_of).toBe(pilot.id);

    store.write("maintenance/report.json", report(requiredScope));
    expect(
      store.finish(retry.id, "maintenance/report.json", "completed", "no_change")
        .status,
    ).toBe("completed");
    expect(
      fs.readFileSync(store.file(`maintenance/runs/${pilot.id}.json`)),
    ).toEqual(firstReceipt);
  });

  it("rejects unexplained expansion and narrowing even with an amendment reason", () => {
    const pilot = store.begin("2026-10", ["genomics"], baseline);
    store.write("maintenance/report.json", report(["genomics"]));
    store.finish(pilot.id, "maintenance/report.json", "blocked");

    expect(() =>
      store.begin("2026-10", requiredScope, baseline, pilot.id),
    ).toThrow("explicit scope amendment");
    expect(() =>
      store.begin(
        "2026-10",
        ["existing-sources"],
        baseline,
        pilot.id,
        "Replace the original scope with a different one",
      ),
    ).toThrow("only expand");
    expect(store.runs()).toHaveLength(1);
    expect(store.get(pilot.id).status).toBe("blocked");
  });

  it("does not finish when a referenced artifact changed or disappeared", () => {
    const run = store.begin("2026-10", requiredScope, baseline);
    const artifact = "maintenance/reports/source-receipt.json";
    store.write(artifact, { revision: "reviewed" });
    const original = fs.readFileSync(store.file(artifact));
    store.write(
      "maintenance/report.json",
      report(requiredScope, { [artifact]: digest(original) }),
    );

    store.write(artifact, { revision: "modified-after-review" });
    expect(() =>
      store.finish(run.id, "maintenance/report.json", "completed", "no_change"),
    ).toThrow("Evidence artifact checksum mismatch");
    expect(store.get(run.id).status).toBe("running");
    fs.unlinkSync(store.file(artifact));
    expect(() =>
      store.finish(run.id, "maintenance/report.json", "completed", "no_change"),
    ).toThrow();
    expect(store.get(run.id).report_sha256).toBeNull();

    fs.writeFileSync(store.file(artifact), original);
    expect(
      store.finish(run.id, "maintenance/report.json", "completed", "no_change")
        .status,
    ).toBe("completed");
  });

  it("blocks export if retained evidence changes or disappears after completion", () => {
    const run = store.begin("2026-10", requiredScope, baseline);
    const artifact = "maintenance/reports/source-receipt.json";
    store.write(artifact, { revision: "reviewed" });
    const original = fs.readFileSync(store.file(artifact));
    store.write(
      "maintenance/report.json",
      report(requiredScope, { [artifact]: digest(original) }),
    );
    store.finish(run.id, "maintenance/report.json", "completed", "no_change");
    expect(store.publicData().runs[0].status).toBe("completed");

    fs.appendFileSync(store.file(artifact), " ");
    expect(() => store.publicData()).toThrow("Evidence artifact checksum mismatch");
    fs.unlinkSync(store.file(artifact));
    expect(() => store.publicData()).toThrow();
    fs.writeFileSync(store.file(artifact), original);
    expect(store.publicData().runs[0].status).toBe("completed");
  });

  it("returns actionable CLI exit code 2 for blocked and overdue maintenance", () => {
    const run = store.begin("2026-10", ["genomics"], baseline);
    store.write("maintenance/report.json", report(["genomics"]));
    store.finish(run.id, "maintenance/report.json", "blocked");
    const result = spawnSync(
      process.execPath,
      [
        path.join(repository, "node_modules/tsx/dist/cli.mjs"),
        path.join(repository, "scripts/refresh/cli.ts"),
        "check-due",
      ],
      { cwd: root, encoding: "utf8", timeout: 15_000 },
    );
    expect(result.error).toBeUndefined();
    expect(result.stderr).toBe("");
    expect(result.status).toBe(2);
    const payload = JSON.parse(result.stdout);
    expect(payload.alerts).toContain("Monthly refresh is overdue");
    expect(payload.alerts).toContain("2026-10: blocked");
    expect(store.get(run.id).status).toBe("blocked");
  });
});
