# Horisma project data dictionary

**Dictionary version:**0.1.0. **Date:**2026-11-04. **Status:** DRAFT_COMPLETE_FOR_REVIEW.
Workspace: `E:/2026-AI4S/Horisma`. This is a scientific specification, not an implemented database, validator, operator service or proof.

## Authority and interpretation

This document owns research semantics and field meanings. [Controlled vocabularies](../../spec/controlled_vocabularies.yaml) own machine codes and their meanings. [Logic catalogue](../../spec/logic_catalog.yaml) owns stable logical obligations; [operator catalogue](../../spec/operator_catalog.yaml) owns reusable capability/composition contracts. [Synthetic examples](../../spec/examples/data_dictionary_examples.yaml) specify expected conformance outcomes, not historical findings or executable tests. Changes must synchronize the same version across these files.

Canonical bodies are under docs; root filenames are compatibility links. Do not store Horisma research/state in an EIDOS directory or import the old Horisma labels. Raw source identity, passage support, adjudication/release and execution each have separate status vocabularies. No universal PASS field is defined.

Concept/form/sense/family are different objects. Historical contributor, operational actor and pseudonymous participant are different roles. Naming, discovery, authorship, empirical contribution and popularization are not interchangeable. An attribution discrepancy is a policy-relative comparison, not evidence of intent, theft or legal ownership.

### Epistemic layers

1. Preserve exact source bytes, document versions and passages.
2. Record what an identified source says, using atomic scoped propositions.
3. Independently assess passage relations and claim support under versioned policies.
4. Derive a same-concept/role/scope discrepancy finding with its explicit comparison norm.
5. Present approved findings, qualified accounts and open questions as different publication modes.

Support/contradiction may coexist as evidence relations without asserting both an object-world proposition and its negation. Unknown is not false. A schema- or example-conforming record does not prove historical truth. Empirical hypotheses are not logical axioms. All catalogue proof obligations remain UNPROVEN at this checkpoint.

## Common field contract (inherited by every entity below)

Each field introduced here is version0.1.0. Each entity header fixes its owner/reviewer, grain, disclosure default and definition stage. Each row supplies the remaining field-specific metadata. Inheritance is normative: these are not omitted decisions.

| Field | Type; cardinality; obligation | Meaning and examples | Missing/provenance/disclosure |
|---|---|---|---|
| entity_id | opaque `<entity_type>:<uuid4>`;1;required | Persistent entity identity; not a person's name or a date | Never missing; created by project registry; INTERNAL |
| record_id | opaque `record:<uuid4>`;1;required | Immutable version identity; references bind this value | Never missing; registry; inherits entity class |
| record_version | integer>=1;1;required | Monotonic version within an entity; not evidence strength | Never missing; registry |
| supersedes_record_id | exact RecordRef;0..1;optional | Earlier version, retaining its history; self/cycles invalid | First version uses null/NOT_APPLICABLE |
| dictionary_version | string;1;required |0.1.0 for these contracts; no silent legacy coercion | Never missing; declared contract |
| vocabulary_version | string;1;required | Exact catalogue version, not a floating latest label | Never missing; catalogue |
| record_status | enum:record_status;1;required | ACTIVE means current, not true or approved | Never missing; lifecycle event |
| created_at | UTC datetime;1;required | Actual recording instant, not historical event time | Never missing; system observation |
| created_by_actor_ref | exact actor RecordRef;1;required | Identifies human/software/model origin | Never missing; authorization registry |
| disclosure_class | enum:disclosure_class;1;required | May tighten inherited class; relaxing needs a rights/privacy decision | Never missing; reviewed policy |
| missing_reasons | field-path -> enum:missing_reason;0..n;required map | Maps null/omitted values to reasons; no -999/empty-string sentinels | Known complete records use an empty map; INTERNAL |
| provenance_artifact_refs | Artifact RecordRef list;0..n;required list | Exact source/processing/annotation receipts; model prose not independent evidence | Empty is explicitly absent, not proof of completeness |

**Requiredness:** R requires a non-null value; O permits null with an applicable reason; C requires a non-null value when the stated condition holds, and is otherwise optional unless its definition explicitly forbids a value. Pending proof attempts may retain actual proof/toolchain artifacts without claiming acceptance. A metric value, by contrast, is present only when its measurement status is defined. Missing optional keys must be represented in missing_reasons before interchange. Lists use0..n unless required, which requires1..n. Scalar/ref cardinality is1 when required and0..1 otherwise. Required maps may be empty only when their definition permits it.

**Universal scalar rules:** integers/numbers must be finite, with declared range and unit. Fraction is [0,1]. No guessed default dates, confidence values or demographics. Every nullable field has null plus a missing reason; zero/false/known-empty are genuine observations. Exact file hashes are SHA256 over file bytes; they do not establish document identity. An opaque reference is not a path. Reference examples using @name are explanatory symbols, not production IDs.

Missingness applies only to fields belonging to the record's type and to nested members whose parent structure is present. A null structured parent has one reason at the parent path; descendants are absent and require no separate reasons. An actor record does not carry missingness entries for unrelated metric fields. Conditional fields require their stated receipts before accepted statuses, even when pending attempts legitimately retain nulls.

**Provenance/reviewer inheritance:** observed source fields need a bound document/passage; human judgment fields need annotation/policy/reviewer records; derived values need their definition and input versions; operational values need actual logs/measurements. The entity reviewer is responsible for field interpretation; the source/actor establishing a value must still be recorded. Unit defaults are dimensionless for Boolean/enum/ref, not-applicable for text/path, and explicitly stated for quantities. No automatic default numeric value is supplied.

## Structured value types

All nested members below are fields introduced in0.1.0 and inherit null/provenance/disclosure rules. They are logical value types, not implemented JSON Schemas.

| Type | Members and precise interpretation | Positive/negative boundary |
|---|---|---|
| TemporalExtent | original_text:text; calendar_system:enum; precision:enum; normalized_lower/upper:date-or-null; normalization_artifact_ref:ArtifactRef-or-null. Bounds are inclusive calendar dates and derived possibilities, never observations of a particular day. Normalize only when calendar conversion is established. | A YEAR extent may spanJan1–Dec31 while retaining YEAR; claimingJan1 as observed is invalid. Incomparable/missing bounds yield no before/after conclusion. |
| PassageLocator | anchor_kind:enum:passage_anchor_kind; printed_page:text-or-null; pdf_page_index:integer>=0-or-null; derivative_artifact_ref:ArtifactRef-or-null; start_offset/end_offset:integer-or-null; region:[x0,y0,x1,y1]-or-null. Text offsets are Unicode code-point positions [start,end) in exact unnormalized derivative bytes after UTF8 decode. Regions use [0,1] page coordinates, top-left origin. | Page anchors need an index and source binding; text anchors need derivative/hash and start<end; image anchors need page and0<=x0<x1<=1,0<=y0<y1<=1. No locator detached from a version. |
| IdentifierList | List of {scheme:enum:identifier_scheme,value:text,other_scheme_name:text-or-null}; other_scheme_name is required exactly for the catalogue's other-scheme code. Normalized value, if used, is a separate documented derivative. | A DOI identifies a candidate work, not a verified body passage. |
| RecordRefList | List of exact immutable record_id values; target types stated by field. | Persistent entity names alone cannot bind a review/version. |
| PublicationModeMap | Included claim_record_id -> enum:publication_mode; domain equals the edition's included claim set. | An open question remains visibly qualified; it cannot silently become an established fact. |
| CreditAllocation | List of {actor_ref:VignetteActorRef,share:fraction}; unique actors; complete responses sum to1 within1e-6 and actor domain equals the assignment's protocol-defined response_actor_refs, all within its vignette. Raw response retained separately. | Percent is divided by100 under the protocol; abstention is null with a reason, not all-zero shares. Unrelated actors invalidate even a normalized vector. |
| LogicRefList | Registered logic_id values from logic_catalog.yaml. | A referenced expression is not a verified theorem. |
| OperatorRef | Registered operator_id plus exact operator version in the run configuration. | A contract or installed provider is not a qualified Horisma integration. |

## Entity relationships and staged contracts

Core meanings are specified now. PROPOSED entities need implementation qualification; PROTOCOL_DEPENDENT entities additionally need approved sampling, analysis/ethics and measurement decisions. These markers never supply missing sample sizes, outcomes or approvals. Entity relationships may be mutually referential (e.g. work/version); scientific derivation and supersession relations must be acyclic.

### `actor`

Grain: One operational human/software/model identity, not a historical contributor.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `INTERNAL`; responsible reviewer: Project owner. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `display_label` | Operational display label; not an authority credential. | `text`; 1; R | verbatim label | not allowed; INTERNAL | Inherited provenance rule; Project owner; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L03 |
| `kind` | Distinguish human review from software/model output. | `enum`; 1; R | actor_kind | not allowed; INTERNAL | Inherited provenance rule; Project owner; definition+inputs for derivatives | a member of `actor_kind` / an unregistered code or generic PASS | L07 |
| `authorization_artifact_ref` | Evidence of assigned review/operation permissions; not self-declared authority. | `ref:artifact`; 0..1; O | exact version | null + missing_reason; INTERNAL | Inherited provenance rule; Project owner; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L17 |

### `project_protocol`

Grain: One immutable version of the project scientific contract.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `INTERNAL`; responsible reviewer: Research owner. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `research_question_refs` | Questions covered by this protocol. | `refs:research_question`; 1..n; R | exact versions | not allowed; INTERNAL | Inherited provenance rule; Research owner; definition+inputs for derivatives | `@research_question_a` (symbolic exact-version reference) / a name or current filename | L03 |
| `scope_statement` | Population, period, languages and exclusions; not universal coverage. | `text`; 1; R | bounded scope | not allowed; INTERNAL | Inherited provenance rule; Research owner; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L13 |
| `policy_refs` | Applicable adjudication policies. | `refs:adjudication_policy`; 1..n; R | exact versions | not allowed; INTERNAL | Inherited provenance rule; Research owner; definition+inputs for derivatives | `@adjudication_policy_a` (symbolic exact-version reference) / a name or current filename | L09 |
| `approval_ref` | Review of this protocol; absence is not approval. | `ref:review_decision`; 0..1; O | exact version | null + missing_reason; INTERNAL | Inherited provenance rule; Research owner; definition+inputs for derivatives | `@review_decision_a` (symbolic exact-version reference) / a name or current filename | L17 |

### `research_question`

Grain: One scoped, answerable research question.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `PUBLIC_ELIGIBLE`; responsible reviewer: Research owner. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `question_text` | Question, not a presupposed finding. | `text`; 1; R | English plus original text if applicable | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Research owner; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L29 |
| `unit_of_analysis` | Independent observational unit; distinguish claims, families and participants. | `text`; 1; R | specified unit | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Research owner; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L19 |
| `target_construct` | Construct under study and the forbidden broader interpretation. | `text`; 1; R | operational definition | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Research owner; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L09 |

### `hypothesis`

