import { describe, expect, it } from "vitest";
import { loadRecords } from "../scripts/omics/records";
import { validateSourceIdentity } from "../shared/omics/source-identity";
import type { CatalogueRecord } from "../shared/omics/catalogue-query";

// The release build runs this check (validateSnapshot); running it here catches a batch that
// would block the release before it merges.
describe("source identity in the store", () => {
  it("pairs every source_label with a reviewed source_identity", () => {
    const records = loadRecords() as unknown as CatalogueRecord[];
    const byId = new Map(records.map((r) => [r.id, r]));
    const failures: string[] = [];
    for (const record of records) {
      try { validateSourceIdentity(record, byId); } catch (error) { failures.push((error as Error).message); }
    }
    expect(failures).toEqual([]);
  });
});
