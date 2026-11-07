"""Evaluations and results for the HyInv batch, built from the parsed cells.

One evaluation per (system, protocol, dataset) and one result per printed cell.
Every evaluation is author_reported: the model's own authors ran every system.
"""

from entities import (
    AREAS, B, BENCHMARK, MODEL, NATIVE, PANEL_DATA, PROTOCOLS, SRC_REPORT, record,
)

HYINV_DEFAULT = f"{B}-config-hyinv-default"

# Page numbers are read from the PDF by parse.pages() and filled in by evidence().
PAGES = {}


def page(key):
    return f"page {PAGES[key]} of {PAGES['count']}"

SYSTEMS = {
    "HyInv": (HYINV_DEFAULT, "hyinv"),
    "ProteinZero V2 (ESM2)": (f"{B}-config-proteinzero-v2-esm2", "proteinzero-v2-esm2"),
    "ProteinZero V2 (ESM1)": (f"{B}-config-proteinzero-v2-esm1", "proteinzero-v2-esm1"),
    "ProteinMPNN grouped": (f"{B}-config-proteinmpnn-grouped", "proteinmpnn-grouped"),
    "ProteinMPNN": (f"{B}-config-proteinmpnn", "proteinmpnn"),
    "LigandMPNN": (f"{B}-config-ligandmpnn", "ligandmpnn"),
    "ProteinMPNN (low-noise, grouped)": (
        f"{B}-config-proteinmpnn-low-noise-grouped", "proteinmpnn-low-noise-grouped"),
    "PiFold": (f"{B}-config-pifold", "pifold"),
    "LM-Design 650M": (f"{B}-config-lm-design-650m", "lm-design-650m"),
    "CMLM": (f"{B}-config-cmlm", "cmlm"),
    "DPLM-2 3B": (f"{B}-config-dplm-2-3b", "dplm-2-3b"),
    "Native": (NATIVE, "native-sequence"),
}

PANEL_SLUG = {
    "CATH4.3 test": ("cath43-test", f"{B}-data-cath43-test"),
    "CATH4.2 test": ("cath42-test", f"{B}-data-cath42-test"),
    "TS500": ("ts500", f"{B}-data-ts500"),
    "TS50": ("ts50", f"{B}-data-ts50"),
    "RecentPDB": ("recentpdb", f"{B}-data-recentpdb"),
    "RecentPDB Boltz2": ("recentpdb", f"{B}-data-recentpdb"),
    "RecentPDB Protenix2": ("recentpdb", f"{B}-data-recentpdb"),
    "Development": ("cath43-validation", f"{B}-data-cath43-validation"),
}

DESIGNS_PER_CHAIN = {
    "CATH4.3 test": "2 designs per chain (K = 2)",
    "CATH4.2 test": "2 designs per chain (K = 2)",
    "TS500": "2 designs per chain (K = 2)",
    "TS50": "2 designs per chain (K = 2)",
    "RecentPDB": "2 designs per chain (K = 2)",
    "RecentPDB Boltz2": "2 designs per chain (K = 2)",
    "RecentPDB Protenix2": "2 designs per chain (K = 2)",
}

REVIEW = {
    "method": ["pdf-text-parse", "deterministic-table-parse", "source-hash-verification"],
    "method_note": "pdftotext -layout text layer of the pinned PDF, parsed by "
                   "data/omics/hyinv-20261106/extract/parse.py, which checks the PDF's SHA-256 "
                   "against the pinned value and asserts every row label, column count and printed "
                   "number format. Table 2 and the scTM block of Figure 14 are asserted to agree with "
                   "Table 6 at their printed precision, the repeated cells of Figure 4a to agree with "
                   "Table 1, and the values repeated in Sections 3.2 and 4 to agree with Tables 8 "
                   "and 9. Printed cell text is kept exactly as printed.",
    "reviewer": ["claude"],
    "reviewer_note": "Extracted by a Claude agent for issue #232. This is the extraction record only: "
                     "no independent review and no human review is claimed, and review-evidence has "
                     "not run on this batch.",
    "date": "2026-11-06",
}


PANEL_DATA_KEY = {
    "RecentPDB Boltz2": "RecentPDB",
    "RecentPDB Protenix2": "RecentPDB",
    "Development": "CATH4.3 validation",
}


