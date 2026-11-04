# Horisma formalization and scientific inference contract

Version 0.1.0; 2026-11-04. Status: specification, not a checked formal theory. No theorem, empirical hypothesis or historical priority claim has been proved by this document.

## Authority and notation

The [data dictionary](../data-dictionary/Horisma_Project_Data_Dictionary_EN.md) defines entities and measurements; [vocabularies](../../spec/controlled_vocabularies.yaml) define codes; the [logic catalogue](../../spec/logic_catalog.yaml) registers obligations L01–L40 and D01. [Synthetic scenarios](../../spec/examples/data_dictionary_examples.yaml) record expected outcomes. All current catalogue obligations are unproved. Production schemas, validators, transactional storage and Lean integration belong to later implementation.

Use many-sorted first-order specification notation, finite sets and rational arithmetic. `forall`, `exists!`, implication and equivalence carry their usual scoped meanings. An expression with conditional expectations is a proposed statistical definition, not a first-order proof. Catalogue formulas are a reviewable intermediate representation; semicolons separate obligations. A prover must receive an explicit encoding, with complete signatures and no implicit coercions.

`Record` denotes an immutable record version; `Claim`, `Finding`, `Job` and `Score` are specification aliases for atomic_claim, discrepancy_finding, operator_run and a declared model/metric observation. Other CamelCase sorts map to the identically named snake_case dictionary entity or value type. `WriteEvent` and `ServiceCall` are future operational observations, bound to a run configuration and receipt, not historical entities. `Field` is a registered field path, including a structured member. Equality compares IDs/versions or declared typed values, never names, filenames or semantic similarity scores.

For every field f of type T_f, `Value_f : Record -> Option[T_f]`. Missing means None, with exactly one registered reason. Observed zero, false and an empty set/list are Some values. `UNDEFINED` represents None for a partial mathematical quantity; it is not a rational number. Functions such as date bounds and division are used only under their defined-domain guards. An absent proposition is unknown; do not apply a closed-world rule to history.

The missingness quantifier ranges over fields applicable to the record type with a present parent structure. A null structured parent has one reason at its own path; nonexistent descendants do not each require a reason. Conditional requiredness mandates a receipt when an accepted status requires it; otherwise pending records may retain actual artifacts without claiming acceptance.

`does_not_entail` is metalanguage identifying a forbidden automatic promotion. It is not object-level negation or an executable connective. Operational auditing must show the promotion cannot occur from that premise alone. A mathematical non-entailment proof would additionally require a specified model class and countermodel. Those are not supplied here.

## Grounding the predicates

The following bindings constrain how a future implementation may interpret the catalogue. They are semantic contracts, not currently implemented Boolean functions. Every evaluation must retain exact inputs, policy version, evaluation time, reviewer authority where applicable, and an explicit unknown/error outcome when prerequisites are absent.

| Predicate or function; typed arguments | Required grounding and boundary | Catalogue |
|---|---|---|
| ExistsExactVersion(Record), References(Record,Record) | Immutable record_id resolution and retained history; supersession and derivation are acyclic | L01–L04 |
| IdentityVerified(DocumentVersion), PassageBoundTo(Passage,DocumentVersion) | Actual identity review plus source bytes/hash and exact locator/derivative binding; a DOI lookup alone is insufficient | L05 |
| CurrentIndependentTranscriptionReview(Passage) | Independent wording comparison against the original source image/text, bound to exact source/derivative/locator and retained raw OCR/corrections; assessors reading only the same derivative are insufficient | L36 |
| InScope(Passage,Claim), Supports(Passage,Claim), Mentions(Passage,Claim) | Independently annotated proposition, role, period and scope under an exact adjudication policy; no truth oracle is implied | L05–L08 |
| SameConceptRoleScope(Finding) | Explicit concept/sense alignment, equal contribution role, comparable attribution scope and declared time/genre domain; comparison_kind alone does not establish the facts | L09–L10 |
| PolicyQualifiedCreditConflict(Finding) | D01 requires either an explicit role/priority assertion contradicted under the policy, or omission of credit required by a stated norm; missing a name alone is insufficient | L09, D01 |
| CurrentComparedEvidence(Finding), IndependentHumanReview(Finding) | Bound evidence and at least two independent human annotations, retained disagreements and third-person resolution where needed; a model vote is not human review | L09, L11 |
| KnownValidNormalizedBounds(TemporalExtent), JustifiedCalendarAlignment(TemporalExtent,TemporalExtent) | Original text, precision, calendar and justified normalization receipt; both bounds known and lower<=upper. Unknown order is not a negative ordering fact | L12–L14 |
| RequiresHumanSource(Job,DocumentVersion), LeaseReleased(Job) | Blocked dependency and independent human-source request; acquisition stops, owned work closes, lease is released. Resumption rechecks identity and operation-specific rights | L15–L16 |
| EffectiveApproved(ReviewDecision,Artifact) | Approved event by an authorized human for the exact kind/use/scope, matching target digest, current transitive dependencies, no effective revocation | L17 |
| CanRelease(BookEdition), AssertedFacts(BookEdition) | Exact bundle manifest, per-claim publication mode and current scientific, language, rights and release reviews. Only established facts enter AssertedFacts; qualified accounts/questions retain visible qualifications | L18 |
| SameDatasetVersion(Task,Task), Family(Task), Split(Task) | Resolve each task through the frozen dataset manifest and its concept-family split assignment; translations/aliases do not become independent families | L19, L35 |
| Rate(Integer,Integer), Macro(FiniteSet[ConceptFamily]) | Eligibility, counts, condition/language and excluded families must be declared. Empty eligible denominators yield None, never zero | L20–L21 |
| ModelSelfRating(Score,Claim), CompleteValidAllocation(CreditAllocation) | Uncalibrated self-rating, token softmax and independently calibrated task-correctness probability are distinct; allocation shares are fractions with declared tolerance and raw response retained | L22–L24 |
| RuntimeServiceCall(Run,ServiceCall), SourceRetrievalCall(Run,ServiceCall) | Separate call classes. Inference/translation/portrait/judging use controlled local, appropriately open-licensed resources; lawful source retrieval can use explicit public endpoints | L25–L26, L34 |
| PublicExport(Artifact), IncludedPayloads(Artifact) | Inspect transitive included payloads and metadata, not merely top-level filenames. Each needs eligibility, operation-specific rights, authorized public projection and current export review; no sealed or restricted data | L27, L35 |
| FormallyProved(ProofRecord), EmpiricalHypothesis(Hypothesis) | Exact statement/assumptions/proof/toolchain plus independent checker receipt; empirical findings remain evidence-based rather than logical axioms | L28–L29 |
| ConcurrentGPUOwners(Run,Run), AutomaticRecovery(RecoveryEvent) | Finite resource ownership and actual process closure before retry/reassignment; accepted research manifests remain unchanged | L30–L31 |
| GeneratedPortrait(Artifact), HorismaWrite(WriteEvent) | Portrait provenance cannot establish biography. Resolve paths including links/reparse points; all scientific outputs/logs/caches/temp/exports stay in Horisma-owned declared roots | L32–L33 |
| Processes(Run,Artifact), CurrentRightsDecision(RightsDecision) | Affirmative permission for the exact bytes/operation with satisfied conditions. Source-file/artifact wrappers bind the same payload path/hash; permission for another artifact or use is insufficient | L37 |
| UniqueFrozenEvaluationContext(ModelResponse) | One exact dataset/task/target/gold/scoring-policy plus actual prompt/evidence-access receipt; a task shared across releases cannot supply implicit context | L38 |
| ValidFamilyPartition(DatasetVersion) | Canonical one-version-per-family mapping, bidirectional concept membership and task/claim/concept/family consistency checked before split equality | L39 |
| ValidAssignment(ConditionAssignment), ResponseActorSet(ConditionAssignment) | Cue recipient and response actor set belong to the assigned vignette; complete allocation domain equals that set and the actual delivered stimulus/format/cue is bound | L40 |

