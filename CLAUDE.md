# CLAUDE.md

Use this repository as a modular WebGL 2.0 systems skill, not a single giant prompt. Keep context focused.

- Start with `SKILL.md`.
- Follow `references/00-orchestrator.md` (or `locales/{zh-CN,ja,ko}/references/00-orchestrator.md` for CJK tasks).
- Select only the modules listed in `registry/module-map.json` for the active task intent, and keep invariants separate from conditional heuristics when reviewing shaders or pass graphs.
- Use `schemas/authoring-base.json` or `schemas/runtime-compact.json` when structured output is requested.
- Avoid phrases listed in `registry/forbidden-slop.json`.
