/** The table grid, and the one property it has to have.
 *
 * A grid is only worth holding if a cell's coordinates and a cell's
 * characters name the same thing. Every test below that matters is a form
 * of the same assertion: take the cell at row r, column c, slice the text
 * layer at the code point offsets the grid gives, and get back exactly the
 * characters the grid says are there. Where that cannot be had, the grid
 * holds no offsets and a resolver must refuse.
 *
 * The structural cases are fixtures written here. The agreement check also
 * runs over the JATS and HTML artifacts committed under data/omics, so the
 * property is asserted against real publisher markup and not only against
 * markup written to pass.
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import zlib from "node:zlib";
import { createHash } from "node:crypto";
import { afterEach, expect, it } from "vitest";
import { manifestRowSchema } from "../../schema";
import { upsertRow } from "../../../../scripts/archive/manifest";
import { putObject } from "../../../../scripts/archive/objects";
import { layerText, layersOfObject } from "../../../omics/layers/index";
import { decode, encodingOf } from "../classify";
import { htmlLayer, htmlRules } from "../html";
import { layerOf } from "../index";
import { scanMarkup, tidy, tidyTraced } from "../markup";
import { xmlLayer, xmlRules } from "../xml";
import { candidateHeader, cellAt, cellRange, gridLayer, gridOf, printsValue, readGrid, serialiseGrid, tableAt } from "./index";
import type { Grid } from "./types";

const digest = (bytes: Buffer): string => createHash("sha256").update(bytes).digest("hex");

const roots: string[] = [];
afterEach(() => roots.splice(0).forEach((root) => fs.rmSync(root, { recursive: true, force: true })));
const temporaryRoot = (): string => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "archive-grid-"));
  roots.push(root);
  return root;
};

const fixture = (file: string): Buffer => {
  const bytes = fs.readFileSync(file);
  return file.endsWith(".gz") ? zlib.gunzipSync(bytes) : bytes;
};

const jats = "data/omics/use-case-coverage-cnv-20261011-hwang2026/artifacts/PMC12841491.xml.gz";
const html = "data/omics/poisk-20261115/artifacts/poisk-explorer.html.gz";

/** The characters at a half open code point range, counted the way a span
 * counts them. Deliberately the slow and obvious implementation: the point
 * of the check is to agree with something that cannot be wrong. */
const atPoints = (text: string, start: number, end: number): string => [...text].slice(start, end).join("");

/** Build a grid over a fragment of JATS, which is the markup both
 * normalisers write tables in. */
function jatsGrid(body: string): { grid: Grid; text: string } {
  const markup = `<?xml version="1.0"?><article><body>${body}</body></article>`;
  const text = xmlLayer(Buffer.from(markup, "utf8")).bytes.toString("utf8");
  const built = gridOf(markup, xmlRules, "jats-table-grid@1", "europepmc-fulltext-xml@1", "0".repeat(64));
  expect(built.text).toBe(text);
  return { grid: built.grid, text };
}

/** Every cell in every table: the offsets and the characters agree. */
function cellsAgree(grid: Grid, text: string): number {
  let checked = 0;
  for (const table of grid.tables)
    for (const cell of table.cells) {
      if (cell.start === null || cell.end === null) {
        expect(cell.text).toBe("");
        continue;
      }
      expect(cell.end).toBeGreaterThan(cell.start);
      expect(atPoints(text, cell.start, cell.end)).toBe(cell.text);
      expect(cell.text.trim()).toBe(cell.text);
      checked += 1;
    }
  return checked;
}

/** `tidy` as it was written before it was traced. The layer hashes in the
 * registry were produced by this, so a change in the traced version that
 * moved the text would move every stored offset. */