At P0, compile these meanings into explicit predicate signatures and executable checks for the selected slice. Unimplemented predicates must remain unimplemented/unknown. Defining `PolicySatisfied` as always true, or assuming a historical conclusion as an axiom, invalidates the intended interpretation even if a proof kernel accepts the resulting theorem.

## Explicit credit-conflict definition

For a finding f, define:

```text
Conflict(f) := ExplicitRolePriorityContradictedUnderPolicy(f)
               OR OmittedCreditRequiredByExplicitNorm(f)

SupportedDiscrepancy(f) := SameConceptRoleScope(f)
                          AND Conflict(f)
                          AND CurrentComparedEvidence(f)
                          AND PolicySatisfied(f)
                          AND IndependentHumanReview(f)
```

Both conflict branches need a bound attribution statement, contribution evidence and a versioned comparison norm. The omission branch must identify the specific genre/scope where credit was obligatory and demonstrate the omission within that inspected scope. It cannot infer deception, plagiarism, appropriation or legal ownership. Agreement, unequal fame, different roles and earlier dates alone do not satisfy Conflict.

An earliest-located statement quantifies over the inspected, versioned search scope S: evidence located within S has no earlier eligible witness *in S*. It does not quantify over all historical evidence. Incomplete search, inaccessible archives and uncertain dates remain explicit limits. A programme witnesses scheduling; actual delivery requires different evidence.

## Proposed statistical definitions

A rate k/n is defined only for integer 0<=k<=n and n>0. A family macro score averages the defined within-family rates over eligible families; report the family denominator and exclusions. A zero numerator with a positive denominator is a measured zero. No eligible observations means undefined. Multilingual duplicates remain grouped.

For the proposed behavioural study, Y_A is credit assigned to fictional actor A, on [0,1]. Define Delta(f) as the conditional mean difference when the randomized prestige cue is assigned to A versus B, within format f. The proposed contrast is Delta(fact-matched narrative) minus Delta(ledger). Its positive direction is algebraic attenuation of the prespecified signed contrast. Random assignment/identification, consistency, eligibility, participant/item dependence, missingness, uncertainty and stopping rules require the approved protocol before any causal interpretation. No sample size, effect size, human approval or observed result is supplied here.

## Proof and manuscript traceability

Use the chain `research question -> exact protocol -> field/input versions -> logic_id -> implementation/check receipt -> scoped result -> manuscript/book claim`. Every manuscript proposition must identify whether it is a definition, methodological condition, synthetic example, historical assessment or empirical estimate. A receipt showing valid JSON, successful code execution or an accepted formal derivation does not substitute for missing evidence.

A future proof record must bind the exact typed statement, all assumptions, proof artifact hash, compiler/kernel/library versions, options, allowed axioms and independent verification receipt. Unchecked axioms, admitted obligations and placeholders prevent proof acceptance. Require an admissible positive witness, a negative control rejected for the intended reason, and nonvacuity checks. Finite tests inspect cases; a proof verifies the encoded proposition under its assumptions. Neither proves that an empirical premise is true.

Changing sources, policies, statements, estimands, code, proof assumptions or translations creates new versions and invalidates affected approvals/derivations. Preserve the old record and provenance; do not rewrite prior findings to restore a green status.
