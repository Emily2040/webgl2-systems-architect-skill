# Module 07 - Validation and CI

## Purpose

Convert "this seems fine" into evidence. Validation is where pretty theories either survive contact with pixels or fall over like a cardboard dragon.

## Validation layers

### 1. Static validation

Check before runtime:

- shader sources compile under offline or editor tooling
- skill/repo metadata is structurally valid
- schemas parse
- examples parse
- required files exist
- root `SKILL.md` stays small and router-like

### 2. Runtime correctness

Check during execution:

- no missing resources
- no incomplete framebuffers
- no silent fallback paths
- no unexpected context loss loops
- no broken restore path

### 3. Visual validation

Use:
- screenshot baselines
- pixel or perceptual diffs
- targeted artifact checks for banding, Z-fighting, shadow acne, aliasing, temporal instability, or missing subject features

### 4. Performance validation

Measure:
- frame time
- representative pass times
- memory growth
- startup latency
- context-switch hotspots
- readback stalls
- thermal or battery regression signals when available

### 5. Review validation

Require:
- explicit assumptions
- named bottlenecks
- numeric derivations
- tier-aware feature gating
- a visible definition of done

## Acceptance gates

A production-ready answer or patch should clear these gates:

- `correctness`: no known blockers or compile hazards left unexplained
- `grounding`: all major claims tied to data, code, or stated assumptions
- `performance`: cost centers identified and prioritized
- `recovery`: context loss and failure handling are defined
- `portability`: feature use is conditioned on capability detection
- `maintainability`: modules, schemas, and repo structure stay coherent

## CI for the skill repo

Validate the repo itself:

- canonical `SKILL.md` exists
- wrappers point to the canonical source
- frontmatter is valid and uses standard keys
- JSON schemas parse
- example JSON parses and matches the expected shape
- `forbidden-slop.json` parses
- the validator script exits non-zero on failure

## Reporting format

Return:

- `validation_checks`
- `acceptance_gates`
- `confidence_rating`
- `remaining_unknowns`
- `recommended_tests`

Confidence labels:
- `high` - supported by code, measurements, or direct evidence
- `medium` - supported by strong inference
- `low` - assumption-heavy; user should verify before shipping

## Common failure modes

- reporting average FPS while hiding 1% lows or pass spikes
- validating only the "pretty" scene and not the stress scene
- claiming portability without capability gates
- shipping a skill repo whose wrappers or schemas quietly drifted out of sync
