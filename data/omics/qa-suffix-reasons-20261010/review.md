# Independent review of the QA fixes for #88 (b) and #89, 2026-10-10

Reviewer: a separate Claude review agent that did not make the fixes. No human review is claimed. Nothing was executed except the checks listed here.

## Verdict

Approved. The first change set, 33 lines, was approved with four wording fixes made in place. The follow-up of 18 records, made after this review, is approved as made (see Follow-up review below). The store now differs from origin/main (`78d9afc`) in 51 lines:

- the `description` of 37 methods and 11 models;
- the `source_ids` of one of those methods (DELFI);
- `attributes.reason` of 3 CNV judgement claims.

No other field and no other byte changed. All 51 metadata-correction claims have `previous_value` equal to origin/main exactly and `value` equal to the working tree.

The store cannot pass `npm run records -- check` until provenance records the change (see What remains for the integrator).

## How the check was done

1. Extracted `methods.jsonl`, `models.jsonl`, `claims.jsonl` and `sources.jsonl` from origin/main and compared them line by line with the working tree. For every changed line, I re-encoded the old field value, replaced it with the new one, and confirmed that the result equals the new line byte for byte.
2. For the 30 descriptions, I split the old text into the new sentence plus the removed tail and confirmed that the tail is a citation only. Then I matched every author and year in it against the record's `source_ids` by source ID, name and attributes.
3. Searched all method, model, pipeline and service descriptions with a looser pattern for trailing or inner citations, to find anything the fix missed.
4. For the 3 reasons, I read each claim's `endpoint` and `limitations` and every `evidence_concerns` entry on its `source_ids`, and checked each statement against them.
5. Compared each of the 33 correction claims with origin/main and the working tree, and validated `batch.jsonl` in memory with `recordSchema`, `validateVocabularies` and `validateAttributes`.

## #88 (b): description suffixes

All 30 changes remove only a trailing parenthetical citation and keep the sentence, ending it with a full stop. Each sentence still reads correctly on its own. Every cited author and year has a matching source in `source_ids`:

| Records | Cited | Source in `source_ids` |
| --- | --- | --- |
| 8 RNA fusion methods | Tamura et al. 2026 | `rna-fusion-20261009-source-tamura2026` |
| 16 somatic methods | Guille et al. 2025 | `somatic-20261009-source-guille2025` |
| MuTect, Mutect2 (also) | Wang et al. 2020 | `somatic-20261009-source-wang2020`, `-wang2020-tables` |
| 6 regulatory-variant models | Manzo et al. 2025 | `regulatory-variant-20261009-source-manzo2025` |
| Enformer (also) | Tang et al. 2025 | `regulatory-variant-20261009-source-tang2025` |

### The Sei record

The QA fix left "(Tang et al. 2025 Results)" in the middle of the Sei sentence. That is not acceptable. Issue #88 asks that the description say what the model does, with provenance kept elsewhere. A mid-sentence citation is the same problem the trailing suffix was, and it is easy to remove without changing meaning, because Tang et al. 2025 is already in `source_ids`. I reordered the sentence:

- Before review: "Supervised sequence model pretrained on 21,907 chromatin profiling datasets (Tang et al. 2025 Results), built from residual dilated convolutions."
- Now: "Supervised sequence model built from residual dilated convolutions and pretrained on 21,907 chromatin profiling datasets."

The facts are unchanged. The correction claim's `value` and `description` were updated to match; its `previous_value` remains the origin/main text.

### Not covered by this fix

The brief's pattern only matches suffixes naming a Table or Supplement. A looser search finds 18 more method and model descriptions with a trailing or inner author-year citation, for example:
- `rna-fusion-20261009-method-fusionseeker`: "(Lin et al. 2026 Methods)";
- `regulatory-variant-20261009-model-gpn`: "(Tang et al. 2025 Results)";
- `ctdnafrag-20261009-method-ichorcna`: "(Adalsteinsson et al. 2017)";
- `somatic-oncogenicity-20261009-method-cadd`: "(Rentzsch et al. 2019, Nucleic Acids Research 47:D886)". That text came from my own proposal in the splicing follow-up review and has the same problem.

