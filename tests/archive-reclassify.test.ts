/** The three rules of `npm run archive -- reclassify`.
 *
 * 1. A row only ever moves to a tier the classifier can justify from evidence.
 * 2. A human-recorded licence always beats a candidate.
 * 3. A row moving from public to restricted is reported apart and never
 *    written, because its bytes may already be a public release asset.
 *
 * Every test builds its own root: source records, a licence map, a candidates
 * file and one manifest shard. Nothing here reaches the network and nothing
 * here reads the committed store.
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createHash } from "node:crypto";
import { afterEach, describe, expect, it } from "vitest";
import { planReclassify, reclassifyObjects } from "../scripts/archive/reclassify";
import { readManifest } from "../scripts/archive/manifest";
import { canonicalLine, visibilityOf, type ArchiveTier, type ManifestRow } from "../shared/archive/schema";

const roots: string[] = [];
afterEach(() => roots.splice(0).forEach((root) => fs.rmSync(root, { recursive: true, force: true })));

const digest = (value: string) => createHash("sha256").update(value).digest("hex");

/** The map rows these tests read tiers through. One per licence string, in
 * the five-column form readLicenceMap() parses. */
const mapRows: [string, string, ArchiveTier][] = [
  ["CC BY 4.0", "cc-by", "t0-public"],
  ["CC BY-NC-ND 4.0", "cc-by-nc-nd", "t3-verbatim-nd-nc"],
  ["GPL-3.0", "copyleft-code", "t0-public"],
  ["All rights reserved", "all-rights-reserved", "t4-private"],
];

interface Row {
  key: string;
  tier: ArchiveTier;
  sources: string[];
  observed?: string | null;
  removed?: boolean;
}

/** A root with the four files reclassify reads: the source records, the
 * licence map, the candidates and one manifest shard per key. */
function fixtureRoot(input: {
  sources: { id: string; licence?: string }[];
  candidates?: { source_id: string; values: string[] }[];
  rows: Row[];
}): string {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "archive-reclassify-"));
  roots.push(root);
  fs.mkdirSync(path.join(root, "data/entities"), { recursive: true });
  fs.mkdirSync(path.join(root, "data/archive/objects"), { recursive: true });
  fs.writeFileSync(
    path.join(root, "data/entities/sources.jsonl"),
    input.sources.map((source) => JSON.stringify({ id: source.id, kind: "source", attributes: source.licence ? { licence: source.licence } : {} })).join("\n") +
      "\n",
  );
  fs.writeFileSync(
    path.join(root, "data/archive/licence-map.tsv"),
    ["licence\tfamily\ttier\tbasis\tnote", ...mapRows.map(([licence, family, tier]) => `${licence}\t${family}\t${tier}\tidentifier\t`)].join("\n") + "\n",
  );
  fs.writeFileSync(
    path.join(root, "data/archive/licence-candidates.jsonl"),
    (input.candidates ?? [])
      .map((candidate) =>
        JSON.stringify({
          schema_version: 1,
          source_id: candidate.source_id,
          // Deliberately stale. The resolver wrote these fields against the
          // map as it stood then, and reclassify must re-read the values.
          status: "unmapped",
          observed_licence: null,
          family: null,
          archive_tier: null,
          recorded_licence: null,
          recorded_tier: "t4-private",
          agreement: "no-candidate",
          unmapped_values: candidate.values,
          reason: "written before the map carried these strings",
          observations: candidate.values.map((value) => ({
            route: "github",
            endpoint: "https://api.github.com/repos/o/r/license",
            field: "license.spdx_id",
            value,
            observed_at: "2026-11-17T00:00:00Z",
          })),
        }),
      )
      .join("\n") + "\n",
  );

  const byShard = new Map<string, string[]>();
  for (const row of input.rows) {
    const full: ManifestRow = {
      sha256: row.key,
      bytes: 11,
      media_type: "application/pdf",
      layer: "exact-bytes",
      origin: "https://example.org/a.pdf",
      requested_url: null,
      first_seen_at: "2026-11-17T00:00:00Z",
      store: "local-cache",
      mirrors: [],
      visibility: visibilityOf(row.tier),
      archive_tier: row.tier,
      observed_licence: row.observed ?? null,
      exposure: "policy",
      derived_from: null,
      derivation: null,
      previous_path: null,
      source_ids: row.sources,
      ...(row.removed
        ? { removed_at: "2026-11-17T00:00:00Z", removed_reason: "rights holder request", removed_requester: "docs/reviews/2026-11-17-takedown.md" }
        : {}),
    };
    const shard = row.key[0];
    byShard.set(shard, [...(byShard.get(shard) ?? []), canonicalLine(full as unknown as Record<string, unknown>)]);
  }
  for (const [shard, lines] of byShard) fs.writeFileSync(path.join(root, `data/archive/objects/${shard}.jsonl`), lines.sort().join("\n") + "\n");
  return root;
}

