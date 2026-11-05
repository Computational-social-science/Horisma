# Horisma

Horisma studies how scientific contribution, attribution and uncertainty survive retelling. Its shared evidence infrastructure supports scientist/contribution data, reproducible model evaluation and the book series **The Secrets of Terms**. Each volume uses **The Secrets of Terms** as its main title and the target term as its subtitle; the commissioning volume is **The Secrets of Terms: The Matthew Effect**.

Current design:0.2.0 (2026-11-05). This is a clean rebuild. Existing historical assertions remain candidates; no qualified historical gold or accepted book is claimed.

## Authoritative entries

- [Current research proposal](docs/research/Horisma_Terminological_Provenance_Project_Research_Proposal_EN.md)
- [Implementation and acceptance](docs/research/Horisma_Implementation_Acceptance_Plan_EN.md)
- [Data dictionary: frozen core and versioned extensions](docs/data-dictionary/README.md)
- [Current document authority registry](spec/extensions/document_authority.yaml)
- [Research-card and publication contract](spec/extensions/research_cards.yaml)
- [Wiki](wiki/Home.md)

## Local workflow

Use `research-docs` to discover maintained authorities instead of loading all historical checkpoints. Downstream research reads the Paper2Skill-produced `references/paper.md` selected by the private entrypoint catalogue; PDF/OCR/staging artifacts are supporting provenance. Event cards have one JSON authority and generated MD/Quarto/Logseq views. Domain IDs and edition-pinned revisions are separate from displayed footnote numbers.

Use the project environment, not an arbitrary PATH Python:

```
.venv/Scripts/python.exe scripts/horisma_p0.py research-build
.venv/Scripts/python.exe scripts/horisma_p0.py research-check outputs/research-slices/<digest>
.venv/Scripts/python.exe scripts/horisma_p0.py research-evaluate --candidate gemma3:12b
.venv/Scripts/python.exe scripts/horisma_p0.py validate
.venv/Scripts/python.exe scripts/horisma_p0.py research-entity-sources
.venv/Scripts/python.exe scripts/horisma_p0.py research-entities-build outputs/research-slices/<digest>
.venv/Scripts/python.exe scripts/horisma_p0.py research-entities-evaluate
.venv/Scripts/python.exe -m pytest -q
```

Private source files are required for a real slice; public clones can run synthetic tests, with private-response replays explicitly skipped when originals are unavailable. Optional research dependencies are declared in pyproject.toml. Existing local OCR weights are supplied explicitly; no paid API or automatic model download is required.

Source versions, rendered regions, native text and OCR comparisons are privately preserved by content hash. A matching hash proves identity of bytes, not historical truth or complete context. Shared source/person/task/chapter revisions invalidate together when inputs change.

EIDOS Agent is reused through an existing pinned installed worker and a project-local adapter. Its actual check currently refuses scientific acceptance because qualification prerequisites are missing. No monitor, cron or unattended deployment is started.

Private PDFs, extraction, model responses and source custody blobs remain out of Git. Technical acceptance, scientific qualification, reader quality and public release are separate. New UI effects and additional book formats are not substitutes for evidence.

The exact publication naming migration is available as `research-publication-rebase <old-slice.json>`, followed by `research-eidos-check`. It preserves frozen evidence inputs, re-scores sealed outputs without inference, and rebuilds current entity/case/card/book dependencies. Operational freshness does not confer historical acceptance or release.
