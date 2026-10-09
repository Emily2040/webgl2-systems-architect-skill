# 07 - Validation, Profiling, and CI Gates

## Purpose

Verify that a WebGL 2.0 renderer or skill package compiles, renders non-trivial pixels, recovers from context loss, and fails loudly when an invariant breaks. Never ship on compile-only confidence.

## When to load

Load for `architecture`, `debug`, `optimize`, `review`, and `migration` tasks.

## Inputs

- Candidate shaders, JS/TS runtime code, or structured architecture plan
- Available test environment (local browser, headless Chrome/Playwright, or CI runner)
- Target performance, visual, and portability gates

## Rules

### 1. Run the five-stage WebGL 2.0 verification ladder

Every implementation or debug patch must specify checks across these five stages:

1. **Shader compile & program link gate**
   - Verify `#version 300 es` is at byte 0.
   - Check `gl.getShaderParameter(s, gl.COMPILE_STATUS)` and `gl.getProgramParameter(p, gl.LINK_STATUS)`; surface `getShaderInfoLog` / `getProgramInfoLog` with line numbers on failure.
2. **Framebuffer completeness & state gate**
   - Verify every custom FBO with `const status = gl.checkFramebufferStatus(gl.FRAMEBUFFER);` and require `status === gl.FRAMEBUFFER_COMPLETE`.
   - Explicitly guard against `gl.FRAMEBUFFER_INCOMPLETE_ATTACHMENT` (unrenderable float format without `EXT_color_buffer_float`) and `gl.FRAMEBUFFER_INCOMPLETE_MULTISAMPLE` (mismatched sample counts across attachments).
   - Poll `gl.getError()` in debug/CI builds after setup and first-frame draw calls, never inside the production hot loop.
3. **Pixel & PBO readback smoke gate**
   - Render a deterministic frame and verify non-clear, non-`NaN` pixel values at known coordinates (see `fixtures/webgl2-smoke/index.html`).
   - Test both immediate smoke readback (`gl.readPixels`) and non-blocking `gl.PIXEL_PACK_BUFFER` + `gl.fenceSync` completion.
4. **Context-loss drill**
   - Trigger `gl.getExtension("WEBGL_lose_context")?.loseContext()` followed by `restoreContext()`, and assert that `window.__webgl2Smoke.ok` (or application render state) recovers without `INVALID_OPERATION` errors.
5. **Differential performance & visual regression gate**
   - Capture screenshots under a pinned OS/browser/DPR configuration and measure per-pass deltas by toggling one pass at a time.

### 2. Design diagnostic shader modes for fast root-cause isolation

When debugging visual or numerical defects, recommend one-switch diagnostic outputs:

- world/view normal visualization (`outColor = vec4(N * 0.5 + 0.5, 1.0)`)
- normalized raymarch step-count or overdraw heatmap
- UV / mip-level discontinuity check (`fwidth(uv)`)
- `isnan(x)` / `isinf(x)` hot-pink (`vec4(1.0, 0.0, 1.0, 1.0)`) detector pass

### 3. Enforce repository and schema self-tests in CI

For changes to this skill repository:

- Run `python scripts/validate_repo.py` on both Linux and Windows runners.
- Validate all `examples/*.output.json` files against `schemas/authoring-base.json` or `schemas/runtime-compact.json`.
- Parse all `.svg` assets as strict XML (`xml.etree.ElementTree.fromstring`) and verify text-fit margins.
- Enforce `registry/forbidden-slop.json` across all four supported locales (`en`, `zh-CN`, `ja`, `ko`).
- Run negative self-tests in `validate_repo.py` to confirm that broken XML, unmapped modules, schema violations, and banned slop phrases are actively rejected.

### 4. Calibrate confidence to the evidence tier

State the verification confidence explicitly at the end of the response:

- **High confidence**: verified by live WebGL 2.0 execution, pixel readback, and GPU/frame timing on target hardware.
- **Medium confidence**: shader/code inspected and static/smoke checks passed, but target device timings are estimated.
- **Low confidence**: prompt-only architecture plan without code or device telemetry; assumptions must be validated first.

## Failure modes

- Declaring a multi-pass FBO pipeline ready without checking `gl.checkFramebufferStatus(gl.FRAMEBUFFER)`
- Calling `gl.getError()` inside every production draw call (forces a CPU/GPU synchronization stall)
- Running screenshot diffs across different GPU vendors without tolerance thresholds or software/pinned baselines
- Writing validator checks that pass even when an SVG is malformed XML or a module path is missing

## Output contribution

Populate `deliverables` (validation matrix), `risks`, and final verification steps.