def comparison(panel, protocol_id, extra=None):
    # Panels that are not one of the report's named chain panels (the timing
    # backbones, the de novo application panel) carry no PANEL_DATA entry; the
    # caller supplies their population and split through `extra`.
    population = PANEL_DATA.get(PANEL_DATA_KEY.get(panel, panel), (None,) * 6)
    out = {
        "protocol_id": protocol_id,
        "dataset_version": "As assembled for the HyInv technical report (2026-10-14); no chain list "
                           "or split manifest is published",
        "split": population[5],
        "population": population[4],
        "inputs": "Backbone N, CA, C and O coordinates of the panel chain; no sequence, alignment, "
                  "language model or structure predictor at design time",
        "adaptation": "No adaptation: each system runs at one fixed setting on every panel, and no "
                      "panel was used to tune a baseline",
        "metric_implementation": PROTOCOLS[protocol_id.replace(f"{B}-", "")]["implementation"],
        "aggregation": PROTOCOLS[protocol_id.replace(f"{B}-", "")]["aggregation"],
        "budget": DESIGNS_PER_CHAIN.get(panel),
    }
    if extra:
        out.update(extra)
    return out


def evaluation(eval_id, name, system_id, protocol_id, data_id, panel, locator,
               extra_comparison=None, origin_note=None):
    comp = comparison(panel, protocol_id, extra_comparison)
    missing = {
        f"comparison.{key}": {"reason": "unreported"}
        for key, value in comp.items() if value is None
    }
    attributes = {
        "origin": "author_reported",
        "protocol": protocol_id,
        "version": "HyInv technical report, 2026-10-14, retrieved at commit 0dcc533c",
        "comparison": comp,
        "source_locator": locator,
    }
    if missing:
        attributes["missing_metadata"] = missing
    if origin_note:
        attributes["provenance"] = origin_note
    return record(
        eval_id,
        "evaluation",
        name,
        "Author-reported comparison transcribed from the pinned technical report. Run by the team "
        "that released HyInv; not reproduced by Rewire.",
        attributes,
        links=[
            {"relation": "system", "target_id": system_id},
            {"relation": "assessment", "target_id": protocol_id},
            {"relation": "data", "target_id": data_id},
        ],
        facets={"areas": AREAS, "contexts": ["research"]},
        sources=[SRC_REPORT],
    )


def result(result_id, name, eval_id, printed, numeric, protocol_slug, locator,
           uncertainty=None, unit_detail=None, qualifier_extra=None, coverage=None,
           limitations=None):
    spec = PROTOCOLS[protocol_slug]
    attributes = {
        "metric": spec["metric"],
        "metric_direction": spec["direction"],
        "unit": spec["unit"],
        "metric_qualifier": spec["qualifier"] + (f"; {qualifier_extra}" if qualifier_extra else ""),
        "printed_value": printed,
        "numeric_value": numeric,
        "source_locator": locator,
        "review": dict(REVIEW),
    }
    if unit_detail:
        attributes["unit_detail"] = unit_detail
    if coverage:
        attributes["coverage"] = coverage
    if limitations:
        attributes["limitations"] = limitations
    if uncertainty:
        attributes["uncertainty"] = uncertainty
    else:
        attributes["missing_metadata"] = {"uncertainty": {"reason": "unreported"}}
    return record(
        result_id,
        "result",
        name,
        "Value transcribed exactly as printed in the pinned technical report. Author-reported; not "
        "reproduced by Rewire.",
        attributes,
        links=[{"relation": "evaluation", "target_id": eval_id}],
        facets={},
        sources=[SRC_REPORT],
    )


def interval(lower, upper, note=None):
    out = {
        "type": "confidence_interval",
        "lower": lower,
        "upper": upper,
        "level": 0.95,
        "resamples": 10000,
        "method": "bootstrap_percentile",
        "printed": f"[{lower}, {upper}]",
    }
    if note:
        out["note"] = note
    return out


