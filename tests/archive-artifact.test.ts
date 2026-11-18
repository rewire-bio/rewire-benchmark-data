/** Whether stored means we hold the artifact.
 *
 * The four cases that forced this check are described in
 * shared/archive/artifact.ts. Three of them are modelled here, because the
 * pages themselves are hundreds of kilobytes of publisher markup and are not
 * committed; each fixture carries the measurement it is modelled on. The
 * passing side is not modelled: it is read from artifacts committed under
 * data/omics, so a PDF and an XML that pass are real examples.
 *
 * Nothing here writes inside the tree and nothing reaches the network.
 */
import fs from "node:fs";
import zlib from "node:zlib";
import { expect, it } from "vitest";
import { checkArtifact, interstitialPhrases, minimumCharacters, phraseWindows } from "../shared/archive/artifact";
import { hasPdftotext } from "../shared/archive/layers/pdf";
import { layerOf } from "../shared/archive/layers/index";
import { reasons } from "../shared/archive/schema";

const pdftotext = hasPdftotext();
const fixture = (file: string): Buffer => {
  const bytes = fs.readFileSync(file);
  return file.endsWith(".gz") ? zlib.gunzipSync(bytes) : bytes;
};

const committedPdf = "data/omics/lit-rna-other-20261011-khoo2026/artifacts/2610.02249v1.pdf.gz";
const committedXml = "data/omics/use-case-coverage-cnv-20261011-hwang2026/artifacts/PMC12841491.xml.gz";
const committedHtml = "data/omics/poisk-20261115/artifacts/poisk-explorer.html.gz";
const committedSpreadsheet = "data/omics/use-case-coverage-cnv-20261009/artifacts/nardone2025-table-s1.xlsx.gz";

/** The consent banner a large publisher puts on every page it serves, in the
 * dialog element html-text@1 strips with its content. Keeping it in a dialog
 * is the point: the phrases have to be read from the markup, because by the
 * time the text layer exists this is gone. */
const consentDialog = `<dialog open class="cc-banner"><h2>Your privacy, your choice</h2>
<p>We use cookies to give you the best experience. You can manage your cookies at any time.</p>
<button>Accept all cookies</button><a href="/info/cookies">Cookie policy</a></dialog>`;

/** link.springer.com for a chapter behind a cookie wall: 346,436 bytes whose
 * whole text layer was the 76 character title line. */
const cookieWall = Buffer.from(`<!doctype html><html lang="en"><head>
<title>A Phylogenetic Approach to Genomic Language Modeling | Springer Nature Link</title>
<meta name="citation_doi" content="10.1007/978-3-031-90252-9_7">
<script>window.dataLayer=[{page:"chapter",cookies_not_supported:true}];</script>
<style>.cc-banner{position:fixed}</style></head><body>
<header><nav><a href="/">Home</a></nav></header>
${consentDialog}
<main></main><footer><p>Springer Nature</p></footer></body></html>`);

/** alphafoldserver.com/output-terms: 382,715 bytes that rendered to nothing,
 * because the page is a script that draws its own text. No consent wording
 * anywhere in it, which is why a phrase list alone would not catch it. */
const emptyRender = Buffer.from(`<!doctype html><html><head><title>Output terms</title>
<script src="/static/app.bundle.js"></script>
<script>const terms=["a","b","c"];document.addEventListener("DOMContentLoaded",render);</script>
</head><body><div id="root"></div><noscript>This page needs the application.</noscript></body></html>`);

/** www.nature.com/articles/s41587-024-02511-w/tables/1: 172,577 bytes whose
 * layer was 1,422 characters of browser notice and caption with the table
 * itself absent. Above any threshold a genuine page can carry, which is why
 * the detector exists. */
const caption = Array.from(
  { length: 3 },
  (_unused, index) =>
    `<p>Performance of three random seeds of each independent ablation on four variant effect
prediction metrics, panel ${index + 1}. ClinVar reports the area under the receiver operating
characteristic. COSMIC and OMIM report the area under the precision recall curve. gnomAD reports
an odds ratio over all variant types, with the rare variants subset to match the number of common
variants. The ablations themselves are detailed in the Methods section of the article.</p>`,
).join("\n");
const tableLandingPage = Buffer.from(`<!doctype html><html lang="en"><head>
<title>Extended Data Table 1 Ablation study | Nature Biotechnology</title></head><body>
<header><a href="#content">Skip to main content</a></header>
${consentDialog}
<main>${caption}<a href="/articles/s41587-024-02511-w">Back to article page</a></main>
</body></html>`);

