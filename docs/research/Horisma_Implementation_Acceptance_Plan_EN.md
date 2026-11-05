# Horisma implementation and acceptance plan

Revision0.2.0,2026-11-05. Implements the current [research proposal](Horisma_Terminological_Provenance_Project_Research_Proposal_EN.md). This replaces the former serial sequencing and mandatory human-evidence-review profile. Frozen P0 files remain unchanged.

## Current delivery unit

A private, reproducible research slice connects source/version custody, concepts, people, contribution assertions, passages, review prerequisites, development tasks and chapter projections. Source aliases are compatibility labels; stable work/version IDs identify the evidence. The current integration sample is two people, five assertions and eight tasks. The separate28-candidate P0 ledger is not promoted.

## Shared commands

Use the project virtual environment and explicit Horisma root:

```
.venv/Scripts/python.exe scripts/horisma_p0.py research-build
.venv/Scripts/python.exe scripts/horisma_p0.py research-check outputs/research-slices/<digest>
.venv/Scripts/python.exe scripts/horisma_p0.py research-ocr outputs/research-slices/<digest> --model-dir <existing-local-ocr-model-directory>
.venv/Scripts/python.exe scripts/horisma_p0.py research-evaluate --candidate gemma3:12b
.venv/Scripts/python.exe scripts/horisma_p0.py research-route outputs/research-slices/<digest> --screen outputs/model-screens/<run>/report.json
```

`research-build --ocr-model-dir <directory>` combines deterministic rebuilding and image-derived OCR comparison. `ops/state/research-slice-head.json` identifies the latest built slice; it is an operational pointer, not acceptance. Compatibility region/asset scripts delegate to the shared builder. Earlier development scripts and exporters remain non-release tools.

## A. Integrated identity, schema adapters and invalidation

Source versions and private derivatives are preserved in an immutable content-addressed vault. Person assertions project existing role codes: displayed author→AUTHORSHIP, interview contribution→EMPIRICAL_BASIS; retrospective acknowledgment remains an event. Partial record profiles are declared, not passed off as complete dictionary records.

Coordinate conversion retains PDF points, dimensions and normalized regions. Chapter citations include exact paragraph hashes, evidence-unit references and source-derived passages. Whitespace normalization is explicit and separate from raw extraction. Frozen contracts are not edited to accommodate an adapter.

Acceptance: identical deterministic inputs rebuild the same slice; changes to source, assertion, chapter or relevant implementation invalidate current consumer eligibility. Vault artifacts remain available for historical replay. Stale checks exit nonzero. Atomic writes do not replace prior immutable artifacts.

## B. Historical-document fidelity and custody

Five regions must have an actual image/OCR comparison or a concrete failure. Preserve source, crop, native text, OCR, diff, model hashes and operation context privately. A title-only crop cannot support an opening-paragraph claim; the1968 region now includes title, byline and opening. The1964 preview also includes its printed date. Context selection and OCR correctness remain different checks.

Printed512 of the supplied Price PDF is index3 because of its cover sheet. Preserve correction provenance. Never infer PDF index from printed page subtraction alone.

Acceptance: all five comparisons are present, corruption and stale evidence are rejected, and missing OCR models yield explicit failures. Agreement—including1.0—does not by itself qualify historical text. Sentence splitting is a candidate locator, not automatic atomicity or complete-context acceptance.

## C. Evaluation, failure replay and routing

The three retained StartLux failures are replayed from hash-bound original responses. Literal replay diagnostics are distinguished from general semantic judges. A frozen24-case synthetic corpus has12 development and12 locked-screen cases; its constructed labels are not historical gold and its near-template scope does not establish generalization.

Actual first screen: StartLux10/12 locked cases; Gemma3:12b12/12. Both produced24 structurally valid outputs. Measured generation-call totals were approximately12.8s and31.1s respectively; these exclude model loading and are not end-to-end throughput claims. The original run completed results but exited with a Windows lock-cleanup error, corrected and regression-tested afterward; do not rewrite the original receipt as successful execution.

Routing prefers a passing scoped synthetic candidate before speed. Screen corpus and current model digest are checked; active unrelated workloads are not unloaded. Candidates remain diagnostic-only until actual task qualification. Changes to source packets create a new diagnostic context; completed contexts are reused rather than regenerated silently. No model/publication policy promotes itself.

Acceptance: full request/response/configuration binding, explicit denominator, failures and abstentions. No historical accuracy without qualified labels. Per-case timeout45s, initial load90s, no case retries; maximum baseline plus one candidate per screen. Do not expand to a third model during this slice just to obtain a pass.

