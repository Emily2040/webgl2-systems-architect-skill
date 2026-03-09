# Module 06 - Runtime Ops

## Purpose

Engineer the JS/WebGL runtime so it does not sabotage the GPU with needless state churn, allocations, leaks, or synchronization stalls.

## Core idea

The browser-visible WebGL API is a command submission layer with expensive crossings. Optimize orchestration first, then optimize draw or shader details.

## State policy

Shadow mutable GL state on the JS side:

- program
- VAO
- framebuffer
- active texture unit
- bound textures per unit
- depth/blend/cull toggles

Only issue a GL call when the desired value differs from the shadow state.

Why:
- redundant `useProgram`, `bindTexture`, `bindFramebuffer`, and enable/disable churn burns CPU time
- on tiled GPUs, framebuffer switches are especially expensive

## Resource ownership

Track every GPU object through a central resource registry:

- buffers
- textures
- renderbuffers
- framebuffers
- VAOs
- shaders
- programs

Support:
- `register`
- `retain`
- `release`
- `abandonAll` on context loss
- `reportLeaks`

Do not create or destroy resources casually inside the frame loop.

## Buffer and layout rules

- prefer interleaved static vertex data unless attributes update independently
- document UBO layouts; avoid `vec3` in `std140` blocks
- orphan dynamic buffers before rewriting when the same buffer may still be in flight
- keep instance data compact and aligned

## Draw ordering

Sort in this priority order:

1. render target / framebuffer
2. program or pipeline class
3. uniform block or material set
4. texture set
5. VAO or mesh

Opaque:
- front-to-back when depth helps

Transparent:
- back-to-front unless a special technique changes the rules

For fullscreen pipelines:
- optimization is mostly pass count, resolution, and bandwidth, not draw count

## Context attributes

Treat context attributes as measured policies, not universal commandments.

Benchmark and justify:
- `alpha`
- `depth`
- `stencil`
- `antialias`
- `powerPreference`
- `preserveDrawingBuffer`
- `desynchronized`

Examples:
- fullscreen raymarch with no geometry depth may not need a depth buffer
- some integrated GPU paths behave better with `alpha: true` plus opaque clear
- MSAA may cost more than a domain-specific AA pass

## Synchronization hazards

Avoid in hot paths:
- `gl.getError()`
- direct `readPixels`
- frequent `finish`-style behavior
- debug-info queries after startup
- allocations that trigger GC mid-frame
- DOM reads that force layout

When readback is required:
- prefer pipelined PBO + fence strategies

## Context loss and watchdogs

Every production renderer needs two ugly but necessary survival skills:

1. context loss recovery
2. a render-loop circuit breaker

Plan for:
- canceling the frame loop on loss
- abandoning stale handles without deleting them on the dead context
- recreating resources in dependency order on restore
- stopping restart loops after a capped number of failures

## Output fields

Return:

- `state_policy`
- `resource_policy`
- `draw_order_policy`
- `sync_hazards`
- `context_loss_plan`
- `watchdog_plan`
- `likely_runtime_bottlenecks`

## Common failure modes

- doing allocations or string building in the frame loop
- switching FBOs more often than the pass graph requires
- using draw-count metrics to debug a fullscreen fragment bottleneck
- forgetting that one bad `readPixels` can erase the gains from ten careful optimizations
