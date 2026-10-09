# 01 - Triage and Task Classification

## Purpose

Classify the WebGL 2.0 request so the agent loads only the required modules and avoids dumping unrelated rules. Start here on every task.

## When to load

Load on every request before any other module.

## Inputs

- User prompt and target language (`en`, `zh-CN`, `ja`, `ko`)
- Existing code, shaders, pass graphs, or repository files if provided
- Screenshots, videos, GPU profiler captures, or runtime error logs if provided
- Target device, browser, and frame-rate constraints if known

## Rules

### 1. Classify the request across four axes

1. **Intent**
   - `architecture`: system layout, pass graph, capability tiering, startup orchestration
   - `implementation`: new `#version 300 es` shader, pass, mesh/VAO/UBO pipeline, or runtime feature
   - `debug`: visual bug, `NaN`/precision artifact, incomplete FBO, state leak, or context-loss failure
   - `optimize`: FPS drop, fill-rate bottleneck, bandwidth pressure, shader stall, or synchronous readback
   - `review`: code audit, visual credibility check, portability evaluation, or ship readiness
   - `migration`: WebGL 1 to WebGL 2.0 upgrade or WebGL 2.0 to WebGPU/WGSL transition plan

2. **Project class**
   - `raster-mesh`: vertex/index buffers, instanced meshes, forward or deferred shading
   - `sdf-raymarch`: fullscreen procedural SDF raymarching, volumetric or analytical surfaces
   - `hybrid`: raster G-buffer or mesh pass combined with raymarched/fullscreen effects
   - `postprocess`: multi-pass filter chain, bloom, TAA, DOF, tone mapping, or compositing
   - `data-vis`: GPU instanced glyphs, particle fields, heatmaps, or large scatter plots
   - `ui`: resolution-independent vector/SDF widgets, text atlases, or compositor overlays

3. **Subject**
   - Name the concrete visual or technical target: `human face bust`, `terrain flyover`, `HDR bloom chain`, `instanced scatter plot`, or `WebGPU bind-group migration`.

4. **Evidence quality**
   - `measured`: timer queries, frame times, captures, or reproducible code exist
   - `estimated`: target device class is known, but pass costs are inferred
   - `unknown`: prompt-only request; all hardware budgets must be marked as assumptions

### 2. Inspect provided artifacts before proposing changes

- If shaders or JS/TS files exist, inspect version directives (`#version 300 es`), VAO/UBO bindings, FBO setup, and draw loops first.
- If screenshots or captures exist, identify whether the defect is geometric, shading/precision, compositing, or bandwidth-bound.
- If the request is prompt-only, keep assumptions explicit and small.

### 3. Select modules by intent (must match `registry/module-map.json`)

- `architecture`: `skills/core/01-triage.md`, `skills/core/02-hardware-budget.md`, `skills/core/03-pipeline-and-concurrency.md`, `skills/core/04-subject-audit.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`, `skills/core/07-validation-and-ci.md`
- `implementation`: `skills/core/01-triage.md`, `skills/core/03-pipeline-and-concurrency.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`
- `debug`: `skills/core/01-triage.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`, `skills/core/07-validation-and-ci.md`
- `optimize`: `skills/core/01-triage.md`, `skills/core/02-hardware-budget.md`, `skills/core/03-pipeline-and-concurrency.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`, `skills/core/07-validation-and-ci.md`
- `review`: `skills/core/01-triage.md`, `skills/core/04-subject-audit.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`, `skills/core/07-validation-and-ci.md`
- `migration`: `skills/core/01-triage.md`, `skills/core/03-pipeline-and-concurrency.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`, `skills/core/07-validation-and-ci.md`

### 4. Decide whether parallel lanes help

- Single localized bug (`debug` on one shader): run sequentially.
- Multi-constraint task (`architecture`, `optimize`, `review`, `migration`): split into parallel lanes (`A` through `E`) and merge in orchestrator order.

## Failure modes

- Loading every module for a one-line shader fix
- Treating SDF raymarching rules as mandatory for a raster mesh pipeline
- Recommending optimization cuts before classifying whether the bottleneck is fill-rate, bandwidth, vertex, or CPU sync
- Omitting `skills/core/05-shader-rules.md` during `architecture` or `migration` planning

## Output contribution

Populate `task.intent`, `task.project_class`, `task.subject`, `inputs.hardware_data_quality`, `modules`, and initial `assumptions`.
