/** The text layer: classification, the four normalisers, container
 * expansion, and the property the whole thing exists for, which is that the
 * same bytes through the same tool version produce the same layer sha256.
 *
 * Fixtures are artifacts already committed under data/omics, expanded in
 * memory. Nothing here writes inside the tree: every store test runs against
 * a temporary root, so data/archive stays untouched.
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import zlib from "node:zlib";
import { createHash } from "node:crypto";
import { afterEach, expect, it } from "vitest";
import { classify } from "./classify";
import { expandContainer } from "./container";
import { hasPdftotext } from "./pdf";
import { layerOf, walk } from "./index";
import { textLayer } from "./text";
import { storeLayers } from "./store";
import { manifestRowSchema, type ManifestRow } from "../schema";
import { readManifest } from "../../../scripts/archive/manifest";
import { hasObject } from "../../../scripts/archive/objects";

const digest = (bytes: Buffer) => createHash("sha256").update(bytes).digest("hex");
const pdftotext = hasPdftotext();

const roots: string[] = [];
afterEach(() => roots.splice(0).forEach((root) => fs.rmSync(root, { recursive: true, force: true })));
const temporaryRoot = () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "archive-layers-"));
  roots.push(root);
  return root;
};

/** A committed artifact, expanded where it is gzipped. The seven
 * restrictively licensed originals are deliberately not used, because issue
 * 276 ruling 3 removes them from the tip tree. */
const fixture = (file: string): Buffer => {
  const bytes = fs.readFileSync(file);
  return file.endsWith(".gz") ? zlib.gunzipSync(bytes) : bytes;
};

const jats = "data/omics/use-case-coverage-cnv-20261011-hwang2026/artifacts/PMC12841491.xml.gz";
const biorxivXml = "data/omics/poisk-20261115/artifacts/biorxiv-v1-source.xml.gz";
const html = "data/omics/poisk-20261115/artifacts/poisk-explorer.html.gz";
const markdown = "data/omics/bacformer-20261115/artifacts/bacformer-readme-61dca95.md";
const markdownWithHtml = "data/omics/bioemu2-20261115/artifacts/repo_README.md.gz";
const pdf = "data/omics/lit-rna-other-20261011-khoo2026/artifacts/2610.02249v1.pdf.gz";
const spreadsheet = "data/omics/use-case-coverage-cnv-20261009/artifacts/nardone2025-table-s1.xlsx.gz";
const zipOfPdf = "data/omics/use-case-coverage-model-execution-20261009/artifacts/samarakoon2025-supplementary-data.zip.gz";

const row = (overrides: Partial<ManifestRow> = {}): ManifestRow =>
  manifestRowSchema.parse({
    sha256: digest(Buffer.from("parent")),
    bytes: 6,
    media_type: "application/octet-stream",
    layer: "exact-bytes",
    origin: "https://example.org/one",
    requested_url: null,
    first_seen_at: "2026-11-17T09:00:00Z",
    store: "local-cache",
    visibility: "restricted",
    archive_tier: "t4-private",
    observed_licence: null,
    exposure: "policy",
    derived_from: null,
    derivation: null,
    previous_path: null,
    source_ids: ["source-one"],
    ...overrides,
  });

it("reads the class from the bytes, not from the suffix or the served type", () => {
  expect(classify(fixture(jats)).class).toBe("xml");
  // The bioRxiv source XML opens at its root element with no prolog, which is
  // what file(1) calls text/plain.
  expect(classify(fixture(biorxivXml)).class).toBe("xml");
  expect(classify(fixture(html)).class).toBe("html");
  expect(classify(fixture(markdown)).class).toBe("text");
  expect(classify(fixture(pdf)).class).toBe("pdf");
  expect(classify(fs.readFileSync(pdf)).class).toBe("container");
  // A README that opens with a centred div is markdown, not a document.
  expect(classify(fixture(markdownWithHtml)).class).toBe("text");
  // A served type does not override the bytes.
  expect(classify(fixture(jats), "text/plain; charset=utf-8").class).toBe("xml");
  expect(classify(fixture(pdf), "text/html").class).toBe("pdf");
});

