# 01 - 重构设计原理与架构取舍 (zh-CN)

## 1. 为什么将单体提示词拆分为模块化技能包

早期的 WebGL 2.0 提示词往往将人像解剖比例、光线步进（Raymarching）步长、FBO 帧缓冲状态、移动端带宽估算和 CI 测试混杂在同一个长篇文档中。这种单体结构会导致三个工程问题：

1. **上下文稀释（Context Dilution）**：当开发者只想排查 `webglcontextlost` 黑屏或 `EXT_color_buffer_float` 缺失时，模型却被迫加载大段面部解剖学或地形噪声规则。
2. **伪精确与魔法数字（Pseudo-Precision）**：缺乏统一推导契约时，着色器中容易出现未注明几何/物理来源的硬编码常量（如随意的 `0.003` 或 `1.42`）。
3. **验证缺失（Unverified Claims）**：仅凭“代码能编译”或空洞宣传形容词就宣告完成，缺少 FBO 完整性检查、非阻塞 PBO 像素回读与上下文丢失恢复演练。

## 2. 核心工程改进

- **按意图最小化路由（`registry/module-map.json`）**：通过 `01-triage.md` 将任务划分为 6 类工程意图（`architecture`、`implementation`、`debug`、`optimize`、`review`、`migration`）与 6 类项目形态，仅按需加载对应模块。
- **区分硬件实测与启发式估算（`02-hardware-budget.md`）**：要求优先使用 `EXT_disjoint_timer_query_webgl2` 环形缓冲与 `gl.getParameter` 实机上限，严禁将纸面 TFLOPS 当作浏览器实测帧率。
- **单上下文串行提交与真异步分离（`03-pipeline-and-concurrency.md`）**：明确区分 Web Worker CPU 并行、跨帧管线化（`KHR_parallel_shader_compile` 轮询、多帧 `PIXEL_PACK_BUFFER` + `gl.fenceSync` 非阻塞回读）与单 `WebGL2RenderingContext` 串行命令队列。
- **可观测视觉层级与降级裁剪序（`04-subject-audit.md`）**：将视觉目标拆解为 5 个可观测层与 P0/P1/P2 优先级，当帧时间超出 `gpuBudgetMs` 时严格按 P2 -> 半分辨率辅助通道 -> DPR 钳制 -> P1 采样数的顺序裁剪，绝不牺牲 P0 轮廓。
- **GLSL ES 3.00 数值与微分纪律（`05-shader-rules.md`）**：强制 `#version 300 es`、`std140` 16 字节对齐 UBO、Lipschitz 有界 SDF 步进、4 采样四面体法线，以及在非均匀分支前预计算 `dFdx`/`dFdy` 并调用 `textureGrad`。
- **双模式 JSON 输出契约与反套话门禁（`schemas/` + `registry/forbidden-slop.json`）**：提供 `authoring-base.json` 与 `runtime-compact.json` 两种严格 Schema，并通过 `scripts/validate_repo.py` 自动拦截中、英、日、韩四语种空洞营销套话。
