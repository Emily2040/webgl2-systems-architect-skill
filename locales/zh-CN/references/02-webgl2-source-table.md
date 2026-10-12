# 02 - WebGL 2.0 与 GLSL ES 3.00 权威规范索引表 (zh-CN)

本技能包中的所有硬性不变量（Invariants）均源自以下规范与硬件架构文档：

| 领域 | 权威规范 / 标准文档 | 核心工程约束与模块映射 |
| --- | --- | --- |
| **WebGL 2.0 渲染上下文与状态机** | Khronos WebGL 2.0 Specification (基于 OpenGL ES 3.0.4) | 单上下文命令串行提交、强制绑定 VAO (`createVertexArray`)、`texStorage2D` 不可变纹理分配、`invalidateFramebuffer` 瓦片内存释放、`MAX_CLIENT_WAIT_TIMEOUT_WEBGL == 0` (`03`, `06`) |
| **GLSL ES 3.00 着色器语言** | The OpenGL ES Shading Language 3.00 Specification | 首字节 `#version 300 es`、`in`/`out` 阶段接口、`layout(location = N)`、`layout(std140)` 16 字节对齐规则、非均匀控制流下隐式导数 (`texture`, `dFdx`, `dFdy`, `fwidth`) 未定义行为 (`05`) |
| **异步编译与 GPU 计时扩展** | Khronos WebGL Extension Registry (`KHR_parallel_shader_compile`, `EXT_disjoint_timer_query_webgl2`, `EXT_color_buffer_float`, `OES_texture_float_linear`, `WEBGL_lose_context`) | 跨帧轮询 `COMPLETION_STATUS_KHR`、检查 `GPU_DISJOINT_EXT === false` 的 3–4 帧计时环、浮点颜色附件完整性验证与上下文恢复演练 (`02`, `03`, `06`, `07`) |
| **SDF 光线步进与四面体法线数学** | Hart (1996) *Sphere Tracing: A Geometric Method for the Antialiased Ray Tracing of Implicit Surfaces* · 四面体有限差分法 | Lipschitz 界步长缩放 (`stepScale = 0.65..0.85`)、4 采样四面体梯度法线 (`k = (±1,±1,±1)`) 替代 6 采样中心差分 (`05`) |
| **WebGL 2.0 -> WebGPU 架构迁移** | W3C WebGPU & WGSL Specifications | `VAO -> GPUVertexBufferLayout`、`std140 UBO -> GPUBindGroup`、`WebGLFramebuffer -> GPURenderPassDescriptor`、裁剪空间深度 `Z in [-1, 1] -> [0, 1]` 与帧缓冲 UV 原点隔离 (`06`) |
