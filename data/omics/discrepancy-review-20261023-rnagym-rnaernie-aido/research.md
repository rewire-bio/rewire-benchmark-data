# Research: RNAErnie against AIDO.RNA, RNAGym leaderboard against Wang 2026 (#209)

`discrepancy-8c69346a6089882b` flags the RNAGym fitness leaderboard v0.1.1 for ranking RNAErnie above AIDO.RNA on the ncRNA DMS assays, where Wang et al. 2026 ranks AIDO.RNA above RNAErnie. Revision 1 recorded it as `investigating`, with the hypothesis that Wang's absolute Spearman caused the reversal. This batch adds revision 2: `explained`.

## Findings

1. **Same assays.** Wang uses 31 RNAGym ncRNA assays of at most 440 nt. The reference sheet at the pinned leaderboard commit has 31 ncRNA assays, the longest 425 nt.
2. **Wang's SR is absolute.** Stated in the Methods. This is a real difference but does not explain the reversal on its own.
3. **The leaderboard's RNAErnie score is not comparable with its AIDO.RNA score.** At v0.1.1 RNAErnie's score was carried over from its original script. The maintainers later read that script: one pass over the unmasked wild type, softmax, raw probability differences summed over the mutated positions. They call its 0.1937 "not comparable with the masked checkpoints" (commit `d43db8c613`). It cannot be rescored without a paddlepaddle environment.
4. **Rescoring reverses the order.** v0.1.1 scored AIDO.RNA with mut-fill, the weakest of four strategies. Rescored with wt-fill, AIDO.RNA "takes second place from RNA-ERNIE" (commit `d024cd81a3`). The current v0.2 table: AIDO.RNA 650M 0.21, 1.6B 0.20, RNA-ERNIE 0.19. That is Wang's order.
5. **RNA-ERNIE's ribozyme lead is mostly mutation count.** Ribozyme 0.14 overall, about 0.02 among variants with the same number of mutations. The mutation-count baseline scores 0.20 on ribozymes.

## Decision

`explained`: the outlier rests on a score its own publisher says is not comparable, and the publisher's rescored table agrees with the consensus. No result is changed.

## Not done

- No evidence concern was added to the four v0.1.1 RNAErnie results. The finding will keep firing while those results are compared; it is settled by this claim.
- The absolute Spearman in Wang's fitness tables is a general concern: the RNAGym maintainers report that 190 of 496 model and assay pairs on these assays rank variants backwards (commit `093ae10565`), and all were credited as positive under the absolute metric. Whether to add a concern on Wang's SR results or contact the authors is a separate decision.
- v0.2 is a development branch with 29 assays and molecule averaging. If it is merged to `main` and released, it should be extracted as a new source.

## Limits

- Automated review by a Claude agent; not human scientific review.
- The extractor and the reviewer are the same agent in the same session.
