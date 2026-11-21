import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { records, recordsById } from "./helpers/records";

type Step = { status?: string; validation_receipt?: { source_id?: string; scope?: string } };
type Recipe = { instructions?: Step[] };

// The board badges a result "Reproduced" when it or its evaluation cites the validation receipt
// of an executed, full-protocol run-recipe instruction (scripts/kg/release_graph.py,
// run_receipts; scripts/kg/product_queries.py). The badge does not read `status`.
function runReceipts(all: typeof records) {
  const ids = new Set<string>();
  for (const record of all)
    for (const recipe of (record.attributes.run_recipes as Recipe[] | undefined) ?? [])
      for (const step of recipe.instructions ?? [])
        if (step.status === "executed" && step.validation_receipt?.scope === "full_protocol" && step.validation_receipt.source_id)
          ids.add(step.validation_receipt.source_id);
  return ids;
}

function badged(all: typeof records, byId: Map<string, (typeof records)[number]>) {
  const receipts = runReceipts(all);
  return all.filter((record) => {
    if (record.kind !== "result") return false;
    const evaluation = byId.get(record.links.find((link) => link.relation === "evaluation")?.target_id ?? "");
    return [...record.source_ids, ...(evaluation?.source_ids ?? [])].some((id) => receipts.has(id));
  });
}

describe("the board's Reproduced badge", () => {
  it("is not given to a result whose status is not reproduced", () => {
    const wrong = badged(records, recordsById).filter((result) => result.status !== "reproduced");
    expect(wrong.map((result) => result.id)).toEqual([]);
  });
});

describe("evo2-cloud-operations records", () => {
  const prefix = "rewire-local-20261121-evo2ops";
  const batch = readFileSync("data/omics/rewire-evo2-cloud-operations-20261121/batch.jsonl", "utf8")
    .trim()
    .split("\n")
    .map((line) => JSON.parse(line) as (typeof records)[number]);
  const stored = records.filter((record) => record.id.startsWith(`${prefix}-`));
  const receiptPath = new Map(
    stored
      .filter((record) => record.kind === "source" && record.attributes.source_type === "rewire_run_receipt")
      .map((record) => [record.id, String(record.attributes.artifact_url).split("/").slice(6).join("/")]),
  );
  const results = stored.filter((record) => record.kind === "result");

  it("are in the store as the batch has them", () => {
    expect(stored.length).toBe(92);
    expect(stored.map((record) => JSON.stringify(record)).sort()).toEqual(batch.map((record) => JSON.stringify(record)).sort());
  });

  it("claim no reproduction: the receipts hold no AUROC and one throughput was not repeated", () => {
    expect(stored.filter((record) => record.status !== "source_checked").map((record) => record.id)).toEqual([]);
    expect(stored.filter((record) => record.attributes.run_recipes).map((record) => record.id)).toEqual([]);
    expect(stored.filter((record) => record.attributes.reproduction).map((record) => record.id)).toEqual([]);
    const receipts = runReceipts(records);
    expect([...receiptPath.keys()].filter((id) => receipts.has(id))).toEqual([]);
    expect(badged(records, recordsById).filter((result) => result.id.startsWith(prefix))).toEqual([]);
  });

  it("cite a run receipt only on a result whose value is read from that receipt", () => {
    expect(receiptPath.size).toBe(4);
    let fromReceipt = 0;
    for (const result of results) {
      const evaluation = recordsById.get(result.links[0].target_id)!;
      expect(evaluation.source_ids).toEqual(result.source_ids);
      const cited = result.source_ids.filter((id) => receiptPath.has(id));
      const holdsValue = cited.filter((id) => String(result.attributes.source_locator).startsWith(`${receiptPath.get(id)}, JSON pointer `));
      if (result.attributes.metric === "inference-throughput") {
        expect(holdsValue).toHaveLength(1);
        fromReceipt += 1;
      } else expect(cited).toEqual([]);
    }
    expect(results).toHaveLength(31);
    expect(fromReceipt).toBe(3);
  });

  it("state on the L40S throughput that the study's repeat on another host measured a different value", () => {
    const result = recordsById.get(`${prefix}-result-evo2-7b-runpod-l40s-scoring-throughput`)!;
    const evaluation = recordsById.get(`${prefix}-evaluation-evo2-7b-runpod-l40s-scoring-throughput`)!;
    const protocol = recordsById.get(`${prefix}-protocol-brca1-scoring-throughput`)!;
    expect(result.attributes.printed_value).toBe("0.6117");
    for (const record of [result, evaluation, protocol]) {
      expect(record.source_ids).toContain(`${prefix}-receipt-reproduction-runpod-l40s`);
      expect(record.source_ids).toContain(`${prefix}-source-run-log`);
      const limitations = (record.attributes.limitations as string[]).join(" ");
      expect(limitations).toContain("0.6117");
      expect(limitations).toContain("0.9081");
    }
    const others = results.filter((record) => record.id !== result.id);
    expect(others.filter((record) => record.source_ids.includes(`${prefix}-receipt-reproduction-runpod-l40s`))).toEqual([]);
  });
});
