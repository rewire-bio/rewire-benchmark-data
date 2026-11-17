/** C3: numeric_value against printed_value.
 *
 * The parser is parseCell from scripts/omics/extract/tables.ts, the same function the
 * extractors read cells with. Using it rather than a fresh regex is the whole point of this
 * check: parseCell already handles the Unicode minus sign and the other dashes, mathematical
 * bold digits, the x10^n form, thousands separators, footnote marks, and the "value plus or
 * minus spread" and "value (spread)" shapes. A regex written here would disagree with the
 * extractors, and the disagreement would be reported as a defect in the store.
 *
 * The printed percent sign is only stripped when the result's own unit is percent, because
 * that is the one case parseCell accepts it in, and because silently turning a percent into a
 * fraction is the error this check is looking for rather than a step it should take.
 *
 * Five rules:
 *
 * differs. Both values parse, they are not the same number, and none of the explanations below
 *   applies. This is the queue to read first.
 * numeric-is-the-second-number. The printed cell holds two numbers, as "45 (59.2%)" or
 *   "4,205 (264)" do, and the stored numeric value is the second one. The record is readable
 *   and may well be right, but printed_value and numeric_value are then not the same quantity,
 *   which is what a reader comparing the two would assume.
 * printed-is-rounded. The numeric value rounds, half up at the printed value's own number of
 *   decimal places, to the printed value. Recorded apart from the rest because it is the one
 *   disagreement with an innocent explanation: a paper prints three decimals and the recorded
 *   value came from the source data file behind the table. It is still reported, because
 *   nothing in the store says which of the two a reader should quote, and most of these
 *   records do carry printed_value_basis to say so.
 * rescaled-by-100. A disagreement that is exactly a factor of 100, reported apart from the
 *   rest because it is the unit mistake, not a transcription mistake.
 * unparseable-printed. parseCell refuses the printed value, or reads it as not reported.
 *   Mostly printed values that hold more than a number: a confidence interval, a unit suffix,
 *   a count beside a percentage, a spread parseCell cannot read.
 * numeric-not-a-number. numeric_value is present and is not a finite number.
 *
 * The prototype figure of 170 did not reproduce and was not inherited. Neither did the other
 * two figures in circulation (a strict check gave 1,640, a naive half-up check 603). What this
 * implementation measures is in data/omics/checks-baseline.json.
 *
 * Comparison is at a relative tolerance of 1e-12. Both sides come from decimal strings, so an
 * honest agreement is normally bit identical; the tolerance only absorbs the last-place noise
 * of two different decimal spellings of one number, such as 9e-4 against 9x10^-4.
 */
import { parseCell } from "../extract/tables";
import type { Check, CheckInput, Finding } from "./finding";
import { text } from "./finding";

const TOLERANCE = 1e-12;

const same = (a: number, b: number): boolean => a === b || Math.abs(a - b) <= Math.max(Math.abs(a), Math.abs(b)) * TOLERANCE;

/** Does `value` round, half up, to the decimal `printed` at the precision `printed` is written
 * to? E notation is left out: the printed precision of 4.03e-04 is not read off its digits. */
function roundsTo(value: number, printed: string): boolean {
  if (/[eE]/.test(printed)) return false;
  const places = printed.includes(".") ? printed.split(".")[1].length : 0;
  const scale = 10 ** places;
  const rounded = Math.sign(value) * Math.round(Math.abs(value) * scale) / scale;
  return same(rounded, Number(printed));
}

export const printedVsNumeric: Check = {
  id: "C3",
  title: "printed value against numeric value",
  rules: ["differs", "numeric-is-the-second-number", "printed-is-rounded", "rescaled-by-100", "unparseable-printed", "numeric-not-a-number"],
  run({ results }: CheckInput): Finding[] {
    const findings: Finding[] = [];
    for (const record of results) {
      const printed = text(record, "printed_value");
      const numeric = text(record, "numeric_value");
      const unit = text(record, "unit");
      if (printed === undefined || numeric === undefined) continue;
      // Which fields the triage will want to split the queue by: a display-rounded workbook
      // cell and a declared printed_value_basis are the two innocent explanations.
      const context = [
        record.attributes.printed_value_basis !== undefined ? "has printed_value_basis" : "",
        record.attributes.workbook_number_format !== undefined ? "has workbook_number_format" : "",
      ].filter(Boolean).join("; ");
      const suffix = context ? `; ${context}` : "";
      const want = Number(numeric);
      if (!Number.isFinite(want)) {
        findings.push({
          check: "C3",
          rule: "numeric-not-a-number",
          severity: "report",
          subject: record.id,
          detail: `numeric_value ${JSON.stringify(numeric)} is not a finite number; printed_value ${JSON.stringify(printed)}${suffix}`,
        });
        continue;
      }
      let value: string | null;
      let spread: string | null = null;
      try {
        const cell = parseCell(printed, unit === "percent" ? { unit: "percent" } : {});
        value = cell.value;
        spread = cell.sd;
      } catch (error) {
        findings.push({
          check: "C3",
          rule: "unparseable-printed",
          severity: "report",
          subject: record.id,
          detail: `parseCell refuses printed_value ${JSON.stringify(printed)} (unit ${unit ?? "none"}): ${(error as Error).message}${suffix}`,
        });
        continue;
      }
      // A cell parseCell reads as not reported, such as a dash, carries no number to compare.
      if (value === null) {
        findings.push({
          check: "C3",
          rule: "unparseable-printed",
          severity: "report",
          subject: record.id,
          detail: `parseCell reads printed_value ${JSON.stringify(printed)} as not reported, but numeric_value is ${numeric}${suffix}`,
        });
        continue;
      }
      const got = Number(value);
      if (same(got, want)) continue;
      const rule = same(got * 100, want) || same(got / 100, want)
        ? "rescaled-by-100"
        : roundsTo(want, value)
          ? "printed-is-rounded"
          : spread !== null && same(Number(spread), want)
            ? "numeric-is-the-second-number"
            : "differs";
      findings.push({
        check: "C3",
        rule,
        severity: "report",
        subject: record.id,
        detail: `printed_value ${JSON.stringify(printed)} reads as ${got}; numeric_value is ${numeric} (unit ${unit ?? "none"})${suffix}`,
      });
    }
    return findings;
  },
  context({ results }: CheckInput): Record<string, number> {
    let compared = 0;
    let noNumeric = 0;
    for (const record of results) {
      const printed = text(record, "printed_value");
      const numeric = text(record, "numeric_value");
      if (printed !== undefined && numeric !== undefined) compared += 1;
      else noNumeric += 1;
    }
    return { results_with_both_values: compared, results_skipped: noNumeric };
  },
};
