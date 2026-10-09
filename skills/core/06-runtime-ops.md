# 06 - State, Resources, Context Loss, and WebGPU Migration

## Purpose

Prevent WebGL 2.0 state leaks, VRAM leaks, mobile tile-bandwidth stalls, and broken context recovery while keeping resource abstractions ready for WebGPU migration. Track every GPU handle.

## When to load

Load on every intent (`architecture`, `implementation`, `debug`, `optimize`, `review`, `migration`).

## Inputs

- Host JS/TS renderer code, pass setup, resize logic, and event listeners
- Resource creation and disposal paths (textures, buffers, VAOs, Samplers, FBOs, programs)
- Migration target if transitioning from WebGL 1 to WebGL 2.0 or WebGL 2.0 to WebGPU

## Rules

### 1. Isolate pass state and use WebGL 2.0 native objects

Every pass must set the state it relies on and restore non-default modes:

- **Vertex Array Objects (VAOs)**: Always create a VAO (`gl.createVertexArray()`), record all `bindBuffer(ARRAY_BUFFER)`, `enableVertexAttribArray`, `vertexAttribPointer`, and `vertexAttribDivisor` calls once at init, and bind only the VAO (`gl.bindVertexArray(vao)`) inside the frame loop. Even fullscreen `gl_VertexID` triangle passes require a bound VAO in WebGL 2.0.
- **Uniform Buffer Objects (UBOs)**: Bind `std140` blocks via `gl.uniformBlockBinding(prog, blockIdx, bindingPoint)` and `gl.bindBufferBase(gl.UNIFORM_BUFFER, bindingPoint, ubo)`. When using `gl.bindBufferRange`, align byte offsets to `gl.getParameter(gl.UNIFORM_BUFFER_OFFSET_ALIGNMENT)`.
- **Sampler objects**: Decouple filtering/wrapping from texture storage with `gl.createSampler()` and `gl.bindSampler(unit, sampler)` so one texture can be sampled as linear and nearest in the same pass.
- **Explicit pass state**: Explicitly set `viewport`, `scissor`, `depthMask`, `depthFunc`, `enable`/`disable(BLEND, DEPTH_TEST, CULL_FACE, SCISSOR_TEST)`, and `drawBuffers`.

### 2. Allocate immutable textures and invalidate transient attachments

- Prefer `gl.texStorage2D(target, levels, internalFormat, width, height)` (and `texStorage3D`) + `gl.texSubImage2D` over mutable `gl.texImage2D`. Immutable storage eliminates driver mip-completeness validation overhead at draw time.
- Choose explicit sized internal formats (`RGBA8`, `SRGB8_ALPHA8`, `RG16F`, `RGBA16F`, `R11F_G11F_B10F`, `DEPTH_COMPONENT24`, `DEPTH24_STENCIL8`).
- On tiled mobile GPUs (Apple, Adreno, Mali), call `gl.invalidateFramebuffer(gl.FRAMEBUFFER, [gl.DEPTH_ATTACHMENT, gl.STENCIL_ATTACHMENT])` after resolving or finishing a pass so the driver skips flushing transient tile memory back to system RAM.

### 3. Handle resize, disposal, and context loss cleanly

- **Resize**: Debounce `ResizeObserver` / DPR changes, clamp `canvas.width` and `canvas.height` to `[1, gl.getParameter(gl.MAX_RENDERBUFFER_SIZE)]`, and reallocate size-dependent FBO attachments only when pixel dimensions change.
- **Explicit disposal**: Pair every `createBuffer`, `createTexture`, `createFramebuffer`, `createRenderbuffer`, `createVertexArray`, `createSampler`, `createProgram`, and `createQuery` with its `delete*` call on teardown. Detach and delete compiled `WebGLShader` objects immediately after `gl.linkProgram(prog)` succeeds.
- **Context loss & restore**:
  ```js
  canvas.addEventListener("webglcontextlost", (e) => {
    e.preventDefault(); // Required to allow restoration
    cancelAnimationFrame(rafId);
    rafId = 0;
  });
  canvas.addEventListener("webglcontextrestored", () => {
    rebuildAllResourcesInDependencyOrder(); // Shaders -> Buffers/VAOs/Samplers -> Textures -> FBOs
    rafId = requestAnimationFrame(renderLoop);
  });
  ```
  Never call `gl.delete*` on old handles after context loss; those handles already belong to the lost context.

### 4. Map WebGL 2.0 concepts cleanly for WebGPU migration

When `intent === "migration"`, structure abstractions around these five mappings:

| WebGL 2.0 Concept | WebGPU / WGSL Equivalent | Migration Rule |
|---|---|---|
| `VAO` + `vertexAttribPointer` | `GPUVertexBufferLayout` on `GPURenderPipeline` | Store declarative vertex layout descriptors in JS rather than scattered `gl.vertexAttribPointer` calls |
| `std140` UBO + texture units + `WebGLSampler` | `GPUBindGroupLayout` + `GPUBindGroup` | Group uniforms into 16-byte-aligned UBO structs (`FrameUniforms`, `PassUniforms`, `MaterialUniforms`) |
| `useProgram` + mutable blend/depth state | Immutable `GPURenderPipeline` | Key pipelines by `(shaderId, blendMode, depthCompare, cullMode, targetFormat)` |
| `WebGLFramebuffer` + `invalidateFramebuffer` | `GPURenderPassDescriptor` (`loadOp: "clear"`, `storeOp: "discard"`) | Express each pass with explicit `loadOp`/`storeOp` descriptors |
| GLSL ES 3.00 clip space (`Z in [-1, 1]`, bottom-left origin) | WGSL clip space (`Z in [0, 1]`, top-left framebuffer/texture UV origin) | Isolate projection matrix depth range and UV Y-flip in a single camera/postprocess helper |

## Failure modes

- Calling `gl.drawArrays` for a `gl_VertexID` fullscreen triangle without binding a VAO
- Allocating mutable `texImage2D` mip chains with mismatched sizes (black texture sampling)
- Forgetting `e.preventDefault()` on `webglcontextlost` or reusing pre-loss `WebGLProgram` handles
- Scattering loose `gl.uniform1f` calls instead of `std140` UBOs before a WebGPU migration

## Output contribution

Populate runtime `decisions`, resource/state `risks`, and `deliverables` (lifecycle checklist or WebGPU migration table).
