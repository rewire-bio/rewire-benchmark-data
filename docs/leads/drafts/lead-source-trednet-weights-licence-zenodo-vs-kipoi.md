# TREDNet weights: CC BY 4.0 on Zenodo, CC-BY-ND in the Kipoi descriptions

Raise at: https://github.com/okurman/TREDNet (issues)  
Register entry: `lead-source-trednet-weights-licence-zenodo-vs-kipoi`

Zenodo record 6463875, which holds `TREDNet_weights_phase_one.hdf5` and the other weight files, declares `"license": {"id": "cc-by-4.0"}`. The Kipoi model description `kipoi/TREDNet/phase_one/model.yaml` in the repository at commit 0fcd3023a210df6c5ca9a4ae7a055eb9f9d4eaa7 takes its weights from the same record (`url: https://zenodo.org/record/6463875/files/TREDNet_weights_phase_one.hdf5`) and declares:

> license: CC-BY-ND

A no-derivatives licence would not allow fine-tuned or modified versions of the weights; CC BY does.

Which licence applies to the released weights? The Kipoi files also describe held-out chromosomes 7, 8 and 9 where the PNAS paper gives 8 and 9; if the Kipoi files describe an earlier training run, a note there would help.

This was found while compiling an independent database of benchmark results: <record page>
