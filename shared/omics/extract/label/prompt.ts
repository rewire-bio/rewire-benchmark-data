/** The prompt: a file in the repository, hashed, and a question rendered from the table.
 *
 * ADR 0002 decision 5 puts prompts at `prompts/extract/<stage>.v1.md` and makes them immutable
 * once a release references one, with the receipt carrying the path and the hash. The split
 * here follows from that: the file holds everything that does not change between tables, so
 * its hash means something, and the question holds everything that does. A shortlist baked
 * into the prompt file would change its hash on every table and the receipt's prompt hash
 * would stop identifying anything.
 *
 * The question prints the table's own words and nothing else. No cell value reaches it: the
 * stage is given text and asked which record a table is about, and a value it never sees is a
 * value it cannot get wrong. That is the whole safety property, and it is enforced here by
 * what is rendered rather than by asking the stage not to look. A caption that prints
 * "CASF-2016" prints a figure, and that is a name; `namesOnly` in `table.ts` is what keeps a
 * cell's own digits out of the row labels and headings.
 */
import fs from "node:fs";
import path from "node:path";
import { createHash } from "node:crypto";
import type { Shortlist } from "./shortlist";
import type { LabelTable } from "./table";

/** Where the stage's prompt lives, relative to the repository root. */
export const PROMPT_PATH = "prompts/extract/label.v1.md";
/** What the receipt calls this prompt. The version is in the name because a second version is
 * a second file, never an edit of this one. */
export const PROMPT_ID = "extract/label.v1";

export interface Prompt {
  id: string;
  path: string;
  sha256: string;
  text: string;
}

/** Read the prompt file and hash its bytes. Throws where the file is missing, because a run
 * whose prompt cannot be named is a run whose receipt would be a guess. */
export function loadPrompt(root = "."): Prompt {
  const file = path.join(root, PROMPT_PATH);
  if (!fs.existsSync(file)) throw new Error(`The label stage's prompt is missing: ${PROMPT_PATH}`);
  const bytes = fs.readFileSync(file);
  return { id: PROMPT_ID, path: PROMPT_PATH, sha256: createHash("sha256").update(bytes).digest("hex"), text: bytes.toString("utf8") };
}

const block = (title: string, lines: string[]): string =>
  lines.length === 0 ? `## ${title}\n\n(none printed)` : `## ${title}\n\n${lines.map((line) => `- ${line}`).join("\n")}`;

/**
 * The question for one table.
 *
 * Every printed string is quoted with `JSON.stringify` so that a caption's own line breaks,
 * tabs and quotation marks arrive as themselves and cannot run two fields together. The
 * shortlist is printed in id order, which `shortlistFor` already sorted, so the order carries
 * no hint about which entry the filter preferred.
 */
export function renderQuestion(input: {
  table: LabelTable;
  shortlist: Shortlist;
  /** The source's own title, as the store's source record names it. */
  sourceTitle: string;
}): string {
  const { table, shortlist } = input;
  const held: string[] = [];
  if (table.held_back.column_headers > 0) held.push(`${table.held_back.column_headers} further column headings`);
  if (table.held_back.row_labels > 0) held.push(`${table.held_back.row_labels} further row labels`);
  if (table.held_back.numeric > 0) held.push(`${table.held_back.numeric} headings or labels that print no name`);

  return [
    `# Table ${table.anchor.label === "" ? table.anchor.index : JSON.stringify(table.anchor.label)} of ${JSON.stringify(input.sourceTitle)}`,
    "",
    `Printed label: ${JSON.stringify(table.anchor.label)}`,
    `Caption: ${JSON.stringify(table.anchor_text)}`,
    "",
    block("Column headings, as printed", table.column_headers.map((header) => JSON.stringify(header))),
    "",
    block("Row labels, as printed", table.row_labels.map((label) => JSON.stringify(label))),
    held.length > 0 ? `\nNot shown: ${held.join(", ")}.` : "",
    "",
    block(
      "Shortlist",
      shortlist.entries.map((entry) => `\`${entry.id}\` (${entry.kind}): ${JSON.stringify(entry.name)}`),
    ),
    "",
    "Which one of those records does this table report, or `none`? Quote from the caption above.",
  ]
    .filter((line) => line !== "")
    .join("\n");
}
