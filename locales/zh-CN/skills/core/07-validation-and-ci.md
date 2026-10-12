# 07 - 验证阶梯、性能剖析与 CI 门禁 (zh-CN)

## 目的 (Purpose)

验证 WebGL 2.0 渲染器及技能包不仅能通过编译，还能输出正确像素、通过 FBO 完整性检查、从上下文丢失中无错恢复，并在违反不变量时立即报错拦截。绝不把“编译通过”当作交付完成。

## 适用时机 (When to load)

在 `architecture`、`debug`、`optimize`、`review`、`migration` 任务中加载。

## 输入 (Inputs)

- 待验证的着色器、主机端 JS/TS 渲染代码或架构方案
- 测试运行环境（本地浏览器、无头 Chromium/Playwright 或 CI 流水线）

## 核心规则 (Rules)

### 1. 执行 WebGL 2.0 五级验证阶梯（5-Rung Verification Ladder）

1. **着色器编译与链接门禁**：断言文件首字节为 `#version 300 es`，且 `COMPILE_STATUS` 与 `LINK_STATUS` 均为 `true`（`getShaderInfoLog` / `getProgramInfoLog` 为空）。
2. **帧缓冲完整性与状态门禁**：对所有自定义 FBO 断言 `gl.checkFramebufferStatus(gl.FRAMEBUFFER) === gl.FRAMEBUFFER_COMPLETE`，拦截缺失 `EXT_color_buffer_float` 导致的 `FRAMEBUFFER_INCOMPLETE_ATTACHMENT` 或采样数不一致导致的 `FRAMEBUFFER_INCOMPLETE_MULTISAMPLE`。
3. **像素与跨帧 PBO + Fence 非阻塞回读门禁**：渲染确定性测试帧（参考 `fixtures/webgl2-smoke/index.html`），通过 `gl.PIXEL_PACK_BUFFER` + `gl.fenceSync` 跨帧轮询 `clientWaitSync(fence, 0, 0)`，待信号就绪后调用 `getBufferSubData` 断言中心像素非黑且无 NaN。
4. **上下文丢失恢复演练**：调用 `gl.getExtension('WEBGL_lose_context').loseContext()` 与 `restoreContext()`，断言一帧内恢复正常绘制且 `gl.getError() === gl.NO_ERROR`。
5. **差分性能与视觉回归门禁**：在固定 OS/浏览器/DPR 下比对基准截图，并通过逐通道开关记录帧时间差分与 `EXT_disjoint_timer_query_webgl2` 读数。

### 2. 内置四类着色器诊断输出模式 (`uDebugMode`)

为快速隔离渲染故障，着色器应支持一键切换诊断视图：

```glsl
if (uDebugMode == 1) { outColor = vec4(N * 0.5 + 0.5, 1.0); return; }           // 四面体法线可视化
if (uDebugMode == 2) { outColor = vec4(vec3(float(steps) / float(MAX_STEPS)), 1.0); return; } // 步数热力图
if (uDebugMode == 3) { outColor = vec4( dPdx * 16.0, length(dPdy) * 16.0, 1.0); return; }     // UV 微分接缝检查
if (isnan(col.r) || isnan(col.g) || isnan(col.b) || isinf(col.r)) {
  outColor = vec4(1.0, 0.0, 1.0, 1.0); return; // NaN / Inf 品红高亮报警
}
```

### 3. 仓库级静态校验与逆向自测门禁

运行 `python scripts/validate_repo.py` 与 `python scripts/verify_browser.py`，校验 JSON Schema、模块集合严格相等、全部 8 张 SVG 的 XML 合法性与文本框边距、四语种（`en`、`zh-CN`、`ja`、`ko`）结构与代码块对等、`registry/forbidden-slop.json` 四语种禁用词拦截，以及验证器自身的逆向自测（Negative Self-Tests）。

## 常见失效模式 (Failure modes)

- 未校验 `gl.checkFramebufferStatus` 就上线多通道浮点 FBO 管线
- 在生产环境每帧渲染循环中调用 `gl.getError()` 或同步 `gl.readPixels` 造成严重卡顿

## 输出契约贡献 (Output contribution)

填充 `deliverables`（验证矩阵）、`risks`、`validation_gates` 以及最终置信度评估。