The others are:
- `ctdnafrag-20261009-method-delfi`, `ctdnameth-20261009-method-houseman-cp`;
- `regulatory-variant-20261009-method-epimap`, `-method-epiraction`, `-model-trednet`;
- `rna-fusion-20261009-method-fusilli`, `-fusioncatcher`, `-jaffa`, `-longgf`;
- `somatic-20261009-method-neusomatic`, `-strelka`;
- three `egfrnsclc-20261009-model-*` records ending "(as used by Lin et al. 2025)".

These were outside the brief and the 33-line limit, so they were not changed in the first pass. The collector then fixed all 18; see Follow-up review.

## #89: CNV held reasons

All three new reasons are reader-facing and avoid the workflow language the issue lists. Every fact in them comes from the claim or its sources' `evidence_concerns`:

- **Both De La Vega reasons.** The CNVnator 1 to 5 kb conflict and the lowest-precision conflict are the concern on `cnv-20261009-source-delavega2025` (Results 3.1 paragraphs 3 and 5 against Supplemental Table 3 B9, C9, W11, W13). The concern adds that the prose may describe figures, which were not checked. The reasons do not repeat that hedge; "the Results text and Supplemental Table 3 disagree" is still accurate.
- **Coriell panel.** "The conflict is in the HG002 table, not in this panel table" is right: Supplemental Table 3 is the HG002 table, and the panel judgement rests on article Table 1 ("Precision only in Table 1"). "These precision values" matches its endpoint.
- **Nardone.** The depth and aligner statements are the concern on `cnv-20261009-source-nardone2025-table-s1`. The inGAP disagreement is the concern on `cnv-20261009-source-nardone2025`.

I made three wording fixes. They add no new claim:

1. Both De La Vega reasons: "1-5 kb" is now "1 to 5 kb", the reader-facing form #89 itself suggests.
2. Coriell panel: "it applies to the whole article" is now "it is recorded against the whole article". The concern is a property of the record, not a finding that the panel table is affected.
3. Nardone:
   - "25x with bwa-mem2 in Methods" is now "reads subsampled to 25x and aligned with bwa-mem2 for preliminary evaluations in Methods". The concern says "for preliminary evaluations", and dropping it made Methods sound definitive.
   - "5,000-9,999 bp" is now "5,000 to 9,999 bp".
   - The last sentence, "The table values are recorded, but they are not compared with other HG002 tables until this is resolved", is now "The table values are recorded as printed, but they are not shown until this is resolved". The reason opens "Not shown", and the judgement is held, so the old sentence described a different consequence (no automatic comparison) from the one the reader sees.

`changes.md` still shows the pre-review texts for these four records. `review_edits.py` in this folder reproduces my edits after `apply_fixes.py`.

The three claims stay `needs_review`, unpinned, with their earlier `reviewed_evaluations`, as before. Only the reason text changed.

## Correction claims (`batch.jsonl`)

- 33 claims, one per changed field, each with a single `subject` link to a distinct record.
- `field` is `description` for 30 claims and `attributes.reason` for 3, following the existing `attributes.entity_level` precedent.
- `previous_value` equals origin/main and `value` equals the working tree for all 33, after my edits.
- `source_ids` equals the subject's.
- I set them to `source_checked` with an independent review block.
- The batch passes `recordSchema`, the vocabulary check and the attribute check.

## Follow-up review: 18 more records (2026-10-10)

After this review, the collector edited the 18 records listed under 'Not covered by this fix', with `apply_fixes_18.py`, and appended 18 correction claims to `batch.jsonl` (51 in all). The follow-up section of `changes.md` lists them.

### Checks