QUALITY_BLOCKS = [
    # (parsed table, cell key, protocol slug, printed column name, locator template)
    ("table6", None, "protocol-sctm-esmfold2", "scTM",
     "Table 6, row '{row}', column '{col}' ({page})"),
    ("figure14", "recovery", "protocol-sequence-recovery", "Recovery",
     "Figure 14, 'Recovery' block, row '{row}', column '{col}' ({page})"),
    ("figure14", "diversity", "protocol-sequence-diversity", "Diversity",
     "Figure 14, 'Diversity' block, row '{row}', column '{col}' ({page})"),
    ("figure15", "plddt", "protocol-plddt-esmfold2", "pLDDT",
     "Figure 15, 'pLDDT' block, row '{row}', column '{col}' ({page})"),
    ("figure15", "scrmsd", "protocol-scrmsd-esmfold2", "scRMSD (A)",
     "Figure 15, 'scRMSD' block, row '{row}', column '{col}' ({page})"),
    ("figure15", "lddt", "protocol-lddt-esmfold2", "CA-lDDT",
     "Figure 15, 'CA-lDDT' block, row '{row}', column '{col}' ({page})"),
]

PREDICTOR_PROTOCOL = {
    "RecentPDB Boltz2": "protocol-sctm-boltz2",
    "RecentPDB Protenix2": "protocol-sctm-protenix2",
}
DIFFERENCE_PROTOCOL = {
    "RecentPDB Boltz2": "protocol-sctm-difference-boltz2",
    "RecentPDB Protenix2": "protocol-sctm-difference-protenix2",
}
COLUMN_LABEL = {
    "RecentPDB Boltz2": "RecentPDB, Boltz2",
    "RecentPDB Protenix2": "RecentPDB, Protenix2",
}
LOW_DIVERSITY_ROWS = {"PiFold", "CMLM", "LM-Design 650M", "DPLM-2 3B"}
LOW_DIVERSITY_NOTE = (
    "Appendix D.2 names this method as a single point at much lower diversity than HyInv, so this "
    "cell is not a matched-diversity comparison."
)


def quality(parsed, out):
    """Table 6, Figure 14 (recovery, diversity) and Figure 15."""
    seen_evals = {}
    for table, block, slug, column_name, locator_template in QUALITY_BLOCKS:
        cells = parsed[table] if block is None else parsed[table][block]
        for (row, panel), value in cells.items():
            system_id, system_slug = SYSTEMS[row]
            protocol_slug = PREDICTOR_PROTOCOL.get(panel, slug)
            protocol_id = f"{B}-{protocol_slug}"
            panel_slug, data_id = PANEL_SLUG[panel]
            short = protocol_slug.replace("protocol-", "")
            eval_id = f"{B}-eval-{short}-{system_slug}-{panel_slug}"
            locator = locator_template.format(
                row=row, col=COLUMN_LABEL.get(panel, panel), page=page(table))
            if eval_id not in seen_evals:
                seen_evals[eval_id] = True
                out.append(
                    evaluation(
                        eval_id,
                        f"{row} on {panel} ({PROTOCOLS[protocol_slug]['name']}, HyInv report)",
                        system_id,
                        protocol_id,
                        data_id,
                        panel,
                        locator,
                    )
                )
            limitations = [LOW_DIVERSITY_NOTE] if row in LOW_DIVERSITY_ROWS else None
            out.append(
                result(
                    f"{B}-result-{short}-{system_slug}-{panel_slug}",
                    f"{row} {column_name} on {panel} (HyInv report)",
                    eval_id,
                    value,
                    value,
                    protocol_slug,
                    locator,
                    limitations=limitations,
                )
            )


def differences(parsed, out):
    """Table 7: HyInv minus baseline, in units of 1e-3 scTM, with a paired 95% interval."""
    for (row, panel), cell in parsed["table7"].items():
        system_id, system_slug = SYSTEMS[row]
        protocol_slug = DIFFERENCE_PROTOCOL.get(panel, "protocol-sctm-difference-esmfold2")
        protocol_id = f"{B}-{protocol_slug}"
        panel_slug, data_id = PANEL_SLUG[panel]
        short = protocol_slug.replace("protocol-", "")
        eval_id = f"{B}-eval-{short}-{system_slug}-{panel_slug}"
        column = COLUMN_LABEL.get(panel, panel)
        locator = f"Table 7, row '{row}', column '{column}' ({page('table7')})"
        out.append(
            evaluation(
                eval_id,
                f"HyInv minus {row} on {panel} (paired scTM difference, HyInv report)",
                system_id,
                protocol_id,
                data_id,
                panel,
                locator,
                extra_comparison={
                    "adaptation": "No adaptation. The difference is paired by chain against the HyInv "
                                  "default setting on the same panel with shared folding randomness; "
                                  "the baseline runs at its one published temperature, so the two "
                                  "systems are not at equal design-set diversity",
                },
            )
        )
        excludes_zero = float(cell["lower"]) > 0 and float(cell["upper"]) > 0
        out.append(
            result(
                f"{B}-result-{short}-{system_slug}-{panel_slug}",
                f"HyInv minus {row} scTM on {panel} (HyInv report)",
                eval_id,
                cell["printed"],
                cell["value"],
                protocol_slug,
                locator,
                uncertainty=interval(
                    cell["lower"], cell["upper"],
                    "Printed in units of 10^-3 scTM, as the point estimate is. The interval "
                    + ("excludes" if excludes_zero else "includes")
                    + " zero.",
                ),
                unit_detail="Units of 10^-3 scTM, exactly as printed",
                qualifier_extra=f"the baseline is {row}",
                limitations=[LOW_DIVERSITY_NOTE] if row in LOW_DIVERSITY_ROWS else None,
            )
        )


