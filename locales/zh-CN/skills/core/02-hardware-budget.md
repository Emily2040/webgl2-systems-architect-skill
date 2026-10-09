# 02 - 硬件探测与帧预算推导 (zh-CN)

## Purpose

将架构设计与性能优化建立在真实的 WebGL 2.0 能力上限、显存带宽公式与实测帧耗时之上。先测量，再裁剪特性。

## When to load

在 `architecture` 与 `optimize` 任务中加载，或在涉及掉帧、DPR 缩放、带宽与发热降频时加载。

## Inputs

- 目标平台、视口尺寸与目标帧率（`30`、`60`、`90` 或 `120` FPS）
- 运行时 `gl.getParameter` 与 `gl.getExtension` 返回值
- 现有通道耗时或差分开关实测数据

## Rules

### 1. 直接查询 WebGL 2.0 硬件能力上限

使用 `gl.getParameter` 与 `gl.getExtension` 获取真实上限，而非仅凭 User-Agent 猜测：

- 纹理与体积上限：`MAX_TEXTURE_SIZE`, `MAX_CUBE_MAP_TEXTURE_SIZE`, `MAX_3D_TEXTURE_SIZE`, `MAX_ARRAY_TEXTURE_LAYERS`, `MAX_TEXTURE_IMAGE_UNITS`, `MAX_VERTEX_TEXTURE_IMAGE_UNITS`
- 多渲染目标 (MRT) 与 MSAA：`MAX_COLOR_ATTACHMENTS`, `MAX_DRAW_BUFFERS`, `MAX_SAMPLES`, `MAX_RENDERBUFFER_SIZE`
- Uniform 与 UBO 限制：`MAX_VERTEX_UNIFORM_VECTORS`, `MAX_FRAGMENT_UNIFORM_VECTORS`, `MAX_UNIFORM_BUFFER_BINDINGS`, `MAX_UNIFORM_BLOCK_SIZE`, `UNIFORM_BUFFER_OFFSET_ALIGNMENT`
- 变换反馈与顶点属性：`MAX_VERTEX_ATTRIBS`, `MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS`, `MAX_VARYING_VECTORS`
- 关键扩展：`EXT_disjoint_timer_query_webgl2`, `KHR_parallel_shader_compile`, `EXT_color_buffer_float`, `OES_texture_float_linear`, `WEBGL_lose_context`

### 2. 严格遵循证据优先级

1. **环形缓冲 GPU 计时查询 (`EXT_disjoint_timer_query_webgl2`)**：延迟 2-3 帧轮询 `QUERY_RESULT_AVAILABLE`，并在确认 `GPU_DISJOINT_EXT === false` 后读取 `QUERY_RESULT`。
2. **受控差分实测**：固定相机与场景，逐个切换渲染通道或调整 DPR 测量帧耗时差值。
3. **显式上下文上限查询 (`gl.getParameter`)**。
4. **设备分档估算**（最低优先级，必须标记为 `estimated` 或 `unknown`）。

### 3. 显式计算帧预算、填充率与带宽

```text
frameBudgetMs = 1000 / targetFPS
gpuBudgetMs   = frameBudgetMs - cpuMainThreadReserveMs - browserCompositorReserveMs
activePixels  = (cssWidth * targetDPR) * (cssHeight * targetDPR)
bandwidthBps  = activePixels * bytesPerPixelReadWriteAcrossPasses * targetFPS
targetDPR     = min(devicePixelRatio, maxDPRCap, sqrt(gpuBudgetMs / (cssWidth * cssHeight * 1e-6 * msPerMegapixel)))
```

### 4. 定义三档硬件降级策略 (`low` / `mid` / `high`)

明确说明每一档变化的内部渲染比例、`targetDPR` 上限、FBO 格式（`RGBA8` vs 需 `EXT_color_buffer_float` 的 `RGBA16F`）、MSAA 采样数以及步进/滤波采样次数。

## Failure modes

- 将纸面 GPU TFLOPS 当作浏览器实测性能
- 在同一帧同步读取计时查询或忽略 `GPU_DISJOINT_EXT`
- `bindBufferRange` 偏移量未按 `UNIFORM_BUFFER_OFFSET_ALIGNMENT` 对齐

## Output contribution

填充 `inputs.hardware_data_quality`、`derivations`（帧预算、DPR 钳制、带宽）、分档 `decisions` 与硬件 `risks`。
