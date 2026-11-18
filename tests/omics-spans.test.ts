/** The span resolvers, ADR 0002 step 5.
 *
 * Five things are asserted here.
 *
 * 1. The two offset systems agree. A span carries code point offsets because that is what
 *    `oa:TextPositionSelector` counts and UTF-8 byte offsets because that is what a resolver
 *    slices, and on text outside the basic multilingual plane the two differ. Both are checked
 *    against `sliceSpan`, which is the layer registry's published contract, on a fixture and on
 *    a real layer from the store.
 * 2. Each resolver returns a span where the layer carries one and refuses with a stated reason
 *    where it does not. The refusals are the point: a resolver that guesses puts a wrong span on
 *    a record and a wrong span reads as a check that passed.
 * 3. A locator that names a row by a composite key is refused unless every part of the key is
 *    printed on the line accepted as the row.
 * 4. Re-anchoring moves a span to a rebuilt layer by its quote, or refuses. The rule is tested on
 *    a real layer perturbed three ways: text inserted before the span, the quote deleted, the
 *    quote duplicated.
 * 5. Every outcome over a sample of the store's own locators is either a span or one of the
 *    listed refusal reasons, so the measurement's buckets cannot silently acquire a new one.
 *
 * Everything here is offline and calls no model. The tests that need layer bytes skip when the
 * object cache is not on this machine, because the cache is gitignored by design.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { hasObject } from "../scripts/archive/objects";
import { measure } from "../scripts/omics/spans/cli";
import { layerText, readRegistry, sliceSpan, type LayerRecord } from "../shared/omics/layers/index";
import { parseLocator } from "../shared/omics/locator";
import {
  countPoints,
  indexLayer,
  reanchor,
  refusalReasons,
  resolveDelimitedCell,
  resolveFigureCaption,
  resolveLineRange,
  resolveLocator,
  resolvePage,
  resolveQuote,
  resolveSectionParagraph,
  resolveTableCell,
  spanAt,
  type RefusalReason,
  type Resolution,
} from "../shared/omics/spans/index";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

/** A layout text layer as `pdftotext -layout` writes one: columns held apart by runs of spaces,
 * captions starting their line, a table that runs to the next caption. */
const LAYOUT = [
  "Introduction",
  "",
  "We report accuracy for three models, and Table 3 gives the numbers.",
  "",
  "            Table 3. Accuracy by model",
  "      Model                          AUROC          AUPRC",
  "      Caduceus                       0.912          0.845",
  "      DNABERT-2                      0.903          0.831",
  "      Ridge (one-hot)                0.874",
  "",
  "            Table 7. Accuracy by length",
  "      Size     Model      Length     AUROC          AUPRC",
  "      Medium   Chroma     300        0.398          0.512",
  "      Medium   Chroma     400        0.741          0.655",
  "",
  "            Table 4. Accuracy on the held-out split",
  "      Model                          AUROC          AUPRC",
  "      Caduceus                       0.712          0.645",
  "",
  "            Figure 2. Accuracy against sequence length, with 95% intervals",
  "      Panels a and b share an axis.",
  "",
  "Methods",
  "",
  "We trained each model for ten epochs on one node.",
  "The learning rate was fixed.",
  "",
  "Evaluation used a held-out chromosome.",
  "",
  "Results",
  "",
  "Accuracy rose with length.",
].join("\n");

const layout = indexLayer(LAYOUT, "a".repeat(64), "pdf-text-layer@1");

const CSV = ["sample,metric,value", "A,auroc,0.91", "B,auroc,0.88", "C,auroc,"].join("\n");
const csv = indexLayer(CSV, "b".repeat(64), "text-utf8@1");

/** One cell per line, which is what the HTML and JATS normalisers produce. No column positions. */
const FLAT = ["Table 5: Accuracy", "", "Model", "AUROC", "", "Caduceus", "0.912"].join("\n");
const flat = indexLayer(FLAT, "c".repeat(64), "html-text@1");

const PAGED = ["page one text", "\fpage two text", "\fpage three text"].join("\n");
const paged = indexLayer(PAGED, "d".repeat(64), "pdf-text-layer@1");

const cell = (row: string, column: string, keys: string[] = [], table = "3"): Resolution =>
  resolveTableCell(layout, { anchor: { kind: "table", value: table, raw: `Table ${table}` }, row, column, keys });

const reasonOf = (outcome: Resolution): RefusalReason | "resolved" => (outcome.ok ? "resolved" : outcome.reason);