it("reports a class it cannot determine instead of inventing a layer", () => {
  expect(classify(Buffer.alloc(0)).unsupported).toBe("empty object");
  expect(classify(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a])).unsupported).toBe("raster image, no text layer");
  const ole2 = Buffer.alloc(16);
  Buffer.from([0xd0, 0xcf, 0x11, 0xe0, 0xa1, 0xb1, 0x1a, 0xe1]).copy(ole2);
  expect(classify(ole2).unsupported).toBe("legacy office binary, no normaliser");
});

it("reads an office package as a spreadsheet, which ./office normalises", () => {
  const packaged = classify(fixture(spreadsheet));
  expect(packaged.class).toBe("office");
  expect(packaged.unsupported).toBeNull();
  const node = layerOf(fixture(spreadsheet), { pdftotext: false });
  expect(node.layer?.normaliser).toBe("ooxml-sheet-tsv@1");
  expect(node.unsupported).toBeNull();
});

it("passes text through with the encoding normalised and nothing else changed", () => {
  const bytes = fixture(markdown);
  const layer = textLayer(bytes);
  expect(layer.bytes.equals(bytes)).toBe(true);
  expect(layer.identity).toBe(true);
  expect(layer.output_sha256).toBe(digest(bytes));

  const crlf = Buffer.from("one\r\ntwo\r\n", "utf8");
  expect(textLayer(crlf).bytes.toString("utf8")).toBe("one\r\ntwo\r\n");
  const bom = Buffer.concat([Buffer.from([0xef, 0xbb, 0xbf]), Buffer.from("value", "utf8")]);
  expect(textLayer(bom).bytes.toString("utf8")).toBe("value");
  expect(textLayer(bom).identity).toBe(false);
  // Composed and decomposed forms stay as they were written.
  const decomposed = Buffer.from("café", "utf8");
  expect(textLayer(decomposed).bytes.equals(decomposed)).toBe(true);
});

it("keeps section boundaries and document order in publisher XML", () => {
  const layer = layerOf(fixture(jats), { pdftotext: false }).layer;
  expect(layer).not.toBeNull();
  const text = layer!.bytes.toString("utf8");
  expect(layer!.normaliser).toBe("europepmc-fulltext-xml@1");
  expect(text).toContain("Improving CNV Detection Performance");
  // An inline cross reference stays inside its sentence.
  expect(text).toContain("the gain or loss of a gene [1].");
  // A section title is its own line, with a blank line before the section.
  expect(text).toMatch(/\n\n1\. Introduction\n/);
  // Markup never reaches the layer.
  expect(text).not.toContain("<sec");
  expect(text).not.toContain("&#x");
  expect(text.indexOf("Improving CNV Detection Performance")).toBeLessThan(text.indexOf("1. Introduction"));
  expect(text.indexOf("1. Introduction")).toBeLessThan(text.indexOf("References"));
});

it("removes the boilerplate from HTML and leaves the reading text", () => {
  const layer = layerOf(fixture(html), { pdftotext: false }).layer;
  const text = layer!.bytes.toString("utf8");
  expect(layer!.normaliser).toBe("html-text@1");
  expect(text).toContain("Patent-derived antibody sequence database");
  expect(text).not.toContain("<script");
  expect(text).not.toContain("document.querySelector");
  expect(text).not.toContain("addEventListener");
  // The page's inline stylesheet does not reach the layer either.
  expect(text).not.toContain("--surface:");
});

it.skipIf(!pdftotext)("sends a PDF through the repository's pinned pdftotext path", () => {
  const bytes = fixture(pdf);
  const node = layerOf(bytes, { pdftotext: true });
  expect(node.classification.class).toBe("pdf");
  expect(node.layer!.tool).toBe("pdftotext");
  expect(node.layer!.tool_version).toMatch(/^pdftotext version /);
  expect(node.layer!.input_sha256).toBe(digest(bytes));
  expect(node.layer!.output_sha256).toBe(digest(node.layer!.bytes));
  expect(node.layer!.derivation).toContain("pdftotext -layout -enc UTF-8 - -");
  expect(node.layer!.characters).toBeGreaterThan(1000);
  expect(node.layer!.identity).toBe(false);
});

