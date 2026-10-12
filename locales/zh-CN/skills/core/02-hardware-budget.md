# 02 - 硬件能力探测与帧预算模型 (zh-CN)

## 目的 (Purpose)

将架构设计与性能优化建立在真实的 WebGL 2.0 硬件上限、显存带宽公式与实测帧时间之上。先测量，再裁剪视觉特性。

## 适用时机 (When to load)

在 `architecture` 与 `optimize` 任务中加载，或当问题涉及帧率下降、DPR 缩放、显存带宽与移动端热降频时加载。

## 输入 (Inputs)

- 目标平台、CSS 视口尺寸与目标帧率（`30`、`60`、`90`、`120`）
- 运行时 `gl.getParameter` 与 `gl.getExtension` 查询结果
- 现有的通道计时日志或受控开关差分测量数据

## 核心规则 (Rules)

### 1. 查询真实的 WebGL 2.0 硬件上限

严禁依赖 User-Agent 字符串猜测 GPU 能力，必须在初始化时通过 `gl.getParameter` 与 `gl.getExtension` 探测：

- **纹理上限**：`MAX_TEXTURE_SIZE`、`MAX_CUBE_MAP_TEXTURE_SIZE`、`MAX_3D_TEXTURE_SIZE`、`MAX_ARRAY_TEXTURE_LAYERS`、`MAX_TEXTURE_IMAGE_UNITS`、`MAX_VERTEX_TEXTURE_IMAGE_UNITS`
- **多渲染目标与多重采样**：`MAX_COLOR_ATTACHMENTS`、`MAX_DRAW_BUFFERS`、`MAX_SAMPLES`、`MAX_RENDERBUFFER_SIZE`
- **Uniform 与 UBO 上限**：`MAX_VERTEX_UNIFORM_VECTORS`、`MAX_FRAGMENT_UNIFORM_VECTORS`、`MAX_UNIFORM_BUFFER_BINDINGS`、`MAX_UNIFORM_BLOCK_SIZE`、`UNIFORM_BUFFER_OFFSET_ALIGNMENT`
- **关键扩展**：`EXT_disjoint_timer_query_webgl2`、`KHR_parallel_shader_compile`、`EXT_color_buffer_float`、`OES_texture_float_linear`、`WEBGL_lose_context`

### 2. 严格遵守性能证据优先级

1. **环形缓冲 GPU 计时查询 (`EXT_disjoint_timer_query_webgl2`)**：延迟 3–4 帧轮询 `QUERY_RESULT_AVAILABLE`，仅在 `gl.getParameter(ext.GPU_DISJOINT_EXT) === false` 时采纳 `QUERY_RESULT`。
2. **受控差分开关测量**：固定相机与场景，逐一开关单个渲染通道或切换 DPR，记录帧时间差值。
3. **`gl.getParameter` 实机上限查询**。
4. **设备档位启发式估算**（最低优先级；必须标记为 `estimated` 或 `unknown`）。

### 3. 显式推导帧预算、像素填充率与带宽公式

```text
frameBudgetMs = 1000 / targetFPS
gpuBudgetMs   = frameBudgetMs - cpuMainThreadReserveMs - browserCompositorReserveMs
activePixels  = (cssWidth * targetDPR) * (cssHeight * targetDPR)
bandwidthBps  = activePixels * bytesPerPixelReadWriteAcrossPasses * targetFPS
targetDPR     = min(devicePixelRatio, maxDPRCap, sqrt(gpuBudgetMs / (cssWidth * cssHeight * 1e-6 * msPerMegapixel)))
```

### 4. 定义三档自适应质量策略 (`low` / `mid` / `high`)

为每档明确指定内部渲染分辨率比例、`targetDPR` 上限、FBO 附件格式（`RGBA8` vs 需 `EXT_color_buffer_float` 的 `RGBA16F`）、MSAA 采样数以及光线步进/滤波采样次数。

## 常见失效模式 (Failure modes)

- 将纸面 GPU TFLOPS 算力当作浏览器内的实际可持续帧率
- 在同一帧内同步读取计时查询，或忽略 `GPU_DISJOINT_EXT` 标志
- `bindBufferRange` 偏移量未按 `UNIFORM_BUFFER_OFFSET_ALIGNMENT` 对齐

## 输出契约贡献 (Output contribution)

填充 `inputs.hardware_data_quality`、`derivations`（帧预算、DPR 钳制、带宽）、分档 `decisions` 及硬件 `risks`。
