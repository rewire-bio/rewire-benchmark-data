/** The layer registry, its sanity gate and the coverage identity.
 *
 * Four things are asserted here, each one a property ADR 0002 step 4 names.
 *
 * 1. Regenerating the registry over an unchanged store produces the same
 *    bytes. The full version of that is `npm run layers -- check`, which
 *    re-derives all 1,167 objects and takes minutes because 201 of them go
 *    through pdftotext. This file asserts the two halves that can be checked
 *    quickly: the committed file is exactly what the serialiser writes from
 *    its own contents, and a fixed sample of objects covering every
 *    normaliser re-derives to the committed rows byte for byte.
 * 2. The sanity gate fails the bacformer version 2 rendering ADR 0002 names
 *    and passes version 3, whose layer the archive holds.
 * 3. Coverage balances: every source is in exactly one bucket and the
 *    buckets sum to the store's source count.
 * 4. A span slices the characters it names, in code points, with the byte
 *    offsets beside them.
 *
 * Every test here is offline and calls no model. Those that need the object
 * cache skip when it is not on this machine, because the cache is
 * gitignored by design and a clone does not carry it.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { readManifest } from "../scripts/archive/manifest";
import { hasObject, readObject } from "../scripts/archive/objects";
import { latestBySource, readReceipts } from "../scripts/archive/receipts";
import {
  coverageOf,
  layersOfObject,
  metricsOf,
  ratiosOf,
  readRegistry,
  readUnsupported,
  registryPath,
  sanityOf,
  serialiseRegistry,
  sliceSpan,
  thresholds,
  type LayerRecord,
  type ReceiptFact,
} from "../shared/omics/layers/index";
import { coverageBuckets } from "../shared/omics/layers/types";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const registry = readRegistry(root);
const cached = (sha256: string): boolean => hasObject(sha256, root);

/** Two rows per normaliser, one derived straight from a stored object and
 * one from inside a container, taken in layer-hash order. The sample is
 * chosen from the registry rather than pinned, so it follows the store: a
 * new object with a lower hash changes which rows are checked and does not
 * change what is being checked, which is that every normaliser re-derives.
 * The normaliser list is read off the registry too, so a normaliser the
 * archive lane adds is covered the moment its first layer is committed. */
function sample(): LayerRecord[] {
  const wanted = [...new Set(registry.map((record) => record.normaliser))].sort();
  const picked: LayerRecord[] = [];
  for (const normaliser of wanted) {
    const byNormaliser = registry.filter((record) => record.normaliser === normaliser).sort((a, b) => (a.layer_sha256 < b.layer_sha256 ? -1 : 1));
    const direct = byNormaliser.find((record) => record.container_path === null);
    const inContainer = byNormaliser.find((record) => record.container_path !== null);
    for (const record of [direct, inContainer]) if (record) picked.push(record);
  }
  return picked;
}

describe("the registry is generated and regenerating it changes nothing", () => {
  it("is committed in exactly the form the serialiser writes", () => {
    expect(fs.existsSync(registryPath(root)), "the registry is committed").toBe(true);
    expect(serialiseRegistry(registry)).toBe(fs.readFileSync(registryPath(root), "utf8"));
  });

  it("holds one row per layer per object it is reachable from, and no duplicate", () => {
    const keys = registry.map((record) => `${record.layer_sha256} ${record.object_sha256} ${record.container_path ?? ""}`);
    expect(new Set(keys).size).toBe(keys.length);
  });

  it("names only objects the manifest holds, with the manifest's own source ids", () => {
    const manifest = readManifest(root);
    const wrong = registry.filter((record) => {
      const row = manifest.get(record.object_sha256);
      return !row || JSON.stringify([...row.source_ids].sort()) !== JSON.stringify(record.source_ids);
    });
    expect(wrong.map((record) => record.object_sha256)).toEqual([]);
  });

  it("re-derives a sample of objects to the committed rows, byte for byte", () => {
    const manifest = readManifest(root);
    const picked = sample();
    expect(picked.length).toBeGreaterThan(3);
    const checked = new Set<string>();
    for (const record of picked) {
      if (!cached(record.object_sha256)) continue;
      const row = manifest.get(record.object_sha256);
      expect(row, `${record.object_sha256} is in the manifest`).toBeTruthy();
      const again = layersOfObject(row as never, readObject(record.object_sha256, root));
      const match = again.records.find(
        (candidate) => candidate.layer_sha256 === record.layer_sha256 && candidate.container_path === record.container_path,
      );
      expect(match, `${record.layer_sha256} re-derives from ${record.object_sha256}`).toBeTruthy();
      expect(serialiseRegistry([match as LayerRecord])).toBe(serialiseRegistry([record]));
      checked.add(record.normaliser);
    }
    // The cache is gitignored, so a clone has none of it and the sample
    // checks nothing. On a machine that holds the objects every normaliser
    // in the sample has to have been re-derived.
    if (picked.some((record) => cached(record.object_sha256)))
      expect([...checked].sort()).toEqual([...new Set(picked.map((record) => record.normaliser))].sort());
  });
});

