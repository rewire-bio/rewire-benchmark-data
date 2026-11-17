/** Locator grammar v2: the conformance the report rests on.
 *
 * Three things are pinned here. The ported v1 regex agrees with `check-values` row for row on the
 * 14 `data/omics/*​/value-check.tsv` files, so the coverage report's `table_row_col` class is the
 * same set of locators the old check parses. The grammar reads the sample of stored locators the
 * way the fixture records, so a change to one token shows up as a row that moved. The span type
 * keeps both offset bases, so a span written later cannot quietly mix them.
 *
 * Nothing here loads the record store: the value-check files and the fixture are read as text. */
import fs from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import {
  classifyLocator, coverageOf, parseLocator, parsesUnderLegacyRegex, renderLocator,
  selectorRole, spanSchema, splitSegments, locatorClasses, locatorSchema,
} from "../shared/omics/locator";

const root = path.resolve(__dirname, "..");

describe("the ported v1 locator regex", () => {
  const files = fs.readdirSync(path.join(root, "data/omics"))
    .map((batch) => path.join(root, "data/omics", batch, "value-check.tsv"))
    .filter((file) => fs.existsSync(file))
    .sort();

  it("reads the same rows check-values did", () => {
    expect(files.length).toBe(14);
    let parsed = 0;
    let notParsed = 0;
    const disagreed: string[] = [];
    for (const file of files) {
      const lines = fs.readFileSync(file, "utf8").split("\n").filter((l) => l.length > 0);
      expect(lines[0]).toBe("id\tstatus\tprinted_value\tsource_locator");
      for (const line of lines.slice(1)) {
        const fields = line.split("\t");
        const [id, status] = fields;
        const locator = fields.slice(3).join("\t");
        const matches = parsesUnderLegacyRegex(locator);
        if (status === "locator_not_parsed") notParsed += 1; else parsed += 1;
        if (matches !== (status !== "locator_not_parsed")) {
          disagreed.push(`${path.relative(root, file)} ${id} status=${status} locator=${JSON.stringify(locator)}`);
        }
      }
    }
    expect(disagreed).toEqual([]);
    // The row-by-row agreement above is the durable assertion; it holds over whatever value-check
    // files exist. The counts below pin the 2026-11-17 measurement over the 14 files that had been
    // checked by then (867 in_cell, 994 in_row, 20 row_not_found, 551 locator_not_parsed), and
    // have to be raised when another batch runs check-values.
    expect(notParsed).toBe(551);
    expect(parsed).toBe(1881);
  });

  it("rejects what the stricter forms of the same table locator leave out", () => {
    expect(parsesUnderLegacyRegex("Table S18, row 'Bacformer', column 'Binary AUPRC'")).toBe(true);
    // No quotes around the row value.
    expect(parsesUnderLegacyRegex("Table A2; row ESMC-300M naive supervised; column spearman")).toBe(false);
    // A Roman numeral where the regex wants digits.
    expect(parsesUnderLegacyRegex("Table IV, row 'X', column 'Accuracy'")).toBe(false);
    // The table named inside the string rather than at its start.
    expect(parsesUnderLegacyRegex("'Suppl Table 3 Track performance'!K8")).toBe(false);
  });
});

