/** The sanity gate: whether a layer can be used as an extraction substrate.
 *
 * ADR 0002 decision 1 names five signals and one verdict of pass, suspect or
 * fail. It does not name thresholds, and a threshold argued from theory would
 * be a guess. Every number below was set from the 2,227 layers the archive's
 * 1,167 objects produce, and each one records the measurement it came from
 * and how many real layers it cuts. The run is
 * `npm run layers -- build`, and `npm run layers -- thresholds` reprints the
 * distribution each threshold sits in.
 *
 * The shape of the calibration set matters, so it is stated here. 24 of the
 * objects are labelled bad by the archive lane: their fetch receipt says
 * `not_artifact`, meaning bytes arrived and are demonstrably not the source.
 * They are the negative set. The other 1,143 are the positive set, and the
 * rule everywhere below is that a `fail` threshold cuts none of the positive
 * set, because a gate that refuses real work gets switched off, which is how
 * the one check this repository already had came to be run on 14 of 194
 * batch folders.
 *
 * The five properties, with what each one measured.
 *
 * P1 offsets stable under regeneration. Deriving every layer twice from the
 *    same stored bytes gave the same sha256 on 2,227 of 2,227, pdftotext
 *    26.08.0 included. The property is therefore an equality, not a
 *    threshold, and `npm run layers -- check` re-derives and reports any
 *    layer whose hash moved. It is recorded per layer rather than measured
 *    per layer: a hash that reproduces is the only evidence a span taken
 *    today still points at the same characters tomorrow.
 *
 * P2 non-zero characters. 8 of 2,227 layers hold no non-whitespace character
 *    at all: 6 HTML pages that render to nothing and 2 PDFs whose text layer
 *    is three page breaks. A layer with no content cannot carry a span, so
 *    this is a fail at zero with no threshold to choose.
 *
 * P3 printable ratio. Over the 2,219 layers with content the minimum is
 *    0.9914, on the Chai-1 technical report, whose text layer carries 400
 *    control characters in 46,500, 306 of them NUL. The fail threshold is
 *    0.98, which cuts none of them; the suspect threshold is 0.999, which
 *    flags 2 (0.09%).
 *
 * P4 replacement characters. 11 layers of 2,227 carry any U+FFFD, and the
 *    highest share is 0.0030, on a bioRxiv preprint. The fail threshold is
 *    0.01, over three times the measured maximum and cutting none of them;
 *    any occurrence is suspect, which flags 11 (0.49%).
 *
 * P5 punctuation-run mojibake. This is the bacformer version 2 case ADR 0002
 *    requires to come out fail: a font mapping that rendered 0.81 +/- 0.07 as
 *    +.)! +.+( and had a conclusion drawn from it. Its signature is text that
 *    is heavy in punctuation and holds no digits, because the digits became
 *    punctuation. Measured over the 1,846 layers of 1,000 characters or more:
 *    9 carry punctuation above a quarter of the text, 7 of them plain text or
 *    CSV and 2 HTML, and their digit share runs from 0.044 to 0.879; 157 have
 *    a digit share under 0.005, and the highest punctuation share among those
 *    is 0.1661. The two conditions together occur 0 times, and the gap either
 *    way is wide. So the rule is punctuation above 0.25 and digits under
 *    0.005 of alphanumerics, on a layer of at least 1,000 characters, and it
 *    cuts none of the store. The floor is there because the ratios of a short
 *    layer are noise: 381 layers hold under 1,000 characters and 139 of them
 *    carry no digit at all.
 *
 * P6 page breaks against pdfinfo. A PDF text layer must carry one form feed
 *    per page. Measured over all 201 PDF layers in the store, pdfinfo and the
 *    form feed count agree 201 times out of 201, so a mismatch is a fail with
 *    no tolerance. A PDF pdfinfo cannot read records null and the property is
 *    not applied, because an unreadable pdfinfo is a fact about pdfinfo.
 *
 * What was tried and is not here. No threshold on layer length separates the
 * negative set from the positive one. The 24 bad layers run from 0 to 6,236
 * characters and 16 legitimate stored layers sit under 2,000, because a model
 * hub's config.json is a legitimate 900-character source. A length gate at
 * any point that caught the negatives would cut real layers, so the archive
 * lane's capture-time check keeps that job and this gate does not repeat it.
 */
import type { LayerMetrics, SanityVerdict } from "./types";

/** Every threshold, in one object, so a reader can see them together and a
 * test can assert on them. Each is annotated with what it cut when it was
 * set. */
export const thresholds = {
  /** P3 fail. Measured minimum over layers with content: 0.9914. Cuts 0. */
  printableFail: 0.98,
  /** P3 suspect. Flags 2 of 2,219 (0.09%). */
  printableSuspect: 0.999,
  /** P4 fail. Measured maximum: 0.0030. Cuts 0. */
  replacementFail: 0.01,
  /** P5, punctuation share. Measured: 9 layers above it, all digit-rich. */
  mojibakePunctuation: 0.25,
  /** P5, digit share of alphanumerics. Measured: none of those 9 is below
   * it. */
  mojibakeDigits: 0.005,
  /** P5 floor. Below this the ratios are noise: 381 layers, 40 with no
   * digit. */
  mojibakeCharacters: 1000,
} as const;

