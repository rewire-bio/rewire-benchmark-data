/** How wide a cell span is allowed to be, and what to do when the layer prints no boundary.
 *
 * `pdftotext -layout` separates two columns with two or more spaces, and the table resolver
 * splits a line on exactly that. The separator is a property of the rendering and not of the
 * table: where two columns sit close together, or where one of them prints a long value, the
 * renderer leaves a single space between them and the two columns arrive as one field. The
 * resolver then returns that field, and the span covers several columns while naming one.
 *
 * Measured on 2026-11-18: 66 of the 7,345 spans that print the stored value are a table cell
 * whose field runs across more than one column. The worst of them covers three models' results
 * with the stored value in the middle, and a containment check scores it correct. It is not a
 * cell span, and a span that is not a cell span cannot defend the value it is supposed to check.
 *
 * This module answers one question: does the picked field sit in one column? Where it does not,
 * the answer is a refusal and not a narrower span.
 *
 * Narrowing was built and measured before it was removed. Taking the single run of characters
 * under the named column's band fired on 9 of the 66 and returned the neighbouring column's
 * number on 4 of those 9: on the datta2026 layer a column prints "X +/- Y / Z / N" with single
 * spaces inside it, so the runs of the joined field do not line up with the columns, and the one
 * run under the band belongs to the column before it. Where the layer prints no boundary, no
 * amount of arithmetic puts one there, and a span that holds the wrong column's number while
 * naming this one is the failure this lane exists to prevent.
 *
 * All offsets here are relative to the start of their own line. A header line and a row line
 * begin at different places in the layer, so comparing layer offsets between them is meaningless.
 */

/** A horizontal extent on a line: half open, in UTF-16 units from the line's first character. */
export interface Extent {
  from: number;
  to: number;
}

/** Do two extents share any horizontal position? Touching end to end is not sharing. */
export const overlap = (a: Extent, b: Extent): boolean => a.from < b.to && b.from < a.to;

/** What the width check decided: the field is one cell, or it is not a cell at all. */
export type Width = { ok: true } | { ok: false; detail: string };

/** The runs of non-space characters in a field, with their positions on the line.
 *
 * A field holds no run of two or more spaces, so its only internal separator is a single space.
 * That is the smallest boundary the layer states, and it is the only one a narrowing may use.
 */
export function tokensOf(field: { text: string; from: number }): Extent[] {
  const found: Extent[] = [];
  const pattern = /[^ ]+/g;
  let match: RegExpExecArray | null;
  while ((match = pattern.exec(field.text)) !== null)
    found.push({ from: field.from + match.index, to: field.from + match.index + match[0].length });
  return found;
}

/**
 * Is the picked field one cell, or several columns the renderer joined?
 *
 * `bands` are the header level's fields on their own line, `at` is the one the locator named, and
 * `field` is the row's field the geometry picked. Everything is line relative.
 *
 * The field runs across more than one column when two of its runs of characters sit under two
 * different header bands. That is the whole test, and it is a statement about the layer rather
 * than about the value: one run under this column and another under the next means the renderer
 * printed two columns as one field, whatever either of them holds.
 *
 * A field wider than its own heading is not caught by it and should not be. A cell printing
 * "0.991 +/- 0.003" under a heading reading "AUROC" is one cell, and the whole of it is the
 * cell, however far past the heading it reaches: it is caught only if one of its runs lands
 * under the next heading, which is the case where the field could be two cells instead of one.
 */
export function cellWidth(input: { bands: Extent[]; at: number; field: { text: string; from: number; to: number } }): Width {
  const { bands, field } = input;
  const crossed = new Set<number>();
  for (const token of tokensOf(field)) {
    const band = bands.findIndex((extent) => overlap(token, extent));
    if (band >= 0) crossed.add(band);
  }
  if (crossed.size <= 1) return { ok: true };
  return {
    ok: false,
    detail: `the field runs across ${crossed.size} columns, and the layer prints no boundary inside it that says which part is the cell`,
  };
}
