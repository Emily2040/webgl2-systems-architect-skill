# Redesign Rationale

## What changed from the source prompt

The original material had strong engineering content but poor skill shape. It behaved like a massive doctrine dump rather than a router. That causes context bloat, weak task selection, and instruction drift.

This redesign changes the architecture in five ways:

1. **Monolith -> router**
   - The root `SKILL.md` is tiny and only routes to the orchestrator.
   - Deep rules moved into focused modules.

2. **Serial doctrine -> lane-based orchestration**
   - Independent work now lives in explicit lanes: hardware, subject, pipeline, runtime, validation.
   - The orchestrator can run those lanes in parallel when the host supports it, or pseudo-parallel when it does not.

3. **Absolute rules -> conditioned policies**
   - Several original rules were too absolute for a portable skill.
   - Example: context attributes, reversed-Z, worker rendering, and throughput math are now conditional on the project class, measurements, and capability profile.

4. **Conversation-only output -> structured contracts**
   - The skill now defines `authoring-base` and `runtime-compact` schemas so downstream tools can consume the result.

5. **Technique guide -> repository product**
   - The repo includes wrappers, schemas, examples, validator script, CI workflow, and an anti-slop registry.

## First-principles judgment calls

A few notable changes were deliberate:

- **Measured evidence outranks theoretical TFLOPS.**  
  The original prompt leaned heavily on public shader-core and clock estimates. Those are useful for planning but weaker than timer queries and differential measurements on the actual browser/device path.

- **Parallelism is modeled honestly.**  
  A single WebGL context still serializes draw submission. So the redesign distinguishes:
  - truly parallel or async tasks
  - pipelined tasks
  - tasks that remain serial no matter how fancy the promises look

- **The skill is not a book.**  
  The handbook material remains available through modules, but the agent only loads what the request needs.

## What stayed

The redesign preserves the best bones of the source material:

- numeric derivation discipline
- self-contained functions
- subject-audit thinking
- state/resource/runtime rigor
- validation and review checklists
- performance awareness across the whole stack
