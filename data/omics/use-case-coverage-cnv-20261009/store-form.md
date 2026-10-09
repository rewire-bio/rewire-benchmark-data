# Store form of the reviewed batch

`batch.jsonl` is the reviewed batch and is unchanged. The store holds `batch.store.jsonl`, made from it in three deterministic steps after `main` adopted single-meaning relations (#50) and declared attributes (#54):

1. `normalizeRecords` (`shared/omics/relations.ts`): relation renames only.
2. `npm run attributes:migrate -- --batch` (`normalizeAttributes`): missing reasons, uncertainty and review shapes.
3. `python3 -I extract/registry_fit.py`: moves keys the registry does not declare to declared ones. Every move is listed below. `pmcid` is dropped because each value is already in the source `version` and `artifact_url`. Results rename `source_cell_text` to the declared `raw_xml_value`.

Running step 2 again leaves the file byte-identical (SHA-256 `2b57950eebf38140e49303be16fa5e699cda860bf9f5d9d0adf4b7f52bc8d662`).

## Moves

- `cnv-20261009-benchmark-seqc2-hcc1395-somatic-cnv`: missing_metadata.printed_results moved to limitations
- `cnv-20261009-config-nardone2025-dragen-4-0`: version_note moved to model_identity_note
- `cnv-20261009-data-behera2024-hg002-giab-sv06-cnv-del-bins`: related_dataset moved to scope_note
- `cnv-20261009-data-delavega2025-coriell-virtual-panel`: missing_metadata.truth_counts moved to missing_metadata.denominator
- `cnv-20261009-data-delavega2025-hg002-giab-sv06-exons`: missing_metadata.per_stratum_counts moved to missing_metadata.denominator
- `cnv-20261009-data-gabrielaite2021-na12878-wgs`: missing_metadata.exact_depth moved to missing_metadata.population_detail
- `cnv-20261009-data-nardone2025-hg002-giab-sv06-tier1-del-hg38`: missing_metadata.scored_truth_count moved to missing_metadata.scored_count
- `cnv-20261009-data-nardone2025-hg002-giab-sv06-tier1-del-hg38`: missing_metadata.depth and .aligner merged into population_detail (reason conflicting)
- `cnv-20261009-data-seqc2-hcc1395-cnv-benchmark`: missing_metadata.per_caller_values moved to scope_note
- `cnv-20261009-eval-delavega2025-dragen42-default`: missing_metadata.origin_note moved to limitations
- `cnv-20261009-eval-delavega2025-dragen42-hs`: missing_metadata.origin_note moved to limitations
- `cnv-20261009-eval-delavega2025-dragen42-hs-coriell-panel`: missing_metadata.origin_note moved to limitations
- `cnv-20261009-eval-delavega2025-dragen42-hs-filters`: missing_metadata.origin_note moved to limitations
- `cnv-20261009-eval-delavega2025-dragen42-hs-filters-coriell-panel`: missing_metadata.origin_note moved to limitations
- `cnv-20261009-eval-nardone2025-cnvnator`: missing_metadata.inputs moved to missing_metadata.comparison.inputs
- `cnv-20261009-eval-nardone2025-delly`: missing_metadata.inputs moved to missing_metadata.comparison.inputs
- `cnv-20261009-eval-nardone2025-dragen-4-0`: missing_metadata.inputs moved to missing_metadata.comparison.inputs
- `cnv-20261009-eval-nardone2025-dragen-4-2`: missing_metadata.inputs moved to missing_metadata.comparison.inputs
- `cnv-20261009-eval-nardone2025-ingap`: missing_metadata.inputs moved to missing_metadata.comparison.inputs
- `cnv-20261009-eval-nardone2025-lumpy`: missing_metadata.inputs moved to missing_metadata.comparison.inputs
- `cnv-20261009-eval-nardone2025-manta`: missing_metadata.inputs moved to missing_metadata.comparison.inputs
- `cnv-20261009-eval-nardone2025-matchclip`: missing_metadata.inputs moved to missing_metadata.comparison.inputs
- `cnv-20261009-eval-nardone2025-softsv`: missing_metadata.inputs moved to missing_metadata.comparison.inputs
- `cnv-20261009-eval-nardone2025-wham`: missing_metadata.inputs moved to missing_metadata.comparison.inputs
- `cnv-20261009-protocol-behera2024-hg002-cnv-del-10-20kb`: printed_label_note moved to scope_note
- `cnv-20261009-protocol-delavega2025-coriell-virtual-panel`: missing_metadata.sensitivity moved to limitations
- `cnv-20261009-protocol-gabrielaite2021-na12878-wgs-overlap`: missing_metadata.dosage_direction moved to missing_metadata.metric_definition
- `cnv-20261009-protocol-gabrielaite2021-na12878-wgs-overlap`: missing_metadata.tool_versions moved to limitations
- `cnv-20261009-protocol-nardone2025-hg002-del-wittyer`: missing_metadata.matching_parameters moved to missing_metadata.metric_implementation
- `cnv-20261009-source-delavega2025`: dropped pmcid PMC12005901 (already in version and artifact_url)
- `cnv-20261009-source-delavega2025-table-s3`: container_sha256 moved to hash_scope
- `cnv-20261009-source-gabrielaite2021`: dropped pmcid PMC8699073 (already in version and artifact_url)
- `cnv-20261009-source-gabrielaite2021-table-s2`: container_sha256 moved to hash_scope
- `cnv-20261009-source-nardone2025`: dropped pmcid PMC12383524 (already in version and artifact_url)
- `cnv-20261009-source-nardone2025-table-s1`: container_sha256 moved to hash_scope
- `cnv-20261009-source-seqc2-somatic-cnv-2024`: dropped pmcid PMC11188507 (already in version and artifact_url)
