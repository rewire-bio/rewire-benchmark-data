/** The licence map has to stay complete, or a source gets a tier nobody chose.
 *
 * Three files have to agree: the archiveTiers in shared/archive/schema.ts, the SKOS
 * schemes in data/vocab/, and the rows in data/archive/licence-map.tsv. These
 * tests pin them to each other and to the licence strings the store carries,
 * so a new licence string fails the build until someone reviews it.
 */
import { describe, expect, it } from "vitest";
import { determineForSource, licenceClassifier, prePolicySourceIds, readLicenceMap, readSourceLicences, stricterTier } from "../scripts/licence/map";
import { buildTriage } from "../scripts/licence/triage";
import { defaultArchiveTier, archiveTiers, visibilityOf } from "../shared/archive/schema";
import { loadSchemes } from "../scripts/omics/vocab";

const map = readLicenceMap();
const licences = readSourceLicences();
const schemes = loadSchemes();

/** The row a spelling row names in its note, or null when the row is not a
 * spelling of another. The note form is fixed so that the claim is checkable:
 *   Read as a spelling of "<row>" on <date>.
 */
const spellingOf = (licence: string): string | null => {
  const note = map.get(licence)?.note ?? "";
  const read = /^Read as a spelling of "(.+)" on \d{4}-\d{2}-\d{2}\./.exec(note);
  return read ? read[1] : null;
};

/** Whether a row is an owner ruling on a string no record carries: a licence a
 * metadata service serves that no earlier row states a reading for, so it can
 * be neither a record row nor a spelling of one. The note form is fixed so the
 * claim is checkable:
 *   Owner ruling of <date> (issue <n>): ...
 */
const isRuling = (licence: string): boolean => /^Owner ruling of \d{4}-\d{2}-\d{2} \(issue \d+\): \S/.test(map.get(licence)?.note ?? "");

