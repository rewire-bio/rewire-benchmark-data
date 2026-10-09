import { test } from "vitest";
import assert from "node:assert/strict";
import { validateSnapshot } from "../../shared/omics/validation";
import { fixture } from "../fixtures/catalogue";
test("release validation rejects broken provenance, numeric corruption, and duplicate identities", () => {
  assert.equal(validateSnapshot(fixture()).records.length, 6);
  const broken = fixture();
  broken.records[1].source_ids = ["missing"];
  assert.throws(() => validateSnapshot(broken), /Invalid source/);
  const duplicate = fixture();
  duplicate.records.push(duplicate.records[0]);
  assert.throws(() => validateSnapshot(duplicate), /Duplicate/);
  const numeric = fixture();
  numeric.records[5].attributes.numeric_value = "NaN";
  assert.throws(() => validateSnapshot(numeric));
});
test("hosted services retain a distinct identity and unknown entity types remain invalid", () => {
  const snapshot = fixture();
  const model = snapshot.records.find((record: { kind: string }) => record.kind === "model")!;
  model.attributes.entity_level = "service";
  assert.equal(
    validateSnapshot(snapshot).records.find((record) => record.id === model.id)!
      .attributes.entity_level,
    "service",
  );
  model.attributes.entity_level = "unidentified";
  assert.throws(
    () => validateSnapshot(snapshot),
    /Model needs explicit entity_level/,
  );
});

test("service imports use the same profile structure as static rendering", () => {
  const snapshot = fixture();
  const model = snapshot.records.find((record: { kind: string }) => record.kind === "model")!;
  const profile: any = {
    summary: "Fixture",
    sections: [],
    facts: [],
    strengths: [],
    limitations: [],
    coverage: "limited",
    gaps: ["Fixture"],
    review: {
      method: "automated_source_review",
      date: "2026-09-16",
      note: "Fixture",
    },
  };
  model.attributes.profile = profile;
  assert.doesNotThrow(() => validateSnapshot(snapshot));
  profile.summary_source_ids = ["source-one"];
  assert.throws(() => validateSnapshot(snapshot), /Summary evidence/);
  profile.summary_source_locator = "Fixture summary";
  profile.facts.push({
    label: "Context",
    value: "Fixture",
    status: "independently_verified",
    source_ids: ["source-one"],
    source_locator: "Fixture section",
  });
  assert.throws(() => validateSnapshot(snapshot));
  profile.facts[0].status = "unreported";
  assert.doesNotThrow(() => validateSnapshot(snapshot));
});
