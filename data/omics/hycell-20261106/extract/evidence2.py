"""Results the HyCell report prints in prose (Sections 3.2 and 4)."""

from evidence import DATA, page

CT = DATA["Cross-tissue immune"]


def build(parsed, o):
    pr = parsed["prose"]
    s32 = f"Section 3.2 'Embedding structure', final sentence ({page('section32')})"
    pca_b, hy_b, pca_bio, _hy_bio = pr["ctia"]
    o.add("batch-correction", "PCA", CT, pca_b, s32 + "; PCA batch correction")
    o.add("batch-correction", "HyCell", CT, hy_b, s32 + "; HyCell batch correction")
    o.add("bio-conservation", "PCA", CT, pca_bio, s32 + "; PCA biological conservation")
    # HyCell's 0.63 rounds Figure 1b's 0.633, which is already recorded; not stored twice.

    s41 = f"Section 4.1 ({page('section41')})"
    ari, nmi = pr["cd4"]
    o.add("cd4-split-ari", "HyCell", CT, ari, s41 + ", sentence giving HyCell's split (ARI)",
          limits=["Every other embedding, Stack and PCA included, reaches ARI at most 0.031 on this "
                  "split; their individual values are printed only as Figure 4a bars."])
    o.add("cd4-split-nmi-chemistry", "HyCell", CT, nmi, s41 + ", 'NMI with chemistry'")
    for label, value in zip(["HyCell", "UCE", "Tahoe-x1 (70M)"], pr["cd4_donor"]):
        o.add("cd4-split-ari-within-donor", label, CT, value,
              s41 + f", sentence 'Within single donors', value for {label}")
    for label, value in zip(["HyCell", "PCA"], pr["gd"]):
        o.add("gd-t-split-ari", label, CT, value,
              s41 + f", gamma-delta T against tissue-resident CD8 T, value for {label}")

    s42 = f"Section 4.2 ({page('section42')})"
    all_cells = {"HyCell": pr["pt_hycell"][0], "Stack": pr["pt_others"][0],
                 "SCimilarity": pr["pt_others"][2], "PCA": pr["pt_others"][4]}
    donor = {"HyCell": pr["pt_hycell"][1], "Stack": pr["pt_others"][1],
             "SCimilarity": pr["pt_others"][3], "PCA": pr["pt_others"][5]}
    for label, value in all_cells.items():
        o.add("pseudotime-stage-spearman", label, CT, value, s42 + f", all cells, {label}")
    for label, value in donor.items():
        o.add("pseudotime-stage-spearman-donor-mean", label, CT, value,
              s42 + f", averaged over donors, {label}")

    s43 = f"Section 4.3 ({page('section43')})"
    o.add("decoder-fold-change-spearman", "HyCell", CT, pr["decoder_fc"][0],
          s43 + ", decoded against counted fold changes")
    c = pr["consistency"]
    for slug, dec, cnt, pair in [("donor-consistency-plasma", c[0], c[1], "plasma-cell axis"),
                                 ("donor-consistency-monocyte", c[2], c[3], "monocytes"),
                                 ("donor-consistency-cd4", c[4], c[5], "CD4 T cells")]:
        o.add(slug, "HyCell", CT, dec, s43 + f", {pair}, decoder; also Figure 5c")
        o.add(slug, "pseudobulk counts", CT, cnt, s43 + f", {pair}, pseudobulk counts; also Figure 5c")
    return o