TABLE8_SYSTEMS = {
    "Decoupled draft, Td = 0.6 (HyInv default)": (
        f"{B}-config-hyinv-decoupled-td06-update288", "hyinv-decoupled-td06"),
    "Decoupled draft, Td = 0.3": (
        f"{B}-config-hyinv-decoupled-td03-update288", "hyinv-decoupled-td03"),
    "Top-p 0.9": (f"{B}-config-hyinv-topp09-update288", "hyinv-topp09"),
    "Min-p 0.1": (f"{B}-config-hyinv-minp01-update288", "hyinv-minp01"),
}
TABLE8_DIVERSITY = {
    "Development": "read at development diversity D = 0.30",
    "CATH4.3 test": "read at diversity D = 0.32",
    "RecentPDB": "read at diversity D = 0.30",
}


def sampler_gain(parsed, out):
    """Table 8: gain of a sampler setting over the unmodified sampler at equal diversity."""
    slug = "protocol-sctm-fixed-diversity-gain-vs-unmodified-sampler"
    protocol_id = f"{B}-{slug}"
    short = "sctm-fd-gain-vs-unmodified"
    for (row, panel), cell in parsed["table8"].items():
        system_id, system_slug = TABLE8_SYSTEMS[row]
        panel_slug, data_id = PANEL_SLUG[panel]
        eval_id = f"{B}-eval-{short}-{system_slug}-{panel_slug}"
        locator = f"Table 8, row '{row}', column '{panel}' ({page('table8')})"
        out.append(
            evaluation(
                eval_id,
                f"{row} over the unmodified sampler on {panel} at equal diversity (HyInv report)",
                system_id,
                protocol_id,
                data_id,
                panel,
                locator,
                extra_comparison={
                    "adaptation": "Both settings are read from their own scTM-against-diversity "
                                  "curves at the same diversity, so the comparison is at equal "
                                  "diversity by construction. Checkpoint at update 288, not the "
                                  "released update 640",
                    "budget": "Development panel K = 2 designs per chain; held-out panels K = 4 with "
                              "new draws and fold seeds",
                },
            )
        )
        out.append(
            result(
                f"{B}-result-{short}-{system_slug}-{panel_slug}",
                f"{row}: gain over the unmodified sampler on {panel} (HyInv report)",
                eval_id,
                cell["printed"],
                cell["value"],
                slug,
                locator,
                uncertainty=interval(
                    cell["lower"], cell["upper"],
                    "95% interval over CATH topology clusters, over chains on RecentPDB, from 1,000 "
                    "draws in which all points of all curves are recomputed from one cluster "
                    "resample.",
                ),
                qualifier_extra=TABLE8_DIVERSITY[panel],
            )
        )