/** Count what the gate reads. One pass over the code points, because a layer
 * can be thirteen million characters long. */
export function metricsOf(text: string, pdfPages: number | null = null): LayerMetrics {
  let characters = 0;
  let nonSpace = 0;
  let replacement = 0;
  let printable = 0;
  let digits = 0;
  let letters = 0;
  let punctuation = 0;
  let run = 0;
  let longestRun = 0;
  let pageBreaks = 0;
  for (const character of text) {
    characters += 1;
    const code = character.codePointAt(0) as number;
    if (character === "�") replacement += 1;
    if (character === "\f") pageBreaks += 1;
    const control = (code < 0x20 && !"\t\n\r\f".includes(character)) || (code >= 0x7f && code <= 0x9f);
    if (!control) printable += 1;
    const space = /\s/u.test(character);
    if (!space) nonSpace += 1;
    const digit = /\p{Nd}/u.test(character);
    const letter = !digit && /\p{L}/u.test(character);
    if (digit) digits += 1;
    else if (letter) letters += 1;
    if (!digit && !letter && !space) {
      punctuation += 1;
      run += 1;
      if (run > longestRun) longestRun = run;
    } else run = 0;
  }
  return {
    characters,
    non_space: nonSpace,
    replacement,
    printable,
    digits,
    letters,
    punctuation,
    longest_punctuation_run: longestRun,
    page_breaks: pageBreaks,
    pdf_pages: pdfPages,
  };
}

/** The three ratios the thresholds are written in. Separate from the record,
 * which holds counts, so that a regenerated registry is byte-identical. */
export function ratiosOf(metrics: LayerMetrics): {
  printable: number;
  replacement: number;
  punctuation: number;
  digits: number;
} {
  const alphanumeric = metrics.digits + metrics.letters;
  return {
    printable: metrics.characters ? metrics.printable / metrics.characters : 0,
    replacement: metrics.characters ? metrics.replacement / metrics.characters : 0,
    punctuation: metrics.characters ? metrics.punctuation / metrics.characters : 0,
    digits: alphanumeric ? metrics.digits / alphanumeric : 0,
  };
}

export interface Sanity {
  verdict: SanityVerdict;
  /** One line per property the gate did not find, worst first. Empty at
   * pass. */
  reasons: string[];
}

const round = (value: number, places = 4): string => value.toFixed(places);

/**
 * The verdict for one layer.
 *
 * `normaliser` decides whether the PDF page-break property applies. It is the
 * normaliser id from `shared/archive/layers`, so a second PDF normaliser
 * would have to be named here rather than inheriting the rule silently.
 */
export function sanityOf(metrics: LayerMetrics, normaliser: string): Sanity {
  const ratios = ratiosOf(metrics);
  const fail: string[] = [];
  const suspect: string[] = [];

  // P2. A layer with no content cannot carry a span.
  if (metrics.non_space === 0)
    fail.push(`the layer holds ${metrics.characters} characters and none of them is content`);

  // P3. Control characters where text should be.
  if (metrics.non_space > 0 && ratios.printable < thresholds.printableFail)
    fail.push(`printable characters are ${round(ratios.printable)} of the layer, under ${thresholds.printableFail}`);
  else if (metrics.non_space > 0 && ratios.printable < thresholds.printableSuspect)
    suspect.push(`printable characters are ${round(ratios.printable)} of the layer, under ${thresholds.printableSuspect}`);

  // P4. Bytes the decoder could not read.
  if (ratios.replacement > thresholds.replacementFail)
    fail.push(`U+FFFD is ${round(ratios.replacement)} of the layer, over ${thresholds.replacementFail}`);
  else if (metrics.replacement > 0)
    suspect.push(`the layer carries ${metrics.replacement} U+FFFD ${metrics.replacement === 1 ? "character" : "characters"}`);

  // P5. The bacformer version 2 signature: punctuation where the numbers were.
  if (
    metrics.characters >= thresholds.mojibakeCharacters &&
    ratios.punctuation > thresholds.mojibakePunctuation &&
    ratios.digits < thresholds.mojibakeDigits
  )
    fail.push(
      `punctuation is ${round(ratios.punctuation)} of the layer and digits are ${round(ratios.digits)} of its alphanumerics, ` +
        `the signature of a font mapping that rendered the numbers as punctuation`,
    );

  // P6. A page of the PDF for every page break.
  if (normaliser.startsWith("pdf-text-layer@") && metrics.pdf_pages !== null && metrics.page_breaks !== metrics.pdf_pages)
    fail.push(`the layer carries ${metrics.page_breaks} page breaks and pdfinfo reports ${metrics.pdf_pages} pages`);

  if (fail.length) return { verdict: "fail", reasons: [...fail, ...suspect] };
  if (suspect.length) return { verdict: "suspect", reasons: suspect };
  return { verdict: "pass", reasons: [] };
}

/** Whether a layer may be cited. ADR 0002 decision 1: no record, claim or
 * candidate may cite a layer at fail. A suspect layer may be cited and its
 * reasons travel with it. */
export const usable = (verdict: SanityVerdict): boolean => verdict !== "fail";
