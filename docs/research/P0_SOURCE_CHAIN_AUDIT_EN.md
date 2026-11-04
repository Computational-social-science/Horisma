# Preliminary source and citation-chain audit

2026-11-04. Scope: all 28 current scholarly-source candidates. This is a local analyst/model audit of existing intake derivatives, not completed independent adjudication or source-image verification. The original candidate ledger is retained unchanged.

## Executed work

Local deterministic operators checked source hashes, rebound review excerpts, indexed document-scoped reference candidates and validated cache bindings. The selected resident StartLux model proposed ordinal text-fit categories for every candidate. This used 7,821 local prompt tokens and 635 local completion tokens; no main-model savings percentage is claimed. No new PDF download, paid access, model installation or remote inference was used in this round.

The rubric distinguishes NOT_ESTABLISHED (0), PARTIAL_OR_AMBIGUOUS (1) and DIRECT_AUTHOR_STATEMENT (2). Scores describe a proposed relationship between the provided text and the candidate proposition. They are not truth probabilities, evidence-quality grades, cited-body support scores or human approvals. The runtime model ID was observed; its weights digest was not independently reverified for this audit.

StartLux proposed direct author statement for 26 candidates and partial/ambiguous for HC-P0-005 and HC-P0-015. These suggestions remain unqualified for automatic acceptance. All historical assessments are still null/NOT_ASSESSED, and no completed human annotation has been recorded.

## Material findings

| Candidates | Observation and consequence |
|---|---|
| 004, 013, 025, 027 | Original anchors were too broad, irrelevant or crossed a page boundary. New audit windows locate the relevant wording; 004 explicitly uses two pages. Old candidate/attempt records remain available. |
| 003 | Perc reference 2 identifies Price's 1965 *Networks of scientific papers*. The available Price 1976 paper is a different work and cannot close this chain. The 1965 work is requested from a human. |
| 001, 002 | Extracted Perc reference 1 gives pages 53–63; the current Merton work metadata gives 56–63. This is a bibliographic/OCR discrepancy pending original-image identity review, not an established scholarly error or miscredit verdict. |
| 020 | The 1988 essay reports a reflection dated 1973 about joint authorship. The original 1973 volume has not been checked. Neither this retrospective statement nor joint authorship establishes joint naming. |
| 018, 020 | Merton's footnote 2 names multiple works and includes a retrospective quotation. Do not turn one footnote number into one supposedly verified cited work. |
| 024 | OCR column order/reference numbering is not reliable enough to bind the Cole-and-Cole citation without source-image review. No conceptual-priority role is assigned. |
| 005 | The methodological assertion cites additional sources; their bodies have not been read here. A bibliography entry does not establish that a cited work supports the proposition. |

Reference extraction was corrected to handle lowercase author prefixes such as “de Solla” and to exclude body citations preceding the bibliography start. Earlier lookup receipts are retained; the corrected reference index and reconciliation are versioned separately. Exact text slices and source hashes establish bindings, not semantic support or transcription fidelity.

## Private review handoff

Under `data/evidence/p0/matthew-effect-v1/audit-v1/`, `audit_report_EN.md` summarizes all 28 rows; per-candidate JSON retains excerpts, offsets, raw model outputs and citation proposals. `citation_chain_reconciliation.v2.json` records the corrected reference lookup. `run_manifest.json` binds the audited ledger and actual model configuration. Changed propositions, excerpts, model IDs, rubric/prompt bindings or configuration invalidate cached scores rather than silently reusing them.

`additional_human_source_requests.json` contains eight additional dependencies: Price 1965, the original Merton 1973 volume, Zuckerman's 1965 dissertation and 1967 author-ordering work, the Cole-and-Cole volume, and three methodological sources cited by Perc. These are absent from the currently verified working corpus; whole-host absence or a paywall is not inferred. No access attempt was claimed. Supply must be lawful and followed by exact-version identity, operation-specific rights, fidelity and support review. The two earlier acquisition-failure requests remain separate.

## Acceptance and next work

Engineering tests pass, including refusal of negative page indexes, stale cache bindings and invalid ordinal/model outputs. Source identity, original-image fidelity, rights and independent human evidence adjudication remain open. The earlier L37 limitation is not waived by cached-text scoring or private operation.

Prioritize 003/020/024 for exact-source and attribution-chain review, and 005/015 for resolving the model's ambiguous text-fit suggestions. Then complete independent review of the remaining candidates. No P0 scientific acceptance gate is passed and no GitHub synchronization was performed in this round. Keep changes local until a coherent accepted milestone or explicit owner request.