## D. Scientific argument and reader value

Series: Credit Where Credit Is Due. Book: The Matthew Effect. Chapter one starts with recognition of comparable contributions and then distinguishes visibility, evaluation, memory and resources. Concept history enters as an example, not the entire chapter.

Merton1968 reward/communication passages and Merton1988 caution about extrapolation have been read locally. Huber's main-text methods, results and limitations were inspected, including institution-level randomization and reviewer-level recommendations. The supplement retrieval timed out; no supplement or data replication is claimed. See the chapter realignment document for the phenomenon/mechanism/evidence/alternative/remaining-observation matrix.

Acceptance: sixteen mapped paragraphs, including an explicit imagined opening, source-reporting passages and separate hypotheses. No new animation, print/EPUB batch or claim of a completed book. Format exporters declare development-only output and use the agreed titles.

## EIDOS reuse and acceptance boundaries

Use the installed, wheel-hash-verified EIDOS Agent0.5.0 worker for project-local checks, immutable run receipts, freshness/status and local feedback. The Horisma adapter calls the shared domain validator using the project interpreter. It must refuse scientific acceptance while region/reviewer/support prerequisites remain unmet. EIDOS metadata and Horisma research state stay project-local; no new dashboard, cron, package upgrade or central enrollment.

EIDOS's generic scientific gate is not automatically a qualified historical-attribution reviewer. Empty domain claims or unresolved prerequisites remain refused. Feedback bundles contain technical descriptions only and are not automatically uploaded or marked fixed.

## End-of-slice acceptance

Report four dimensions independently: engineering integrity; qualified evidence; evaluation validity; reader-value candidate. Public release additionally needs exact-bundle rights/editorial/format evidence. Trusted producer registry is currently empty; positive receipt paths are tested only with synthetic fixtures.

Before a technical milestone: run the relevant unit/integration tests, frozen P0 validation, deterministic rebuild, actual OCR and model report inspection, stale-input rejection and independent code review. Then inspect a strict Git allowlist. Private PDFs, vault blobs, extracted passages, responses and unapproved book prose must not be staged. No scientific-release claim follows from a technical checkpoint. Unattended operation still requires recovery controls and a real24-hour shadow run; behavioural research needs its own protocol/ethics path.

## Parser route extension: anymd and Docling (same slice)

The user-selected mature tools were tested, not accepted from their README claims. anymd8.5.9 was isolated under .rebuild/tools with npm lifecycle scripts disabled; its native binary is pinned by hash. No global MCP setup, hosted parser or paid Pro cite-check was enabled. Existing Docling2.140.0 ran all five selected pages offline with cached layout weights and existing local RapidOCR. Docling2.147.0 was separately installed in an isolated sandbox and passed a one-page CPU smoke test; it did not replace the existing CUDA research environment.

The four older pages are image scans with hidden text. anymd's no-OCR path returned only watermark/terms text and found0/3 target terms on each. Its born-digital news-page output found3/3 target terms. Docling found3/3 retrieval terms on all five pages and provided labels/geometry; this is target coverage, not transcription accuracy. One news item's charspan exceeded its text length and was quarantined rather than clipped into apparent validity. Several merged or over-broad paragraph contexts still require examination.

Use research-parse --backend auto --source-id <1..5> [--ocr-model-dir <existing directory>] for heuristic task routing. The route registry selects offline Docling layout/OCR for scans or mixed pages and pinned anymd native extraction for born-digital pages. research-parsers <slice> builds the private comparison with normalized geometry and preserved outputs. Candidate parser passages remain separate from accepted scientist assertions or benchmark gold.

Docling reported generation/conversion times of roughly6–14s per selected page in the existing runtime, excluding Python import/startup; anymd native conversion was subsecond but omitted the old scanned-page contents. The2.147 CPU smoke took about28s for the1968 page. Different runtime/device modes prevent interpreting that as a version-level speed ranking. This is a five-page purposeful diagnostic sample, not a general parser benchmark.

## Critical layout audit: names, dates, footnotes and continuations

2026-11-05. `research-audit <slice> --model-dir <local weights>` consumes sealed Docling attempts and checks eight declared targets against source-bound native text and regional image OCR. It records critical-name/number differences, empty channels, unfinished quotation/parenthesis context and probable cross-column merges. These are development diagnostics, not transcription or historical acceptance. Name matching currently covers the declared Merton/Zuckerman variants, not general named-entity validation.

