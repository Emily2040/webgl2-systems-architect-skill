# 07 - 验证阶梯、性能剖析与 CI 门禁 (zh-CN)

## Purpose

验证 WebGL 2.0 渲染器或技能包能够正常编译、输出预期像素、从上下文丢失中恢复，并在违反不变量时立即报错。绝不以“仅编译通过”作为交付标准。

## When to load

在 `architecture`、`debug`、`optimize`、`review` 与 `migration` 任务中加载。

## Inputs

- 待验证的着色器、JS/TS 运行时代码或结构化架构方案
- 测试环境（本地浏览器、无头 Chrome/Playwright 或 CI 运行器）

## Rules

### 1. 执行五级 WebGL 2.0 验证阶梯

1. **着色器编译与程序链接门禁**：检查 `#version 300 es` 位于首字节，验证 `COMPILE_STATUS` 与 `LINK_STATUS`。
2. **帧缓冲完整性与状态门禁**：对每个自定义 FBO 检查 `gl.checkFramebufferStatus(gl.FRAMEBUFFER) === gl.FRAMEBUFFER_COMPLETE`，重点排查未开启 `EXT_color_buffer_float` 导致的 `FRAMEBUFFER_INCOMPLETE_ATTACHMENT` 以及多重采样数不一致导致的 `FRAMEBUFFER_INCOMPLETE_MULTISAMPLE`。
3. **像素与 PBO + Fence 冒烟回读门禁**：渲染确定性画面并验证中心像素 RGBA 值（参见 `fixtures/webgl2-smoke/index.html`），同时验证 `gl.PIXEL_PACK_BUFFER` + `gl.fenceSync` 非阻塞回读。
4. **上下文丢失恢复演练**：调用 `WEBGL_lose_context.loseContext()` 与 `restoreContext()`，确认画面与状态完整恢复且 `gl.getError() === gl.NO_ERROR`。
5. **差分性能与视觉回归门禁**：固定 OS/浏览器/DPR 基线对比截图，并逐通道切换测量耗时差值。

### 2. 调试着色器诊断视图

排查渲染异常时提供单开关诊断模式：法线可视化 (`N * 0.5 + 0.5`)、光线步进次数热力图、UV 导数突变检测 (`fwidth(uv)`) 以及 `isnan`/`isinf` 亮洋红 (`vec4(1.0, 0.0, 1.0, 1.0)`) 探针。

### 3. 仓库自检与负向自测门禁

运行 `python scripts/validate_repo.py` 验证 JSON Schema、模块集合相等性、SVG XML 良构性与文本框边界、四语言（`en`, `zh-CN`, `ja`, `ko`）对等性、`registry/forbidden-slop.json` 禁用词扫描以及负向自测用例。

## Failure modes

- 未调用 `gl.checkFramebufferStatus` 就上线多通道 FBO 管线
- 在生产渲染主循环内每帧调用 `gl.getError()` 导致 CPU/GPU 同步停顿

## Output contribution

填充 `deliverables`（验证矩阵）、`risks`、`validation_gates` 与最终置信度评估。