describe("licence map", () => {
  it("maps every licence string the store carries", () => {
    const unmapped = [...new Set([...licences.values()].filter((licence): licence is string => licence !== null))]
      .filter((licence) => !map.has(licence))
      .sort();
    expect(unmapped, "add a reviewed row to data/archive/licence-map.tsv for each of these").toEqual([]);
  });

  it("gives every row a tier, family and basis that exist as concepts", () => {
    const tierKeys = schemes.get("archive-tier")!.concepts;
    const familyKeys = schemes.get("licence-family")!.concepts;
    const basisKeys = schemes.get("licence-basis")!.concepts;
    for (const row of map.values()) {
      expect(tierKeys.has(row.archive_tier), `${row.licence}: tier ${row.archive_tier}`).toBe(true);
      expect(familyKeys.has(row.family), `${row.licence}: family ${row.family}`).toBe(true);
      expect(basisKeys.has(row.basis), `${row.licence}: basis ${row.basis}`).toBe(true);
    }
  });

  it("keeps the archive-tier scheme and the archiveTiers in the archive schema identical", () => {
    expect([...schemes.get("archive-tier")!.concepts.keys()].sort()).toEqual([...archiveTiers].sort());
  });

  it("stores an unmapped licence string privately instead of stopping the fetch", () => {
    // The build fails on an unmapped string. A fetch in progress must not: a
    // licence never blocks capture, so the object lands at the private default
    // with the string nobody mapped recorded beside it.
    const id = [...licences.keys()][0];
    const determination = determineForSource(id, new Map(), new Map([[id, "A licence nobody has mapped"]]));
    expect(determination.reason).toBe("unmapped-licence");
    expect(determination.archive_tier).toBe(defaultArchiveTier);
    expect(visibilityOf(determination.archive_tier)).toBe("restricted");
    expect(determination.observed_licence).toBe("A licence nobody has mapped");
  });

  it("holds no row the store no longer uses, except a declared spelling or ruling", () => {
    // An orphan row is not harmful, but it is a sign a licence string was
    // edited on a record rather than superseded, so it is worth seeing.
    //
    // Two kinds of row are the exception, and both exist for the resolver
    // rather than for a record. A spelling row reads a served string as a
    // licence an earlier row already states. A ruling row carries a reading
    // the owner made for a served string no earlier row covers, which is why
    // it cannot be a spelling of anything.
    // data/archive/licence-candidates.jsonl is not committed, so the check is
    // on the note rather than on the candidates.
    const carried = new Set([...licences.values()].filter((licence) => licence !== null));
    expect([...map.keys()].filter((licence) => !carried.has(licence) && !spellingOf(licence) && !isRuling(licence))).toEqual([]);
  });

  it("gives every ruling row a licence string no record carries and no spelling note", () => {
    // A ruling row is for a string only a metadata service serves. One a
    // record carries belongs in the ordinary review path, and one an earlier
    // row already reads belongs in a spelling row, so a ruling row that is
    // either is a row filed under the wrong kind.
    const carried = new Set([...licences.values()].filter((licence) => licence !== null));
    for (const licence of [...map.keys()].filter(isRuling)) {
      expect(carried.has(licence), `${licence}: a record carries this string, so it is not a ruling row`).toBe(false);
      expect(spellingOf(licence), `${licence}: a row cannot be both a ruling and a spelling`).toBeNull();
    }
  });

  it("gives every spelling row the family and tier of the row it is read as", () => {
    // The whole guarantee of a spelling row: it adds a key, never a reading.
    // The row it points at has to be one a record carries, so no spelling
    // stands on another spelling and every tier traces to a reviewed row.
    const carried = new Set([...licences.values()].filter((licence) => licence !== null));
    for (const row of map.values()) {
      const target = spellingOf(row.licence);
      if (!target) continue;
      const read = map.get(target);
      expect(read, `${row.licence}: no row "${target}"`).toBeDefined();
      expect(carried.has(target), `${row.licence}: "${target}" is not a licence any record carries`).toBe(true);
      expect(read!.family, `${row.licence}: family`).toBe(row.family);
      expect(read!.archive_tier, `${row.licence}: tier`).toBe(row.archive_tier);
    }
  });

  it("gives a source with no licence the private default, never a public tier", () => {
    const blank = [...licences.entries()].filter(([, licence]) => licence === null).map(([id]) => id);
    expect(blank.length).toBeGreaterThan(0);
    for (const id of blank.slice(0, 50)) {
      const determination = determineForSource(id, map, licences);
      expect(determination.archive_tier).toBe(defaultArchiveTier);
      expect(visibilityOf(determination.archive_tier)).toBe("restricted");
    }
  });

  it("reads a tier for every source record without throwing", () => {
    for (const id of licences.keys()) expect(archiveTiers).toContain(determineForSource(id, map, licences).archive_tier);
  });

  it("takes the most restrictive tier when sources share an object", () => {
    expect(stricterTier("t0-public", "t3-verbatim-nd-nc")).toBe("t3-verbatim-nd-nc");
    expect(stricterTier("t4-private", "t1-public-nc")).toBe("t4-private");
    expect(stricterTier("t0-public", "t2-verbatim-nd")).toBe("t2-verbatim-nd");
    const classify = licenceClassifier();
    const input = { url: "https://example.org/x", mediaType: "application/pdf" };
    const open = classify({ ...input, sourceIds: ["protein-stability-20261009-source-chu2024"] });
    expect(open.archive_tier).toBe("t0-public");
    const mixed = classify({ ...input, sourceIds: ["protein-stability-20261009-source-chu2024", "phylogpn-2025"] });
    expect(mixed.archive_tier).toBe("t3-verbatim-nd-nc");
    expect(mixed.observed_licence).toBe("CC BY-NC-ND 4.0");
    expect(classify({ ...input, sourceIds: [] }).archive_tier).toBe(defaultArchiveTier);
  });

  it("marks the seven pre-policy originals and nothing else", () => {
    const classify = licenceClassifier();
    const input = { url: "https://example.org/x", mediaType: "application/pdf" };
    for (const id of prePolicySourceIds) {
      expect(licences.has(id), `${id} is not a source record`).toBe(true);
      expect(classify({ ...input, sourceIds: [id] }).exposure).toBe("pre-policy");
    }
    expect(classify({ ...input, sourceIds: ["protein-stability-20261009-source-chu2024"] }).exposure).toBe("policy");
  });

  it("puts every undetermined source in the triage queue and no determined one", () => {
    const queued = new Set(buildTriage().map((row) => row.source_id));
    for (const [id, licence] of licences) {
      const basis = licence === null ? null : map.get(licence)!.basis;
      if (basis === "identifier" || basis === "prose") expect(queued.has(id), `${id} has a determined licence`).toBe(false);
      if (basis === "unresolved" || basis === "conflicting") expect(queued.has(id), `${id} needs a determination`).toBe(true);
    }
  });
});
