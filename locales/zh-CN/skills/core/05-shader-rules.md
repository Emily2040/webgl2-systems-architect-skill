# 05 - GLSL ES 3.00 与着色器数学规范 (zh-CN)

## Purpose

确保 WebGL 2.0 着色器跨平台可移植、自包含、数值稳定且无魔法常量。每个着色器必须以 `#version 300 es` 开头。

## When to load

在编写、审查、调试、优化或迁移 GLSL ES 3.00 顶点与片元着色器时加载。

## Inputs

- 着色器源码或目标着色算法
- 项目类别与目标 GPU 精度配置（移动端 `mediump` FP16 与桌面端 `highp` FP32）

## Rules

### 1. 严格执行 GLSL ES 3.00 (`#version 300 es`) 接口契约

- 首行首字节必须为 `#version 300 es`，并显式声明精度（`precision highp float; precision highp int;`）。
- 顶点输入使用 `layout(location = N) in`，阶段间传递使用 `in` / `out`，片元输出使用 `layout(location = 0) out vec4 outColor;`。严禁混用 WebGL 1.0 的 `attribute`、`varying`、`texture2D` 或 `gl_FragColor`。
- 跨通道共享的每帧参数放入 `layout(std140) uniform FrameBlock { ... };`，便于与 WebGPU `GPUBindGroup` 对齐。

### 2. 严禁自由变量与无推导注释的魔法字面量

每个辅助函数必须通过参数、UBO、`in` 变量或具名常量显式声明输入，所有数值常量必须注释物理或几何推导来源（如 `SURF_HIT_EPS = 0.0042`、`NORMAL_GRAD_EPS = 0.0084`、`SKIN_F0 = 0.0255`）。

### 3. 防护精度溢出、除零与非均匀控制流导数

- 世界坐标、相机位置、光线起点/方向、累计时间 `uTime` 与深度计算必须使用 `highp`。
- 防护分母与幂运算：`inversesqrt(max(dot(v, v), 1e-12))`、`sqrt(max(x, 0.0))`、`pow(max(base, 0.0), expVal)`。
- 在进入非均匀 `if`、`for` 或光线步进 `break` 循环**之前**计算 `vec2 dPdx = dFdx(uv); vec2 dPdy = dFdy(uv);`，分支内部使用 `textureGrad(uTex, uv, dPdx, dPdy)` 或 `textureLod`，避免 2x2 像素块导数未定义伪影。
- SDF 法线计算优先采用 4 次采样的四面体差分法（Tetrahedral normal）。

## Failure modes

- 在 `#version 300 es` 中残留 `varying` 或 `gl_FragColor` 导致编译失败
- 在动态分支或光线步进循环内部直接调用隐式 LOD 的 `texture(uTex, uv)` 或 `fwidth()`
- `std140` UBO 中混用未对齐的 `vec3` 数组导致跨平台字节偏移错位

## Output contribution

填充 `derivations`（常量推导、精度选择、循环上界）、着色器 `decisions` 与数值稳定性 `risks`。