def numerics_check(parsed, out):
    """Table 9: BF16 path minus the reference sampler at fixed diversity."""
    slug = "protocol-sctm-fixed-diversity-bf16-minus-reference"
    protocol_id = f"{B}-{slug}"
    short = "sctm-fd-bf16-minus-reference"
    subsets = {
        "Subset 1": (f"{B}-data-cath43-validation-subset-1", "subset-1"),
        "Subset 2": (f"{B}-data-cath43-validation-subset-2", "subset-2"),
        "Subset 3": (f"{B}-data-cath43-validation-subset-3", "subset-3"),
        "Whole development panel": (f"{B}-data-cath43-validation", "cath43-validation"),
    }
    for row, cell in parsed["table9"].items():
        data_id, data_slug = subsets[row]
        eval_id = f"{B}-eval-{short}-{data_slug}"
        locator = f"Table 9, row '{row}', column 'S@D difference' ({page('table9')})"
        out.append(
            evaluation(
                eval_id,
                f"BF16 path minus the reference sampler on {row} at fixed diversity (HyInv report)",
                f"{B}-config-hyinv-bf16-update288",
                protocol_id,
                data_id,
                "Development",
                locator,
                extra_comparison={
                    "population": f"{row} of the development panel: {cell['targets']} chains in "
                                  f"{cell['clusters']} CATH topology clusters. The whole panel is the "
                                  "union of the three disjoint subsets",
                    "adaptation": "Both numerical paths are read from their own four-point quadratic "
                                  "fits at development diversity D = 0.30 and paired by chain. "
                                  "Checkpoint at update 288, not the released update 640",
                    "budget": "2 designs per chain (K = 2), rewrite temperatures up to 0.5",
                },
            )
        )
        out.append(
            result(
                f"{B}-result-{short}-{data_slug}",
                f"BF16 path minus reference sampler, S@D on {row} (HyInv report)",
                eval_id,
                cell["printed"],
                cell["value"],
                slug,
                locator,
                uncertainty=interval(
                    cell["lower"], cell["upper"],
                    "95% interval over CATH topology clusters. The report's own pass rule is whether "
                    "the lower end is at or above the -0.002 margin fixed before the check; for this "
                    f"row the printed verdict is '{cell['lower_end_above_margin']}'.",
                ),
                coverage={
                    "scored": int(cell["targets"]),
                    "eligible": int(cell["targets"]),
                    "unit": "chains",
                    "note": f"{cell['clusters']} CATH topology clusters.",
                },
                qualifier_extra=f"the report's printed verdict on whether the lower interval end is "
                                f"at or above the fixed -0.002 margin is "
                                f"'{cell['lower_end_above_margin']}'",
            )
        )


# Appendix D.3: HyInv above the ProteinMPNN temperature curve at HyInv's diversity.
PROTEINMPNN_CURVE = {
    "CATH4.3 test": ("+0.0146 [+0.0058, +0.0242]", "+0.0146", "+0.0058", "+0.0242"),
    "RecentPDB": ("+0.0187 [+0.0078, +0.0302]", "+0.0187", "+0.0078", "+0.0302"),
}
# Section 5.4: reinforcement learning at fixed development diversity.
RL_LEVELS = {
    f"{B}-config-hyinv-plain-sampling-supervised": (
        "supervised", "0.839", "the supervised checkpoint before reinforcement learning"),
    f"{B}-config-hyinv-plain-sampling-update640": (
        "update-640", "0.852", "the released update-640 checkpoint"),
}


