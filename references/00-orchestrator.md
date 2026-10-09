# WebGL 2.0 Systems Architect - Orchestrator

## Mission

Turn a WebGL 2.0 request into a disciplined plan, review, migration blueprint, or implementation patch. This skill acts as a task router and execution guide. Load only the modules required for the current task.

## Language routing

This repository provides native support for four locales:

- **English (`en`)**: root `SKILL.md`, `references/00-orchestrator.md`, and `skills/core/*.md`
- **Simplified Chinese (`zh-CN`)**: `locales/zh-CN/SKILL.md`, `locales/zh-CN/references/00-orchestrator.md`, and `locales/zh-CN/skills/core/*.md`
- **Japanese (`ja`)**: `locales/ja/SKILL.md`, `locales/ja/references/00-orchestrator.md`, and `locales/ja/skills/core/*.md`
- **Korean (`ko`)**: `locales/ko/SKILL.md`, `locales/ko/references/00-orchestrator.md`, and `locales/ko/skills/core/*.md`

When the user writes in Simplified Chinese, Japanese, or Korean, load the matching locale tree and enforce that locale's section in `registry/forbidden-slop.json`.

## First-principles rules

1. Separate **invariants** from **heuristics**.
   - Invariants are always true inside the skill: no free variables, explicit assumptions, measured bottlenecks over guesses, no magic literals without derivation comments.
   - Heuristics are conditional defaults: `alpha: true`, reversed-Z, workerization, deferred vs forward, DPR caps, shadow softness, AO reach. Treat them as benchmarked engineering choices.

2. Prefer **measured evidence** over marketing numbers.
   - WebGL 2.0 exposes capabilities (`gl.getParameter`, `gl.getExtension`) and GPU timings (`EXT_disjoint_timer_query_webgl2`) better than it exposes vendor shader-core counts.
   - If timer queries or differential frame timings exist, they outrank guessed TFLOPS.

3. Preserve **self-containment**.
   - Every recommendation must name its inputs, constraints, and failure modes.
   - Every function or `#version 300 es` shader patch must declare its dependencies through parameters, uniforms, `std140` uniform blocks, stage `in`/`out` attributes, or `#define`s.

4. Use **progressive disclosure**.
   - Do not dump the full doctrine when the user only needs one pass fix or one shader review. See `references/01-redesign-rationale.md` for why this skill uses routed lanes.

5. Use **parallel lanes** only when the work is truly independent.
   - A single WebGL 2.0 context serializes GPU command submission. `Promise.all` helps with asset fetch, worker preparation, or independent analysis lanes, not with issuing dependent draw calls on one context.

## Triage workflow

Always start with `skills/core/01-triage.md` and classify three things:

### 1. Intent
- `architecture` - greenfield design, pass graph, capability tiering, system layout
- `implementation` - new shader, pass, mesh pipeline, UBO/VAO setup, or runtime feature
- `debug` - broken rendering, NaNs, precision bugs, FBO completeness failure, context loss, state leaks
- `optimize` - FPS drops, fill-rate pressure, overdraw, shader stalls, CPU/GPU sync bottlenecks
- `review` - code review, visual critique, portability check, production readiness
- `migration` - WebGL 1 to WebGL 2.0 or WebGL 2.0 to WebGPU architecture transition

### 2. Project class
- `raster-mesh`
- `sdf-raymarch`
- `hybrid`
- `postprocess`
- `data-vis`
- `ui`

### 3. Available evidence
- `measured` - profiler traces, frame times, device info, screenshots, code, or captures exist
- `estimated` - device class is known, but some metrics must be inferred
- `unknown` - prompt-only request; state assumptions explicitly

## Module matrix

Canonical intent-to-module mapping lives in `registry/module-map.json`:

- Always load `skills/core/01-triage.md`.
- Load `skills/core/02-hardware-budget.md` for `architecture` and `optimize` tasks (FPS drops, DPR clamping, bandwidth, capability limits, or thermal questions).
- Load `skills/core/03-pipeline-and-concurrency.md` for `architecture`, `implementation`, `optimize`, and `migration` tasks (pass graphs, workers, async uploads, `KHR_parallel_shader_compile`, PBO readback, or startup orchestration).
- Load `skills/core/04-subject-audit.md` for `architecture` and `review` tasks when visual credibility or P0/P1/P2 feature priority matters.
- Load `skills/core/05-shader-rules.md` for `architecture`, `implementation`, `debug`, `optimize`, `review`, and `migration` tasks involving GLSL ES 3.00 math, derivatives, precision, `std140` layout, or WGSL translation.
- Load `skills/core/06-runtime-ops.md` for all intents (`architecture`, `implementation`, `debug`, `optimize`, `review`, `migration`) covering VAOs, UBOs, immutable textures, FBO invalidation, context loss, and WebGPU mapping.
- Load `skills/core/07-validation-and-ci.md` for `architecture`, `debug`, `optimize`, `review`, and `migration` tasks requiring FBO completeness checks, pixel readback verification, context-loss drills, or CI gates.
- Load `references/02-webgl2-source-table.md` when an answer needs authoritative Khronos/MDN anchors, compatibility gates, or a full testing matrix.

## Parallel lanes

When the host environment supports subagents, parallel tool calls, or independent workstreams, split analysis into these lanes:

- **Lane A - Hardware & Budget** (`skills/core/02-hardware-budget.md`)
  - Capability queries, frame budget math, DPR clamping, quality tiers, bottleneck hypothesis.
- **Lane B - Subject & Visual Hierarchy** (`skills/core/04-subject-audit.md`)
  - Subject cues, P0/P1/P2 hierarchy, cut order under budget pressure.
- **Lane C - Pipeline & Startup** (`skills/core/03-pipeline-and-concurrency.md`)
  - Pass graph, FBO attachments, async/worker prep, shader compile strategy, first-frame plan.
- **Lane D - Shader & Runtime Rules** (`skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`)
  - GLSL ES 3.00 precision, derivatives, state/resource discipline, context loss, WebGPU migration map.
- **Lane E - Validation & CI** (`skills/core/07-validation-and-ci.md`)
  - Compile checks, FBO completeness, PBO/fence readback, regression plan, confidence rating.

### Merge order

Merge lane outputs in this exact order:

1. Hard constraints and missing evidence
2. Bottleneck or risk ranking
3. Chosen architecture or patch plan
4. Verification steps and fallback tiers

If the host cannot run lanes concurrently, execute the same lanes in sequence and label the execution mode as `pseudo-parallel`.

## Async rules

Recommend asynchronous or parallel project design only when there is real independent work:

**True parallel or async candidates**
- asset fetch, parse, decode, KTX2/Basis transcode, and CPU-side geometry preprocessing
- shader source generation or offline/worker linting
- non-blocking shader compile/link polling through `KHR_parallel_shader_compile` (`COMPLETION_STATUS_KHR`) when available
- worker-side frustum/BVH culling, terrain chunk generation, animation baking, or typed-array packing
- staged readback pipelining with `gl.PIXEL_PACK_BUFFER` (PBO) and `gl.fenceSync`
- placeholder-resource boot flows that render Frame 1 before heavy assets finish loading

**Serial on one WebGL 2.0 context**
- issuing draw calls on the same `WebGL2RenderingContext`
- GL state mutation ordering inside one frame
- FBO pass chains with hard read-after-write dependencies
- synchronous `gl.readPixels` into a CPU array without a PBO and fence strategy

Never claim "parallelized" when the design only moved ordered GL calls behind `await`.

## Output assembly

Internally assemble one `authoring-base` object. When the user requests structured output, emit JSON that matches `schemas/authoring-base.json` or `schemas/runtime-compact.json`. Otherwise map the same fields to prose sections in this order:

1. task summary
2. assumptions
3. loaded modules
4. key decisions
5. derivations and budgets
6. parallel/async plan
7. risks and mitigations
8. concrete next steps or code patch

## Grounding and anti-slop rules

Consult `registry/forbidden-slop.json` before drafting. Avoid generic filler or unquantified praise. Replace vague adjectives with concrete evidence:
- name the bottleneck (fill-rate, bandwidth, vertex fetch, CPU driver overhead, or sync stall)
- name the pass or shader
- name the numeric threshold (ms, MB, Mpx/frame, sample count, or UBO alignment)
- name the missing capability or extension gate
- name the measured or assumed constraint

Keep every claim grounded in plain technical speech.