Grain: One falsifiable proposed empirical hypothesis.  
Stage: `PROTOCOL_DEPENDENT`; default disclosure: `INTERNAL`; responsible reviewer: Research owner. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `statement` | Research hypothesis; never a trusted logical axiom. | `text`; 1; R | falsifiable proposition | not allowed; INTERNAL | Inherited provenance rule; Research owner; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L29 |
| `protocol_ref` | Protocol defining scope and interpretation. | `ref:project_protocol`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Research owner; definition+inputs for derivatives | `@project_protocol_a` (symbolic exact-version reference) / a name or current filename | L03 |
| `logical_statement_ref` | Typed formal representation, if available; not proof of the hypothesis. | `ref:logical_statement`; 0..1; O | exact version | null + missing_reason; INTERNAL | Inherited provenance rule; Research owner; definition+inputs for derivatives | `@logical_statement_a` (symbolic exact-version reference) / a name or current filename | L29 |
| `falsification_condition` | Outcome that would challenge the hypothesis. | `text`; 1; R | observable test | not allowed; INTERNAL | Inherited provenance rule; Research owner; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L29 |

### `sampling_frame`

Grain: One versioned, bounded universe and sampling procedure.  
Stage: `PROTOCOL_DEPENDENT`; default disclosure: `INTERNAL`; responsible reviewer: Research owner. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `protocol_ref` | Protocol owning the frame. | `ref:project_protocol`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Research owner; definition+inputs for derivatives | `@project_protocol_a` (symbolic exact-version reference) / a name or current filename | L03 |
| `frame_manifest_ref` | Eligible units and their identifiers; not a list selected only for controversy. | `ref:artifact`; 1; R | bound manifest | not allowed; INTERNAL | Inherited provenance rule; Research owner; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L19 |
| `inclusion_exclusion_rule` | Eligibility and exclusion criteria fixed before evaluation. | `text`; 1; R | prespecified rule | not allowed; INTERNAL | Inherited provenance rule; Research owner; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L19 |
| `sampling_procedure` | Selection probabilities/strata or explicit nonprobability design. | `text`; 1; R | procedure and seed policy | not allowed; INTERNAL | Inherited provenance rule; Research owner; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L13 |

### `concept`

Grain: One meaning-bearing research concept, independent of spelling.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `PUBLIC_ELIGIBLE`; responsible reviewer: Domain adjudicator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `definition_claim_refs` | Source-grounded definition claims; a label alone does not define identity. | `refs:atomic_claim`; 1..n; R | exact versions | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | `@atomic_claim_a` (symbolic exact-version reference) / a name or current filename | L05 |
| `family_ref` | Leakage-control family, not a disciplinary code. | `ref:concept_family`; 1; R | exact version | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | `@concept_family_a` (symbolic exact-version reference) / a name or current filename | L19 |
| `scope_note` | What the concept includes/excludes; ambiguous merging is not permitted. | `text`; 1; R | sense boundaries | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L10 |

### `lexical_form`

Grain: One written form in a stated language/script.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `PUBLIC_ELIGIBLE`; responsible reviewer: Language reviewer. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `form_text` | Preserve spelling; search normalization must not replace evidence text. | `text`; 1; R | original Unicode | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Language reviewer; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L05 |
| `language_tag` | Source language, not restricted to the six publication lanes. | `language`; 1; R | source BCP47 tag | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Language reviewer; definition+inputs for derivatives | en / English nationality inferred from a name | L03 |
| `script_note` | Script/transliteration note; not a nationality inference. | `text`; 0..1; O | observed script | null + missing_reason; PUBLIC_ELIGIBLE | Inherited provenance rule; Language reviewer; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L32 |

### `sense`

Grain: One attested mapping between a form and a concept in context.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `PUBLIC_ELIGIBLE`; responsible reviewer: Domain/language reviewer. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `lexical_form_ref` | Form being interpreted. | `ref:lexical_form`; 1; R | exact version | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain/language reviewer; definition+inputs for derivatives | `@lexical_form_a` (symbolic exact-version reference) / a name or current filename | L03 |
| `concept_ref` | Concept in this usage, not all homographic meanings. | `ref:concept`; 1; R | exact version | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain/language reviewer; definition+inputs for derivatives | `@concept_a` (symbolic exact-version reference) / a name or current filename | L10 |
| `attestation_claim_refs` | Evidence of this usage/sense association. | `refs:atomic_claim`; 1..n; R | exact versions | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain/language reviewer; definition+inputs for derivatives | `@atomic_claim_a` (symbolic exact-version reference) / a name or current filename | L05 |

### `concept_family`

Grain: One declared group used to keep related cases together.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `INTERNAL`; responsible reviewer: Benchmark curator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `member_concept_refs` | Related meanings/aliases grouped for leakage control. | `refs:concept`; 1..n; R | exact versions | not allowed; INTERNAL | Inherited provenance rule; Benchmark curator; definition+inputs for derivatives | `@concept_a` (symbolic exact-version reference) / a name or current filename | L19 |
| `grouping_rationale` | Why these concepts belong together; not a discovered natural kind. | `text`; 1; R | explicit rationale | not allowed; INTERNAL | Inherited provenance rule; Benchmark curator; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L19 |
| `overlap_audit_ref` | Audit of source/person overlap across families. | `ref:artifact`; 0..1; O | bound report | null + missing_reason; INTERNAL | Inherited provenance rule; Benchmark curator; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L19 |

### `taxonomy_assignment`

Grain: One contextual mapping of a sense to a pinned classification.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `PUBLIC_ELIGIBLE`; responsible reviewer: Domain adjudicator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `sense_ref` | The attested sense/use being classified. | `ref:sense`; 1; R | exact version | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | `@sense_a` (symbolic exact-version reference) / a name or current filename | L10 |
| `scheme` | Scheme family; no universal latest-JACS assumption. | `enum`; 1; R | taxonomy_scheme | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | a member of `taxonomy_scheme` / an unregistered code or generic PASS | L03 |
| `vocabulary_artifact_ref` | Exact vocabulary release/bytes and its rights decision. | `ref:artifact`; 1; R | pinned source release | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L03 |
| `code` | Actual code; null UNKNOWN is preferable to a guessed code. | `text`; 0..1; O | code in pinned vocabulary | null + missing_reason; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L02 |
| `context_time` | Context of assignment; modern labels are not timeless identities. | `TemporalExtent`; 0..1; O | historical time | null + missing_reason; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | year1964 with YEAR precision / 1964-01-01 asserted as an observed day | L12 |
| `mapping_evidence_refs` | Evidence and interpretation supporting the mapping. | `refs:atomic_claim`; 1..n; R | exact versions | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | `@atomic_claim_a` (symbolic exact-version reference) / a name or current filename | L05 |

### `contributor`

Grain: One historical person, organization or collective identity.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `PUBLIC_ELIGIBLE`; responsible reviewer: Domain adjudicator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `kind` | Entity kind; unknown is not automatically a person. | `enum`; 1; R | contributor_kind | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | a member of `contributor_kind` / an unregistered code or generic PASS | L32 |
| `display_name` | Name for presentation, not a merge key or proof of identity. | `text`; 1; R | source-attested name | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L03 |
| `identifier_values` | ORCID/other identifiers if actually established. | `IdentifierList`; 0..n; O | source identifiers | null + missing_reason; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | documented DOI and its scheme / a guessed DOI as authenticated evidence | L05 |
| `identity_assertion_refs` | Dated sourced biography; no inference from portraits/flags. | `refs:identity_assertion`; 0..n; O | exact versions | null + missing_reason; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | `@identity_assertion_a` (symbolic exact-version reference) / a name or current filename | L32 |

### `identity_assertion`

Grain: One sourced biographical assertion, with time and scope.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `RESTRICTED`; responsible reviewer: Domain/privacy reviewer. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `contributor_ref` | Person/organization described. | `ref:contributor`; 1; R | exact version | not allowed; RESTRICTED | Inherited provenance rule; Domain/privacy reviewer; definition+inputs for derivatives | `@contributor_a` (symbolic exact-version reference) / a name or current filename | L03 |
| `attribute_name` | For example birth event, citizenship or affiliation; these are different constructs. | `text`; 1; R | specified attribute | not allowed; RESTRICTED | Inherited provenance rule; Domain/privacy reviewer; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L32 |
| `asserted_value` | Preserve uncertainty; do not infer gender, nationality or death from a name. | `text`; 0..1; O | source-attested value | null + missing_reason; RESTRICTED | Inherited provenance rule; Domain/privacy reviewer; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L32 |
| `valid_time` | Time to which the assertion applies. | `TemporalExtent`; 0..1; O | historical time | null + missing_reason; RESTRICTED | Inherited provenance rule; Domain/privacy reviewer; definition+inputs for derivatives | year1964 with YEAR precision / 1964-01-01 asserted as an observed day | L12 |
| `evidence_refs` | Support for this particular attribute. | `refs:evidence_link`; 1..n; R | exact versions | not allowed; RESTRICTED | Inherited provenance rule; Domain/privacy reviewer; definition+inputs for derivatives | `@evidence_link_a` (symbolic exact-version reference) / a name or current filename | L05 |

### `contribution_assertion`

Grain: One claim that an entity performed a specified role.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `PUBLIC_ELIGIBLE`; responsible reviewer: Domain adjudicator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `contributor_ref` | Contributor, distinct from the author reporting the attribution. | `ref:contributor`; 1; R | exact version | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | `@contributor_a` (symbolic exact-version reference) / a name or current filename | L03 |
| `concept_ref` | Referent/sense within which the role is asserted. | `ref:concept`; 1; R | exact version | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | `@concept_a` (symbolic exact-version reference) / a name or current filename | L10 |
| `role` | Naming, discovery, evidence and popularization remain distinct. | `enum`; 1; R | contribution_role | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | a member of `contribution_role` / an unregistered code or generic PASS | L10 |
| `event_kind` | Scheduled presentation is not actual delivery. | `enum`; 1; R | historical_event_kind | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | a member of `historical_event_kind` / an unregistered code or generic PASS | L14 |
| `event_time` | Claimed event date, not file retrieval time. | `TemporalExtent`; 0..1; O | historical time | null + missing_reason; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | year1964 with YEAR precision / 1964-01-01 asserted as an observed day | L12 |
| `claim_ref` | Atomic proposition whose evidence is assessed. | `ref:atomic_claim`; 1; R | exact version | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | `@atomic_claim_a` (symbolic exact-version reference) / a name or current filename | L05 |

### `work`

