# Re-review: Feng variant-effect judgements after the per-group evaluations, 2026-10-14

Reviewer: an independent Claude (Opus 5.5) review agent for PR #157, separate from the agent that extracted the per-group results (#142). No human review is claimed. Nothing was executed.

Batch review: [../2026-10-14-feng-remaining-tables.md](../2026-10-14-feng-remaining-tables.md).

## Why

Batch `feng-dna-fm-20261014` adds Supplementary Data 4 of Feng et al. 2025: the AUC on each of the three held-out chromosome groups behind every Table 5 and Table 6 mean. They are held on 59 new per-group evaluations (aggregation "per outer chromosome test group, not averaged") on the same configurations, protocols and datasets as the stored mean evaluations. Those protocols are mapped as proxy in five reviewed judgements. A new evaluation on a mapped protocol is shown without a new judgement, so each judgement was reviewed again.

| Claim | Use case | Protocol | New per-group evaluations |
| --- | --- | --- | --- |
| `use-case-mapping-amp-20261007-feng-pathogenic-common-variant` | `use-case-rare-disease-candidate-ranking` | `amp-feng-20261007-protocol-pathogenic-common-variant-classification` | 11 |
| `use-case-mapping-amp-20261007-feng-qtl-eqtl` | `use-case-regulatory-variant-gene-follow-up` | `amp-feng-20261007-protocol-qtl-eqtl` | 12 |
| `use-case-mapping-amp-20261007-feng-qtl-sqtl` | `use-case-regulatory-variant-gene-follow-up` | `amp-feng-20261007-protocol-qtl-sqtl` | 12 |
| `use-case-mapping-amp-20261007-feng-qtl-paqtl` | `use-case-regulatory-variant-gene-follow-up` | `amp-feng-20261007-protocol-qtl-paqtl` | 12 |
| `use-case-mapping-amp-20261007-feng-qtl-ipaqtl` | `use-case-regulatory-variant-gene-follow-up` | `amp-feng-20261007-protocol-qtl-ipaqtl` | 12 |

## What was checked

- The reviewed evaluations of each judgement are unchanged: same records, same results, same comparison. The per-group values are not on them.
- Endpoint and relevance against the new values. Per-group AUCs measure the same endpoint on a third of the variants each. They do not bring the task closer to ranking a patient's candidate variants or to choosing variants, elements and genes for perturbation. Proxy still holds for all five.
- Spread within a configuration, from Supplementary Data 4:

  | Protocol | Smallest and largest within-configuration range | Top configuration in each group |
  | --- | --- | --- |
  | Pathogenic vs common | 0.0014 to 0.057 (Enformer hidden states 0.6575 to 0.7145) | NT-v2 in all three (0.7312, 0.7318, 0.7326) |
  | eQTL | 0.0066 to 0.0372 (GROVER 0.5683 to 0.6055) | AlphaGenome output tracks in all three; Enformer hidden states second in all three |
  | sQTL | 0.0085 to 0.0886 (Sei output tracks 0.5794 to 0.668) | AlphaGenome output tracks in all three |
  | paQTL | 0.003 to 0.1714 (AlphaGenome output tracks 0.6781 to 0.8495) | AlphaGenome output tracks in all three |
  | ipaQTL | 0.0211 to 0.1719 (Sei output tracks 0.5469 to 0.7188) | AlphaGenome output tracks in all three |

  The Supplementary Data 4 legend says "There are notable differences between different test sets for paQTL and ipaQTL." The values agree.

## Decision

All five judgements hold. No verdict changes. Three edits per claim, recorded with `npm run records -- change`:

1. `excluded_evaluations` lists the new per-group evaluations on the protocol, each with the reason: a per-group breakdown of the three-group mean already shown for that configuration, excluded so each configuration is compared once, at the aggregation the paper reports. The per-group evaluations stay in the catalogue and on their evaluation pages.
2. One limitation added, before the closing "no independent reproduction" line, giving the within-configuration range and the top configuration per group. The paQTL and ipaQTL limitations quote the legend and say that differences of a few hundredths between configuration means should be read with that spread in mind.
3. `revision` 1 to 2, `reason` and `review` updated. The review names this re-review and keeps the 2026-10-07 reviewer note.

The claims were then re-pinned with `npm run use-cases:repin -- docs/reviews/use-cases/feng-variant-effect-per-group-2026-10-14.md` and the five claim IDs. The use-case summaries for both use cases rest on the judgements' reviewed evaluations, which did not change, so they are not affected; neither summary quotes a Feng value.

## Gaps

- Per-group Cohen's d is not published.
- No reproduction and no human scientific review.
