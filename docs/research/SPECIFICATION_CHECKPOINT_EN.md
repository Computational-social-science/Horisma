# Horisma specification checkpoint

2026-11-04; contract version 0.1.0. This records a documentation/contract review, not scientific acceptance, production validation, operational deployment or formal proof.

This earlier specification checkpoint is followed by the [P0 engineering freeze and scholarly-claim pilot](P0_EVIDENCE_CONTRACT_EN.md). The base dictionary remains 0.1.0; that intake profile has its own version and preserves the distinctions below.

## Deliverables and ownership

The [project structure](../architecture/PROJECT_STRUCTURE_EN.md) separates research documents, specifications, private data, derived outputs, future implementation and legacy material. Original root document names are compatibility entries. Horisma files remain under `E:/2026-AI4S/Horisma`; EIDOS was inspected read-only as an external operational reuse candidate.

The [English data dictionary](../data-dictionary/Horisma_Project_Data_Dictionary_EN.md) defines 55 logical entities, 271 entity-specific fields and 12 inherited common fields. [Vocabularies](../../spec/controlled_vocabularies.yaml) define 41 code domains. The [logic catalogue](../../spec/logic_catalog.yaml) contains 41 obligations, all unproved. [Operator contracts](../../spec/operator_catalog.yaml) define 23 primitives and six composites; all Horisma integrations remain unqualified. [Sixty synthetic scenarios](../../spec/examples/data_dictionary_examples.yaml) specify expected semantic outcomes; they are partial projections, not executable production tests or research gold.

The [project skill](../../.agents/skills/horisma-research-contracts/SKILL.md) reuses these canonical authorities. It passed the bundled skill syntax/scaffold check. An independent read-only request simulation exercised paywall supply, model self-rating, execution success, credit comparability, EIDOS-path writes, stale approval, PDF release and false proof claims. That simulation exposed the transcription-fidelity gap; a distinct review field, operator, L36 and positive/negative scenarios now specify its remedy. This is limited behavioral evidence, not model qualification.

## Checks performed

Private document-assembly/check tools ran with Python 3.14.3 and PyYAML 6.0.3. They are retained under `.rebuild/authoring`, not shipped as production record validators.

- YAML parsed with duplicate mapping keys rejected; catalogue IDs and referenced fields, entities, vocabularies, rules, components and transition targets were checked.
- Registered logic obligations have synthetic scenario references. Those checks establish reference coverage, not correct execution of every scenario or completeness of the science.
- Canonical Markdown/skill links and code fences were checked; candidate/private payload ignore rules were inspected.
- Repeated specification assembly was checked with writes intercepted; duplicated refinement entries were repaired. Module-global checker state is reset for repeated invocation.
- The retained original inventory is pinned by an independent local digest/count receipt; deleting missing entries cannot legitimately clear availability. Original Git deletion paths remain deleted, apart from the intentionally new clean-rebuild .gitignore.

The latest static consistency check reports zero static errors and three source-availability issues. The checker uses a separate nonzero outcome for source gaps; there is no overall all-green research/pipeline result. Local check receipts and hashes are retained under `.rebuild`; they do not provide a public release or proof certificate.

## Material source limitation

The original inventory records 625 candidate files. Later checking found 622 byte-identical and three missing Wikipedia PDFs: Matthew effect, Harriet Zuckerman and Robert K. Merton. [Availability observations](../../legacy/material_availability.json) retain prior hashes and an unestablished cause. Missing entries were not removed from the baseline. The separately downloaded revision-bound HTML remains an unverified tertiary candidate; it does not replace primary-source evidence or restore missing PDF bytes.

## Next gate

Review/freeze the evidence and adjudication subset, then start P0: a bounded source manifest, lawful human requests where needed, 20–30 candidate atomic claims and independent human annotations. Implement executable schemas and the smallest offline English evidence-to-book slice only against that contract. Benchmark/study fields remain proposed or protocol-dependent, with no invented sample sizes, effects, approvals or validation claims. [Acceptance plan](Horisma_Implementation_Acceptance_Plan_EN.md).