/** A page that carries the same banner and is the artifact. Measured over the
 * 274 committed artifacts and the 38 pilot objects, consent wording appears
 * in the markup of two GitHub repository pages at 6,555 and 13,614
 * characters, a committed preprint full text at 50,523 and a Nature article
 * full text at 118,205, all four genuine. */
const article = Array.from(
  { length: 24 },
  (_unused, index) =>
    `<p>Section ${index + 1}. Research and medical genomics require comprehensive, scalable methods
for the discovery of disease targets, evolutionary drivers and genetic markers with clinical
significance, which needs a framework that identifies every type of variant independent of its
size or its location in the genome.</p>`,
).join("\n");
const fullArticle = Buffer.from(`<!doctype html><html lang="en"><head>
<title>Comprehensive genome analysis and variant detection at scale</title></head><body>
${consentDialog}<main><h1>Comprehensive genome analysis</h1>${article}</main></body></html>`);

it("names every reason it can give in the receipt vocabulary", () => {
  // The three reasons this check adds are receipt reasons, so the schema and
  // this module cannot drift apart.
  for (const reason of ["interstitial_body", "text_below_threshold", "publisher_html_only"] as const)
    expect(reasons).toContain(reason);
  expect(new Set(interstitialPhrases.map((phrase) => phrase.name)).size).toBe(interstitialPhrases.length);
});

it("takes a cookie wall for what it is, from the markup the text layer throws away", () => {
  // The whole point: the consent wording is in a dialog, so the layer is the
  // title line and nothing else, exactly as the real page measured.
  const layer = layerOf(cookieWall, { pdftotext: false }).layer;
  expect(layer!.characters).toBeLessThan(200);
  expect(layer!.bytes.toString("utf8")).not.toContain("Accept all cookies");

  const check = checkArtifact({ bytes: cookieWall, mediaType: "text/html", finalUrl: "https://link.springer.com/chapter/10.1007/978-3-031-90252-9_7?error=cookies_not_supported", hasDoi: true });
  expect(check.terminal).toBe(false);
  expect(check.reason).toBe("interstitial_body");
  expect(check.signals).toContain("cookie-consent");
  expect(check.signals).toContain("cookies-required");
});

it("fails a page that renders to nothing, which carries no phrase to match", () => {
  const check = checkArtifact({ bytes: emptyRender, mediaType: "text/html", finalUrl: "https://alphafoldserver.com/output-terms", hasDoi: false });
  expect(check.characters).toBeLessThan(minimumCharacters.html!);
  expect(check.signals).toEqual([]);
  expect(check.reason).toBe("text_below_threshold");
  expect(check.terminal).toBe(false);
});

it("catches an interstitial that clears the threshold, and keeps the article that carries the same banner", () => {
  const stub = checkArtifact({ bytes: tableLandingPage, mediaType: "text/html", finalUrl: "https://www.nature.com/articles/s41587-024-02511-w/tables/1?error=cookies_not_supported", hasDoi: true });
  // Above the threshold and inside the weak window, which is the gap the
  // 1,422 character real page sits in.
  expect(stub.characters!).toBeGreaterThan(minimumCharacters.html!);
  expect(stub.characters!).toBeLessThan(phraseWindows.weak);
  expect(stub.reason).toBe("interstitial_body");

  const held = checkArtifact({ bytes: fullArticle, mediaType: "text/html", finalUrl: "https://example.org/genomics/dragen", hasDoi: false });
  expect(held.characters!).toBeGreaterThan(phraseWindows.weak);
  expect(held.signals).toEqual([]);
  expect(held.terminal).toBe(true);
  expect(held.reason).toBe(null);
});

it("sends a publisher's HTML back to the fallback routes when the source has a DOI", () => {
  const input = { bytes: fullArticle, mediaType: "text/html", finalUrl: "https://www.nature.com/articles/s41587-024-02382-1?error=cookies_not_supported" };
  // The body is the whole article and it is still not the artifact of record:
  // Europe PMC held the JATS XML for this DOI the whole time, as PMC12022141.
  const surrogate = checkArtifact({ ...input, hasDoi: true });
  expect(surrogate.terminal).toBe(false);
  expect(surrogate.reason).toBe("publisher_html_only");

  // Without a DOI there is no fallback to send it to, so the page is what we
  // have and the archive says so.
  expect(checkArtifact({ ...input, hasDoi: false }).terminal).toBe(true);

  // A redirect from the publisher's own landing page counts the same way.
  const redirected = checkArtifact({
    ...input,
    finalUrl: "https://consent.example.org/articles/s41587-024-02382-1",
    requestedUrl: "https://www.nature.com/articles/s41587-024-02382-1",
    hasDoi: true,
  });
  expect(redirected.reason).toBe("publisher_html_only");
});

