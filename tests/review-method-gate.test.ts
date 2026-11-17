/** Review is automated (docs/record-contract.md, determination 6 of 2026-11-17). Two rules are
 * checked here. A review dated after 2026-11-17 may not carry rendered-source-visual-check,
 * because no value is read off a rendered page any more. And a review's method is controlled by
 * data/vocab/review-method.ttl while its reviewer is controlled by data/vocab/agent.ttl: the two
 * schemes are separate, and swapping them would reject every review in the store. */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { readMapping } from "../scripts/kg/export";
import { loadSchemes, validateVocabularies } from "../scripts/omics/vocab";
import { attributeIssues } from "../shared/omics/attributes";
import { addBatch, recordSha256, writeStore } from "../scripts/omics/records";

const mapping = readMapping();
const schemes = loadSchemes();

const source = (id: string, attributes: Record<string, unknown>) => ({
  id,
  kind: "source" as const,
  name: "A paper",
  description: "",
  status: "source_checked" as const,
  facets: {},
  source_ids: [],
  links: [],
  attributes: { url: "https://example.org/paper", version: "v1", retrieved_at: "2026-11-18T00:00:00Z", ...attributes },
});

const issues = (review: Record<string, unknown>) => attributeIssues(source("test-source", { review }));

describe("the rendered-source-visual-check gate", () => {
  it("refuses a review dated after 2026-11-17 and says what to record instead", () => {
    const problems = issues({ method: ["rendered-source-visual-check"], date: "2026-11-18" });
    expect(problems).toHaveLength(1);
    expect(problems[0]).toContain("rendered-source-visual-check is historical");
    expect(problems[0]).toContain("pdf-text-parse or deterministic-table-parse");
    expect(problems[0]).toContain("independent-cell-check");
  });

  it("refuses it on a review timestamped after the cutoff with no date of its own", () => {
    expect(issues({ method: ["rendered-source-visual-check"], reviewed_at: "2026-11-18T09:00:00Z" })[0])
      .toContain("may not carry it");
  });

  it("refuses it alongside other methods, because the list is what the review asserts", () => {
    expect(issues({ method: ["pdf-text-parse", "rendered-source-visual-check"], date: "2027-01-04" })).toHaveLength(1);
  });

  it("leaves every review dated on or before the cutoff alone", () => {
    expect(issues({ method: ["rendered-source-visual-check"], date: "2026-11-17" })).toEqual([]);
    expect(issues({ method: ["rendered-source-visual-check"], date: "2026-11-16", reviewer: ["claude"] })).toEqual([]);
    expect(issues({ method: ["rendered-source-visual-check"], reviewed_at: "2026-11-17T23:59:00Z" })).toEqual([]);
  });

  it("leaves a current method on a current review alone", () => {
    expect(issues({ method: ["pdf-text-parse", "independent-cell-check"], date: "2026-11-18" })).toEqual([]);
  });

  it("refuses the method at intake", () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "review-method-gate-"));
    try {
      const stored = source("test-source", {});
      writeStore([stored], new Map([[stored.id,
        { id: stored.id, sha256: recordSha256(stored), added_in: "test", added_by: "test", changed_by: [] }]]), root);
      const batch = path.join(root, "batch.jsonl");
      fs.writeFileSync(batch, JSON.stringify(source("test-source-companion", {
        review: { method: ["rendered-source-visual-check"], reviewer: ["claude"], date: "2026-11-18" },
      })) + "\n");
      expect(() => addBatch(batch, "data/omics/test-batch", root)).toThrow("rendered-source-visual-check is historical");
    } finally {
      fs.rmSync(root, { recursive: true, force: true });
    }
  });
});

describe("the schemes a review is validated against", () => {
  const record = (review: Record<string, unknown>) => ({ id: "test-result", facets: {}, attributes: { review } });

  it("takes a review method from review-method.ttl and a reviewer from agent.ttl", () => {
    expect(() => validateVocabularies(mapping, [record({ method: ["pdf-text-parse"], reviewer: ["claude"] })], schemes)).not.toThrow();
  });

  it("rejects an agent key used as a method and a method key used as a reviewer", () => {
    expect(() => validateVocabularies(mapping, [record({ method: ["claude"] })], schemes))
      .toThrow(/"claude" is not a concept in the review-method vocabulary/);
    expect(() => validateVocabularies(mapping, [record({ method: ["pdf-text-parse"], reviewer: ["pdf-text-parse"] })], schemes))
      .toThrow(/"pdf-text-parse" is not a concept in the agent vocabulary/);
  });

  it("keeps rendered-source-visual-check in the scheme, with a note saying it is historical", () => {
    expect(schemes.get("review-method")!.concepts.has("rendered-source-visual-check")).toBe(true);
    const ttl = fs.readFileSync("data/vocab/review-method.ttl", "utf8");
    expect(ttl).toContain('skos:definition "Values compared by eye with the rendered PDF or page."@en');
    expect(ttl).toMatch(/skos:scopeNote "Historical\. The 5,894 reviews/);
  });

  it("records in agent.ttl that every concept in it is a tool", () => {
    expect(fs.readFileSync("data/vocab/agent.ttl", "utf8"))
      .toMatch(/skos:scopeNote "Every concept in this scheme is a tool identity/);
  });
});
