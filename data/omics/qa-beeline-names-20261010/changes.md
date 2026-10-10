# BEELINE protocol names (rewire-benchmark-data#92)

The text is edited in place in `data/entities/protocols.jsonl`, 54 lines. The other 544 lines are byte-identical. `batch.jsonl` holds one metadata-correction claim per changed field: 250 in total (54 names, 54 descriptions, 71 panel titles, 71 caveats). The 54 descriptions were added in review: they carried the same "Input conditions" sentence as the caveats. The records CLI was not run: the integrator runs `records -- change` for the 54 protocols and `records -- add` for `batch.jsonl`. Until then, `addBatch` refuses the store with "changed without a provenance entry", as expected. Against the store at HEAD, `batch.jsonl` adds cleanly (250 records).

`build.py` reads the original lines from git HEAD, applies the change, regenerates `batch.jsonl` and the table below, and asserts its checks. `build.py --check` repeats the checks without writing.

## Patterns

- **44 Figure 5 protocols.** Name `BEELINE 2020 Figure 5 · <cell type> · <reference_network> network, <gene_selection> genes`. Panel title `<new name>: Early Precision Ratio`. Caveat `Input conditions: <reference_network> network, <gene_selection> genes.` Both values are copied verbatim from the old object.
- **10 Figure 2 and Figure 4 protocols.** The trailing ` · {}` is dropped from the name, for example `BEELINE 2020 Figure 2 · LI`. Each panel title becomes `<new name>: <metric>` (AUPRC Ratio, Stability Across Datasets, Early Precision Ratio, EPR Activation or EPR Inhibition). The sentence `Input conditions: {}.` is dropped from each of their 27 caveats, because the real conditions are on the evaluations. Each caveat now reads `Source-specific evaluation. No equivalence to other releases, protocols or model families is inferred.` No caveat became empty, so none was removed.

## Checks (asserted by build.py)

- Exactly the 54 target lines changed, and in those records nothing outside `name`, `description` and `attributes` changed.
- No brace remains in any new name, panel title or `Input conditions` caveat. All 54 new names are unique among the 598 protocols.
- **Structured values:** each of the 264 evaluations of the 44 Figure 5 protocols carries `attributes.conditions.reference_network` and `conditions.gene_selection`, equal to the values in the old name. The protocols hold them only as text. No field was added.
- **Pins and judgements:** none cover these 54 protocols. No use case links them, no assessed_by judgement names them and no pin mentions their IDs. Each has one benchmark-membership claim, which uses the ID.
- **Other references:** no other record's name or text contains an old name. The dated snapshots in `data/omics/baseline-coverage/` were left as they are.

## "log/gof"

Two mESC protocols name the reference network `log/gof`:
- `acquired-protocol-174f1a5acdc3c13db7b2`, TFs+500;
- `acquired-protocol-b1b289fa63273aa8bba2`, TFs+1000.

The archived source CSV prints the same text. In `data/omics/acquisition/2026-09-19/cells-networks/sources/beeline-14_ESM.csv.gz` (decompressed SHA-256 `1f6a38649aa1fc1d90522e3d09f85f7e5714cc80c585ef679ed7603d7a1c7b70`, matching the source record `acquired-source-31344fb7e5e8ae6b9666`), row 19 reads:

```
log/gof,mESC,34,775,0.16,1.32,1.36,1.26,1.3,1.04,0.84,34,1099,0.15,1.31,1.33,...
```

Column 1 holds the reference network. The new names keep `log/gof` as printed. BEELINE describes this mESC network as loss- and gain-of-function, usually abbreviated `lof/gof`, so the source table probably has a typo. That was not checked against the paper.

## Old and new names

