import { test } from "vitest";
import assert from "node:assert/strict";
import { privateFieldNames } from "../../shared/omics/private-fields";
import { createCatalogueQuery } from "../../shared/omics/catalogue-query";
import { createEvidenceIndex } from "../../shared/omics/evidence-table";
import { validateSnapshot } from "../../shared/omics/validation";
import { fixture } from "../fixtures/catalogue";

const boundaries = [
  ["service import", validateSnapshot],
  ["public queries", createCatalogueQuery],
  ["direct evidence export", createEvidenceIndex],
] as const;

for (const key of privateFieldNames) {
  test(`all public boundaries reject nested ${key}, including mixed case`, () => {
    for (const spelling of [key, key.toUpperCase()]) {
      const snapshot = fixture();
      snapshot.records[0].attributes.extra = [{ nested: { [spelling]: "PRIVATE_SENTINEL" } }];
      for (const [name, validate] of boundaries) {
        assert.throws(() => validate(snapshot), (error: unknown) => {
          assert.ok(error instanceof Error, name);
          assert.match(error.message, /Private/, name);
          assert.ok(!error.message.includes("PRIVATE_SENTINEL"), name);
          return true;
        });
      }
    }
  });
}

test("coverage metadata and excluded records cannot bypass public privacy checks", () => {
  for (const location of ["coverage", "excluded"]) {
    const snapshot = fixture();
    if (location === "coverage") snapshot.coverage.extra = [{ owner_uid: "PRIVATE_SENTINEL" }];
    else {
      snapshot.records[0].status = "excluded";
      snapshot.records[0].attributes.private_notes = "PRIVATE_SENTINEL";
    }
    for (const [, validate] of boundaries) assert.throws(() => validate(snapshot), /Private/);
  }
});

test("public scientific metadata remains available through every boundary", () => {
  const snapshot = fixture();
  snapshot.records[0].attributes.tokenizer = { name: "Example", token_count: 1024 };
  for (const [, validate] of boundaries) assert.doesNotThrow(() => validate(snapshot));
  assert.ok(createEvidenceIndex(snapshot).forRecord(snapshot.records[0].id).length);
});