describe("the two offset systems", () => {
  /** An astral code point, a combining mark and a plain one, so UTF-16 units, code points and
   * UTF-8 bytes all disagree. */
  const mixed = "aé́ 𝜋 value 0.412 and 𝜋 again";

  it("counts code points, not UTF-16 units", () => {
    const index = indexLayer(mixed, "e".repeat(64), "text-utf8@1");
    expect(countPoints(mixed)).toBeLessThan(mixed.length);
    expect(index.points[index.points.length - 1]).toBe(countPoints(mixed));
  });

  it("agrees with sliceSpan, which is the registry's published contract", () => {
    const index = indexLayer(mixed, "e".repeat(64), "text-utf8@1");
    const at = mixed.indexOf("0.412");
    const span = spanAt(index, at, at + 5);
    const slice = sliceSpan(mixed, span.start, span.end);
    expect(span.exact).toBe("0.412");
    expect([span.start, span.end, span.byte_start, span.byte_end]).toEqual([slice.start, slice.end, slice.byte_start, slice.byte_end]);
    expect(span.byte_start).toBeGreaterThan(span.start);
  });

  it("never splits a surrogate pair", () => {
    const index = indexLayer(mixed, "e".repeat(64), "text-utf8@1");
    const at = mixed.indexOf("𝜋");
    const span = spanAt(index, at + 1, at + 2);
    expect(span.exact).toBe("𝜋");
    expect(span.end - span.start).toBe(1);
    expect(span.byte_end - span.byte_start).toBe(4);
  });

  it("puts 48 code points of context either side", () => {
    const long = `${"x".repeat(200)}0.412${"y".repeat(200)}`;
    const index = indexLayer(long, "f".repeat(64), "text-utf8@1");
    const span = spanAt(index, 200, 205);
    expect(countPoints(span.prefix ?? "")).toBe(48);
    expect(countPoints(span.suffix ?? "")).toBe(48);
  });
});

describe("the table cell resolver", () => {
  it("returns the cell, with the row and column the layer prints", () => {
    const outcome = cell("Caduceus", "AUPRC");
    expect(outcome.ok).toBe(true);
    if (!outcome.ok) return;
    expect(outcome.span.exact).toBe("0.845");
    expect(outcome.row_label).toBe("Caduceus");
    expect(outcome.column_header).toBe("AUPRC");
    expect(LAYOUT.slice(0, outcome.span.byte_start).length).toBe(outcome.span.start);
  });

  it("reads the column name case for case with the locator's", () => {
    const outcome = cell("DNABERT-2", "auroc");
    expect(outcome.ok && outcome.span.exact).toBe("0.903");
  });

  it("stops at the next caption, so Table 4's rows are not Table 3's", () => {
    const outcome = resolveTableCell(layout, {
      anchor: { kind: "table", value: "4", raw: "Table 4" },
      row: "Caduceus",
      column: "AUROC",
    });
    expect(outcome.ok && outcome.span.exact).toBe("0.712");
    expect(cell("Caduceus", "AUROC").ok && (cell("Caduceus", "AUROC") as { span: { exact: string } }).span.exact).toBe("0.912");
  });

  it("refuses a table the layer does not caption", () => {
    expect(reasonOf(resolveTableCell(layout, { anchor: { kind: "table", value: "9", raw: "Table 9" }, row: "Caduceus", column: "AUROC" }))).toBe("anchor_not_found");
  });

  it("refuses a row the window does not print", () => {
    expect(reasonOf(cell("Mamba", "AUROC"))).toBe("row_not_found");
  });

  it("refuses a column the window does not print", () => {
    expect(reasonOf(cell("Caduceus", "F1"))).toBe("column_not_found");
  });

  it("refuses a cell the row leaves blank", () => {
    expect(reasonOf(cell("Ridge (one-hot)", "AUPRC"))).toBe("cell_empty");
  });

  it("refuses a layer that prints no column positions", () => {
    const outcome = resolveTableCell(flat, { anchor: { kind: "table", value: "5", raw: "Table 5" }, row: "Caduceus", column: "AUROC" });
    expect(reasonOf(outcome)).toBe("no_column_geometry");
  });

  it("refuses a composite row key whose parts are not all on one line", () => {
    expect(reasonOf(cell("Medium", "AUROC", ["Chroma", "500"], "7"))).toBe("row_key_unmatched");
  });

  it("uses the parts of a composite key to tell two rows apart", () => {
    const outcome = cell("Medium", "AUROC", ["Chroma", "400"], "7");
    expect(outcome.ok && outcome.span.exact).toBe("0.741");
    expect(reasonOf(cell("Medium", "AUROC", [], "7"))).toBe("row_ambiguous");
  });

  it("refuses when two captions name the table and both hold the row and column", () => {
    const twice = indexLayer(`${LAYOUT}\n\n            Table 3. Accuracy by model, repeated\n      Model                          AUROC          AUPRC\n      Caduceus                       0.912          0.845\n`, "a".repeat(64), "pdf-text-layer@1");
    const outcome = resolveTableCell(twice, { anchor: { kind: "table", value: "3", raw: "Table 3" }, row: "Caduceus", column: "AUPRC" });
    expect(reasonOf(outcome)).toBe("anchor_ambiguous");
  });
});