| Protocol | Old name | New name |
| --- | --- | --- |
| `acquired-protocol-fabd886c5f7a9dbfdbab` | `BEELINE 2020 Figure 2 · BF · {}` | BEELINE 2020 Figure 2 · BF |
| `acquired-protocol-562a238b609a61077d81` | `BEELINE 2020 Figure 2 · BFC · {}` | BEELINE 2020 Figure 2 · BFC |
| `acquired-protocol-1b09d04bdd84c0554bd1` | `BEELINE 2020 Figure 2 · CY · {}` | BEELINE 2020 Figure 2 · CY |
| `acquired-protocol-18da78ff7de51ffb5605` | `BEELINE 2020 Figure 2 · LI · {}` | BEELINE 2020 Figure 2 · LI |
| `acquired-protocol-d66bbf2b3dd743f2db47` | `BEELINE 2020 Figure 2 · LL · {}` | BEELINE 2020 Figure 2 · LL |
| `acquired-protocol-19f8c76e99a986094a6f` | `BEELINE 2020 Figure 2 · TF · {}` | BEELINE 2020 Figure 2 · TF |
| `acquired-protocol-25210daa0dccd840d2fb` | `BEELINE 2020 Figure 4 · GSD · {}` | BEELINE 2020 Figure 4 · GSD |
| `acquired-protocol-c7f45d872952b996c96a` | `BEELINE 2020 Figure 4 · HSC · {}` | BEELINE 2020 Figure 4 · HSC |
| `acquired-protocol-37b5599b7d976211e8c1` | `BEELINE 2020 Figure 4 · VSC · {}` | BEELINE 2020 Figure 4 · VSC |
| `acquired-protocol-f6bf921e477601ffffec` | `BEELINE 2020 Figure 4 · mCAD · {}` | BEELINE 2020 Figure 4 · mCAD |
| `acquired-protocol-408cb9c598ef659f51a6` | `BEELINE 2020 Figure 5 · MHSC-GM · {"reference_network":"Cell-type specific ChIP-Seq","gene_selection":"TFs+1000"}` | BEELINE 2020 Figure 5 · MHSC-GM · Cell-type specific ChIP-Seq network, TFs+1000 genes |
| `acquired-protocol-f6bd2f323f0f81692075` | `BEELINE 2020 Figure 5 · MHSC-GM · {"reference_network":"Cell-type specific ChIP-Seq","gene_selection":"TFs+500"}` | BEELINE 2020 Figure 5 · MHSC-GM · Cell-type specific ChIP-Seq network, TFs+500 genes |
| `acquired-protocol-a8f87266d6be53bbd23b` | `BEELINE 2020 Figure 5 · MHSC-GM · {"reference_network":"Non-specific ChIP-Seq","gene_selection":"TFs+1000"}` | BEELINE 2020 Figure 5 · MHSC-GM · Non-specific ChIP-Seq network, TFs+1000 genes |
| `acquired-protocol-ceaaa7b9d8af61e51736` | `BEELINE 2020 Figure 5 · MHSC-GM · {"reference_network":"Non-specific ChIP-Seq","gene_selection":"TFs+500"}` | BEELINE 2020 Figure 5 · MHSC-GM · Non-specific ChIP-Seq network, TFs+500 genes |
| `acquired-protocol-c8cff8ffd3fbf524bf2e` | `BEELINE 2020 Figure 5 · MHSC-GM · {"reference_network":"STRING","gene_selection":"TFs+1000"}` | BEELINE 2020 Figure 5 · MHSC-GM · STRING network, TFs+1000 genes |
| `acquired-protocol-c57e646de930422fa536` | `BEELINE 2020 Figure 5 · MHSC-GM · {"reference_network":"STRING","gene_selection":"TFs+500"}` | BEELINE 2020 Figure 5 · MHSC-GM · STRING network, TFs+500 genes |
| `acquired-protocol-30ca92be5250d3347718` | `BEELINE 2020 Figure 5 · hESC · {"reference_network":"Cell-type specific ChIP-Seq","gene_selection":"TFs+1000"}` | BEELINE 2020 Figure 5 · hESC · Cell-type specific ChIP-Seq network, TFs+1000 genes |
| `acquired-protocol-a930238c7acc35fd34ee` | `BEELINE 2020 Figure 5 · hESC · {"reference_network":"Cell-type specific ChIP-Seq","gene_selection":"TFs+500"}` | BEELINE 2020 Figure 5 · hESC · Cell-type specific ChIP-Seq network, TFs+500 genes |
| `acquired-protocol-bd9b01304308808a7b38` | `BEELINE 2020 Figure 5 · hESC · {"reference_network":"Non-specific ChIP-Seq","gene_selection":"TFs+1000"}` | BEELINE 2020 Figure 5 · hESC · Non-specific ChIP-Seq network, TFs+1000 genes |
| `acquired-protocol-eceec78306355eece4e7` | `BEELINE 2020 Figure 5 · hESC · {"reference_network":"Non-specific ChIP-Seq","gene_selection":"TFs+500"}` | BEELINE 2020 Figure 5 · hESC · Non-specific ChIP-Seq network, TFs+500 genes |
| `acquired-protocol-b3a78798ab8a7602a63a` | `BEELINE 2020 Figure 5 · hESC · {"reference_network":"STRING","gene_selection":"TFs+1000"}` | BEELINE 2020 Figure 5 · hESC · STRING network, TFs+1000 genes |
| `acquired-protocol-6ddc5a89a2b4c4c474d7` | `BEELINE 2020 Figure 5 · hESC · {"reference_network":"STRING","gene_selection":"TFs+500"}` | BEELINE 2020 Figure 5 · hESC · STRING network, TFs+500 genes |
| `acquired-protocol-4178cb595371e239c8fd` | `BEELINE 2020 Figure 5 · hHep · {"reference_network":"Cell-type specific ChIP-Seq","gene_selection":"TFs+1000"}` | BEELINE 2020 Figure 5 · hHep · Cell-type specific ChIP-Seq network, TFs+1000 genes |
| `acquired-protocol-34109c3e92506dce8489` | `BEELINE 2020 Figure 5 · hHep · {"reference_network":"Cell-type specific ChIP-Seq","gene_selection":"TFs+500"}` | BEELINE 2020 Figure 5 · hHep · Cell-type specific ChIP-Seq network, TFs+500 genes |
| `acquired-protocol-e0ffaca06ad1222ac21e` | `BEELINE 2020 Figure 5 · hHep · {"reference_network":"Non-specific ChIP-Seq","gene_selection":"TFs+1000"}` | BEELINE 2020 Figure 5 · hHep · Non-specific ChIP-Seq network, TFs+1000 genes |
| `acquired-protocol-81fdcee5288c3672584a` | `BEELINE 2020 Figure 5 · hHep · {"reference_network":"Non-specific ChIP-Seq","gene_selection":"TFs+500"}` | BEELINE 2020 Figure 5 · hHep · Non-specific ChIP-Seq network, TFs+500 genes |
| `acquired-protocol-2a8b0faaeabb2b42f8fb` | `BEELINE 2020 Figure 5 · hHep · {"reference_network":"STRING","gene_selection":"TFs+1000"}` | BEELINE 2020 Figure 5 · hHep · STRING network, TFs+1000 genes |
| `acquired-protocol-994c136cc78955a7777e` | `BEELINE 2020 Figure 5 · hHep · {"reference_network":"STRING","gene_selection":"TFs+500"}` | BEELINE 2020 Figure 5 · hHep · STRING network, TFs+500 genes |
| `acquired-protocol-b782c1901e3d8fb8348e` | `BEELINE 2020 Figure 5 · mDC · {"reference_network":"Cell-type specific ChIP-Seq","gene_selection":"TFs+1000"}` | BEELINE 2020 Figure 5 · mDC · Cell-type specific ChIP-Seq network, TFs+1000 genes |
| `acquired-protocol-4745597f348c3ff0e85a` | `BEELINE 2020 Figure 5 · mDC · {"reference_network":"Cell-type specific ChIP-Seq","gene_selection":"TFs+500"}` | BEELINE 2020 Figure 5 · mDC · Cell-type specific ChIP-Seq network, TFs+500 genes |
| `acquired-protocol-1227fd691dca8a3aa41d` | `BEELINE 2020 Figure 5 · mDC · {"reference_network":"Non-specific ChIP-Seq","gene_selection":"TFs+1000"}` | BEELINE 2020 Figure 5 · mDC · Non-specific ChIP-Seq network, TFs+1000 genes |
| `acquired-protocol-3c4df1f88f28c01a7508` | `BEELINE 2020 Figure 5 · mDC · {"reference_network":"Non-specific ChIP-Seq","gene_selection":"TFs+500"}` | BEELINE 2020 Figure 5 · mDC · Non-specific ChIP-Seq network, TFs+500 genes |
| `acquired-protocol-a72274bbb664040489be` | `BEELINE 2020 Figure 5 · mDC · {"reference_network":"STRING","gene_selection":"TFs+1000"}` | BEELINE 2020 Figure 5 · mDC · STRING network, TFs+1000 genes |
| `acquired-protocol-edb7d264956f89df17fc` | `BEELINE 2020 Figure 5 · mDC · {"reference_network":"STRING","gene_selection":"TFs+500"}` | BEELINE 2020 Figure 5 · mDC · STRING network, TFs+500 genes |
| `acquired-protocol-7f7b37c767904dd8a6fb` | `BEELINE 2020 Figure 5 · mESC · {"reference_network":"Cell-type specific ChIP-Seq","gene_selection":"TFs+1000"}` | BEELINE 2020 Figure 5 · mESC · Cell-type specific ChIP-Seq network, TFs+1000 genes |
| `acquired-protocol-024f47659eb7e75f56dc` | `BEELINE 2020 Figure 5 · mESC · {"reference_network":"Cell-type specific ChIP-Seq","gene_selection":"TFs+500"}` | BEELINE 2020 Figure 5 · mESC · Cell-type specific ChIP-Seq network, TFs+500 genes |
| `acquired-protocol-fbb04bf73e09481732c8` | `BEELINE 2020 Figure 5 · mESC · {"reference_network":"Non-specific ChIP-Seq","gene_selection":"TFs+1000"}` | BEELINE 2020 Figure 5 · mESC · Non-specific ChIP-Seq network, TFs+1000 genes |
| `acquired-protocol-dc2ce864a7578927cabc` | `BEELINE 2020 Figure 5 · mESC · {"reference_network":"Non-specific ChIP-Seq","gene_selection":"TFs+500"}` | BEELINE 2020 Figure 5 · mESC · Non-specific ChIP-Seq network, TFs+500 genes |
| `acquired-protocol-b7da29c68a46720cce0b` | `BEELINE 2020 Figure 5 · mESC · {"reference_network":"STRING","gene_selection":"TFs+1000"}` | BEELINE 2020 Figure 5 · mESC · STRING network, TFs+1000 genes |
| `acquired-protocol-7913b13aba9d987c38ae` | `BEELINE 2020 Figure 5 · mESC · {"reference_network":"STRING","gene_selection":"TFs+500"}` | BEELINE 2020 Figure 5 · mESC · STRING network, TFs+500 genes |
| `acquired-protocol-b1b289fa63273aa8bba2` | `BEELINE 2020 Figure 5 · mESC · {"reference_network":"log/gof","gene_selection":"TFs+1000"}` | BEELINE 2020 Figure 5 · mESC · log/gof network, TFs+1000 genes |
| `acquired-protocol-174f1a5acdc3c13db7b2` | `BEELINE 2020 Figure 5 · mESC · {"reference_network":"log/gof","gene_selection":"TFs+500"}` | BEELINE 2020 Figure 5 · mESC · log/gof network, TFs+500 genes |
| `acquired-protocol-b614e3405917763fb159` | `BEELINE 2020 Figure 5 · mHSC-E · {"reference_network":"Cell-type specific ChIP-Seq","gene_selection":"TFs+1000"}` | BEELINE 2020 Figure 5 · mHSC-E · Cell-type specific ChIP-Seq network, TFs+1000 genes |
| `acquired-protocol-b022aafcf374cd51f0f3` | `BEELINE 2020 Figure 5 · mHSC-E · {"reference_network":"Cell-type specific ChIP-Seq","gene_selection":"TFs+500"}` | BEELINE 2020 Figure 5 · mHSC-E · Cell-type specific ChIP-Seq network, TFs+500 genes |
| `acquired-protocol-f4f5a4cb785dc55503bb` | `BEELINE 2020 Figure 5 · mHSC-E · {"reference_network":"Non-specific ChIP-Seq","gene_selection":"TFs+1000"}` | BEELINE 2020 Figure 5 · mHSC-E · Non-specific ChIP-Seq network, TFs+1000 genes |
| `acquired-protocol-51354be75f1492ed099a` | `BEELINE 2020 Figure 5 · mHSC-E · {"reference_network":"Non-specific ChIP-Seq","gene_selection":"TFs+500"}` | BEELINE 2020 Figure 5 · mHSC-E · Non-specific ChIP-Seq network, TFs+500 genes |
| `acquired-protocol-a9a52bfc61cc00ae40eb` | `BEELINE 2020 Figure 5 · mHSC-E · {"reference_network":"STRING","gene_selection":"TFs+1000"}` | BEELINE 2020 Figure 5 · mHSC-E · STRING network, TFs+1000 genes |
| `acquired-protocol-78f8093a50e8fca5eacc` | `BEELINE 2020 Figure 5 · mHSC-E · {"reference_network":"STRING","gene_selection":"TFs+500"}` | BEELINE 2020 Figure 5 · mHSC-E · STRING network, TFs+500 genes |
| `acquired-protocol-d60261afa2c58e4aa12e` | `BEELINE 2020 Figure 5 · mHSC-L · {"reference_network":"Cell-type specific ChIP-Seq","gene_selection":"TFs+1000"}` | BEELINE 2020 Figure 5 · mHSC-L · Cell-type specific ChIP-Seq network, TFs+1000 genes |
| `acquired-protocol-f7ef0c77a6155a1ff0d4` | `BEELINE 2020 Figure 5 · mHSC-L · {"reference_network":"Cell-type specific ChIP-Seq","gene_selection":"TFs+500"}` | BEELINE 2020 Figure 5 · mHSC-L · Cell-type specific ChIP-Seq network, TFs+500 genes |
| `acquired-protocol-bd571aa3305cceba1f0b` | `BEELINE 2020 Figure 5 · mHSC-L · {"reference_network":"Non-specific ChIP-Seq","gene_selection":"TFs+1000"}` | BEELINE 2020 Figure 5 · mHSC-L · Non-specific ChIP-Seq network, TFs+1000 genes |
| `acquired-protocol-ed61833eb749ba711c5b` | `BEELINE 2020 Figure 5 · mHSC-L · {"reference_network":"Non-specific ChIP-Seq","gene_selection":"TFs+500"}` | BEELINE 2020 Figure 5 · mHSC-L · Non-specific ChIP-Seq network, TFs+500 genes |
| `acquired-protocol-7977f5aa02ec0001bc1a` | `BEELINE 2020 Figure 5 · mHSC-L · {"reference_network":"STRING","gene_selection":"TFs+1000"}` | BEELINE 2020 Figure 5 · mHSC-L · STRING network, TFs+1000 genes |
| `acquired-protocol-61ae01473c4e5c4a9ce5` | `BEELINE 2020 Figure 5 · mHSC-L · {"reference_network":"STRING","gene_selection":"TFs+500"}` | BEELINE 2020 Figure 5 · mHSC-L · STRING network, TFs+500 genes |