Grain: One bibliographic intellectual work, distinct from its versions/files.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `PUBLIC_ELIGIBLE`; responsible reviewer: Source curator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `title` | Transcribe title; title tokens do not support body claims. | `text`; 1; R | source title | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Source curator; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L06 |
| `author_contributor_refs` | Bibliographic authorship, not naming priority. | `refs:contributor`; 0..n; O | exact versions | null + missing_reason; PUBLIC_ELIGIBLE | Inherited provenance rule; Source curator; definition+inputs for derivatives | `@contributor_a` (symbolic exact-version reference) / a name or current filename | L10 |
| `identifiers` | DOI/ISBN/URI identify works; they do not prove relevance. | `IdentifierList`; 0..n; O | documented identifiers | null + missing_reason; PUBLIC_ELIGIBLE | Inherited provenance rule; Source curator; definition+inputs for derivatives | documented DOI and its scheme / a guessed DOI as authenticated evidence | L05 |
| `source_kind` | Wikipedia is a preferred tertiary seed, not primary adjudication. | `enum`; 1; R | source_kind | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Source curator; definition+inputs for derivatives | a member of `source_kind` / an unregistered code or generic PASS | L01 |

### `document_version`

Grain: One identified edition/revision of a work.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `INTERNAL`; responsible reviewer: Source curator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `work_ref` | Parent work identity. | `ref:work`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | `@work_a` (symbolic exact-version reference) / a name or current filename | L03 |
| `version_label` | Revision, edition or stated unknown; never silently current. | `text`; 1; R | edition/revision | not allowed; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L03 |
| `identity_status` | Document/version identity verification, not passage support. | `enum`; 1; R | source_identity_status | not allowed; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | a member of `source_identity_status` / an unregistered code or generic PASS | L05 |
| `identity_review_ref` | Required evidence for a VERIFIED identity status. | `ref:review_decision`; 1 when condition; else 0..1; C:identity_status=VERIFIED | exact version | null + missing_reason; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | `@review_decision_a` (symbolic exact-version reference) / a name or current filename | L05 |
| `publication_time` | Publication date, distinct from events described in the text. | `TemporalExtent`; 0..1; O | historical date | null + missing_reason; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | year1964 with YEAR precision / 1964-01-01 asserted as an observed day | L12 |
| `permanent_uri` | For Wikipedia prefer oldid; preserve original requested URL separately. | `uri`; 0..1; O | uncredentialed URI | null + missing_reason; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | https://example.org/source / URL containing a password | L03 |

### `source_file`

Grain: One exact set of locally acquired source bytes.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `RESTRICTED`; responsible reviewer: Source/rights curator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `document_version_ref` | Version the bytes claim to represent. | `ref:document_version`; 1; R | exact version | not allowed; RESTRICTED | Inherited provenance rule; Source/rights curator; definition+inputs for derivatives | `@document_version_a` (symbolic exact-version reference) / a name or current filename | L03 |
| `relative_path` | Never an EIDOS state path or a publication permission. | `path`; 1; R | workspace-relative private path | not allowed; RESTRICTED | Inherited provenance rule; Source/rights curator; definition+inputs for derivatives | data/intake/example.pdf / ../Eidos/outputs/private.pdf | L27 |
| `sha256` | Content hash, not identity or scientific authentication. | `sha256`; 1; R | SHA256 of exact bytes | not allowed; RESTRICTED | Inherited provenance rule; Source/rights curator; definition+inputs for derivatives | a 64-character lowercase hex digest of actual bytes / invented digest or model confidence | L05 |
| `byte_count` | Observed file length; empty files are not usable PDFs. | `integer`; 1; R | bytes; >=0 | not allowed; RESTRICTED | Inherited provenance rule; Source/rights curator; definition+inputs for derivatives | 0 when actually observed and allowed / -999 as missing sentinel | L05 |
| `rights_decision_refs` | Separate local-processing and redistribution decisions. | `refs:rights_decision`; 0..n; O | exact versions | null + missing_reason; RESTRICTED | Inherited provenance rule; Source/rights curator; definition+inputs for derivatives | `@rights_decision_a` (symbolic exact-version reference) / a name or current filename | L16 |
| `artifact_ref` | Source-file and artifact wrappers must bind identical bytes/digest and resolved payload path, enabling operation-specific rights review. | `ref:artifact`; 1; R | same exact payload | not allowed; RESTRICTED | Inherited provenance rule; Source/rights curator; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L37 |

### `acquisition_attempt`

Grain: One bounded attempt to obtain a document/version.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `INTERNAL`; responsible reviewer: Source curator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `document_version_ref` | Requested document, not a guessed replacement. | `ref:document_version`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | `@document_version_a` (symbolic exact-version reference) / a name or current filename | L03 |
| `requested_uri` | Lawful endpoint or source location. | `uri`; 0..1; O | no credentials | null + missing_reason; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | https://example.org/source / URL containing a password | L15 |
| `access_status` | HTTP200/local presence is not identity or rights verification. | `enum`; 1; R | source_access_status | not allowed; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | a member of `source_access_status` / an unregistered code or generic PASS | L16 |
| `failure_kind` | Paywall, access denial and transient network failure are distinct. | `enum`; 0..1; O | failure_kind | null + missing_reason; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | a member of `failure_kind` / an unregistered code or generic PASS | L15 |
| `source_file_ref` | Actual acquired bytes if any; no fabricated extract. | `ref:source_file`; 0..1; O | exact version | null + missing_reason; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | `@source_file_a` (symbolic exact-version reference) / a name or current filename | L05 |

### `human_source_request`

Grain: One dependency handed to a person for lawful source access.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `INTERNAL`; responsible reviewer: Source curator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `document_version_ref` | Work/version metadata supplied to the person. | `ref:document_version`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | `@document_version_a` (symbolic exact-version reference) / a name or current filename | L15 |
| `dependent_claim_refs` | Claims blocked by this source dependency. | `refs:atomic_claim`; 1..n; R | exact versions | not allowed; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | `@atomic_claim_a` (symbolic exact-version reference) / a name or current filename | L15 |
| `failure_kind` | Reason for handoff, not automatic evidence of a paywall. | `enum`; 1; R | failure_kind | not allowed; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | a member of `failure_kind` / an unregistered code or generic PASS | L15 |
| `requested_locators` | Why the source is needed and which pages/questions matter. | `text`; 1; R | pages/questions | not allowed; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L15 |
| `inbox_relative_path` | Local deposit destination, never public Git or an EIDOS directory. | `path`; 1; R | private Horisma intake path | not allowed; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | data/intake/example.pdf / ../Eidos/outputs/private.pdf | L27 |
| `resume_review_refs` | Identity/version/rights checks before resumption. | `refs:review_decision`; 0..n; O | exact versions | null + missing_reason; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | `@review_decision_a` (symbolic exact-version reference) / a name or current filename | L16 |

### `passage`

Grain: One precisely locatable span/region in an identified document.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `RESTRICTED`; responsible reviewer: Source/domain reviewer. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `document_version_ref` | Document supplying the passage. | `ref:document_version`; 1; R | exact version | not allowed; RESTRICTED | Inherited provenance rule; Source/domain reviewer; definition+inputs for derivatives | `@document_version_a` (symbolic exact-version reference) / a name or current filename | L05 |
| `source_file_ref` | Local snapshot or admitted extract binding. | `ref:source_file`; 1; R | exact bytes | not allowed; RESTRICTED | Inherited provenance rule; Source/domain reviewer; definition+inputs for derivatives | `@source_file_a` (symbolic exact-version reference) / a name or current filename | L05 |
| `locator` | Printed page/PDF index or exact derivative offsets/region. | `PassageLocator`; 1; R | position in bound artifact | not allowed; RESTRICTED | Inherited provenance rule; Source/domain reviewer; definition+inputs for derivatives | PDF page index0 bound to a source digest / page number without document version | L05 |
| `original_text` | Withhold when rights require; never replace original with translation. | `text`; 0..1; O | verbatim source text | null + missing_reason; RESTRICTED | Inherited provenance rule; Source/domain reviewer; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L16 |
| `language_tag` | Language of the original passage. | `language`; 1; R | source language | not allowed; RESTRICTED | Inherited provenance rule; Source/domain reviewer; definition+inputs for derivatives | en / English nationality inferred from a name | L05 |
| `transcription_review_ref` | Independent wording-fidelity review against original source image/text; preserve raw extraction and corrected versions. Historical assessors reading only the same OCR do not satisfy this check. | `ref:review_decision`; 1 when condition; else 0..1; C:extracted text used as evidence | exact source/derivative/region binding | null + missing_reason; RESTRICTED | Inherited provenance rule; Source/domain reviewer; definition+inputs for derivatives | `@review_decision_a` (symbolic exact-version reference) / a name or current filename | L36 |

### `atomic_claim`

Grain: One proposition with explicit scope, not a whole paragraph.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `INTERNAL`; responsible reviewer: Domain adjudicator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `proposition` | Retain original wording; a question or report is not an asserted fact. | `text`; 1; R | atomic proposition | not allowed; INTERNAL | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L05 |
| `concept_ref` | Concept/sense to which the proposition applies. | `ref:concept`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | `@concept_a` (symbolic exact-version reference) / a name or current filename | L10 |
| `scope_statement` | Bounded proposition; no silent universalization. | `text`; 1; R | role/time/document context | not allowed; INTERNAL | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L13 |
| `origin` | Wikipedia/legacy/model proposals do not inherit acceptance. | `enum`; 1; R | assertion_origin | not allowed; INTERNAL | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | a member of `assertion_origin` / an unregistered code or generic PASS | L01 |
| `search_scope_ref` | Mandatory for earliest/absence claims. | `ref:search_scope`; 0..1; O | exact version | null + missing_reason; INTERNAL | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | `@search_scope_a` (symbolic exact-version reference) / a name or current filename | L13 |
| `derived_from_claim_refs` | Logical/processing dependency, not independent corroboration. | `refs:atomic_claim`; 0..n; O | exact versions | null + missing_reason; INTERNAL | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | `@atomic_claim_a` (symbolic exact-version reference) / a name or current filename | L04 |
| `logical_statement_ref` | Optional formal encoding, not a proof of historical truth. | `ref:logical_statement`; 0..1; O | exact version | null + missing_reason; INTERNAL | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | `@logical_statement_a` (symbolic exact-version reference) / a name or current filename | L28 |

### `search_scope`

Grain: One documented corpus/query/cutoff boundary for a search.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `INTERNAL`; responsible reviewer: Source curator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `corpus_manifest_ref` | Explicit included documents and their versions. | `ref:artifact`; 1; R | exact manifest | not allowed; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L13 |
| `query_artifact_ref` | Queries, variants, language coverage and attempted sources. | `ref:artifact`; 1; R | bound queries/logs | not allowed; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L13 |
| `temporal_coverage` | Declared search period; not the event time. | `TemporalExtent`; 0..1; O | search interval | null + missing_reason; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | year1964 with YEAR precision / 1964-01-01 asserted as an observed day | L12 |
| `coverage_limits` | OCR, language, access and collection gaps remain visible. | `text`; 1; R | explicit limitations | not allowed; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L13 |
| `searched_all_declared_material` | True concerns only the declared corpus, never all history. | `boolean`; 0..1; O | observed scope completion | null + missing_reason; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | false after an actual check / unknown encoded as false | L13 |

### `attribution_assertion`

