/** The cache holds source bytes and git must never see them. */
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { expect, it } from "vitest";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const cache = "data/archive/cache";

const tracked = (pathspec: string): string[] =>
  execFileSync("git", ["ls-files", "-z", "--", pathspec], { cwd: root, encoding: "utf8", maxBuffer: 64 * 1024 ** 2 })
    .split("\0")
    .filter(Boolean);

it("tracks no file at all under the object cache, so no file over 1 MiB can be added there", () => {
  const files = tracked(cache);
  const large = files.filter((file) => fs.statSync(path.join(root, file)).size > 1024 * 1024);
  expect({ tracked: files, over_1_mib: large }).toEqual({ tracked: [], over_1_mib: [] });
});

it("ignores the cache path, including a file over 1 MiB written into it", () => {
  const directory = path.join(root, cache, "ab");
  const file = path.join(directory, `${"a".repeat(64)}.gz`);
  const existed = fs.existsSync(file);
  fs.mkdirSync(directory, { recursive: true });
  if (!existed) fs.writeFileSync(file, Buffer.alloc(1024 * 1024 + 1));
  try {
    const status = execFileSync("git", ["status", "--porcelain", "--", cache], { cwd: root, encoding: "utf8" });
    expect(status.trim()).toBe("");
  } finally {
    if (!existed) fs.rmSync(file, { force: true });
  }
});

it("keeps the committed manifest text only, with no tracked object over 1 MiB beside it", () => {
  const large = tracked("data/archive").filter((file) => fs.statSync(path.join(root, file)).size > 1024 * 1024);
  expect(large).toEqual([]);
});
