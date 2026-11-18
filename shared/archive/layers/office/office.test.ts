/** The Office layer: detection from the central directory, the two
 * normalisers, the determinism the archive rests on, and the addressing a
 * claim needs.
 *
 * Fixtures are artifacts already committed under data/omics, expanded in
 * memory, plus small packages this file writes itself. The written ones are
 * there to prove the cases the committed corpus cannot: a package whose
 * [Content_Types].xml is the last member, a cell holding a tab, a sheet over
 * the row limit.
 *
 * Nothing here writes inside the tree and nothing here reaches the object
 * store, so the whole file runs on a fresh clone.
 */
import fs from "node:fs";
import zlib from "node:zlib";
import { createHash } from "node:crypto";
import { describe, expect, it } from "vitest";
import { classify } from "../classify";
import { layerOf } from "../index";
import { parseLocator } from "../../../omics/locator";
import { sliceSpan } from "../../../omics/layers/index";
import {
  cellRange,
  cellRangeByReference,
  columnLabel,
  columnNumber,
  detectOffice,
  escapeCell,
  officeLayer,
  parseReference,
  readPackage,
  readWorkbook,
  reference,
  rfc7111Fragment,
  serialiseDocument,
  serialiseWorkbook,
  sheetBlocks,
  sheetLimits,
  unescapeCell,
} from "./index";

const digest = (bytes: Buffer) => createHash("sha256").update(bytes).digest("hex");
const fixture = (file: string): Buffer => {
  const bytes = fs.readFileSync(file);
  return file.endsWith(".gz") ? zlib.gunzipSync(bytes) : bytes;
};

/** A committed workbook with one sheet, small enough to assert on. */
const smallWorkbook = "data/omics/use-case-coverage-cnv-20261009/artifacts/nardone2025-table-s1.xlsx.gz";
/** A committed macro enabled workbook. */
const macroWorkbook = "data/omics/feng-dna-fm-20261013/artifacts/MOESM3_ESM.xlsm.gz";
/** A committed Word supplement that is one table. */
const tableDocument = "data/omics/use-case-coverage-dna-pathogen-20261011-hu2026/artifacts/spectrum.03993-25-s0001.docx.gz";
/** The committed packages whose first local header does not name the
 * application. Two open at a drawing, one at docProps and one at the
 * relationships part, which names nothing at all. */
const firstHeaderUnhelpful = [
  "data/omics/gfm-guides-20261014-esm1b/artifacts/brandes2023-supplementary-table-2.xlsx.gz",
  "data/omics/gfm-guides-20261014-kedzierska2025/artifacts/kedzierska2025-additional-file-1.xlsx.gz",
  "data/omics/use-case-coverage-dna-pathogen-20261011-hu2026/artifacts/spectrum.03993-25-s0001.docx.gz",
  "data/omics/use-case-coverage-somatic-20261009/artifacts/guille2025-supplementary-methods.docx.gz",
];

// -------------------------------------------------------------------------
// A zip writer, so a test can control member order.

/** A zip holding the given members, stored rather than deflated, in the
 * order given. Enough of the format for the reader under test: local header,
 * data, central directory, end of central directory record. */
