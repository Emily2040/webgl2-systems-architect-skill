# 01 - 意图分诊与范围定界 (zh-CN)

## 目的 (Purpose)

在进行任何着色器推导、FBO 拓扑设计或性能优化之前，将用户的 WebGL 2.0 需求精确归类为单一工程意图与项目形态，锁定最小模块集合。绝不跳过分诊直接编码。

## 适用时机 (When to load)

在所有任务中均作为首个模块加载（`architecture`、`implementation`、`debug`、`optimize`、`review`、`migration`）。

## 输入 (Inputs)

- 用户的原始需求描述、目标设备平台及帧率预期
- 已提供的代码、着色器、截图、性能日志或仅提示词（`prompt-only`）

## 核心规则 (Rules)

### 1. 确定主工程意图（6 选 1）

- **`architecture`**：从零设计多通道 WebGL 2.0 渲染器、SDF 步进管线、帧缓冲拓扑或混合管线。
- **`implementation`**：编写具体的 `#version 300 es` 着色器、VAO/UBO/Sampler 绑定、FBO 创建或主机端 JS/TS 渲染代码。
- **`debug`**：排查黑屏、`FRAMEBUFFER_INCOMPLETE_*`、非均匀流导数破面、NaN 传染、`webglcontextlost` 崩溃或同步回读卡顿。
- **`optimize`**：解决掉帧、移动端高 DPR 像素填充率过载、瓦片内存带宽瓶颈或 CPU/GPU 同步停顿。
- **`review`**：审计现有着色器或渲染器代码的数学稳定性、魔法数字、状态泄漏与验证覆盖率。
- **`migration`**：从 WebGL 1.0 升级至 WebGL 2.0，或设计 WebGL 2.0 与 WebGPU (`navigator.gpu` + WGSL) 双后端渐进迁移方案。

### 2. 确定项目形态（6 选 1）

```text
raster-mesh | sdf-raymarch | hybrid | postprocess | data-vis | ui
```

### 3. 盘点输入凭据并标注硬件数据质量

将 `inputs.hardware_data_quality` 显式标记为以下四级之一：
- **`measured`**：包含 `EXT_disjoint_timer_query_webgl2` 实测数据或受控开关差分帧时间。
- **`partial`**：包含 `gl.getParameter` 实机上限或部分 FPS 观测，但无分通道计时。
- **`estimated`**：仅知晓设备档位（如“中端安卓手机”、“移动端 Safari”），必须声明为启发式估算。
- **`unknown`**：未提供任何目标硬件信息。

### 4. 按 `registry/module-map.json` 锁定模块集合

输出 `modules` 数组必须与 `registry/module-map.json[intent]` 完全相等（不多加载无关模块，不遗漏必选模块）。

## 常见失效模式 (Failure modes)

- 在 `debug` 或 `implementation` 小任务中盲目加载全部 7 个模块，导致上下文被无关规则稀释
- 将启发式猜测的设备性能伪装成实测（`measured`）硬件数据
- 输出 JSON 中的 `modules` 列表与 `registry/module-map.json` 不一致

## 输出契约贡献 (Output contribution)

生成 `task`（或顶层 `intent`、`project_class`、`subject`、`locale`）、`inputs`、`modules` 与初始 `assumptions`。
