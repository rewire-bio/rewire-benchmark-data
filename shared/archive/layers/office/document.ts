/** ooxml-document-text@1: a Word document to text, with its tables kept as
 * rows.
 *
 * Nine of the Office packages in the store are Word documents and every one
 * of them is a supplementary table: `sm_table_2_r1_bbac019.docx`,
 * `spectrum.03993-25-s0001.docx` and the rest. A normaliser that flattened a
 * table into a paragraph would make those numbers unaddressable, so a table
 * is serialised the same way a worksheet is: one line per row, one tab
 * separated field per cell, the same escaping. A reader addresses a cell by
 * the line and the field, which is what RFC 7111 defines for a delimited
 * file. There is no A1 origin, because a Word table has no sheet and no
 * column letters.
 *
 * What is read: `word/document.xml`, in document order, and nothing else.
 * Headers, footers, footnotes, endnotes and comments live in their own parts
 * and are left out, because they are not the document body and including
 * them would put text in the layer that no reader sees in that position.
 *
 * What is left out of the body, and why. `w:instrText` is field instruction
 * code, not text. `w:delText` is text a tracked change deleted, so it is not
 * in the document as it reads. `mc:Fallback` is the alternate rendering of
 * content that `mc:Choice` already supplied, so keeping it would double the
 * text. `w:rPh` has no counterpart here.
 *
 * Nothing is trimmed, collapsed or normalised beyond that. A paragraph's
 * characters are the characters its runs hold.
 */
import { layerFromText } from "../text";
import type { Layer } from "../types";
import { escapeCell } from "./sheet";
import { part, type OfficePackage } from "./package";
import { scanXml } from "./xml";

/** Discarded with their content. */
const skip = new Set(["instrtext", "deltext", "fallback"]);

/** The body part of a Word package. */
export const bodyPart = "word/document.xml";

/**
 * The document, serialised.
 *
 * A paragraph outside a table is a line. A table is a block of lines, one per
 * row, with the cells tab separated. A paragraph inside a cell joins the
 * cell's other paragraphs with a single space, so that a cell stays one
 * field. `w:tab` and `w:br` inside a cell are a space for the same reason,
 * and outside a cell `w:br` is a line.
 */
export function serialiseDocument(text: string): string {
  const lines: string[] = [];
  /** Characters of the line being built, outside a table. */
  let line: string[] = [];
  /** Fields of the table row being built, innermost table first. */
  const rows: string[][] = [];
  /** Characters of the cell being built, innermost cell first. */
  const cells: string[][] = [];
  let skipping = 0;
  let inText = 0;

  const current = (): string[] => (cells.length > 0 ? cells[cells.length - 1] : line);
  const endLine = (): void => {
    lines.push(line.join(""));
    line = [];
  };

  scanXml(text, {
    open(name, attributes) {
      if (skip.has(name)) { skipping += 1; return; }
      if (skipping > 0) return;
      if (name === "t") { inText += 1; return; }
      if (name === "tr") { rows.push([]); return; }
      if (name === "tc") { cells.push([]); return; }
      // A space, never a literal tab: a tab in a prose line would make that
      // line look like a table row to a reader counting fields.
      if (name === "tab") { current().push(" "); return; }
      if (name === "br" || name === "cr") {
        if (cells.length > 0) current().push(" ");
        else endLine();
        return;
      }
      if (name === "nobreakhyphen") { current().push("‑"); return; }
      if (name === "softhyphen") { current().push("­"); return; }
      if (name === "sym" && attributes.char) {
        const code = Number.parseInt(attributes.char, 16);
        if (Number.isFinite(code) && code > 0 && code <= 0x10ffff) current().push(String.fromCodePoint(code));
      }
    },
    close(name) {
      if (skip.has(name)) { skipping = Math.max(0, skipping - 1); return; }
      if (skipping > 0) return;
      if (name === "t") { inText = Math.max(0, inText - 1); return; }
      if (name === "p") {
        // A paragraph inside a cell keeps the cell on one line.
        if (cells.length > 0) {
          const cell = cells[cells.length - 1];
          if (cell.length > 0 && cell[cell.length - 1] !== " ") cell.push(" ");
        } else endLine();
        return;
      }
      if (name === "tc") {
        const cell = cells.pop() ?? [];
        const row = rows[rows.length - 1];
        const field = escapeCell(cell.join("").replace(/ $/, ""));
        if (row) row.push(field);
        else current().push(field);
        return;
      }
      if (name === "tr") {
        const row = rows.pop() ?? [];
        while (row.length > 0 && row[row.length - 1] === "") row.pop();
        const rendered = row.join("\t");
        if (cells.length > 0) current().push(rendered);
        else lines.push(rendered);
        return;
      }
    },
    text(value) {
      if (skipping === 0 && inText > 0) current().push(value);
    },
  });
  if (line.length > 0) endLine();
  return lines.length > 0 ? `${lines.join("\n")}\n` : "";
}

/** The text layer of a Word document. */
export function documentLayer(input: Buffer, pkg: OfficePackage, problems: string[]): Layer {
  const body = part(pkg, bodyPart);
  if (body === null) throw new Error(`the package holds no ${bodyPart}`);
  const text = serialiseDocument(body);
  if (text === "") problems.push(`${bodyPart} holds no text`);
  return layerFromText(
    input,
    text,
    "ooxml-document-text@1",
    "ooxml-document-text@1 word/document.xml in document order, tables as tab separated rows",
  );
}