function zipOf(members: [string, string][]): Buffer {
  const locals: Buffer[] = [];
  const directory: Buffer[] = [];
  let offset = 0;
  for (const [name, content] of members) {
    const nameBytes = Buffer.from(name, "utf8");
    const data = Buffer.from(content, "utf8");
    const crc = zlib.crc32 ? zlib.crc32(data) : 0;
    const local = Buffer.alloc(30 + nameBytes.length);
    local.writeUInt32LE(0x04034b50, 0);
    local.writeUInt16LE(20, 4);
    local.writeUInt32LE(crc, 14);
    local.writeUInt32LE(data.length, 18);
    local.writeUInt32LE(data.length, 22);
    local.writeUInt16LE(nameBytes.length, 26);
    nameBytes.copy(local, 30);
    locals.push(local, data);

    const entry = Buffer.alloc(46 + nameBytes.length);
    entry.writeUInt32LE(0x02014b50, 0);
    entry.writeUInt16LE(20, 4);
    entry.writeUInt16LE(20, 6);
    entry.writeUInt32LE(crc, 16);
    entry.writeUInt32LE(data.length, 20);
    entry.writeUInt32LE(data.length, 24);
    entry.writeUInt16LE(nameBytes.length, 28);
    entry.writeUInt32LE(offset, 42);
    nameBytes.copy(entry, 46);
    directory.push(entry);
    offset += local.length + data.length;
  }
  const body = Buffer.concat(locals);
  const central = Buffer.concat(directory);
  const end = Buffer.alloc(22);
  end.writeUInt32LE(0x06054b50, 0);
  end.writeUInt16LE(members.length, 8);
  end.writeUInt16LE(members.length, 10);
  end.writeUInt32LE(central.length, 12);
  end.writeUInt32LE(body.length, 16);
  return Buffer.concat([body, central, end]);
}

const contentTypes = (main: string, part: string): string =>
  `<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">` +
  `<Default Extension="xml" ContentType="application/xml"/><Override PartName="${part}" ContentType="${main}"/></Types>`;

const spreadsheetMain = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml";

/** A one sheet workbook from a grid of cell references to values. */
function workbookOf(name: string, cells: Record<string, string>, order: "content-types-first" | "content-types-last" = "content-types-first"): Buffer {
  const rows = new Map<number, string[]>();
  for (const [ref, value] of Object.entries(cells)) {
    const parsed = parseReference(ref);
    if (!parsed) throw new Error(`${ref} is not a reference`);
    const row = rows.get(parsed.row) ?? [];
    row.push(`<c r="${ref}" t="inlineStr"><is><t xml:space="preserve">${value.replace(/&/g, "&amp;").replace(/</g, "&lt;")}</t></is></c>`);
    rows.set(parsed.row, row);
  }
  const sheetXml =
    `<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>` +
    [...rows.entries()].sort((a, b) => a[0] - b[0]).map(([number, cs]) => `<row r="${number}">${cs.join("")}</row>`).join("") +
    `</sheetData></worksheet>`;
  const workbookXml =
    `<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" ` +
    `xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>` +
    `<sheet name="${name}" sheetId="1" r:id="rId1"/></sheets></workbook>`;
  const relsXml =
    `<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">` +
    `<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>`;
  const parts: [string, string][] = [
    ["xl/drawings/drawing1.xml", "<?xml version=\"1.0\"?><wsDr/>"],
    ["xl/workbook.xml", workbookXml],
    ["xl/_rels/workbook.xml.rels", relsXml],
    ["xl/worksheets/sheet1.xml", sheetXml],
  ];
  const types: [string, string] = ["[Content_Types].xml", contentTypes(spreadsheetMain, "/xl/workbook.xml")];
  return zipOf(order === "content-types-first" ? [types, ...parts] : [...parts, types]);
}

// -------------------------------------------------------------------------

