# Module 02 - Hardware Budget

## Purpose

Build a performance envelope from first principles without pretending the browser magically tells you everything about the GPU's secret organs.

## Core rule

Use a three-layer budget, in this order:

1. **API-visible capability limits**
2. **Measured frame-time evidence**
3. **Theoretical throughput estimates** only when trustworthy device data exists

Never invert that order.

## Layer 1 - Capability profile

Start with limits visible from WebGL:

- `MAX_TEXTURE_SIZE`
- `MAX_VARYING_VECTORS`
- `MAX_VERTEX_UNIFORM_VECTORS`
- `MAX_FRAGMENT_UNIFORM_VECTORS`
- `MAX_DRAW_BUFFERS`
- extensions such as:
  - `EXT_color_buffer_float`
  - `EXT_float_blend`
  - `EXT_disjoint_timer_query_webgl2`
  - `KHR_parallel_shader_compile`
  - compressed texture extensions

This defines what the renderer may attempt.

## Layer 2 - Measured budget

If timing data exists, prefer it over guessed FLOPS.

Recommended budgeting flow:

1. choose target frame time  
   `frameBudgetMs = 1000 / targetFPS`

2. reserve room for browser + app overhead  
   default planning split:
   - CPU-side app + browser: `30%`
   - GPU rendering: `70%`

3. derive a planning GPU budget  
   `gpuBudgetMs = frameBudgetMs * 0.70`

4. estimate per-pixel headroom from a representative pass  
   `msPerMegapixel = measuredPassMs / (pixelCount / 1e6)`

5. use that measurement to decide:
   - safe DPR cap
   - pass count
   - postprocess viability
   - ray-march step budget
   - shadow/AO sample budgets

If timer queries are unavailable, use stable frame-time deltas across controlled toggles:
- base scene
- base + shadows
- base + AO
- base + full-res postprocess

That differential measurement is more honest than invented "cycles per pixel" from missing hardware data.

## Layer 3 - Theoretical estimate

Use only if the device data is known from trusted hardware research or the user supplied it.

Formula:

```text
peakOpsPerSecond = shaderCores * clockHz * opsPerCyclePerCore
usableOpsPerSecond = peakOpsPerSecond * utilizationFactor
```

Planning defaults:
- `opsPerCyclePerCore = 2` for FMA-style accounting
- `utilizationFactor = 0.50` as a conservative planning number

Per-frame envelope:

```text
usableOpsPerFrame = usableOpsPerSecond / targetFPS
opsPerPixel = usableOpsPerFrame / pixelCount
```

Important: this is a planning sketch, not ground truth. Public core counts, clocks, and browser thermals often drift from reality.

## DPR and fill-rate policy

Always derive a DPR recommendation, because pixel count is the sneaky goblin that eats mobile performance.

```text
pixelCount = cssWidth * cssHeight * targetDPR^2
```

If you have a measured megapixel cost:

```text
maxMegapixels = gpuBudgetMs / msPerMegapixel
targetDPR = sqrt((maxMegapixels * 1e6) / (cssWidth * cssHeight))
```

Clamp:
- minimum `1.0`
- maximum `devicePixelRatio`
- project-specific ceiling such as `2.0` when mobile fill-rate dominates

## Tiering

Create a capability tier only after limits and measurements are known.

Suggested buckets:

- `tier 1 / conservative`
  - low varyings, no float FBO, weak draw buffer support, unstable timing
- `tier 2 / balanced`
  - solid baseline WebGL 2 limits, moderate resolution, selective postprocess
- `tier 3 / aggressive`
  - strong caps, good measured headroom, advanced passes viable

Do not treat tier names as quality labels. They are routing labels for render paths.

## Output fields

Return these fields to the orchestrator:

- `hardware_profile`
- `capability_tier`
- `frame_budget_ms`
- `gpu_budget_ms`
- `pixel_budget`
- `recommended_dpr`
- `measured_vs_estimated_confidence`
- `expensive_features_to_gate`

## Common failure modes

- assuming vendor FLOPS are reliable enough for fine-grained decisions
- using native DPR by default on mobile
- applying one budget to both raymarch and mesh pipelines
- treating extension presence as proof of speed rather than proof of possibility
