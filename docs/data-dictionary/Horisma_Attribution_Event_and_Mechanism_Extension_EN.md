# Attribution events, mechanism inference and book argument: data dictionary extension

Version0.1.1 —2026-11-05. Status: **PROPOSED_SCIENTIFIC_TEMPLATE_NOT_IMPLEMENTED_ADJUDICATOR**. This extension accompanies the unchanged frozen core and [machine template](../../spec/extensions/attribution_event_template.yaml). It is a reusable design for future terminology cases, not an accepted reconstruction of Matthew-effect history.

## Completeness assessment

The existing core already separates contribution_assertion from attribution_assertion, and discrepancy_finding references both under an adjudication policy. It also defines passage/evidence links, search limits, hypotheses and publication modes. The name/biography extension adds source-bound people, terms and mentions. Therefore a useful logical foundation exists.

The current system is not yet a complete reusable historical-misallocation template. Its missing layer is the explicit case-level join: role/object/time-scoped contribution anchors, observed credit anchors, availability-aware comparison norms, dependent-source transmission, mechanism identification and edition-specific reader arguments. Definitions and candidate records do not demonstrate that these joins or scientific assessments are operationally qualified. Regional fidelity and semantic qualification remain missing in the current pilot.

## A. Two anchored views, with many-to-many roles

“Progenitor” denotes a contributor candidate for a **specified role and contribution object**, within a declared search/time frame. It is not a permanent person category. Naming, concept development, empirical interviews, methods, authorship, translation and popularization can involve different people. More than one person may occupy a role; one person may occupy several roles.

“Beneficiary” is used narrowly as the recipient of credit **in a particular observed account**. A credited actor may also be a legitimate contributor. An actual benefit in prestige, citations, money or opportunities requires a separate measured outcome. Receiving credit neither establishes causing an omission nor establishes misconduct or intent. No required binary victim/offender pair is created.

All fields in this extension inherit exact version references, provenance, missing reasons, disclosure control and revision requirements. Types below are logical record types, not new database tables. Default disclosure is INTERNAL; source-dependent material remains private unless separately eligible. Empty fields use explicit missing reasons. Fields introduced in extension0.1.0 retain that introduction version;0.1.1 records the partial implementation profile and Matthew-first sequence. Responsible scientific assessment is the task-qualified automated lane, with source delivery by humans permitted and no mandatory human evidence adjudication.

| Object and stable field | Definition; type/cardinality; requirement | Provenance/measurement/missingness | Valid / prohibited use |
|---|---|---|---|
| `provenance_case.case_id` | Stable case identity;1 required. | One concept/sense/question/search frame; no metric unit. | A scoped terminology case / a scientist's name as the case definition. |
| `concept_ref`, `sense_refs`, `concept_family_ref` | Exact concept, meaning and leakage-family references;1,1..n,1 required. | Source-supported candidate sense; UNRESOLVED where necessary. | Distinct senses / automatic equivalence from a matching word. |
| `contribution_anchor_refs`, `credit_anchor_refs` | Two collections of exact records;0..n with reasons when empty. | Both can contain several people/roles; readiness separate from assessment. | Many-to-many anchors / forced single originator and wrongdoer. |
| `contribution_anchor.role`, `contribution_object_ref`, `scope_ref` | Role and exact contribution object/scope;1 each required. | Align core contribution roles; source claim and evidence refs mandatory. | Empirical interview materials / treating interviews as proof of naming. |
| `event_time`, `origin_basis` | Original TemporalExtent and basis;0..1 time with missing reason,1 basis. | Preserve calendar, precision and uncertainty. Earliest located is search-relative. | A printed1964 occurrence / an assumed actual presentation date. |
| `credit_anchor.reporting_actor_refs`, `credited_contributor_refs` | Reporter and credited recipients;0..n reporter with missing reason,1..n targets. | Distinguish quoting speaker, document author and credited person. | A source quoting an earlier author / assigning its I to the outer author. |
| `literal_mention_refs`, `reporting_passage_refs` | Unchanged mentions and exact passage versions;1..n. | Resolve names/coreferences separately; unresolved identity blocks assessed allocation. | Source-bound surname candidate / canonical spelling substituted into a quote. |
| `account_time`, `knowledge_availability_refs` | Account date and evidence about knowledge available at that time;time0..1 with reason,refs0..n. | Publication, scheduled event, actual occurrence, retrospective acknowledgment and system revision are different clocks. | Later acknowledgment known only later / anachronistic omission judgment. |
| `measured_benefit_refs` | Optional independently defined benefit outcomes;0..n. | Units, denominator, population and measurement provenance required if present. | Measured citation share / fame inferred from a credited name. |

For the Matthew pilot, the1968 displayed byline, reported interview contribution and later joint-authorship acknowledgment are separate records. Joint-authorship entitlement cannot establish joint coinage. The original1973 item remains a source dependency; its representation in1988 is a retrospective quoted report. These are boundaries of the current evidence, not completed historical verdicts.

