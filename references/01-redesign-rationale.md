# Redesign Rationale

## What changed from the source prompt

Monolithic prompts fail under real production constraints. The original material had strong graphics-engineering content, yet it behaved like a single doctrine dump rather than a router. That causes context bloat, weak task selection, and instruction drift.

This architecture organizes the skill in six ways:

1. **Monolith -> router**
   - The root `SKILL.md` is tiny (`< 800` characters) and routes directly to `references/00-orchestrator.md`.
   - Deep technical rules live in focused modules (`skills/core/01-triage.md` through `skills/core/07-validation-and-ci.md`).

2. **Serial doctrine -> lane-based orchestration**
   - Independent work lives in explicit lanes (`A` through `E`): hardware budget, subject audit, pipeline concurrency, shader/runtime discipline, and validation/CI.
   - The orchestrator runs those lanes in parallel when the host supports subagents, or in `pseudo-parallel` sequence when it does not.

3. **Absolute rules -> conditioned policies**
   - Context attributes, reversed-Z, worker rendering, and throughput math are conditioned on project class, measured GPU timings, and capability profiles.

4. **Conversation-only output -> structured contracts**
   - The skill defines `schemas/authoring-base.json` and `schemas/runtime-compact.json` with validated examples covering `architecture`, `optimize`, `debug`, and `migration`.

5. **Single-language prompt -> native four-language engineering pack**
   - Native documentation and localized skill trees (`en`, `zh-CN`, `ja`, `ko`) ensure engineers working in English, Simplified Chinese, Japanese, or Korean receive idiomatic graphics-systems guidance and locale-aware anti-slop enforcement.

6. **Static marketing docs -> interactive WebGL 2.0 workbench**
   - `docs/index.html` and `fixtures/webgl2-smoke/index.html` execute live `#version 300 es` shaders with VAOs, `std140` UBOs, PBO + `gl.fenceSync` readback, and simulated `WEBGL_lose_context` recovery.

## First-principles judgment calls

- **Measured evidence outranks theoretical TFLOPS.**
  Public shader-core and clock estimates are useful for rough planning, but timer queries (`EXT_disjoint_timer_query_webgl2`) and differential pass measurements on the actual browser/device path outrank guessed hardware numbers.

- **Parallelism is modeled honestly.**
  A single WebGL 2.0 context serializes draw submission. The skill separates truly parallel CPU/worker tasks, pipelined GPU readback (`PIXEL_PACK_BUFFER` + `fenceSync`), and serial single-context state/draw submission.

- **The skill is not a book.**
  The agent loads only the modules mapped in `registry/module-map.json` for the classified intent.

## Core invariants preserved

The package enforces six foundational disciplines across every module:

- numeric derivation comments for every threshold, epsilon, and step bound
- self-contained shader and runtime functions with explicit inputs
- P0/P1/P2 subject-audit prioritization before micro-detail polish
- explicit VAO, UBO, immutable texture (`texStorage2D`), and context-loss recovery discipline
- FBO completeness and non-blocking PBO/fence verification
- zero-dependency repository self-validation in `scripts/validate_repo.py`