describe("detection", () => {
  it("reads the kind from the central directory, not from the first local header", () => {
    const last = workbookOf("Sheet1", { A1: "value" }, "content-types-last");
    // The first member is a drawing, which names no application.
    const firstName = last.subarray(30, 30 + last.readUInt16LE(26)).toString("utf8");
    expect(firstName).toBe("xl/drawings/drawing1.xml");
    expect(detectOffice(last)?.kind).toBe("xlsx");
    expect(classify(last).class).toBe("office");
    expect(classify(last).media_type).toBe("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
    expect(readPackage(last)?.evidence).toBe(`[Content_Types].xml declares ${spreadsheetMain}`);
  });

  it("identifies the committed packages whose first local header names nothing useful", () => {
    for (const file of firstHeaderUnhelpful) {
      if (!fs.existsSync(file)) continue;
      const bytes = fixture(file);
      const first = bytes.subarray(30, 30 + bytes.readUInt16LE(26)).toString("utf8");
      expect(first).not.toBe("[Content_Types].xml");
      const detected = detectOffice(bytes);
      expect(detected).not.toBeNull();
      expect(["xlsx", "xlsm", "docx"]).toContain(detected!.kind);
      expect(readPackage(bytes)!.kind).toBe(detected!.kind);
    }
  });

  it("leaves a plain zip to the container reader", () => {
    const plain = zipOf([["readme.txt", "nothing here"], ["data/one.csv", "a,b\n1,2\n"]]);
    expect(detectOffice(plain)).toBeNull();
    expect(classify(plain).class).toBe("container");
  });

  it("reports a presentation rather than guessing a layer for it", () => {
    const main = "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml";
    const deck = zipOf([
      ["ppt/presentation.xml", "<?xml version=\"1.0\"?><presentation/>"],
      ["[Content_Types].xml", contentTypes(main, "/ppt/presentation.xml")],
    ]);
    expect(detectOffice(deck)?.kind).toBe("pptx");
    expect(classify(deck).unsupported).toBe("office presentation package, no normaliser");
    expect(layerOf(deck, { pdftotext: false }).layer).toBeNull();
    expect(layerOf(deck, { pdftotext: false }).unsupported).toBe("office presentation package, no normaliser");
  });
});

describe("the sheet layer", () => {
  it("produces the same layer hash from the same bytes", () => {
    for (const file of [smallWorkbook, macroWorkbook, tableDocument]) {
      if (!fs.existsSync(file)) continue;
      const bytes = fixture(file);
      const first = officeLayer(bytes);
      const second = officeLayer(bytes);
      expect(first?.layer).not.toBeNull();
      expect(first!.layer!.output_sha256).toBe(second!.layer!.output_sha256);
      expect(first!.layer!.output_sha256).toBe(digest(first!.layer!.bytes));
      expect(first!.layer!.input_sha256).toBe(digest(bytes));
      expect(first!.layer!.identity).toBe(false);
    }
  });

  it("keeps the stored text of a value and applies no number formatting", () => {
    const pkg = readPackage(workbookOf("S", { A1: "0.10", B1: "1E-05", C1: "0001" }))!;
    const problems: string[] = [];
    const [sheet] = readWorkbook(pkg, problems);
    expect(problems).toEqual([]);
    expect(sheet.cells.map((cell) => cell.value)).toEqual(["0.10", "1E-05", "0001"]);
    expect(serialiseWorkbook([sheet])).toBe("\f# sheet\t1\tS\tA1:C1\n0.10\t1E-05\t0001\n");
  });

  it("escapes a value that would otherwise break the grid, reversibly", () => {
    const awkward = "one\ttwo\nthree\\four";
    expect(escapeCell(awkward)).toBe("one\\ttwo\\nthree\\\\four");
    expect(unescapeCell(escapeCell(awkward))).toBe(awkward);
    expect(escapeCell("bell\u0007")).toBe("bell\\x07");
    expect(unescapeCell("bell\\x07")).toBe("bell\u0007");
    const layer = officeLayer(workbookOf("S", { A1: awkward, B1: "after" }))!.layer!;
    const text = layer.bytes.toString("utf8");
    expect(text.split("\n")).toHaveLength(3);
    expect(cellRangeByReference(text, "S", "B1")!.value).toBe("after");
    expect(cellRangeByReference(text, "S", "A1")!.value).toBe(awkward);
  });

  it("counts one form feed per sheet and one line per row", () => {
    const bytes = fixture(smallWorkbook);
    const text = officeLayer(bytes)!.layer!.bytes.toString("utf8");
    const blocks = sheetBlocks(text);
    expect(blocks).toHaveLength(1);
    expect(blocks[0].index).toBe(1);
    expect(blocks[0].name).toBe("TableS1");
    expect(blocks[0].range).toBe("A1:I84");
    expect(blocks[0].header_line).toBe(0);
    expect(blocks[0].rows).toBe(84);
    expect([...text].filter((character) => character === "\f")).toHaveLength(1);
  });

  it("refuses a sheet past the row limit instead of truncating it", () => {
    const cells: Record<string, string> = { A1: "head" };
    cells[`A${sheetLimits.rowsPerSheet + 1}`] = "tail";
    const result = officeLayer(workbookOf("Wide", cells))!;
    expect(result.layer).toBeNull();
    expect(result.unsupported).toContain("over the 250000 row limit");
  });
});

describe("addressing", () => {
  it("maps an A1 reference onto the character range of its field", () => {
    const bytes = fixture(smallWorkbook);
    const layer = officeLayer(bytes)!.layer!;
    const text = layer.bytes.toString("utf8");
    const pkg = readPackage(bytes)!;
    const problems: string[] = [];
    const [sheet] = readWorkbook(pkg, problems);
    expect(problems).toEqual([]);

    // Every cell the workbook holds resolves to its own value, through the
    // layer text alone.
    for (const cell of sheet.cells) {
      const range = cellRange(text, sheet.name, cell.row, cell.column);
      expect(range, `${reference(cell.row, cell.column)}`).not.toBeNull();
      expect(range!.value).toBe(cell.value);
      // And the code point offsets agree with the span slicer the registry
      // hands to a resolver.
      expect(sliceSpan(text, range!.start, range!.end).exact).toBe(range!.field);
    }
  });

  it("gives the RFC 7111 reading of the same cell", () => {
    const text = officeLayer(workbookOf("S", { A1: "a", B1: "b", A7: "g", B7: "h" }))!.layer!.bytes.toString("utf8");
    const range = cellRangeByReference(text, "S", "B7")!;
    expect(range.value).toBe("h");
    // The header is layer line 0, so sheet row 7 is layer line 7 and RFC 7111
    // record 8. Column B is field 2.
    expect(range.line).toBe(7);
    expect(range.field_number).toBe(2);
    expect(rfc7111Fragment(range)).toBe("#cell=8,2");
  });

  it("resolves the locator grammar's own spreadsheet forms over a committed workbook", () => {
    const text = officeLayer(fixture(smallWorkbook))!.layer!.bytes.toString("utf8");
    // Row 4 of the committed sheet is the header and row 5 the first data
    // row: Lumpy, DEL, 50-99.
    for (const printed of ["sheet 'TableS1', cell C5", "'TableS1'!C5"]) {
      const parsed = parseLocator(printed);
      const anchor = parsed.anchors.find((candidate) => candidate.kind === "sheet");
      const address = parsed.addresses.find((candidate) => candidate.kind === "sheet_cell");
      expect(anchor?.value, printed).toBe("TableS1");
      expect(address?.value, printed).toBe("C5");
      const range = cellRangeByReference(text, anchor!.value, address!.value)!;
      expect(range.value, printed).toBe("50-99");
      expect(sliceSpan(text, range.start, range.end).exact).toBe("50-99");
      expect(rfc7111Fragment(range)).toBe("#cell=6,3");
    }
  });

  it("counts offsets in code points, which a JavaScript index is not", () => {
    // U+1D70E sits outside the basic plane, so it is one code point and two
    // UTF-16 units. Everything after it in the layer has a JavaScript index
    // one higher than its offset, which is the whole reason a span is
    // counted this way.
    const text = officeLayer(workbookOf("S", { A1: "\u{1D70E} = 0.3", B1: "0.412" }))!.layer!.bytes.toString("utf8");
    const range = cellRangeByReference(text, "S", "B1")!;
    expect(range.value).toBe("0.412");
    expect(text.indexOf("0.412")).toBe(range.start + 1);
    expect(sliceSpan(text, range.start, range.end).exact).toBe("0.412");
    // And the cell holding the astral character slices back whole.
    const first = cellRangeByReference(text, "S", "A1")!;
    expect(sliceSpan(text, first.start, first.end).exact).toBe("\u{1D70E} = 0.3");
  });

  it("counts a column label the way A1 does", () => {
    expect(columnNumber("A")).toBe(1);
    expect(columnNumber("Z")).toBe(26);
    expect(columnNumber("AA")).toBe(27);
    expect(columnNumber("XFD")).toBe(16384);
    for (const column of [1, 26, 27, 52, 53, 702, 703, 16384]) expect(columnNumber(columnLabel(column))).toBe(column);
    expect(parseReference("$B$12")).toEqual({ row: 12, column: 2 });
    expect(parseReference("12B")).toBeNull();
  });

  it("returns nothing for a cell the sheet does not hold", () => {
    const text = officeLayer(workbookOf("S", { A1: "only" }))!.layer!.bytes.toString("utf8");
    expect(cellRangeByReference(text, "S", "A2")).toBeNull();
    expect(cellRangeByReference(text, "S", "B1")).toBeNull();
    expect(cellRangeByReference(text, "Missing", "A1")).toBeNull();
  });
});

describe("the document layer", () => {
  it("keeps a table as tab separated rows", () => {
    const body =
      `<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>` +
      `<w:p><w:r><w:t>Supplemental Table 1.</w:t></w:r></w:p>` +
      `<w:tbl><w:tr><w:tc><w:p><w:r><w:t>Model</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>AUPRC</w:t></w:r></w:p></w:tc></w:tr>` +
      `<w:tr><w:tc><w:p><w:r><w:t>GPN</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>0.412</w:t></w:r></w:p></w:tc></w:tr></w:tbl>` +
      `</w:body></w:document>`;
    expect(serialiseDocument(body)).toBe("Supplemental Table 1.\nModel\tAUPRC\nGPN\t0.412\n");
  });

  it("leaves out field codes and deleted text", () => {
    const body =
      `<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>` +
      `<w:p><w:r><w:t>kept </w:t></w:r><w:r><w:instrText>REF _Ref1 \\h</w:instrText></w:r>` +
      `<w:del><w:r><w:delText>removed</w:delText></w:r></w:del><w:r><w:t>text</w:t></w:r></w:p>` +
      `</w:body></w:document>`;
    expect(serialiseDocument(body)).toBe("kept text\n");
  });

  it("joins the paragraphs of one cell rather than splitting the row", () => {
    const body =
      `<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>` +
      `<w:tbl><w:tr><w:tc><w:p><w:r><w:t>first</w:t></w:r></w:p><w:p><w:r><w:t>second</w:t></w:r></w:p></w:tc>` +
      `<w:tc><w:p><w:r><w:t>one</w:t></w:r></w:p></w:tc></w:tr></w:tbl></w:body></w:document>`;
    expect(serialiseDocument(body)).toBe("first second\tone\n");
  });

  it("reads a committed Word supplement as rows a reader can count", () => {
    if (!fs.existsSync(tableDocument)) return;
    const layer = officeLayer(fixture(tableDocument))!.layer!;
    const lines = layer.bytes.toString("utf8").split("\n");
    expect(lines[0]).toBe("Supplemental Table 1. Detection of D1 and D2 Communities on Illumina, MGI, ONT and HD-ONT Platforms");
    expect(lines[1].split("\t")[0]).toBe("Reference group");
    expect(lines[1].split("\t")).toHaveLength(9);
  });
});

describe("the whole pipeline", () => {
  it("gives a package one layer of its own and no member objects", () => {
    const bytes = fixture(smallWorkbook);
    const node = layerOf(bytes, { pdftotext: false });
    expect(node.classification.class).toBe("office");
    expect(node.members).toEqual([]);
    expect(node.unsupported).toBeNull();
    expect(node.problems).toEqual([]);
    expect(node.layer?.normaliser).toBe("ooxml-sheet-tsv@1");
    expect(node.layer?.derivation).toBe("ooxml-sheet-tsv@1 stored cell values, one tab separated block per sheet");
  });

  it("reads a macro enabled workbook with the spreadsheet normaliser", () => {
    if (!fs.existsSync(macroWorkbook)) return;
    const result = officeLayer(fixture(macroWorkbook))!;
    expect(result.kind).toBe("xlsm");
    expect(result.layer?.normaliser).toBe("ooxml-sheet-tsv@1");
    expect(result.layer!.characters).toBeGreaterThan(0);
  });
});