const reference = (text: string): string => {
  const lines = text.split("\n").map((line) => line.replace(/[^\S\n]+/g, " ").trim());
  const kept: string[] = [];
  for (const line of lines) {
    if (line === "" && (kept.length === 0 || kept[kept.length - 1] === "")) continue;
    kept.push(line);
  }
  while (kept.length && kept[kept.length - 1] === "") kept.pop();
  return kept.length ? `${kept.join("\n")}\n` : "";
};

it("tidies exactly the text the untraced version tidied", () => {
  const cases = [
    "",
    "\n",
    "a",
    "a\n",
    "  a  \n",
    "a\n\n\nb",
    "\n\n\na\n\n\n",
    "a \t\u00a0 b",
    "\u00a0\u00a0\n a \n\u00a0",
    "one  two\nthree\n\n\nfour \n",
    "\u{1d4b1} \u0301 x\n\n",
    "trailing   ",
    " \f ",
    "a\r\nb",
  ];
  for (const value of cases) expect(tidy(value)).toBe(reference(value));
});

it("maps every kept character onto the tidied text", () => {
  const raw = "  alpha   beta \n\n\n  gamma  \n";
  const { text, out } = tidyTraced(raw);
  expect(text).toBe(tidy(raw));
  for (let index = 0; index < raw.length; index += 1) {
    const at = out[index];
    if (at < 0) continue;
    // A character that survived is either itself or the one space a run of
    // whitespace collapsed to.
    expect(text[at] === raw[index] || (/\s/.test(raw[index]) && text[at] === " ")).toBe(true);
  }
});

it("gives a cell its own characters in the text layer", () => {
  const { grid, text } = jatsGrid(
    `<table-wrap><label>Table 1</label><caption><p>Scores</p></caption><table>` +
      `<thead><tr><th>Model</th><th>AUPRC</th></tr></thead>` +
      `<tbody><tr><td>GPN-Promoter</td><td>0.412</td></tr><tr><td>Nucleotide Transformer</td><td>0.388</td></tr></tbody>` +
      `</table></table-wrap>`,
  );
  expect(grid.tables).toHaveLength(1);
  const table = grid.tables[0];
  expect(table.rows).toBe(3);
  expect(table.columns).toBe(2);
  expect(table.header_rows).toBe(1);
  expect(table.headers).toEqual([["Model"], ["AUPRC"]]);
  expect(table.label?.text).toBe("Table 1");
  expect(table.caption?.text).toBe("Scores");
  expect(cellsAgree(grid, text)).toBe(6);

  const cell = cellRange(grid, 0, 1, 1);
  expect(cell?.text).toBe("0.412");
  expect(atPoints(text, cell?.start ?? 0, cell?.end ?? 0)).toBe("0.412");
  // The coordinate and the character range name one cell, which is the
  // whole contract.
  expect(cellAt(table, 2, 0)?.text).toBe("Nucleotide Transformer");
});

it("keeps a two level header as a path per column", () => {
  const { grid, text } = jatsGrid(
    `<table><thead>` +
      `<tr><th rowspan="2">Model</th><th colspan="2">ProteinGym</th><th colspan="2">ClinVar</th></tr>` +
      `<tr><th>AUPRC</th><th>Spearman</th><th>AUPRC</th><th>Spearman</th></tr>` +
      `</thead><tbody><tr><td>GPN</td><td>0.41</td><td>0.55</td><td>0.60</td><td>0.71</td></tr></tbody></table>`,
  );
  const table = grid.tables[0];
  expect(table.header_rows).toBe(2);
  expect(table.columns).toBe(5);
  expect(table.headers).toEqual([
    ["Model", "Model"],
    ["ProteinGym", "AUPRC"],
    ["ProteinGym", "Spearman"],
    ["ClinVar", "AUPRC"],
    ["ClinVar", "Spearman"],
  ]);
  // The two AUPRC columns are told apart by their path and by nothing else,
  // which is the case a flattened layer cannot represent at all.
  expect(cellRange(grid, 0, 2, 1)?.text).toBe("0.41");
  expect(cellRange(grid, 0, 2, 3)?.text).toBe("0.60");
  cellsAgree(grid, text);
});

