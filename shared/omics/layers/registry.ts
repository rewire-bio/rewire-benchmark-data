/** Building and reading the layer registry.
 *
 * The registry is generated from the object manifest. It is never hand
 * written and it holds no bytes: every row names a layer the archive's
 * stored bytes produce, and the bytes themselves stay in ADR 0004's object
 * store. Regenerating it over an unchanged store writes the same file, byte
 * for byte, which is the property `tests/omics-layer-registry.test.ts`
 * asserts and the reason nothing here reads a clock.
 *
 * The derivation is `shared/archive/layers`, which the archive lane owns.
 * This file calls it and copies nothing out of it.
 *
 * Container members. A zip or a tarball has no text layer; its members do,
 * and a member is not an object in the manifest. The row for a member layer
 * names the container in `object_sha256`, the member's own digest in
 * `derived_from` and its path inside the container in `container_path`.
 * Expanding the container again reproduces the member exactly, so that triple
 * is a complete address without the archive lane having to store the member.
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { canonicalLine } from "../../archive/schema";
import type { ManifestRow } from "../../archive/schema";
import { layerOf, walk, type LayerNode } from "../../archive/layers/index";
import { metricsOf, sanityOf } from "./sanity";
import { layerRecordSchema, type LayerRecord } from "./types";

export const registryPath = (root = "."): string => path.join(root, "data/omics/layers/registry.jsonl");
/** The other half of the generated pair: the held objects that produced no
 * layer, each with the reason the derivation gave. Coverage needs it to say
 * which stated reason applies to a source that is held and unreadable, and
 * it is the list the next normaliser is written against. */
export const unsupportedPath = (root = "."): string => path.join(root, "data/omics/layers/unsupported.jsonl");

/** Pages as pdfinfo reports them, or null when it cannot read the file.
 *
 * pdfinfo ships with the pdftotext the PDF normaliser already depends on, so
 * this adds no dependency. It is given the bytes on disk in a directory of
 * its own, and the directory goes away again. */
export function pdfPageCount(bytes: Buffer): number | null {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "layer-pages-"));
  const file = path.join(directory, "object.pdf");
  try {
    fs.writeFileSync(file, bytes);
    const report = execFileSync("pdfinfo", [file], { encoding: "utf8", timeout: 120_000 });
    const match = /^Pages:\s+(\d+)$/m.exec(report);
    return match ? Number(match[1]) : null;
  } catch {
    return null;
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
}

/** What a build could not do. A reader of the registry needs both halves:
 * the layers that exist and the objects that produced none. */
export interface BuildProblem {
  object_sha256: string;
  container_path: string | null;
  /** The reason from the derivation, or the error that stopped it. */
  reason: string;
}

export interface BuildResult {
  records: LayerRecord[];
  /** Objects, or members, that carry no layer, each with the reason. */
  unsupported: BuildProblem[];
  /** Objects whose bytes could not be read at all. */
  unreadable: BuildProblem[];
}

/** Sort order for the file: the layer hash, then the object it was reached
 * from, then the path inside the container. The same layer bytes can be
 * reached from two objects, so the hash alone is not a key. */
function compare(a: LayerRecord, b: LayerRecord): number {
  if (a.layer_sha256 !== b.layer_sha256) return a.layer_sha256 < b.layer_sha256 ? -1 : 1;
  if (a.object_sha256 !== b.object_sha256) return a.object_sha256 < b.object_sha256 ? -1 : 1;
  const left = a.container_path ?? "";
  const right = b.container_path ?? "";
  return left < right ? -1 : left > right ? 1 : 0;
}

function recordFor(row: ManifestRow, node: LayerNode, containerPath: string | null): LayerRecord | null {
  const layer = node.layer;
  if (!layer) return null;
  const pages = node.classification.class === "pdf" ? pdfPageCount(node.content) : null;
  const metrics = metricsOf(layer.bytes.toString("utf8"), pages);
  const sanity = sanityOf(metrics, layer.normaliser);
  return layerRecordSchema.parse({
    layer_sha256: layer.output_sha256,
    object_sha256: row.sha256,
    derived_from: node.sha256,
    container_path: containerPath,
    normaliser: layer.normaliser,
    tool: layer.tool,
    tool_version: layer.tool_version,
    derivation: layer.derivation,
    encoding: node.classification.encoding,
    media_type: node.classification.media_type,
    identity: layer.identity,
    bytes: layer.bytes.length,
    metrics,
    sanity: sanity.verdict,
    sanity_reasons: sanity.reasons,
    source_ids: [...row.source_ids].sort(),
    visibility: row.visibility,
    store: row.store,
  });
}

