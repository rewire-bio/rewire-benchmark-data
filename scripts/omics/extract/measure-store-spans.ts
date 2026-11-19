/** Stage one of the paired measurement: where in a layer each stored result actually sits.
 *
 * The 52,278 stored results were written by 115 hand-written Python scripts. Each carries a
 * printed value and a locator string. This runs the repository's own span measurement
 * (`measure` in scripts/omics/spans/cli.ts, the code behind `npm run spans -- measure`) over
 * every one of them and dumps the resolved span offsets, which is the only thing that lets an
 * old result and a new candidate be joined by position rather than by value.
 *
 * Joining by value would be worthless: a table of f1 scores prints 0.73 in four places.
 *
 * Usage: npx tsx scripts/omics/extract/measure-store-spans.ts <out.jsonl>
 */
import fs from "node:fs";
import { measure } from "../spans/cli";

const out = process.argv[2];
if (!out) throw new Error("Usage: npx tsx scripts/omics/extract/measure-store-spans.ts <out.jsonl>");

const report = measure({ root: ".", log: (line) => console.error(line) });

const lines: string[] = [];
for (const item of report.work) {
  const span = item.resolved?.span ?? null;
  lines.push(
    JSON.stringify({
      id: item.result.id,
      sources: item.result.source_ids,
      locator: item.result.locator,
      printed_value: item.result.printed_value,
      ok: Boolean(item.resolved),
      kind: item.resolved?.kind ?? null,
      reason: item.refusal?.reason ?? null,
      layer: span?.layer_sha256 ?? null,
      start: span?.start ?? null,
      end: span?.end ?? null,
      exact: span?.exact ?? null,
      value_present: item.value_present,
      value_exact: item.value_exact,
    }),
  );
}
fs.writeFileSync(out, `${lines.join("\n")}\n`);
console.error(
  `${report.locators} locators, ${report.resolved} resolved, ${report.value_exact} spans printing the stored value and nothing else`,
);
