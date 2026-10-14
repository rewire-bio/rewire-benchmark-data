# Sources

## lit-agents-20261013-biomlbench-source-miller2025-v3

- Title: BioML-bench: Evaluation of AI Agents for End-to-End Biomedical ML
- Authors: Henry E. Miller, Matthew Greenig, Benjamin Tenmann, Bo Wang
- URL: https://www.biorxiv.org/content/10.1101/2025.09.01.673319v3
- Artifact: https://www.biorxiv.org/content/10.1101/2025.09.01.673319v3.full.pdf (12 pages, 2,282,513 bytes)
- Version: bioRxiv version 3, posted 2025-09-28. Versions 1 (2025-09-04) and 2 (2025-09-07) exist; only v3 was read.
- DOI: 10.1101/2025.09.01.673319
- Status: preprint. The bioRxiv publication API reports no published version (queried 2026-10-13). No arXiv version was found.
- Licence: CC-BY-4.0 (bioRxiv API and the PDF page header)
- Retrieved: 2026-10-13T12:38:42Z
- SHA-256: 875cb3519dac9b0ec51c35224e1fc90b107b0676a4cc7c22cecb56eb8ac38b35
- Not archived in the batch (size); the hash pins the bytes read.

## lit-agents-20261013-biomlbench-source-repo-673f3d8

- URL: https://github.com/science-machine/biomlbench/tree/673f3d8d3462fc6cdcbbd9695fba612b9332ca65
- Artifact: https://codeload.github.com/science-machine/biomlbench/tar.gz/673f3d8d3462fc6cdcbbd9695fba612b9332ca65 (1,533,925 bytes)
- Version: commit 673f3d8d3462fc6cdcbbd9695fba612b9332ca65, 2025-09-14, head of `main` at retrieval (GitHub API `pushed_at` 2025-09-14T17:37:56Z). README title "BioML-bench (v0.1-alpha)".
- Licence: MIT
- Retrieved: 2026-10-13T12:38:10Z
- SHA-256 of the tar.gz: c23978275652d61452e710dfdf94613237b85ab9b90605af457d082c351ae559 (a second download later the same session gave the same hash)

Files cited, SHA-256 of each file inside the archive:

| File | SHA-256 |
| --- | --- |
| README.md | 90e9f9e352d4f2c22817ba8305aa836c12dd56a0055ac7518de014e625721c92 |
| LICENSE | 7f0f5da32622d347c31280b5a35bb5a2db91e97c706b4f4f9ce02776371d20f3 |
| experiments/biomlbench_v0.1a.txt | d19b815b1222f178457ba4e46e5430eaa2dba299e4c06d3240367624a26b5faf |
| agents/biomni/config.yaml | 2443f151826a640d16f711384b44a8b4843cc70c940bc62fc50dfcc9f461d26d |
| agents/biomni/main.py | 52e8344651c19c1d86b0bf24a68652f884d2fbc9dc75ce8ad0cda83794d68134 |
| agents/aide/config.yaml | c5ee94e79b2962e47b780f7d3c1cfa0a4f588287ee157b33c42cfd81388494f5 |
| agents/aide/requirements.txt | c8f06bcea1f98df3739a265e599c35b089fff3951360351517f02b74809aba34 |
| agents/stella/config.yaml | 5ca7fd937e28e228caf58c414d4385e5e868b1078507a7c01bf838b5e8af9a7f |
| agents/mlagentbench/config.yaml | 85806153b3c25d42a1b2ab96ee93054766f08b60eea52b05e8254568250c9205 |

The task `config.yaml` and `description.md` files under `biomlbench/tasks/` were read for each of the 20 in-scope tasks (grader name, Polaris main metric, ProteinGym fold columns). Their hashes are covered by the archive hash.

No official leaderboard or results file exists in the repository at this commit; see research.md.
