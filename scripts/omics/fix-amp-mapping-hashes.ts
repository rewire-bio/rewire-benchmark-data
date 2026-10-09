/** Compute the real mappingEvidenceHash for each new AMP mapping against the
 * just-built candidate snapshot, and patch it into data/omics/use-cases/
 * inputs.json in place of the placeholder. Explicit review step per
 * integration-plan.md: "this hash can only be computed once the referenced
 * catalogue records exist in a built snapshot ... not before." Run once,
 * then rebuild to confirm every mapping stays active (not demoted). */
import fs from "node:fs";
import { mappingEvidenceHash, parseUseCaseInputs } from "../../shared/omics/use-cases";
import type { CatalogueSnapshot } from "../../shared/omics/catalogue-query";

const NEW_MAPPING_IDS = [
  "use-case-mapping-amp-20261007-issue10-lancet-virtual-tumor",
  "use-case-mapping-amp-20261007-issue11-enfusion-seraseq",
  "use-case-mapping-amp-20261007-issue11-enfusion-nch-clinical",
  "use-case-mapping-amp-20261007-issue12-fraser-kremer",
  "use-case-mapping-amp-20261007-issue13",
  "use-case-mapping-amp-20261007-issue14",
  "use-case-mapping-amp-20261007-issue15",
  "use-case-mapping-amp-20261007-issue16",
  "use-case-mapping-amp-20261007-issue17",
  "use-case-mapping-amp-20261007-issue18",
  "use-case-mapping-amp-20261007-feng-splice-acceptor",
  "use-case-mapping-amp-20261007-feng-splice-donor",
  "use-case-mapping-amp-20261007-feng-promoter-tata",
  "use-case-mapping-amp-20261007-feng-promoter-nontata",
  "use-case-mapping-amp-20261007-feng-pathogenic-common-variant",
  "use-case-mapping-amp-20261007-feng-qtl-eqtl",
  "use-case-mapping-amp-20261007-feng-qtl-sqtl",
  "use-case-mapping-amp-20261007-feng-qtl-paqtl",
  "use-case-mapping-amp-20261007-feng-qtl-ipaqtl",
];

function main() {
  const snapshot: CatalogueSnapshot = JSON.parse(fs.readFileSync("public/omics/catalogue.json", "utf8"));
  const rawInputs = JSON.parse(fs.readFileSync("data/omics/use-cases/inputs.json", "utf8"));
  const inputs = parseUseCaseInputs(rawInputs);
  const useCasesById = new Map(inputs.use_cases.map((u) => [u.id, u]));
  const updated = rawInputs.mappings.map((m: any) => {
    if (!NEW_MAPPING_IDS.includes(m.id)) return m;
    const entry = useCasesById.get(m.use_case_id);
    if (!entry) throw new Error(`Unknown use case for mapping ${m.id}`);
    const hash = mappingEvidenceHash(snapshot, entry, m);
    return { ...m, evidence_sha256: hash };
  });
  const touched = updated.filter((m: any) => NEW_MAPPING_IDS.includes(m.id));
  if (touched.length !== NEW_MAPPING_IDS.length)
    throw new Error(`Expected to update ${NEW_MAPPING_IDS.length} mappings, touched ${touched.length}`);
  rawInputs.mappings = updated;
  fs.writeFileSync("data/omics/use-cases/inputs.json", JSON.stringify(rawInputs, null, 2) + "\n");
  console.log(`Patched evidence_sha256 for ${touched.length} new mappings.`);
  for (const m of touched) console.log(` ${m.id}: ${m.evidence_sha256}`);
}
main();
