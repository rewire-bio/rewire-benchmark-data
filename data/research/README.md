# Research evidence inputs

`manifests.json` describes verified evidence for specific dataset/evaluation pairs. It records exact artifact hashes, original identifiers, metric definitions, source catalogue releases, exposure, limitations and allowed local recipes. A successful source audit alone does not make a dataset ready for research.

`investigations.json` contains only reports that have received explicit human review. It is initially empty. Worker output belongs in ignored `workbench/research-imports/`; staging a report does not publish it or change its review status.

These files add versioned research sidecars to a new catalogue release. They do not replace scientific records or rewrite historical releases. A manifest's source release can precede the release containing the manifest.

## Preparing the initial evidence

The four seed manifests are produced by `scripts/prepare-research-seeds.py` in the sibling `rewire-benchmarks` repository. The script checks the preserved MFASS v2, ProteinGym AMFR, mRNABench Sample designed and FLIP2 Rhomax results. It requires the original local artifacts; re-preparing a dataset can change opaque identifiers and is not a substitute.

Only copy the resulting `manifests.json` here. Keep normalized observation tables, original prepared data, private path resolvers and execution logs in the runner's ignored workspace. A null artifact URI means that the exact artifact must be supplied through a private resolver; it is not publicly downloadable from this catalogue. Hashes establish identity, not redistribution permission.

Investigation execution (the research runner, its budgets and operations) lives in the sibling `rewire-benchmarks` repository.

## Staging and review

From this repository, stage a worker bundle against its original source catalogue and private artifact resolver:

```sh
npx tsx scripts/omics/research-import.ts \
  /absolute/path/to/bundle.json \
  /absolute/path/to/manifests.json \
  /absolute/path/to/source-catalogue.json \
  /absolute/path/to/resolver.private.json
```

The importer verifies identities, artifact bytes, frozen plans, operation lineage, numerical receipt hashes and metric definitions. It writes only to ignored `workbench/research-imports/<report-id>`. Receipt integrity is not independent recomputation or scientific review.

A reviewer must inspect all attempts, failed explanations, denominators, code and numerical evidence. Unsupported biological interpretations must be removed or qualified. Version 1 accepts exploratory findings only. Supporting a future independent-validation claim will require a separate contract linking unexposed validation evidence, overlap checks and its execution receipts. Human review cannot turn an exposed test set into independent validation.

After explicit review, a curator can add the report to `data/research/investigations.json` with human review metadata. The release builder rejects pending reports. Generating a local release is separate from publishing the site.
