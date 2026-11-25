import { describe, expect, it } from "vitest";
import { deriveUseCaseInputs } from "../shared/omics/use-cases";
import type { CatalogueRecord } from "../shared/omics/catalogue-query";
import { records, recordsById } from "./helpers/records";

describe("mRNABench Sample designed MRL CPU receipt promotion", () => {
  const receiptId = "runner-receipt-mrnabench-designed-mrl-cpu-37cf4634";
  const recipeSourceId = "runner-recipe-mrnabench-designed-mrl-baselines-37cf4634";
  const evaluationIds = [
    "rewire-local-20260920-evaluation-mrnabench-composition",
    "rewire-local-20260920-evaluation-mrnabench-train-mean",
  ];
  const resultIds = [
    "rewire-local-20260920-result-mrnabench-composition-mse",
    "rewire-local-20260920-result-mrnabench-composition-pearson",
    "rewire-local-20260920-result-mrnabench-composition-spearman",
    "rewire-local-20260920-result-mrnabench-train-mean-mse",
    "rewire-local-20260920-result-mrnabench-train-mean-pearson",
    "rewire-local-20260920-result-mrnabench-train-mean-spearman",
  ];

  it("carries executed recipe and full-protocol CPU receipt on the protocol", () => {
    const protocol = recordsById.get("rewire-protocol-mrnabench-designed-mrl-v1");
    expect(protocol).toBeDefined();
    expect(protocol!.source_ids).toContain(receiptId);
    expect(protocol!.source_ids).toContain(recipeSourceId);
    const recipes = protocol!.attributes.run_recipes as Array<Record<string, unknown>>;
    expect(recipes.map((recipe) => recipe.id)).toEqual([
      "local-20260920-mrnabench-repeat",
      "mrnabench-designed-mrl-baselines",
    ]);
    const executed = recipes[1];
    expect(executed.purpose).toBe("generate_and_evaluate");
    const instructions = executed.instructions as Array<Record<string, unknown>>;
    expect(instructions).toHaveLength(1);
    expect(instructions[0].status).toBe("executed");
    expect(instructions[0].validation_receipt).toMatchObject({
      source_id: receiptId,
      scope: "full_protocol",
    });
  });

  it("promotes both baseline evaluations and all six child results to reproduced", () => {
    for (const id of evaluationIds) {
      const evaluation = recordsById.get(id);
      expect(evaluation, id).toBeDefined();
      expect(evaluation!.status).toBe("reproduced");
      expect(evaluation!.source_ids).toContain(receiptId);
      expect(evaluation!.source_ids).toContain(recipeSourceId);
      expect(evaluation!.attributes.reproduction).toMatchObject({
        recipe_owner_id: "rewire-protocol-mrnabench-designed-mrl-v1",
        recipe_id: "mrnabench-designed-mrl-baselines",
        applicability: "generate_and_evaluate",
      });
    }
    for (const id of resultIds) {
      const result = recordsById.get(id);
      expect(result, id).toBeDefined();
      expect(result!.status).toBe("reproduced");
      expect(result!.source_ids).not.toContain(receiptId);
    }
  });

  it("keeps use-case-mapping-utr-translation-baselines-designed-v1 active and direct", () => {
    const derived = deriveUseCaseInputs({
      records: records as unknown as CatalogueRecord[],
    });
    const mapping = derived.mappings.find(
      (item) => item.id === "use-case-mapping-utr-translation-baselines-designed-v1",
    );
    expect(mapping).toBeDefined();
    expect(mapping!.lifecycle).toBe("active");
    expect(mapping!.relevance).toBe("direct");
    expect([...mapping!.evaluation_ids].sort()).toEqual([...evaluationIds].sort());
  });
});
