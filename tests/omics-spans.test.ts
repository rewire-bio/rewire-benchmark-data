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
  columnForms,
  countPoints,
  indexLayer,
  reanchor,
  refusalReasons,
  resolveDelimitedCell,
  resolveFigureCaption,
  resolveJsonPointer,
  resolveLineRange,
  resolveLocator,
  resolvePage,
  resolveQuote,
  resolveSectionParagraph,
  resolveTableCell,
  pointerTokens,
  readJson,
  renderPointer,
  walk,
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

// -----------------------------------------------------------------------------------------
// What a resolver may commit to. Every case below was a span the 2026-11-18 measurement
// returned whose text does not print the value the record stores, reduced to a fixture.

/** A two-level header, a header line a sentence was wrapped into, a row label on a line of its
 * own, and two metrics whose names differ by one letter outside ASCII. Each shape returned a
 * wrong cell before the rules this file asserts. */
const AWKWARD = [
  "            Table 8. Ablations",
  "      Method                              ωAUROC            pAUROC",
  "      Evo-2                                -0.0596           0.0625",
  "",
  "            Table 9. Benchmarks",
  "      Model                 Human                   Mouse       and the rest of a sentence",
  "      HyenaDNA              0.298                   0.396",
  "",
  "            Table 10. Correlations",
  "      Dataset",
  "      READ                  0.051             0.205",
  "",
  "            Table 11. Free energy",
  "      Method        Perc. within 2                 Perc. within 1",
  "                    cent.        raw               cent.       raw",
  "      ABFE          0.98         0.40              0.71        0.33",
  "",
  "            Table 12. Blocks",
  "      upper block",
  "      random mutations      3.89       4.81",
  "      lower block",
  "      random mutations      13.94      35.09",
  "",
  "We refer to Table 9 when a wrapped sentence",
  "Figure 4 shows this clearly, and the caption is elsewhere.",
  "",
  "      Figure 4. Binding curves for four targets",
  "      Apparent dissociation constants were 60.2 and 8.55 nM.",
].join("\n");
const awkward = indexLayer(AWKWARD, "e".repeat(64), "pdf-text-layer@1");

const at = (table: string, row: string, column: string, extra: { keys?: string[]; subColumns?: string[] } = {}): Resolution =>
  resolveTableCell(awkward, { anchor: { kind: "table", value: table, raw: `Table ${table}` }, row, column, ...extra });

describe("the column a header names", () => {
  it("reads a decoration off a header and nothing else", () => {
    expect(columnForms("MMD ↓")).toContain("mmd");
    expect(columnForms("AUROC (%)")).toContain("auroc");
    expect(columnForms("ωAUROC")).toEqual(["ωauroc"]);
  });

  it("refuses a column whose name is part of a wider header", () => {
    expect(reasonOf(at("8", "Evo-2", "AUROC"))).toBe("column_not_found");
  });

  it("returns the cell when the header names that column and no other", () => {
    const outcome = at("8", "Evo-2", "ωAUROC");
    expect(outcome.ok && outcome.span.exact).toBe("-0.0596");
  });
});

describe("which field of a row sits in the column", () => {
  it("is decided by position, not by counting fields", () => {
    // The header line carries a wrapped sentence, so it holds as many fields as the row does
    // and the nth field of the row is the wrong one.
    const outcome = at("9", "HyenaDNA", "Mouse");
    expect(outcome.ok && outcome.span.exact).toBe("0.396");
  });

  it("never returns the row label as the value of a later column", () => {
    const outcome = at("10", "READ", "Dataset");
    expect(outcome.ok).toBe(false);
  });

  it("places a sub-column inside its parent's band", () => {
    const outcome = at("11", "ABFE", "Perc. within 2", { subColumns: ["cent."] });
    expect(outcome.ok && outcome.span.exact).toBe("0.98");
    expect(outcome.ok && outcome.column_header).toBe("cent.");
  });

  it("refuses a sub-column that is not printed under the column named", () => {
    expect(reasonOf(at("11", "ABFE", "Perc. within 2", { subColumns: ["median"] }))).toBe("column_not_found");
  });

  it("refuses a row whose block the locator names and the layer does not print on the row", () => {
    expect(reasonOf(at("12", "random mutations", "upper block", { keys: ["lower"] }))).toBe("column_not_found");
  });
});

describe("a figure caption is a caption and not a mention", () => {
  it("refuses a wrapped sentence that begins with the figure's label", () => {
    const outcome = resolveFigureCaption(awkward, "4");
    expect(outcome.ok && outcome.span.exact.startsWith("Figure 4. Binding curves")).toBe(true);
  });
});

