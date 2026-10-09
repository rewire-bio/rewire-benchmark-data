import { defineConfig } from "vitest/config";

// Integration files that rebuild a full release or the prepared SQLite file. Pull requests
// run without them (npm run test:fast); main and releases run everything (npm test).
const fullOnly = [
  "tests/prepared-catalogue.test.ts",
  "tests/omics-data.test.ts",
  "tests/omics-evidence-table.test.ts",
  "tests/omics-facet-scoping.test.ts",
  "tests/omics-extract.test.ts",
  "tests/omics-evidence-completion.test.ts",
  "tests/omics-beacon.test.ts",
  "tests/omics-alphagenome.test.ts",
];

// Workers default to the available cores; most test files load the full record store, so
// parallel files matter more than anything inside a test.
export default defineConfig({
  test: {
    environment: "node",
    exclude: ["node_modules/**", "workbench/**", ...(process.env.TEST_SCOPE === "fast" ? fullOnly : [])],
  },
});
