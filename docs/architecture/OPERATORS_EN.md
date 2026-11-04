# Horisma reusable operator architecture

Version 0.1.0; 2026-11-04. The [catalogue](../../spec/operator_catalog.yaml) specifies 23 primitive and six composite operators. None is a qualified Horisma implementation yet. Existing EIDOS providers are reuse candidates, not deployed Horisma integrations.

## One capability, one explicit contract

Common functions become reusable operators: source acquisition, document identity, extraction, passage anchoring, temporal normalization, concept resolution, taxonomy mapping, contribution extraction, evidence assessment, adjudication, profile projection, portrait candidates, book rendering, localization, rights review, freshness, metrics, release checks, formal review, owned execution, project receipts and defect-feedback export.

Each operator has a stable ID/version, typed input/output entities, prerequisite/result rules, execution mode, resource class, complete input/configuration bindings, idempotency/cache rules, typed failures and retry limits. Use the [data dictionary](../data-dictionary/Horisma_Project_Data_Dictionary_EN.md) for field semantics. Repeated functions belong here before a second independent implementation is introduced. A new operator needs a consumer and a bounded purpose; a helper function need not become a service or an autonomous agent.

The six domain operators compose primitives. Their catalogue lists reusable components, not a deployed schedule or a complete dataflow DAG. At implementation, explicitly bind component inputs, versions and dependency ordering; reject missing/ambiguous outputs. `Automated_Review_Operator` produces check reports and release candidates; human authority remains separate. Model proposals cannot manufacture human identity, rights permission, approval or gold.

Identity review must establish the claimed work/version before passage support is admitted. Extraction requires operation-specific local processing permission. A rights review must inspect the source/license/permission basis, not infer permission from availability. Rendering and translation take only explicitly selected immutable inputs and preserve all claim modes and limitations.

The transcription-review primitive compares extracted/OCR wording with the original source image/text and binds the reviewed region, source and derivative versions. Preserve raw extraction and corrected derivatives. Multiple assessors reading the same corrupted OCR do not independently establish wording fidelity; transcription review and historical adjudication are separate gates.

## Efficient execution without scientific shortcuts

Prefer pure in-process functions and batches for deterministic work. Reuse exact extracted text and indexes rather than reparsing for each language/consumer. Cache keys bind operator/code/configuration versions, exact input bytes, model/weights/tokenizer/quantization, prompt/workflow, locale, seed and nondeterminism policy. Identical filenames or term strings do not authorize cache reuse. Stochastic outputs keep separate attempts; human decisions are never fabricated from cache.

Use an owned subprocess only when isolation, deadlines, incompatible dependencies or GPU ownership justify it. One active exclusive GPU lease prevents competing inference/image workers from overcommitting the device. A subprocess exit is an operational observation; evidence support and approval remain separate. Retries are bounded, retain all attempts and require verified closure of earlier owned work. Do not claim exactly-once execution.

Qualify efficiency with measured latency, throughput, peak memory and cache hits on fixed inputs at fixed quality/abstention requirements. An operator contract, local installation or small parameter count is not performance evidence. Hardware/model inventories must be measured before operational promises.

## Runtime policy and failure routing

Inference, translation, images and model judging must use controlled local, appropriately licensed open resources without a proprietary/paid API dependency. A missing local capability fails explicitly or creates a human task; free-tier credits and hosted fallbacks are not substitutes. Public source retrieval is a distinct lawful allowlisted activity. A blocked PDF produces a human-source request, releases its lease and preserves dependent claims for resumption. Manual supply re-enters identity and operation-specific rights checks.

All scientific outputs, logs, caches, temporary files and exports remain inside Horisma or a separately declared Horisma state root. An SDK may read installed EIDOS code; it may not store Horisma science under an EIDOS checkout/state directory. A shared future dashboard consumes scoped operational projections, not shared scientific storage.

Operational self-check/self-heal may detect missing inputs, stale bindings and failed ownership, then restart/requeue/restore only under approved bounds. It may not edit accepted findings, lower evidence thresholds, change models/policies or approve publication to clear an alarm.

## Implementation order

P0 freezes the bounded Matthew Effect source/claim/reviewer contract. P1 implements and checks the smallest offline source-to-reviewed-English-book composition. P2 qualifies existing local models. P3 tests ownership, recovery and a 24-hour shadow run. All other languages, benchmark claims and human experiments retain their separate gates. [Implementation plan](../research/Horisma_Implementation_Acceptance_Plan_EN.md).
