# 03 - Pipeline Topology and Concurrency

## Purpose

Design render pass graphs, startup flows, and asynchronous pipelines that match how WebGL 2.0 actually executes on CPU threads and a single GPU queue. Single contexts serialize draw calls.

## When to load

Load for `architecture`, `implementation`, `optimize`, and `migration` tasks involving pass graphs, FBO chains, worker pipelines, shader compilation, or readback.

## Inputs

- Project class (`raster-mesh`, `sdf-raymarch`, `hybrid`, `postprocess`, `data-vis`, `ui`)
- Target pass chain, asset sizes, and startup latency budget
- Browser support for `OffscreenCanvas`, Web Workers, and `KHR_parallel_shader_compile`

## Rules

### 1. Choose context attributes by requirement, not habit

Declare `canvas.getContext("webgl2", attrs)` options explicitly:

- `alpha`: `false` for opaque canvases to skip browser page-compositor blending; `true` only when transparent DOM compositing is required
- `depth` / `stencil`: enable only when the default framebuffer uses depth or stencil testing (offscreen FBOs manage their own renderbuffers)
- `antialias`: `false` when rendering into offscreen postprocess FBOs or SDF raymarchers; use `gl.renderbufferStorageMultisample` + `gl.blitFramebuffer` for explicit MSAA resolve
- `powerPreference`: `"high-performance"` for sustained 3D/raymarch workloads; `"default"` or `"low-power"` for battery-sensitive UI/data-vis
- `preserveDrawingBuffer`: `false` unless persistent frame accumulation or synchronous external capture requires it
- `desynchronized`: enable only after verifying tear-free behavior across target browsers

### 2. Separate true parallel work from serial single-context GL submission

Be explicit about which lane each task belongs to:

- **Parallel on CPU / Web Workers**
  - `fetch`, JSON/glTF parsing, Draco/Meshopt decompression, KTX2/Basis Universal transcoding
  - BVH/octree construction, frustum culling, terrain chunk generation, and typed-array vertex packing (`Transferable` `ArrayBuffer`s)
  - `createImageBitmap` decoding off the main thread before `texSubImage2D`
- **Pipelined across frames (non-blocking GPU/CPU overlap)**
  - Shader compile/link polling with `KHR_parallel_shader_compile`:
    ```js
    const ext = gl.getExtension("KHR_parallel_shader_compile");
    // Poll each frame before querying LINK_STATUS to avoid blocking the main thread:
    if (!ext || gl.getProgramParameter(prog, ext.COMPLETION_STATUS_KHR)) {
      const ok = gl.getProgramParameter(prog, gl.LINK_STATUS);
    }
    ```
  - Asynchronous GPU readback using `gl.PIXEL_PACK_BUFFER` (PBO) and `gl.fenceSync`:
    ```js
    gl.bindBuffer(gl.PIXEL_PACK_BUFFER, pbo);
    gl.readPixels(x, y, w, h, gl.RGBA, gl.UNSIGNED_BYTE, 0); // byte offset 0 into PBO
    gl.bindBuffer(gl.PIXEL_PACK_BUFFER, null);
    const fence = gl.fenceSync(gl.SYNC_GPU_COMMANDS_COMPLETE, 0);
    gl.flush();
    // Poll on a later frame:
    const state = gl.clientWaitSync(fence, 0, 0);
    if (state === gl.ALREADY_SIGNALED || state === gl.CONDITION_SATISFIED) {
      gl.bindBuffer(gl.PIXEL_PACK_BUFFER, pbo);
      gl.getBufferSubData(gl.PIXEL_PACK_BUFFER, 0, dstUint8Array);
      gl.bindBuffer(gl.PIXEL_PACK_BUFFER, null);
      gl.deleteSync(fence);
    }
    ```
- **Strictly serial on one `WebGL2RenderingContext`**
  - State changes (`bindFramebuffer`, `useProgram`, `bindVertexArray`), resource uploads (`bufferSubData`, `texSubImage2D`), and draw calls (`drawElementsInstanced`, `drawArrays`).

### 3. Stage the first-frame startup sequence

Never block Frame 1 behind full-scene shader compilation and high-res texture uploads:

1. Create context, query limits/extensions, and allocate immutable 1x1 fallback textures (`texStorage2D`).
2. Compile only the bootstrap/primary pass shader and render an immediate Frame 1.
3. Stream meshes/textures in workers and poll auxiliary shader programs via `COMPLETION_STATUS_KHR` across subsequent frames.

### 4. Bound the pass graph and sort state transitions

For every pass in the graph, document:

- input textures/UBOs, output FBO target (`drawBuffers`), resolution scale (`1.0x`, `0.5x`, `0.25x`), and attachment formats
- sort order inside raster passes: **Render Target (FBO) -> Program -> UBO/Texture Bindings -> VAO -> Draw Call**
- never sample a texture while it is bound as an active `COLOR_ATTACHMENTi` or `DEPTH_ATTACHMENT` on the current FBO (feedback loop undefined behavior)

## Failure modes

- Wrapping sequential `gl.*` calls in `async`/`await` and claiming parallel GPU execution
- Querying `gl.getProgramParameter(prog, gl.LINK_STATUS)` immediately after `gl.linkProgram(prog)` while `COMPLETION_STATUS_KHR` is still `false`
- Calling `gl.readPixels` into a CPU `Uint8Array` every frame without a PBO and `gl.fenceSync`
- Allocating new FBOs, textures, or buffers inside `requestAnimationFrame`

## Output contribution

Populate `decisions` (context attributes, pass graph, startup sequence), `parallel_plan`, and concurrency `risks`.