it("expands a row span so the cells under it keep their columns", () => {
  const { grid, text } = jatsGrid(
    `<table><tbody>` +
      `<tr><td rowspan="2">Zero shot</td><td>GPN</td><td>0.41</td></tr>` +
      `<tr><td>Evo</td><td>0.52</td></tr>` +
      `</tbody></table>`,
  );
  const table = grid.tables[0];
  expect(table.columns).toBe(3);
  expect(cellRange(grid, 0, 1, 0)?.text).toBe("Zero shot");
  expect(cellRange(grid, 0, 1, 1)?.text).toBe("Evo");
  expect(cellRange(grid, 0, 1, 2)?.text).toBe("0.52");
  cellsAgree(grid, text);
});

it("holds no offsets for a cell that prints nothing", () => {
  const { grid } = jatsGrid(`<table><tbody><tr><td>GPN</td><td></td><td> </td></tr></tbody></table>`);
  const table = grid.tables[0];
  expect(table.cells).toHaveLength(3);
  expect(table.cells[1].start).toBeNull();
  expect(table.cells[1].text).toBe("");
  expect(table.cells[2].start).toBeNull();
  expect(cellRange(grid, 0, 0, 1)).toBeNull();
});

it("reports no header rows where the markup marks none", () => {
  const { grid } = jatsGrid(`<table><tbody><tr><td>Model</td><td>AUPRC</td></tr><tr><td>GPN</td><td>0.41</td></tr></tbody></table>`);
  expect(grid.tables[0].header_rows).toBe(0);
  expect(grid.tables[0].headers).toEqual([[], []]);
  // Two columns, so the rule declines: see the candidate header tests below.
  expect(grid.tables[0].inferred_header).toBeUndefined();
});

it("reads a header row written as th cells without a thead", () => {
  const { grid } = jatsGrid(`<table><tr><th>Model</th><th>AUPRC</th></tr><tr><td>GPN</td><td>0.41</td></tr></table>`);
  expect(grid.tables[0].header_rows).toBe(1);
  expect(grid.tables[0].headers).toEqual([["Model"], ["AUPRC"]]);
});

/** Two body rows, used by every candidate header test below so that what
 * changes between them is only the row the rule is being asked about. */
const body = `<tr><td>GPN</td><td>0.41</td><td>0.72</td></tr><tr><td>Evo</td><td>0.52</td><td>0.80</td></tr>`;

it("puts a header row the markup does not mark in a field of its own", () => {
  const { grid } = jatsGrid(`<table><tbody><tr><td>Model</td><td>AUPRC</td><td>AUROC</td></tr>${body}</tbody></table>`);
  const table = grid.tables[0];
  // The marked header is still empty, which is the whole point: a reader
  // and a resolver can always tell what the markup said from what was
  // inferred, and a resolver that will not act on an inference ignores one
  // field.
  expect(table.header_rows).toBe(0);
  expect(table.headers).toEqual([[], [], []]);
  expect(table.inferred_header).toEqual({ rule: "first-row@1", rows: 1, headers: [["Model"], ["AUPRC"], ["AUROC"]] });
});

it("records no candidate header where the markup marks one", () => {
  const { grid } = jatsGrid(
    `<table><thead><tr><th>Model</th><th>AUPRC</th><th>AUROC</th></tr></thead><tbody>${body}</tbody></table>`,
  );
  expect(grid.tables[0].header_rows).toBe(1);
  expect(grid.tables[0].inferred_header).toBeUndefined();
});

it("declines a candidate header where the first row prints values", () => {
  const { grid } = jatsGrid(`<table><tbody>${body}<tr><td>Caduceus</td><td>0.37</td><td>0.65</td></tr></tbody></table>`);
  const table = grid.tables[0];
  expect(table.inferred_header).toBeUndefined();
  expect(candidateHeader(table, { thead: false }).declined).toBe("first_row_prints_a_value");
});