describe("rule 1: a row only moves to a tier the evidence justifies", () => {
  it("moves a private row to the tier a candidate justifies and leaves an unevidenced row alone", async () => {
    const moving = digest("moving");
    const untouched = digest("untouched");
    const root = fixtureRoot({
      sources: [{ id: "has-candidate" }, { id: "knows-nothing" }],
      candidates: [{ source_id: "has-candidate", values: ["GPL-3.0"] }],
      rows: [
        { key: moving, tier: "t4-private", sources: ["has-candidate"] },
        { key: untouched, tier: "t4-private", sources: ["knows-nothing"] },
      ],
    });

    const plan = planReclassify(root);
    expect(plan.before).toMatchObject({ "t4-private": 2, "t0-public": 0 });
    expect(plan.after).toMatchObject({ "t4-private": 1, "t0-public": 1 });
    expect(plan.unevidenced).toBe(1);
    expect(plan.moves.map((move) => [move.sha256, move.from, move.to])).toEqual([[moving, "t4-private", "t0-public"]]);
    expect(plan.publishable_before).toBe(0);
    expect(plan.publishable_after).toBe(1);

    const before = readManifest(root);
    const summary = await reclassifyObjects({ root });
    expect(summary).toMatchObject({ written: 1, refused: false });

    const after = readManifest(root);
    // The row that moved moved in exactly three columns.
    expect(after.get(moving)).toEqual({
      ...before.get(moving),
      archive_tier: "t0-public",
      visibility: "public",
      observed_licence: "GPL-3.0",
    });
    // The row with no evidence is byte for byte what it was. A tier nobody
    // can justify is not a tier, so absence never moves a row.
    expect(after.get(untouched)).toEqual(before.get(untouched));
  });

  it("leaves a removed row at t5-no-store, whatever its sources now resolve to", async () => {
    const removed = digest("removed");
    const root = fixtureRoot({
      sources: [{ id: "open-source-record", licence: "CC BY 4.0" }],
      rows: [{ key: removed, tier: "t5-no-store", sources: ["open-source-record"], removed: true }],
    });
    const plan = planReclassify(root);
    expect(plan.skipped_removed).toBe(1);
    expect(plan.moves).toEqual([]);
    expect(plan.after).toMatchObject({ "t5-no-store": 1 });

    await reclassifyObjects({ root });
    const row = readManifest(root).get(removed);
    expect(row?.archive_tier).toBe("t5-no-store");
    expect(row?.removed_at).toBe("2026-11-17T00:00:00Z");
  });
});