it("reads a login or consent landing from the path, never from the query string", () => {
  // error=cookies_not_supported is on the final URL of two genuine Springer
  // PDFs and of a Nature article full text, so the query carries no signal.
  const query = checkArtifact({ bytes: fullArticle, mediaType: "text/html", finalUrl: "https://example.org/article?error=cookies_not_supported", hasDoi: false });
  expect(query.terminal).toBe(true);

  const login = checkArtifact({ bytes: fullArticle, mediaType: "text/html", finalUrl: "https://academic.oup.com/login?redirect=/article/28/24/3232", hasDoi: false });
  expect(login.reason).toBe("interstitial_body");
  expect(login.signals).toEqual(["stop-path"]);
});

it("passes a real PDF and a real XML, and measures neither by a threshold it cannot meet", () => {
  const xml = checkArtifact({ bytes: fixture(committedXml), mediaType: "application/xml", finalUrl: "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12841491/fullTextXML", hasDoi: true });
  expect(xml.layerClass).toBe("xml");
  expect(xml.characters!).toBeGreaterThan(minimumCharacters.xml!);
  expect(xml.terminal).toBe(true);

  if (pdftotext) {
    const pdf = checkArtifact({ bytes: fixture(committedPdf), mediaType: "application/pdf", finalUrl: "https://arxiv.org/pdf/2610.02249v1", hasDoi: false, pdftotext: true });
    expect(pdf.layerClass).toBe("pdf");
    expect(pdf.characters!).toBeGreaterThan(minimumCharacters.pdf!);
    expect(pdf.terminal).toBe(true);
  }

  // Without pdftotext there is no layer, so there is nothing to measure. A
  // gap in our tooling is not evidence about the response.
  const unmeasured = checkArtifact({ bytes: fixture(committedPdf), mediaType: "application/pdf", finalUrl: "https://arxiv.org/pdf/2610.02249v1", hasDoi: false, pdftotext: false });
  expect(unmeasured.characters).toBe(null);
  expect(unmeasured.terminal).toBe(true);
});

it("keeps what it cannot measure: a container, an office package and the HTML at the measured floor", () => {
  // The smallest genuine HTML layer in the measured set, at 1,453
  // characters. The threshold sits below it on purpose.
  const floor = checkArtifact({ bytes: fixture(committedHtml), mediaType: "text/html", finalUrl: "https://example.org/poisk-explorer", hasDoi: false });
  expect(floor.characters!).toBeGreaterThanOrEqual(minimumCharacters.html!);
  expect(floor.terminal).toBe(true);

  // An XLSX is a zip of XML parts. Its layer is built once the bytes are
  // stored, not here, and no length threshold was ever measured for one, so
  // the capture check keeps it without measuring it.
  const packaged = checkArtifact({ bytes: fixture(committedSpreadsheet), mediaType: "application/octet-stream", finalUrl: "https://example.org/table-s1.xlsx", hasDoi: true });
  expect(packaged.layerClass).toBe("office");
  expect(packaged.characters).toBe(null);
  expect(packaged.terminal).toBe(true);

  const gzipped = checkArtifact({ bytes: fs.readFileSync(committedPdf), mediaType: "application/gzip", finalUrl: "https://example.org/supplement.pdf.gz", hasDoi: true });
  expect(gzipped.layerClass).toBe("container");
  expect(gzipped.terminal).toBe(true);
});

it("holds every threshold below the floor the measurement found for its class", () => {
  // The floors, measured over the 274 committed artifacts and the 38 pilot
  // objects. A threshold at or above a floor would refuse a real artifact.
  const floors = { pdf: 11948, xml: 2316, html: 1453, text: 135 } as const;
  for (const [layerClass, floor] of Object.entries(floors))
    expect(minimumCharacters[layerClass as keyof typeof floors]!).toBeLessThan(floor);
  // The largest interstitial measured is the 1,422 character Nature table
  // page, and the weak window has to sit above it.
  expect(phraseWindows.weak).toBeGreaterThan(1422);
  expect(phraseWindows.weak).toBeLessThan(6555);
});
