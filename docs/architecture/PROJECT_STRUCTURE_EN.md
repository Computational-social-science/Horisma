# Horisma clean-rebuild project structure

Version0.1.0;2026-11-04. Workspace: `E:/2026-AI4S/Horisma`.

```text
Horisma/
  README.md                    project entry and readiness
  docs/research/               canonical proposal, review, implementation plan
  docs/data-dictionary/        canonical English data dictionary
  docs/methods/                formalization and measurement conventions
  docs/architecture/          this ownership/layout specification
  spec/                       versioned vocabularies and formal logic catalogue
                              reusable primitive/composite operator catalogue
    examples/                 synthetic conformance/counterexample specifications
  data/intake/                private source/manual-PDF intake
  data/evidence/              new immutable research records after acceptance
  data/benchmarks/            private/sealed evaluation material
  outputs/                    derived candidates and reviewed release bundles
  ops/                        Horisma-owned operational specification/state selection
  src/                        future rebuilt implementation; no legacy runtime imported
  tests/                      future executable tests
  legacy/                     hash catalogue of old material quarantined in place
  wiki/                       navigation/readiness, not a second normative definition
  .rebuild/                   private snapshots and document-assembly/check records
  .agents/skills/              project-scoped reusable research-contract workflow
```

Existing root document names remain compatibility entries. Their canonical bodies are in docs; only those canonical bodies are edited. No data/schema is copied into an EIDOS directory. EIDOS is an external versioned SDK dependency.

The restructure did not move original PDFs, notebooks, figures or assets. `legacy/material_inventory.json` records their earlier observed paths/bytes and marks them unverified. A later availability check found three candidate PDFs missing; `legacy/material_availability.json` records the gap without overwriting the original inventory or attributing a cause. No automatic dataset loader may sweep the workspace recursively. Intake is explicit. Old scientific labels never become gold through relocation or filename changes.

The new .gitignore protects local intake, evidence, sealed tests, outputs and candidate materials from accidental staging. It cannot remove previously tracked material: existing deleted paths stay deleted; future release must use an explicit reviewed export allowlist and inspect the index. The .gitignore itself is a new clean-rebuild policy, not restoration of the previous file.

Research definitions are owned by the data dictionary, machine codes by the vocabulary catalogue, and logical obligations by the logic catalogue. SQLite, operator code and theorem-prover integration remain future implementation. Directory presence does not imply those capabilities exist.