The1964 programme's Matthew-effect entry was merged with a different session in a Docling item. Its actual continuation, “scientific communication” and Merton's name, was independently located in the original PDF's next column and region OCR was retained. The1968 first-clause item spanned two columns; a source-column recovery candidate retrieves the complete left-column opening instead. The preview's left-to-next-column relation remains a proposed continuation, not an automatically joined authoritative quotation.

In the1988 footnote, native hidden text contains Harniet and a damaged19731 token while Docling/image OCR produce Harriet and1973. No spelling/year is silently replaced. The repeated image OCR shares RapidOCR weights with Docling and does not constitute independent model or independent historical corroboration.

For tiny crops with empty OCR, one8-point context expansion is permitted, clamped to actual PDF dimensions; both attempts are retained. Missing text channels are not labelled contradictions. Float differences between Docling page dimensions and the actual PDF boundary are handled at the crop boundary rather than accepting out-of-page coordinates.

Diagnostics project to the five current assertion revisions and eight task revisions; missing source diagnostics remain explicit. No scientist field, historical gold or score is promoted. Next: evaluate the recovered column fragments as new context packets, include negative/context controls, and qualify image/text fidelity before any source-support acceptance. No new model call, paid service, human evidence-review queue or GitHub push is part of this audit.

## Transcription correction and overcorrection gate

2026-11-05. The PDF lane now has a separate correction-proposal primitive and a protected-edit gate, governed by spec/extensions/transcription_correction.yaml. Raw source, native extraction and original OCR stay unchanged. Three views are explicit: diplomatic transcription, tracked typography normalization and separately labelled editorial prose. Grammar correction is forbidden in diplomatic and normalized views. Editorial derivatives are never eligible as verbatim quotations.

Edits bind exact input hashes and unique source substrings resolved to Unicode offsets. Stale, overlapping or ambiguous proposals are quarantined. The gate checks identities, number/sign/comparison expressions, negation including contractions, modality, contribution roles, quantifiers, citations and quotation marks, plus a bounded rewrite fraction. These are conservative heuristics, not a proof of semantic equivalence. Critical edits cannot self-authorize from a model's rationale; OCR repairs remain blocked pending qualified image and semantic evidence. No correction grants historical acceptance.

The existing local Gemma3:12b vision backend was screened on four synthetic image controls before real-region use. It preserved three but changed deliberately printed limitted to limited, failing literal-preservation screening. Real PDF visual-transcription requests were therefore abstained; no qualification was granted. This demonstrates why fluent OCR-like output is not faithful transcription. Image/prompt/model identity and responses are preserved privately.

StartLux remains first for bounded correction proposals. Its real footnote proposal contained a nonexistent exact anchor, attempted19731→1973, and attempted to change the original wording This is occasion to This is an occasion. The whole invalid proposal was quarantined. Per-edit deterministic replay separately exposes the invalid anchor, protected numeric edit and forbidden grammar-in-quotation edit. A line-break proposal remains image-review dependent. The source text was not changed.

Unambiguous synthetic editorial positive controls were also run locally: These results is preliminary→These results are preliminary and The estimate is limitted→The estimate is limited. Both produced EDITORIAL_DERIVATIVE_ONLY, never a verified source transcription. The initial data is example was not treated as universally erroneous; it was replaced as a positive control by the unambiguous plural-results case.

Use research-correct <slice> --audit <sealed-layout-report> for bounded screening/proposals, or --replay <retained-report> to apply the current gate to preserved model responses with zero new model calls. Missing audit input produces abstention rather than mandatory human review or a missing-field crash. The four-control screen is only a stop/go development check, not general OCR qualification. The next bottleneck is an independently task-qualified visual backend and per-edit image evidence; do not loosen preservation rules to obtain more corrections.

## Expanded literal screen and PaddleOCR candidate

The frozen twelve-case corpus in spec/examples/visual_literal_challenge.json covers printed spelling/grammar errors, corrupted names/year brackets, negation, modality/roles, signed numbers, comparison operators, event/date scope, an open quotation, a footnote marker and a continuation fragment. These are clean single-font synthetic stop/go controls, not degraded historical-page gold. Freeze a new version for new challenges rather than silently tuning this corpus.

The existing Qwen tag qwen3.8:27b reported qwen35 family,27.3B Q4_K_M, but the bounded run timed out before any control response: zero attempted, twelve unrun, no accuracy score or historical input. Subsequent operator revisions record the failed phase and cleanup outcome explicitly; they do not rewrite the original run. No paid fallback or repeat with a larger budget was used.

