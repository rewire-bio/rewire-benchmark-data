import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
describe("recipes quoted from each project's own instructions", () => {
  const overlays: {
    id: string;
    source_ids?: string[];
    run_recipes?: {
      id: string;
      instructions: {
        code: string;
        status: string;
        source_ids: string[];
        source_locator: string;
      }[];
    }[];
  }[] = JSON.parse(
    readFileSync("data/omics/reviewed/run-recipes/overlays.json", "utf8"),
  );
  const sources = new Map(
    readFileSync("data/omics/reviewed/run-recipes/records.jsonl", "utf8")
      .split("\n")
      .filter(Boolean)
      .map((line) => JSON.parse(line))
      .map((r) => [r.id, r]),
  );
  const generated = overlays.filter((overlay) =>
    overlay.run_recipes?.some(
      (recipe) =>
        recipe.id.endsWith("-official") || recipe.id.endsWith("-rewirebench"),
    ),
  );
  const quoted = generated.map((overlay) => ({
    ...overlay,
    run_recipes: overlay.run_recipes!.filter(
      (recipe) =>
        recipe.id.endsWith("-official") || recipe.id.endsWith("-rewirebench"),
    ),
  }));

  it("covers the benchmarks whose projects publish commands", () => {
    expect(quoted.length).toBeGreaterThanOrEqual(14);
  });

  it("offers the runner's own recipe where rewirebench implements the scoring", () => {
    const runner = quoted.filter((overlay) =>
      overlay.run_recipes!.some((recipe) => recipe.id.endsWith("-rewirebench")),
    );
    expect(runner.map((overlay) => overlay.id).sort()).toEqual([
      "discovery-benchmark-genomic-benchmarks",
      "discovery-benchmark-tdc-molecular-tasks",
    ]);
    for (const overlay of runner) expect(overlay.run_recipes).toHaveLength(2);
  });

  it("pins every quoted instruction to a line range in a hashed file", () => {
    for (const overlay of quoted)
      for (const recipe of overlay.run_recipes!)
        for (const instruction of recipe.instructions) {
          expect(instruction.status).toBe("source_reviewed_not_executed");
          // Either the project's own README or the runner's own docs, always
          // a named file at a pinned commit and an exact line range.
          expect(instruction.source_locator).toMatch(
            /^(README\.md|docs\/[\w.-]+\.md) at [0-9a-f]{8}, .+, lines \d+-\d+$/,
          );
          for (const id of instruction.source_ids) {
            const source = sources.get(id);
            expect(source, `${overlay.id} cites ${id}`).toBeDefined();
            expect(String(source.attributes.artifact_sha256)).toMatch(
              /^[a-f0-9]{64}$/,
            );
          }
          // A quote is code, not the prose around it.
          expect(instruction.code).not.toMatch(/^\s*(```|~~~)/m);
          expect(instruction.code.trim().length).toBeGreaterThan(0);
        }
  });

  it("says plainly that nothing here was executed", () => {
    for (const overlay of quoted)
      for (const recipe of overlay.run_recipes!)
        expect(
          (recipe as unknown as { limitations: string[] }).limitations.join(
            " ",
          ),
        ).toMatch(/not executed by (rewire|this repository)/);
  });
});