it("declines a candidate header where the first row does not write a cell per column", () => {
  // The top level of a two level header. The column is named on the second
  // level, so taking the first would name a heading standing over three
  // columns and a resolver would have to choose between them.
  const { grid } = jatsGrid(
    `<table><tbody><tr><td></td><td colspan="2">Zero shot</td></tr>` +
      `<tr><td>Model</td><td>AUPRC</td><td>AUROC</td></tr>${body}</tbody></table>`,
  );
  const table = grid.tables[0];
  expect(table.columns).toBe(3);
  expect(table.inferred_header).toBeUndefined();
  expect(candidateHeader(table, { thead: false }).declined).toBe("first_row_incomplete");
});

it("declines a candidate header where a cell of the first row spans rows", () => {
  const { grid } = jatsGrid(
    `<table><tbody><tr><td rowspan="2">Model</td><td>AUPRC</td><td>AUROC</td></tr>` +
      `<tr><td>0.41</td><td>0.72</td></tr><tr><td>Evo</td><td>0.52</td><td>0.80</td></tr></tbody></table>`,
  );
  expect(grid.tables[0].inferred_header).toBeUndefined();
  expect(candidateHeader(grid.tables[0], { thead: false }).declined).toBe("first_row_spans");
});

it("declines a candidate header where the markup marks a header cell on another row", () => {
  const { grid } = jatsGrid(
    `<table><tbody><tr><td>Dataset</td><td>Split</td><td>Metric</td></tr>` +
      `<tr><th>Model</th><th>AUPRC</th><th>AUROC</th></tr>${body}</tbody></table>`,
  );
  const table = grid.tables[0];
  expect(table.header_rows).toBe(0);
  expect(table.inferred_header).toBeUndefined();
  expect(candidateHeader(table, { thead: false }).declined).toBe("marked_elsewhere");
});

it("declines a candidate header where the markup wrote a thead the first row is not in", () => {
  const { grid } = jatsGrid(
    `<table><thead></thead><tbody><tr><td>Model</td><td>AUPRC</td><td>AUROC</td></tr>${body}</tbody></table>`,
  );
  const table = grid.tables[0];
  expect(table.header_rows).toBe(0);
  expect(table.inferred_header).toBeUndefined();
  // The same rows with no thead are the candidate of the first test, so the
  // thead is the only reason this one has none. Markup that says where the
  // header is wins, even when it says it badly.
  expect(candidateHeader(table, { thead: true }).declined).toBe("marked_elsewhere");
  expect(candidateHeader(table, { thead: false }).header?.headers).toEqual([["Model"], ["AUPRC"], ["AUROC"]]);
});

it("declines a candidate header where no column below prints values", () => {
  const { grid } = jatsGrid(
    `<table><tbody><tr><td>Model</td><td>Code</td><td>Weights</td></tr>` +
      `<tr><td>GPN</td><td>github.com/a</td><td>zenodo.org/b</td></tr>` +
      `<tr><td>Evo</td><td>github.com/c</td><td>zenodo.org/d</td></tr></tbody></table>`,
  );
  expect(grid.tables[0].inferred_header).toBeUndefined();
  expect(candidateHeader(grid.tables[0], { thead: false }).declined).toBe("no_column_of_values_below");
});

it("declines a candidate header where the row below it is a second level of headings", () => {
  const { grid } = jatsGrid(
    `<table><tbody><tr><td>Dataset</td><td>Half life</td><td>Rate</td></tr>` +
      `<tr><td>Metric</td><td>Spearman</td><td>AUROC</td></tr>` +
      `<tr><td>RNA-FM</td><td>0.46</td><td>0.62</td></tr><tr><td>Saluki</td><td>0.67</td><td>0.58</td></tr></tbody></table>`,
  );
  expect(grid.tables[0].inferred_header).toBeUndefined();
  expect(candidateHeader(grid.tables[0], { thead: false }).declined).toBe("row_below_prints_no_value");
});

