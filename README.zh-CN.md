# WebGL 2.0 系统架构师技能包 (WebGL 2.0 Systems Architect Skill)

[English](./README.md) · **简体中文** · [日本語](./README.ja.md) · [한국어](./README.ko.md)

[![Validate Skill Repository](https://github.com/Emily2040/webgl2-systems-architect-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/Emily2040/webgl2-systems-architect-skill/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-38bdf8.svg)](./LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-2dd4bf.svg)](./CHANGELOG.md)
[![Locales](https://img.shields.io/badge/locales-EN%20%7C%20zh--CN%20%7C%20ja%20%7C%20ko-f59e0b.svg)](./locales)

![WebGL 2.0 Systems Architect 六大工程支柱概览](./docs/assets/skill-infographic.svg)

`webgl2-systems-architect-skill` 是一个支持多智能体并行分流的 **WebGL 2.0 渲染器架构、GLSL ES 3.00 (`#version 300 es`) 着色器规范、GPU 帧预算推导、非阻塞 `PIXEL_PACK_BUFFER` (PBO) + `gl.fenceSync` 回读管线、上下文丢失恢复与 WebGL 2.0 到 WebGPU 迁移** 工程技能包。

本仓库内置 **英文 (`en`)**、**简体中文 (`zh-CN`)**、**日文 (`ja`)** 与 **韩文 (`ko`)** 四语言原生文档、本地化技能模块与反套话（Anti-Slop）校验规则。

- **GitHub 仓库**: <https://github.com/Emily2040/webgl2-systems-architect-skill>
- **交互式 WebGL 2.0 工程工作台 (`docs/index.html`)**: [打开本地四语言工作台](./docs/index.html?lang=zh-CN)
- **实时 WebGL 2.0 冒烟测试夹具**: [`fixtures/webgl2-smoke/index.html`](./fixtures/webgl2-smoke/index.html)
- **作者**: **Iamemily2050** (`Emily2040`) · [个人网站](https://Iamemily2050.com) · [X](https://x.com/iamemily2050) · [Instagram](https://instagram.com/iamemily2050)

---

## 为什么采用路由式架构

传统的图形学提示词往往把整本教科书一次性塞进上下文窗口，不仅浪费 Token，还会把不兼容的规则混为一谈（例如在实例化光栅网格管线中强行套用 SDF 光线步进规则），导致输出充满泛泛而谈的空话。

本技能将 WebGL 2.0 图形系统工程重构为按需路由的模块化工作流：

1. **极简路由入口**：根目录 [`SKILL.md`](./SKILL.md) 严格控制在 800 字符以内，直接路由至总控编排器 [`references/00-orchestrator.md`](./references/00-orchestrator.md)（中文会话可直接加载 [`locales/zh-CN/references/00-orchestrator.md`](./locales/zh-CN/references/00-orchestrator.md)）。
2. **分流优先的模块加载**：[`skills/core/01-triage.md`](./locales/zh-CN/skills/core/01-triage.md) 按 6 类任务意图（`architecture`, `implementation`, `debug`, `optimize`, `review`, `migration`）与 6 类项目类型（`raster-mesh`, `sdf-raymarch`, `hybrid`, `postprocess`, `data-vis`, `ui`）对请求进行分类，仅加载 [`registry/module-map.json`](./registry/module-map.json) 中映射的模块。
3. **严格区分不变量与启发式默认项**：不变量（无自由变量、显式假设、带推导注释的数值常量、必绑 VAO、FBO 完整性检查）在任何场景下恒成立；启发式策略（`alpha: false`、反向 Z、延迟/前向渲染取舍、DPR 钳制上限、采样步数）则取决于实测帧预算。
4. **诚实的 WebGL 2.0 并发模型**：Web Worker 可并行处理网络拉取、glTF/Draco 解压、KTX2 转码与视锥剔除；`KHR_parallel_shader_compile` 与 `gl.PIXEL_PACK_BUFFER` + `gl.fenceSync` 可跨帧流水线化轮询状态；但单个 `WebGL2RenderingContext` 上的状态切换与绘制调用始终保持串行。
5. **可执行的自动化门禁**：[`scripts/validate_repo.py`](./scripts/validate_repo.py) 自动校验 JSON Schema、模块集合严格相等、SVG XML 良构性与文本框边界、四语言对等性、禁用套话扫描以及负向自测用例。

---

## 架构蓝图

![WebGL 2.0 Systems Architect 多通道路由与并发执行蓝图](./docs/assets/architecture.svg)

---

## 原生四语言支持 (`en`, `zh-CN`, `ja`, `ko`)

工程师与编程智能体可在四种语言环境下原生运行本技能：

| 语言 (Locale) | 根目录文档 | 本地化技能入口 | 本地化总控编排器 | 核心模块 (`01`..`07`) |
|---|---|---|---|---|
| **English (`en`)** | [`README.md`](./README.md) | [`SKILL.md`](./SKILL.md) | [`references/00-orchestrator.md`](./references/00-orchestrator.md) | [`skills/core/`](./skills/core) |
| **简体中文 (`zh-CN`)** | [`README.zh-CN.md`](./README.zh-CN.md) | [`locales/zh-CN/SKILL.md`](./locales/zh-CN/SKILL.md) | [`locales/zh-CN/references/00-orchestrator.md`](./locales/zh-CN/references/00-orchestrator.md) | [`locales/zh-CN/skills/core/`](./locales/zh-CN/skills/core) |
| **日本語 (`ja`)** | [`README.ja.md`](./README.ja.md) | [`locales/ja/SKILL.md`](./locales/ja/SKILL.md) | [`locales/ja/references/00-orchestrator.md`](./locales/ja/references/00-orchestrator.md) | [`locales/ja/skills/core/`](./locales/ja/skills/core) |
| **한국어 (`ko`)** | [`README.ko.md`](./README.ko.md) | [`locales/ko/SKILL.md`](./locales/ko/SKILL.md) | [`locales/ko/references/00-orchestrator.md`](./locales/ko/references/00-orchestrator.md) | [`locales/ko/skills/core/`](./locales/ko/skills/core) |

[`registry/forbidden-slop.json`](./registry/forbidden-slop.json) 内置全部四个语种的禁用词与替换规则，强制将“电影级画质”、“极致性能”、“无缝体验”等空洞形容词替换为具体的瓶颈类型、通道名称与帧耗时预算。

---

## 核心模块与意图路由矩阵

[`registry/module-map.json`](./registry/module-map.json) 定义了每类意图加载的标准模块集合：

| 任务意图 (`intent`) | 加载模块 | 核心交付物 |
|---|---|---|
| `architecture` | `01-triage`, `02-hardware-budget`, `03-pipeline-and-concurrency`, `04-subject-audit`, `05-shader-rules`, `06-runtime-ops`, `07-validation-and-ci` | 分档系统架构、渲染通道图、帧预算推导公式与 P0/P1/P2 视觉层级 |
| `implementation` | `01-triage`, `03-pipeline-and-concurrency`, `05-shader-rules`, `06-runtime-ops` | 自包含 `#version 300 es` 着色器、VAO/`std140` UBO 绑定与通道实现代码 |
| `debug` | `01-triage`, `05-shader-rules`, `06-runtime-ops`, `07-validation-and-ci` | FBO 不完整、`mediump` 溢出、2x2 像素块导数接缝及上下文丢失根因定位 |
| `optimize` | `01-triage`, `02-hardware-budget`, `03-pipeline-and-concurrency`, `05-shader-rules`, `06-runtime-ops`, `07-validation-and-ci` | 通道差分计时方案、动态 `targetDPR` 钳制、`invalidateFramebuffer` 与带宽优化 |
| `review` | `01-triage`, `04-subject-audit`, `05-shader-rules`, `06-runtime-ops`, `07-validation-and-ci` | 代码质量、状态隔离、P0/P1/P2 视觉可信度与上线就绪审计 |
| `migration` | `01-triage`, `03-pipeline-and-concurrency`, `05-shader-rules`, `06-runtime-ops`, `07-validation-and-ci` | WebGL 1 升级 WebGL 2.0 或 WebGL 2.0 迁移至 WebGPU（`GPUBindGroup`、WGSL、裁剪空间 `Z in [0, 1]`）蓝图 |

---

## 结构化输出契约与示例

下游工具与 CI 流程可请求符合以下任一 JSON Schema 的结构化输出：

- [`schemas/authoring-base.json`](./schemas/authoring-base.json) — 完整架构与迁移契约（包含 `skill`, `task`, `inputs`, `modules`, `assumptions`, `decisions`, `derivations`, `parallel_plan`, `deliverables`, `risks`, `validation_gates`）。
  - 示例 (`architecture` / `sdf-raymarch`)：[`examples/face-raymarch.output.json`](./examples/face-raymarch.output.json)
  - 示例 (`migration` / `hybrid`)：[`examples/webgpu-migration-hybrid.output.json`](./examples/webgpu-migration-hybrid.output.json)
- [`schemas/runtime-compact.json`](./schemas/runtime-compact.json) — 紧凑运行时契约（包含 `intent`, `project_class`, `subject`, `locale`, `modules`, `assumptions`, `derivations`, `key_decisions`, `parallel_tasks`, `risks`, `next_steps`, `validation_gates`）。
  - 示例 (`optimize` / `raster-mesh`)：[`examples/terrain-midrange.output.json`](./examples/terrain-midrange.output.json)
  - 示例 (`debug` / `postprocess`)：[`examples/postprocess-context-loss.output.json`](./examples/postprocess-context-loss.output.json)

---

## 仓库目录结构

```text
webgl2-systems-architect-skill/
├── SKILL.md                              # 紧凑路由入口 (< 800 字符)
├── AGENTS.md / CLAUDE.md / GEMINI.md     # 跨平台智能体启动指令
├── README.md / README.zh-CN.md / README.ja.md / README.ko.md
├── agents/openai.yaml                    # OpenAI / Codex 接口元数据
├── references/
│   ├── 00-orchestrator.md                # 并行通道编排、合并顺序与输出规范
│   ├── 01-redesign-rationale.md          # 架构设计依据与核心不变量
│   └── 02-webgl2-source-table.md         # Khronos/MDN/WebGPU 规范锚点与 7 项兼容性门禁
├── skills/core/                          # 01-triage 至 07-validation-and-ci 核心模块
├── locales/{zh-CN,ja,ko}/                # 原生中/日/韩技能路由、总控编排器与核心模块
├── registry/
│   ├── module-map.json                   # 标准意图 -> 模块映射表
│   └── forbidden-slop.json               # 四语言禁用套话与证据替换规则
├── schemas/                              # authoring-base.json 与 runtime-compact.json
├── examples/                             # 覆盖多意图的 4 个 Schema 校验示例
├── fixtures/webgl2-smoke/index.html      # 实时 WebGL2 VAO + std140 UBO + PBO/fenceSync 夹具
├── docs/
│   ├── index.html                        # 交互式四语言 WebGL2 工程工作台
│   └── assets/                           # 通过 XML 与边界校验的 SVG/PNG 架构蓝图
└── scripts/validate_repo.py              # 零第三方依赖的全量验证与负向自测脚本
```

---

## 安装与验证

### 1. 在 Codex / Claude Code / Gemini / Antigravity 中安装

将仓库克隆至本地技能目录：

```bash
git clone https://github.com/Emily2040/webgl2-systems-architect-skill.git
```

调用 `$webgl2-systems-architect-skill` 或引导智能体读取 [`locales/zh-CN/SKILL.md`](./locales/zh-CN/SKILL.md)。

### 2. 运行仓库校验与负向自测

仅依赖 Python 3 标准库：

```bash
python scripts/validate_repo.py
```

### 3. 启动交互式工作台与冒烟测试

```bash
python -m http.server 8080
```

在浏览器中打开 `http://localhost:8080/docs/index.html?lang=zh-CN` 或 `http://localhost:8080/fixtures/webgl2-smoke/index.html`。

---

## 版本与作者信息

- **技能包名称**: `webgl2-systems-architect-skill`
- **当前版本**: `2.0.0`
- **开源协议**: [MIT](./LICENSE)
- **作者**: **Iamemily2050** (`Emily2040`)
- **Git 提交邮箱**: `191656017+Emily2040@users.noreply.github.com`
- **相关链接**: [GitHub 仓库](https://github.com/Emily2040/webgl2-systems-architect-skill) · [个人网站](https://Iamemily2050.com) · [X (@iamemily2050)](https://x.com/iamemily2050) · [Instagram (@iamemily2050)](https://instagram.com/iamemily2050)
