/** Whether the bytes a route returned are the artifact.
 *
 * The 2026-11-17 pilot stored 38 of 40 sources and reported all 38 as held.
 * Four of them were not the source. link.springer.com served 346 KB of HTML
 * for a chapter behind a cookie wall and the whole text layer was a
 * 76 character title line; alphafoldserver.com served 382 KB that rendered to
 * nothing at all; a Nature extended data table came back as 1,422 characters
 * of cookie notice and caption with the table itself absent; and a Nature
 * article came back as the publisher's own HTML while Europe PMC held the
 * JATS XML the whole time. Each one returned 200, so each one was called
 * stored. This module is what makes stored mean we hold the artifact.
 *
 * Three independent checks, because no one of them covers the four cases.
 *
 * 1. A publisher's HTML is never the end of the chain for a source with a
 *    DOI. For such a source the artifact of record is the PDF or the JATS
 *    XML, and the three DOI routes exist to find it. The HTML is a surrogate
 *    even when it renders the whole article: the Nature case above renders
 *    118,205 characters and Europe PMC still has the better copy. So the
 *    fallbacks run, and the HTML is kept only when none of them reaches the
 *    artifact.
 * 2. A minimum of usable text per class, measured rather than invented. See
 *    minimumCharacters below for each floor and what set it.
 * 3. A detector for the interstitials: cookie consent pages, human
 *    verification, access teasers, subscribe teasers, and a redirect that
 *    lands on a login or consent path.
 *
 * Two measured facts shape check 3, and both are the reason it is not simply
 * a phrase list.
 *
 * The phrases are read from the raw markup, not from the text layer. html.ts
 * strips dialog, header, footer, aside and nav with their content, which is
 * exactly where a cookie banner and a verification notice live. The Springer
 * cookie wall has nothing but its title left by the time the layer exists.
 *
 * And a phrase alone condemns nothing, because cookie wording is on every
 * page a large publisher serves. Measured over the 274 committed artifacts
 * and the 38 pilot objects, consent wording appears in the markup of two
 * GitHub repository pages (6,555 and 13,614 characters), a committed
 * preprint full text (50,523) and the Nature article full text (118,205),
 * all four of them genuine. So a phrase counts only in a body short enough
 * to hold no artifact, and the two windows below come from that measurement.
 *
 * Nothing here is a verdict on the source. It is a verdict on one response.
 * A source whose artifact no route reached keeps its bytes and gets the
 * not_artifact outcome, so a later run can try again.
 */
import { classify, decode, type LayerClass } from "./layers/classify";
import { layerOf } from "./layers/index";
import { sourceClassOf } from "./worklist";
import type { Reason, SourceClass } from "./schema";

/** The least usable text a class may produce and still be the artifact.
 *
 * Measured with the command in docs/source-preservation.md over the 274
 * committed artifacts and the 38 objects the pilot stored. Each floor is the
 * smallest character count a genuine artifact of that class produced, and
 * each threshold sits below its floor:
 *
 *   pdf   floor 11,948  a committed two page assessment note
 *   xml   floor  2,316  the arXiv Atom record for 2306.15006
 *   html  floor  1,453  the committed poisk-explorer page
 *   text  floor    135  a committed one paragraph note
 *
 * html is the binding one. Its floor of 1,453 is 31 characters above the
 * largest interstitial measured, the 1,422 character Nature table page, so a
 * threshold cannot separate those two and is not asked to: check 1 and
 * check 3 take that case and this threshold stays a round number below the
 * floor. It catches the two stubs no other check would argue about, at 76
 * and 0 characters.
 *
 * text is only required to be non-empty. Two HuggingFace dataset configs the
 * pilot stored are 510 and 518 characters and are exactly what their records
 * point at, so nothing in the measured set separates a short real text file
 * from a short stub by length.
 *
 * A class absent from this table is not measured by length: a container is
 * the artifact, an office package is measured by the extractor lane rather
 * than at capture, and any other unknown class produces no layer to
 * measure.
 */
export const minimumCharacters: Partial<Record<LayerClass, number>> = {
  pdf: 1024,
  xml: 1024,
  html: 1024,
  text: 1,
};

/** How short a body has to be for a phrase in its markup to condemn it.
 *
 * weak covers cookie and consent wording, which genuine pages carry. The
 * largest interstitial measured is 1,422 characters and the smallest genuine
 * page carrying consent wording is 6,555, so 2,048 sits inside that gap.
 *
 * strong covers human verification, access teasers, subscribe teasers and
 * sign-in walls. None of those phrases appears anywhere in the 312 content
 * nodes measured, so the window is set by what an interstitial plausibly is
 * rather than by a false positive: a publisher teaser carrying an abstract
 * runs to a few thousand characters, and 8,192 is above that and below the
 * median genuine page.
 */
export const phraseWindows = { weak: 2048, strong: 8192 } as const;

/** The phrases, read from the raw markup. weak wording is on genuine pages
 * and only counts in a short body; strong wording was measured nowhere. */
