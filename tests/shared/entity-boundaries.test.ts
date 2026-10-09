import { test } from "vitest";
import assert from "node:assert/strict";
import { validateSnapshot } from "../../shared/omics/validation";
import { fixture } from "../fixtures/catalogue";

function typedFixture() {
  const snapshot = fixture();
  snapshot.schema_version = "1.1";
  snapshot.records.find((r: any) => r.id === "model-one").kind =
    "configuration";
  snapshot.records.find((r: any) => r.id === "benchmark-one").kind = "protocol";
  snapshot.records.find((r: any) => r.id === "dataset-one").kind =
    "dataset_subset";
  return snapshot;
}

test("service rejects schema 1.1 entity kinds labelled as schema 1.0", () => {
  const snapshot = typedFixture();
  snapshot.schema_version = "1.0";
  assert.throws(() => validateSnapshot(snapshot), /require schema version 1.1/);
});

test("service accepts schema 1.1 entities with historical, typed and current role names", () => {
  assert.doesNotThrow(() => validateSnapshot(fixture()));
  const snapshot = typedFixture();
  assert.doesNotThrow(() => validateSnapshot(snapshot));
  const evaluation = snapshot.records.find((r: any) => r.kind === "evaluation");
  evaluation.links = [
    { relation: "configuration", target_id: "model-one" },
    { relation: "protocol", target_id: "benchmark-one" },
    { relation: "dataset_subset", target_id: "dataset-one" },
  ];
  assert.doesNotThrow(() => validateSnapshot(snapshot));
  evaluation.links = [
    { relation: "system", target_id: "model-one" },
    { relation: "assessment", target_id: "benchmark-one" },
    { relation: "data", target_id: "dataset-one" },
  ];
  assert.doesNotThrow(() => validateSnapshot(snapshot));
});

for (const role of ["system", "assessment", "data"]) {
  test(`service rejects missing and duplicated ${role} evaluation roles`, () => {
    for (const mode of ["missing", "duplicate"]) {
      const snapshot = typedFixture();
      const evaluation = snapshot.records.find(
        (r: any) => r.kind === "evaluation",
      );
      evaluation.links = [
        { relation: "system", target_id: "model-one" },
        { relation: "assessment", target_id: "benchmark-one" },
        { relation: "data", target_id: "dataset-one" },
      ];
      if (mode === "missing") {
        evaluation.links = evaluation.links.filter(
          (link: any) => link.relation !== role,
        );
      } else {
        evaluation.links.push(
          structuredClone(
            evaluation.links.find((link: any) => link.relation === role),
          ),
        );
      }
      assert.throws(
        () => validateSnapshot(snapshot),
        new RegExp(`Invalid evaluation ${role}`),
      );
    }
  });
}

test("service rejects two different relation names for the same evaluation subject role", () => {
  const snapshot = typedFixture();
  snapshot.records
    .find((r: any) => r.kind === "evaluation")
    .links.push({ relation: "configuration", target_id: "model-one" });
  // An older typed name and the legacy role name both mean "system": two subjects.
  assert.throws(() => validateSnapshot(snapshot), /Invalid evaluation system/);
});

test("service rejects a relationship used from a kind its rules do not allow", () => {
  const snapshot = typedFixture();
  snapshot.records
    .find((r: any) => r.kind === "evaluation")
    .links.push({ relation: "measured_in", target_id: "evaluation-one" });
  assert.throws(
    () => validateSnapshot(snapshot),
    /Relationship measured_in cannot link evaluation/,
  );
});
