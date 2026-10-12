# Review: lit-rna-20261011-rnagym, 2026-10-12

Reviewer: Claude review agent `reviewer-ro-1`, independent of the extractor `lit-rna-otheromics`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

Excerpts of `reviewer-ro-1`'s report that concern this batch, unedited.

Reviewer: Claude review agent (reviewer-ro-1), independent of the collector lit-rna-otheromics; no human review claimed.
Date: 2026-10-12. Worktree reviewed: /Users/timrichardson/Documents/projects/personal/blog/rewire-benchmark-data-lit-rna-otheromics (batch folders treated as the source of truth; no record was edited and nothing was committed).

- `data/omics/lit-rna-20261011-rnagym` (64 results): approved with corrections (G1).

No printed value, numeric value, uncertainty value or locator is wrong in any of the three batches. The corrections mark results whose source is internally inconsistent, fix one wrong descriptive field, and tighten wording.

None of the three batches proposes a use-case judgement or summary text, and no existing use case covers RNA language models, RNA fitness or RNA 3D structure. There is no summary text or use-case field change to approve.

## Corrections

All corrections apply to `batch.jsonl` before `records -- add`, so no `records -- change` or `metadata-correction-*` claim is needed. Status `disputed` with `attributes.source_warnings` follows the store's precedent for results the source contradicts (for example the ctdnameth, brca and alphagenome-2026 results). I did not use source-level `evidence_concerns` because the build then blocks comparison for every result citing that source: all 216 rna3d results or all 1190 rnalm-zeroshot results, when the problem is confined to a few cells.

### lit-rna-20261011-rnagym

G1. Scoring convention stated for models it does not cover. The README's 'Scoring convention' section describes masked language models only. Evo 1, Evo 1.5, Evo 2 and GenSLM are autoregressive and Orthrus is contrastive, yet their configurations carry the masked-marginal text. In `lit-rna-20261011-rnagym-config-evo-1-rnagym-v0-1-1`, `-config-evo-1-5-rnagym-v0-1-1`, `-config-evo-2-7b-rnagym-v0-1-1`, `-config-evo-2-40b-rnagym-v0-1-1`, `-config-genslm-rnagym-v0-1-1` and `-config-orthrus-rnagym-v0-1-1`, set `attributes.parameters` to: "Zero-shot. The leaderboard README states the scoring convention for masked language models only (masked-marginal log-likelihood ratio, 'Scoring convention'); the convention used for this model is not stated there." Leave the masked language model configurations unchanged.

### Review fields to apply

After C1 to D4, set `status` to `source_checked` on every other record in the three batches and fill each result's `review` with the following. Keep `artifact_sha256` and `retrieval_url` as they are, because they match what I checked.

- `method`: ["source-hash-verification", "deterministic-table-parse", "independent-cell-check"]. For rna3d results located in Supplementary Tables S6, S7 and S15, use ["source-hash-verification", "pdf-text-parse", "independent-cell-check"].
- `reviewer`: ["claude"]
- `reviewer_note`: "Claude review agent reviewer-ro-1, independent of the extractor lit-rna-otheromics; no human review claimed"
- `date`: "2026-10-12"
- `method_note`:
  - rnalm-zeroshot: "Re-fetched the Europe PMC supplementary archive; the .docx inside matched its SHA-256. An independent w:tc parse of Supplementary Tables 4-11 matched all 1190 printed values, numeric values, standard deviations and locators; 48 cells were also checked by hand against a textutil rendering."
  - rnagym: "Re-fetched README, CSVs and LICENSE at commit 2828cf9 and matched their SHA-256. An independent Markdown table parse matched all 64 printed and numeric values and locators; all 64 were also read against the rendered table."
  - rna3d: "Re-fetched the PMC XML and the supplementary PDF and matched their SHA-256. An independent parse of Tables 2-5 and Supplementary Tables S6, S7 and S15 (pdftotext -layout and -raw) matched all 216 printed and numeric values and locators; 42 cells were also checked by hand. Success rates in S6-S7 were recomputed from S2-S5 as a consistency check, not as a derivation."
- `note`: keep the extraction note and append "Independent review 2026-10-12: value, locator, metric, unit, direction and linked configuration and protocol checked." For the disputed results, also append "Disputed: see source_warnings."

Then write each batch's `review.json` and the dated review in `docs/reviews/`, and run `npm test`, `npm run typecheck` and `npm run build`.

3. rnagym. Confirmed. The CSV key is "RNAErnie", and the repository root README at the same commit lists "RNAErnie | Genomic Language Model | Wang et al. ... Nature Machine Intelligence, 2024". ERNIE-RNA does not appear in the repository README. The link to `gfm2-20261011-you2026-model-rnaernie` is correct.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store. The review fields were set by `finalise` in `extract/lib.py`.

1. G1: the Evo 1, Evo 1.5, Evo 2 7B, Evo 2 40B, GenSLM and Orthrus configurations carry the reviewer's `parameters` text; the masked language model configurations are unchanged.
2. Review fields: every record is `source_checked`; each result carries the reviewer's review block, with the extraction description kept in `note`.
3. Order: added after lit-rna-20261011-rnalm-zeroshot, whose AIDO.RNA and RiNALMo family records it links to.

## Records after correction

- benchmark: 1
- configuration: 16
- dataset: 4
- evaluation: 64
- model: 3
- protocol: 4
- result: 64
- source: 1

Status: source_checked 157.
