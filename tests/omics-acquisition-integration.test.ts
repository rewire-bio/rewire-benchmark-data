import fs from "node:fs";
import { migrated } from "./helpers/vocab";
import { describe, it, expect } from "vitest";
import { batchRecords } from "./helpers/records";
import { profileSchema } from "../shared/omics/profile-schema";
import type { RecordEntry } from "../scripts/omics/schema";
const root = "data/omics/acquisition/2026-09-19";
const read = (name: string): any[] =>
  fs
    .readFileSync(`${root}/${name}`, "utf8")
    .trim()
    .split("\n")
    .filter(Boolean)
    .map((l) => JSON.parse(l));
const candidates = [
  ...read("proteins/candidates.jsonl"),
  ...read("challenges/candidates.jsonl"),
  ...read("cells-networks/candidates.jsonl"),
];
const byCandidate = new Map(candidates.map((c) => [c.candidate_id, c]));
const records: any[] = batchRecords(`${root}/reviewed-records.jsonl`);
const byId = new Map(records.map((r) => [r.id, r]));
const results = records.filter((r) => r.kind === "result");
const protocols = records.filter((r) => r.kind === "protocol");
const evalFor = (r: any) =>
  byId.get(r.links.find((l: any) => l.relation === "evaluation").target_id)!;
const protocolFor = (r: any) =>
  byId.get(
    evalFor(r).links.find((l: any) => l.relation === "assessment").target_id,
  )!;
const candidateFor = (r: any) =>
  byCandidate.get(r.attributes.acquisition_candidate_id)!;