export const interstitialPhrases: { name: string; strength: "weak" | "strong"; pattern: RegExp }[] = [
  { name: "cookie-consent", strength: "weak", pattern: /we use cookies|accept all cookies|cookie (policy|settings|preferences)|manage (your )?cookies/i },
  { name: "cookies-required", strength: "weak", pattern: /cookies_not_supported|cookies are not supported|please enable cookies/i },
  { name: "human-verification", strength: "strong", pattern: /verifying you are human|verify you are (a )?human|checking your browser|just a moment|attention required/i },
  { name: "javascript-required", strength: "strong", pattern: /(enable|turn on) javascript|javascript is (disabled|required)/i },
  { name: "access-teaser", strength: "strong", pattern: /get access|access options|buy (this )?article|purchase access|institutional access|access through your/i },
  { name: "subscribe-teaser", strength: "strong", pattern: /subscribe to (continue|read)|subscription required|become a (member|subscriber)/i },
  { name: "sign-in-wall", strength: "strong", pattern: /(sign|log) in to (continue|read|view|access)/i },
];

/** Path segments that mean the redirect ended somewhere other than the
 * artifact. Segments only: the query string carries no signal, because
 * error=cookies_not_supported is on the final URL of two genuine Springer
 * PDFs and of the Nature article full text as well as of the cookie wall. */
const stopSegments = new Set([
  "login",
  "signin",
  "sign-in",
  "log-in",
  "logon",
  "auth",
  "authorize",
  "sso",
  "consent",
  "cookieabsent",
  "cookies",
  "captcha",
  "challenge",
  "denied",
  "accessdenied",
  "forbidden",
  "paywall",
  "subscribe",
]);

const landsOnStopPath = (url: string): boolean => {
  let parsed: URL;
  try {
    parsed = new URL(url);
  } catch {
    return false;
  }
  return parsed.pathname
    .split("/")
    .some((segment) => stopSegments.has(decodeURIComponent(segment).toLowerCase()));
};

const hostClassOf = (url: string): SourceClass | null => {
  try {
    return sourceClassOf(new URL(url).host);
  } catch {
    return null;
  }
};

export interface ArtifactInput {
  /** The bytes as received, before they are gzipped into the cache. */
  bytes: Buffer;
  /** The media type as served, which is a hint. The class comes from the
   * bytes: the pilot was served one XLSX as application/octet-stream. */
  mediaType?: string | null;
  /** The URL the response came from, after redirects. */
  finalUrl: string;
  /** The URL the record asked for, where it differs. Its host decides the
   * publisher check as well, because a publisher landing page redirects to
   * its own consent host. */
  requestedUrl?: string;
  /** Whether any source sharing this URL carries a DOI, which is what the
   * three fallback routes need to resolve. */
  hasDoi: boolean;
  /** Whether pdftotext is available. Without it a PDF produces no layer and
   * is not measured, never failed. */
  pdftotext?: boolean;
}

export interface ArtifactCheck {
  /** Whether this response may end the route chain. */
  terminal: boolean;
  /** Why it may not, for the receipt and for routes_tried. */
  reason: Reason | null;
  /** What the check saw, so a log line and a test can both cite it. */
  layerClass: LayerClass;
  /** Characters of usable text, or null when the class produces no layer. */
  characters: number | null;
  /** Which phrases matched, in table order. */
  signals: string[];
}

const measured = (
  terminal: boolean,
  reason: Reason | null,
  layerClass: LayerClass,
  characters: number | null,
  signals: string[] = [],
): ArtifactCheck => ({ terminal, reason, layerClass, characters, signals });

/** Whether one response is the artifact, and if not, what it is instead. */
export function checkArtifact(input: ArtifactInput): ArtifactCheck {
  const classification = classify(input.bytes, input.mediaType);
  const layerClass = classification.class;

  // A container is the artifact. Its members are expanded by the layer work
  // after it is stored, so there is nothing to measure here and expanding it
  // twice would only cost the run. An office package is a zip and goes the
  // same way: shared/archive/layers/office reads it once the bytes are
  // stored, and no length threshold was ever measured for one.
  if (layerClass === "container" || layerClass === "office" || layerClass === "unknown")
    return measured(true, null, layerClass, null);

  const tree = layerOf(input.bytes, { mediaType: input.mediaType, pdftotext: input.pdftotext, maxDepth: 0 });
  const characters = tree.layer?.characters ?? null;

  const isHtml = layerClass === "html";
  const signals: string[] = [];
  if (isHtml) {
    const markup = classification.encoding ? decode(input.bytes, classification.encoding) : "";
    for (const phrase of interstitialPhrases) {
      const window = phraseWindows[phrase.strength];
      if (characters !== null && characters >= window) continue;
      if (phrase.pattern.test(markup)) signals.push(phrase.name);
    }
    if (landsOnStopPath(input.finalUrl)) signals.push("stop-path");
    if (signals.length) return measured(false, "interstitial_body", layerClass, characters, signals);
  }

  // A class with no layer is not measured by length. pdftotext missing, or a
  // normaliser that could not read the bytes, is a gap in our tooling and not
  // evidence about the response.
  const floor = minimumCharacters[layerClass];
  if (characters !== null && floor !== undefined && characters < floor)
    return measured(false, "text_below_threshold", layerClass, characters, signals);

  if (isHtml && input.hasDoi) {
    const publisher =
      hostClassOf(input.finalUrl) === "publisher" ||
      (input.requestedUrl !== undefined && hostClassOf(input.requestedUrl) === "publisher");
    if (publisher) return measured(false, "publisher_html_only", layerClass, characters, signals);
  }

  return measured(true, null, layerClass, characters, signals);
}