PaddleOCR3.7.0 and PaddlePaddle3.3.1/PaddleX3.7.2 were installed into a separate Python3.12 CPU environment. The existing project CUDA runtime was untouched. Official English v5 recognition and mobile detection models were downloaded at pinned repository commits, with file hashes and a local environment lock. This selects a different recognizer from existing RapidOCR v6 weights, while retaining their shared PaddleOCR lineage limitation. During inference, local model paths are explicit and Python socket.connect attempts are blocked; this is a process-level Python control, not an OS network-isolation claim.

Use research-parse --backend paddleocr --source-id 4. This explicit lane runs the same twelve controls and only then a preserved source/version-bound regional image. It does not change automatic routes. First screening passed12/12; the extended run repeated12/12 and read the1988 footnote. It preserved This is occasion and produced Harriet/[1973], but concatenated the citation page range159-175 into159175. Whitespace-folded native/OCR agreement was about0.997; the critical discrepancy still blocks fidelity qualification. Neither unqualified channel is treated as ground truth. No original extraction, assertion, task label or chapter quotation was automatically replaced.

The parent passes an exact slice path/digest; the child cannot follow a moved head. A150-second process budget retains stdout/stderr and removes only its own terminated-process lease on timeout. Reports bind corpus/font/model/producer hashes; deterministic sealed-output diagnostics compare protected signatures and reference current scientist/contribution/task projections. Historical and publication eligibility remain false. Tests cover head movement, source corruption, malformed corpus identity, model unavailability, first-control stop and foreign-lease preservation.

