import { describe, expect, it } from "vitest";
import { taskLinkProblems, unlinkedProtocols } from "../scripts/omics/check-task-links";

const protocol = (id: string, relation?: string, exemption?: string) => ({
  id, links: relation ? [{ relation, target_id: "task-t" }] : [], attributes: exemption ? { task_link_exemption: exemption } : {},
});

describe("task-link ratchet", () => {
  it("counts a protocol with no task, benchmark or parent link and no exemption as unlinked", () => {
    const protocols = [protocol("p-task", "evaluates_task"), protocol("p-bench", "part_of"), protocol("p-parent", "parent"),
      protocol("p-data", "uses_data"), protocol("p-exempt", undefined, "A one-off protocol with no shared task."), protocol("p-none")];
    expect(unlinkedProtocols(protocols)).toEqual(["p-data", "p-none"]);
  });

  it("fails on a new unlinked protocol and on a listed one that is now linked", () => {
    expect(taskLinkProblems([protocol("p-old"), protocol("p-new")], ["p-old"])).toEqual([
      expect.stringContaining("p-new has no evaluates_task"),
    ]);
    expect(taskLinkProblems([protocol("p-old", "part_of")], ["p-old"])).toEqual([expect.stringContaining("p-old is in")]);
    expect(taskLinkProblems([protocol("p-old")], ["p-old"])).toEqual([]);
  });
});
