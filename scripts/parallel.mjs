/** Run npm scripts at the same time; fail if any fails. Used by `npm run build` to overlap
 * the knowledge-graph inference (Python, one core) with the prepared SQLite file (Node).
 * Usage: node scripts/parallel.mjs <script> [<script> ...] */
import { spawn } from "node:child_process";

const scripts = process.argv.slice(2).filter(Boolean);
const codes = await Promise.all(
  scripts.map(
    (name) =>
      new Promise((resolve) => {
        const child = spawn("npm", ["run", "-s", name], { stdio: "inherit" });
        child.on("exit", (code, signal) => resolve(code ?? (signal ? 1 : 0)));
        child.on("error", () => resolve(1));
      }),
  ),
);
const failed = scripts.filter((_, i) => codes[i] !== 0);
if (failed.length) {
  console.error(`Failed: ${failed.join(", ")}`);
  process.exit(1);
}