Next acceptance target: freeze citation-range/bracket/quotation and degraded-print controls, then evaluate PP-StructureV3 on the known1964/1968 column failures. PaddleOCR-VL is a separate optional regional candidate, not yet installed or executed as a model. Official references: [repository](https://github.com/PaddlePaddle/PaddleOCR), [installation](https://www.paddleocr.ai/latest/en/version3.x/installation.html), [PP-StructureV3](https://www.paddleocr.ai/latest/en/version3.x/pipeline_usage/PP-StructureV3.html), [PaddleOCR-VL](https://www.paddleocr.ai/latest/en/version3.x/pipeline_usage/PaddleOCR-VL.html). No general OCR ranking or scientific acceptance is inferred from this one-region trial.

### Complementary channels and local variant records

No single toolkit is required or assumed to solve every part. Separate custody, layout/reading order, glyph transcription, critical-field preservation and semantic support. Tool eligibility is scoped to its measured task and evidence unit. Failure in one span does not erase other candidates, while no unqualified span becomes a quotation through another tool's fluent completion.

The shared research-crosscheck command reuses four preserved channels with zero inference calls. The current1988 adapter probes contributor name, bracketed year, citation volume/page range, printed grammar and joint-authorship modality. Its reusable variant-ledger primitive retains exact per-channel offsets, all matches, missing/ambiguous status and literal differences. It records differing crop boundaries and shared model lineage. RapidOCR and Docling are correlated channels; v5/v6 are related recognizers; multiple outputs are not multiple independent historical sources.

The actual record exposes three literal disagreements: contributor spelling, damaged year bracket and citation-range punctuation. Printed grammar and joint-authorship wording match within the declared probes but remain unqualified. A regex nonmatch means not located by that probe, not absent from the source. No majority vote, merged text, accepted witness or automatic correction is produced. Critical unresolved spans become bounded next-crop/recognizer targets; support and attribution review still require qualified evidence credentials. This is complementary observation, not automatic truth synthesis.

Scientist-name infrastructure now has a source-bound person/name-form/mention development adapter governed by person_names.yaml0.2.0. It covers reported full/initialled/alias/multilingual forms, explicit given/family components and context-bound short mentions, with source validity gaps. The two scientists remain partial candidates, not a complete authority database; the earlier five regex probes are separate diagnostics. No preferred spelling automatically corrects source text or establishes contribution credit.

## Scientist identity, terminology and coreference increment

The project-local shared entry points are research-entity-sources, research-entities-build, research-entities-check and research-entities-evaluate. A bounded, free public-metadata acquisition captured the Wikipedia-to-Wikidata bindings for the two people and Matthew-effect concept plus referenced name components/country. Direct TLS access timed out; the host's existing proxy configuration succeeded. No private PDF/text was transmitted. Captured revisions/bytes support offline rebuilding; cache reuse rechecks binding bytes, mapping, primary catalogue and index keys.

Authority labels/aliases are reports about forms, not qualified historical identity. Exact scalar offsets and JSON Pointers bind each observation. Given/family components retain both explicit person-to-component properties and component-label sources; token order is not guessed. A source alias can contain initials; observable shape is recorded without expanding it. Name language coverage reports snapshot availability, not global completeness. Accumulated/cumulative advantage remains a related mechanism rather than automatic term alias. Concept sense remains unassessed after a lexical match.

The private pilot contains two source-reported scientist profiles and one concept. Source attributes preserve upstream statement IDs, ranks, values, references and temporal qualifiers. Citizenship, nationality, birthplace and sex-or-gender constructs remain distinct. Local flag-icons7.5.0 under Country-flags supplies hashed SVG/license associations via source-reported ISO codes; historical appropriateness and display eligibility remain unresolved. Portraits are not generated or inferred. The data dictionary now specifies these fields and the implemented partial-adapter boundary.

Mentions bind untouched source/channel text and exact offsets. Family/given short forms need scoped full-form context. Same-name candidates remain ambiguous. Harniet is retained as an OCR/unlisted-name hypothesis, not added to aliases. Stable occurrence IDs are separate from decision revisions. Coreference is a conservative English candidate layer: ambiguous/unresolved prior people remain possible antecedents, unregistered capitalized spans block false uniqueness, and first person requires a bound speaker. An outer author does not automatically own quoted I/we. Paragraph/quotation boundaries are preserved. No text is substituted and no QUALIFIED_LINK is emitted.

Native and preserved crosscheck channels feed typed candidate mention/coreference edges and exact revisions of the existing eight development tasks. Correlated channels remain distinct observations of the same source, not independent historical samples. Historical gold/accuracy stay null. The frozen thirty-case synthetic challenge covers full/alias/initialled/short/multilingual forms, homonyms, OCR corruption, source scope and coreference. Passing it is rule regression evidence, not LLM capability, historical accuracy or generalized NER recall.

### Critical pipeline audit and ordered improvements

| Failure mode | Implemented constraint / observation | Next measurable acceptance |
|---|---|---|
| Wrong crop, double-column fusion, missing footnote | Source/page/region and geometry retained; known column defects remain candidates. | Same-page reading-order/continuation challenge before parser promotion. |
| OCR fluency or high agreement hides a critical error | Native/Paddle/Rapid/Docling raw variants retained; citation separator loss remains unresolved. | Frozen degraded-print, range/bracket/name/negation controls and image-bound per-span checks. |
| Missing extraction interpreted as absence | Missing/ambiguous probes and unknown fields stay explicit. | Report coverage against a declared, qualified observation frame; no blanket absence claims. |
| Cached authority records or Wikipedia binding swapped | Byte hashes, QID index keys and catalogue mappings revalidated offline. | Corruption and swapped-binding tests must reject without network fallback. |
| Short-form narrowing leaves another person's form ref | Candidate forms filtered to retained entities; original lexical matches preserved separately. | Mention→form→entity join checks and same-surname counterexamples. |
| Ambiguous/abstained names dropped from antecedents | All potential prior person candidates retained; unknown capitalized spans block uniqueness. | Blind ambiguous/unknown-entity contexts; no complete NER/coreference claim from current rules. |
| Quoted speech assigned to the outer author | Speaker evidence and quotation ownership separated; common quotes/paragraphs constrain scope. | Nested/fragmented/historical and non-English quotation tests; currently incomplete. |
| Related mechanism or translated name becomes a synonym/identity | Candidate term relations and form provenance remain separate from sense/identity. | Comparative sense/context cases and additional language sources before equivalence qualification. |
| Correlated outputs become majority truth | No merged quote, vote or automatic acceptance; coupling and regional scope retained. | Task-qualified regional fidelity and heterogeneous semantic review, still missing. |
| Biography or current flag is projected across a whole life | Source qualifiers/precision preserved; historical flag appropriateness unestablished. | Temporal biography/territory mapping tests, without guessing unknown years or nationality. |

Core obligations: every textual occurrence round-trips its offsets; same spelling does not entail identity; alias observation does not entail concept equivalence; coreference candidates never rewrite evidence; source/code changes invalidate dependent profiles/tasks; accepted identity/transcription remains false until the qualified lane supplies scoped evidence. Tests exercise these invariants; no formal proof is claimed.

Parser expansion is task-driven. [MinerU](https://github.com/opendatalab/MinerU) is registered as documentation-reviewed, not installed or executed. Its local structured/layout path is a candidate for the existing five-page comparison; code and model terms and offline mode must be pinned first. Marker is explicitly excluded at the user's request and will not be installed, called or benchmarked. Existing Docling/PaddleOCR routes remain; no hosted parsing or paid API is introduced.