it("declines a candidate header for a two column table", () => {
  // A two column table is as often a list of keys and their values as a
  // table with a heading row, and the rule cannot tell the two apart.
  const { grid } = jatsGrid(
    `<table><tbody><tr><td>Hyperparameter</td><td>Value</td></tr>` +
      `<tr><td>learning rate</td><td>0.0005</td></tr><tr><td>layers</td><td>7</td></tr></tbody></table>`,
  );
  expect(grid.tables[0].inferred_header).toBeUndefined();
  expect(candidateHeader(grid.tables[0], { thead: false }).declined).toBe("too_few_columns");
});

it("writes nothing in the layer for a table with no candidate header", () => {
  // The field is absent rather than null, so every grid that gains no
  // candidate serialises to the bytes it did before the field existed and
  // keeps its hash.
  const { grid } = jatsGrid(
    `<table><thead><tr><th>Model</th><th>AUPRC</th><th>AUROC</th></tr></thead><tbody>${body}</tbody></table>`,
  );
  expect(serialiseGrid(grid)).not.toContain("inferred_header");
});

it("names the rule in the layer and reads it back", () => {
  const { grid } = jatsGrid(`<table><tbody><tr><td>Model</td><td>AUPRC</td><td>AUROC</td></tr>${body}</tbody></table>`);
  const bytes = serialiseGrid(grid);
  expect(bytes).toContain('"inferred_header":{"headers":[["Model"],["AUPRC"],["AUROC"]],"rows":1,"rule":"first-row@1"}');
  expect(readGrid(bytes).tables[0].inferred_header).toEqual(grid.tables[0].inferred_header);
});

it("tells a printed value from a heading", () => {
  // The test that keeps a data row out of the header field. It is whole
  // string: a heading often starts with a digit and a value never ends in a
  // word.
  for (const value of [
    "0.41",
    "1,234",
    "2.6M",
    "0.722 / 0.948",
    "76.1 {71.1\u201380.6}",
    "0.020 \u00b1 3e-4",
    "8.90E\u20101",
    "<0.001",
    "45.3%",
    "9.2 h",
    "-",
    "\u2713",
    "n/a",
  ])
    expect(printsValue(value)).toBe(true);
  for (const heading of [
    "Model",
    "AUPRC",
    "length 100",
    "19,237 raQTLs",
    "10-cl./binary",
    "Top-1",
    "Spearman r All",
    "M-KB (h)",
    "# Params",
    "Value",
  ])
    expect(printsValue(heading)).toBe(false);
});

it("counts offsets in code points, not in UTF-16 units", () => {
  const { grid, text } = jatsGrid(`<p>\u{1d4b1}\u{1d4b1}\u{1d4b1}</p><table><tr><td>0.41</td></tr></table>`);
  const cell = cellRange(grid, 0, 0, 0);
  expect(cell?.text).toBe("0.41");
  expect(atPoints(text, cell?.start ?? 0, cell?.end ?? 0)).toBe("0.41");
  // Three astral characters are three code points and six UTF-16 units, so
  // a span taken in the wrong system misses by three.
  expect(text.indexOf("0.41")).toBe((cell?.start ?? 0) + 3);
});

it("gives no grid for a document with no table", () => {
  const markup = `<?xml version="1.0"?><article><body><p>No tables here.</p></body></article>`;
  const input = Buffer.from(markup, "utf8");
  expect(gridLayer(input, xmlLayer(input))).toBeNull();
});

it("gives no grid for CALS markup rather than a wrong one", () => {
  // The store holds no CALS table. One would need namest, nameend and
  // morerows, and reading entry elements as though they were td would place
  // every span at one cell.
  const markup =
    `<?xml version="1.0"?><article><body><table-wrap><tgroup cols="2">` +
    `<tbody><row><entry>GPN</entry><entry>0.41</entry></row></tbody></tgroup></table-wrap></body></article>`;
  const input = Buffer.from(markup, "utf8");
  expect(gridLayer(input, xmlLayer(input))).toBeNull();
});