## B. Comparison and provenance closure

| Stable field / object | Definition; type/cardinality; requirement | Evidence/measurement boundary | Valid / prohibited use |
|---|---|---|---|
| `credit_comparison.contribution_anchor_refs`, `credit_anchor_refs` | Exact role-scoped anchors;1..n each for a comparison-ready record. | Missing anchors leave readiness partial. | Comparing the same contribution / comparing authorship with a different conceptual role. |
| `concept_sense_comparability`, `role_comparability`, `object_scope_comparability` | Evidence-coded comparability records;1 each. | Not unchecked booleans supplied by the same model; producer and rationale are required. | Bound comparison rationale / a blanket same-person flag. |
| `temporal_frame`, `knowledge_availability_frame` | Contemporary, retrospective or explicitly separated views;1 each. | Availability itself can remain unknown. | Stated retrospective norm / projecting a later correction into an earlier writer's knowledge. |
| `policy_ref`, `genre`, `incompatibility_rule_ref` | Versioned obligation/incompatibility rule and account genre;1 each. | Norm is explicit and contestable. Byline reporting and intellectual-history synthesis differ. | A genre-specific omission criterion / any omission treated as miscredit. |
| `evidence_qualification_refs`, `finding_ref` | Current scoped qualifications and optional finding;1..n qualifications when assessed, finding0..1. | Core five assessments remain distinct from readiness/unassessed. | Unresolved comparison / INSUFFICIENT_EVIDENCE used for every unreviewed record. |
| `provenance_edge_extension.relation_domain`, `relation_code` | Typed bibliography/transmission/assessment/derivation relation;1 each. | Citation, quotation, reliance and support are different edges. | CITES / a citation alone promoted to direct support. |
| `locators`, `rationale`, `limitations`, `qualification_ref` | Exact source/version/region/span and current interpretation;1..n locators,1 rationale/limitations,qualification0..1 while proposed. | Keep reported quotation chains and missing originals explicit. | A secondary quotation of a missing primary source / claiming direct inspection. |
| `source_dependency_group_ref` | Source-family/copying dependence reference;0..1 with UNKNOWN reason. | Correlated copying/OCR channels do not create independent confirmation. | Shared quotation lineage / counting translations as independent sources. |
| `unresolved_dependencies`, `revision` | Exact missing/conflicting/stale inputs and record version;0..n,1. | Update invalidates dependent findings/tasks/editions without deleting history. | Old edition retains its dated status / silently rewriting a past judgment. |

Closure is a traversable, version-bound dependency graph: source work → document/file → location and transcription variants → atomic proposition → evidence relation → scoped contribution/credit anchors → policy-relative comparison → qualified finding → edition argument. Inverse traversal explains which downstream outputs become stale. An inverse dependency edge does not reverse the evidential direction or make a generated book corroborate its own claims.

## C. Mechanism attribution is a separate research problem

| Stable field / mechanism hypothesis | Definition; type/cardinality; requirement | Measurement and identification boundary |
|---|---|---|
| `mechanism_id`, `hypothesis_ref`, `mechanism_family` | Stable mechanism hypothesis and declared family;1 each. | Current examples are proposed explanations, not established mechanisms. |
| `outcome_definition_ref`, `unit_of_analysis`, `target_population_ref`, `sampling_frame_ref` | What changes, for whom, and over which units/frame;1 each, protocol-dependent when unapproved. | A book sentence, attribution event, author, institution and participant are different units. |
| `temporal_order`, `candidate_pathway_refs` | Proposed causal ordering/DAG/variable links;1 plus1..n. | A chronological sequence alone is not a causal identification strategy. |
| `observable_implications`, `discriminating_observations`, `falsification_conditions` | Testable predictions and refuters;1..n each. | Missing observations remain missing; no invented sample size/effect size/power. |
| `alternative_explanation_refs`, `causal_design_ref` | Competing mechanisms and identification protocol;1..n alternatives,design0..1 with reason while proposed. | Consider role compression, source availability, editing/space, translation, status cues and repeated copying. |
| `evidence_refs`, `identification_status` | Exact evidence and stage;0..n,1. | PROPOSED, operationalized, association tested and causally identified are distinct; no causal label from one case/model error. |

“Attribution compression” remains a falsifiable hypothesis. Neither later coauthorship acknowledgment nor an observed erroneous account establishes that prestige, deliberate appropriation, herd behaviour or an information-deluge mechanism caused it. Mechanisms need observations that separate alternatives, suitable sampling and an identification design. Descriptive prevalence needs a defined denominator and source-dependence handling. Actor intent is an independent claim; a structural mechanism does not identify an intentional offender.

## D. Book methodology and reader-facing argument