describe("reviewed acquisition graph and scientific scope", () => {
  it("does not promote incomplete scientific metadata using numerical transcription checks", () => {
    for (const r of records.filter((r) =>
      ["configuration", "protocol", "dataset_subset", "evaluation"].includes(
        r.kind,
      ),
    ))
      expect(r.status, r.id).toBe("discovered");
    for (const r of results) expect(r.status).toBe("source_checked");
  });
  it("preserves every accepted source string, unit, metric, uncertainty and reciprocal evaluation link", () => {
    const decisions = read("integration-decisions.jsonl");
    expect(results.length).toBe(decisions.filter((d) => d.accepted).length);
    for (const r of results) {
      const c = candidateFor(r);
      expect(r.attributes.printed_value, r.id).toBe(c.printed_value);
      expect(Number(r.attributes.numeric_value), r.id).toBe(c.numeric_value);
      // Units and metrics are concept keys now; the batch keeps the source wording.
      expect(r.attributes.metric, r.id).toBe(migrated("metric", c.metric));
      expect(r.attributes.unit, r.id).toBe(migrated("unit", c.unit));
      expect(r.attributes.uncertainty, r.id).toEqual(c.uncertainty);
      expect(evalFor(r).kind).toBe("evaluation");
      expect(protocolFor(r).links).toContainEqual({
        relation: "part_of",
        target_id: c.benchmark_id,
      });
    }
  });
  it("keeps BEELINE reference networks and gene selections in separate protocol strata", () => {
    const groups = new Map<string, Set<string>>();
    for (const r of results) {
      const c = candidateFor(r);
      if (!c.benchmark_id.includes("beeline")) continue;
      const id = protocolFor(r).id;
      const set = groups.get(id) || new Set();
      set.add(
        JSON.stringify([
          c.dataset,
          c.conditions.reference_network,
          c.conditions.gene_selection,
        ]),
      );
      groups.set(id, set);
    }
    expect(groups.size).toBeGreaterThan(17);
    for (const scopes of groups.values()) expect(scopes.size).toBe(1);
  });
  it("retains every provisional VCC submission exactly once across bounded source-order panels", () => {
    const rs = results.filter((r) =>
      candidateFor(r).benchmark_id.includes("virtual-cell"),
    );
    expect(rs).toHaveLength(1048);
    const panels = protocols
      .filter((p) =>
        p.links.some((l: any) => l.target_id.includes("virtual-cell")),
      )
      .flatMap((p) => p.attributes.comparison_panels);
    const ids = panels.flatMap((p: any) => p.result_ids);
    expect(new Set(ids).size).toBe(rs.length);
    expect(ids.length).toBe(rs.length);
    expect(panels.every((p: any) => p.result_ids.length <= 80)).toBe(true);
    for (const r of rs) {
      const e = evalFor(r);
      expect(e.attributes.conditions.is_final).toBe(false);
      expect(e.attributes.conditions.anchor_version).toBe(
        "vcc2026-valA-r4+vcc2026-valB-r4+vcc2026-valC-r4",
      );
      expect(e.attributes.conditions.submission_id).toBe(
        candidateFor(r).conditions.submission_id,
      );
    }
  });
  it("does not compare Vina's ground-truth pocket or DiffDock's rigid receptor with co-folding inputs", () => {
    const protocolsByMethod = new Map<string, Set<string>>();
    for (const r of results) {
      const c = candidateFor(r);
      if (!c.benchmark_id.includes("plinder")) continue;
      const s = protocolsByMethod.get(c.model_or_submission) || new Set();
      s.add(protocolFor(r).id);
      protocolsByMethod.set(c.model_or_submission, s);
    }
    const vina = [...protocolsByMethod.get("Vina")!][0],
      diff = [...protocolsByMethod.get("DiffDock")!][0],
      af = [...protocolsByMethod.get("AF3")!][0];
    expect(vina).not.toBe(diff);
    expect(vina).not.toBe(af);
    expect(diff).not.toBe(af);
  });
  it("preserves per-metric aggregation when several metric rows share one evaluation", () => {
    for (const r of results) {
      const c = candidateFor(r);
      if (!c.benchmark_id.includes("plinder")) continue;
      const aggregation =
        r.attributes.reported_conditions?.aggregation ??
        r.attributes.conditions?.aggregation ??
        r.attributes.aggregation ??
        evalFor(r).attributes.conditions.aggregation;
      expect(aggregation, `${c.model_or_submission}/${c.metric}`).toBe(
        c.conditions.aggregation,
      );
    }
  });
  it("retains CAFA anonymous identities and unresolved mode semantics without invented model-family links", () => {
    const rs = results.filter((r) =>
      candidateFor(r).benchmark_id.includes("cafa"),
    );
    expect(rs).toHaveLength(438);
    for (const r of rs) {
      const e = evalFor(r);
      expect(e.attributes.conditions.evaluation_mode).toContain(
        "not established",
      );
      const m = byId.get(
        e.links.find((l: any) => l.relation === "system").target_id,
      )!;
      expect(m.name).toMatch(/^CAFA3 /);
      expect(m.links).toEqual([]);
      expect(m.attributes.missing_metadata.model_family).toBe("unextracted");
    }
  });
  it("preserves CAMI gold-standard reference identity and explicitly reported standard errors", () => {
    const rs = results.filter((r) =>
      candidateFor(r).benchmark_id.includes("cami"),
    );
    const refs = rs.filter(
      (r) => candidateFor(r).model_or_submission === "Gold standard",
    );
    expect(refs).toHaveLength(16);
    for (const r of refs)
      expect(evalFor(r).attributes.conditions.gold_standard_reference).toBe(
        true,
      );
    const means = rs.filter((r) => candidateFor(r).metric.startsWith("Average "));
    expect(means).toHaveLength(64);
    for (const r of means) {
      expect(r.attributes.uncertainty.kind).toBe("standard_error");
      expect(r.attributes.uncertainty.source_column).toContain(
        "Std error of av.",
      );
    }
  });
  it("keeps scIB feature/scaling configurations distinct without merging separate evaluated configurations", () => {
    const seen = new Map<string, Set<string>>();
    for (const r of results) {
      const c = candidateFor(r);
      if (!c.benchmark_id.includes("scib")) continue;
      const e = evalFor(r);
      const key = JSON.stringify([
        c.model_or_submission,
        c.conditions.features,
        c.conditions.scaling,
        c.conditions.configuration,
      ]);
      const s = seen.get(e.id) || new Set();
      s.add(key);
      seen.set(e.id, s);
    }
    for (const values of seen.values()) expect(values.size).toBe(1);
  });
  it("does not publish unresolved PEtab timings, conflicting FLIP2 values or missing numerical cells", () => {
    for (const r of results) {
      const c = candidateFor(r);
      expect(c.benchmark_id).not.toContain("petab");
      expect(c.numeric_value).not.toBeNull();
      expect(c.publication_eligibility).not.toBe("quarantined_source_conflict");
    }
  });
  it("binds provenance hashes to the actual XML artifact and CAFA archive member", () => {
    for (const r of results) {
      const c = candidateFor(r);
      const source = byId.get(r.source_ids[0]);
      if (!source) continue;
      if (c.artifact_url)
        expect(source.attributes.artifact_url).toBe(c.artifact_url);
      if (c.benchmark_id.includes("cafa")) {
        expect(source.attributes.hash_scope).toMatch(/member/i);
        expect(source.attributes.archive_sha256).toMatch(/^[a-f0-9]{64}$/);
        expect(source.attributes.artifact_member).toContain("_fmax_sheet.csv");
      }
    }
  });
});