it("expands a container into a layer per member it can classify", () => {
  const gzipped = fs.readFileSync(pdf);
  const expansion = expandContainer(gzipped);
  expect(expansion.kind).toBe("gzip");
  expect(expansion.members).toHaveLength(1);
  expect(expansion.members[0].sha256).toBe(digest(fixture(pdf)));

  // A zip inside a gzip: the container, the member and the member's layer.
  const tree = layerOf(fs.readFileSync(zipOfPdf), { pdftotext });
  expect(tree.classification.class).toBe("container");
  const nodes = walk(tree);
  expect(nodes.map((entry) => entry.node.classification.class)).toEqual(["container", "container", "pdf"]);
  const member = nodes[2];
  expect(member.path).toBe("Publication-ready_Supplementary materials-20250404.pdf");
  expect(member.parent).toBe(nodes[1].node.sha256);
  if (pdftotext) expect(member.node.layer!.characters).toBeGreaterThan(1000);
});

it("reads a ustar tar and reports what it cannot read", () => {
  const header = Buffer.alloc(512);
  header.write("notes.txt", 0);
  header.write("0000644\0", 100);
  header.write("0000000\0", 108);
  header.write("0000000\0", 116);
  header.write("00000000014\0", 124);
  header.write("00000000000\0", 136);
  header.write("        ", 148);
  header.write("0", 156);
  header.write("ustar\0" + "00", 257);
  const body = Buffer.alloc(512);
  body.write("twelve bytes", 0);
  const tar = Buffer.concat([header, body, Buffer.alloc(1024)]);
  const expansion = expandContainer(tar);
  expect(expansion.kind).toBe("tar");
  expect(expansion.members.map((member) => member.path)).toEqual(["notes.txt"]);
  expect(expansion.members[0].bytes.toString("utf8")).toBe("twelve bytes");
  expect(expansion.problems).toEqual([]);
  expect(expandContainer(Buffer.concat([Buffer.from("PK\x03\x04"), Buffer.alloc(40)])).problems).toEqual([
    "no zip end of central directory record",
  ]);
  expect(() => expandContainer(Buffer.from("not a container"))).toThrow("not gzip, zip or tar");
});

/** What each TypeScript normaliser produced at the version named beside it.
 * These pin the version number to its output: change a boundary table, a
 * skip set or the entity table and this test fails until the normaliser
 * number goes up, which is the rule types.ts states. The PDF layer is not
 * pinned here, because its output belongs to poppler and moves with it. */
const pinned: [string, string, string][] = [
  [jats, "europepmc-fulltext-xml@1", "23875a827daf4d503c48a17237f2025a2f9d66e5e341cea2ce76fc640c98cf12"],
  [html, "html-text@1", "68cf9208646bb73b427371fd508dedad169aa73e941df167b22648280139c786"],
  [markdown, "text-utf8@1", "6e4fdabbd05c93ff63b0eb583ce6a9309eaa13998087cc32ddeaa6928025b235"],
];

it("pins each normaliser version to the layer it produces", () => {
  for (const [file, normaliser, sha256] of pinned) {
    const layer = layerOf(fixture(file), { pdftotext: false }).layer;
    expect(layer!.normaliser).toBe(normaliser);
    expect(layer!.output_sha256).toBe(sha256);
  }
});

