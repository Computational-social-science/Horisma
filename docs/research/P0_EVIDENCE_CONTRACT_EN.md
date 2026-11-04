# P0 evidence contract and scholarly-claim pilot

Checkpoint: 2026-11-04. Base dictionary 0.1.0; P0 intake profile 1.0.0. Status: engineering contract frozen and candidate intake prepared; scientific adjudication, source-fidelity review and operation-specific rights clearance remain incomplete.

## What is frozen

The [freeze manifest](../../spec/p0/freeze_manifest.json) binds eight exact artifacts: the base dictionary, vocabularies, logic and operator catalogues, plus the P0 [protocol](../../spec/p0/protocol.json), [JSON Schema](../../spec/p0/candidate_ledger.schema.json), [operator bindings](../../spec/p0/operator_bindings.yaml) and [formal obligations](../../spec/p0/formal_obligations.yaml). Freeze authorization is the user's implementation instruction. It grants no historical finding, rights decision, human annotation or formal proof. Changes require an explicitly versioned successor and retained prior bindings; do not refresh hashes merely to clear a failed check.

The JSON format is a typed *intake projection*, not a substitute for every field in the project data dictionary. Candidate aliases map to future atomic_claim records; source entries map to works, document versions and source files; locators map to passage candidates; reporting formulas map to proposed logical statements. Promotion needs exact immutable entity references, complete provenance and independent review.

Git attributes preserve the exact frozen bytes instead of automatically converting their line endings. Ordinary source files use LF. A fresh Git checkout must pass the same freeze check; a working-directory-only hash match is insufficient.

## Correct source hierarchy

Wikipedia is the preferred entry for term/person/reference discovery. It is not the default claim corpus. The revision-bound bibliography contains 42 citation instances and 39 proposed work groups after DOI grouping. Citation instances remain separate; grouping is not identity verification. These are discovery counts, not a comprehensive literature search.

The current 28 candidate atomic propositions come from four scholarly document versions: Merton's 1968 paper, Merton's 1988 retrospective essay, Price's 1976 paper and Perc's explicitly versioned arXiv manuscript. Each has seven selected candidates. The sample is purposive and bounded by accessible documents and reading capacity; it supports no estimate of what most publications say, who first coined a term, or the prevalence of miscredit. A preprint is not silently equated with a journal edition.

The user's compound example motivates separate naming-person, coining-date and biblical-inspiration propositions. Birth/death years belong to identity assertions. The exact supplied wording remains an unattributed lead unless located in a specified scholarly version. A citation to a 1968 publication does not itself establish a 1968 coining event. A text crediting Merton does not automatically assert sole coining; an authorship reflection does not automatically establish joint naming.

## Candidate records and audit trail

Private records are under `data/evidence/p0/matthew-effect-v1/`:

| Artifact | Role |
|---|---|
| `wikipedia_bibliography.json`, `literature_inventory_EN.md` | Reference discovery and retained citation instances |
| `candidate_ledger.v2.json`, `candidate_catalogue_v2_EN.md` | Current 28 scholarly-source candidates, all unassessed |
| `candidate_revision_history.json` | Prior projection retained; version 2 fixes offset drift and an overassigned contribution role |
| `human_source_requests.json` | Two bounded access failures handed to humans; no unseen-body claims generated |
| `independent_review_templates.json` | 56 unfilled slots for two independent humans per candidate; these are not annotations |
| `local_compute_receipt.json` | Local parser/model identity, package versions and observed model token counts |

Acquired PDFs, original per-page text and raw model attempts stay under `data/intake/literature/`. The four PDFs total 56 pages. Local reading preserves raw extraction; source hashes, page indices, whitespace-only normalized-page hashes, Unicode offsets and short anchors are checked together. Longer surrounding context is selected by bound offsets for review. Whole-page regions provide a fallback view, not a claim of pinpoint image verification.

Offset matching demonstrates a binding, not that the text supports the proposition. Unicode casefolding can expand ligatures and shift offsets; candidate version 2 uses index-preserving matching. Independent comparison to the original PDF image is still required, especially for scanned multi-column text and footnotes. No transcription fidelity approval has been invented.

`SOURCE_ASSERTS(document_version,candidate)` is a proposed source-reporting proposition. It does not assert historical truth, exclusivity, intent, misconduct or an accepted scientific result. All assessments remain null with NOT_ASSESSED; reviews remain pending and proof status unproved. The model/schema checker cannot grant human authority.

## Local computation and its measured limit

Deterministic PDF reading ran locally with pypdf 6.19.0 in the Horisma virtual environment. Five drafting calls used an already resident local StartLux 4B Q8 endpoint; no model was downloaded or swapped, and the shared process was not stopped. Observed receipts total 26,590 prompt tokens and 3,130 completion tokens. These are local-call counts, not a measured main-model savings percentage or a complete cost audit.

The rewrite pilot failed: it changed a contributor's name and often supplied oversized or nonliteral anchors. Zero freely rewritten model outputs were accepted. Raw attempts remain quarantined; the main model curated the bounded candidate projection against scholarly passages. The local model is not qualified as a historical adjudicator or a reliable full-document extractor. Further model-assisted processing should favor bounded span/label proposals and explicit source checks, with task-specific qualification before promotion. The installed model's noncommercial weight restriction also needs to remain visible in deployment choices.

The present analyst intake is not yet L37-conforming because affirmative operation-specific rights decisions are pending. Manual operation and private storage do not satisfy that gate. Do not describe the intake as an approved autonomous workflow, or continue/promote bulk processing without the required clearance. PDF/text redistribution remains unauthorized by these records.

## Access failures and human handoff

One selected scholarly review endpoint returned access denied; another selected publisher page required a redirect outside the source allowlist. Their receipts distinguish observed access failure from an inferred paywall. Each creates a pre-claim source-discovery request with a research dependency, requested material and resumption conditions. Candidate dependencies are empty because no unseen-body claim was fabricated. Human supply must re-enter identity/version, exact-operation rights and transcription review.

## Reproducible checks and next acceptance gate

Run from the Horisma workspace:

```powershell
.venv/Scripts/python.exe -m pytest tests/p0 -q
.venv/Scripts/python.exe scripts/horisma_p0.py validate
```

The first command uses synthetic, offline fixtures. The second requires private intake and validates the 28-candidate projection plus frozen bindings. Its success receipt explicitly denies scientific approval and formal proof. A public source-only clone can run the synthetic checks without private PDFs; it cannot reproduce unpublished candidate evidence from absent files.

Next: assign two genuinely independent human reviewers; verify exact sources, relevant passages, role/scope and transcription; resolve disagreements with a third adjudicator; clear the local-processing and export operations separately. Only then promote the evidence/adjudication slice and implement P1's reviewed English book materializer. P0 candidate preparation is complete; the research acceptance gate is not passed.
