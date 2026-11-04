# Optional local PFLM pattern operators

2026-11-04; extension 0.1.0. This extension is separate from the frozen P0 intake contract. It is installed locally for controlled experiments and disabled by default for scientific filtering.

## Capability and intended placement

The [upstream repository](https://github.com/cbl/prior-fitted-language-model/tree/1e62eeb8ebbc3a314fa10d784fd8e1d56c72927f) and [paper](https://arxiv.org/abs/2610.05879) describe a roughly 300M-parameter byte-level prior-fitted model with in-context adaptation. Code and weights are Apache-2.0. This supports evaluating lightweight local pattern instruments; it does not establish task quality for scholarly attribution or reference entailment.

Horisma places it after document decoding and paragraph/citation indexing:

```text
PDF/HTML/text -> local deterministic reading and exact source bindings
             -> literal target/attribution candidate retrieval
             -> optional PFLM few-shot pattern/label-cost ranking
             -> exact citation-marker-to-bibliography candidate links
             -> independent passage, role/scope and support assessment
```

The deterministic retrieval operator keeps original paragraphs and returns candidates, never destructive exclusions. Numeric citation linking retains unresolved markers and marks linked items as CITES_CANDIDATE. It does not label a bibliography entry SUPPORTS. Author-year formats, marker ranges, layout/OCR ambiguity and full entailment require later qualified implementations; the current narrow linker does not claim to cover them.

PFLM has no PDF layout or image input in this adapter. Binary PDFs are refused. It receives exact UTF-8 text or an explicit few-shot pattern context and equal-byte-length label alternatives. It can propose rankings for attribution-like paragraphs or citation-marker patterns, subject to empirical qualification. It cannot establish coining priority, identify an omitted contributor from memory, correct an unusual name, decide whether a cited reference supports a proposition, or grant approval.

## Local assembly and provenance

| Component | Pinned identity |
|---|---|
| Code | `cbl/prior-fitted-language-model@1e62eeb8ebbc3a314fa10d784fd8e1d56c72927f`; installed package `pflm1==0.1.0` |
| Weights | `lennartcb/pflm1@20de84b6a178af5c7824f823bd0058452db2b360` |
| Safetensors | 589,843,368 bytes; SHA256 `385b7b21cae8605dbc4fe0611b6a78576017260824011a0cbe402e3014061c0e` |
| Local execution | Horisma virtual environment; CPU/float32; at most six CPU threads in the current loader |

Weights and upstream clone remain under `.rebuild`, outside the public technical export. No EIDOS directory is used. No paid inference, hosted fallback, CUDA service, flash-attention installation or model replacement was introduced. Existing Torch/Transformers were reused. Public model download is a distinct one-time acquisition; inference is local-only and does not download missing files.

The loader checks all 16 installed Python source files through a canonical CRLF-to-LF fingerprint, plus exact config and safetensor hashes. Python source newline canonicalization is limited to implementation identity; historical source bytes are never rewritten this way. Remote model code is disabled. The optional installation entry is [requirements-pflm.txt](../../requirements-pflm.txt); it is not part of base CI dependencies.

## Contracts and numerical limits

[Extension contracts](../../spec/extensions/pflm_operator.yaml) define byte prediction cost and exploratory label ranking. [Implementation](../../src/horisma_p0/pflm_adapter.py) keeps raw input unchanged, refuses nonfinite/negative scores and uses an explicit eligible-byte denominator. Empty input is undefined, not zero. Upstream scoring uses float32 log-softmax; byte likelihood remains distinct from calibrated semantic correctness or factual confidence.

The first byte has the declared uniform prior cost of eight bits. Comparisons must use the same text, context, byte accounting and label protocol. Label alternatives have equal byte length, and numerical ties remain undecided. Rare names, scripts, OCR corruption and formatting shifts can alter statistical cost; lower cost does not establish a historically correct spelling. No automatic repair or paragraph deletion is authorized.

For one-byte labels, the ranker evaluates the context once and reuses the public next-byte logits. Float64 shifted logits and log1p retain very small top-label costs without exponentiate-then-log underflow or subtracting a large log-normalizer. Multi-byte alternatives use separate continuation streams. This numerical check is distinct from semantic task validation.

Run an explicit local scoring command from the project root:

```powershell
.venv/Scripts/python.exe scripts/pflm_score.py path/to/approved_utf8_text.txt
```

This has a bounded input size and reads only local model files. It is not permission to process new scholarly files before the P0 operation-specific rights gate. The current scientific corpus remains unadjudicated.

## Qualification before real filtering

Local real-weight CPU smoke checks use synthetic bytes and short label-pattern contexts. They check loading, finite scores and chunk consistency, not real-document recall. See the separately recorded validation checkpoint for measured results. Unit tests use simple synthetic stubs so base CI needs neither Torch nor weights.

In the current four-case synthetic attribution task, both the unbalanced and balanced few-shot contexts yielded 1/4 correct labels, versus 4/4 for the literal baseline. This small exploratory setup does not determine general capability, but it fails the present promotion gate. Automatic filtering stays disabled. [Measured checkpoint](../research/P0_VALIDATION_CHECKPOINT_EN.md).

For repeated experiments, load one verified model per bounded batch and reuse the model object; do not reload weights for each paragraph. Reset/fix the declared context protocol between independent cases. Prefix reuse for label alternatives is not permission to carry information across held-out dataset boundaries.

Before enabling real paragraph filtering, independently label held-out scholarly passages and reference links. Compare literal/regex/link baselines, deterministic retrieval plus PFLM, and the selected local instruction model at the same review budget. Prespecify recall, false exclusion, precision, unresolved links, byte/time/memory cost and source-family split; report denominator and uncertainty. Include unusual names, multilingual text, negated attribution, quoted statements, footnotes and cross-document marker collisions. PFLM must earn a task-specific role through these measurements. Until then it remains an optional observer/ranker, with originals retained and no evidence-support authority.
