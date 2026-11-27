# Puffin-D weights: Zenodo record says CC BY 4.0, README and LICENSE say academic use only

Raise at: https://github.com/jzhoulab/puffin (issues)  
Register entry: `lead-source-puffin-weights-zenodo-cc-by-vs-academic-only`

The README at commit 9bc81eb922f44556879d1d2afd4c757a1d6c291e downloads the model from Zenodo (`wget https://zenodo.org/record/7941729/files/puffin_D.pth`) and states:

> Puffin is completely free for any non-commercial and academic use, and please contact us for commercial applications.

The LICENSE in the same commit permits use "for academic research use only". The Zenodo record 7941729 that holds `puffin_D.pth` declares `"license": {"id": "cc-by-4.0"}`, which allows commercial use.

Is the Zenodo licence intended for the weights, or was it a default setting on the deposit? If the academic terms apply, updating the Zenodo record would remove the ambiguity.

This was found while compiling an independent database of benchmark results: <record page>
