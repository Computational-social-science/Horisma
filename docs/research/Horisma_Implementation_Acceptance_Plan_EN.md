# Horisma implementation entry plan

**Status:** planned; follows review of the [clean-rebuild proposal](Horisma_Terminological_Provenance_Project_Research_Proposal_EN.md).  
**Workspace owner:** Horisma, `E:/2026-AI4S/Horisma`. No Horisma files or state belong in an EIDOS directory.

## P0 — Evidence contract before operator implementation

Current checkpoint: the [P0 engineering contract](P0_EVIDENCE_CONTRACT_EN.md) is frozen by exact digest. The local pilot contains 28 unassessed scholarly-source candidates from four versions, a discovery bibliography, two human-source requests and unfilled independent-review templates. This is candidate preparation, not a passed scientific/rights/transcription acceptance gate.

Specification checkpoint 0.1.0 now supplies the [canonical data dictionary](../data-dictionary/Horisma_Project_Data_Dictionary_EN.md), [vocabularies](../../spec/controlled_vocabularies.yaml), [logic obligations](../../spec/logic_catalog.yaml), [operator contracts](../../spec/operator_catalog.yaml), [synthetic scenarios](../../spec/examples/data_dictionary_examples.yaml) and [formalization conventions](../methods/FORMALIZATION_EN.md). These remain drafts for owner review; they are not executable validators, deployed integrations, accepted historical labels or proofs. Freeze the evidence/adjudication subset first; later benchmark/study variables retain proposed/protocol-dependent status.

Deliver a small source inventory and schemas for source versions, passages, atomic claims, contribution roles, adjudications and human-source requests. Define document dates separately from asserted event dates. Select approximately 20–30 candidate Matthew Effect claims, including contradictions and unresolved cases. Candidate count is a planning bound, not a statistical sample-size claim.

Use the [preferred Wikipedia intake](MATTHEW_EFFECT_INTAKE_EN.md) for initial term/person/reference discovery; candidate claims chiefly come from scholarly body passages. Independently verify primary documents before adjudicating. Reuse common primitives from the catalogue before introducing parallel implementations. Every implemented primitive must bind its field/rule versions and positive/negative controls; efficiency claims require measurements at the same quality boundary.

Acceptance:

- Each included document has a stable identity, content digest, acquisition record and rights status.
- A passage is independently locatable by printed/PDF page or stable offsets.
- Naming, discovery, presentation, publication and credit assertions are not interchangeable.
- Missing or paywalled PDFs create `WAITING_HUMAN_SOURCE` records. Nothing infers unseen passages or repeatedly attempts circumvention.
- The old corpus and generated text cannot silently become accepted claims or gold labels.
- Null/missing reasons, five completed assessment labels and separate source/evidence/review/execution domains retain their dictionary meanings.
- Role/scope comparability alone is insufficient: a supported discrepancy needs a stated credit incompatibility and independent human review.
- Accepted scientific findings and formal proof status cannot be manufactured by successful execution, syntax checks or finite synthetic examples.

## P1 — One offline evidence-to-book slice

Implement deterministic schema/support checks, a minimal claim/adjudication ledger, a human-source inbox and one English book materializer. Use the six interfaces defined in the proposal without requiring six mature services. Verify HTML, PDF and EPUB separately. Record unresolved issues and obtain editorial approval of the exact release bundle.

Acceptance includes deliberately wrong DOI/passages, invalid locators, contradictory sources, missing rights, changed input digests and absent reviewer approval. Every negative control must produce the specified refusal rather than merely crash for an unrelated reason.

## P2 — Qualify existing local resources

Inventory actual local model/backends, licenses and host resources without downloading new models by default. Use a project-qualified interpreter or isolated backend. Set loopback-only inference routing, offline evidence indexes, one GPU lease, bounded context/output and no hosted fallback. Report quality, abstention, latency and memory on the pilot. Human adjudication remains independent.

Require zero calls to paid/proprietary inference, translation, image or judging APIs. External service absence must not create a silent mode change. Electricity and necessary human work remain explicit resource requirements.

## P3 — Operational shadow acceptance

Only after the pilot succeeds, qualify a single supervisor and transactional task queue. Use Horisma-owned state and logs; if a separate NVMe state root is needed, declare it explicitly. Reuse EIDOS through a pinned installed SDK and a narrow adapter, not source-tree coupling or shared scientific state.

Run crash/restart, timeout/cancellation, duplicate worker, expired lease, interrupted publication, model unavailability, network failure, paywall, GPU contention and backup/restore controls. Accepted research records must remain unchanged. Complete a recorded 24-hour shadow soak before unattended promotion. Operational recovery must not approve findings or upgrade models/policies.

## P4 — Additional language and benchmark

Qualify one additional language with a bilingual reviewer. Freeze independently adjudicated evaluation data and concept-family splits; compare local models with retrieval/rule baselines. Keep generation, gold annotation and model judging independent. Publish uncertainty and justified abstention. Remaining UN-language lanes stay draft until their own gates pass.

## P5 — Confirmatory behavioural research

Complete the novelty review, ethics determination, preregistration and simulation-based sample-size plan. Use ethically admissible controlled vignettes for the proposed prestige-cue/provenance-format estimand. Public portal reactions remain descriptive. Select the paper venue from the demonstrated contribution; NHB remains an ambition.

## Definition of implementation readiness

Proceed from design to P0 when the research/editorial owner, source set and adjudication rules are agreed. No service, scheduler, source download, model installation, participant recruitment or public deployment is represented as completed by this document.
