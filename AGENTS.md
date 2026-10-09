# AGENTS.md

## Purpose

Route WebGL 2.0 architecture, GLSL ES 3.00 shader authoring, pass-graph design, runtime lifecycle management, profiling, WebGPU migration, and validation tasks through the modular skill package. Keep context lean.

## Startup behavior

1. Read `SKILL.md`.
2. Read `references/00-orchestrator.md` (or `locales/{zh-CN,ja,ko}/references/00-orchestrator.md` for CJK tasks).
3. Load `skills/core/01-triage.md` first.
4. Load only the modules listed in `registry/module-map.json` for the resolved intent.
5. Prefer measured GPU evidence over guessed numbers and enforce `registry/forbidden-slop.json`.
