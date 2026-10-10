# Review: issue #88a functional descriptions, 2026-10-10

Reviewer: a separate Claude review agent, independent of the extractor. No human review is claimed.

Verdict: approved with corrections. 43 of the 54 descriptions were supported as written. I corrected 11 in place, replaced two new sources with existing store records, set licences on 13 sources and marked all 94 batch records `source_checked`. One test needs a one-line fix before the batch is added (see "Checks run").

## 1. Scope of the diff

Compared `data/entities/models.jsonl` and `pipelines.jsonl` with origin/main record by record.

- Exactly 54 records differ: 44 models and 10 pipelines. The 11th pipeline in scope, `dilated-resnet`, is unchanged.
- Models changed only `description` and, for 34 of them, `source_ids`. Pipelines changed only `description`, `source_ids` and `attributes.source_locator`. No other field changed and record order is unchanged.
- Every claim's `previous_value` equals the origin/main description exactly, and every claim's `value` equals the record's current description.

## 2. Descriptions against their sources

I re-downloaded all 42 new source artifacts and read every description against the cited text: the abstract, the ProteinGym README row, the ProteinGym benchmark CSV header (re-downloaded; matches its pin), or the cited full-text section. For the existing sources (MIMIC HTML, MSAlign PDF, FramePool XML, Jores PDF, RhoMax XML) I checked the collector's saved copies against the store pins (all match) and read the cited passages.

Corrected (old wording in brackets):

| Record | Problem | Change |
| --- | --- | --- |
| `uc20260930-model-xtrimopglm` | Called a "protein language model of 100 billion parameters", but the record's locator is the `xTrimoPGLM-1B-MLM` column and ProteinGym scores seven checkpoints from 1B to 100B-int4 | "Family of protein language models, scaled up to 100 billion parameters ...; ProteinGym scores several sizes" |
| `uc20260930-model-tranception` | Said it "retrieves homologous sequences at inference", but the locator is the `Tranception S no retrieval` column | "can retrieve ...; ProteinGym scores it with and without retrieval" |
| `uc20260930-model-aido-protein-rag` | The scored column is `AIDO Protein-RAG (16B)`. The cited RAG paper describes a model fine-tuned from a 3B masked language model and releases 3B weights; the Hugging Face card for the 16B model says it builds on a 16B base model and adds alignment and structure data. The old text named no size, which is right, but omitted the inputs ProteinGym lists | Added the README row (AIDO, MSA & Structure) as a source and the input clause; still no size |
| `mimic-2026-mrnabench-method-nt-v2` | "one of a family ... pretrained on 3,202 human genomes and 850 genomes" read as the evaluated model's training data | Parameter range and genomes now describe the family in a parenthesis |
| `mimic-2026-mrnabench-method-rinalmo` | "650-million-parameter" | Removed |
| `mimic-2026-mrnabench-method-aido-rna` | "1.6-billion-parameter" | Removed |
| `mimic-2026-mrnabench-method-evo2` | "with 7B and 40B parameters" | Removed |
| `uc20260930-model-framepool` | "a proxy for translation rate" | "translation efficiency", the source's term |
| `uc20260930-model-esm-1b` | "Transformer protein language model"; the abstract does not name the architecture | "Deep contextual protein language model", the abstract's wording |
| `uc20260930-model-protgpt2` | "Transformer language model"; the abstract cites Transformer progress as motivation but does not state the architecture | "Deep unsupervised language model", from the title |
| `uc20260930-model-progen2` | "trained on over a billion protein sequences" | "trained on sequence datasets drawn from over a billion proteins", the abstract's wording |

The three parameter counts were removed because MIMIC Table S11 and the records do not identify the checkpoint, and the mRNABench full text shows the risk: Table 2 reports "best model per model family", and Appendix D lists several sizes per family (for example `aido-rna-650m`, `aido-rna-1b600m` and CDS-adapted variants). Which size MIMIC quoted can be read from mRNABench Appendix D; until then the descriptions stay at family level.

Supported as written: the other 43. Notes on the judgement calls the collector flagged:

- AIDO Protein-RAG: see the table. Agree with naming no checkpoint.
- ESCOTT: agree. ProteinGym lists ESCOTT with "MSA & Structure" under the PRESCOTT reference, and the PRESCOTT abstract separates sequence and structure scoring from the allele-frequency step. The description attributes allele frequencies to PRESCOTT, not to the scored ESCOTT column.
- UniRep evotuned: agree. The CSV column is `Unirep evotuned` and the README row reads "Single sequence (MSA for evo-tuning)". The UniRep abstract supports the base representation.
- NT-v2 at family level: agree with the approach; reworded as above.

The MSAlign descriptions (FLARE, JESTR, Emb-Cos, MIST, MVP, DeepSets) match Section 5.1 and Tables 1 and 3, including which methods need the target's formula. Optimus, FramePool, Jores and RhoMax match their full texts. VESPAl matches the VESPA full text ("using only conservation probabilities and BLOSUM62"), and S2F, S2F-MSA and S3F-MSA match the S3F full text (ESM-2-650M features; EVE ensembles by summed z-scores in Section 4.1).

