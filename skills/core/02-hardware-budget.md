# 02 - Hardware Probe and Frame Budget

## Purpose

Ground architecture and performance decisions in WebGL 2.0 capability limits, bandwidth math, and measured frame timings. Measure before cutting visible features.

## When to load

Load for `architecture` and `optimize` tasks, or whenever FPS drops, DPR scaling, memory bandwidth, or thermal throttling are involved.

## Inputs

- Target platforms, viewport dimensions, and FPS target (`30`, `60`, `90`, or `120`)
- Runtime WebGL 2.0 context parameters and extension availability if accessible
- Existing pass timings, frame-time logs, or differential feature toggles if available

## Rules

### 1. Query actual WebGL 2.0 capability limits first

Query the context directly with `gl.getParameter` and `gl.getExtension` instead of guessing device tiers from user-agent strings:

- Texture & volume bounds: `MAX_TEXTURE_SIZE`, `MAX_CUBE_MAP_TEXTURE_SIZE`, `MAX_3D_TEXTURE_SIZE`, `MAX_ARRAY_TEXTURE_LAYERS`, `MAX_TEXTURE_IMAGE_UNITS`, `MAX_VERTEX_TEXTURE_IMAGE_UNITS`
- MRT & MSAA bounds: `MAX_COLOR_ATTACHMENTS`, `MAX_DRAW_BUFFERS`, `MAX_SAMPLES`, `MAX_RENDERBUFFER_SIZE`
- Uniform & UBO bounds: `MAX_VERTEX_UNIFORM_VECTORS`, `MAX_FRAGMENT_UNIFORM_VECTORS`, `MAX_UNIFORM_BUFFER_BINDINGS`, `MAX_UNIFORM_BLOCK_SIZE`, `UNIFORM_BUFFER_OFFSET_ALIGNMENT`
- Transform feedback & vertex bounds: `MAX_VERTEX_ATTRIBS`, `MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS`, `MAX_VARYING_VECTORS`
- Key extensions: `EXT_disjoint_timer_query_webgl2`, `KHR_parallel_shader_compile`, `EXT_color_buffer_float`, `OES_texture_float_linear`, `WEBGL_compressed_texture_astc`, `WEBGL_compressed_texture_s3tc`, `WEBGL_lose_context`

Treat `WEBGL_debug_renderer_info` (`UNMASKED_RENDERER_WEBGL`) as optional telemetry; browsers frequently mask or disable it for privacy.

### 2. Rank evidence strictly

Use this hierarchy:

1. **Ring-buffered GPU timer queries (`EXT_disjoint_timer_query_webgl2`)**
   - Poll `gl.getQueryParameter(q, gl.QUERY_RESULT_AVAILABLE)` 2-3 frames later.
   - Check `gl.getParameter(ext.GPU_DISJOINT_EXT)` before trusting `gl.getQueryParameter(q, gl.QUERY_RESULT)`.
2. **Controlled differential measurements**
   - Toggle one pass, halve internal resolution, or clamp DPR while holding camera and scene state fixed.
3. **Explicit capability limits (`gl.getParameter`)**
4. **Heuristic device-tier estimates** (lowest rank; label as `estimated` or `unknown`).

### 3. Compute frame, fill-rate, and bandwidth budgets explicitly

State the budget math in every architecture or optimization plan:

```text
frameBudgetMs = 1000 / targetFPS
gpuBudgetMs   = frameBudgetMs - cpuMainThreadReserveMs - browserCompositorReserveMs
activePixels  = (cssWidth * targetDPR) * (cssHeight * targetDPR)
bandwidthBps  = activePixels * bytesPerPixelReadWriteAcrossPasses * targetFPS
```

At `60 FPS`, `frameBudgetMs = 16.67 ms`. Reserve `3.0-4.5 ms` for JS dispatch and browser compositing on mobile, leaving `12.0-13.5 ms` for GPU execution. If `msPerMegapixel` is measured across two DPR values, clamp DPR dynamically:

```text
targetDPR = min(devicePixelRatio, maxDPRCap, sqrt(gpuBudgetMs / (cssWidth * cssHeight * 1e-6 * msPerMegapixel)))
```

### 4. Define explicit capability tiers

Every multi-device architecture must specify at least three tiers (`low`, `mid`, `high`) and state what changes per tier:

- internal render scale and `targetDPR` cap (for example `1.0`, `1.5`, `2.0`)
- FBO attachment format (`RGBA8` vs `RGBA16F` gated on `EXT_color_buffer_float`)
- MSAA sample count (`0` vs `min(4, gl.getParameter(gl.MAX_SAMPLES))`)
- raymarch step counts, shadow/AO taps, and postprocess pass activation

### 5. Isolate the bottleneck before cutting quality

- **Fill-rate / fragment bound**: frame time drops roughly linearly when DPR or viewport area is halved.
- **Bandwidth / tile-flush bound**: frame time drops when reducing FBO switches, switching `RGBA16F` to `R11F_G11F_B10F`/`RGBA8`, or calling `gl.invalidateFramebuffer`.
- **Vertex / geometry bound**: frame time changes with triangle count or instancing, not viewport size.
- **CPU / driver sync bound**: frame time spikes on synchronous `gl.readPixels`, `gl.finish`, `getProgramParameter(LINK_STATUS)` stalls, or excessive `uniform*` calls.

## Failure modes

- Presenting guessed GPU TFLOPS as measured device performance
- Reading `EXT_disjoint_timer_query_webgl2` results in the same frame or ignoring `GPU_DISJOINT_EXT`
- Binding `bindBufferRange` offsets that are not multiples of `UNIFORM_BUFFER_OFFSET_ALIGNMENT`
- Cutting P0 visual cues before clamping DPR or half-res auxiliary passes

## Output contribution

Populate `inputs.hardware_data_quality`, `derivations` (frame budget, DPR clamp, bandwidth), `decisions` (tier table), and hardware `risks`.
