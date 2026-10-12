import { describe, expect, it } from "vitest";
import { ZodError } from "zod";
import { publicRecords } from "../scripts/omics/schema";
import { currentRecords } from "../shared/omics/current";
import { validateSnapshot } from "../shared/omics/validation";
import { records } from "./helpers/records";

// The release validates its snapshot with the service schema, which is stricter than the store
// checks run by records:add (for example, every claim needs a source locator). Pull requests run
// the same check here, so a record the release would refuse fails before merge.
describe("release validation", () => {
  it("accepts every public record in the store", () => {
    const visible = publicRecords(currentRecords(records));
    const snapshot = { schema_version: "1.1", release_id: "2026-01-01-000000000000", released_at: "2026-01-01T00:00:00Z", records: visible, coverage: {} };
    let problems: string[] = [];
    try {
      validateSnapshot(snapshot);
    } catch (error) {
      if (!(error instanceof ZodError)) throw error;
      problems = [...new Set(error.issues.map((i) => `${visible[Number(i.path[1])]?.id ?? i.path.join(".")}: ${i.message}`))];
    }
    expect(problems).toEqual([]);
  });
});
