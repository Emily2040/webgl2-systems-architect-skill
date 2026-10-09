# WebGL2 Source and Test Matrix

## Purpose

Use this file whenever an engineering answer requires source-backed WebGL 2.0 or WebGPU migration guidance, explicit hardware capability gates, extension fallback rules, or a reproducible browser verification plan. Prefer primary specifications.


## Authoritative anchors

| Area | Primary source | Use in this skill |
|---|---|---|
| General WebGL performance | MDN WebGL best practices: https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices | DPR caps, per-pixel budgets, async PBO readback, shader compile/link guidance, mipmaps, `texStorage2D`, `invalidateFramebuffer` |
| WebGL 2.0 API behavior | Khronos WebGL 2.0 specification: https://registry.khronos.org/webgl/specs/latest/2.0/ | API limits, WebGL2-vs-WebGL1 differences, query timing rules, VAO/UBO binding rules, FBO completeness |
| GLSL ES 3.00 language | Khronos OpenGL ES SL 3.00 specification: https://registry.khronos.org/OpenGL/specs/es/3.0/GLSL_ES_Specification_3.00.pdf | `#version 300 es`, `in`/`out`, `layout(std140)`, precision qualifiers, derivative behavior under non-uniform flow |
| Extensions | Khronos WebGL extension registry: https://registry.khronos.org/webgl/extensions/ | Ratified extension names (`EXT_color_buffer_float`, `EXT_disjoint_timer_query_webgl2`, `OES_texture_float_linear`) |
| Extension usage | MDN Using WebGL extensions: https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/Using_Extensions | Explicit `gl.getExtension()` gates and tier degradation |
| Async shader link polling | MDN `KHR_parallel_shader_compile`: https://developer.mozilla.org/en-US/docs/Web/API/KHR_parallel_shader_compile | Poll `ext.COMPLETION_STATUS_KHR` before querying `LINK_STATUS` |
| Context loss | Khronos HandlingContextLost: https://wikis.khronos.org/webgl/HandlingContextLost | `event.preventDefault()`, cancel `requestAnimationFrame`, rebuild VAOs/UBOs/textures on `webglcontextrestored` |
| WebGPU migration | W3C WebGPU & WGSL specifications: https://www.w3.org/TR/webgpu/ and https://www.w3.org/TR/WGSL/ | Map VAOs to `GPUVertexBufferLayout`, UBOs/samplers to `GPUBindGroup`, FBOs to `GPURenderPassDescriptor`, clip-space Z `[-1, 1]` to `[0, 1]` |
| Visual regression tests | Playwright screenshots: https://playwright.dev/docs/test-snapshots | Deterministic screenshot baselines with pinned OS/browser/GPU flags |
| Conformance thinking | Khronos WebGL conformance: https://wikis.khronos.org/webgl/Testing/Conformance | Keep application smoke tests distinct from browser conformance suites |

## Compatibility gates

Every WebGL 2.0 architecture or patch must verify these seven gates when applicable:

1. `canvas.getContext("webgl2", attributes)` succeeds and handles `null` with an explicit fallback UI.
2. Required hardware limits (`MAX_TEXTURE_SIZE`, `MAX_COLOR_ATTACHMENTS`, `MAX_SAMPLES`, `UNIFORM_BUFFER_OFFSET_ALIGNMENT`) are queried with `gl.getParameter`.
3. Optional extensions (`EXT_color_buffer_float`, `EXT_disjoint_timer_query_webgl2`, `KHR_parallel_shader_compile`) are requested with `gl.getExtension`.
4. Extension absence triggers a deterministic fallback path (for example `RGBA16F` -> `RGBA8` or synchronous compile fallback).
5. Framebuffers verify `gl.checkFramebufferStatus(gl.FRAMEBUFFER) === gl.FRAMEBUFFER_COMPLETE` and matching multisample counts across attachments.
6. Context loss handlers call `event.preventDefault()`, stop the active frame loop, discard stale `WebGLObject` handles, and rebuild resources in dependency order on `webglcontextrestored`.
7. GPU timing and pixel readback avoid same-frame synchronous stalls by polling `QUERY_RESULT_AVAILABLE` / `GPU_DISJOINT_EXT` and `gl.fenceSync` with `gl.PIXEL_PACK_BUFFER`.

## Test strategy matrix

| Layer | Check | Why |
|---|---|---|
| Skill package | `python scripts/validate_repo.py` on Ubuntu and Windows | Verifies schemas, routing equality, XML/SVG bounds, 4-language parity, anti-slop rules, and negative self-tests |
| Structured output | Validate `examples/*.output.json` against `schemas/*.json` | Prevents contract drift across intents and project classes |
| Shader & state fixture | Compile/link `#version 300 es` with VAO + `std140` UBO | Proves standard WebGL 2.0 state setup without legacy WebGL 1 fallbacks |
| Browser smoke | Load `fixtures/webgl2-smoke/index.html` and check `window.__webgl2Smoke.ok` | Verifies live rendering, PBO/fence readback, and context-loss hooks |
| Workbench proof | Load `docs/index.html` in headless browser across `en`, `zh-CN`, `ja`, `ko` | Verifies interactive WebGL 2.0 canvas telemetry, calculators, and localization |
| Context loss | Trigger `WEBGL_lose_context.loseContext()` and `restoreContext()` | Prevents recovery loops and stale handle reuse |
| Performance | Repeatable camera path plus pass toggles and disjoint timer queries | Isolates fill-rate, bandwidth, or vertex bottlenecks before cutting features |