Grain: One source statement allocating a particular role/credit.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `PUBLIC_ELIGIBLE`; responsible reviewer: Domain adjudicator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `reporting_passage_ref` | Where the attribution was observed. | `ref:passage`; 1; R | exact version | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | `@passage_a` (symbolic exact-version reference) / a name or current filename | L05 |
| `attributed_contributor_ref` | Recipient of credit, not necessarily the reporting author. | `ref:contributor`; 1; R | exact version | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | `@contributor_a` (symbolic exact-version reference) / a name or current filename | L10 |
| `concept_ref` | Concept/sense of attribution. | `ref:concept`; 1; R | exact version | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | `@concept_a` (symbolic exact-version reference) / a name or current filename | L10 |
| `role` | Role actually attributed, not an inferred broader role. | `enum`; 1; R | contribution_role | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | a member of `contribution_role` / an unregistered code or generic PASS | L10 |
| `scope` | Association is not an exclusive-origin assertion. | `enum`; 1; R | attribution_scope | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Domain adjudicator; definition+inputs for derivatives | a member of `attribution_scope` / an unregistered code or generic PASS | L09 |

### `evidence_link`

Grain: One passage-to-claim assessment under a policy.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `INTERNAL`; responsible reviewer: Independent annotator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `passage_ref` | Evidence location; citation existence alone is insufficient. | `ref:passage`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Independent annotator; definition+inputs for derivatives | `@passage_a` (symbolic exact-version reference) / a name or current filename | L05 |
| `claim_ref` | Precisely assessed proposition. | `ref:atomic_claim`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Independent annotator; definition+inputs for derivatives | `@atomic_claim_a` (symbolic exact-version reference) / a name or current filename | L05 |
| `relation` | Mentions/reports must not be promoted to direct support. | `enum`; 1; R | evidence_relation | not allowed; INTERNAL | Inherited provenance rule; Independent annotator; definition+inputs for derivatives | a member of `evidence_relation` / an unregistered code or generic PASS | L06 |
| `policy_ref` | Rules used to interpret passage support. | `ref:adjudication_policy`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Independent annotator; definition+inputs for derivatives | `@adjudication_policy_a` (symbolic exact-version reference) / a name or current filename | L09 |
| `rationale` | Explain support and its limits; no numeric self-confidence substitute. | `text`; 1; R | scoped explanation | not allowed; INTERNAL | Inherited provenance rule; Independent annotator; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L22 |

### `annotation`

Grain: One independent assessor decision on a claim/evidence set.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `INTERNAL`; responsible reviewer: Independent annotator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `claim_ref` | Target proposition. | `ref:atomic_claim`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Independent annotator; definition+inputs for derivatives | `@atomic_claim_a` (symbolic exact-version reference) / a name or current filename | L05 |
| `annotator_ref` | Must distinguish human from model assistance. | `ref:actor`; 1; R | exact actor | not allowed; INTERNAL | Inherited provenance rule; Independent annotator; definition+inputs for derivatives | `@actor_a` (symbolic exact-version reference) / a name or current filename | L07 |
| `evidence_link_refs` | Inspected support/counter-evidence, including gaps. | `refs:evidence_link`; 0..n; O | exact versions | null + missing_reason; INTERNAL | Inherited provenance rule; Independent annotator; definition+inputs for derivatives | `@evidence_link_a` (symbolic exact-version reference) / a name or current filename | L05 |
| `proposed_assessment` | Null NOT_ASSESSED before assessment; not an implicit insufficient label. | `enum`; 0..1; O | claim_assessment | null + missing_reason; INTERNAL | Inherited provenance rule; Independent annotator; definition+inputs for derivatives | a member of `claim_assessment` / an unregistered code or generic PASS | L08 |
| `blinding_note` | Exposure to legacy/model answers and relevant conflicts. | `text`; 1; R | actual procedure | not allowed; INTERNAL | Inherited provenance rule; Independent annotator; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L09 |

### `adjudication_policy`

Grain: One versioned interpretation/comparison and reviewer policy.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `PUBLIC_ELIGIBLE`; responsible reviewer: Research owner/domain adjudicator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `scope_statement` | Question, genres, dates, roles and excluded interpretations. | `text`; 1; R | admissible claims | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Research owner/domain adjudicator; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L09 |
| `decision_rules_artifact_ref` | Rules for all five assessment labels and comparison thresholds. | `ref:artifact`; 1; R | bound rules | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Research owner/domain adjudicator; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L09 |
| `independence_requirement` | At least two independent human annotations; third adjudicator resolves disagreement. | `text`; 1; R | reviewer independence | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Research owner/domain adjudicator; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L09 |
| `normative_basis` | Expected credit is policy/genre specific, not a fact inferred from fame. | `text`; 1; R | stated comparison norm | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Research owner/domain adjudicator; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L11 |
| `credit_incompatibility_rule` | What makes role/priority claims incompatible, or credit obligatory in this genre; comparability alone is insufficient. | `text`; 1; R | explicit rule | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Research owner/domain adjudicator; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | D01 |

### `adjudication`

Grain: One resolved or explicitly unresolved assessment of a claim.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `INTERNAL`; responsible reviewer: Human adjudicator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `claim_ref` | Target with fixed scope. | `ref:atomic_claim`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Human adjudicator; definition+inputs for derivatives | `@atomic_claim_a` (symbolic exact-version reference) / a name or current filename | L05 |
| `policy_ref` | Applied rules, not a mutable policy name. | `ref:adjudication_policy`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Human adjudicator; definition+inputs for derivatives | `@adjudication_policy_a` (symbolic exact-version reference) / a name or current filename | L09 |
| `annotation_refs` | Independent decisions; retain disagreements. | `refs:annotation`; 1..n; R | exact versions | not allowed; INTERNAL | Inherited provenance rule; Human adjudicator; definition+inputs for derivatives | `@annotation_a` (symbolic exact-version reference) / a name or current filename | L08 |
| `assessment` | Completed assessment label; null with reason before completion. | `enum`; 0..1; O | claim_assessment | null + missing_reason; INTERNAL | Inherited provenance rule; Human adjudicator; definition+inputs for derivatives | a member of `claim_assessment` / an unregistered code or generic PASS | L08 |
| `disagreement_resolution` | Needed when annotations differ; agreement is not proof of truth. | `text`; 0..1; O | actual adjudication | null + missing_reason; INTERNAL | Inherited provenance rule; Human adjudicator; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L09 |

### `discrepancy_finding`

Grain: One derived, policy-relative comparison; not a character verdict.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `INTERNAL`; responsible reviewer: Independent human adjudicator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `attribution_ref` | Observed allocation of a particular role. | `ref:attribution_assertion`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Independent human adjudicator; definition+inputs for derivatives | `@attribution_assertion_a` (symbolic exact-version reference) / a name or current filename | L09 |
| `contribution_refs` | Comparison contributions with evidence. | `refs:contribution_assertion`; 1..n; R | exact versions | not allowed; INTERNAL | Inherited provenance rule; Independent human adjudicator; definition+inputs for derivatives | `@contribution_assertion_a` (symbolic exact-version reference) / a name or current filename | L10 |
| `comparison_kind` | Same-concept/role/scope must be established before supported discrepancy. | `enum`; 1; R | comparison_kind | not allowed; INTERNAL | Inherited provenance rule; Independent human adjudicator; definition+inputs for derivatives | a member of `comparison_kind` / an unregistered code or generic PASS | L10 |
| `policy_ref` | Explicit comparison/omission norm. | `ref:adjudication_policy`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Independent human adjudicator; definition+inputs for derivatives | `@adjudication_policy_a` (symbolic exact-version reference) / a name or current filename | L09 |
| `adjudication_refs` | Independent source-based assessments, not a model vote. | `refs:adjudication`; 1..n; R | exact versions | not allowed; INTERNAL | Inherited provenance rule; Independent human adjudicator; definition+inputs for derivatives | `@adjudication_a` (symbolic exact-version reference) / a name or current filename | L09 |
| `conclusion` | No implied intent, theft, legal ownership or misconduct. | `enum`; 1; R | discrepancy_conclusion | not allowed; INTERNAL | Inherited provenance rule; Independent human adjudicator; definition+inputs for derivatives | a member of `discrepancy_conclusion` / an unregistered code or generic PASS | L11 |
| `incompatibility_rationale` | State the supported conflict or why none/unresolved; never a fame-based assertion. | `text`; 1; R | policy-bound evidence | not allowed; INTERNAL | Inherited provenance rule; Independent human adjudicator; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | D01 |

### `review_decision`

Grain: One authorized decision on an exact target digest and use.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `INTERNAL`; responsible reviewer: Authorized human reviewer. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `reviewer_ref` | Human approval cannot be minted by a model field. | `ref:actor`; 1; R | exact authorized actor | not allowed; INTERNAL | Inherited provenance rule; Authorized human reviewer; definition+inputs for derivatives | `@actor_a` (symbolic exact-version reference) / a name or current filename | L17 |
| `target_artifact_ref` | The reviewed bundle/source/protocol artifact. | `ref:artifact`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Authorized human reviewer; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L17 |
| `target_sha256` | Approval binds exact bytes and declared dependencies. | `sha256`; 1; R | exact target bytes | not allowed; INTERNAL | Inherited provenance rule; Authorized human reviewer; definition+inputs for derivatives | a 64-character lowercase hex digest of actual bytes / invented digest or model confidence | L17 |
| `status` | Effective status becomes stale after any relevant change. | `enum`; 1; R | review_status | not allowed; INTERNAL | Inherited provenance rule; Authorized human reviewer; definition+inputs for derivatives | a member of `review_status` / an unregistered code or generic PASS | L17 |
| `review_scope` | Identity, scientific assessment, language, rights or release; not interchangeable. | `text`; 1; R | specific purpose | not allowed; INTERNAL | Inherited provenance rule; Authorized human reviewer; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L18 |

### `artifact`

Grain: One immutable payload or manifest used/produced by the project.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `INTERNAL`; responsible reviewer: Artifact owner. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `kind` | For example source PDF, OCR, book, model weights or illustration. | `text`; 1; R | declared media/purpose | not allowed; INTERNAL | Inherited provenance rule; Artifact owner; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L32 |
| `relative_path` | No traversal, credential path or EIDOS scientific state. | `path`; 1; R | Horisma-owned path | not allowed; INTERNAL | Inherited provenance rule; Artifact owner; definition+inputs for derivatives | data/intake/example.pdf / ../Eidos/outputs/private.pdf | L27 |
| `sha256` | Digest does not prove source authenticity or science. | `sha256`; 1; R | exact file bytes | not allowed; INTERNAL | Inherited provenance rule; Artifact owner; definition+inputs for derivatives | a 64-character lowercase hex digest of actual bytes / invented digest or model confidence | L05 |
| `dependency_refs` | Explicit transitive dependencies; no self/circular derivation. | `refs:artifact`; 0..n; O | exact versions | null + missing_reason; INTERNAL | Inherited provenance rule; Artifact owner; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L04 |
| `rights_decision_refs` | Per-operation permissions for included components. | `refs:rights_decision`; 0..n; O | exact versions | null + missing_reason; INTERNAL | Inherited provenance rule; Artifact owner; definition+inputs for derivatives | `@rights_decision_a` (symbolic exact-version reference) / a name or current filename | L18 |
| `public_projection_of_ref` | Explicit reviewed public projection; underlying private source does not become public. | `ref:artifact`; 0..1; O | source projection | null + missing_reason; INTERNAL | Inherited provenance rule; Artifact owner; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L27 |

