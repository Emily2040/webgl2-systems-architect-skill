# WebGL2 Source and Test Matrix

## Purpose

Use this file when an answer needs source-backed WebGL2 guidance, compatibility gates, or a production test plan. Prefer primary references over folklore.

## Authoritative anchors

| Area | Primary source | Use in this skill |
|---|---|---|
| General WebGL performance | MDN WebGL best practices: https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices | DPR caps, per-pixel budgets, async readback, shader compile/link guidance, mipmaps, `texStorage`, framebuffer invalidation |
| WebGL2 API behavior | Khronos WebGL 2.0 spec: https://registry.khronos.org/webgl/specs/latest/2.0/ | API limits, WebGL2-vs-WebGL1 differences, query timing rules, GLSL ES 3.00 constraints, uniform block rules |
| Extensions | Khronos WebGL extension registry: https://registry.khronos.org/webgl/extensions/ | Extension names, ratified status, browser/vendor-specific caution |
| Extension usage | MDN Using WebGL extensions: https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/Using_Extensions | Require explicit `getExtension()` gates and fallback behavior |
| Async shader link polling | MDN `KHR_parallel_shader_compile`: https://developer.mozilla.org/en-US/docs/Web/API/KHR_parallel_shader_compile | Poll program completion only when the extension exists; do not claim universal support |
| Context loss | Khronos HandlingContextLost: https://wikis.khronos.org/webgl/HandlingContextLost | Cancel loops, recreate resources, avoid infinite restore cycles |
| Browser smoke tests | Playwright screenshots: https://playwright.dev/docs/test-snapshots | Screenshot baselines with stable environment notes |
| Conformance thinking | Khronos WebGL conformance: https://wikis.khronos.org/webgl/Testing/Conformance | Keep app smoke tests distinct from browser conformance tests |

## Compatibility gates

Every WebGL2 architecture or patch should name these gates when relevant:

1. `canvas.getContext("webgl2", attributes)` succeeds.
2. Required limits are queried with `gl.getParameter`.
3. Required extensions are requested with `gl.getExtension`.
4. Extension absence has an explicit fallback or feature cut.
5. Context loss handlers stop the active frame loop, abandon stale handles, and rebuild resources in dependency order.
6. Timing data avoids same-frame query assumptions and handles disjoint timer results.

## Test strategy matrix

| Layer | Check | Why |
|---|---|---|
| Skill package | `python scripts/validate_repo.py` on Ubuntu and Windows | Catches wrapper, schema, example, and packaging drift |
| Structured output | Validate examples against `schemas/*.json` | Prevents silent contract breakage |
| Shader fixture | Compile/link a minimal WebGL2 program | Proves the browser target can execute WebGL2 |
| Browser smoke | Load `fixtures/webgl2-smoke/index.html` and read `window.__webgl2Smoke.ok` | Gives CI or local tests a concrete rendering target |
| Visual regression | Playwright screenshot comparison in one stable OS/browser environment | Catches layout or rendering regressions with controlled variance |
| Context loss | Simulate context loss where supported, then verify restore path | Prevents recovery loops and stale resource use |
| Performance | Repeatable camera path plus feature toggles and timer queries when available | Finds actual bottlenecks before cutting visible features |
