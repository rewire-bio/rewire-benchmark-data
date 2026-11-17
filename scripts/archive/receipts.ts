/** Fetch receipts: what happened when we went to get a source.
 *
 * data/omics/audits/<date>-archive-fetch.receipts.jsonl, the path ADR 0003
 * gives, append-only, one JSON object per line with sorted keys. A receipt is
 * written for a failure as well, because a source we could not get is a fact
 * the recollection needs.
 *
 * A receipt records a transfer. A source that was skipped because it is
 * already held gets no second receipt, which is how a second run writes
 * nothing new. A run crossing midnight UTC writes two files, so every reader
 * here reads the whole directory.
 */
import fs from "node:fs";
import path from "node:path";
import { canonicalLine, fetchReceiptSchema, type FetchReceipt } from "../../shared/archive/schema";

export const receiptDir = (root = "."): string => path.join(root, "data/omics/audits");
const NAME = /^(\d{4}-\d{2}-\d{2})-archive-fetch\.receipts\.jsonl$/;

export const receiptPath = (date: string, root = "."): string => {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) throw new Error(`Not a date: ${date}`);
  return path.join(receiptDir(root), `${date}-archive-fetch.receipts.jsonl`);
};

/** Append one receipt. The line is written in one call, so an interrupted run
 * leaves whole lines. */
export function appendReceipt(receipt: FetchReceipt, root = "."): void {
  const parsed = fetchReceiptSchema.parse(receipt);
  const file = receiptPath(parsed.fetched_at.slice(0, 10), root);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.appendFileSync(file, `${canonicalLine(parsed as unknown as Record<string, unknown>)}\n`);
}

/** Every archive fetch receipt written so far, oldest file first. */
export function readReceipts(root = "."): FetchReceipt[] {
  const directory = receiptDir(root);
  if (!fs.existsSync(directory)) return [];
  const receipts: FetchReceipt[] = [];
  for (const name of fs.readdirSync(directory).sort()) {
    if (!NAME.test(name)) continue;
    const file = path.join(directory, name);
    for (const [index, line] of fs.readFileSync(file, "utf8").split("\n").entries()) {
      if (!line.trim()) continue;
      const parsed = fetchReceiptSchema.safeParse(JSON.parse(line));
      if (!parsed.success) throw new Error(`${name} line ${index + 1}: ${parsed.error.issues[0].message}`);
      receipts.push(parsed.data);
    }
  }
  return receipts;
}

/** The latest receipt per source, by fetched_at, so a retry does not count
 * twice. Ties go to the later line, which is the later write. */
export function latestBySource(receipts: FetchReceipt[]): Map<string, FetchReceipt> {
  const latest = new Map<string, FetchReceipt>();
  for (const receipt of receipts) {
    const held = latest.get(receipt.source_id);
    if (!held || receipt.fetched_at >= held.fetched_at) latest.set(receipt.source_id, receipt);
  }
  return latest;
}
