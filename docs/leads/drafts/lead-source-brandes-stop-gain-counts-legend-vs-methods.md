# Stop-gain benchmark: two sets of pathogenic counts in the same paper

Raise at: https://github.com/ntranoslab/esm-variants (issues)  
Register entry: `lead-source-brandes-stop-gain-counts-legend-vs-methods`

In Brandes et al. 2023 (Nature Genetics, doi 10.1038/s41588-023-01465-0, read as PMC10484790), the Fig. 6d legend gives the stop-gain groups as:

> undergo NMD (32,362 pathogenic and 198 benign variants) or (3) all stop-gain variants (36,034 pathogenic and 345 benign

The Methods description of the bootstrapping gives the same groups as:

> 32,441 pathogenic and 198 benign variants expected to lead to NMD, and 36,113 pathogenic and 345 benign variants

The benign counts and the group without NMD (3,672 pathogenic, 147 benign) agree. Both pathogenic counts differ by the same 79 variants.

Which counts belong to the stop-gain benchmark file in the repository, and were the reported AUCs computed on that set?

This was found while compiling an independent database of benchmark results: <record page>
