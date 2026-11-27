import { describe, expect, it } from "vitest";
import { boardsProblems, parseBoards, type BoardsFile } from "../shared/omics/boards";

const release = "2026-11-27-aaaaaaaaaaaa";
const row = (id: string, positions: [number, number], strength: number) => ({
  model_id: id, record_ids: [id], name: id.toUpperCase(), positions, strength, interval: [strength - 0.05, strength + 0.05] as [number, number],
  studies: { s1: 3, s2: 1 }, opponents: 2, comparisons: 4, basis: "several studies" as const,
});

function file(): BoardsFile {
  return {
    schema_version: 1, release_id: release, released_at: "2026-11-27T11:48:36.000Z", method: "m",
    boards: [{
      use_case: "brca", use_case_id: "use-case-brca", title: "BRCA", release_id: release, released_at: "2026-11-27T11:48:36.000Z",
      method: "m", summary: "Orders 2 models.",
      counts: { studies: 2, groups: 4, models: 3, ranked: 2, one_study: 1, not_a_model: 0, not_connected: 0, too_few: 0 },
      rows: [row("a", [1, 2], 0.7), row("b", [1, 2], 0.6)],
      not_ranked: [{ model_id: "c", name: "C", reason: "one study", study_ids: ["s1"] }],
      studies: { s1: { source_ids: ["src-1"], dois: ["10.1/x"] }, s2: { source_ids: ["src-2"], dois: [] } },
    }],
  };
}

describe("boards file", () => {
  it("accepts a well formed file and an empty board", () => {
    expect(boardsProblems(file(), release)).toEqual([]);
    const withGroups = { ...file(), groups: [{ id: "variant", label: "Variant", use_cases: [["brca", "BRCA"]] as [string, string][] }] };
    expect(boardsProblems(withGroups, release)).toEqual([]);
    const badGroups = { ...file(), groups: [{ id: "variant", label: "Variant", use_cases: ["brca"] }] };
    expect(boardsProblems(badGroups).join("\n")).toMatch(/use_cases must be/);
    const empty = file();
    empty.boards[0] = { ...empty.boards[0], rows: [], summary: "No ranking.",
      counts: { ...empty.boards[0].counts, models: 1, ranked: 0 } };
    expect(boardsProblems(empty)).toEqual([]);
    expect(parseBoards(file(), release).boards[0].rows).toHaveLength(2);
  });

  it("refuses a file for another release", () => {
    expect(() => parseBoards(file(), "2026-11-28-bbbbbbbbbbbb")).toThrow(/release_id/);
  });

  it("refuses rows that claim more precision or evidence than they carry", () => {
    const cases: [string, (f: BoardsFile) => void, RegExp][] = [
      ["one row", (f) => { f.boards[0].rows.pop(); f.boards[0].counts.ranked = 1; f.boards[0].counts.too_few = 1; f.boards[0].not_ranked.push({ model_id: "b", name: "B", reason: "no second model to rank", study_ids: ["s1"] }); }, /no rows or at least two/],
      ["one study", (f) => { f.boards[0].rows[0].studies = { s1: 4 }; }, /at least two studies/],
      ["position outside the board", (f) => { f.boards[0].rows[1].positions = [2, 3]; }, /within the board/],
      ["position excludes its place", (f) => { f.boards[0].rows[1].positions = [1, 1]; }, /row's place/],
      ["interval misses strength", (f) => { f.boards[0].rows[0].interval = [0.1, 0.2]; }, /contain the strength/],
      ["out of order", (f) => { f.boards[0].rows[1].strength = 0.71; f.boards[0].rows[1].interval = [0.7, 0.8]; }, /order of strength/],
      ["comparisons", (f) => { f.boards[0].rows[0].comparisons = 9; }, /sum over studies/],
      ["basis", (f) => { (f.boards[0].rows[0] as { basis: string }).basis = "trust me"; }, /basis/],
      ["record ids", (f) => { f.boards[0].rows[0].record_ids = ["z"]; }, /record_ids/],
      ["untraceable study", (f) => { delete f.boards[0].studies.s2; }, /study s2 has no source list/],
      ["counts", (f) => { f.boards[0].counts.models = 9; }, /counts.models/],
      ["reason", (f) => { (f.boards[0].not_ranked[0] as { reason: string }).reason = "other"; }, /reason other/],
      ["duplicate use case", (f) => { f.boards.push(structuredClone(f.boards[0])); }, /appears twice/],
      ["board release", (f) => { f.boards[0].release_id = "x"; }, /differs from the file's/],
    ];
    for (const [label, change, message] of cases) {
      const f = structuredClone(file());
      change(f);
      expect(boardsProblems(f).join("\n"), label).toMatch(message);
    }
  });
});
