/** A ratchet on protocols with no task link (issue #208). The discrepancy rules can only tell
 * whether two studies measured the same task when each protocol is placed in a task, benchmark or
 * suite; without that, a finding's scope is "unknown" (docs/discrepancies.md).
 *
 * data/ontology/task-link-baseline.json lists the protocols that had no such link when the ratchet
 * started. The check fails when a protocol outside the list has no evaluates_task, part_of or
 * parent link and no task_link_exemption attribute saying why, and when the list names a protocol
 * that is now linked or gone, so the list only shrinks.
 *
 * Usage: npm run check:task-links            check
 *        npm run check:task-links -- --write  rewrite the list from the store (only to shrink it) */
import fs from "node:fs";
import path from "node:path";

export const baselineFile = "data/ontology/task-link-baseline.json";
const TASK_RELATIONS = new Set(["evaluates_task", "part_of", "parent"]);

type Protocol = { id: string; links?: { relation: string; target_id: string }[]; attributes?: Record<string, unknown> };

export function unlinkedProtocols(protocols: Protocol[]): string[] {
  return protocols
    .filter((p) => !(p.links ?? []).some((l) => TASK_RELATIONS.has(l.relation)) && !p.attributes?.task_link_exemption)
    .map((p) => p.id)
    .sort();
}

export function taskLinkProblems(protocols: Protocol[], baseline: string[]): string[] {
  const unlinked = new Set(unlinkedProtocols(protocols));
  const listed = new Set(baseline);
  const problems = [...unlinked]
    .filter((id) => !listed.has(id))
    .map((id) => `${id} has no evaluates_task, part_of or parent link; add one, or a task_link_exemption saying why`);
  for (const id of baseline)
    if (!unlinked.has(id)) problems.push(`${id} is in ${baselineFile} but is now linked, exempt or gone; remove it (npm run check:task-links -- --write)`);
  return problems;
}

export function storeProtocols(root = "."): Protocol[] {
  const dir = path.join(root, "data", "entities");
  return fs.readdirSync(dir)
    .filter((name) => name.startsWith("protocols") && name.endsWith(".jsonl"))
    .sort()
    .flatMap((name) => fs.readFileSync(path.join(dir, name), "utf8").split("\n").filter(Boolean).map((line) => JSON.parse(line) as Protocol))
    .filter((record) => (record as { kind?: string }).kind === "protocol");
}

if (process.argv[1]?.endsWith("check-task-links.ts")) {
  const protocols = storeProtocols();
  if (process.argv.includes("--write")) {
    const unlinked = unlinkedProtocols(protocols);
    const previous = fs.existsSync(baselineFile) ? (JSON.parse(fs.readFileSync(baselineFile, "utf8")).protocols as string[]) : null;
    const added = previous ? unlinked.filter((id) => !previous.includes(id)) : [];
    if (added.length) {
      console.error(`Refusing to grow the list; link these instead:\n  ${added.join("\n  ")}`);
      process.exit(1);
    }
    fs.writeFileSync(baselineFile, JSON.stringify({
      note: "Protocols with no task, benchmark or suite link (issue #208). scripts/omics/check-task-links.ts fails on any other unlinked protocol and on an entry that is now linked, so this list only shrinks.",
      protocols: unlinked,
    }, null, 2) + "\n");
    console.log(`Wrote ${unlinked.length} unlinked protocols to ${baselineFile}.`);
  } else {
    const baseline = JSON.parse(fs.readFileSync(baselineFile, "utf8")).protocols as string[];
    const problems = taskLinkProblems(protocols, baseline);
    if (problems.length) {
      console.error(problems.join("\n"));
      process.exit(1);
    }
    console.log(`${protocols.length} protocols checked; ${baseline.length} still have no task link.`);
  }
}
