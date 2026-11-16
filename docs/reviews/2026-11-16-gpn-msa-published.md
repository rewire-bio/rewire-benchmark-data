# GPN-MSA, published version: independent review

2026-11-16. Batch `data/omics/gpn-msa-published-20261116/`, the second item of
[rewire-bio/rewire-benchmark-data#226](https://github.com/rewire-bio/rewire-benchmark-data/issues/226).
Reviewed by a Claude (Opus 5) agent that did not extract the batch, against the extraction frozen
at `batch.jsonl` SHA-256 `d00df69afbdb0e148e158a51f8f9cb6dfe8903b590baf68a8d10bf6dc5ea5e5d`,
13 records. Not human scientific review. Nothing was reproduced: no model was run and no score
recomputed.

Receipt: `data/omics/gpn-msa-published-20261116/review.json`. Reviewer scripts and outputs:
`data/omics/gpn-msa-published-20261116/review/`.

The batch asks one question: does the peer-reviewed version print different numbers from the
bioRxiv v2 values the store already holds? The extractor answered no, and flagged that its own
answer was not independent. That flag was the right call and it is the reason this review exists.

**The answer stands, and it is now independent.** An OCR route the extractor could not find was
available, so the 136 published values were read by machine rather than by eye, written out before
any comparison, and then diffed three ways. All 136 cells agree. Two stored values remain
uncompared and that is recorded as a gap, not papered over.

Two stored records were changed. Two correction claims were added to the batch, which now holds 15
records. No stored value, metric, unit, direction or denominator was touched.

## Sources and hashes

All five artifacts were re-retrieved at 2026-11-16T00:48Z to 00:49Z.

| Record | Recorded SHA-256 | Refetched |
| --- | --- | --- |
| `source-nbt-2025` (article page) | `accc02ff43f84cf716d56a92b09664cb36506984162d0f5d45773db1c41c2d3f` | does not reproduce, by design |
| `source-extended-data-table-1-page` | `abe7bcaf55b0354a7f50f8d2cd91b47c16bc189cfa45b8f2ac0c1fb99dd6491f` | matches |
| `source-extended-data-table-1-image` | `b2673b8e14f8d0c4e12892600620ccd93c6de6f36a112473816057c9d7423387` | matches |
| `source-figure-2-page` | `d031178b99df61866b0a302fdfe35f37a18c4f3c3bdb31c5b232514dd7cbd5d6` | matches |
| `source-supplementary-information` | `75874bda760405cb98d3712e9319a94fb73838b4a412fd3ba340ddf3b7d6fcb4` | matches |

The article page refetched to `ece279575986ff0912e4de19bb39ecb55dd09a26ea5de0917112e5bea2b7d802`.
That is the behaviour its `hash_scope` already describes, and it is credible precisely because the
other four pages and files from the same two hosts, fetched in the same minute with the same
client, came back byte for byte identical. The passages the batch quotes were all found verbatim in
the refetched page. The pin is a retrieval stamp, not a content check, and the record says so.

The preprint was also re-downloaded, to check the batch's claims about it rather than take them on
trust. Its bytes do not reproduce the pinned
`10411077df1ae59614f9a9a9f85384103d54127ba67a9b3c469a4a2d6c33cee4` either; that too is already
recorded in its own `hash_scope`, which explains that bioRxiv rewrites per-download stamps. The
`pdftotext -layout` text layer is what the comparisons used.

### The preprint pin cannot be repaired by archiving bytes

Three separate downloads of the preprint were taken during this review. All three are 2,247,726
bytes. None hashes to the pinned value, and they do not even agree with each other: two gave
`688e3788e0555b0b1089f474c5cc7dfd22113fdaa168339c1b9f21490fa22646` and one gave
`d2d939c881b067174a1fbfad5c41b0d9c4a76c4f18979acfb04fafd2e9e7c758`. So the instability is not a
single stamp applied per download but a rotation between variants, which matters for what can be
done about it: archiving one copy would not let a later reader verify their own download against
it either.

The `pdftotext -layout` text layer of all three is byte-identical:

```
c6e95eb807550bb97aa2b8991c013f28fe11742006582c25818fcf90cad30c79
```

That is the reproducible check on this source, it is stable, and no record currently holds it. The
record's `hash_scope` already asserts in prose that a re-download gives "an identical pdftotext
-layout text layer" without ever naming the hash that would let anyone confirm it. Recording that
one value turns a prose assurance into a check. This review does not apply it: the source belongs
to `data/omics/gfm-guides-20261014-gpnmsa`, and cross-batch fixes to GPN-MSA records are being
sequenced elsewhere. See the ruling below.

## The comparison was made independent

This is the whole value of the batch, so it is worth being exact about what was and was not done.

The published ablation study is distributed as `41587_2024_2511_Tab1_ESM.jpg`, 1594 by 949 pixels,
with no text layer. The extractor read its 136 cells by eye and wrote them into a script while the
stored values were on screen. It said plainly that this is evidence and not verification, and that
no OCR tool was available because `tesseract` is not installed. That was true of `tesseract`, but
not of the machine: macOS ships the Vision framework, and `swift` and `swiftc` are present.

The review therefore built one (`review/ocr.swift`, 60 lines) around `VNRecognizeTextRequest` with
`recognitionLevel` set to accurate and `usesLanguageCorrection` set to false, which matters, since
language correction is exactly what would turn a digit into a plausible word. It was run over the
re-downloaded JPEG twice, at native size and at 2x. Each pass returned 136 numeric observations,
every single one at confidence 1.000, and the two passes agree on every value. The only difference
between them anywhere is the column header, read as "ClinVar" at 1x and "Clin Var" at 2x, which is
word segmentation and not a value.

`review/grid.py` then rebuilt the 17 by 8 grid from the observation geometry alone: bands by
vertical centre, order within a band by horizontal centre. It contains no stored value, and the
reading was written to `review/reviewer-reading-extended-data-table-1.tsv` before any comparison
was made.

Only then did `review/threeway.py` compare. It checks each cell against the stored record's
`printed_value`, against its `numeric_value`, and against both columns of the extractor's
`extract/comparison.tsv`, and it rebuilds the row-and-column mapping from the OCR labels rather
than trusting the extractor's. Result, in `review/threeway-result.txt`:

```
cells checked three ways: 136
problems: 0
```

The coverage was checked at the same time, independently of the extractor's count: 138 stored
results cite `gfm-guides-20261014-gpnmsa-source-biorxiv-v2`, all 138 appear in `comparison.tsv`,
and nothing appears in `comparison.tsv` that does not cite that source. So the batch's "136 of 138"
is exactly right.

### Why this is strong, and what it still is not

The stored 136 values were produced by a completely different channel: a `pdftotext -layout` parse
of the preprint PDF, by a different agent, in October. The reviewer's 136 values were produced by
OCR of a raster image from the publisher, in November. Two unrelated error-prone readings of two
separately typeset artifacts agree on all 136 cells, to the decimal place. A shared error would
have to be a coincidence 136 times over.

The stored side of that diff has since been confirmed independently of this review as well: the
extractor re-parsed preprint Supplementary Table 4 from a freshly downloaded copy, with all 17 row
labels asserted, and all 136 cells reproduce the stored `printed_value` exactly, thirteen months
after the original batch was made. So neither leg of the comparison now rests on a single reading.
The published side, the raster table, is the leg this review was written to establish, and that is
what the OCR pass does.

It is still a reading of printed numbers and not a reproduction of the study, and OCR is a
recognition step rather than a parse of a text layer. The claim has been reworded to say both
things, so that a later reader cannot mistake it for verification. In particular it now says
explicitly that the published Methods, which could in principle define the ablations differently,
are paywalled and were not retrieved; identical numbers are good evidence the settings did not
change, not proof.

The store has no review-method concept for OCR, and none of the existing ones is honest about it:
`transcription` and `rendered-source-visual-check` both mean "by eye", and `pdf-text-parse` and
`deterministic-table-parse` both mean a text layer that this artifact does not have. The records
use the nearest existing concepts and name the technique in full in every `method_note`, and
`vocab-proposal.ttl` proposes `optical-character-recognition` for the coordinator.

## The paywall and the two uncompared values

Rechecked from scratch rather than accepted:

- The refetched article page carries the abstract and then "This is a preview of subscription
  content, access via your institution". It has no Main and no Methods section.
- Europe PMC returns one record, PMID 39747647, with `isOpenAccess` N, `inPMC` N, `hasPDF` N, and
  "Subscription required" against its only full-text link.
- Unpaywall reports `oa_status` green with two locations, both `submittedVersion`: the bioRxiv PDF
  and PMC10592768, the NIH preprint pilot copy of the preprint.
- OpenAlex agrees. Its only `publishedVersion` locations are the paywalled DOI and two PubMed
  landing pages, neither of which carries the body.
- The string `TADBP` does not occur in the article page, the Extended Data Table 1 page or the
  Figure 2 page. It occurs once in the Supplementary Information, in the ProteinGym dataset list in
  Supplementary Table 3, with no AUROC beside it.

So `gfm-guides-20261014-gpnmsa-result-dms-tadbp-gpn-msa-auroc` (0.83) and
`...-esm-1b-auroc` (0.75) genuinely cannot be compared. In the preprint they sit in a Results
sentence on page 6: "GPN-MSA performs better than ESM-1b on some proteins (e.g., TADBP, for which
GPN-MSA AUROC is 0.83, while ESM-1b AUROC is 0.75)." The published counterpart of that sentence is
behind the paywall. This is a recorded gap and the batch is right not to claim otherwise.