/** Every layer under one stored object.
 *
 * `bytes` are that object's expanded bytes. Nothing is fetched and nothing is
 * written, so this is the function a reviewer runs to re-derive a layer from
 * a fresh clone and check a span against it. */
export function layersOfObject(row: ManifestRow, bytes: Buffer): BuildResult {
  const result: BuildResult = { records: [], unsupported: [], unreadable: [] };
  let tree: LayerNode;
  try {
    tree = layerOf(bytes, { mediaType: row.media_type });
  } catch (error) {
    result.unreadable.push({ object_sha256: row.sha256, container_path: null, reason: (error as Error).message });
    return result;
  }
  for (const { node, path: memberPath } of walk(tree)) {
    const record = recordFor(row, node, memberPath);
    if (record) result.records.push(record);
    else if (node.unsupported)
      result.unsupported.push({ object_sha256: row.sha256, container_path: memberPath, reason: node.unsupported });
  }
  return result;
}

/** The registry over a whole manifest.
 *
 * `read` gives an object's expanded bytes, and throwing is how it reports
 * that the bytes are not held. `onObject` is called after each object, for a
 * progress line on a run over a thousand of them. */
export function buildRegistry(
  rows: Iterable<ManifestRow>,
  read: (sha256: string) => Buffer,
  onObject?: (sha256: string, done: number) => void,
): BuildResult {
  const result: BuildResult = { records: [], unsupported: [], unreadable: [] };
  let done = 0;
  for (const row of rows) {
    done += 1;
    let bytes: Buffer;
    try {
      bytes = read(row.sha256);
    } catch (error) {
      result.unreadable.push({ object_sha256: row.sha256, container_path: null, reason: (error as Error).message });
      onObject?.(row.sha256, done);
      continue;
    }
    const one = layersOfObject(row, bytes);
    result.records.push(...one.records);
    result.unsupported.push(...one.unsupported);
    result.unreadable.push(...one.unreadable);
    onObject?.(row.sha256, done);
  }
  result.records.sort(compare);
  return result;
}

/** The file body: one record per line, keys sorted, sorted by layer hash.
 * Everything that writes the registry goes through this, so the file on disk
 * and the file a test compares against are produced the same way. */
export function serialiseRegistry(records: LayerRecord[]): string {
  const body = [...records]
    .sort(compare)
    .map((record) => canonicalLine(record as unknown as Record<string, unknown>))
    .join("\n");
  return body ? `${body}\n` : "";
}

export function writeRegistry(records: LayerRecord[], root = "."): void {
  const file = registryPath(root);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, serialiseRegistry(records));
}

const compareProblem = (a: BuildProblem, b: BuildProblem): number => {
  if (a.object_sha256 !== b.object_sha256) return a.object_sha256 < b.object_sha256 ? -1 : 1;
  const left = a.container_path ?? "";
  const right = b.container_path ?? "";
  if (left !== right) return left < right ? -1 : 1;
  return a.reason < b.reason ? -1 : a.reason > b.reason ? 1 : 0;
};

export function serialiseUnsupported(problems: BuildProblem[]): string {
  const body = [...problems]
    .sort(compareProblem)
    .map((problem) => canonicalLine(problem as unknown as Record<string, unknown>))
    .join("\n");
  return body ? `${body}\n` : "";
}

export function writeUnsupported(problems: BuildProblem[], root = "."): void {
  const file = unsupportedPath(root);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, serialiseUnsupported(problems));
}

export function readUnsupported(root = "."): BuildProblem[] {
  const file = unsupportedPath(root);
  if (!fs.existsSync(file)) return [];
  return fs
    .readFileSync(file, "utf8")
    .split("\n")
    .filter((line) => line.trim())
    .map((line) => JSON.parse(line) as BuildProblem);
}

/** The registry as it stands. A missing file is an empty registry, which is
 * what a clone that has not run the build has. */
export function readRegistry(root = "."): LayerRecord[] {
  const file = registryPath(root);
  if (!fs.existsSync(file)) return [];
  return fs
    .readFileSync(file, "utf8")
    .split("\n")
    .filter((line) => line.trim())
    .map((line, index) => {
      const parsed = layerRecordSchema.safeParse(JSON.parse(line));
      if (!parsed.success) throw new Error(`data/omics/layers/registry.jsonl line ${index + 1}: ${parsed.error.issues[0].message}`);
      return parsed.data;
    });
}
