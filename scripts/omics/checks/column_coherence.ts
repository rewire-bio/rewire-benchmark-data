/** C5: results that claim the same printed column of the same table.
 *
 * The grouping, stated because the figure means nothing without it: a group is one
 * (source IDs, table or figure anchor, column name). Two results are in the same group when
 * they cite the same source records, the same printed table or figure, and the same column of
 * it. The comparability key inside a group is (metric, unit, metric_direction). A group whose
 * results hold more than one key is one finding.
 *
 * Why the column and not the table. One printed table usually prints several metrics, one per
 * column, so grouping by table alone reports a disagreement wherever a paper printed AUROC
 * beside runtime, which is not a defect. A column is the narrowest unit of the printed page
 * that should carry one metric in one unit, so a split inside a column is a real question
 * about the extraction. metric_qualifier is deliberately not in the key: a column is read down
 * its rows and the rows are what the qualifier distinguishes.
 *
 * Neither prototype figure was inherited. One grouped by (source, anchor, column selector) and
 * gave 676 of 2,446 columns and 19,374 results; the other grouped by (source, anchor) alone
 * and gave 362 of 530 tables and 32,141 results. The design flagged its own grouping as
 * unreviewed. What this implementation measures is in data/omics/checks-baseline.json, with
 * the group and result counts kept apart.
 *
 * The locator is read with the regexes below rather than with a parsed locator object, because
 * the typed locator does not exist yet. They are a reported approximation and the context
 * counts say how much of the store they addressed: a result whose locator yields no anchor or
 * no column is in no group and is reported by neither rule.
 */
import type { Check, CheckInput, Finding, Rec } from "./finding";
import { text } from "./finding";

/** "Table 2", "Supplementary Table 6", "Extended Data Fig. 3b", "Additional file 2 Table S3". */
const anchorRe =
  /^\s*((?:appendix\s+|supplementary\s+|supplemental\s+|extended\s+data\s+|additional\s+file\s+\d+,?\s+)*(?:table|tables|figure|fig\.?)\s*[a-z]{0,2}\d+(?:\.\d+)*[a-z]?)/i;

/** The column name, in any of the spellings the store uses: column "X", column 'X',
 * column(X), column X. "column group" names the span above the column, so the last match that
 * is not a group is the column itself. */
const columnRe = /\bcolumn(\s+group)?\s*(?:"([^"]*)"|'([^']*)'|\(([^)]*)\)|([^,;]+))/gi;

const anchorOf = (locator: string): string | null => {
  const found = anchorRe.exec(locator);
  return found ? found[1].replace(/\s+/g, " ").trim().toLowerCase() : null;
};

const columnOf = (locator: string): string | null => {
  let column: string | null = null;
  for (const match of locator.matchAll(columnRe)) {
    if (match[1]) continue;
    const value = (match[2] ?? match[3] ?? match[4] ?? match[5] ?? "").trim().replace(/["']/g, "").replace(/\s+/g, " ");
    if (value) column = value.toLowerCase();
  }
  return column;
};

const keyOf = (record: Rec): string =>
  [text(record, "metric") ?? "", text(record, "unit") ?? "", text(record, "metric_direction") ?? ""].join(" / ");

type Group = { id: string; records: Rec[] };

function groups(results: Rec[]): { grouped: Map<string, Group>; noAnchor: number; noColumn: number } {
  const grouped = new Map<string, Group>();
  let noAnchor = 0;
  let noColumn = 0;
  for (const record of results) {
    const locator = text(record, "source_locator");
    if (!locator) {
      noAnchor += 1;
      continue;
    }
    const anchor = anchorOf(locator);
    if (!anchor) {
      noAnchor += 1;
      continue;
    }
    const column = columnOf(locator);
    if (!column) {
      noColumn += 1;
      continue;
    }
    const id = `${[...(record.source_ids ?? [])].sort().join("+")} | ${anchor} | column ${column}`;
    const group = grouped.get(id) ?? { id, records: [] };
    group.records.push(record);
    grouped.set(id, group);
  }
  return { grouped, noAnchor, noColumn };
}

export const columnCoherence: Check = {
  id: "C5",
  title: "column coherence",
  rules: ["column-splits-comparability-key"],
  run({ results }: CheckInput): Finding[] {
    const findings: Finding[] = [];
    for (const group of groups(results).grouped.values()) {
      const keys = new Map<string, number>();
      for (const record of group.records) keys.set(keyOf(record), (keys.get(keyOf(record)) ?? 0) + 1);
      if (keys.size < 2) continue;
      const shown = [...keys].sort((a, b) => b[1] - a[1]).map(([key, n]) => `${key} (${n})`).join("; ");
      findings.push({
        check: "C5",
        rule: "column-splits-comparability-key",
        severity: "report",
        subject: group.id,
        detail: `${group.records.length} results in this column hold ${keys.size} metric / unit / direction keys: ${shown}`,
      });
    }
    return findings;
  },
  context({ results }: CheckInput): Record<string, number> {
    const { grouped, noAnchor, noColumn } = groups(results);
    let inGroups = 0;
    let inSplit = 0;
    let split = 0;
    for (const group of grouped.values()) {
      inGroups += group.records.length;
      const keys = new Set(group.records.map(keyOf));
      if (keys.size > 1) {
        split += 1;
        inSplit += group.records.length;
      }
    }
    return {
      columns: grouped.size,
      columns_with_more_than_one_key: split,
      results_in_columns: inGroups,
      results_in_split_columns: inSplit,
      results_with_no_anchor: noAnchor,
      results_with_no_column: noColumn,
    };
  },
};