def equal_diversity_prose(out):
    """The equal-diversity values printed in Appendix D.3 and Section 5.4."""
    slug = "protocol-sctm-fixed-diversity-vs-proteinmpnn-curve"
    protocol_id = f"{B}-{slug}"
    short = "sctm-fd-vs-proteinmpnn-curve"
    for panel, (printed, value, lower, upper) in PROTEINMPNN_CURVE.items():
        panel_slug, data_id = PANEL_SLUG[panel]
        eval_id = f"{B}-eval-{short}-hyinv-{panel_slug}"
        locator = (f"Appendix D.3 'scTM against diversity', sentence giving the reading on {panel} "
                   f"({page('proteinmpnn_curve')})")
        out.append(
            evaluation(
                eval_id,
                f"HyInv above the ProteinMPNN curve at HyInv's diversity on {panel} (HyInv report)",
                HYINV_DEFAULT,
                protocol_id,
                data_id,
                panel,
                locator,
                extra_comparison={
                    "adaptation": "ProteinMPNN is read from the quadratic fit through its three "
                                  "temperatures at the diversity HyInv samples at, so this is the "
                                  "report's one equal-diversity comparison against a baseline. Two of "
                                  "the three ProteinMPNN temperatures were generated for this report",
                },
            )
        )
        out.append(
            result(
                f"{B}-result-{short}-hyinv-{panel_slug}",
                f"HyInv minus the ProteinMPNN curve at HyInv's diversity on {panel} (HyInv report)",
                eval_id,
                printed,
                value,
                slug,
                locator,
                uncertainty=interval(lower, upper, "95% intervals over clusters."),
                qualifier_extra="read at the diversity of the HyInv default setting on this panel",
            )
        )
    level_slug = "protocol-sctm-fixed-diversity-esmfold2"
    for system_id, (name, value, description) in RL_LEVELS.items():
        eval_id = f"{B}-eval-sctm-fd-{name}-cath43-validation"
        locator = ("Section 5.4 'Reinforcement learning', sentence 'RL raises scTM at fixed "
                   "diversity from 0.839 to 0.852 with plain sampling' "
                   f"({page('rl_ablation')})")
        out.append(
            evaluation(
                eval_id,
                f"HyInv {description} at development diversity 0.30 (HyInv report)",
                system_id,
                f"{B}-{level_slug}",
                f"{B}-data-cath43-validation",
                "Development",
                locator,
                extra_comparison={
                    "adaptation": "Plain single-temperature sampling, read from the "
                                  "scTM-against-diversity curve at development diversity 0.30",
                    "budget": "Development read-out; the report does not state K for this sentence",
                },
            )
        )
        out.append(
            result(
                f"{B}-result-sctm-fd-{name}-cath43-validation",
                f"HyInv {description}: scTM at development diversity 0.30 (HyInv report)",
                eval_id,
                value,
                value,
                level_slug,
                locator,
                qualifier_extra=f"the checkpoint is {description}",
            )
        )
    gain_slug = "protocol-sctm-fixed-diversity-gain-vs-supervised-checkpoint"
    eval_id = f"{B}-eval-sctm-fd-gain-vs-supervised-hyinv-cath43-validation"
    locator = ("Section 5.4 'Reinforcement learning', parenthesis '(+0.0133, Figure 8a)' "
               f"({page('rl_ablation')})")
    out.append(
        evaluation(
            eval_id,
            "HyInv update 640 over the supervised checkpoint at development diversity 0.30 "
            "(HyInv report)",
            f"{B}-config-hyinv-plain-sampling-update640",
            f"{B}-{gain_slug}",
            f"{B}-data-cath43-validation",
            "Development",
            locator,
            extra_comparison={
                "adaptation": "Both checkpoints read from their own curves at development diversity "
                              "0.30 with plain sampling; the difference is of the two fitted values",
                "budget": "Development read-out; the report does not state K for this sentence",
            },
        )
    )
    out.append(
        result(
            f"{B}-result-sctm-fd-gain-vs-supervised-hyinv-cath43-validation",
            "HyInv update 640 minus the supervised checkpoint: scTM at development diversity 0.30 "
            "(HyInv report)",
            eval_id,
            "+0.0133",
            "+0.0133",
            gain_slug,
            locator,
            limitations=["Printed as a parenthesis in Section 5.4 beside the two levels 0.839 and "
                         "0.852, which are printed to three decimal places; the four-decimal "
                         "difference is the authors' own figure and is not the difference of the two "
                         "printed levels."],
        )
    )


TABLE1_SYSTEMS = {
    "ProteinMPNN": (f"{B}-config-proteinmpnn", "proteinmpnn"),
    "ProteinZero V2": (f"{B}-config-proteinzero-v2-esm2", "proteinzero-v2-esm2"),
    "HyInv, FP32 reference sampler": (
        f"{B}-config-hyinv-reference-sampler-timing", "hyinv-reference-sampler"),
    "HyInv, exact FP32 path": (f"{B}-config-hyinv-exact-fp32-timing", "hyinv-exact-fp32"),
    "HyInv (BF16)": (f"{B}-config-hyinv-bf16-timing", "hyinv-bf16"),
}
TABLE1_REQUESTS = [
    ("ms_148", "128 designs (ms), 148 res.", "millisecond",
     "128 designs for a 148-residue backbone"),
    ("ms_402", "128 designs (ms), 402 res.", "millisecond",
     "128 designs for a 402-residue backbone"),
    ("s_10000", "10,000 designs (s)", "second",
     "a library of 10,000 designs for a 250-residue backbone"),
]
# Figure 4a holds the eight systems Table 1 leaves out, all for the 402-residue request.
FIGURE4A_ONLY = {
    "CMLM": "cmlm",
    "ProteinZero V2 (ESM1)": "proteinzero-v2-esm1",
    "PiFold": "pifold",
    "ProteinMPNN (low-noise, grouped)": "proteinmpnn-low-noise-grouped",
    "ProteinMPNN grouped": "proteinmpnn-grouped",
    "LM-Design 650M": "lm-design-650m",
    "LigandMPNN": "ligandmpnn",
    "DPLM-2 3B": "dplm-2-3b",
}
UNIT_NAME = {"millisecond": "ms", "second": "s"}


