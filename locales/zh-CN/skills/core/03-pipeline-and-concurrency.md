# 03 - 渲染管线拓扑与并发编排 (zh-CN)

## Purpose

设计符合 WebGL 2.0 真实执行模型的渲染通道图、首帧启动流与异步管线。单上下文的 GL 绘制命令在驱动层始终串行。

## When to load

在 `architecture`、`implementation`、`optimize` 与 `migration` 任务中加载。

## Inputs

- 项目类别（`raster-mesh`, `sdf-raymarch`, `hybrid`, `postprocess`, `data-vis`, `ui`）
- 渲染通道链、资源体量与首帧启动延迟预算
- 浏览器对 `OffscreenCanvas`、Web Worker 与 `KHR_parallel_shader_compile` 的支持情况

## Rules

### 1. 按实际需求配置上下文属性

显式声明 `canvas.getContext("webgl2", attrs)` 参数：不透明画布设 `alpha: false` 以避免浏览器合成器额外混合；仅在默认帧缓冲需要深度/模板时开启 `depth`/`stencil`；后处理或 SDF 管线设 `antialias: false`，离屏 MSAA 使用 `renderbufferStorageMultisample` + `blitFramebuffer`。

### 2. 区分真正并行的 CPU 工作与单上下文串行 GL 提交

- **CPU / Web Worker 并行**：网络拉取、glTF/Draco 解压、KTX2/Basis 转码、BVH 构建、视锥剔除、地形网格生成与 `createImageBitmap` 解码。
- **跨帧流水线化（非阻塞 GPU/CPU 重叠）**：
  - 使用 `KHR_parallel_shader_compile` 轮询 `ext.COMPLETION_STATUS_KHR`，就绪后再查询 `gl.LINK_STATUS`。
  - 使用 `gl.PIXEL_PACK_BUFFER` (PBO) + `gl.fenceSync(gl.SYNC_GPU_COMMANDS_COMPLETE, 0)` + `gl.clientWaitSync` + `gl.getBufferSubData` 实现非阻塞像素回读。
- **单上下文严格串行**：`bindFramebuffer`、`useProgram`、`bindVertexArray`、`texSubImage2D` 与 `drawArrays` / `drawElementsInstanced`。

### 3. 分阶段首帧启动与状态排序

首帧仅编译主通道着色器并绑定 1x1 占位纹理（`texStorage2D`）立即渲染 Frame 1；后续帧通过 Worker 流式上传资源并轮询辅助着色器。光栅化通道内部按 **FBO -> Program -> UBO/纹理 -> VAO -> Draw Call** 排序，严禁同时采样当前 FBO 正在写入的附件。

## Failure modes

- 用 `async`/`await` 包装顺序 GL 调用并声称实现了 GPU 并行
- 在 `COMPLETION_STATUS_KHR` 仍为 `false` 时查询 `LINK_STATUS` 阻塞主线程
- 每帧直接向 CPU 数组调用同步 `gl.readPixels`

## Output contribution

填充 `decisions`（上下文属性、通道图、启动流）、`parallel_plan` 与并发 `risks`。