describe("the sanity gate", () => {
  /** The bacformer version 2 rendering ADR 0002 requires to come out fail:
   * a font mapping that printed 0.81 +/- 0.07 as +.)! +.+(, so the numbers
   * became punctuation. */
  const mojibake = "+.)! +.+( +.($ +.!& +.,# +.*% ".repeat(60);

  it("fails the bacformer version 2 rendering", () => {
    const sanity = sanityOf(metricsOf(mojibake), "pdf-text-layer@1");
    expect(sanity.verdict).toBe("fail");
    expect(sanity.reasons.join(" ")).toContain("punctuation");
  });

  it("passes the bacformer version 3 layer the archive holds", () => {
    const record = registry.find((candidate) => candidate.layer_sha256.startsWith("86636e89b167d7304b3a83ee"));
    expect(record, "the bacformer version 3 layer is in the registry").toBeTruthy();
    expect((record as LayerRecord).sanity).toBe("pass");
    expect((record as LayerRecord).metrics.page_breaks).toBe((record as LayerRecord).metrics.pdf_pages);
  });

  it("fails a layer with no content", () => {
    expect(sanityOf(metricsOf("\f\f\f"), "pdf-text-layer@1").verdict).toBe("fail");
    expect(sanityOf(metricsOf(""), "html-text@1").verdict).toBe("fail");
  });

  it("fails a PDF layer whose page breaks do not match pdfinfo", () => {
    const text = `${"page one text ".repeat(20)}\f${"page two text ".repeat(20)}\f`;
    expect(sanityOf(metricsOf(text, 2), "pdf-text-layer@1").verdict).toBe("pass");
    expect(sanityOf(metricsOf(text, 3), "pdf-text-layer@1").verdict).toBe("fail");
  });

  it("does not apply the page-break rule to a normaliser that is not the PDF one", () => {
    const text = "a paragraph with no page break in it at all, repeated. ".repeat(20);
    expect(sanityOf(metricsOf(text, 7), "html-text@1").verdict).toBe("pass");
  });

  it("refuses no layer in the store on the printable, replacement or mojibake thresholds", () => {
    // The rule the thresholds were set by: a fail threshold cuts none of the
    // real work. The only fails in the store are empty layers.
    const fails = registry.filter((record) => record.sanity === "fail");
    const notEmpty = fails.filter((record) => record.metrics.non_space > 0);
    expect(notEmpty.map((record) => record.layer_sha256)).toEqual([]);
  });

  it("keeps every measured layer inside the distributions the thresholds were set from", () => {
    const withContent = registry.filter((record) => record.metrics.non_space > 0);
    const worstPrintable = Math.min(...withContent.map((record) => ratiosOf(record.metrics).printable));
    const worstReplacement = Math.max(...registry.map((record) => ratiosOf(record.metrics).replacement));
    expect(worstPrintable).toBeGreaterThan(thresholds.printableFail);
    expect(worstReplacement).toBeLessThan(thresholds.replacementFail);
  });

  it("counts characters in code points, not UTF-16 units", () => {
    const metrics = metricsOf("a\u{1F9EC}b");
    expect(metrics.characters).toBe(3);
    expect("a\u{1F9EC}b".length).toBe(4);
  });
});

