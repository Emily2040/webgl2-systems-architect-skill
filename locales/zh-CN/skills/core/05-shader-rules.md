# 05 - GLSL ES 3.00 与着色器数学纪律 (zh-CN)

## 目的 (Purpose)

确保 WebGL 2.0 着色器具备跨平台可移植性、自包含性与数值稳定性，彻底消除未推导的魔法数字。所有着色器必须以 `#version 300 es` 开头。

## 适用时机 (When to load)

在编写、审计、调试、优化 GLSL ES 3.00 顶点/片元着色器，或将其迁移至 WGSL 时加载。

## 输入 (Inputs)

- 着色器源码或目标着色/光线步进算法
- 项目形态与目标 GPU 精度特征（移动端 `mediump` FP16 vs 桌面端 `highp` FP32）

## 核心规则 (Rules)

### 1. 严守 GLSL ES 3.00 (`#version 300 es`) 阶段契约

- 文件第 0 字节必须为 `#version 300 es`，并显式声明精度（`precision highp float; precision highp int;`）。
- 顶点输入使用 `layout(location = N) in`，阶段间传递使用 `in` / `out`，片元输出使用 `layout(location = 0) out vec4 outColor;`。严禁混用 WebGL 1.0 的 `attribute`、`varying`、`texture2D` 或 `gl_FragColor`。
- 跨通道共享的帧级 Uniform 必须打包进 `layout(std140) uniform FrameBlock { ... };`，以 16 字节对齐（使用 `vec4`/`mat4` 避免 `vec3` 填充陷阱），实现与 WebGPU `GPUBindGroup` 的 1:1 映射。

### 2. 严禁自由变量与无推导的魔法常量

每个辅助函数只能通过参数、UBO、`in` 变量或具名常量获取输入；每个数值常量必须附带几何或物理推导注释（如 `SURF_HIT_EPS = 0.0042`、`NORMAL_GRAD_EPS = 0.0084`、`SKIN_F0 = 0.0255`）。

### 3. 保护数值精度、Lipschitz 步长界与非均匀流下的导数

- 世界坐标、相机位置、光线原点/方向、累计时间 `uTime` 与深度计算必须使用 `highp`。
- 对除法、平方根与幂运算加安全下界：`inversesqrt(max(dot(v, v), 1e-12))`、`sqrt(max(x, 0.0))`、`pow(max(base, 0.0), expVal)`。
- 非精确 SDF（包含扭曲、非均匀缩放或位移混合）必须乘以 Lipschitz 安全步长系数 `stepScale = 0.65..0.85`。
- 在进入非均匀 `if`、`for` 或光线步进 `break` 循环**之前**预计算屏幕空间导数 `vec2 dPdx = dFdx(uv); vec2 dPdy = dFdy(uv);`，并在分支内显式调用 `textureGrad(uTex, uv, dPdx, dPdy)` 或 `textureLod`。
- SDF 表面法线计算采用 4 采样四面体差分法（比 6 采样中心差分节省 33% SDF 求值）：

```glsl
vec3 calcNormal(highp vec3 p) {
  const float h = 0.0084; // NORMAL_GRAD_EPS = 2.0 * SURF_HIT_EPS
  const vec2 k = vec2(1.0, -1.0);
  return normalize(
    k.xyy * mapScene(p + k.xyy * h) +
    k.yyx * mapScene(p + k.yyx * h) +
    k.yxy * mapScene(p + k.yxy * h) +
    k.xxx * mapScene(p + k.xxx * h)
  );
}
```

## 常见失效模式 (Failure modes)

- 在 `#version 300 es` 着色器中混用 `varying` 或 `gl_FragColor` 导致编译失败
- 在动态光线步进循环或非均匀分支内直接调用隐式 LOD `texture(uTex, uv)` 或 `fwidth()`，产生 2×2 像素块接缝破面
- 在 `std140` UBO 中裸放 `vec3` 数组而未按 16 字节步幅对齐

## 输出契约贡献 (Output contribution)

填充 `derivations`（常量推导、精度选择、Lipschitz 步长与循环上限）、着色器 `decisions` 与数值 `risks`。
