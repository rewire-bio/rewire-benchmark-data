/** Reading the number out of one printed cell, and what to do with the text printed beside it.
 *
 * `parseCell` is the reader the hand-written extraction scripts have always used, and it is
 * strict in two ways that are right for a caller filling a standard deviation field and wrong
 * for this pass.
 *
 * It refuses a cell whose tail is not itself one number: `4.66 (3.77-5.77)`,
 * `0.52 (95% CI 0.48-0.56)`, `0.9715 (0.9714–0.9716)`. This pass does not have to read the
 * tail. It puts it in `uncertainty_printed` verbatim and decides nothing about it.
 *
 * It refuses a cell carrying a percent sign unless the caller already knows the column is a
 * percentage, so that nothing silently turns a percentage into a fraction. This pass converts
 * nothing either: the printed value keeps the sign, the number keeps the digits the document
 * prints, and `printedUnit` reads the sign as the unit.
 *
 * Measured against the store on 2026-11-19, before this file existed, both passes caught those
 * refusals and dropped the cell. 1,357 stored results sat on a cell the extractor had read and
 * dropped; reading the tail recovered 1,153 of them and reading the percent sign recovered a
 * further 96, leaving 108. maintenance/reports/extract-vs-store-2026-11-19.md has the run.
 *
 * So the rule here is: try `parseCell`; where it refuses, try again knowing the cell prints a
 * percent sign; where it still refuses, accept a cell that is one number followed by one
 * bracketed or `±` tail and read the head through the same reader. Nothing is interpreted. A
 * cell that is not one of those shapes is still refused, which keeps `[0.011, 0.031]`,
 * `≤ 0.070`, `12.69 Å` and a sentence out: none of those prints a point value this pass can
 * read without deciding what the document means.
 */
import { parseCell } from "../../../scripts/omics/extract/tables";

/** One number and one tail: `4.66 (3.77-5.77)`, `0.82 ± 0.01`, `12 (95% CI 10-14)`.
 *
 * The head may not itself contain a bracket or a `±`, so a cell printing two brackets is not
 * this shape and is refused. */
const HEAD_AND_TAIL = /^([^(\[±]+?)\s*(?:±\s*(.+)|\((.+)\))$/;

export interface CellValue {
  /** The head as a decimal string, on the scale the document prints it. */
  value: string;
  /** The text printed beside it, verbatim, or null where the cell prints only the number. */
  spread: string | null;
}

interface Parsed {
  value: string | null;
  sd: string | null;
}

/** `parseCell`, with its refusal returned rather than thrown, and a second attempt that tells
 * it the cell prints a percent sign. The second attempt only removes a trailing sign from the
 * spelling. It never multiplies or divides. */
function read(text: string): Parsed | null {
  try {
    return parseCell(text);
  } catch {
    if (!/%\s*$/.test(text.trim())) return null;
    try {
      return parseCell(text, { unit: "percent" });
    } catch {
      return null;
    }
  }
}

/** The number a cell prints and the text beside it, or null where the cell prints no number.
 *
 * Null covers four different facts and the caller counts them as one, `cells_not_numeric`: a
 * dash or an `N/A`, which `parseCell` reads as not reported; a cell printing an interval or a
 * bound and no point value; a cell printing a number with a unit this pass has no rule for;
 * and a cell printing words. */
export function readCellValue(printed: string): CellValue | null {
  const whole = read(printed);
  if (whole) return whole.value === null ? null : { value: whole.value, spread: whole.sd };
  const match = HEAD_AND_TAIL.exec(printed.replace(/\s+/g, " ").trim());
  if (!match) return null;
  const head = read(match[1].trim());
  if (!head || head.value === null) return null;
  const tail = (match[2] ?? match[3] ?? "").trim();
  return { value: head.value, spread: tail === "" ? null : tail };
}