## 3. Sources

Hashes: 32 of 42 re-downloads matched their pins byte for byte. The other 10 (mif, orthrus, protgpt2, protssn, rinalmo, siterm, unirep, venusrem, vespa, wavenet) are Europe PMC REST search responses whose fresh bytes differ only in JSON key order. The collector's saved copies match the pins and parse to the same content as my downloads. I added a `hash_scope` note to all 31 Europe PMC search sources left in the batch saying the hash describes one retrieval of a response that is not byte-stable, and that the title and abstract are the evidence.

Identity: each source names the original paper (title, DOI or arXiv identifier, year) and its abstract or section supports what cites it. The S3F HTML and VESPA full text are the papers themselves.

Duplicates: two new sources repeated existing store records, which collection.md asks us to avoid. I replaced them in records, claims and changes.md and removed them from the batch:

- `qa-descriptions-20261010-source-proteingym-readme` is the same artifact URL and SHA-256 as `run-doc-proteingym-readme-md-144fe22b` (source_checked).
- `qa-descriptions-20261010-source-mrnabench` (preprint abstract) is covered by `expansion-p3-mrnabench-2025`, the Europe PMC full text PMC12265608, CC BY 4.0. I re-downloaded it and it matches its pin.

Two remaining overlaps are kept on purpose: `mulan` (the existing full-text record `evidence-expansion-p2-mulan-2025-771a9a26ebda` no longer reproduces its pin; today's download hashes to 2ed7f38a...) and `ernie-rna` (the existing `ernie-rna-2025` is only `discovered`).

Licences: the collector left 21 of the 40 as unreported. I set 13 from primary statements and left 9 unreported:

- arXiv abstract pages: CC-BY-4.0 for DNABERT-2, Protriever and Tranception; the arXiv non-exclusive licence for HyenaDNA, PoET, RITA, S3F and the S3F HTML.
- bioRxiv and medRxiv API licence fields: CC-BY-NC-ND-4.0 for ESCOTT (PRESCOTT), ProSST and TranceptEVE; "All rights reserved (bioRxiv licence 'cc_no')" for SaProt.
- The remaining journal records (CARP, DeepSequence, EVE, MIF, Orthrus, ProGen2, SiteRM, UniRep, xTrimoPGLM) give no licence in Europe PMC and stay unreported.
- The Europe PMC licence field carries no version (for example "cc by"). The batch records it as 4.0, the store's convention; bioRxiv and these journals use 4.0.

Archive: agree that nothing is archived. Each artifact is a few kilobytes of public, re-retrievable text, and the fix rests on the abstract text, not on bytes that could change. The `hash_scope` notes say why the Europe PMC hashes cannot be re-verified byte for byte.

## 4. dilated-resnet

I do not agree that no source exists. changes.md says the mRNABench full text is not available through Europe PMC, but the store already pins it (`expansion-p3-mrnabench-2025`, PMC12265608, CC BY 4.0). Its baselines section says: "we include an ab-initio supervised dilated CNN comparison. This model is trained from scratch on the train split in evaluations. This supervised CNN uses a DilatedResNet architecture consiting of either three or four DilatedResNetBlocks."

I left the record unchanged, because adding it would be a 55th change with its own claim. Suggested text, citing `coverage-source-mimic-2026-v1-html` and `expansion-p3-mrnabench-2025`:

> Supervised dilated convolutional baseline from mRNABench, built from three or four DilatedResNet blocks and trained from scratch on each task's training split, with task scores quoted from prior work in MIMIC Table S11.

## 5. Records marked

All 54 claims and 40 sources are `source_checked`. Each has a review block: method, reviewer `claude`, reviewer note, date and a note with the result. Sources also carry `artifact_sha256` and `retrieval_url`. For claims, the collector's note is kept and the review result appended.

## Checks run

In a scratch copy of origin/main, I ran `addBatch` on `batch.jsonl` (94 records), copied in the edited entity files and recorded the 54 changes. Then `records check` reported "42623 records match their provenance", and `tsc --noEmit` passed. `vitest run` passed 499 of 500 tests. The one failure is `tests/omics-evidence-completion.test.ts`, "keeps hosted service restrictions distinct from the local model and logs identity corrections". It takes the first record whose id starts with `metadata-correction-` and expects `previous_value` "family", so any new metadata-correction claim that sorts first breaks it. The fix is to look up `metadata-correction-6ff08f49b3b45f847dd6` by id. I did not edit the test. I did not run the full data build.

In the worktree, the provenance hashes of the 54 edited records stay stale until `records -- change` is run, as changes.md says.

## Limitations

- An automated review by a Claude agent, not human scientific review.
- Descriptions were checked against abstracts and cited sections, not whole papers, except where the full text was the cited source.
- The checkpoints quoted in MIMIC Table S11 are not identified; mRNABench Appendix D would identify them.
