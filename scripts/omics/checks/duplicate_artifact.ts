/** C9: source records that pin the same bytes from the same place.
 *
 * A group is one (artifact_sha256, url) pair. Two or more source records in one group pin the
 * same archived bytes and name the same retrieval URL, so they are the same source held twice.
 * That is not always a mistake, because one of them may be superseded on purpose, but every
 * group is a question for a reader: either one record supersedes the other and says so, or the
 * two should be one record.
 *
 * This disagrees with the figure of 171 that the design carried, and the disagreement is in
 * the grouping, not in the store. The prototype grouped by artifact_sha256 alone and kept a
 * group only when every record in it shared one url, which drops a duplicate pair whenever a
 * third record pins the same bytes under a different url. Those pairs are duplicates on any
 * reading, so they are reported here. The difference is 16 groups: 171 by the prototype's
 * rule, 187 by this one. The prototype's rule also carried a line that could not do what it
 * was written to do, which is a further reason not to inherit the number.
 *
 * url is the retrieval URL of the source. artifact_url, where it exists, is the address the
 * archived bytes were fetched from, which is often a service endpoint shared by many sources,
 * so it is reported in the detail and is not part of the key.
 */
import type { Check, CheckInput, Finding, Rec } from "./finding";
import { text } from "./finding";

export const duplicateArtifact: Check = {
  id: "C9",
  title: "duplicate artifact",
  rules: ["same-artifact-and-url"],
  run({ sources }: CheckInput): Finding[] {
    const groups = new Map<string, Rec[]>();
    for (const record of sources) {
      const sha = text(record, "artifact_sha256");
      const url = text(record, "url");
      if (!sha || !url) continue;
      const key = `${sha} ${url}`;
      groups.set(key, [...(groups.get(key) ?? []), record]);
    }
    const findings: Finding[] = [];
    for (const [key, records] of groups) {
      if (records.length < 2) continue;
      const ids = records.map((record) => record.id).sort();
      const statuses = records.map((record) => `${record.id} (${record.status ?? "no status"})`).sort();
      findings.push({
        check: "C9",
        rule: "same-artifact-and-url",
        severity: "report",
        subject: key,
        detail: `${ids.length} source records pin these bytes at this url: ${statuses.join(", ")}`,
      });
    }
    return findings.sort((a, b) => (a.subject < b.subject ? -1 : 1));
  },
  context({ sources }: CheckInput): Record<string, number> {
    const withSha = sources.filter((record) => text(record, "artifact_sha256")).length;
    const bySha = new Map<string, number>();
    for (const record of sources) {
      const sha = text(record, "artifact_sha256");
      if (sha) bySha.set(sha, (bySha.get(sha) ?? 0) + 1);
    }
    return {
      sources: sources.length,
      sources_with_an_artifact_hash: withSha,
      artifact_hashes_held_by_more_than_one_source: [...bySha.values()].filter((n) => n > 1).length,
    };
  },
};