### `book_edition`

Grain: One versioned book claim set and render/release manifest.  
Stage: `PROPOSED`; default disclosure: `INTERNAL`; responsible reviewer: Scientific editor. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `claim_refs` | All factual and qualified propositions in the edition. | `refs:atomic_claim`; 1..n; R | exact versions | not allowed; INTERNAL | Inherited provenance rule; Scientific editor; definition+inputs for derivatives | `@atomic_claim_a` (symbolic exact-version reference) / a name or current filename | L18 |
| `publication_modes` | Each included claim maps to a presentation mode; not a global truth badge. | `PublicationModeMap`; 1; R | per-claim mode | not allowed; INTERNAL | Inherited provenance rule; Scientific editor; definition+inputs for derivatives | every included claim assigned one declared mode / one global PASS for all claims | L18 |
| `source_artifact_ref` | Canonical source used for all formats. | `ref:artifact`; 1; R | bound source tree/manifest | not allowed; INTERNAL | Inherited provenance rule; Scientific editor; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L17 |
| `render_artifact_refs` | File creation does not establish reader/print validity. | `refs:artifact`; 0..n; O | HTML/PDF/EPUB | null + missing_reason; INTERNAL | Inherited provenance rule; Scientific editor; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L07 |
| `release_review_ref` | No substantive publication without current human bundle approval. | `ref:review_decision`; 0..1; O | exact bundle | null + missing_reason; INTERNAL | Inherited provenance rule; Scientific editor; definition+inputs for derivatives | `@review_decision_a` (symbolic exact-version reference) / a name or current filename | L18 |

### `localization`

Grain: One translation tied to one exact source edition/claim set.  
Stage: `PROPOSED`; default disclosure: `INTERNAL`; responsible reviewer: Independent bilingual reviewer. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `parent_book_ref` | Do not translate an unbound changing draft. | `ref:book_edition`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Independent bilingual reviewer; definition+inputs for derivatives | `@book_edition_a` (symbolic exact-version reference) / a name or current filename | L17 |
| `target_language` | Six planned publication lanes, each separately reviewed. | `enum`; 1; R | target_language | not allowed; INTERNAL | Inherited provenance rule; Independent bilingual reviewer; definition+inputs for derivatives | a member of `target_language` / an unregistered code or generic PASS | L17 |
| `preserved_claim_refs` | Claim identities, uncertainty and roles survive translation. | `refs:atomic_claim`; 1..n; R | exact versions | not allowed; INTERNAL | Inherited provenance rule; Independent bilingual reviewer; definition+inputs for derivatives | `@atomic_claim_a` (symbolic exact-version reference) / a name or current filename | L18 |
| `translated_artifact_ref` | Source-language quotations remain separately accessible. | `ref:artifact`; 1; R | exact bytes | not allowed; INTERNAL | Inherited provenance rule; Independent bilingual reviewer; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L05 |
| `locale_review_ref` | Back-translation/model fluency is not independent approval. | `ref:review_decision`; 0..1; O | exact translated target | null + missing_reason; INTERNAL | Inherited provenance rule; Independent bilingual reviewer; definition+inputs for derivatives | `@review_decision_a` (symbolic exact-version reference) / a name or current filename | L18 |

### `correction`

Grain: One traceable correction/withdrawal affecting a dependency set.  
Stage: `PROPOSED`; default disclosure: `PUBLIC_ELIGIBLE`; responsible reviewer: Scientific editor. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `superseded_record_refs` | Retain former versions and why they are replaced. | `RecordRefList`; 1..n; R | exact versions | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Scientific editor; definition+inputs for derivatives | exact immutable record references / mutable filenames as scientific identities | L03 |
| `reason` | Correct error without rewriting prior history. | `text`; 1; R | specific finding | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Scientific editor; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L31 |
| `affected_artifact_refs` | All derived translations/books requiring invalidation/review. | `refs:artifact`; 1..n; R | exact versions | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Scientific editor; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L17 |
| `replacement_record_refs` | Replacement may be absent pending investigation. | `RecordRefList`; 0..n; O | exact versions | null + missing_reason; PUBLIC_ELIGIBLE | Inherited provenance rule; Scientific editor; definition+inputs for derivatives | exact immutable record references / mutable filenames as scientific identities | L02 |

### `dataset_version`

Grain: One frozen dataset manifest and annotation protocol.  
Stage: `PROTOCOL_DEPENDENT`; default disclosure: `SEALED_EVALUATION`; responsible reviewer: Independent benchmark curator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `protocol_ref` | Sampling and research purpose. | `ref:project_protocol`; 1; R | exact version | not allowed; SEALED_EVALUATION | Inherited provenance rule; Independent benchmark curator; definition+inputs for derivatives | `@project_protocol_a` (symbolic exact-version reference) / a name or current filename | L19 |
| `task_refs` | Frozen task inventory; not generated answer narratives as gold. | `refs:benchmark_task`; 1..n; R | exact versions | not allowed; SEALED_EVALUATION | Inherited provenance rule; Independent benchmark curator; definition+inputs for derivatives | `@benchmark_task_a` (symbolic exact-version reference) / a name or current filename | L01 |
| `gold_adjudication_refs` | Independent gold with disagreement records. | `refs:adjudication`; 1..n; R | sealed exact versions | not allowed; SEALED_EVALUATION | Inherited provenance rule; Independent benchmark curator; definition+inputs for derivatives | `@adjudication_a` (symbolic exact-version reference) / a name or current filename | L01 |
| `split_assignment_refs` | Family-level partitions and documented overlap audit. | `refs:split_assignment`; 1..n; R | exact versions | not allowed; SEALED_EVALUATION | Inherited provenance rule; Independent benchmark curator; definition+inputs for derivatives | `@split_assignment_a` (symbolic exact-version reference) / a name or current filename | L19 |
| `access_policy_artifact_ref` | Evaluator versus development access and leakage audit, including prompts/caches. | `ref:artifact`; 1; R | sealed access policy | not allowed; SEALED_EVALUATION | Inherited provenance rule; Independent benchmark curator; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L35 |
| `gold_binding_manifest_ref` | Frozen release-specific gold and scoring bindings; task identity alone is insufficient. | `ref:artifact`; 1; R | task/target/adjudication/policy bindings | not allowed; SEALED_EVALUATION | Inherited provenance rule; Independent benchmark curator; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L38 |
| `canonical_family_manifest_ref` | Exactly one canonical version per family entity, consistent bidirectional concept membership and task/claim/concept/family bindings before splitting. | `ref:artifact`; 1; R | release-specific partition | not allowed; SEALED_EVALUATION | Inherited provenance rule; Independent benchmark curator; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L39 |

### `split_assignment`

Grain: One concept-family assignment within a dataset version.  
Stage: `PROTOCOL_DEPENDENT`; default disclosure: `SEALED_EVALUATION`; responsible reviewer: Benchmark curator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `family_ref` | Family, not one language string. | `ref:concept_family`; 1; R | exact version | not allowed; SEALED_EVALUATION | Inherited provenance rule; Benchmark curator; definition+inputs for derivatives | `@concept_family_a` (symbolic exact-version reference) / a name or current filename | L19 |
| `split` | All aliases/translations remain in this partition for this dataset. | `enum`; 1; R | dataset_split | not allowed; SEALED_EVALUATION | Inherited provenance rule; Benchmark curator; definition+inputs for derivatives | a member of `dataset_split` / an unregistered code or generic PASS | L19 |
| `assignment_protocol_ref` | Partition/selection rules and seed policy. | `ref:project_protocol`; 1; R | exact version | not allowed; SEALED_EVALUATION | Inherited provenance rule; Benchmark curator; definition+inputs for derivatives | `@project_protocol_a` (symbolic exact-version reference) / a name or current filename | L19 |
| `dataset_ref` | Partition ownership; assignments may differ across separately frozen dataset versions, with overlap audits. | `ref:dataset_version`; 1; R | exact dataset version | not allowed; SEALED_EVALUATION | Inherited provenance rule; Benchmark curator; definition+inputs for derivatives | `@dataset_version_a` (symbolic exact-version reference) / a name or current filename | L19 |

### `benchmark_task`

Grain: One scored question with a declared evidence-access condition.  
Stage: `PROTOCOL_DEPENDENT`; default disclosure: `SEALED_EVALUATION`; responsible reviewer: Benchmark curator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `family_ref` | Independent grouping unit. | `ref:concept_family`; 1; R | exact version | not allowed; SEALED_EVALUATION | Inherited provenance rule; Benchmark curator; definition+inputs for derivatives | `@concept_family_a` (symbolic exact-version reference) / a name or current filename | L19 |
| `question_artifact_ref` | Frozen prompt/question; no answer leakage. | `ref:artifact`; 1; R | exact bytes | not allowed; SEALED_EVALUATION | Inherited provenance rule; Benchmark curator; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L19 |
| `condition` | Do not combine closed-book/oracle/retrieved evidence scores. | `enum`; 1; R | evaluation_condition | not allowed; SEALED_EVALUATION | Inherited provenance rule; Benchmark curator; definition+inputs for derivatives | a member of `evaluation_condition` / an unregistered code or generic PASS | L21 |
| `evidence_packet_ref` | Absent in closed-book; record actual access in other conditions. | `ref:artifact`; 0..1; O | condition-bound packet | null + missing_reason; SEALED_EVALUATION | Inherited provenance rule; Benchmark curator; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L05 |
| `target_claim_refs` | Claims evaluated, including unresolved controls. | `refs:atomic_claim`; 1..n; R | exact versions | not allowed; SEALED_EVALUATION | Inherited provenance rule; Benchmark curator; definition+inputs for derivatives | `@atomic_claim_a` (symbolic exact-version reference) / a name or current filename | L08 |

### `model_configuration`

