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

  it("holds no row the store no longer uses", () => {
    // An orphan row is not harmful, but it is a sign a licence string was
    // edited on a record rather than superseded, so it is worth seeing.
    const carried = new Set([...licences.values()].filter((licence) => licence !== null));
    expect([...map.keys()].filter((licence) => !carried.has(licence))).toEqual([]);
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
