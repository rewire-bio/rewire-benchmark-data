/** text-utf8@1: plain text, markdown and source code.
 *
 * The encoding is normalised to UTF-8 and nothing else changes. Line endings
 * are left alone, because CRLF is content and rewriting it would move every
 * offset a later span cites. Unicode is not normalised either: ADR 0003
 * section 2 forbids it here, because an ICU version change would then shift
 * every stored offset, and normalisation belongs in the comparison function
 * instead.
 *
 * Bytes that are already UTF-8 with no byte order mark come back identical,
 * so the layer sha256 equals the object's own and nothing new is stored.
 */
import { createHash } from "node:crypto";
import { decode, encodingOf, type Encoding } from "./classify";
import type { Layer } from "./types";

const digest = (bytes: Buffer): string => createHash("sha256").update(bytes).digest("hex");

/** Count characters the way a span does: code points, not UTF-16 units. */
export const characterCount = (text: string): number => [...text].length;

/** Build the layer for a decoded string, with the digests filled in. */
export function layerFromText(
  input: Buffer,
  text: string,
  normaliser: Layer["normaliser"],
  derivation: string,
): Layer {
  const bytes = Buffer.from(text, "utf8");
  const inputSha = digest(input);
  const outputSha = digest(bytes);
  return {
    normaliser,
    tool: normaliser,
    tool_version: normaliser.split("@")[1],
    derivation,
    input_sha256: inputSha,
    output_sha256: outputSha,
    bytes,
    characters: characterCount(text),
    identity: inputSha === outputSha,
  };
}

/** The text layer of plain text, markdown or source code. */
export function textLayer(input: Buffer, encoding?: Encoding): Layer {
  const found = encoding ?? encodingOf(input);
  if (!found) throw new Error("textLayer was given bytes that do not decode as text");
  return layerFromText(input, decode(input, found), "text-utf8@1", `text-utf8@1 decode ${found} to utf-8`);
}