it("skips a table the HTML normaliser drops with its container", () => {
  const markup = `<html><body><nav><table><tr><td>Home</td><td>About</td></tr></table></nav><p>Body.</p></body></html>`;
  const input = Buffer.from(markup, "utf8");
  const text = htmlLayer(input);
  expect(text.bytes.toString("utf8")).not.toContain("About");
  expect(gridLayer(input, text)).toBeNull();
});

it("closes a cell and a row the markup leaves open", () => {
  const { grid, text } = jatsGrid(`<table><tr><td>GPN<td>0.41<tr><td>Evo<td>0.52</table>`);
  const table = grid.tables[0];
  expect(table.rows).toBe(2);
  expect(table.columns).toBe(2);
  expect(cellRange(grid, 0, 1, 1)?.text).toBe("0.52");
  cellsAgree(grid, text);
});

it("places a cell whose span is not a count of cells as one cell", () => {
  const { grid } = jatsGrid(`<table><tr><td colspan="many">A</td><td>B</td></tr></table>`);
  const table = grid.tables[0];
  expect(table.columns).toBe(2);
  expect(table.problems.join(" ")).toContain('colspan="many"');
});

it("stops a caption at the table rather than reading the rest of the document", () => {
  // The close tag is missing. A caption that ran on would take the whole
  // article with it and a resolver matching on captions would match
  // everything.
  const { grid } = jatsGrid(
    `<table-wrap><caption><p>Promoter benchmarks` +
      `<table><tr><th>Model</th></tr><tr><td>GPN</td></tr></table></table-wrap><p>Unrelated prose.</p>`,
  );
  expect(grid.tables[0].caption?.text).toBe("Promoter benchmarks");
});

it("round trips through its own bytes", () => {
  const { grid } = jatsGrid(
    `<table-wrap><label>Table 2</label><table><thead><tr><th>Model</th><th>AUPRC</th></tr></thead>` +
      `<tbody><tr><td>GPN</td><td>0.41</td></tr></tbody></table></table-wrap>`,
  );
  const body = serialiseGrid(grid);
  expect(readGrid(body)).toEqual(grid);
  expect(serialiseGrid(readGrid(body))).toBe(body);
});

it("hashes the same on a second derivation", () => {
  const input = fixture(jats);
  const text = xmlLayer(input);
  const first = gridLayer(input, text);
  const second = gridLayer(input, text);
  expect(first).not.toBeNull();
  expect(first?.output_sha256).toBe(second?.output_sha256);
  expect(first?.output_sha256).toBe(digest(first?.bytes as Buffer));
  expect(first?.identity).toBe(false);
});

it("carries the grid beside the text layer, never instead of it", () => {
  const node = layerOf(fixture(jats));
  expect(node.layer?.normaliser).toBe("europepmc-fulltext-xml@1");
  expect(node.grid?.normaliser).toBe("jats-table-grid@1");
  expect(node.grid?.output_sha256).not.toBe(node.layer?.output_sha256);
  const grid = readGrid(node.grid?.bytes.toString("utf8") as string);
  expect(grid.text_layer_sha256).toBe(node.layer?.output_sha256);
});

it("agrees with the text layer on every cell of a committed JATS article", () => {
  const input = fixture(jats);
  const text = xmlLayer(input).bytes.toString("utf8");
  const built = gridOf(scanSource(input), xmlRules, "jats-table-grid@1", "europepmc-fulltext-xml@1", "0".repeat(64));
  expect(built.text).toBe(text);
  expect(built.grid.tables.length).toBeGreaterThan(0);
  expect(cellsAgree(built.grid, text)).toBeGreaterThan(20);
});