Grain: One actual local backend/weights/tokenizer/generation configuration.  
Stage: `PROPOSED`; default disclosure: `INTERNAL`; responsible reviewer: Model qualification owner. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `weights_artifact_ref` | Model name/parameter count alone is not a reproducible model. | `ref:artifact`; 1; R | exact weights identity | not allowed; INTERNAL | Inherited provenance rule; Model qualification owner; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L26 |
| `tokenizer_artifact_ref` | Tokenizer identity separate from weights. | `ref:artifact`; 1; R | exact tokenizer | not allowed; INTERNAL | Inherited provenance rule; Model qualification owner; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L03 |
| `backend_uri` | No hosted proprietary/paid fallback; offline errors remain typed. | `uri`; 1; R | loopback local endpoint | not allowed; INTERNAL | Inherited provenance rule; Model qualification owner; definition+inputs for derivatives | https://example.org/source / URL containing a password | L26 |
| `context_token_limit` | Measured effective context limit including prompts/evidence. | `integer`; 1; R | tokens; >0 | not allowed; INTERNAL | Inherited provenance rule; Model qualification owner; definition+inputs for derivatives | 0 when actually observed and allowed / -999 as missing sentinel | L22 |
| `output_token_limit` | Bounded generation budget, not a quality score. | `integer`; 1; R | tokens; >0 | not allowed; INTERNAL | Inherited provenance rule; Model qualification owner; definition+inputs for derivatives | 0 when actually observed and allowed / -999 as missing sentinel | L22 |
| `sampling_config_ref` | Configuration artifact must name seed or nondeterminism explicitly. | `ref:artifact`; 1; R | temperature/seed/quantization/dtype | not allowed; INTERNAL | Inherited provenance rule; Model qualification owner; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L03 |
| `qualification_review_ref` | No performance/ranking claim outside measured tasks. | `ref:review_decision`; 0..1; O | declared scope | null + missing_reason; INTERNAL | Inherited provenance rule; Model qualification owner; definition+inputs for derivatives | `@review_decision_a` (symbolic exact-version reference) / a name or current filename | L22 |

### `model_response`

Grain: One model answer attempt with actual accessible inputs.  
Stage: `PROTOCOL_DEPENDENT`; default disclosure: `INTERNAL`; responsible reviewer: Independent evaluator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `task_ref` | Task/condition and eligible gold policy. | `ref:benchmark_task`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Independent evaluator; definition+inputs for derivatives | `@benchmark_task_a` (symbolic exact-version reference) / a name or current filename | L19 |
| `configuration_ref` | Actual selected local configuration. | `ref:model_configuration`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Independent evaluator; definition+inputs for derivatives | `@model_configuration_a` (symbolic exact-version reference) / a name or current filename | L26 |
| `answer_artifact_ref` | Retain failed/malformed answers and attempts. | `ref:artifact`; 1; R | exact raw answer | not allowed; INTERNAL | Inherited provenance rule; Independent evaluator; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L07 |
| `raw_self_rating` | Optional requested score; never called historical truth probability. | `fraction`; 0..1; O | 0..1; uncalibrated | null + missing_reason; INTERNAL | Inherited provenance rule; Independent evaluator; definition+inputs for derivatives | 0.25 / 75 treated as a fraction | L22 |
| `calibration_ref` | Absent is not a calibrated score of zero. | `ref:artifact`; 1 when condition; else 0..1; C:calibrated_correctness_probability is non-null | independent calibration study | null + missing_reason; INTERNAL | Inherited provenance rule; Independent evaluator; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L22 |
| `token_softmax_artifact_ref` | Raw token probabilities with tokenizer/logit-processing/dtype configuration; not a calibrated answer correctness probability. | `ref:artifact`; 0..1; O | token-distribution observation | null + missing_reason; INTERNAL | Inherited provenance rule; Independent evaluator; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L22 |
| `calibrated_correctness_probability` | Requires a bound independent calibration study for this task/outcome and evaluation condition; never historical truth probability. | `fraction`; 0..1; O | 0..1; declared task outcome | null + missing_reason; INTERNAL | Inherited provenance rule; Independent evaluator; definition+inputs for derivatives | 0.25 / 75 treated as a fraction | L22 |
| `evaluation_context_ref` | Bind the frozen release, gold/scoring policy and actually accessible prompt/evidence; no ambiguous cross-release scoring. | `ref:evaluation_context`; 1; R | exact attempt context | not allowed; INTERNAL | Inherited provenance rule; Independent evaluator; definition+inputs for derivatives | `@evaluation_context_a` (symbolic exact-version reference) / a name or current filename | L38 |

### `metric_definition`

Grain: One versioned mathematical measurement and aggregation rule.  
Stage: `PROTOCOL_DEPENDENT`; default disclosure: `PUBLIC_ELIGIBLE`; responsible reviewer: Methods reviewer. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `name` | Distinguish retrieval, identity, support, correctness and calibration. | `text`; 1; R | construct-specific name | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Methods reviewer; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L21 |
| `formula` | Define numerator, denominator, independent unit and undefined cases. | `text`; 1; R | expression with domain | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Methods reviewer; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L20 |
| `unit_and_direction` | For example fraction, seconds, MiB; higher/lower is not universally better. | `text`; 1; R | scale and interpretation | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Methods reviewer; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L24 |
| `protocol_ref` | Eligible universe, exclusions, uncertainty method and aggregation. | `ref:project_protocol`; 1; R | exact version | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Methods reviewer; definition+inputs for derivatives | `@project_protocol_a` (symbolic exact-version reference) / a name or current filename | L21 |
| `logic_ids` | Formal derivation and assumptions, not a model-generated explanation. | `LogicRefList`; 1..n; R | catalogue rules | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Methods reviewer; definition+inputs for derivatives | L20 / unsupported/unregistered logic identifier | L20 |

### `metric_observation`

Grain: One actually measured/derived value under one definition and scope.  
Stage: `PROTOCOL_DEPENDENT`; default disclosure: `INTERNAL`; responsible reviewer: Independent evaluator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `definition_ref` | Fixed measurement semantics. | `ref:metric_definition`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Independent evaluator; definition+inputs for derivatives | `@metric_definition_a` (symbolic exact-version reference) / a name or current filename | L20 |
| `measurement_status` | NOT_MEASURED differs from measured zero and NOT_DEFINED. | `enum`; 1; R | metric_status | not allowed; INTERNAL | Inherited provenance rule; Independent evaluator; definition+inputs for derivatives | a member of `metric_status` / an unregistered code or generic PASS | L02 |
| `value` | Null for missing/undefined/invalidated observations. | `number`; 1 when condition; else 0..1; C:measurement_status=DEFINED | definition unit | null + missing_reason; INTERNAL | Inherited provenance rule; Independent evaluator; definition+inputs for derivatives | 0.0 when measured / NaN/infinity or unknown encoded as zero | L20 |
| `numerator` | Observed count for rate metrics, not inferred from a rounded score. | `integer`; 0..1; O | count; >=0 | null + missing_reason; INTERNAL | Inherited provenance rule; Independent evaluator; definition+inputs for derivatives | 0 when actually observed and allowed / -999 as missing sentinel | L20 |
| `denominator` | Eligible observations; zero denominator makes a rate undefined. | `integer`; 0..1; O | count; >=0 | null + missing_reason; INTERNAL | Inherited provenance rule; Independent evaluator; definition+inputs for derivatives | 0 when actually observed and allowed / -999 as missing sentinel | L20 |
| `eligible_family_refs` | Required for family-macro results; report excluded families separately. | `refs:concept_family`; 1..n when condition; else 0..n; C:family-macro metric | actual families | null + missing_reason; INTERNAL | Inherited provenance rule; Independent evaluator; definition+inputs for derivatives | `@concept_family_a` (symbolic exact-version reference) / a name or current filename | L21 |
| `input_artifact_refs` | Raw scores/logs, eligibility and uncertainty calculation inputs. | `refs:artifact`; 1..n; R | exact measurements | not allowed; INTERNAL | Inherited provenance rule; Independent evaluator; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L20 |

### `study_protocol`

Grain: One version of a proposed/approved human-research protocol.  
Stage: `PROTOCOL_DEPENDENT`; default disclosure: `RESTRICTED`; responsible reviewer: Research/ethics owner. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `project_protocol_ref` | Research question and scientific scope. | `ref:project_protocol`; 1; R | exact version | not allowed; RESTRICTED | Inherited provenance rule; Research/ethics owner; definition+inputs for derivatives | `@project_protocol_a` (symbolic exact-version reference) / a name or current filename | L29 |
| `estimand_statement` | Proposed mitigation positive for reduction; actual protocol must approve it. | `text`; 1; R | outcome/conditions/sign | not allowed; RESTRICTED | Inherited provenance rule; Research/ethics owner; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L24 |
| `analysis_plan_artifact_ref` | No invented sample size, power, exclusions or completed study. | `ref:artifact`; 0..1; O | preregistered plan | null + missing_reason; RESTRICTED | Inherited provenance rule; Research/ethics owner; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L29 |
| `ethics_review_ref` | A plan/LLM opinion is not ethics approval. | `ref:review_decision`; 0..1; O | actual institutional determination | null + missing_reason; RESTRICTED | Inherited provenance rule; Research/ethics owner; definition+inputs for derivatives | `@review_decision_a` (symbolic exact-version reference) / a name or current filename | L17 |

### `vignette_actor`

Grain: One explicitly fictional actor inside a research vignette.  
Stage: `PROTOCOL_DEPENDENT`; default disclosure: `INTERNAL`; responsible reviewer: Study owner. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `label` | Not a disguised historical allegation or real-person biography. | `text`; 1; R | fictional label | not allowed; INTERNAL | Inherited provenance rule; Study owner; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L32 |
| `vignette_ref` | Defines fictional context and contribution record. | `ref:vignette`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Study owner; definition+inputs for derivatives | `@vignette_a` (symbolic exact-version reference) / a name or current filename | L03 |
| `documented_role` | Fixed contribution role independent of randomized prestige. | `enum`; 1; R | contribution_role | not allowed; INTERNAL | Inherited provenance rule; Study owner; definition+inputs for derivatives | a member of `contribution_role` / an unregistered code or generic PASS | L10 |

### `vignette`

Grain: One controlled evidence/contribution stimulus.  
Stage: `PROTOCOL_DEPENDENT`; default disclosure: `INTERNAL`; responsible reviewer: Study owner. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `protocol_ref` | Design/ethics scope. | `ref:study_protocol`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Study owner; definition+inputs for derivatives | `@study_protocol_a` (symbolic exact-version reference) / a name or current filename | L29 |
| `actor_refs` | Counterbalanced identities and fixed contribution information. | `refs:vignette_actor`; 1..n; R | fictional actors | not allowed; INTERNAL | Inherited provenance rule; Study owner; definition+inputs for derivatives | `@vignette_actor_a` (symbolic exact-version reference) / a name or current filename | L24 |
| `stimulus_artifact_ref` | Fact-matched versions must retain source facts and reading-demand checks. | `ref:artifact`; 1; R | exact stimulus | not allowed; INTERNAL | Inherited provenance rule; Study owner; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L24 |

### `participant`

Grain: One study-local pseudonym; no direct identity/contact fields here.  
Stage: `PROTOCOL_DEPENDENT`; default disclosure: `RESTRICTED`; responsible reviewer: Authorized study/data steward. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `pseudonym` | Not a name, email, account handle or link to a historical contributor. | `text`; 1; R | random study identifier | not allowed; RESTRICTED | Inherited provenance rule; Authorized study/data steward; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L27 |
| `protocol_ref` | Eligibility, consent and withdrawal policy. | `ref:study_protocol`; 1; R | exact version | not allowed; RESTRICTED | Inherited provenance rule; Authorized study/data steward; definition+inputs for derivatives | `@study_protocol_a` (symbolic exact-version reference) / a name or current filename | L29 |
| `consent_record_artifact_ref` | Separate protected consent record, never public release content. | `ref:artifact`; 1; R | restricted opaque record | not allowed; RESTRICTED | Inherited provenance rule; Authorized study/data steward; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L27 |
| `withdrawal_record_ref` | Actual withdrawal and permitted retention handling. | `ref:artifact`; 0..1; O | restricted record | null + missing_reason; RESTRICTED | Inherited provenance rule; Authorized study/data steward; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L27 |

