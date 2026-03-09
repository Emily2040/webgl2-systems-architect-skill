# WebGL 2 Systems Architect Skill

A modular agent skill for designing, reviewing, debugging, and optimizing WebGL 2.0 projects from first principles.

[![CI](https://github.com/Emily2040/webgl2-systems-architect-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/Emily2040/webgl2-systems-architect-skill/actions/workflows/validate.yml)
![Version](https://img.shields.io/badge/version-1.0.1-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Pattern](https://img.shields.io/badge/design-progressive%20disclosure-purple)

Repository: [Emily2040/webgl2-systems-architect-skill](https://github.com/Emily2040/webgl2-systems-architect-skill)

## What this is for

Use this skill when a user needs help with:

- WebGL 2.0 renderer architecture
- shader engineering and SDF math
- performance budgets and tiering
- runtime orchestration and context safety
- visual subject audits
- validation, CI, and production hardening

This is not a monolithic handbook stuffed into one prompt. The root `SKILL.md` is a router. The orchestrator loads only the modules relevant to the current task.

## Design goals

- keep the root skill tiny
- separate invariants from heuristics
- favor measurements over lore
- model parallel and async work honestly
- produce outputs that are usable by both humans and downstream systems

## Architecture

![Architecture diagram](docs/assets/architecture.svg)

A browser-friendly overview also lives at [`docs/index.html`](docs/index.html).

## Repository map

```text
SKILL.md
AGENTS.md / CLAUDE.md / GEMINI.md
LICENSE
.gitignore
docs/
  index.html
  assets/
    architecture.svg
references/
  00-orchestrator.md
  01-redesign-rationale.md
skills/core/
  01-triage.md
  02-hardware-budget.md
  03-pipeline-and-concurrency.md
  04-subject-audit.md
  05-shader-rules.md
  06-runtime-ops.md
  07-validation-and-ci.md
registry/
  forbidden-slop.json
  module-map.json
schemas/
  authoring-base.json
  runtime-compact.json
examples/
  *.input.md
  *.output.json
scripts/
  validate_repo.py
.github/workflows/
  validate.yml
```

## How it works

1. `SKILL.md` routes to the orchestrator.
2. The orchestrator builds a task record and selects modules.
3. Independent lanes can run in parallel:
   - hardware and caps
   - subject audit
   - pipeline and async design
   - shader/runtime review
   - validation
4. The answer is synthesized into prose or JSON.

## Parallel and async stance

This skill distinguishes between:

- truly parallel or asynchronous work
- pipelined work
- work that is still serial on a single WebGL context

That means the skill will recommend `Promise.all`, workers, `OffscreenCanvas`, or `KHR_parallel_shader_compile` only when they remove actual waiting, not because “async” sounds fashionable.

## Installation

### AGENTS-style loaders

```bash
mkdir -p .agents/skills
cp -R webgl2-systems-architect-skill .agents/skills/webgl2-systems-architect
```

Load `SKILL.md` from the copied folder.

### Wrapper-friendly loaders

If a host prefers alternate entry points, load one of:

- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`

Each wrapper points back to the canonical root skill so logic does not drift.

## Output contracts

When structured output is requested, use:

- `schemas/authoring-base.json` for full authoring output
- `schemas/runtime-compact.json` for compact handoff or runtime use

Examples live in the `examples/` directory.

## Validation

Run the validator:

```bash
python3 scripts/validate_repo.py
```

The GitHub Actions workflow runs the same check on pull requests.

## Notes on the redesign

This skill intentionally converts several blanket rules from the source doctrine into measured policies. Examples include:

- context attributes
- DPR caps
- workerization
- reversed-Z usage
- theoretical throughput math

Those are important ideas, but they are not universal constants. The skill treats them as conditional decisions backed by project class, capability detection, and measurements.

## Author

Created by **Iamemily2050**.

- GitHub: [Emily2040](https://github.com/Emily2040)
- Website: [Iamemily2050.com](https://Iamemily2050.com)
- X: [@iamemily2050](https://x.com/iamemily2050)
- Instagram: [@iamemily2050](https://instagram.com/iamemily2050)