def latency(parsed, out):
    """Table 1 and the eight systems Figure 4a adds, plus Table 1's speed-up column."""
    slug = "protocol-design-latency-h20"
    protocol_id = f"{B}-{slug}"
    data_id = f"{B}-data-latency-backbones"
    created = set()

    def latency_evaluation(system_id, system_slug, locator):
        eval_id = f"{B}-eval-design-latency-{system_slug}"
        if eval_id in created:
            return eval_id
        created.add(eval_id)
        out.append(
            evaluation(
                eval_id,
                f"Latency of a design request for {system_slug} on one NVIDIA H20 (HyInv report)",
                system_id,
                protocol_id,
                data_id,
                "Timing",
                locator,
                extra_comparison={
                    "population": "One backbone per request size: 148 and 402 residues for the "
                                  "128-design columns and 250 residues for the 10,000-design column; "
                                  "no identifiers are printed",
                    "split": "timing input",
                    "adaptation": "Each system runs its own released implementation at its published "
                                  "setting; HyInv's rows use the supervised-stage weights and a "
                                  "rewrite temperature of 0.23",
                    "budget": "128 candidates per request, maximum candidate batch 32 (the "
                              "10,000-design column is one library request)",
                },
            )
        )
        return eval_id

    for row, cells in parsed["table1"].items():
        system_id, system_slug = TABLE1_SYSTEMS[row]
        for key, column, unit, description in TABLE1_REQUESTS:
            locator = f"Table 1, row '{row}', column '{column}' ({page('table1')})"
            eval_id = latency_evaluation(system_id, system_slug, locator)
            printed = f"{cells[key]} {UNIT_NAME[unit]}"
            out.append(
                result(
                    f"{B}-result-design-latency-{system_slug}-{key.replace('_', '-')}",
                    f"{row}: time to design {description} (HyInv report)",
                    eval_id,
                    printed,
                    cells[key].replace(",", ""),
                    slug,
                    locator,
                    unit_detail=f"Printed as '{printed}'; the request is {description}",
                    qualifier_extra=f"the request is {description}",
                )
            )
    for row, system_slug in FIGURE4A_ONLY.items():
        cell = parsed["figure4a"][row]
        system_id = SYSTEMS[row][0]
        locator = f"Figure 4a, bar '{row}', printed label ({page('figure4a')})"
        eval_id = latency_evaluation(system_id, system_slug, locator)
        printed = f"{cell['value']} {cell['unit']}"
        out.append(
            result(
                f"{B}-result-design-latency-{system_slug}-ms-402",
                f"{row}: time to design 128 designs for a 402-residue backbone (HyInv report)",
                eval_id,
                printed,
                cell["value"].replace(",", ""),
                slug,
                locator,
                unit_detail=f"Printed as '{printed}' beside the bar; the request is 128 designs for a "
                            "402-residue backbone",
                qualifier_extra="the request is 128 designs for a 402-residue backbone",
                limitations=["Printed as a bar label in Figure 4a rather than in a numbered table. "
                             "Table 1 lists only five systems, so this is the only printed latency "
                             "for this one.",
                             "Appendix F states the baselines ran as released, unbatched where their "
                             "adapter handles one structure per call."],
            )
        )
        if cell["unit"] != "ms":
            out[-1]["attributes"]["unit"] = "second"

    speed_slug = "protocol-design-speedup-vs-proteinmpnn-h20"
    for row, cells in parsed["table1"].items():
        if "speedup" not in cells:
            continue
        system_id, system_slug = TABLE1_SYSTEMS[row]
        eval_id = f"{B}-eval-design-speedup-{system_slug}"
        locator = f"Table 1, row '{row}', column 'Speed-up vs ProteinMPNN' ({page('table1')})"
        out.append(
            evaluation(
                eval_id,
                f"Speed-up of {system_slug} over ProteinMPNN on one NVIDIA H20 (HyInv report)",
                system_id,
                f"{B}-{speed_slug}",
                data_id,
                "Timing",
                locator,
                extra_comparison={
                    "population": "One backbone per request size; no identifiers are printed",
                    "split": "timing input",
                    "adaptation": "Ratio against ProteinMPNN's released implementation under the "
                                  "report's timing protocol, not against an equally optimised "
                                  "baseline",
                    "budget": "128 candidates per request, maximum candidate batch 32",
                },
            )
        )
        out.append(
            result(
                f"{B}-result-design-speedup-{system_slug}",
                f"{row}: speed-up over ProteinMPNN (HyInv report)",
                eval_id,
                cells["speedup"],
                cells["speedup"].rstrip("×"),
                speed_slug,
                locator,
                unit_detail=f"Printed as '{cells['speedup']}'; a ratio of ProteinMPNN's time to this "
                            "system's time",
            )
        )


