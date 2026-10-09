# Changelog

This file tracks every release. All notable changes to this project are documented below.

## 2.0.0 - 2026-10-10

### Added
- Native four-language support (`en`, `zh-CN`, `ja`, `ko`) across root READMEs (`README.md`, `README.zh-CN.md`, `README.ja.md`, `README.ko.md`), localized skill packs under `locales/{zh-CN,ja,ko}/`, and locale-specific anti-slop rules in `registry/forbidden-slop.json`.
- Interactive four-language WebGL 2.0 Systems Architect Workbench in `docs/index.html` with live `#version 300 es` SDF/diagnostic rendering, VAO + `std140` UBO state, non-blocking `PIXEL_PACK_BUFFER` (PBO) + `gl.fenceSync` readback telemetry, simulated `WEBGL_lose_context` recovery, a frame-budget/DPR clamp calculator, and an interactive triage router.
- Expanded schema-validated examples in `examples/postprocess-context-loss.output.json` (`debug`) and `examples/webgpu-migration-hybrid.output.json` (`migration`), plus WebGL 2.0 to WebGPU migration mappings in `skills/core/06-runtime-ops.md` and `references/02-webgl2-source-table.md`.
- Upgraded `scripts/validate_repo.py` with strict XML/SVG well-formedness and text-fit checks, exact module-set equality, four-language parity verification, active `forbidden-slop.json` scanning, and negative self-tests.

### Changed
- Redesigned `docs/assets/architecture.svg` and `docs/assets/skill-infographic.svg` (and rasterized PNG counterparts) as valid XML technical blueprints with verified container text-fit margins.
- Upgraded `fixtures/webgl2-smoke/index.html` to bind a dedicated VAO, use a 16-byte-aligned `std140` UBO, demonstrate `PIXEL_PACK_BUFFER` + `gl.fenceSync` readback, handle `webglcontextlost` / `webglcontextrestored`, and eliminate magic shader literals.
- Synchronized `registry/module-map.json`, `references/00-orchestrator.md`, and `skills/core/01-triage.md` so `architecture` and `migration` include `skills/core/05-shader-rules.md` with full relative paths.

## 1.0.1 - 2026-03-30

### Changed
- Tightened repository validation, documentation polish, and release metadata.

## 1.0.0 - 2026-03-30

### Added
- Initial modular WebGL 2.0 Systems Architect skill package, schemas, examples, smoke fixture, and validator.
