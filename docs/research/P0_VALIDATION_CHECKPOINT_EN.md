# P0 validation and clean-repository checkpoint

2026-11-04. These are engineering observations, not scientific approval, a historical gold corpus or formal proofs.

## Evidence intake

The P0 schema/binding check accepts the current 28-candidate scholarly-source projection across four exact PDF versions. All 28 assessments remain unassessed, all transcription reviews pending, and zero human annotations are complete. Two inaccessible sources have explicit human-discovery requests. The Wikipedia reference index has 42 citation instances and 39 proposed work groups; it supplies discovery rather than default claim evidence. [Contract and limits](P0_EVIDENCE_CONTRACT_EN.md).

The local P0 tests now cover 34 synthetic cases. They exercise frozen-file mutations, source/acquisition/draft/offset mismatches, scientific-status promotion, invalid model output, external redirects, Unicode, undefined numerical quantities, model provenance, tiny positive label costs, citation collisions and unresolved reference IDs. These checks do not establish original-page fidelity, semantic support, real-document retrieval quality or L37 processing permission.

## PFLM assembly and measured boundary

The optional installed code and local weights match pinned identities; loading uses local safetensors and CPU float32. The actual parameter count is 294,908,512. A 32-byte repeating synthetic stream took 0.322 seconds to score after a 12.12-second load in the observed run. Its mean prediction cost was about 0.9071 bits/byte. Chunk sizes 32 versus 8 differed by at most 9.54e-7 bits per byte. These tiny synthetic timings are not document-scale throughput or OCR results.

| Synthetic attribution-pattern setup | Eligible held-out cases | PFLM correct | Literal rule correct |
|---|---:|---:|---:|
| Three examples; label frequencies unbalanced | 4 | 1 | 4 |
| Four examples; label frequencies balanced | 4 | 1 | 4 |

Both setups use fictional short statements and the same four held-out strings. This exploratory repetition is not an independent test set or evidence that all PFLM configurations fail. It gives no basis to promote the present setup to automatic filtering. No real scholarly-paragraph recall, false-exclusion rate or reference entailment result is claimed. [Balanced synthetic receipt](../validation/pflm_cpu_balanced_v2.json).

Single-byte label alternatives share one context evaluation and use float64 shifted-logit/log1p costs; ties stay unresolved. Raw scores remain uncalibrated. This numerical improvement does not repair semantic errors or permit source changes. [Extension design](../architecture/PFLM_LOCAL_OPERATOR_EN.md).

## Clean GitHub reconstruction

The user deleted the former remote repository and explicitly requested a rebuild. The new [Horisma repository](https://github.com/Computational-social-science/Horisma) started with a fresh root commit, without importing the old runtime or Git history. Local legacy Git metadata is retained under `.rebuild/legacy-git-20261104`; source/data files were not deleted by metadata adoption. Private PDFs, source text, real model drafts and unadjudicated evidence remain outside the public technical export.

The initial source-only commit passed [GitHub Actions](https://github.com/Computational-social-science/Horisma/actions/runs/41811815621) with 21 tests. Later extension tests run through the same pinned workflow. Frozen artifacts are stored without automatic Git newline conversion; all eight Git blobs match their freeze digests. See the latest Actions run for the current commit's status.

Next acceptance: independent source/rights/transcription/adjudication review of the core naming, contribution and authorship cases, then a held-out real-paragraph/citation-link comparison before enabling model-based filtering or the reviewed English book materializer.