describe("parsing a stored locator", () => {
  const rows = fs.readFileSync(path.join(root, "tests/fixtures/locator-sample.tsv"), "utf8")
    .split("\n")
    .filter((line) => line.length > 0 && !line.startsWith("#"))
    .slice(1)
    .map((line) => {
      const [locator, cls, verdict] = line.split("\t");
      return { locator, cls, verdict };
    });

  it("covers every class the store holds", () => {
    expect(rows.length).toBeGreaterThan(30);
    // The twelfth class, table_row_unmatched, has no locator in the store today: every table
    // label with a quoted row that the v1 regex misses is a dotted label.
    expect([...new Set(rows.map((r) => r.cls))].sort())
      .toEqual([...locatorClasses].filter((c) => c !== "table_row_unmatched").sort());
  });

  for (const row of rows) {
    it(`reads ${JSON.stringify(row.locator.slice(0, 60))} as ${row.cls}/${row.verdict}`, () => {
      expect(classifyLocator(row.locator)).toBe(row.cls);
      expect(parseLocator(row.locator).verdict).toBe(row.verdict);
    });
  }

  it("reads a table, a quoted row and a quoted column into typed fields", () => {
    const parsed = parseLocator("Table S18, row 'Bacformer', column 'Binary AUPRC'");
    expect(parsed.anchors).toEqual([{ kind: "table", value: "S18", raw: "Table S18" }]);
    expect(parsed.selectors.map((s) => [s.key, s.value, s.form])).toEqual([
      ["row", "Bacformer", "quoted"],
      ["column", "Binary AUPRC", "quoted"],
    ]);
    expect(parsed.residue).toEqual([]);
    expect(coverageOf(parsed.verdict)).toBe("full");
  });

  it("reads a sheet and a cell as an address", () => {
    const parsed = parseLocator("'Suppl Table 3 Track performance'!K8");
    expect(parsed.anchors.map((a) => a.kind)).toEqual(["sheet"]);
    expect(parsed.addresses).toEqual([{ kind: "sheet_cell", value: "K8", raw: "!K8" }]);
    // A cell with no label to check it against is addressed in one direction only.
    expect(parsed.verdict).toBe("cell_only");
    expect(coverageOf(parsed.verdict)).toBe("partial");
  });

  it("keeps the container a table sits in", () => {
    const parsed = parseLocator("Supplementary Table 9, row 'BRCA2', column 'LR'");
    expect(parsed.anchors[0]).toEqual({
      kind: "table", value: "9", container: "Supplementary", raw: "Supplementary Table 9",
    });
  });

  it("reports what it could not read instead of dropping it", () => {
    const parsed = parseLocator("Table 1 (XML tbl1); row Boltz R; column angle_rmsd; footnote a");
    expect(parsed.residue).toEqual(["footnote a"]);
    expect(parsed.verdict).toBe("residue");
    expect(coverageOf(parsed.verdict)).toBe("residue");
  });

  it("splits on semicolons and on commas outside quotes and brackets", () => {
    expect(splitSegments("Table 4, row 'Ridge (one-hot), tuned'; column 'spearman'"))
      .toEqual(["Table 4", "row 'Ridge (one-hot), tuned'", "column 'spearman'"]);
  });

  it("reads an ordinal in a key as naming that row or column", () => {
    expect(selectorRole("column")).toBe("column");
    expect(selectorRole("column 4")).toBe("column");
    expect(selectorRole("column 1 of 4")).toBe("column");
    expect(selectorRole("row")).toBe("row");
    expect(selectorRole("model")).toBe("other");
  });

  it("calls a locator with no anchor and no address unanchored", () => {
    const parsed = parseLocator("metrics.ndcg");
    expect(parsed.anchors).toEqual([]);
    expect(parsed.addresses).toEqual([]);
    expect(coverageOf(parsed.verdict)).toBe("unanchored");
  });
});

describe("rendering a locator", () => {
  it("writes the canonical form back out unchanged", () => {
    const printed = "Table S18, row 'Bacformer', column 'Binary AUPRC'";
    expect(renderLocator(parseLocator(printed))).toBe(printed);
  });

  it("renders from the typed fields, not from the text they were read from", () => {
    const parsed = parseLocator("Table A2; row ESMC-300M naive supervised; column spearman");
    expect(renderLocator(parsed)).toBe("Table A2, row ESMC-300M naive supervised, column spearman");
  });

  it("reads its own output back as the same structure", () => {
    const printed = "Supplementary Table 9 (sheet 'SupTable9_Likelihood_Ratios'), I10; tool 'alignGVGD_a'; column 'BRCA2_negative_LR'";
    const once = parseLocator(printed);
    const twice = parseLocator(renderLocator(once));
    expect(twice.selectors.map((s) => [s.key, s.value])).toEqual(once.selectors.map((s) => [s.key, s.value]));
    expect(twice.addresses.map((a) => [a.kind, a.value])).toEqual(once.addresses.map((a) => [a.kind, a.value]));
  });
});

describe("the span type", () => {
  const span = {
    layer_sha256: "a".repeat(64),
    start: 10, end: 14,
    byte_start: 12, byte_end: 18,
    exact: "0.81", prefix: "AUPRC ", suffix: " ± 0.07",
  };

  it("keeps code-point offsets and byte offsets apart", () => {
    expect(spanSchema.parse(span)).toEqual(span);
    // oa:TextPositionSelector counts code points, so a span never covers fewer UTF-8 bytes than
    // code points. Offsets written in the wrong basis fail here rather than in a resolver.
    expect(spanSchema.safeParse({ ...span, byte_start: 12, byte_end: 14 }).success).toBe(false);
  });

  it("requires the quoted text, which is what relocates a span when the layer is rebuilt", () => {
    const { exact, ...withoutQuote } = span;
    expect(spanSchema.safeParse(withoutQuote).success).toBe(false);
  });

  it("refuses an end before its start and a layer hash that is not a sha256", () => {
    expect(spanSchema.safeParse({ ...span, end: 4 }).success).toBe(false);
    expect(spanSchema.safeParse({ ...span, layer_sha256: "nope" }).success).toBe(false);
  });
});

describe("the authored locator schema", () => {
  const locator = {
    anchors: [{ kind: "table" as const, value: "S18", raw: "Table S18" }],
    selectors: [{ key: "row", value: "Bacformer", form: "quoted" as const, raw: "row 'Bacformer'" }],
    qualifiers: [],
    printed: "Table S18, row 'Bacformer'",
  };

  it("takes a locator with an anchor", () => {
    expect(locatorSchema.parse(locator).anchors.length).toBe(1);
  });

  it("refuses one with no anchor, which is what a resolver cannot start from", () => {
    expect(locatorSchema.safeParse({ ...locator, anchors: [] }).success).toBe(false);
  });
});