describe("the quote a locator says to find", () => {
  const PAPER = [
    "Unsupervised Clustering of Genomic Regions",
    "",
    "To quantify GPN we measured accuracy, and the model reached 96% on coding regions and 51%",
    "elsewhere. A second sentence follows it here.",
  ].join("\n");
  const paper = indexLayer(PAPER, "f".repeat(64), "pdf-text-layer@1");

  it("takes the last quoted run, not the section heading before it", () => {
    const printed =
      "Results, 'Unsupervised Clustering of Genomic Regions', sentence beginning \"To quantify GPN we measured accuracy\"";
    const outcome = resolveLocator(parseLocator(printed), paper);
    expect(outcome.ok && outcome.span.exact.startsWith("To quantify GPN")).toBe(true);
  });

  it("runs a sentence span to the end of its sentence", () => {
    const outcome = resolveQuote(paper, "To quantify GPN we measured accuracy", true);
    expect(outcome.ok && outcome.span.exact.includes("96%")).toBe(true);
    expect(outcome.ok && outcome.span.exact.includes("A second sentence")).toBe(false);
  });

  it("does not end a sentence on a decimal point", () => {
    const text = indexLayer("We saw 0.891 and stopped. Then more.", "g".repeat(64), "pdf-text-layer@1");
    const outcome = resolveQuote(text, "We saw", true);
    expect(outcome.ok && outcome.span.exact).toBe("We saw 0.891 and stopped.");
  });
});

describe("a span covers characters", () => {
  it("refuses a line that prints nothing", () => {
    const blank = indexLayer("first line\n\nthird line", "h".repeat(64), "text-utf8@1");
    expect(reasonOf(resolveLocator(parseLocator("line 2"), blank))).toBe("empty_span");
  });
});

describe("a publisher's paragraph number", () => {
  it("is refused rather than counted as a block of the layer", () => {
    const outcome = resolveLocator(parseLocator("Results P13, sentence 1"), layout);
    expect(reasonOf(outcome)).toBe("no_resolver_for_kind");
  });
});

// -----------------------------------------------------------------------------------------
// The grammar defects this lane shipped, each with a stored locator that showed it.

describe("a quoted sheet name", () => {
  const stored = [
    "Supplementary file 1, sheet 'Table S9', P7; Discovery block; row 'Gastric'; column 'DNN' under 'Stage III' (n in N7)",
    "Sun Additional file 1, sheet 'Table S7 ', I4; row 'Liver cancer (WGBS)'; column 'CelFEER' under 'AUC values'",
    "Supplementary Table 9 (sheet 'SupTable9_Likelihood_Ratios'), I10; tool 'alignGVGD_a'; column 'BRCA2_negative_LR'",
    "Table S9 (sheet 'Table S9') cell I9, row 'ANEVA-H', column 'F1'",
  ];
  const sheetsOf = (printed: string): string[] =>
    parseLocator(printed).anchors.filter((anchor) => anchor.kind === "sheet").map((anchor) => anchor.value);

  it("ends at its closing quote, whatever its last token looks like", () => {
    expect(sheetsOf(stored[0])).toEqual(["Table S9"]);
    expect(sheetsOf(stored[1])).toEqual(["Table S7"]);
  });

  it("survives the parenthesis it is written inside", () => {
    expect(sheetsOf(stored[2])).toEqual(["SupTable9_Likelihood_Ratios"]);
    expect(sheetsOf(stored[3])).toEqual(["Table S9"]);
  });

  it("leaves no part of itself to be read as a cell address", () => {
    // P7 is the cell. S9 is part of the sheet name and must not appear here, and the N7 inside
    // the parenthetical is a note the grammar reads as one.
    const cells = parseLocator(stored[0]).addresses.filter((address) => address.kind === "sheet_cell");
    expect(cells.map((address) => address.value)).toEqual(["P7"]);
  });
});

describe("a JSON path in a stored locator", () => {
  it("keeps its head when a layer qualifier stands before it", () => {
    const parsed = parseLocator("JSON entries[63].score_avg; submission u2MMaChop9DM3fjqkS7z");
    expect(parsed.addresses.filter((address) => address.kind === "json_path").map((a) => a.value)).toEqual([
      "entries[63].score_avg",
    ]);
  });

  it("is not the file name it is written beside", () => {
    const parsed = parseLocator("leaderboard.json data.10shot, model 'deepgene', key 'micro_MCC'");
    expect(parsed.anchors.filter((anchor) => anchor.kind === "file").map((a) => a.value)).toEqual(["leaderboard.json"]);
    expect(parsed.addresses.filter((address) => address.kind === "json_path").map((a) => a.value)).toEqual(["data.10shot"]);
  });
});