describe("the delimited, line and page resolvers", () => {
  it("returns a cell by line and column header", () => {
    const outcome = resolveDelimitedCell(csv, { line: 2, column: "value" });
    expect(outcome.ok && outcome.span.exact).toBe("0.91");
    expect(outcome.ok && outcome.column_header).toBe("value");
  });

  it("returns the same cell by A1 notation", () => {
    expect(resolveDelimitedCell(csv, { cell: "C2" }).ok && (resolveDelimitedCell(csv, { cell: "C2" }) as { span: { exact: string } }).span.exact).toBe("0.91");
  });

  it("refuses a blank cell and a line past the end", () => {
    expect(reasonOf(resolveDelimitedCell(csv, { line: 4, column: "value" }))).toBe("cell_empty");
    expect(reasonOf(resolveDelimitedCell(csv, { line: 40, column: "value" }))).toBe("line_out_of_range");
    expect(reasonOf(resolveDelimitedCell(csv, { line: 2, column: "absent" }))).toBe("column_not_found");
  });

  it("returns a run of lines", () => {
    const outcome = resolveLineRange(csv, 2, 3);
    expect(outcome.ok && outcome.span.exact).toBe("A,auroc,0.91\nB,auroc,0.88");
  });

  it("returns one page of a PDF layer and refuses a page past the end", () => {
    expect(resolvePage(paged, 2).ok && (resolvePage(paged, 2) as { span: { exact: string } }).span.exact).toBe("page two text\n");
    expect(reasonOf(resolvePage(paged, 9))).toBe("page_out_of_range");
    expect(reasonOf(resolvePage(csv, 1))).toBe("page_out_of_range");
  });
});

describe("the figure and section resolvers", () => {
  it("returns a figure's caption, and says that is what it is", () => {
    const outcome = resolveFigureCaption(layout, "2");
    expect(outcome.ok && outcome.kind).toBe("figure_caption");
    expect(outcome.ok && outcome.span.exact.startsWith("Figure 2. Accuracy against sequence length")).toBe(true);
  });

  it("returns a numbered paragraph of a named section", () => {
    const outcome = resolveSectionParagraph(layout, "Methods", 2);
    expect(outcome.ok && outcome.span.exact).toBe("Evaluation used a held-out chromosome.");
  });

  it("does not count on into the next section", () => {
    expect(reasonOf(resolveSectionParagraph(layout, "Methods", 3))).toBe("paragraph_out_of_range");
    expect(reasonOf(resolveSectionParagraph(layout, "Discussion", 1))).toBe("section_not_found");
  });
});

describe("the quote resolver", () => {
  it("finds a quote that occurs once", () => {
    const outcome = resolveQuote(layout, "three models");
    expect(outcome.ok && outcome.span.exact).toBe("three models");
  });

  it("finds a quote the renderer wrapped across a line", () => {
    const wrapped = indexLayer("the learning rate was\nfixed for every run", "f".repeat(64), "pdf-text-layer@1");
    const outcome = resolveQuote(wrapped, "learning rate was fixed");
    expect(outcome.ok && outcome.span.exact).toBe("learning rate was\nfixed");
  });

  it("refuses a quote that occurs twice and one that occurs not at all", () => {
    expect(reasonOf(resolveQuote(layout, "Caduceus"))).toBe("quote_ambiguous");
    expect(reasonOf(resolveQuote(layout, "a sentence nobody wrote"))).toBe("quote_not_found");
  });
});