it("produces the same layer sha256 for the same bytes through the same tool version", () => {
  const files = [jats, biorxivXml, html, markdown, markdownWithHtml, ...(pdftotext ? [pdf] : [])];
  for (const file of files) {
    const bytes = fixture(file);
    const first = layerOf(bytes, { pdftotext });
    const second = layerOf(Buffer.from(bytes), { pdftotext });
    expect(first.layer).not.toBeNull();
    expect(second.layer!.output_sha256).toBe(first.layer!.output_sha256);
    expect(second.layer!.derivation).toBe(first.layer!.derivation);
    expect(second.layer!.characters).toBe(first.layer!.characters);
  }
  // The same holds through a container, where the member is hashed too.
  const container = fs.readFileSync(zipOfPdf);
  const once = walk(layerOf(container, { pdftotext })).map((entry) => entry.node.sha256);
  const twice = walk(layerOf(Buffer.from(container), { pdftotext })).map((entry) => entry.node.sha256);
  expect(twice).toEqual(once);
});

it("stores a layer as an object of its own with a manifest line naming its parent", async () => {
  const root = temporaryRoot();
  const bytes = fixture(jats);
  const parent = row({ sha256: digest(bytes), bytes: bytes.length, media_type: "application/xml" });
  const result = await storeLayers(parent, bytes, root);
  expect(result.unsupported).toEqual([]);
  expect(result.stored).toHaveLength(1);
  const [stored] = result.stored;
  expect(stored.layer).toBe("text-layer");
  expect(stored.derived_from).toBe(parent.sha256);
  expect(stored.derivation).toBe("europepmc-fulltext-xml@1 text content in document order");
  expect(stored.written).toBe(true);
  expect(stored.added).toBe(true);
  expect(hasObject(stored.sha256, root)).toBe(true);

  const manifest = readManifest(root);
  const line = manifest.get(stored.sha256);
  expect(line).toBeDefined();
  expect(line!.layer).toBe("text-layer");
  expect(line!.derived_from).toBe(parent.sha256);
  expect(line!.source_ids).toEqual(["source-one"]);
  expect(line!.archive_tier).toBe("t4-private");
  expect(line!.visibility).toBe("restricted");
  expect(line!.previous_path).toBeNull();

  // A second run writes nothing, because the bytes decide the key.
  const again = await storeLayers(parent, bytes, root);
  expect(again.stored[0].written).toBe(false);
  expect(again.stored[0].added).toBe(false);
  expect(readManifest(root).size).toBe(1);
});

it("writes no second row when the object already is its own text layer", async () => {
  const root = temporaryRoot();
  const bytes = fixture(markdown);
  const parent = row({ sha256: digest(bytes), bytes: bytes.length, media_type: "text/markdown" });
  const result = await storeLayers(parent, bytes, root);
  expect(result.identities).toEqual([parent.sha256]);
  expect(result.stored).toEqual([]);
  expect(readManifest(root).size).toBe(0);
});

it("stores a container member before the layer derived from it", async () => {
  const root = temporaryRoot();
  const bytes = fs.readFileSync(zipOfPdf);
  const parent = row({ sha256: digest(bytes), bytes: bytes.length, media_type: "application/gzip" });
  const result = await storeLayers(parent, bytes, root, { pdftotext });
  const members = result.stored.filter((entry) => entry.layer === "archive-member");
  expect(members).toHaveLength(2);
  expect(members[0].derived_from).toBe(parent.sha256);
  expect(members[1].derivation).toBe("archive-member@1 Publication-ready_Supplementary materials-20250404.pdf");
  expect(members[1].derived_from).toBe(members[0].sha256);
  if (pdftotext) {
    const layers = result.stored.filter((entry) => entry.layer === "text-layer");
    expect(layers).toHaveLength(1);
    expect(layers[0].derived_from).toBe(members[1].sha256);
  }
  for (const entry of result.stored) expect(hasObject(entry.sha256, root)).toBe(true);
});

it("refuses a derived row with no parent and no command", () => {
  const derived = { ...row(), sha256: digest(Buffer.from("layer")), layer: "text-layer" as const };
  expect(() => manifestRowSchema.parse({ ...derived, derived_from: null, derivation: null })).toThrow();
  expect(() =>
    manifestRowSchema.parse({ ...derived, derived_from: digest(Buffer.from("parent")), derivation: "text-utf8@1 decode utf-8 to utf-8" }),
  ).not.toThrow();
});
