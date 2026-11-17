/** Putting a layer tree into the object store.
 *
 * This is the only file here that writes anything, and the only one that
 * reaches into scripts/archive. Everything else is pure, so a reviewer can
 * re-derive a layer with no store, no cache and no network.
 *
 * A derived row inherits the parent's origin, licence columns and source ids,
 * because a layer answers for the same sources as the bytes it came from, and
 * a tier governs publication of the work, not of one rendering of it. The
 * licence work may move both rows later with updateRow.
 *
 * The identity rule from ./index applies here: a layer whose sha256 equals
 * its input's is not written, because the object already is its own text
 * layer and the manifest holds one row per sha256.
 */
import { manifestRowSchema, utcNow, type ManifestRow } from "../schema";
import { putObject } from "../../../scripts/archive/objects";
import { upsertRow } from "../../../scripts/archive/manifest";
import { layerOf, walk, type LayerNode, type LayerOptions } from "./index";

export type { LayerNode };

export interface StoredLayer {
  sha256: string;
  layer: ManifestRow["layer"];
  derived_from: string;
  derivation: string;
  bytes: number;
  characters: number | null;
  /** The cache did not hold these bytes before. */
  written: boolean;
  /** The manifest did not hold this row before. */
  added: boolean;
}

export interface StoreResult {
  root: LayerNode;
  stored: StoredLayer[];
  /** Layers that equal their input, so the object is its own text layer. */
  identities: string[];
  /** Objects with no layer, each with the reason. */
  unsupported: { sha256: string; path: string | null; reason: string }[];
  problems: string[];
}

function derivedRow(parent: ManifestRow, fields: Partial<ManifestRow>): ManifestRow {
  return manifestRowSchema.parse({
    ...parent,
    first_seen_at: utcNow(),
    previous_path: null,
    ...fields,
  });
}

/**
 * Derive every layer under one stored object and write them beside it.
 *
 * parent is the manifest row of the exact-bytes object, bytes are that
 * object's expanded bytes, and root is the tree the cache and manifest sit
 * under. Nothing here fetches, and the parent row is never rewritten.
 */
export async function storeLayers(
  parent: ManifestRow,
  bytes: Buffer,
  root = ".",
  options: LayerOptions = {},
): Promise<StoreResult> {
  const tree = layerOf(bytes, { mediaType: parent.media_type, ...options });
  const result: StoreResult = { root: tree, stored: [], identities: [], unsupported: [], problems: [] };

  for (const { node, parent: container, path } of walk(tree)) {
    result.problems.push(...node.problems.map((problem) => `${node.sha256}: ${problem}`));
    if (node.unsupported) result.unsupported.push({ sha256: node.sha256, path, reason: node.unsupported });

    if (container && path !== null) {
      const put = putObject(node.content, root);
      const row = derivedRow(parent, {
        sha256: node.sha256,
        bytes: node.bytes,
        media_type: node.classification.media_type,
        layer: "archive-member",
        derived_from: container,
        derivation: `archive-member@1 ${path}`,
      });
      const upsert = await upsertRow(row, root);
      result.stored.push({
        sha256: node.sha256,
        layer: "archive-member",
        derived_from: container,
        derivation: row.derivation as string,
        bytes: node.bytes,
        characters: null,
        written: put.written,
        added: upsert.added,
      });
    }

    const layer = node.layer;
    if (!layer) continue;
    if (layer.identity) {
      result.identities.push(node.sha256);
      continue;
    }
    const put = putObject(layer.bytes, root);
    const row = derivedRow(parent, {
      sha256: layer.output_sha256,
      bytes: layer.bytes.length,
      media_type: "text/plain",
      layer: "text-layer",
      derived_from: node.sha256,
      derivation: layer.derivation,
    });
    const upsert = await upsertRow(row, root);
    result.stored.push({
      sha256: layer.output_sha256,
      layer: "text-layer",
      derived_from: node.sha256,
      derivation: layer.derivation,
      bytes: layer.bytes.length,
      characters: layer.characters,
      written: put.written,
      added: upsert.added,
    });
  }
  return result;
}
