# 05 - GLSL ES 3.00 and Shader Math Rules

## Purpose

Keep WebGL 2.0 shaders portable, self-contained, numerically stable, and free of magic constants. Every shader starts with `#version 300 es`.

## When to load

Load whenever writing, reviewing, debugging, optimizing, or migrating GLSL ES 3.00 vertex or fragment shaders.

## Inputs

- Shader source or target shading algorithm
- Project class (`raster-mesh`, `sdf-raymarch`, `hybrid`, `postprocess`, `data-vis`, `ui`)
- Target GPU precision profile (mobile `mediump` FP16 vs desktop `highp` FP32)

## Rules

### 1. Enforce strict GLSL ES 3.00 (`#version 300 es`) stage contracts

Never mix legacy WebGL 1.0 (`attribute`, `varying`, `texture2D`, `gl_FragColor`) into WebGL 2.0 shaders:

- Start every shader file at byte 0 with `#version 300 es` followed by explicit precision declarations (`precision highp float; precision highp int;`).
- Use `layout(location = N) in` for vertex attributes, `in` / `out` for stage interface variables, and `layout(location = 0) out vec4 outColor;` (or `N` for MRT) for fragment outputs.
- Group shared per-frame and per-pass uniforms into `layout(std140) uniform FrameBlock { ... };` to share bindings across programs and map cleanly to WebGPU `GPUBindGroup` uniform buffers.
- Use `flat in` / `flat out` for integer IDs or instance indices (`gl_InstanceID`, `gl_VertexID`).

### 2. Ban free variables and unexplained magic literals

Every helper function must declare all inputs through parameters, `std140` uniform blocks, stage `in` variables, or named `#define` / `const` declarations. Explain every numeric constant with its geometric, physical, or numerical origin:

```glsl
// 0.5 mm surface hit threshold in head-radius units (1.0 unit = 0.12 m):
const float SURF_HIT_EPS = 0.0042;
// Tetrahedral finite-difference offset scaled to 2x hit epsilon to avoid mediump cancellation:
const float NORMAL_GRAD_EPS = 0.0084;
// Dielectric F0 for skin / non-metals (IOR = 1.38 -> ((1.38 - 1.0) / (1.38 + 1.0))^2 = 0.0255):
const float SKIN_F0 = 0.0255;
```

### 3. Guard precision, divisions, roots, and transcendentals

Mobile GPUs execute `mediump` as IEEE 754 FP16 (range `+-65504`, minimum positive normal `6.10e-5`, ~3.3 decimal digits):

- Use `highp` for world/camera positions, ray origins/directions, elapsed time `uTime` (wrap `uTime` modulo period on CPU before upload), depth math, and SDF distance accumulation.
- Guard denominators, normalizations, and power bases:
  - `inversesqrt(max(dot(v, v), 1e-12))` or `normalize(v + vec3(0.0, 0.0, 1e-8))`
  - `sqrt(max(x, 0.0))`
  - `pow(max(base, 0.0), expVal)` (`pow` with negative or zero base is undefined in GLSL ES 3.00)
  - `clamp(dot(N, V), 0.0, 1.0)` before Fresnel or ACES/AgX tone mapping

### 4. Protect derivatives and mipmap selection across control flow

In GLSL ES 3.00, `dFdx`, `dFdy`, `fwidth`, and implicit-LOD `texture(sampler, uv)` require uniform control flow across each 2x2 pixel quad:

- Compute `vec2 dPdx = dFdx(uv); vec2 dPdy = dFdy(uv);` **before** entering a non-uniform `if`, `for`, or raymarch `break` loop, then sample inside the branch with `textureGrad(uTex, uv, dPdx, dPdy)` or `textureLod(uTex, uv, lod)`.
- For direct integer texel lookups without filtering, use `texelFetch(uTex, ivec2(coord), 0)`.

### 5. Bound loops and SDF raymarching

- All `for` loops must use compile-time or uniform-bounded step counts (`MAX_PRIMARY_STEPS`, `MAX_SHADOW_STEPS`) with an early exit when `abs(d) < SURF_HIT_EPS` or `t > MAX_TRACE_DIST`.
- When using non-Lipschitz SDF deformations (twist, bend, displacement noise), multiply the step increment by an explicit Lipschitz safety factor (`stepScale = 0.65` to `0.85`) to prevent surface overshoot.
- Use 4-tap tetrahedral normals instead of 6-tap central differences:
  ```glsl
  vec3 calcNormal(vec3 p, float eps) {
    const vec2 k = vec2(1.0, -1.0);
    return normalize(
      k.xyy * mapScene(p + k.xyy * eps) +
      k.yyx * mapScene(p + k.yyx * eps) +
      k.yxy * mapScene(p + k.yxy * eps) +
      k.xxx * mapScene(p + k.xxx * eps)
    );
  }
  ```

## Failure modes

- Using `varying` or `gl_FragColor` in a `#version 300 es` shader (compile error)
- Calling `texture(uTex, uv)` or `fwidth()` inside a dynamic raymarch or early-exit branch (quad-edge seams on mobile/ANGLE)
- Passing unwrapped `performance.now()` seconds into `mediump` trig/noise functions (jitter after a few minutes)
- Packing `vec3` arrays inside `std140` uniform blocks without accounting for 16-byte (`vec4`) base alignment

## Output contribution

Populate `derivations` (constants, precision choices, loop bounds), shader `decisions`, and numerical `risks`.