- **The earlier 33 are unchanged.** Their 33 correction claims are the first 33 lines of `batch.jsonl` and reproduce the hash bound before (`7a56842d3cf48b2c3900af9e63b0cbe294e2be5cd833c0ccd99326a95d35f979`) byte for byte. Each of the 33 store lines equals origin/main with exactly the approved value substituted.
- **Only the stated fields changed.** On the 18 records, only `description` differs from origin/main, except `ctdnafrag-20261009-method-delfi`. That record also gains `amp-20261007-ctdna-fragmentomics-source` in `source_ids`, which is Cristiano et al., Nature 2019, the work the removed "(Cristiano et al. 2019)" cited. A character diff shows no other byte changed on any of the 18 lines.
- **The correction claims are right.** All 18 `previous_value` fields equal origin/main exactly, `value` equals the working tree, and `source_ids` equals the subject's.
- **Plain removals.** Ten records lose only a citation and keep every other word: ichorCNA, Houseman CP, EpiMap, FusionCatcher, FusionSeeker, JAFFA, LongGF, GPN, CADD and DELFI. EPIraction keeps "2025 preprint" in place of "bioRxiv 2025". For DELFI, "Defined in Hou et al. ref 45" also goes. It only said where Hou et al. took the definition from, which is now carried by the added source.
- **Reworded sentences.** I checked each against the linked configuration and evaluation records:

  | Record | Fact kept | Store support |
  | --- | --- | --- |
  | Fusilli | Developed by the authors of the study that evaluated it | Its only evaluations come from Lin et al. 2026, so "the comparison that evaluated it" is unambiguous |
  | TREDNet | From the group of the evaluating study's senior author | Its only evaluations come from Manzo et al. 2025. "Developed by the group" restates "from the group"; nothing is added |
  | NeuSomatic | Run in ensemble mode in one study | Two linked comparisons; only the Wang et al. 2020 configurations use the ensemble model (`NeuSomatic_v0.1.3_ensemble_DREAM3.pth`). Which study is now on the configuration records |
  | Strelka | Versions 2.7.1 and 2.9.2 | `somatic-20261009-config-wang2020-strelka` is v2.7.1 and `-guille2025-strelka` is 2.9.2 |
  | GPT-4o | Version 2024-05-13, through the Azure OpenAI API | Matches `egfrnsclc-20261009-config-lin2025-gpt-4o-basic` |
  | Llama 3.1 70B, Qwen 2.5 72B | Open-weight, served with Ollama | Unchanged facts; "in the evaluated runs" replaces "as used by Lin et al. 2025", the only study linked |

  Each keeps every fact of the old text and adds none.
- I set the 18 claims to `source_checked` with an independent review block. The 51-claim batch passes `recordSchema`, the vocabulary check and the attribute check.

Five cited works have no source record, so their citation now survives only in the correction claim's `previous_value`: Adalsteinsson 2017, Houseman 2012, Boix 2021, Nurtdinov and Guigó 2025, and Rentzsch 2019. That is acceptable for this fix, since adding them would need new retrieved sources. For CADD, the follow-up correction proposed in the splicing follow-up review adds `splicing-follow-up-20261009-source-riepe2021`, which cites Rentzsch et al. 2019, to its `source_ids`.

### Later follow-up for #88, not part of this change

Seven borderline method descriptions still carry author-year text and are left for a later #88 follow-up:
- `dna-pathogen-20261009-method-kraken`;
- `regulatory-variant-20261009-method-distance-to-tss`;
- `regulatory-variant-20261009-method-ep-dnase-correlation`;
- `regulatory-variant-20261009-method-residualbind`;
- three `ucc-research-method-abdelaal-*` records, which are also placeholder text.

## Checks run

- Store diff against origin/main: 51 changed lines (37 methods, 11 models, 3 claims), confined to the stated fields.
- `npm run typecheck`: exit 0.
- `npm run records -- check`: fails at `rna-fusion-20261009-method-arriba changed without a provenance entry`. This is expected: provenance was not updated, and this review was not to run `records -- change`.

## What remains for the integrator

1. Record the 51 edits:

   ```
   npm run records -- change data/omics/qa-suffix-reasons-20261010/review.md data/omics/qa-suffix-reasons-20261010 <the 51 subject IDs>
   ```

2. Add the 51 correction claims:

   ```
   npm run records -- add data/omics/qa-suffix-reasons-20261010/batch.jsonl data/omics/qa-suffix-reasons-20261010
   ```

3. Run `npm run records -- check` and `npm test`.

4. Take the 7 borderline descriptions listed under Follow-up review as a later follow-up for #88.
