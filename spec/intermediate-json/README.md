# Horisma normalized intermediate JSON contracts

Version0.1.0 is a structural interchange draft. The frozen English dictionary owns meanings; the frozen YAML vocabulary owns core codes. Generated JSON Schema enforces shape, types, known codes and some explicit conditional requirements. It does not implement every scientific obligation, resolve every cross-record reference, qualify a model, or authorize publication.

Start with [the index](v0.1.0/index.json) and [stage interfaces](v0.1.0/stage_interfaces.json). Every one of the55 core dictionary objects has a schema and a template. Six explicit intermediate profiles cover parse units, entity mentions, citation objects, event cards, manuscript units and pipeline packets. Shared structured values and vocabulary projections reside in [shared.schema.json](v0.1.0/shared.schema.json).

LLMs should load the index and only the selected stage/schema, never glob this entire generated library into context.

The normal route is source/work/version → parsed unit → entity mention → citation object → atomic claim/evidence link → review/event → manuscript unit/edition. Dataset, model-response, metric, study and operations records use the same versioned catalogue. A stage packet carries immutable record/artifact references and execution status. Execution success is separate from scientific review.

## Templates, records and old formats

`*.template.json` is a blank scaffold explicitly marked `template_only`. Its null required fields make it an invalid observed record. It supplies field definitions, types, units, obligations and examples inherited from the dictionary. It is not sample data or evidence that an operator is implemented. `PROPOSED` and `PROTOCOL_DEPENDENT` stages remain visible.

`*.schema.json` validates a filled interchange record. The55 core profiles preserve the dictionary's UUID4 entity/record identities. Existing case/card identifiers are not silently rewritten to meet them. Extension `BoundRef` explicitly retains the existing identifier, a revision digest and a binding kind distinguishing source bytes from record revisions. Old native outputs need named adapters; the stage map marks that migration incomplete. Do not maintain new parallel factual authorities.

Missingness uses record-relative JSON Pointers. Null or legitimately omitted optional fields require a catalogue reason. A null parent has a parent reason; absent descendants do not get invented reasons. Known zero, false, empty collections and uncalibrated confidence remain different. Citation confidence is currently null, never a guessed probability. Core status domains stay separate.

## A citation is a source-bound object

[citation_object.template.json](v0.1.0/citation_object.template.json) separates the witness work/version, bibliographic authors, page/region and exact text span, source kind, reading/diplomatic views, declared transformations and abbreviation candidates. The referenced earlier work is distinct from the available witness. An indirect quotation cannot assert that the earlier original was inspected. Evidence groups prevent copied passages or a reported earlier quotation from becoming independent sources.

Eight real private Matthew candidates are under `data/intermediate/citation_objects/matthew-candidates.v1.json`. They cover1964 notice/programme material,1968 byline/interview/delivery passages, the1988 acknowledgment, the uninspected1973 account quoted through1988, and the1967 programme. Five distinct witness document versions do not imply five independent sources. Two1964 items currently use explicitly labelled frozen-fragment exceptions because no final Paper2Skill entry is registered for them; they are not disguised as packaged readings.

These objects link to the four provisional research results and current reader manuscript. They remain candidates with unverified source identity and no historical-gold/publication flags. The source-backed research account is usable as a draft while uncertainties remain attached to affected propositions.

## Local use

Regenerate from unchanged authorities with `scripts/horisma_p0.py research-json-templates` using the project interpreter. Generated files should not be hand-edited. Change the generator/extension version when releasing changed meanings; never reinterpret a frozen source contract in place.

Validate one filled record with `scripts/horisma_p0.py research-json-validate <record.json>`. Validation reports structural/byte conformance and explicitly says reference closure is not checked. Citation validation checks exact UTF8 artifact bytes, Unicode span and record revision. It rejects invented confidence, unknown fields, mixed status codes and silent citation edits. Some equality/non-null conditions, locator bounds, temporal ordering, allocation normalization and metric undefinedness have executable checks; other semantic conditions remain explicitly unimplemented.

The current operating policy remains local automated review or abstention. Archived vocabulary/historical dictionary wording does not reinstate a mandatory human evidence-review queue. Participant-study ethics and publication accountability are separate requirements.

No private PDF, original extraction, sealed labels, raw model response, live citation record or unapproved manuscript belongs in the technical schema export.
