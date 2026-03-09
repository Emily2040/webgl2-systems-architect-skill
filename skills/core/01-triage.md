# Module 01 - Triage

## Purpose

Classify the request before loading specialist modules. The point of triage is to avoid the classic clown-car failure mode where every rule in the skill jumps into the answer at once.

## Build the task record

Create a task record with these keys:

```json
{
  "intent": "",
  "project_class": "",
  "subject": "",
  "artifacts_present": [],
  "hardware_data_quality": "",
  "target_platforms": [],
  "fps_target": null,
  "constraints": [],
  "deliverable_type": "",
  "confidence": ""
}
```

## Intent mapping

- `architecture` - user wants a design from scratch, a system plan, or a repo/skill redesign.
- `implementation` - user wants actual code, shader snippets, patch structure, or pass graph details.
- `debug` - user reports a bug, compile error, artifact, or broken rendering.
- `optimize` - user reports poor FPS, stalls, memory spikes, thermal issues, or startup latency.
- `review` - user wants critique, QA, validation, or code review.
- `migration` - user asks about WebGPU, portability, or longer-term architecture.

## Project-class mapping

- `raster-mesh` - draw calls, VAOs, meshes, materials, depth, instancing
- `sdf-raymarch` - fullscreen quad, distance fields, AO/shadows/normal epsilons
- `hybrid` - mesh + SDF + postprocess or mixed material systems
- `postprocess` - fullscreen passes, FBO chains, temporal effects
- `data-vis` - charts, graphs, node maps, density fields
- `ui` - layout, text, interaction states, latency, sharpness

If the user does not name a class, infer it from the nouns in the request and mark the inference as an assumption.

## Artifact scan

Record what exists already:

- `prompt-only`
- `code`
- `shaders`
- `perf-data`
- `screenshots`
- `GPU captures`
- `repo-skill`
- `mixed`

The presence of code or captures should pull the answer toward review/debug specificity instead of generic architecture advice.

## Module-selection rules

Always load this module first.

Then select modules:

- load `02-hardware-budget.md` when the request mentions performance, tiering, target devices, DPR, resolution, memory, battery, or quality settings
- load `03-pipeline-and-concurrency.md` when the request mentions startup, workers, async, pass ordering, resource loading, or renderer structure
- load `04-subject-audit.md` when the scene content itself matters
- load `05-shader-rules.md` when GLSL or numeric rendering logic matters
- load `06-runtime-ops.md` when the problem smells like JS/GL orchestration rather than shader math
- load `07-validation-and-ci.md` when the user wants confidence, testing, repo health, or production readiness

## Assumption discipline

Do not halt because inputs are incomplete. Instead:

1. list missing facts
2. choose conservative defaults
3. tag each default with confidence:
   - `high` - implied by provided artifacts
   - `medium` - common for the project class
   - `low` - weak guess; user should verify

Example:
- assume `60 FPS` if the user asks for smooth interactive rendering and gives no alternate target
- assume `mobile-first constraints` if the user mentions Safari, iPhone, Android, battery, or thermals
- assume `single WebGL context` unless the user explicitly describes a worker/OffscreenCanvas architecture

## Exit condition

Triage is done when you can state, in one compact block:

- what the user is actually asking for
- which modules are needed
- what can be analyzed independently
- what assumptions are carrying the answer
