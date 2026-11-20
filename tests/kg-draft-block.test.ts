import { describe, it, expect } from "vitest";
import { draftBlock, draftKinds } from "../scripts/kg/draft-block";
import { readMapping } from "../scripts/kg/export";
import { recordSchema } from "../scripts/omics/schema";
import { relationRules } from "../shared/omics/relations";
import { entityKinds } from "../shared/omics/entity-kinds";

const block = draftBlock(readMapping());

describe("KG manifest draft block", () => {
  it("follows recordSchema field by field, in its order", () => {
    expect(block.record_schema.required).toEqual(Object.keys(recordSchema.shape));
    expect(Object.keys(block.record_schema.properties)).toEqual(Object.keys(recordSchema.shape));
    expect(block.record_schema.additionalProperties).toBe(false);
  });
  it("maps every kind to a class no other kind uses", () => {
    expect(Object.keys(block.kinds)).toEqual([...entityKinds]);
    expect(new Set(Object.values(block.kinds)).size).toBe(entityKinds.length);
  });
  it("copies the relation rules", () => {
    expect(Object.keys(block.link_rules)).toEqual(Object.keys(relationRules));
    for (const [relation, rule] of Object.entries(relationRules)) {
      expect(block.link_rules[relation].from).toEqual([...new Set(rule.from)]);
      expect(block.link_rules[relation].to).toEqual([...new Set(rule.to)]);
    }
  });
  it("leaves out kinds that carry results or link to them", () => {
    expect(draftKinds).not.toContain("evaluation");
    expect(draftKinds).not.toContain("result");
    expect(draftKinds).not.toContain("claim");
    expect(draftKinds).not.toContain("baseline");
    expect(draftKinds).toContain("protocol");
  });
  it("accepts the id pattern records add accepts and nothing looser", () => {
    const pattern = new RegExp((block.record_schema.properties.id as { pattern: string }).pattern);
    for (const id of ["a", "esm-2", "a1-b2"]) expect(pattern.test(id)).toBe(true);
    for (const id of ["foo--bar", "foo-", "-foo", "Foo"]) expect(pattern.test(id)).toBe(false);
  });
});