### `condition_assignment`

Grain: One randomized participant-vignette exposure assignment.  
Stage: `PROTOCOL_DEPENDENT`; default disclosure: `RESTRICTED`; responsible reviewer: Study owner. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `participant_ref` | Participant clustering unit. | `ref:participant`; 1; R | exact version | not allowed; RESTRICTED | Inherited provenance rule; Study owner; definition+inputs for derivatives | `@participant_a` (symbolic exact-version reference) / a name or current filename | L24 |
| `vignette_ref` | Item clustering unit. | `ref:vignette`; 1; R | exact version | not allowed; RESTRICTED | Inherited provenance rule; Study owner; definition+inputs for derivatives | `@vignette_a` (symbolic exact-version reference) / a name or current filename | L24 |
| `presentation` | Ledger versus fact-matched narrative, not unmatched information access. | `enum`; 1; R | presentation_condition | not allowed; RESTRICTED | Inherited provenance rule; Study owner; definition+inputs for derivatives | a member of `presentation_condition` / an unregistered code or generic PASS | L24 |
| `prestige_recipient_ref` | Recipient of the randomized cue; not actual celebrity identity. | `ref:vignette_actor`; 1; R | exact fictional actor | not allowed; RESTRICTED | Inherited provenance rule; Study owner; definition+inputs for derivatives | `@vignette_actor_a` (symbolic exact-version reference) / a name or current filename | L24 |
| `randomization_artifact_ref` | Actual assignment procedure, not a post-hoc inferred condition. | `ref:artifact`; 1; R | seed/procedure receipt | not allowed; RESTRICTED | Inherited provenance rule; Study owner; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L24 |
| `response_actor_refs` | Exact required allocation domain within the assigned vignette; no unrelated actors or omitted required targets. | `refs:vignette_actor`; 1..n; R | protocol-defined response set | not allowed; RESTRICTED | Inherited provenance rule; Study owner; definition+inputs for derivatives | `@vignette_actor_a` (symbolic exact-version reference) / a name or current filename | L40 |
| `delivered_stimulus_artifact_ref` | Exact stimulus bytes binding the assigned vignette, presentation format and prestige-cue recipient, not just a template. | `ref:artifact`; 1; R | actual delivered variant | not allowed; RESTRICTED | Inherited provenance rule; Study owner; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L40 |

### `behavioral_response`

Grain: One participant response to one assigned stimulus.  
Stage: `PROTOCOL_DEPENDENT`; default disclosure: `RESTRICTED`; responsible reviewer: Study analyst. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `assignment_ref` | Links outcome to randomized condition and clustering units. | `ref:condition_assignment`; 1; R | exact version | not allowed; RESTRICTED | Inherited provenance rule; Study analyst; definition+inputs for derivatives | `@condition_assignment_a` (symbolic exact-version reference) / a name or current filename | L24 |
| `allocation` | Canonical shares; missing/abstention is not an all-zero response. | `CreditAllocation`; 0..1; O | fractions; sum=1 | null + missing_reason; RESTRICTED | Inherited provenance rule; Study analyst; definition+inputs for derivatives | two fictional actors with shares0.25 and0.75 / all-zero vector for abstention | L23 |
| `raw_response_artifact_ref` | Retain raw entry and source scale before normalization. | `ref:artifact`; 1; R | restricted original response | not allowed; RESTRICTED | Inherited provenance rule; Study analyst; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L23 |
| `raw_scale` | Percent-to-fraction conversion is divide100, not a new observation. | `text`; 1; R | fraction or percent and bounds | not allowed; RESTRICTED | Inherited provenance rule; Study analyst; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L23 |

### `operator_run`

Grain: One bounded attempt of one declared operator contract.  
Stage: `PROPOSED`; default disclosure: `INTERNAL`; responsible reviewer: Engineering owner. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `operator_id` | Contract identity/version, not an arbitrary shell command. | `OperatorRef`; 1; R | operator catalogue ID | not allowed; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | HOP-SOURCE-INTAKE / an unregistered mutable script path | L03 |
| `input_artifact_refs` | Explicit inputs, with no recursive legacy ingestion. | `refs:artifact`; 1..n; R | exact versions | not allowed; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L01 |
| `output_artifact_refs` | Candidate outputs do not inherit scientific approval. | `refs:artifact`; 0..n; O | actual outputs | null + missing_reason; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L07 |
| `execution_status` | Execution state, separate from source/evidence/review statuses. | `enum`; 1; R | execution_status | not allowed; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | a member of `execution_status` / an unregistered code or generic PASS | L07 |
| `configuration_artifact_ref` | Reproducibility and idempotency parameters, not undocumented ambient configuration. | `ref:artifact`; 1; R | code/lock/prompt/backend/seed manifest | not allowed; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L03 |
| `failure_kind` | Typed operational limit; no silent paid fallback. | `enum`; 0..1; O | failure_kind | null + missing_reason; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | a member of `failure_kind` / an unregistered code or generic PASS | L26 |

### `task_lease`

Grain: One finite ownership grant for one task attempt.  
Stage: `PROPOSED`; default disclosure: `INTERNAL`; responsible reviewer: Engineering owner. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `run_ref` | Attempt being owned. | `ref:operator_run`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | `@operator_run_a` (symbolic exact-version reference) / a name or current filename | L03 |
| `owner_actor_ref` | Actual controller/worker identity, not a reusable PID alone. | `ref:actor`; 1; R | exact actor | not allowed; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | `@actor_a` (symbolic exact-version reference) / a name or current filename | L30 |
| `expires_at` | Finite lease; expiry is operational time, not historical date. | `datetime`; 1; R | UTC instant | not allowed; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | 2026-11-04T00:00:00Z / 1964 guessed as an exact operational timestamp | L30 |
| `status` | Human waits release the lease; cancellation closes owned work. | `enum`; 1; R | execution_status | not allowed; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | a member of `execution_status` / an unregistered code or generic PASS | L15 |
| `idempotency_key` | Retry deduplication, not an exactly-once execution claim. | `sha256`; 1; R | input/config/operator binding | not allowed; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | a 64-character lowercase hex digest of actual bytes / invented digest or model confidence | L31 |

### `resource_observation`

Grain: One measured resource sample with explicit coverage.  
Stage: `PROPOSED`; default disclosure: `INTERNAL`; responsible reviewer: Engineering owner. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `run_ref` | Associated run if applicable. | `ref:operator_run`; 0..1; O | exact version | null + missing_reason; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | `@operator_run_a` (symbolic exact-version reference) / a name or current filename | L03 |
| `sampled_at` | Fresh observation time, not research-result time. | `datetime`; 1; R | UTC instant | not allowed; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | 2026-11-04T00:00:00Z / 1964 guessed as an exact operational timestamp | L07 |
| `gpu_memory_mib` | Actual measurement; no parameter-count-derived fit claim. | `number`; 0..1; O | MiB; >=0 | null + missing_reason; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | 0.0 when measured / NaN/infinity or unknown encoded as zero | L30 |
| `latency_seconds` | Measured elapsed time with operation scope. | `number`; 0..1; O | seconds; >=0 | null + missing_reason; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | 0.0 when measured / NaN/infinity or unknown encoded as zero | L02 |
| `measurement_artifact_ref` | Absence of telemetry cannot establish a successful sample. | `ref:artifact`; 1; R | raw receipt | not allowed; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L02 |

### `cost_audit`

Grain: One API-spend/call audit for a declared interval and coverage.  
Stage: `PROPOSED`; default disclosure: `INTERNAL`; responsible reviewer: Engineering owner. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `coverage_artifact_ref` | Declared interval, endpoints and instrumentation gaps. | `ref:artifact`; 1; R | network/call audit | not allowed; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L25 |
| `measurement_status` | Configured zero-cost policy is not an observed value. | `enum`; 1; R | metric_status | not allowed; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | a member of `metric_status` / an unregistered code or generic PASS | L25 |
| `billable_api_calls` | Actual observed charged-API call count. | `integer`; 1 when condition; else 0..1; C:measurement_status=DEFINED | calls; >=0 | null + missing_reason; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | 0 when actually observed and allowed / -999 as missing sentinel | L25 |
| `spend` | API spend only; not total electricity/hardware/labour cost. | `number`; 1 when condition; else 0..1; C:measurement_status=DEFINED | currency units; >=0 | null + missing_reason; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | 0.0 when measured / NaN/infinity or unknown encoded as zero | L25 |
| `currency` | Currency in the underlying audit; no invented exchange conversion. | `text`; 1; R | ISO4217 code | not allowed; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L25 |

### `recovery_event`

Grain: One proposed/executed bounded operational recovery action.  
Stage: `PROPOSED`; default disclosure: `INTERNAL`; responsible reviewer: Engineering owner. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `run_ref` | Owned failure/recovery context. | `ref:operator_run`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | `@operator_run_a` (symbolic exact-version reference) / a name or current filename | L31 |
| `action` | Restart owned worker, requeue or restore verified backup only. | `text`; 1; R | approved bounded action | not allowed; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L31 |
| `protected_manifest_ref` | Prove preservation; recovery cannot rewrite scientific records. | `ref:artifact`; 1; R | accepted-record inventory | not allowed; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L31 |
| `outcome_artifact_ref` | Missing outcome is not a successful repair. | `ref:artifact`; 0..1; O | actual receipt | null + missing_reason; INTERNAL | Inherited provenance rule; Engineering owner; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L31 |

### `rights_decision`

Grain: One rights finding for one artifact and operation.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `INTERNAL`; responsible reviewer: Rights reviewer. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `artifact_ref` | Material being assessed, not all works by an author. | `ref:artifact`; 1; R | exact bytes | not allowed; INTERNAL | Inherited provenance rule; Rights reviewer; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L16 |
| `operation` | Local reading/processing, quote, full-text/asset redistribution are separate. | `enum`; 1; R | rights_operation | not allowed; INTERNAL | Inherited provenance rule; Rights reviewer; definition+inputs for derivatives | a member of `rights_operation` / an unregistered code or generic PASS | L16 |
| `status` | Unknown does not mean permitted. | `enum`; 1; R | rights_status | not allowed; INTERNAL | Inherited provenance rule; Rights reviewer; definition+inputs for derivatives | a member of `rights_status` / an unregistered code or generic PASS | L27 |
| `basis_artifact_ref` | Applicable conditions, jurisdiction and actual source. | `ref:artifact`; 1; R | license/permission/review evidence | not allowed; INTERNAL | Inherited provenance rule; Rights reviewer; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L16 |
| `conditions_artifact_ref` | Exact scope, applicable constraints and applicability period; use an explicit no-additional-conditions statement when appropriate. | `ref:artifact`; 1; R | explicit conditions | not allowed; INTERNAL | Inherited provenance rule; Rights reviewer; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L37 |