## Rulings

### 1. Is "no values differ" supportable?

Yes, now that the reading is independent, and the claim has been reworded so it cannot be read as
more than it is.

The deciding artifacts are the two captions, which show the protocols did not change. Published
Extended Data Table 1: "Performance of three random seeds of each independent ablation on four
variant effect prediction metrics. ClinVar (AUROC): same setting as Fig. 2c. COSMIC (AUPRC): same
setting as Fig. 2e. OMIM (AUPRC): same setting as Fig. 2f. gnomAD (odds ratio): same approach as
Fig. 2g, including all variant types, but subsetting the rare variants to match the number of
common variants. Ablations are detailed in Methods." Preprint Supplementary Table 4 prints that
same sentence word for word, with "Figure 2a", "2b", "2c" and "2d" in place of the four panel
references.

### 2. The stored locator reading "Supplementary Table 4"

**An added locator note on the source record, not a correction claim on the results, and not 228
rewritten locators.**

228 stored GPN-MSA locators name "Supplementary Table 4". Every one of them is correct: they cite
`gfm-guides-20261014-gpnmsa-source-biorxiv-v2`, and in that artifact Supplementary Table 4 is the
ablation study. Nothing is wrong, so a correction claim on them would assert an error that does not
exist. The hazard is real but it is a different one: a reader who follows such a locator into the
journal version lands on the training hyperparameter table, because published Supplementary Table 4
is preprint Supplementary Table 5. Rewriting 228 locators to carry both numberings would rewrite a
large block of reviewed provenance and re-pin it, to fix a hazard that one sentence on the source
record fixes for all of them at once.