it("agrees with the text layer on every cell of a committed HTML page", () => {
  const input = fixture(html);
  const text = htmlLayer(input).bytes.toString("utf8");
  const built = gridOf(scanSource(input), htmlRules, "html-table-grid@1", "html-text@1", "0".repeat(64));
  expect(built.text).toBe(text);
  expect(cellsAgree(built.grid, text)).toBeGreaterThan(0);
});

it("builds the layer text the normaliser builds, by the same scan", () => {
  const markup = `<?xml version="1.0"?><article><body><table><tr><td>a</td><td>b</td></tr></table></body></article>`;
  expect(scanMarkup(markup, xmlRules)).toBe(xmlLayer(Buffer.from(markup, "utf8")).bytes.toString("utf8"));
  const seen: string[] = [];
  scanMarkup(markup, xmlRules, { open: (name) => seen.push(name) });
  expect(seen).toEqual(["article", "body", "table", "tr", "td", "td"]);
});

it("finds the table by its caption, which is what a locator names", () => {
  const { grid } = jatsGrid(
    `<table-wrap><label>Table S8</label><caption><p>Promoter benchmarks</p></caption>` +
      `<table><tr><th>Model</th><th>AUPRC</th></tr><tr><td>GPN</td><td>0.41</td></tr></table></table-wrap>` +
      `<table-wrap><label>Table S9</label><table><tr><th>Model</th><th>AUPRC</th></tr><tr><td>GPN</td><td>0.99</td></tr></table></table-wrap>`,
  );
  expect(grid.tables.map((table) => table.label?.text)).toEqual(["Table S8", "Table S9"]);
  const wanted = grid.tables.find((table) => table.label?.text === "Table S8");
  expect(tableAt(grid, wanted?.index ?? -1)?.cells.some((cell) => cell.text === "0.41")).toBe(true);
});

it("registers the grid as a row of its own that reads back from the store", async () => {
  // The two calls a resolver makes: find the grid beside a text layer, and
  // read it. Both go through the registry and the object store, so they are
  // exercised against a store of one object rather than against the build.
  const root = temporaryRoot();
  const bytes = fixture(jats);
  const { key } = putObject(bytes, root);
  const manifestRow = manifestRowSchema.parse({
    sha256: key,
    bytes: bytes.length,
    media_type: "application/xml",
    layer: "exact-bytes",
    origin: "https://example.org/article.xml",
    requested_url: null,
    first_seen_at: "2026-11-18T09:00:00Z",
    store: "local-cache",
    visibility: "public",
    archive_tier: "t0-public",
    observed_licence: null,
    exposure: "policy",
    derived_from: null,
    derivation: null,
    previous_path: null,
    source_ids: ["source-one"],
  });
  await upsertRow(manifestRow, root);

  const records = layersOfObject(manifestRow, bytes).records;
  const text = records.find((record) => record.normaliser === "europepmc-fulltext-xml@1");
  const grid = records.find((record) => record.normaliser === "jats-table-grid@1");
  expect(text).toBeDefined();
  expect(grid).toBeDefined();
  expect(grid?.identity).toBe(false);
  expect(grid?.object_sha256).toBe(key);
  expect(grid?.source_ids).toEqual(["source-one"]);

  const read = readGrid(layerText(grid as NonNullable<typeof grid>, root));
  expect(read.text_layer_sha256).toBe(text?.layer_sha256);
  expect(read.tables.length).toBeGreaterThan(0);
  // The offsets in the row that was registered address the text layer that
  // was registered beside it, which is the whole reason both are rows.
  const layer = layerText(text as NonNullable<typeof text>, root);
  for (const table of read.tables) cellsAgree({ ...read, tables: [table] }, layer);
});

/** A committed artifact decoded the way the normaliser decodes it. */
function scanSource(input: Buffer): string {
  const encoding = encodingOf(input);
  if (!encoding) throw new Error("the fixture does not decode as text");
  return decode(input, encoding);
}