### `logical_statement`

Grain: One typed formal statement, definition or hypothesis.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `PUBLIC_ELIGIBLE`; responsible reviewer: Methods/formalization reviewer. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `logic_kind` | Definition, invariant, derivation, transition or empirical hypothesis. | `enum`; 1; R | logic_kind | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Methods/formalization reviewer; definition+inputs for derivatives | a member of `logic_kind` / an unregistered code or generic PASS | L29 |
| `formal_expression` | Formal statement, not an already checked theorem. | `text`; 1; R | typed specification notation | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Methods/formalization reviewer; definition+inputs for derivatives | A scoped source statement / empty string used as unknown | L28 |
| `assumption_statement_refs` | Hypotheses are not silently promoted to axioms. | `refs:logical_statement`; 0..n; O | explicit premises | null + missing_reason; PUBLIC_ELIGIBLE | Inherited provenance rule; Methods/formalization reviewer; definition+inputs for derivatives | `@logical_statement_a` (symbolic exact-version reference) / a name or current filename | L29 |
| `catalogue_logic_ids` | Connection to field constraints and later proof obligations. | `LogicRefList`; 1..n; R | logic catalogue IDs | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Methods/formalization reviewer; definition+inputs for derivatives | L20 / unsupported/unregistered logic identifier | L28 |

### `proof_record`

Grain: One scoped proof attempt/result for an exact formal statement.  
Stage: `PROPOSED`; default disclosure: `PUBLIC_ELIGIBLE`; responsible reviewer: Independent formalization reviewer. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `statement_ref` | The precise proposition, not an English paraphrase alone. | `ref:logical_statement`; 1; R | exact version | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Independent formalization reviewer; definition+inputs for derivatives | `@logical_statement_a` (symbolic exact-version reference) / a name or current filename | L28 |
| `proof_status` | Finite examples/document checks do not mean formally proved. | `enum`; 1; R | proof_status | not allowed; PUBLIC_ELIGIBLE | Inherited provenance rule; Independent formalization reviewer; definition+inputs for derivatives | a member of `proof_status` / an unregistered code or generic PASS | L28 |
| `proof_artifact_ref` | Required for a formally proved status. | `ref:artifact`; 1 when condition; else 0..1; C:proof_status=PROVED_WITH_BOUND_ARTIFACT | exact proof bytes | null + missing_reason; PUBLIC_ELIGIBLE | Inherited provenance rule; Independent formalization reviewer; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L28 |
| `toolchain_artifact_ref` | Exact toolchain and allowed assumptions; required for proof acceptance. | `ref:artifact`; 1 when condition; else 0..1; C:proof_status=PROVED_WITH_BOUND_ARTIFACT | compiler/libraries/kernel/options | null + missing_reason; PUBLIC_ELIGIBLE | Inherited provenance rule; Independent formalization reviewer; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L28 |
| `verification_receipt_ref` | Actual checker result plus negative controls, not invented fixture success. | `ref:artifact`; 1 when condition; else 0..1; C:proof_status=PROVED_WITH_BOUND_ARTIFACT | independent check receipt | null + missing_reason; PUBLIC_ELIGIBLE | Inherited provenance rule; Independent formalization reviewer; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L28 |

### `evaluation_context`

Grain: One frozen dataset/scoring/access context for a response attempt.  
Stage: `PROTOCOL_DEPENDENT`; default disclosure: `SEALED_EVALUATION`; responsible reviewer: Independent evaluator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `dataset_ref` | Unambiguous dataset, family partition, access policy and gold version. | `ref:dataset_version`; 1; R | exact release | not allowed; SEALED_EVALUATION | Inherited provenance rule; Independent evaluator; definition+inputs for derivatives | `@dataset_version_a` (symbolic exact-version reference) / a name or current filename | L38 |
| `task_ref` | Must match the response task and belong to the bound release. | `ref:benchmark_task`; 1; R | exact version | not allowed; SEALED_EVALUATION | Inherited provenance rule; Independent evaluator; definition+inputs for derivatives | `@benchmark_task_a` (symbolic exact-version reference) / a name or current filename | L38 |
| `scoring_policy_artifact_ref` | Outcome definitions and eligible gold mappings, never a floating latest policy. | `ref:artifact`; 1; R | exact scoring rules | not allowed; SEALED_EVALUATION | Inherited provenance rule; Independent evaluator; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L38 |
| `gold_binding_manifest_ref` | Must equal the bound release manifest mapping each task/target to its gold adjudication and scoring policy. | `ref:artifact`; 1; R | exact dataset manifest | not allowed; SEALED_EVALUATION | Inherited provenance rule; Independent evaluator; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L38 |
| `evidence_access` | Declared condition must match the task and actual accessible inputs. | `enum`; 1; R | evaluation_condition | not allowed; SEALED_EVALUATION | Inherited provenance rule; Independent evaluator; definition+inputs for derivatives | a member of `evaluation_condition` / an unregistered code or generic PASS | L38 |
| `realized_input_receipt_ref` | Exact rendered prompt, retrieved passage IDs and hashes, access limitations and observed context; protected when evaluation content is sealed. | `ref:artifact`; 1; R | actual prompt/access receipt | not allowed; SEALED_EVALUATION | Inherited provenance rule; Independent evaluator; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L38 |

### `search_observation`

Grain: One actual bounded search result, including a negative result without a fabricated passage.  
Stage: `CORE_CONTRACT_DEFINED`; default disclosure: `INTERNAL`; responsible reviewer: Source curator. All common fields apply.

| Field | English definition / prohibited inference | Type; cardinality; obligation | Values / units | Missing / disclosure | Provenance / derivation / review | Valid example / invalid example | Logic |
|---|---|---|---|---|---|---|---|
| `search_scope_ref` | Scope actually inspected; not all history. | `ref:search_scope`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | `@search_scope_a` (symbolic exact-version reference) / a name or current filename | L13 |
| `claim_ref` | Question/proposition searched. | `ref:atomic_claim`; 1; R | exact version | not allowed; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | `@atomic_claim_a` (symbolic exact-version reference) / a name or current filename | L05 |
| `outcome` | Negative retrieval belongs here, not on an invented passage. | `enum`; 1; R | search_outcome | not allowed; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | a member of `search_outcome` / an unregistered code or generic PASS | L13 |
| `returned_passage_refs` | Known empty list may accompany a completed negative search. | `refs:passage`; 0..n; O | actual returned spans | null + missing_reason; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | `@passage_a` (symbolic exact-version reference) / a name or current filename | L02 |
| `query_log_artifact_ref` | Inspected documents, queries and unresolved coverage gaps. | `ref:artifact`; 1; R | actual search receipt | not allowed; INTERNAL | Inherited provenance rule; Source curator; definition+inputs for derivatives | `@artifact_a` (symbolic exact-version reference) / a name or current filename | L13 |

## Assessment, measurement and release conventions

Five completed claim-assessment outcomes are maintained in the vocabulary, separate from unassessed/null. Two independent human annotations are required for scientific adjudication; disagreements go to a third human adjudicator. Record relevant conflicts and exposure to old/model answers. Agreement is not a truth proof. A model may propose fields/findings but cannot grant itself human authority.

Same-role/same-scope comparison is a precondition for a discrepancy finding. An author citing Merton for a term does not automatically assert sole creation of every associated empirical idea. Source identity, direct passage support, historical interpretation and the applicable credit norm must all be examined. Country flags and generated portraits never supply biographical evidence.

Rates use count numerators/eligible denominators; zero denominators are NOT_DEFINED. For family-macro support accuracy, first compute correct/eligible within each concept family under the same condition/language, then average eligible families. Report exclusions and n; translations do not create extra independent families. Retrieval success, DOI identity, passage support, response correctness, abstention, selective risk and calibration use separate definitions. A zero unsupported-adverse-claim denominator is undefined, not evidence of perfect safety; report coverage/recall separately.

The proposed human-study outcome is a credit share fraction. L24 defines an algebraic narrative-minus-ledger contrast of cue differences. Positive values mean attenuation in the prespecified signed direction; a causal interpretation additionally requires approved assignment and identification assumptions. This is PROTOCOL_DEPENDENT. Population, item/participant dependence, estimand, eligibility, missingness, exclusions, uncertainty and stopping/power parameters require an approved versioned protocol. No measurements or human approvals are supplied here.

Approval binds target bytes and transitive dependencies; changes make effective review stale. ESTABLISHED_FACT needs current scoped support and review. Qualified accounts and open questions may be published only with explicit presentation mode, source limitations and appropriate human/rights review. Source PDF access and human supply do not imply public redistribution. Participant records and sealed gold are not public exports.

Cost configuration and measured usage differ. Report zero API spend only over an explicitly observed interval with declared coverage. Missing telemetry is NOT_MEASURED. API spend excludes electricity, equipment and human effort. No proprietary/paid API or free-tier fallback is a mandatory runtime dependency.

## Preferred Wikipedia intake and mapping

The user-selected intake is https://en.wikipedia.org/wiki/Matthew_effect. The current private source receipt pins a retrieved page revision and byte hash under data/intake/wikipedia/matthew_effect. Basic term/name/role leads are UNVERIFIED_CANDIDATE, not gold or priority findings. The current seed format is an intake note, not conforming records or an executable schema. Map title/labels to candidate lexical forms; explicitly separate senses; map each reported person/relation to contributor and proposed contribution/attribution records; bind all to the exact source version and locator. Wikipedia leads route to primary-source requests before historical adjudication. Full-text fragments, portraits and life dates are not inferred from model memory.

## Change control and conformance

Record definition/catalogue versions, rationale, affected field IDs/rules and compatibility implications. Renaming/reinterpreting codes or changing a metric denominator requires an explicit version change and migration policy; do not reinterpret old records in place. Old Horisma records enter as unverified intake, never as accepted gold. A new field needs type, unit/domain, missingness, provenance, disclosure, examples and logic bindings before use.

The synthetic examples specify acceptance/rejection and rule IDs; they are not an executable production validator. Document consistency checks and finite counterexamples do not establish formal proof. See [formalization conventions](../methods/FORMALIZATION_EN.md) for assumptions, proof obligations and future book/manuscript traceability.

## Standards and scope

The organization follows [DDI codebook guidance](https://ddialliance.org/create-a-codebook) for concepts, cases, variables and missingness; [PROV-O](https://www.w3.org/TR/prov-o/) for entity/activity/agent distinctions; and [SKOS](https://www.w3.org/TR/skos-reference/) for concepts versus labels. These are conceptual alignments, not conformance claims or an RDF dependency. [CRediT](https://credit.niso.org/) can inform crosswalks for contributions to research outputs; it does not decide historical naming priority. Taxonomy releases, source licenses and protocol parameters must be actually verified and bound before use.