The reusable method answers five reader questions: what contribution is at issue; which account assigns what credit; why the accounts could differ; what the evidence presently permits; and what new evidence could change the account. Narrative, diagrams and short admissible quotations should carry that reasoning; engineering logs remain private apparatus.

`book_argument_unit` binds an exact edition/paragraph/figure to a reader question, argument role, claim/evidence/comparison/mechanism references, alternatives, uncertainty statement, source snapshot and dependency manifest. Roles distinguish definition, observation, source report, method reasoning, hypothesis, alternative and limitation. Views distinguish reader narrative, optional evidence note, methods appendix and private engineering record. First-person resolution is annotated beside the unchanged quote, never substituted inside it.

The book may explain the two-anchor method before all historical questions are resolved. It must display which comparisons and mechanisms remain proposed. A matching role/name/quote is not a causal finding. Source changes trigger a versioned correction and edition re-evaluation; they do not erase older editions. HTML, print and EPUB derive from the same argument snapshot, with optional interactive detail backed by static captions/notes. This extension defines the methodology; it does not authorize a book export or certify journal compliance.

## Acceptance before adoption as a general template

1. Populate the pilot with explicit anchor and comparison records without promoting its current claims.
2. Test same-person/multiple-role, different-originator/different-namer, accurate-byline reporting, known-vs-unavailable later evidence, missing primary quotation and conflicting contributor identities.
3. Current commissioning stays entirely within Matthew Effect until its shared evidence, scientist/contribution, benchmark and book workflow is exercised. Include accurate-byline and role-noncomparability controls within this case. A second terminology case is an operations-stage portability evaluation, not a prerequisite that diverts current commissioning; do not claim cross-case generalization from Matthew alone.
4. Exercise invalidation from changed source/identity/role/policy through task and edition projections.
5. Keep mechanism hypotheses proposed until their separate empirical identification requirements are met.

Machine obligations HAT-01…HAT-10 are in the extension contract. They are scientific/formalization obligations with UNPROVEN status. No completed proof, historical acceptance or causal result is claimed.


## Current implementation profile

### Structured cards and publication anchors

One event card is one source-grounded proposition about an event. Several source reports can refer to the same historical event; card count is not an independent historical sample size. The implemented partial profile is in `spec/extensions/event_cards.yaml`; the broader family design is in `spec/extensions/research_cards.yaml`.

| Field | Meaning and requirement |
|---|---|
| `card_id`, `historical_event_ref`, `revision` | Stable record/event identities and exact content/dependency revision. Layout order or footnote renumbering does not change identity. |
| `card_type`, `schema_version`, `disclosure` | EVENT, explicit partial-profile version, PRIVATE by default. A renderer cannot authorize disclosure. |
| `event`, `account_date` | Existing typed temporal contract; event time and date of the reporting source are separate. Unknown publication date stays unknown. |
| `time_of_day.scope` | Optional local SESSION_START or reported individual time. A session's15:30 cannot establish a speaker's actual start. |
| `participants`, `object_refs` | Role-as-reported and contribution/event objects; not inferred authorship, naming or joint design. |
| `proposition`, `support_scope`, `limitations` | Reader-facing claim, exact inferential scope and unresolved alternatives; each required. |
| `evidence_node_refs`, `evidence_revisions`, `source_version_refs` | Exact version-bound graph/MD units. Unplaced OCR has no invented passage coordinates. |
| `links` | Typed proposed event relations; generated editorial backlinks do not reverse evidential direction or create corroboration. |
| `assessment`, `readiness`, `missing_dependency_refs` | Null/NOT_ASSESSED versus operational readiness and missing originals; never a single PASS flag. |

Quarto section/footnote labels and Logseq file-graph UUIDs are deterministic mappings of stable IDs. Editions pin revisions. Cross-references do not replace primary-source bibliography. Dates and source requirements inherit the existing dictionary rather than a new card-specific historical standard. No formal proof or qualified historical finding follows from a card export.

The candidate graph0.1 implementation materializes explicit versioned sources/reports/passages, contribution/credit anchors, typed role comparability, missing dependencies and shared task/book-argument revisions. It uses a deliberately partial intake profile rather than claiming full conformance to every proposed field above. Five Matthew comparisons and two method argument units are instantiated. Continuous Markdown unit mappings are retrieval derivatives, not new primary sources; quote/nesting/bracket annotations do not rewrite them or confer fidelity. The full finding/qualification producer, knowledge-availability adjudication, mechanism identification and formal proofs remain unimplemented. See the current implementation plan for measured limits.


Publication naming migration receipts bind old_base/new_base content-addressed snapshots, operator_sha256, the unchanged scientific projection digest and the exact changed input paths. They record zero model/pdf-parse calls and no scientific/release approval. The frozen suite retains its original identity; effective_base_slice_path is an explicitly verified current binding, not a replacement historical source version or new independent observation. Each edition/card continues to bind its own source and argument revisions.
