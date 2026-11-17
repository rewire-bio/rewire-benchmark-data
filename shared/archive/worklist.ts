/** The fetch work list, read from the source records.
 *
 * One entry per source record. Sources that share a URL share one transfer and
 * one stored object, so the fetcher groups by URL and writes a receipt per
 * source. Nothing here fetches or writes; it is the list the fetcher, the
 * status command and the measurements all read.
 */
import fs from "node:fs";
import path from "node:path";
import { type SourceClass } from "./schema";

export interface WorkItem {
  source_id: string;
  /** The URL to ask for first. */
  url: string;
  /** Which attribute the URL came from. */
  url_field: "artifact_url" | "url";
  doi: string | null;
  host: string;
  source_class: SourceClass;
  /** The hash the record pins, kept for deduplication only. This work never
   * compares a retrieval against it and never rewrites it. */
  pinned_sha256: string | null;
}

const classes: [RegExp, SourceClass][] = [
  [/(^|\.)ebi\.ac\.uk$/, "europepmc-api"],
  [/(^|\.)(biorxiv|medrxiv)\.org$/, "preprint-server"],
  [/(^|\.)arxiv\.org$/, "arxiv"],
  [/(^|\.)(github\.com|githubusercontent\.com|codeload\.github\.com|gitlab\.com|bitbucket\.org)$/, "code-repository"],
  [/(^|\.)huggingface\.co$/, "model-hub"],
  [/(^|\.)(zenodo\.org|figshare\.com|osf\.io|dataverse\.harvard\.edu)$/, "data-repository"],
  [/(^|\.)ncbi\.nlm\.nih\.gov$/, "pmc"],
  [
    /(^|\.)(springer\.com|springernature\.com|nature\.com|sciencedirect\.com|elsevier\.com|wiley\.com|oup\.com|cell\.com|plos\.org|mdpi\.com|frontiersin\.org|pnas\.org|science\.org|acs\.org|ieee\.org|tandfonline\.com|sagepub\.com|cambridge\.org|royalsocietypublishing\.org)$/,
    "publisher",
  ],
];

/** The host-behaviour class a treatment is keyed on. */
export function sourceClassOf(host: string): SourceClass {
  const lower = host.toLowerCase();
  for (const [pattern, name] of classes) if (pattern.test(lower)) return name;
  return "other-web";
}

const str = (value: unknown): string | null => (typeof value === "string" && value.trim() ? value.trim() : null);

/** Every source record, in file order, with the first fetchable URL it carries. */
export function readWorkList(root = "."): { items: WorkItem[]; withoutUrl: { source_id: string; doi: string | null }[] } {
  const file = path.join(root, "data/entities/sources.jsonl");
  const items: WorkItem[] = [];
  const withoutUrl: { source_id: string; doi: string | null }[] = [];
  for (const line of fs.readFileSync(file, "utf8").split("\n")) {
    if (!line.trim()) continue;
    const record = JSON.parse(line) as { id: string; kind: string; attributes?: Record<string, unknown> };
    if (record.kind !== "source") continue;
    const attributes = record.attributes ?? {};
    const doi = str(attributes.doi);
    let picked: { url: string; field: "artifact_url" | "url" } | null = null;
    for (const field of ["artifact_url", "url"] as const) {
      const value = str(attributes[field]);
      if (value && /^https?:\/\//i.test(value)) {
        picked = { url: value, field };
        break;
      }
    }
    if (!picked) {
      withoutUrl.push({ source_id: record.id, doi });
      continue;
    }
    let host: string;
    try {
      host = new URL(picked.url).host.toLowerCase();
    } catch {
      withoutUrl.push({ source_id: record.id, doi });
      continue;
    }
    items.push({
      source_id: record.id,
      url: picked.url,
      url_field: picked.field,
      doi,
      host,
      source_class: sourceClassOf(host),
      pinned_sha256: str(attributes.artifact_sha256),
    });
  }
  return { items, withoutUrl };
}

/** The work list grouped by URL, so one URL is fetched once. */
export function groupByUrl(items: WorkItem[]): Map<string, WorkItem[]> {
  const groups = new Map<string, WorkItem[]>();
  for (const item of items) {
    const group = groups.get(item.url);
    if (group) group.push(item);
    else groups.set(item.url, [item]);
  }
  return groups;
}

export interface WorkListSummary {
  sources: number;
  with_url: number;
  doi_only: number;
  neither: number;
  distinct_urls: number;
  shared_urls: number;
  with_doi: number;
  by_class: Record<string, number>;
  by_host: Record<string, number>;
}

/** The counts the fetch run is planned from. */
export function summarise(root = "."): WorkListSummary {
  const { items, withoutUrl } = readWorkList(root);
  const byClass: Record<string, number> = {};
  const byHost: Record<string, number> = {};
  for (const item of items) {
    byClass[item.source_class] = (byClass[item.source_class] ?? 0) + 1;
    byHost[item.host] = (byHost[item.host] ?? 0) + 1;
  }
  const groups = groupByUrl(items);
  return {
    sources: items.length + withoutUrl.length,
    with_url: items.length,
    doi_only: withoutUrl.filter((entry) => entry.doi).length,
    neither: withoutUrl.filter((entry) => !entry.doi).length,
    distinct_urls: groups.size,
    shared_urls: [...groups.values()].filter((group) => group.length > 1).length,
    with_doi: items.filter((item) => item.doi).length,
    by_class: Object.fromEntries(Object.entries(byClass).sort((a, b) => b[1] - a[1])),
    by_host: Object.fromEntries(Object.entries(byHost).sort((a, b) => b[1] - a[1])),
  };
}
