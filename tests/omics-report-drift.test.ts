/** A committed figure has to be what the code produces now.
 *
 * Three phases of this work have shipped a document whose numbers were already wrong. The layer
 * registry report went stale in the first, the span resolution report in the second, and in the
 * third a correction block in ADR 0002 was stale within the hour of being written. Each time the
 * measurement was re-run, the prose was not, and nothing failed.
 *
 * This file is what fails. It holds three things to each other, and it does not re-run any
 * measurement to do it:
 *
 *   1. Every figure a document tags prints the value `span-resolution-figures.json` records.
 *   2. The committed tables beside the report print the same figures as that file.
 *   3. Every file that figures file names as an input hashes to what it recorded.
 *
 * Why not re-run `npm run spans -- measure` here and compare? Because a run needs the object
 * cache, which is gitignored by design, so on a clean clone every locator refuses
 * `layer_not_readable` and every figure legitimately changes. A test that re-measured would fail
 * for a reason that is not drift, and it would cost half a minute of CI to say so. Check 3 is the
 * cheap equivalent: the figures are what the code produces now exactly while the code and the
 * records they were measured on are the ones in the tree.
 *
 * What check 3 does not catch is a measuring run that loaded a source file which then changed
 * under it. That run is self-consistent, its figures are of a tree that no longer exists, and
 * nothing a later test reads can tell. `runMeasure` is where that is caught: it reads the input
 * digests before the first layer and again after the last, and writes nothing when they differ.
 *
 * This test is deliberately loud. A change to a resolver, to the grammar, to a normaliser or to
 * a result record moves the figures, so it reddens until `npm run spans -- measure` has been run
 * again and the documents say what it printed. That is the cost of a report that can be trusted,
 * and the run is 30 to 60 seconds.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { changedInputs, inputFiles, marks, printsFigure, readFigures, retag, SPAN_FIGURES } from "../shared/omics/reports/figures";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const figures = readFigures(root);

/** Documents a tagged figure may stand in. Everything in `maintenance/reports` and the ADR this
 * work is step 5 of, because that is where the three stale figures were. */
function documents(): string[] {
  const found: string[] = [];
  const reports = path.join(root, "maintenance/reports");
  if (fs.existsSync(reports))
    for (const name of fs.readdirSync(reports).sort()) if (name.endsWith(".md") || name.endsWith(".html")) found.push(`maintenance/reports/${name}`);
  const adrs = path.join(root, "docs/adr");
  if (fs.existsSync(adrs)) for (const name of fs.readdirSync(adrs).sort()) if (name.endsWith(".html")) found.push(`docs/adr/${name}`);
  return found;
}

/** Figures that have to be tagged somewhere, so the check cannot be made to pass by deleting the
 * tags. These are the headline numbers the report and the ADR lead with, and the ones that went
 * stale before. */
const REQUIRED = ["locators", "resolved", "resolved_pct", "value_exact", "value_exact_pct", "wrong_commits", "reason.no_column_geometry"];

describe("figures committed in a document", () => {
  const tagged = documents().flatMap((file) => marks(fs.readFileSync(path.join(root, file), "utf8")).map((mark) => ({ file, ...mark })));

  it("are tagged with a figure the measurement produces", () => {
    const unknown = tagged.filter((mark) => figures.figures[mark.figure] === undefined);
    expect(unknown.map((mark) => `${mark.file}:${mark.line} tags ${mark.figure}, which ${SPAN_FIGURES} does not hold`)).toEqual([]);
  });

  it("print what the measurement produced", () => {
    const wrong = tagged
      .filter((mark) => figures.figures[mark.figure] !== undefined)
      .filter((mark) => !printsFigure(mark.printed, figures.figures[mark.figure]))
      .map((mark) => `${mark.file}:${mark.line} prints ${JSON.stringify(mark.printed)} for ${mark.figure} and the measurement gives ${figures.figures[mark.figure]}`);
    expect(wrong).toEqual([]);
  });

  it("cover the headline figures", () => {
    const missing = REQUIRED.filter((figure) => !tagged.some((mark) => mark.figure === figure));
    expect(missing).toEqual([]);
  });

  it("are the figures the committed tables print", () => {
    const prefix = path.join(root, "maintenance/reports", `span-resolution-${figures.produced}`);
    const rows = (file: string): string[][] =>
      fs
        .readFileSync(file, "utf8")
        .split("\n")
        .filter((line) => line.trim() !== "")
        .map((line) => line.split("\t"));
    const disagreements: string[] = [];
    const check = (file: string, figure: string, printed: string): void => {
      const value = figures.figures[figure];
      if (value === undefined) disagreements.push(`${file} holds a row for ${figure} and ${SPAN_FIGURES} does not`);
      else if (!printsFigure(printed, value)) disagreements.push(`${file} prints ${printed} for ${figure} and ${SPAN_FIGURES} gives ${value}`);
    };
    for (const [reason, count] of rows(`${prefix}-by-reason.tsv`).slice(1)) {
      if (reason === "TOTAL REFUSED") check("by-reason.tsv", "refused", count);
      else check("by-reason.tsv", `reason.${reason}`, count);
    }
    for (const row of rows(`${prefix}-by-kind.tsv`).slice(1)) check("by-kind.tsv", `kind.${row[0]}.spans`, row[1]);
    for (const row of rows(`${prefix}-by-class.tsv`).slice(1)) {
      if (row[0] === "TOTAL") {
        check("by-class.tsv", "locators", row[1]);
        check("by-class.tsv", "resolved", row[2]);
        continue;
      }
      check("by-class.tsv", `class.${row[0]}.locators`, row[1]);
      check("by-class.tsv", `class.${row[0]}.resolved`, row[2]);
    }
    expect(disagreements).toEqual([]);
  });
});

describe("the tree the figures were measured on", () => {
  it("is the tree now", () => {
    const moved = changedInputs(figures.inputs, inputFiles(root), root).map(
      (file) => `${file.path}: ${file.now}; run ${figures.command} and update the documents`,
    );
    expect(moved).toEqual([]);
  });

  it("is recorded file by file, so a failure can name the file", () => {
    expect(figures.inputs.length).toBeGreaterThan(20);
    expect(figures.inputs.every((input) => /^[0-9a-f]{64}$/.test(input.sha256))).toBe(true);
  });
});

describe("rewriting a tagged figure", () => {
  const document = [
    "| Resolved | 5,399 <!--figure:resolved--> | 10.3% <!--figure:resolved_pct--> |",
    "",
    "The 5,399 in the sentence above is a correction this document keeps on purpose.",
    "A figure nothing measures: 7 <!--figure:not_a_figure-->.",
  ].join("\n");

  it("changes the number in front of the tag and nothing else", () => {
    const { text, changed, unknown } = retag(document, { resolved: 11360, resolved_pct: 21.7 });
    expect(text.split("\n")[0]).toBe("| Resolved | 11,360 <!--figure:resolved--> | 21.7% <!--figure:resolved_pct--> |");
    expect(text.split("\n")[2]).toBe("The 5,399 in the sentence above is a correction this document keeps on purpose.");
    expect(changed.map((mark) => mark.figure)).toEqual(["resolved", "resolved_pct"]);
    expect(unknown.map((mark) => mark.figure)).toEqual(["not_a_figure"]);
  });

  it("leaves a document that already agrees exactly as it is", () => {
    const current = retag(document, { resolved: 5399, resolved_pct: 10.3 });
    expect(current.text).toBe(document);
    expect(current.changed).toEqual([]);
  });
});