describe("coverage balances", () => {
  const sourceIds = fs
    .readFileSync(path.join(root, "data/entities/sources.jsonl"), "utf8")
    .split("\n")
    .filter((line) => line.trim())
    .map((line) => (JSON.parse(line) as { id: string }).id);

  const receipts = new Map<string, ReceiptFact>();
  for (const [sourceId, receipt] of latestBySource(readReceipts(root)))
    receipts.set(sourceId, {
      source_id: sourceId,
      outcome: receipt.outcome,
      sha256: receipt.sha256,
      reason: receipt.reason,
      source_class: receipt.source_class,
    });

  const result = coverageOf(sourceIds, receipts, registry, readUnsupported(root));

  it("puts every source in exactly one bucket and the buckets sum to the store", () => {
    expect(result.problems).toEqual([]);
    const sum = coverageBuckets.reduce((total, bucket) => total + result.tally.buckets[bucket], 0);
    expect(sum).toBe(sourceIds.length);
    expect(result.rows.length).toBe(sourceIds.length);
    expect(new Set(result.rows.map((row) => row.source_id)).size).toBe(sourceIds.length);
  });

  it("counts characters only where a layer is usable", () => {
    const counted = result.rows.filter((row) => row.characters > 0);
    expect(counted.every((row) => row.bucket === "layer_pass" || row.bucket === "layer_suspect")).toBe(true);
    const unusable = result.rows.filter((row) => !["layer_pass", "layer_suspect"].includes(row.bucket));
    expect(unusable.every((row) => row.characters === 0)).toBe(true);
    expect(result.tally.characters).toBe(result.rows.reduce((total, row) => total + row.characters, 0));
  });

  it("separates the text that exists from the reading a source does", () => {
    // A layer cited by two sources is read twice and exists once, so the
    // per-source sum is the larger of the two and neither stands alone.
    const distinct = new Map<string, number>();
    for (const row of result.rows) if (row.layer_sha256 && row.characters > 0) distinct.set(row.layer_sha256, row.characters);
    const sum = [...distinct.values()].reduce((total, value) => total + value, 0);
    expect(result.tally.distinct_layers).toBe(distinct.size);
    expect(result.tally.distinct_characters).toBe(sum);
    expect(result.tally.distinct_characters).toBeLessThanOrEqual(result.tally.characters);
  });

  it("gives every source outside the usable buckets a reason", () => {
    const unusable = result.rows.filter((row) => !["layer_pass", "layer_suspect"].includes(row.bucket));
    expect(unusable.filter((row) => !row.detail.trim()).map((row) => row.source_id)).toEqual([]);
  });

  it("puts a failing layer in the failing bucket", () => {
    const failing: LayerRecord = {
      ...registry[0],
      layer_sha256: "f".repeat(64),
      object_sha256: "e".repeat(64),
      sanity: "fail",
      sanity_reasons: ["the layer holds 0 characters and none of them is content"],
      source_ids: ["fixture-source"],
    };
    const one = coverageOf(
      ["fixture-source"],
      new Map([
        [
          "fixture-source",
          { source_id: "fixture-source", outcome: "stored", sha256: "e".repeat(64), reason: null, source_class: "publisher" } as ReceiptFact,
        ],
      ]),
      [failing],
    );
    expect(one.problems).toEqual([]);
    expect(one.tally.buckets.layer_fail).toBe(1);
    expect(one.tally.characters).toBe(0);
  });
});

describe("spans", () => {
  it("slices the characters a code point span names", () => {
    const text = "alpha beta gamma";
    expect(sliceSpan(text, 6, 10)).toEqual({ exact: "beta", start: 6, end: 10, byte_start: 6, byte_end: 10 });
  });

  it("gives byte offsets that differ from the code point ones on astral text", () => {
    const text = "x\u{1F9EC}y value 0.81";
    const span = sliceSpan(text, 2, 7);
    expect(span.exact).toBe("y val");
    expect(span.start).toBe(2);
    expect(span.byte_start).toBe(5);
    expect(Buffer.from(text, "utf8").subarray(span.byte_start, span.byte_end).toString("utf8")).toBe(span.exact);
  });

  it("refuses a span that runs off the end", () => {
    expect(() => sliceSpan("short", 0, 99)).toThrow(/99/);
    expect(() => sliceSpan("short", 3, 1)).toThrow(/not a range/);
  });
});
