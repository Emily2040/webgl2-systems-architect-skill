# 03 - 管线拓扑与并发设计 (zh-CN)

## 目的 (Purpose)

依据 WebGL 2.0 在 CPU 线程与单 GPU 队列上的真实执行模型，设计渲染通道图（Pass Graph）、首帧启动流程与异步管线。单上下文的 GL 绘制调用永远是串行提交的。

## 适用时机 (When to load)

在涉及通道拓扑、FBO 链路、Web Worker、着色器编译或像素回读的 `architecture`、`implementation`、`optimize`、`migration` 任务中加载。

## 输入 (Inputs)

- 项目形态（`raster-mesh`、`sdf-raymarch`、`hybrid`、`postprocess`、`data-vis`、`ui`）
- 渲染通道列表、资产规模与首帧可交互延迟预算
- `OffscreenCanvas`、Web Worker 与 `KHR_parallel_shader_compile` 可用性

## 核心规则 (Rules)

### 1. 按工程需求而非惯性配置上下文属性

不透明画布必须设置 `alpha: false` 以避免浏览器合成器产生透明混合开销。自定义 FBO 或全屏 SDF 管线应设置 `antialias: false`，需要多重采样时显式使用 `renderbufferStorageMultisample` + `blitFramebuffer`。

### 2. 严格区分真并行、跨帧管线化与单上下文串行提交

- **可在 CPU / Web Worker 中真并行执行**：网络 `fetch`、glTF/Draco 解压、KTX2/Basis 转码、BVH 构建、视锥裁剪、地形网格生成、`createImageBitmap` 解码。
- **可跨帧非阻塞管线化（GPU/CPU 重叠）**：
  - `KHR_parallel_shader_compile`：跨帧轮询 `ext.COMPLETION_STATUS_KHR`，仅在返回 `true` 后查询 `gl.LINK_STATUS`：

```js
function pollProgramLink(gl, ext, prog) {
  if (ext && !gl.getProgramParameter(prog, ext.COMPLETION_STATUS_KHR)) return null;
  return gl.getProgramParameter(prog, gl.LINK_STATUS);
}
```

  - `gl.PIXEL_PACK_BUFFER` (PBO) + `gl.fenceSync`：在第 $N$ 帧触发异步 `readPixels` 并插入栅栏，在后续帧轮询 `clientWaitSync(fence, 0, 0)`，仅当信号就绪后才调用 `getBufferSubData`：

```js
// 第 N 帧：启动非阻塞 PBO 传输并创建 GPU 栅栏
gl.bindBuffer(gl.PIXEL_PACK_BUFFER, pbo);
gl.readPixels(x, y, w, h, gl.RGBA, gl.UNSIGNED_BYTE, 0);
gl.bindBuffer(gl.PIXEL_PACK_BUFFER, null);
const fence = gl.fenceSync(gl.SYNC_GPU_COMMANDS_COMPLETE, 0);
gl.flush();
// 第 N+k 帧：非阻塞轮询 (timeout = 0)，严禁同帧强制 getBufferSubData
const status = gl.clientWaitSync(fence, 0, 0);
if (status === gl.ALREADY_SIGNALED || status === gl.CONDITION_SATISFIED) {
  gl.bindBuffer(gl.PIXEL_PACK_BUFFER, pbo);
  gl.getBufferSubData(gl.PIXEL_PACK_BUFFER, 0, dstPixels);
  gl.bindBuffer(gl.PIXEL_PACK_BUFFER, null);
  gl.deleteSync(fence);
}
```

- **单 `WebGL2RenderingContext` 上严格串行**：状态切换、缓冲/纹理上传、绘制调用。

### 3. 首帧启动分级与状态排序

第 1 帧仅使用轻量引导着色器与 1×1 `texStorage2D` 占位纹理立即出图；高分辨率纹理与重型辅助着色器在后续帧异步流式就绪。通道内绘制按 **FBO -> Program -> UBO/纹理 -> VAO -> Draw Call** 顺序排序。

## 常见失效模式 (Failure modes)

- 用 `async`/`await` 包装串行 `gl.*` 调用并谎称实现了 GPU 并行渲染
- 在 `COMPLETION_STATUS_KHR` 为 `false` 时查询 `LINK_STATUS` 导致主线程卡死
- 在调用 `readPixels` 的同一帧内无视 `TIMEOUT_EXPIRED` 直接调用 `getBufferSubData`，触发同步管线停顿

## 输出契约贡献 (Output contribution)

填充 `decisions`（上下文属性、通道拓扑、启动序列）、`parallel_plan`（或 `parallel_tasks`）与并发 `risks`。