So the note went on the source record. Applied, with
`npm run records -- change docs/reviews/2026-11-16-gpn-msa-published.md`:

`gfm-guides-20261014-gpnmsa-source-biorxiv-v2`

- Limitation 1 replaced. It said the published Extended Data Table 1 "was not read, so the printed
  values here may differ from the journal version". That is now answered, and leaving it would
  invite a later reader to doubt 136 stored results that have been checked against the version of
  record. It now says they were read, that no cell differs, and that the two DMS TADBP values are
  the exception.
- Limitation 4 extended. It recorded the preprint caption's wrong panel pointers as an open
  oddity. The published caption settles it: the preprint caption was wrong and publication fixed
  it. Now cited.
- A limitation added, naming both numbering shifts and saying the locators were deliberately not
  rewritten.
- `companion_of` link added to `gpn-msa-published-20261116-source-nbt-2025`. The extractor pointed
  the published record at the preprint but could not add the reverse edge, which is the one a
  reader of the preprint needs.

The previous text is kept in claim
`metadata-correction-gpn-msa-preprint-source-limitations-20261116`.

### 3. Does the published version warrant a source record?

Yes, and the claims are the right and complete outcome.

It supplied no new measured value, which is exactly why it must not be attached to the 136 stored
results: writing the same numbers again under a second source, or adding the published source to
those results' `source_ids`, would put two records with the same number, the same system and the
same protocol into the graph from one piece of work, and downstream that reads as two independent
agreeing measurements. The extractor was right to refuse this and the review upholds it.