// -----------------------------------------------------------------------------------------
// The JSON Pointer resolver.

describe("JSON Pointer", () => {
  const DOC = JSON.stringify(
    {
      entries: [
        { id: "aaa", score_avg: 0.25, note: "" },
        { id: "bbb", score_avg: 0.5, note: "second" },
      ],
      data: {
        "10shot": [
          { model: "deepgene", micro_MCC: 0.079, cat_MCC: { Enhancers: 0.257 } },
          { model: "caduceus", micro_MCC: 0.244, cat_MCC: { Enhancers: 0.33 } },
        ],
      },
      "a/b": { "c~d": 1 },
    },
    null,
    1,
  );
  const doc = indexLayer(DOC, "i".repeat(64), "text-utf8@1");
  const resolve = (path: string, selectors: { key: string; value: string; role: "row" | "column" | "other" }[] = []) =>
    resolveJsonPointer(doc, { path, selectors });

  it("reads the dotted and bracketed form the store writes as reference tokens", () => {
    expect(pointerTokens("entries[63].score_avg")).toEqual(["entries", "63", "score_avg"]);
    expect(pointerTokens("$.data.10shot")).toEqual(["data", "10shot"]);
    expect(pointerTokens("/a~1b/c~0d")).toEqual(["a/b", "c~d"]);
    expect(renderPointer(["a/b", "c~d"])).toBe("/a~1b/c~0d");
  });

  it("records where every value sits in the text", () => {
    const node = readJson(DOC);
    expect(node?.kind).toBe("object");
    const first = node?.members?.find((member) => member.key === "entries")?.node.items?.[0];
    const id = first?.members?.find((member) => member.key === "id")?.node;
    // A string's span includes its quotes, as a quoted field's span does in a delimited file.
    expect(DOC.slice(id?.from ?? 0, id?.to ?? 0)).toBe('"aaa"');
  });

  it("returns the value a pointer addresses, with the object's own cross-check", () => {
    const outcome = resolve("entries[0].score_avg", [{ key: "submission", value: "aaa", role: "other" }]);
    expect(outcome.ok && outcome.span.exact).toBe("0.25");
  });

  it("refuses when the index and the cross-check name different objects", () => {
    expect(reasonOf(resolve("entries[1].score_avg", [{ key: "submission", value: "aaa", role: "other" }]))).toBe(
      "row_key_unmatched",
    );
  });

  it("picks one element of an array by a selector and descends by key", () => {
    const outcome = resolve("data.10shot", [
      { key: "model", value: "deepgene", role: "other" },
      { key: "key", value: "cat_MCC.Enhancers", role: "column" },
    ]);
    expect(outcome.ok && outcome.span.exact).toBe("0.257");
    expect(outcome.ok && outcome.row_label).toBe("deepgene");
  });

  it("refuses an array with nothing to pick an element by, and a selector that picks none", () => {
    expect(reasonOf(resolve("data.10shot"))).toBe("no_row_in_locator");
    expect(reasonOf(resolve("data.10shot", [{ key: "model", value: "absent", role: "other" }]))).toBe("row_not_found");
  });

  it("refuses a pointer that leaves the document", () => {
    expect(reasonOf(resolve("entries[0].absent", [{ key: "submission", value: "aaa", role: "other" }]))).toBe("column_not_found");
    expect(reasonOf(resolve("entries[9].score_avg"))).toBe("column_not_found");
  });

  it("refuses an index RFC 6901 does not define", () => {
    expect(reasonOf(resolve("entries[0].score_avg"))).toBe("resolved");
    const document = readJson(DOC);
    expect(document && walk(document, ["entries", "01"]).ok).toBe(false);
    expect(document && walk(document, ["entries", "-"]).ok).toBe(false);
  });

  it("refuses a pointer that stops on an object, and an empty value", () => {
    expect(reasonOf(resolve("entries[0]", [{ key: "submission", value: "aaa", role: "other" }]))).toBe("column_not_found");
    expect(reasonOf(resolve("entries[0].note", [{ key: "submission", value: "aaa", role: "other" }]))).toBe("cell_empty");
  });

  it("refuses a layer that is not one JSON document", () => {
    expect(reasonOf(resolveJsonPointer(csv, { path: "entries[0].id", selectors: [] }))).toBe("json_not_parsed");
  });
});