describe("rule 2: a human-recorded licence beats a candidate", () => {
  it("takes the recorded no-derivatives licence over a candidate stating CC BY", async () => {
    const key = digest("recorded-wins");
    const root = fixtureRoot({
      sources: [{ id: "recorded", licence: "CC BY-NC-ND 4.0" }],
      candidates: [{ source_id: "recorded", values: ["CC BY 4.0"] }],
      rows: [{ key, tier: "t4-private", sources: ["recorded"] }],
    });

    const plan = planReclassify(root);
    expect(plan.moves).toHaveLength(1);
    expect(plan.moves[0].to).toBe("t3-verbatim-nd-nc");
    expect(plan.moves[0].observed_licence).toBe("CC BY-NC-ND 4.0");
    expect(plan.moves[0].evidence).toEqual(["recorded-licence"]);

    await reclassifyObjects({ root });
    const row = readManifest(root).get(key);
    expect(row?.archive_tier).toBe("t3-verbatim-nd-nc");
    expect(row?.observed_licence).toBe("CC BY-NC-ND 4.0");
  });

  it("keeps a source private when the recorded string is one the map has no row for", async () => {
    // An unmapped recorded string is a determination nobody has read yet. A
    // service's guess does not get to stand in for it, so the row stays at
    // the private default and the string stays visible on the row.
    const key = digest("recorded-unmapped");
    const root = fixtureRoot({
      sources: [{ id: "recorded", licence: "A licence nobody has mapped" }],
      candidates: [{ source_id: "recorded", values: ["CC BY 4.0"] }],
      rows: [{ key, tier: "t4-private", sources: ["recorded"] }],
    });
    const plan = planReclassify(root);
    expect(plan.moves).toEqual([]);
    expect(plan.after).toMatchObject({ "t4-private": 1 });
  });

  it("takes the most restrictive tier when several records share one object", async () => {
    const key = digest("shared");
    const root = fixtureRoot({
      sources: [{ id: "open", licence: "CC BY 4.0" }, { id: "closed", licence: "CC BY-NC-ND 4.0" }],
      rows: [{ key, tier: "t4-private", sources: ["closed", "open"] }],
    });
    expect(planReclassify(root).moves[0].to).toBe("t3-verbatim-nd-nc");
  });
});

describe("rule 3: a move from public to restricted is a takedown, not a reclassification", () => {
  it("reports the restrictive move apart and writes nothing at all", async () => {
    const restrictive = digest("restrictive");
    const safe = digest("safe");
    const root = fixtureRoot({
      sources: [{ id: "now-closed", licence: "All rights reserved" }, { id: "now-open", licence: "CC BY 4.0" }],
      rows: [
        { key: restrictive, tier: "t0-public", sources: ["now-closed"], observed: "CC BY 4.0" },
        { key: safe, tier: "t4-private", sources: ["now-open"] },
      ],
    });

    const plan = planReclassify(root);
    expect(plan.restrictive).toHaveLength(1);
    expect(plan.restrictive[0]).toMatchObject({
      sha256: restrictive,
      from: "t0-public",
      to: "t4-private",
      from_visibility: "public",
      to_visibility: "restricted",
      source_ids: ["now-closed"],
    });

    const before = readManifest(root);
    const summary = await reclassifyObjects({ root });
    // The safe move was ready to go and is held back with the rest. One
    // reading that turns out to contain a takedown wants a person before any
    // of it lands.
    expect(summary).toMatchObject({ refused: true, written: 0 });
    expect(readManifest(root)).toEqual(before);
  });

  it("lists a tighter move that stays public apart from a takedown, and lets it through", async () => {
    // t0-public to t3-verbatim-nd-nc is more restrictive but still
    // publishable, so it is not a takedown and does not block the run. The
    // bytes may already be a release asset carrying the old tier, which is
    // why it is listed rather than left as a count.
    const key = digest("tighter");
    const root = fixtureRoot({
      sources: [{ id: "now-nd", licence: "CC BY-NC-ND 4.0" }],
      rows: [{ key, tier: "t0-public", sources: ["now-nd"], observed: "CC BY 4.0" }],
    });

    const plan = planReclassify(root);
    expect(plan.restrictive).toEqual([]);
    expect(plan.tightening).toHaveLength(1);
    expect(plan.tightening[0]).toMatchObject({ from: "t0-public", to: "t3-verbatim-nd-nc", to_visibility: "public" });

    const summary = await reclassifyObjects({ root });
    expect(summary).toMatchObject({ refused: false, written: 1 });
    expect(readManifest(root).get(key)?.archive_tier).toBe("t3-verbatim-nd-nc");
  });

  it("writes nothing on a dry run and reports the same plan the real run would apply", async () => {
    const key = digest("dry");
    const root = fixtureRoot({
      sources: [{ id: "open", licence: "CC BY 4.0" }],
      rows: [{ key, tier: "t4-private", sources: ["open"] }],
    });
    const before = readManifest(root);
    const dry = await reclassifyObjects({ root, dryRun: true });
    expect(dry).toMatchObject({ dry_run: true, written: 0, refused: false });
    expect(dry.moves).toHaveLength(1);
    expect(readManifest(root)).toEqual(before);

    const real = await reclassifyObjects({ root });
    expect(real.moves).toEqual(dry.moves);
    expect(real.written).toBe(1);
  });
});