It does supply four things nothing else in the store has: the artifact the comparison rests on, the
four Figure 2 sample sizes the preprint never printed, the corrected panel pointers, and the table
renumbering. Those belong in the graph, and claims attached to the preprint source and the
benchmark are the right vehicle.

No `supersedes` link. The published version supersedes the preprint as a citation, but the preprint
is still the artifact the 138 stored results were read from, and marking it superseded risks
withholding them. `companion_of`, now pointing both ways, carries what a reader needs.

### 4. Does the new Figure 2 panel shift a stored locator?

Yes, exactly one, and it has been amended.

Preprint Figure 2 runs a to g: "(c) Classification of ClinVar pathogenic vs. gnomAD common missense
variants", "(d) ... COSMIC frequent ...", "(e) ... OMIM pathogenic ...", "(f) Enrichment of rare
(singletons) vs. common ... gnomAD variants", "(g) ... DepMap essential vs. non-essential genes".
Published Figure 2 runs a to h with the same c, a new d ("Classification of ClinVar pathogenic
versus ClinVar benign missense variants"), then COSMIC at e, OMIM at f, gnomAD at g and DepMap at
h.

Every stored GPN-MSA locator was scanned for a Figure 2 panel letter of this paper. Two cite one:

- `gfm-guides-20261014-gpnmsa-protocol-ablation-gnomad-odds-ratio` read "Figure 2 caption panel
  (f)", which is gnomAD in the preprint and panel (g) in the published version. Amended to name
  both, with the previous text kept in claim
  `metadata-correction-gpn-msa-ablation-gnomad-locator-20261116`.
- `gfm-guides-20261014-gpnmsa-model-gpn-msa` reads "preprint v2 Figure 2a caption". Already
  version-qualified, and panel a does not move. Left alone.

The other 44 locators matching "Fig" belong to other papers (`lu-hetero-20261019`,
`gfm-guide-20261014` Figure 1, `lit-genomics-20261011` file names) and are unaffected.

### 5. Should the preprint bytes be archived under a batch folder?

**No. Archive nothing; pin the text layer instead.**

The recommendation was to archive the pinned preprint bytes under the batch folder, which
CC BY-NC-ND permits for the preprint though not for the Springer artifacts. The licence reading is
right and the goal is right, but archiving bytes does not reach it, for three reasons.

The pinned bytes no longer exist to be archived. `10411077df1ae59614f9a9a9f85384103d54127ba67a9b3c469a4a2d6c33cee4`
was the extractor's October copy; no download reproduces it. Anything archived now would be a
different copy under a hash that contradicts the record, so the archive would either sit there
not matching its own source record, or force a repin of a source that 138 stored results depend
on. Neither is an improvement.

An archived copy would not make future downloads verifiable either. Three downloads taken during
this review gave two distinct hashes at an identical byte length, so bioRxiv rotates between
variants rather than stamping each request uniquely. A reader comparing their download against an
archived copy would get a mismatch roughly at random, which is worse than no check, because it
looks like evidence of tampering.

And the thing worth pinning is stable and costs nothing to store. The `pdftotext -layout` text
layer is byte-identical across all three downloads at
`c6e95eb807550bb97aa2b8991c013f28fe11742006582c25818fcf90cad30c79`. Every value the store holds
from this source was read from that text layer, not from the PDF bytes, so it is also the artifact
the records actually depend on. Recording its hash in the source record's `hash_scope`, which today
asserts the text layer is identical without naming a hash, converts a prose assurance into a check
anyone can run in two commands. If the store does want bytes as well, the BenchBench precedent of a
gzipped `*.layout.txt.gz` with an `archive_sha256` is the shape to copy, and it should archive the
text layer, not the PDF.

Not applied here, deliberately. The source is owned by `data/omics/gfm-guides-20261014-gpnmsa`,
this review has already changed that record once today, and cross-batch GPN-MSA fixes are being
sequenced by the coordinator. It is a one-field change away whenever that sequencing reaches it.

### 6. The extractor's remaining questions

- **`companion_of` direction.** Now bidirectional. See ruling 2.
- **Should the 16 held-out accuracy cells be extracted?** No, not here. They are identical in both
  versions, confirmed by the reviewer's own parse of both text layers: Supplementary Table 1 gives
  CDS 0.915 / 1.032, 5' UTR 0.837 / 1.646, 3' UTR 0.821 / 1.688, Non-exonic 0.690 / 1.978 over 39M
  positions, and Table 2 gives 0.227 / 0.680, 0.177 / 0.679, 0.245 / 0.603, 0.268 / 0.515 over 245K
  positions. They are language-model accuracy figures, not variant-effect results, which is the
  scope line the earlier batch drew and this review keeps. If they belong in the store they are a
  separate batch, and nothing about the published version changes that judgement.
- **Is the comparison claim's subject right?** Yes. A reader arriving at the preprint source is the
  reader who needs to know what the version of record does with its values, and the numbering and
  panel claims sit on the benchmark because they are properties of the study, not of one artifact.
  No change.
- **The three `denominator` claims against the dataset records.** Not applied, and this is a
  deliberate hold rather than an omission. The ClinVar, COSMIC and OMIM dataset records carry
  `missing_metadata.denominator` with reason `unreported`, which was true of the preprint and is no
  longer true of the paper. Moving the counts onto the records is defensible, but the evidence for
  them is a Figure 2 caption describing the main comparison, and Extended Data Table 1 says only
  that the ablation uses "the same setting as" that panel. For gnomAD the two are demonstrably not
  the same set, since the ablation subsets the rare variants. Rather than move three of four and
  leave the fourth, the review leaves all four as claims, which is where the evidence actually
  sits, and recommends the move be decided together with whoever owns the dataset records.

## Edits

Two stored records, both recorded with `npm run records -- change` against this review:

| Record | Field | Change |
| --- | --- | --- |
| `gfm-guides-20261014-gpnmsa-source-biorxiv-v2` | `limitations`, `links` | Entries 1 and 4 rewritten, one entry added, `companion_of` edge added |
| `gfm-guides-20261014-gpnmsa-protocol-ablation-gnomad-odds-ratio` | `source_locator` | Names both the preprint panel (f) and the published panel (g) |

Inside the batch, every source and claim record had its `review` object replaced with the
reviewer's, its `status` moved from `needs_review` to `source_checked`, and the two correction
claims were added. One claim's `value` was reworded:
`gpn-msa-published-20261116-claim-ablation-values-unchanged` now states how the two readings were
produced and that the published Methods were not retrieved, instead of asserting sameness flatly.

## Discrepancies

None. The batch contributes no result records, so no batch result ID can appear in
`outlier_results` or `consensus_results`, and no `discrepancy_review` revision is called for.

## Gaps

1. The peer-reviewed Results and Methods body was not retrieved and is in no open index. Checked
   independently at review time.
2. The two DMS TADBP AUROCs therefore remain uncompared: 136 of 138, not 138 of 138.
3. The published values rest on OCR of a raster image. That is a machine reading and independent of
   both the extractor and the stored records, but it is recognition rather than a text-layer parse,
   and there is no deterministic route to these values while the publisher ships them as a picture.
4. Because the Methods were not retrieved, the ablation definitions in the published version were
   not read. Identical values are evidence the settings did not change, not proof.
5. The main comparisons against CADD, phyloP, phastCons, ESM-1b, Nucleotide Transformer, HyenaDNA,
   Enformer and SpliceAI are printed only as figures in both versions, with no Source Data file,
   and stay unextracted.
6. The published Figure 2 panel d gives 21,275 ClinVar pathogenic variants where panel c gives
   21,273. The paper does not explain the difference. Panel d has no stored counterpart, so nothing
   in the store depends on it, but it is noted here as a lead rather than left unremarked.
