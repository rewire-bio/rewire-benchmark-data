/** The layer registry contract: what a claim addresses when it cites a span.
 *
 * ADR 0002 decision 1 asks for one stable identity per text layer, carrying
 * the layer hash, the object it derives from, the sources that cite that
 * object, the normaliser and its version, the character length and the
 * encoding. This file is that record and nothing else. The derivation lives
 * in `shared/archive/layers`, the bytes live in ADR 0004's object store, and
 * the registry holds neither: it is a projection, generated from the
 * manifest, and a second copy of a layer would be a second place to be wrong.
 *
 * Two rules a reader needs.
 *
 * 1. Counts, not ratios. Every metric on a record is an integer count, so a
 *    regenerated file is byte-identical whatever a float formatter does.
 *    Ratios are computed on read, in `./sanity`.
 * 2. No clock. Nothing here records when the registry was built. The date a
 *    layer's bytes entered the archive is already on the manifest row, and a
 *    build timestamp is the one field that would make regeneration differ.
 */
import { z } from "zod";

const hex64 = z.string().regex(/^[a-f0-9]{64}$/);
const count = z.number().int().min(0);

/** The sanity verdict ADR 0002 decision 1 names. `fail` is the verdict no
 * record, claim or candidate may cite. */
export const sanityVerdicts = ["pass", "suspect", "fail"] as const;
export type SanityVerdict = (typeof sanityVerdicts)[number];

/** What the sanity gate counted. Every field is a count over the layer text,
 * in code points, so a reader can recompute any threshold without the bytes.
 */
export const layerMetricsSchema = z
  .object({
    /** Code points, which is what `oa:TextPositionSelector` counts. */
    characters: count,
    /** Code points that are not whitespace. A layer of page breaks and
     * spaces has characters and no content. */
    non_space: count,
    /** U+FFFD, the decoder's record of bytes it could not read. */
    replacement: count,
    /** Code points that are not a C0 control other than tab, newline,
     * carriage return and form feed, and not a C1 control. Form feed counts
     * as printable because it is the page separator pdftotext writes. */
    printable: count,
    /** Decimal digits. */
    digits: count,
    /** Letters. */
    letters: count,
    /** Code points that are neither letter, digit nor whitespace. */
    punctuation: count,
    /** The longest unbroken run of those. A font that maps digits to
     * punctuation leaves long runs where numbers were. */
    longest_punctuation_run: count,
    /** Form feeds, which is the page count a PDF text layer carries. */
    page_breaks: count,
    /** Pages as pdfinfo reports them, for a PDF layer. Null elsewhere, and
     * null when pdfinfo could not read the file. */
    pdf_pages: count.nullable(),
  })
  .strict();
export type LayerMetrics = z.infer<typeof layerMetricsSchema>;

/** One text layer, addressable by `layer_sha256`. */
export const layerRecordSchema = z
  .object({
    /** The layer's identity, and the key its bytes sit under in the object
     * store. This is the hash a span cites. */
    layer_sha256: hex64,
    /** The manifest object this layer was reached from. For a layer derived
     * straight from stored bytes this equals `derived_from`; for a layer
     * inside a container it is the container. */
    object_sha256: hex64,
    /** The bytes the normaliser read. A container member is not in the
     * manifest, so this names the member's own digest. */
    derived_from: hex64,
    /** The member's path inside the container, or null when the layer comes
     * from the stored object itself. A member is reproduced by expanding the
     * container again, so the path plus the container digest is the whole
     * address. */
    container_path: z.string().nullable(),
    /** The normaliser and its version, as `shared/archive/layers` names it. */
    normaliser: z.string().min(1),
    tool: z.string().min(1),
    tool_version: z.string().min(1),
    /** The exact command, as the manifest records it for a derived object. */
    derivation: z.string().min(1),
    /** The encoding the normaliser decoded from, or null for a PDF, where
     * the tool decides. */
    encoding: z.string().nullable(),
    /** The media type of the bytes the layer was derived from. */
    media_type: z.string().min(1),
    /** True when the layer bytes equal their input, so the object already is
     * its own text layer and the store holds one object, not two. */
    identity: z.boolean(),
    bytes: count,
    metrics: layerMetricsSchema,
    sanity: z.enum(sanityVerdicts),
    /** One line per property the gate did not find. Empty at `pass`. */
    sanity_reasons: z.array(z.string().min(1)),
    /** The source records that cite the object, from the manifest row. */
    source_ids: z.array(z.string().min(1)),
    /** Whether the object's bytes are published, so a reader outside this
     * machine can fetch them. Copied from the manifest row. */
    visibility: z.string().min(1),
    store: z.string().min(1),
  })
  .strict();
export type LayerRecord = z.infer<typeof layerRecordSchema>;

/** Why a source does or does not carry an extraction substrate. Exactly one
 * bucket per source, and ADR 0002 decision 7 requires the buckets to sum to
 * the source count. */
export const coverageBuckets = [
  /** A layer at `pass`: the substrate the extractor works over. */
  "layer_pass",
  /** A layer at `suspect`: usable, with a recorded caveat. */
  "layer_suspect",
  /** Every layer under the held object is at `fail`. */
  "layer_fail",
  /** The bytes are held and no normaliser reads them: an office package, a
   * raster image, a binary. */
  "no_normaliser",
  /** The bytes are held and are demonstrably not the artifact: the fetch
   * receipt says so. */
  "not_the_artifact",
  /** No bytes were captured. */
  "no_capture",
] as const;
export type CoverageBucket = (typeof coverageBuckets)[number];