describe("re-anchoring a span onto a layer that moved", () => {
  const at = LAYOUT.indexOf("0.845");
  const span = spanAt(layout, at, at + 5);

  it("leaves a span alone when the layer is the one it names", () => {
    const outcome = reanchor(span, layout);
    expect(outcome.ok && outcome.outcome).toBe("unchanged");
    expect(outcome.ok && outcome.evidence).toBe("offsets");
  });

  it("relocates by context when text is inserted before the span", () => {
    const moved = indexLayer(`A new paragraph at the top.\n\n${LAYOUT}`, "9".repeat(64), "pdf-text-layer@1");
    const outcome = reanchor(span, moved);
    expect(outcome.ok && outcome.outcome).toBe("relocated");
    expect(outcome.ok && outcome.evidence).toBe("context");
    expect(outcome.ok && outcome.span.exact).toBe("0.845");
    expect(outcome.ok && outcome.span.start).toBe(span.start + 29);
  });

  it("refuses when the quote is gone", () => {
    const gone = indexLayer(LAYOUT.replace("0.845", "0.999"), "8".repeat(64), "pdf-text-layer@1");
    expect(reasonOf(reanchor(span, gone) as Resolution)).toBe("quote_not_found");
  });

  it("refuses when the quote and its context occur twice", () => {
    const twice = indexLayer(`${LAYOUT}\n${LAYOUT}`, "7".repeat(64), "pdf-text-layer@1");
    expect(reasonOf(reanchor(span, twice) as Resolution)).toBe("quote_ambiguous");
  });
});

describe("over the store itself", () => {
  const registry = readRegistry(root);
  /** The layer the flip2 appendix tables sit in, which holds an astral-free but multi-byte table
   * with a plus or minus sign, so the byte and code point offsets differ. */
  const pick = (): LayerRecord | undefined =>
    registry.find((record) => record.normaliser === "pdf-text-layer@1" && record.sanity === "pass" && record.metrics.characters > 40_000 && hasObject(record.object_sha256, root));

  it("takes a span whose two offset systems both slice the same characters", () => {
    const record = pick();
    if (!record) return;
    const text = layerText(record, root);
    const index = indexLayer(text, record.layer_sha256, record.normaliser);
    const at = text.indexOf("0.");
    if (at < 0) return;
    const span = spanAt(index, at, at + 5);
    const slice = sliceSpan(text, span.start, span.end);
    expect(span.exact).toBe(slice.exact);
    expect(span.byte_start).toBe(slice.byte_start);
    expect(Buffer.from(text, "utf8").subarray(span.byte_start, span.byte_end).toString("utf8")).toBe(span.exact);
  });

  it("re-anchors a real span onto the same layer perturbed three ways", () => {
    const record = pick();
    if (!record) return;
    const text = layerText(record, root);
    const index = indexLayer(text, record.layer_sha256, record.normaliser);
    const at = text.indexOf("\n", 2000) + 1;
    const span = spanAt(index, at, at + 40);
    if (span.exact.trim().length < 10) return;

    const inserted = indexLayer(`${"-".repeat(64)}\n${text}`, "1".repeat(64), record.normaliser);
    const moved = reanchor(span, inserted);
    expect(moved.ok && moved.outcome).toBe("relocated");
    expect(moved.ok && moved.span.exact).toBe(span.exact);

    const deleted = indexLayer(text.split(span.exact).join("####"), "2".repeat(64), record.normaliser);
    expect(reanchor(span, deleted).ok).toBe(false);

    const duplicated = indexLayer(`${text}\n${text}`, "3".repeat(64), record.normaliser);
    const twice = reanchor(span, duplicated);
    expect(twice.ok).toBe(false);
    if (!twice.ok) expect(twice.reason).toBe("quote_ambiguous");
  });

  it("answers every stored locator with a span or a listed reason", () => {
    const file = path.join(root, "data/evidence/results/0.jsonl");
    const locators = fs
      .readFileSync(file, "utf8")
      .split("\n")
      .filter((line) => line.trim())
      .slice(0, 600)
      .map((line) => (JSON.parse(line) as { attributes: { source_locator?: string } }).attributes.source_locator ?? "");
    const seen = new Set<string>();
    for (const printed of locators) {
      const outcome = resolveLocator(parseLocator(printed), layout);
      if (outcome.ok) continue;
      expect(refusalReasons).toContain(outcome.reason);
      seen.add(outcome.reason);
    }
    expect(seen.size).toBeGreaterThan(2);
  });

  it("names every refusal reason once", () => {
    expect(new Set(refusalReasons).size).toBe(refusalReasons.length);
  });

  /** ADR 0002 decision 7 asks for an arithmetic identity rather than a set of numbers that
   * happen to look right. Every locator the measurement reads is either a span or one refusal,
   * and the two sum to the locators read. */
  it("puts every locator in exactly one bucket", () => {
    const report = measure({ root, limit: 300 });
    let refused = 0;
    for (const [reason, count] of report.by_reason) {
      expect(refusalReasons).toContain(reason);
      refused += count;
    }
    expect(report.resolved + refused).toBe(report.locators);
    expect(report.locators).toBe(300);
  });
});
