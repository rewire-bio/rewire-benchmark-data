# Research notes

Part of the 2026-10-12 ML-versus-baseline pass for issue #121. No literature search was run: the source was named in the issue. The store had no Haas et al. 2019 source before this batch; the 2026-10-09 RNA fusion pass screened it and recorded that it prints per-method accuracy only in figures.

## Finding

Confirmed: Haas et al. 2019 compare 23 fusion callers, including STAR-Fusion, Arriba, EricScript and deFuse, on simulated reads and 60 cancer cell lines, but print no per-method accuracy value in a table or in the text. Additional file 1 holds per-fusion predictions; turning them into accuracy would need the paper's scoring rules (lenient paralog matching, minimum-evidence thresholds, truth sets from n = 3 to 10 agreeing methods), which the text does not specify precisely enough for a derivation under docs/collection.md. So this batch holds no protocol, evaluation or result, and no relevance judgement.

## What was recorded

- The source record.
- Table 1 method descriptions for EricScript (AdaBoost classifier trained on synthetic data scores and ranks predictions), Arriba (rule-based filters on STAR chimeric alignments) and STAR-Fusion (filtering of STAR chimeric alignments), as claims on the existing method records. These support the existing method-type tags.
- Two Discussion sentences: STAR-Fusion, Arriba and STAR-SEQR had the best combination of speed and accuracy; EricScript was the least accurate method on cancer cell line RNA-seq.

Record counts: claim 5, source 1. Everything is `needs_review`.

## Not recorded

deFuse also uses an AdaBoost classifier (Table 1), but the store has no deFuse record and no deFuse result exists to attach it to.
