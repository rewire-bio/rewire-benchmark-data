import { describe, expect, it } from "vitest";
import { pullRequestLines } from "../scripts/release/changelog.mjs";

describe("release changelog", () => {
  it("lists merged and squashed pull requests by title, oldest first, and skips direct pushes", () => {
    const log = [
      "Merge pull request #145 from rewire-bio/claude/next\x1fAdd the next batch\n\nLonger description\n",
      "Cut release 2026-10-14-a2714d701935\x1f\n",
      "Fix a locator (#144)\x1f\n",
      "Merge pull request #143 from rewire-bio/fix\x1f\n",
    ].join("\x1e\n") + "\x1e\n";
    expect(pullRequestLines(log)).toEqual([
      "Merge pull request #143 from rewire-bio/fix (#143)",
      "Fix a locator (#144)",
      "Add the next batch (#145)",
    ]);
    expect(pullRequestLines("")).toEqual([]);
  });
});
