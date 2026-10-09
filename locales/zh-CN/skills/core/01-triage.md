# 01 - 任务分流与分类 (zh-CN)

## Purpose

对 WebGL 2.0 请求进行精确分流，确保代理仅加载当前任务所需的模块。所有任务均从本模块开始。

## When to load

在每个请求开始时最先加载。

## Inputs

- 用户提示词与目标语言（`en`、`zh-CN`、`ja`、`ko`）
- 现有的着色器、JS/TS 渲染代码、通道图或仓库文件（如有）
- 截图、录屏、GPU 性能分析捕获或运行时错误日志（如有）
- 目标设备、浏览器与目标帧率约束（如已知）

## Rules

### 1. 按四个维度分类请求

1. **意图 (`intent`)**
   - `architecture`：系统总体架构、渲染通道图、硬件分档策略、启动编排
   - `implementation`：编写新 `#version 300 es` 着色器、FBO 通道、VAO/UBO 管线或运行时功能
   - `debug`：渲染错误、`NaN`/精度伪影、FBO 不完整、状态泄漏或上下文丢失故障
   - `optimize`：掉帧、填充率瓶颈、显存带宽压力、着色器停顿或同步回读阻塞
   - `review`：代码审查、视觉可信度评估、跨平台移植性检查或上线就绪评估
   - `migration`：WebGL 1 升级 WebGL 2.0 或 WebGL 2.0 迁移至 WebGPU/WGSL

2. **项目类别 (`project_class`)**
   - `raster-mesh`、`sdf-raymarch`、`hybrid`、`postprocess`、`data-vis`、`ui`

3. **主体 (`subject`)**
   - 明确命名具体渲染对象，例如 `human face bust`、`terrain flyover`、`HDR bloom chain` 或 `WebGPU bind-group migration`。

4. **证据质量 (`hardware_data_quality`)**
   - `measured`（已有计时查询或捕获）、`estimated`（已知设备档位但通道成本为推算）、`unknown`（纯提示词输入，需显式声明假设）。

### 2. 提出修改前先检查已有工件

- 若提供了代码或着色器，先检查 `#version 300 es` 声明、VAO/UBO 绑定、FBO 完整性与绘制循环。
- 若提供了截图或性能日志，先判定问题是几何、着色精度、合成还是带宽瓶颈。

### 3. 按意图选择模块（严格对应 `registry/module-map.json`）

- `architecture`：`skills/core/01-triage.md`, `skills/core/02-hardware-budget.md`, `skills/core/03-pipeline-and-concurrency.md`, `skills/core/04-subject-audit.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`, `skills/core/07-validation-and-ci.md`
- `implementation`：`skills/core/01-triage.md`, `skills/core/03-pipeline-and-concurrency.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`
- `debug`：`skills/core/01-triage.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`, `skills/core/07-validation-and-ci.md`
- `optimize`：`skills/core/01-triage.md`, `skills/core/02-hardware-budget.md`, `skills/core/03-pipeline-and-concurrency.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`, `skills/core/07-validation-and-ci.md`
- `review`：`skills/core/01-triage.md`, `skills/core/04-subject-audit.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`, `skills/core/07-validation-and-ci.md`
- `migration`：`skills/core/01-triage.md`, `skills/core/03-pipeline-and-concurrency.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`, `skills/core/07-validation-and-ci.md`

## Failure modes

- 为单行着色器修复加载全部模块
- 将 SDF 光线步进规则强加给常规光栅化网格管线
- 未区分填充率、带宽、顶点或 CPU 同步瓶颈就盲目裁剪视觉特性

## Output contribution

填充 `task.intent`、`task.project_class`、`task.subject`、`inputs.hardware_data_quality`、`modules` 与初始 `assumptions`。
