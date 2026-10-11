/** Checks for results computed by Rewire from a source's own supplementary data
 * (`attributes.derivation`, shape in shared/omics/attributes.ts). The shape is checked with the
 * other attributes; this checks what needs the store and the repository: the script exists and
 * matches its hash, each input is a source record with the pinned artifact hash, the inputs come
 * from the same publication as the quoted aggregation, and the evaluation keeps an origin that
 * names who ran it. Rerunning the script is the reviewer's job (review-evidence). */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import type { RecordEntry } from "./schema";

type Derivation = {
  inputs: { source_id: string; artifact_sha256: string }[];
  aggregation_source_id: string;
  script: string;
  script_sha256: string;
};

/** Origins whose evaluation was run by the source's authors or by another paper's authors. A
 * Rewire execution or a paper's quotation of another paper's result cannot carry a derivation. */
const derivableOrigins = new Set(["author_reported", "independent_paper", "unreported"]);

export function derivationIssues(records: RecordEntry[], root = "."): string[] {
  const byId = new Map(records.map((record) => [record.id, record]));
  const scriptHashes = new Map<string, string | null>();
  const hashOf = (script: string) => {
    if (!scriptHashes.has(script)) {
      const file = path.join(root, script);
      scriptHashes.set(script, fs.existsSync(file) ? crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex") : null);
    }
    return scriptHashes.get(script);
  };
  const issues: string[] = [];
  for (const record of records) {
    const d = record.attributes.derivation as Derivation | undefined;
    if (record.kind !== "result" || !d || typeof d !== "object") continue;
    const fail = (message: string) => issues.push(`result ${record.id}: derivation ${message}`);
    const actual = hashOf(d.script);
    if (actual === null) fail(`script ${d.script} does not exist`);
    else if (actual !== d.script_sha256) fail(`script ${d.script} has sha256 ${actual}, not ${d.script_sha256}`);
    if (record.attributes.numeric_value === null || record.attributes.numeric_value === undefined)
      fail("needs a numeric_value");
    const aggregationSource = byId.get(d.aggregation_source_id);
    if (aggregationSource?.kind !== "source") fail(`aggregation source ${d.aggregation_source_id} is not a source record`);
    for (const id of [d.aggregation_source_id, ...d.inputs.map((input) => input.source_id)])
      if (!record.source_ids.includes(id)) fail(`source ${id} is not in the result's source_ids`);
    const doi = aggregationSource?.attributes.doi;
    for (const input of d.inputs) {
      const source = byId.get(input.source_id);
      if (source?.kind !== "source") {
        fail(`input ${input.source_id} is not a source record`);
        continue;
      }
      if (source.attributes.artifact_sha256 !== input.artifact_sha256)
        fail(`input ${input.source_id} pins sha256 ${input.artifact_sha256}, but the source record has ${source.attributes.artifact_sha256 ?? "none"}`);
      // Only the source's own supplementary data counts: the input and the quoted aggregation
      // must come from the same publication.
      if (!doi || source.attributes.doi !== doi)
        fail(`input ${input.source_id} must be supplementary data of the publication that states the aggregation (same doi)`);
    }
    const evaluation = byId.get(record.links.find((link) => link.relation === "evaluation")?.target_id ?? "");
    if (evaluation && !derivableOrigins.has(String(evaluation.attributes.origin)))
      fail(`cannot be used on an evaluation with origin ${evaluation.attributes.origin}`);
  }
  return issues;
}

export function validateDerivations(records: RecordEntry[], root = "."): void {
  const issues = derivationIssues(records, root);
  if (issues.length)
    throw new Error(`${issues.length} derivation problems:\n${issues.slice(0, 20).join("\n")}${issues.length > 20 ? "\n..." : ""}`);
}
