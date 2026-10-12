# 06 - 状态隔离、资源生命周期、上下文恢复与 WebGPU 迁移 (zh-CN)

## 目的 (Purpose)

防止 WebGL 2.0 状态串扰、VRAM 显存泄漏、移动端瓦片 GPU 带宽浪费以及上下文丢失后无法恢复，同时保持面向 WebGPU 平滑迁移的资源抽象。追踪每一个 GPU 句柄。

## 适用时机 (When to load)

在所有工程意图（`architecture`、`implementation`、`debug`、`optimize`、`review`、`migration`）中均需加载。

## 输入 (Inputs)

- 主机端 JS/TS 渲染循环代码、通道配置、视口缩放逻辑与事件监听器
- 纹理、缓冲、VAO、Sampler、FBO 与着色器程序的创建及销毁路径

## 核心规则 (Rules)

### 1. 隔离通道状态并使用 WebGL 2.0 原生对象

- **顶点数组对象 (VAO)**：初始化时使用 `gl.createVertexArray()` 绑定顶点属性布局，渲染循环中仅调用 `gl.bindVertexArray(vao)`。即使是基于 `gl_VertexID` 的无缓冲全屏三角形，WebGL 2.0 也强制要求绑定非空 VAO。
- **Uniform 缓冲对象 (UBO)**：使用 `gl.uniformBlockBinding` 与 `gl.bindBufferBase(gl.UNIFORM_BUFFER, binding, ubo)` 共享 `std140` 数据块；调用 `bindBufferRange` 时偏移量必须为 `UNIFORM_BUFFER_OFFSET_ALIGNMENT` 的整数倍。
- **采样器对象 (Sampler)**：使用 `gl.createSampler()` 与 `gl.bindSampler(unit, sampler)` 将过滤与寻址状态同纹理存储解耦。

### 2. 不可变纹理存储与移动端瓦片帧缓冲失效声明

- 使用 `gl.texStorage2D` / `gl.texStorage3D` + `gl.texSubImage2D` 替代可变 `texImage2D`，消除绘制时的 Mipmap 完整性校验开销。
- 在移动端瓦片（Tile-based）GPU 上，当多通道渲染结束且不再需要瞬态深度/模板附件时，立即调用 `gl.invalidateFramebuffer(gl.FRAMEBUFFER, [gl.DEPTH_ATTACHMENT, gl.STENCIL_ATTACHMENT])`，避免将瓦片内存写回系统 DRAM。

### 3. 显式销毁资源与上下文丢失恢复 (`webglcontextlost` / `webglcontextrestored`)

- `gl.linkProgram(prog)` 成功后立即调用 `gl.detachShader` 与 `gl.deleteShader`。
- 注册上下文恢复状态机，严禁对已丢失的旧句柄调用 `delete*`：

```js
canvas.addEventListener('webglcontextlost', (e) => {
  e.preventDefault();
  cancelAnimationFrame(rafId);
}, false);

canvas.addEventListener('webglcontextrestored', () => {
  initCapabilitiesAndExtensions(gl);
  rebuildShadersVAOsUBOsSamplersTexturesAndFBOs(gl);
  rafId = requestAnimationFrame(renderFrame);
}, false);
```

### 4. WebGL 2.0 到 WebGPU (WGSL) 1:1 架构映射表

| WebGL 2.0 概念 | WebGPU 对等概念 | 迁移工程准则 |
| --- | --- | --- |
| `WebGLVertexArrayObject` (VAO) | `GPUVertexBufferLayout` | 在初始化描述表中静态声明顶点步幅与属性偏移 |
| `std140` UBO + 纹理单元 + `WebGLSampler` | `GPUBindGroupLayout` + `GPUBindGroup` | 按更新频率分组（`group(0)` 帧级、`group(1)` 通道级、`group(2)` 材质级） |
| `useProgram` + 可变混合/深度状态 | 不可变 `GPURenderPipeline` | 以着色器、混合、深度与附件格式为键预构建管线对象 |
| `WebGLFramebuffer` + `invalidateFramebuffer` | `GPURenderPassDescriptor` (`loadOp`/`storeOp`) | 瞬态深度附件直接声明 `storeOp: 'discard'` |
| 裁剪空间 `Z in [-1, 1]`、左下 UV 原点 | 裁剪空间 `Z in [0, 1]`、左上帧缓冲原点 | 在单一投影/全屏 UV 辅助函数中隔离深度重映射与 Y 轴翻转 |

## 常见失效模式 (Failure modes)

- 未绑定 VAO 直接调用 `gl.drawArrays` 触发 `INVALID_OPERATION`
- 在 `webglcontextlost` 中遗漏 `e.preventDefault()`，或在恢复后复用旧纹理/FBO 句柄

## 输出契约贡献 (Output contribution)

填充运行时 `decisions`、状态/生命周期 `risks` 与 `deliverables`（资源生命周期表或 WebGPU 迁移映射表）。
