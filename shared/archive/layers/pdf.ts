/** pdf-text-layer@1: a PDF through the repository's pinned pdftotext path.
 *
 * ADR 0003 section 2 says to promote the normaliser already working here
 * rather than write a second one, so this calls readPinnedPdfText at
 * scripts/omics/extract/pdf.ts. That function verifies the bytes against a
 * digest, pipes them to pdftotext on stdin so the conversion is bound to the
 * bytes it checked, and reads the pdftotext version string back out. It takes
 * a path, so the bytes go to a temporary file that is removed again; the
 * digest it is given is the digest of those same bytes, so the check it makes
 * is the one it was written for.
 *
 * The layer records the tool, its version, the input sha256 and the output
 * sha256. A poppler change moves the output sha256 and therefore stores a new
 * object beside the old one; it never rewrites one.
 */
import { createHash } from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { readPinnedPdfText } from "../../../scripts/omics/extract/pdf";
import { characterCount } from "./text";
import type { Layer } from "./types";

const digest = (bytes: Buffer): string => createHash("sha256").update(bytes).digest("hex");

let probed: boolean | null = null;

/** Whether pdftotext is on the path. A run without it produces no PDF layers
 * and says so, rather than producing empty ones. This is a presence probe,
 * not a second conversion path: it runs pdftotext -v and reads nothing but
 * the exit. The answer is held for the process, because a run over the whole
 * store would otherwise spawn it once per object. */
export function hasPdftotext(): boolean {
  if (probed === null) probed = !spawnSync("pdftotext", ["-v"], { stdio: "ignore", timeout: 30_000 }).error;
  return probed;
}

/** The text layer of a PDF. */
export function pdfLayer(input: Buffer): Layer {
  const sha = digest(input);
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "archive-pdf-"));
  const file = path.join(directory, "object.pdf");
  try {
    fs.writeFileSync(file, input);
    const { text, transformation } = readPinnedPdfText(file, sha);
    const bytes = Buffer.from(text, "utf8");
    const output = digest(bytes);
    if (output !== transformation.output_sha256)
      throw new Error(`pdftotext output for ${sha} does not round trip through UTF-8`);
    return {
      normaliser: "pdf-text-layer@1",
      tool: transformation.tool,
      tool_version: transformation.tool_version,
      derivation: `pdf-text-layer@1 ${transformation.tool} ${transformation.arguments.join(" ")} (${transformation.tool_version})`,
      input_sha256: sha,
      output_sha256: output,
      bytes,
      characters: characterCount(text),
      identity: false,
    };
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
}
