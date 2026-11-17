/** The shape every normaliser returns and the names they are recorded under.
 *
 * A normaliser is a pure function: bytes in, layer out. It reads no file, asks
 * no network and reads no clock, so the same bytes through the same tool
 * version always produce the same layer sha256. That is the property a later
 * extractor relies on when it cites a span of characters in a specific file.
 *
 * The normaliser id is the stable name the manifest records in derivation.
 * Change what a function produces and the number goes up, because a stored
 * layer that silently changes meaning is worse than a second layer.
 */

/** The normalisers this module carries. ADR 0003 section 2 names the first
 * two; the rest are minted here and numbered the same way. */
export const normalisers = [
  "pdf-text-layer@1",
  "europepmc-fulltext-xml@1",
  "html-text@1",
  "text-utf8@1",
  "archive-member@1",
] as const;
export type Normaliser = (typeof normalisers)[number];

/** One layer, and everything the manifest row for it needs. */
export interface Layer {
  normaliser: Normaliser;
  /** The tool that produced the bytes. The TypeScript normalisers name
   * themselves; the PDF one names pdftotext. */
  tool: string;
  tool_version: string;
  /** The exact command, as it is written into the manifest. It carries no
   * path, no timestamp and nothing else a second run could change. */
  derivation: string;
  input_sha256: string;
  output_sha256: string;
  bytes: Buffer;
  /** Characters in the layer, which is what a span is counted in. */
  characters: number;
  /** True when the layer bytes equal the input bytes, so the object already
   * is its own text layer and no second object is stored. */
  identity: boolean;
}
