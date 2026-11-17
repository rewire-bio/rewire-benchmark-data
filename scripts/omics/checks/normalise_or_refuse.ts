/** C13: a stored record that normalizeAttributes would rewrite.
 *
 * normalizeAttributes in shared/omics/attributes.ts is what every reader applies to a record
 * before using it. A record the store holds in a shape that function would change is a record
 * whose bytes and whose read form differ, and nothing at write time stops that: `npm run
 * records -- add` does not normalise and does not refuse.
 *
 * That gap is measured. docs/reviews/2026-11-16-attribute-normalisation.md records 2,574
 * records that reached the store through thirteen independent reviews carrying a review object
 * with both reviewed_at and a date duplicating it, which normalizeAttributes drops. Nobody saw
 * it until a CI test shard failed, because the only thing checking the canonical form runs in
 * CI and the reviewers were each checking their own batch against its sources.
 *
 * The migration has since run, so the expected count today is zero and zero is the baseline.
 * A zero here is the point: the ratchet turns this check into the refusal the review asked
 * for, one PR behind rather than one CI run behind, without touching records -- add.
 *
 * The whole store is loaded, not just the results, because normalizeAttributes resolves a
 * result's parent evaluation through the links of every record.
 */
import { normalizeAttributes } from "../../../shared/omics/attributes";
import type { Check, CheckInput, Finding, Rec } from "./finding";

type Normalisable = { id: string; kind: string; links: { relation: string; target_id: string }[]; attributes: Record<string, unknown> };

/** Keys whose value the normalisation would add, drop or change. */
function changedKeys(before: Record<string, unknown>, after: Record<string, unknown>): string[] {
  const keys = [...new Set([...Object.keys(before), ...Object.keys(after)])].sort();
  return keys.filter((key) => JSON.stringify(before[key]) !== JSON.stringify(after[key]));
}

export const normaliseOrRefuse: Check = {
  id: "C13",
  title: "normalise or refuse",
  rules: ["would-be-rewritten"],
  run({ records }: CheckInput): Finding[] {
    // Every stored record carries links; the schema requires it. The cast is only to meet the
    // input type of normalizeAttributes, which is stricter than the shape the checks read.
    const input = records as Normalisable[];
    const after = normalizeAttributes(input);
    const findings: Finding[] = [];
    for (const [index, record] of input.entries()) {
      if (after[index] === record) continue;
      const keys = changedKeys(record.attributes ?? {}, after[index].attributes ?? {});
      findings.push({
        check: "C13",
        rule: "would-be-rewritten",
        severity: "report",
        subject: record.id,
        detail: `normalizeAttributes would rewrite ${keys.length ? keys.join(", ") : "the attribute order"}`,
      });
    }
    return findings;
  },
  context({ records }: CheckInput): Record<string, number> {
    const kinds = new Set(records.map((record: Rec) => record.kind));
    return { records: records.length, kinds: kinds.size };
  },
};
