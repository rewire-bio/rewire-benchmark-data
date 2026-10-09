import { defineConfig } from "vitest/config";
// Workers default to the available cores; most test files load the full record store, so
// parallel files matter more than anything inside a test.
export default defineConfig({test:{environment:"node", exclude:["node_modules/**","workbench/**"]}});