DE_NOVO_YIELD = {
    "HyInv": (HYINV_DEFAULT, "hyinv", "0.68", "0.38"),
    "ProteinMPNN": (f"{B}-config-proteinmpnn", "proteinmpnn", "0.47", "0.05"),
    "ProteinZero V2": (f"{B}-config-proteinzero-v2-esm2", "proteinzero-v2-esm2", "0.45", "0.11"),
}


def de_novo(out):
    """Section 6: novel-and-foldable designs per de novo backbone, both readings."""
    slug = "protocol-novel-and-foldable-yield"
    protocol_id = f"{B}-{slug}"
    data_id = f"{B}-data-de-novo-backbones"
    locator = ("Section 6 'De novo backbones', sentence '0.68 unfiltered and 0.38 filtered per "
               "backbone, against 0.47 and 0.05 for ProteinMPNN and 0.45 and 0.11 for ProteinZero "
               f"V2' ({page('de_novo_yield')})")
    for row, (system_id, system_slug, unfiltered, filtered) in DE_NOVO_YIELD.items():
        eval_id = f"{B}-eval-novel-foldable-{system_slug}-de-novo"
        out.append(
            evaluation(
                eval_id,
                f"{row}: novel and foldable designs per de novo backbone at matched diversity "
                "(HyInv report)",
                system_id,
                protocol_id,
                data_id,
                "DeNovo",
                locator,
                extra_comparison={
                    "population": "74 de novo backbones in 58 clusters of 30% sequence identity, "
                                  "none with a hit that passes the report's homology rule; 28 have "
                                  "partial hits below the coverage limit (Table 10)",
                    "split": "application panel",
                    "adaptation": "HyInv runs its default setting. ProteinMPNN and ProteinZero V2 are "
                                  "interpolated at the HyInv diversity from their temperature grids, "
                                  "without extrapolating by more than 0.05, so the comparison is at "
                                  "matched diversity",
                    "budget": "4 designs per backbone",
                },
            )
        )
        for reading, value in [("unfiltered", unfiltered), ("composition-filtered", filtered)]:
            out.append(
                result(
                    f"{B}-result-novel-foldable-{system_slug}-{reading}",
                    f"{row}: novel and foldable designs per de novo backbone, {reading} reading "
                    "(HyInv report)",
                    eval_id,
                    value,
                    value,
                    slug,
                    locator,
                    unit_detail="Designs per backbone, of 4 designs made per backbone",
                    qualifier_extra=(
                        "the unfiltered reading, over all designs"
                        if reading == "unfiltered" else
                        "the composition-filtered reading: sequence entropy at least 3.5 bits, "
                        "hydrophobic fraction (AVILMFWY) 0.25 to 0.55, longest homopolymer run at "
                        "most 6"
                    ),
                    coverage={
                        "scored": 74, "eligible": 74, "unit": "backbones",
                        "note": "58 clusters of 30% sequence identity; 4 designs per backbone.",
                    },
                )
            )


def evidence(parsed):
    PAGES.clear()
    PAGES.update(parsed["pages"])
    out = []
    quality(parsed, out)
    differences(parsed, out)
    sampler_gain(parsed, out)
    numerics_check(parsed, out)
    equal_diversity_prose(out)
    latency(parsed, out)
    de_novo(out)
    return out
