# Module 03 - Pipeline and Concurrency

## Purpose

Design the render graph, startup flow, and async strategy. The key first-principles fact is simple: one WebGL context submits GPU work in order. If the design ignores that, the word "parallel" becomes decorative confetti.

## Choose a pipeline archetype

Select the dominant archetype:

- `forward raster`
  - best when draw count is moderate and transparency or material simplicity dominates
- `deferred or clustered raster`
  - only when the lighting count or material complexity justifies the G-buffer cost
- `fullscreen SDF raymarch`
  - best for procedural scenes where geometry upload is secondary to fragment cost
- `hybrid`
  - mesh world plus procedural overlays, decals, SDF effects, or postprocess
- `postprocess stack`
  - when visual style depends on screen-space passes

Document why the chosen archetype beats the alternatives.

## Serial vs parallel reality

### Usually serial on one context

- draw submission
- state changes
- pass execution through dependent FBOs
- texture upload commands once they hit the context
- framebuffer completeness checks
- readback that lacks a fence/PBO strategy

### Good async or parallel candidates

- network fetches for textures, meshes, and config
- CPU-side parse, decode, decompression, transcode
- image decode to `ImageBitmap`
- worker-side terrain generation, culling, animation baking, or data prep
- shader-source generation or static validation
- compile-status polling with `KHR_parallel_shader_compile`
- placeholder-resource boot flow while final assets arrive

## Async recommendation rules

Recommend async only when it removes real waiting or main-thread contention.

Use this decision table:

| Work item | Async / parallel? | Notes |
|---|---|---|
| texture fetch + decode | yes | overlap I/O and CPU with current frame |
| mesh parse + quantization decode | yes | worker-friendly |
| shader compile polling | partial | compile may continue asynchronously in driver; poll completion rather than blocking |
| draw calls on one context | no | ordering remains serialized |
| FBO pass chain | no | hard dependency graph |
| `readPixels` + PBO + fence | yes, pipelined | asynchronous readback pattern |
| `readPixels` direct | no | CPU stall magnet |
| main-thread DOM reads in frame | no | remove rather than parallelize |

## OffscreenCanvas and workers

Use worker-based rendering only when the app benefits from isolating the render loop from main-thread jank and the browser targets support the path acceptably for the product.

Worker architecture:

1. main thread owns UI and input marshaling
2. worker owns `OffscreenCanvas` and WebGL context
3. asset fetch/decode can happen in worker or in dedicated workers
4. communication uses structured messages, not shared mutable chaos

Do not force worker rendering into a project whose primary issue is shader cost rather than main-thread contention.

## Startup graph

Build a boot sequence with explicit dependencies.

Recommended pattern:

1. create context and capability profile
2. create placeholder resources
3. start independent async tasks in parallel:
   - fetch textures
   - fetch meshes
   - generate or load shader source
   - decode images or transcode compressed textures
4. compile programs as early as possible
5. upload ready resources in bounded batches
6. swap placeholders for final resources
7. mark features ready incrementally instead of blocking the first frame

The user should get a first image early, even if it is incomplete.

## Pass graph rules

- sort by render target first; FBO switches are expensive on tiled GPUs
- keep pass count honest; every fullscreen pass taxes fill-rate
- collapse passes when the saved bandwidth exceeds the extra shader cost
- split passes when divergence or overdraw becomes the real bottleneck
- for raymarch pipelines, count steps and map-cost before adding "cinematic" fog, AO, and shadow sugar

## Output fields

Return:

- `pipeline_archetype`
- `pass_graph`
- `serial_tasks`
- `parallel_tasks`
- `async_boot_plan`
- `worker_recommendation`
- `compile_strategy`
- `readback_strategy`

## Common failure modes

- claiming a renderer is "parallel" because resource fetch uses `await`
- pushing all startup work behind one giant promise and showing a blank canvas
- using workers for prestige while the real bottleneck is fragment cost
- treating `KHR_parallel_shader_compile` as a universal guarantee instead of an extension-gated optimization
