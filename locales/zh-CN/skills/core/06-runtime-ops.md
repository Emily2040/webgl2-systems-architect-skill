# 06 - 状态隔离、资源生命周期、上下文恢复与 WebGPU 迁移 (zh-CN)

## Purpose

防止 WebGL 2.0 状态串扰、显存泄漏、移动端瓦片带宽浪费以及上下文丢失后无法恢复，同时保持资源抽象可直接映射至 WebGPU。显式追踪每个 GPU 句柄。

## When to load

在所有意图（`architecture`, `implementation`, `debug`, `optimize`, `review`, `migration`）中加载。

## Inputs

- 宿主 JS/TS 渲染器代码、通道配置、尺寸缩放逻辑与事件监听器
- 纹理、缓冲区、VAO、Sampler、FBO 与着色器程序的创建与销毁路径

## Rules

### 1. 隔离通道状态并使用 WebGL 2.0 原生对象

- **顶点数组对象 (VAO)**：初始化时创建 `gl.createVertexArray()` 并录制顶点属性绑定；绘制循环中仅调用 `gl.bindVertexArray(vao)`。即使是基于 `gl_VertexID` 的全屏三角形通道也必须绑定 VAO。
- **统一缓冲对象 (UBO)**：通过 `gl.uniformBlockBinding` 与 `gl.bindBufferBase(gl.UNIFORM_BUFFER, binding, ubo)` 绑定 `std140` 块；使用 `bindBufferRange` 时偏移量必须对齐 `UNIFORM_BUFFER_OFFSET_ALIGNMENT`。
- **采样器对象 (Sampler)**：使用 `gl.createSampler()` 与 `gl.bindSampler(unit, sampler)` 将滤波与寻址模式同纹理存储解耦。

### 2. 不可变纹理存储与移动端瓦片附件失效声明

- 优先使用 `gl.texStorage2D` / `gl.texStorage3D` 分配不可变纹理存储，配合 `gl.texSubImage2D` 更新数据。
- 在移动端分块渲染 (Tile-based) GPU 上，完成通道后对无需保留的深度/模板附件调用 `gl.invalidateFramebuffer(gl.FRAMEBUFFER, [gl.DEPTH_ATTACHMENT, gl.STENCIL_ATTACHMENT])`，避免将瓦片缓冲写回系统内存。

### 3. 显式销毁与上下文丢失恢复 (`webglcontextlost` / `webglcontextrestored`)

- 链接成功后立即 `detachShader` 并 `deleteShader`。
- 监听 `webglcontextlost` 调用 `event.preventDefault()` 并取消 `requestAnimationFrame`；在 `webglcontextrestored` 中按依赖顺序重建着色器、VAO、UBO、纹理与 FBO，切勿对已丢失上下文的旧句柄调用 `delete*`。

### 4. WebGL 2.0 到 WebGPU 迁移映射

- `VAO` -> `GPUVertexBufferLayout`
- `std140` UBO + 纹理单元 + `WebGLSampler` -> `GPUBindGroupLayout` + `GPUBindGroup`
- `useProgram` + 可变混合/深度状态 -> 不可变 `GPURenderPipeline`
- `WebGLFramebuffer` + `invalidateFramebuffer` -> `GPURenderPassDescriptor` (`loadOp` / `storeOp`)
- 裁剪空间深度 `Z in [-1, 1]` 与左下角 UV 原点 -> WebGPU `Z in [0, 1]` 与左上角帧缓冲原点

## Failure modes

- 全屏三角形绘制未绑定 VAO 触发 `INVALID_OPERATION`
- `webglcontextlost` 未调用 `event.preventDefault()` 或恢复后复用失效句柄

## Output contribution

填充运行时 `decisions`、状态/资源 `risks` 与 `deliverables`（生命周期核对表或 WebGPU 迁移对照表）。
