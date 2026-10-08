/** List records that may describe the same thing, for review. Read-only on the
 * store: it writes a worklist and never links or merges records itself.
 * Usage: npm run identity:candidates [-- <output-dir>] */
import fs from "node:fs";
import path from "node:path";
import { loadRecords } from "./records";
import type { RecordEntry } from "./schema";

const kinds = ["model", "method", "configuration", "pipeline", "service", "benchmark", "task", "protocol", "dataset", "source"];
const parentRelations = ["family", "variant_of", "alias_of", "model"];
const normalise = (name: string) => name.toLowerCase().replace(/[^a-z0-9]/g, "");
const parents = (record: RecordEntry) =>
  record.links.filter((link) => parentRelations.includes(link.relation)).map((link) => link.target_id);

type Candidate = {
  group: string; kind: string; name: string; ids: string[];
  finding: string; proposal: string; target: string; evidence: string;
};

export function identityCandidates(records: RecordEntry[]): Candidate[] {
  const groups = new Map<string, RecordEntry[]>();
  for (const record of records) {
    if (!kinds.includes(record.kind)) continue;
    const key = `${record.kind}:${normalise(record.name)}`;
    groups.set(key, [...(groups.get(key) ?? []), record]);
  }
  const out: Candidate[] = [];
  for (const [group, members] of [...groups].sort(([a], [b]) => (a < b ? -1 : 1))) {
    if (members.length < 2) continue;
    const kind = members[0].kind;
    const ids = members.map((m) => m.id).sort();
    const base = { group, kind, name: members[0].name, ids };
    if (kind === "source") {
      const hashes = new Set(members.map((m) => String(m.attributes.artifact_sha256 ?? "")));
      const urls = new Set(members.map((m) => String(m.attributes.url ?? "")));
      if (hashes.size === 1 && !hashes.has("")) {
        const target = [...members].sort((a, b) => (a.id.length - b.id.length) || (a.id < b.id ? -1 : 1))[0].id;
        out.push({ ...base, finding: "same artifact hash", proposal: "alias_of", target,
          evidence: `artifact_sha256 ${[...hashes][0]}` });
      } else out.push({ ...base, finding: urls.size === 1 ? "same URL, different bytes" : "same title, different URL",
        proposal: "review", target: "", evidence: `${hashes.size} hashes, ${urls.size} URLs` });
      continue;
    }
    if (kind === "configuration" || kind === "pipeline") {
      const sets = members.map((m) => new Set(parents(m)));
      const shared = [...sets[0]].filter((id) => sets.every((s) => s.has(id)));
      if (shared.length) continue;
      const known = [...new Set(sets.flatMap((s) => [...s]))];
      const orphans = members.filter((m) => !parents(m).length).map((m) => m.id).sort();
      out.push({ ...base, ids: orphans.length ? orphans : ids,
        finding: orphans.length ? "configuration without a parent model" : "same name, different parent models",
        proposal: known.length === 1 && orphans.length ? "family" : "review", target: known.length === 1 ? known[0] : "",
        evidence: known.length ? `sibling parents: ${known.join(" ")}` : "no sibling has a parent model" });
      continue;
    }
    const idSet = new Set(ids);
    const aliased = members.some((m) => m.links.some((l) => l.relation === "alias_of" && idSet.has(l.target_id)));
    if (!aliased) out.push({ ...base, finding: "same name, no alias link", proposal: "review", target: "",
      evidence: members.map((m) => `${m.id}: version ${String(m.attributes.version ?? "unstated")}`).join("; ") });
  }
  return out;
}

if (process.argv[1]?.endsWith("identity-candidates.ts")) {
  const dir = process.argv[2] ?? "data/omics/pending-review/identity-candidates";
  const rows = identityCandidates(loadRecords());
  const cell = (value: string) => (/[",\n]/.test(value) || /^[=+\-@]/.test(value) ? `"${value.replace(/"/g, '""')}"` : value);
  const header = ["group", "kind", "name", "finding", "proposal", "target", "ids", "evidence", "decision", "reviewer", "notes"];
  const lines = rows.map((r) => [r.group, r.kind, r.name, r.finding, r.proposal, r.target, r.ids.join(" "), r.evidence, "", "", ""].map(cell).join(","));
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, "candidates.csv"), [header.join(","), ...lines].join("\n") + "\n");
  const summary: Record<string, number> = {};
  for (const r of rows) summary[`${r.kind}: ${r.finding} -> ${r.proposal}`] = (summary[`${r.kind}: ${r.finding} -> ${r.proposal}`] ?? 0) + 1;
  fs.writeFileSync(path.join(dir, "summary.json"), JSON.stringify(summary, null, 2) + "\n");
  console.log(`${rows.length} candidate groups written to ${dir}`);
}
