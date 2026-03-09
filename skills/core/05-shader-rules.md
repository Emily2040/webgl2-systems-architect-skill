# Module 05 - Shader Rules

## Purpose

Control GLSL complexity, numerical stability, and edit safety. Shader bugs are slippery little gremlins because a tiny mistake multiplies across millions of invocations.

## Non-negotiables

- declare precision intentionally; default to `highp float` in fragment shaders unless a measured reason exists to lower it
- every function is self-contained
- no free variables inside helper functions
- every domain-specific numeric literal gets a derivation comment or a named constant
- every loop is bounded
- branchy logic should be justified; otherwise prefer algebraic selection with `mix`, `step`, `smoothstep`, or masks
- all compile changes follow a dependency audit and quick recompile cycle

## Self-containment rule

Bad:
```glsl
float animate(vec3 p) {
  return sin(p.x + u_time);
}
```

Good:
```glsl
float animate(vec3 p, float time) {
  return sin(p.x + time);
}
```

All external dependencies must arrive through parameters, uniforms, varyings, UBOs, textures, or preprocessor defines.

## Numeric derivation rule

Allowed without comment:
- mathematical identities such as `0.0`, `1.0`, `2.0`
- canonical vector constructors or normalization helpers when their meaning is obvious

Not allowed without explanation:
- thresholds
- falloff distances
- roughness clamps
- AO reach
- ray epsilon
- shadow softness
- noise octave counts
- blend radii

Example:
```glsl
float pixelSize = 2.0 * tan(fovRadians * 0.5) * distanceToSurface / resolution.y;
float normalEps = max(0.0002, 0.5 * pixelSize); // 0.5x pixel footprint keeps normals stable without washing out detail
```

## Precision and branching

- use `highp` for position, distance, lighting, and depth-sensitive math
- lower precision only for proven-safe values such as some color intermediates or low-range UV operations
- avoid divergence in hot fragment paths
- if a branch is rare and skips expensive work, keep it and document why it wins

## Raymarch-specific rules

Use these only for SDF or signed-distance pipelines:

- derive normal epsilon from projected pixel footprint
- cap ray steps from scene scale and minimum feature size
- reduce step factor only near the surface or in pathological fields
- ensure `smin` blend radius does not exceed the smallest blended feature scale
- compute AO and shadow sample counts from the cavity or penumbra scale, not from mood

## Raster-specific rules

Use these for mesh pipelines:

- prefer UBOs for shared camera/light data
- respect varying and uniform budgets
- document vertex attribute layouts and alignment
- move non-fragment work upstream when interpolation error is acceptable
- use derivatives and mip choice intentionally for texture detail stability

## Revision safety protocol

For every shader edit:

1. dependency audit  
   list every external symbol touched by the function

2. copy-compile  
   duplicate the function under a temporary name if the edit is risky

3. edit-compile  
   make the change and compile immediately

4. rename-compile  
   if symbols changed, update all references and compile again

5. remove backup  
   delete the temporary copy only after success

This sounds fussy because it is fussy. Fussy beats losing 40 minutes to one missing identifier.

## Output fields

Return:

- `shader_risks`
- `numeric_derivations`
- `compile_hazards`
- `branching_hotspots`
- `precision_recommendations`
- `patch_rules`

## Common failure modes

- hiding important assumptions in globals
- stacking unexplained magic numbers until the shader becomes folklore
- chasing ALU micro-optimizations while overdraw or pass count dominates
- treating every branch as evil instead of measuring the actual hotspot
