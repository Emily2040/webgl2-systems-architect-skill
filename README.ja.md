# WebGL 2.0 システムアーキテクト スキル (WebGL 2.0 Systems Architect Skill)

[English](./README.md) · [简体中文](./README.zh-CN.md) · **日本語** · [한국어](./README.ko.md)

[![Validate Skill Repository](https://github.com/Emily2040/webgl2-systems-architect-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/Emily2040/webgl2-systems-architect-skill/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-38bdf8.svg)](./LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-2dd4bf.svg)](./CHANGELOG.md)
[![Locales](https://img.shields.io/badge/locales-EN%20%7C%20zh--CN%20%7C%20ja%20%7C%20ko-f59e0b.svg)](./locales)

![WebGL 2.0 Systems Architect 6つのエンジニアリング柱の概要](./docs/assets/skill-infographic.svg)

`webgl2-systems-architect-skill` は、**WebGL 2.0 レンダラー設計、GLSL ES 3.00 (`#version 300 es`) シェーダー規律、GPU フレームバジェット計算、非ブロッキング `PIXEL_PACK_BUFFER` (PBO) + `gl.fenceSync` パイプライン、コンテキストロスト復旧、および WebGL 2.0 から WebGPU への移行** のためのルーティング型エンジニアリングスキルです。

本パッケージは **英語 (`en`)**、**簡体字中国語 (`zh-CN`)**、**日本語 (`ja`)**、**韓国語 (`ko`)** の 4 言語において、ネイティブドキュメント、ローカライズされたスキルモジュール、および反スロップ（Anti-Slop）検証ルールを備えています。

- **リポジトリ**: <https://github.com/Emily2040/webgl2-systems-architect-skill>
- **インタラクティブ WebGL 2.0 ワークベンチ (`docs/index.html`)**: [ローカルワークベンチを開く](./docs/index.html?lang=ja)
- **ライブ WebGL 2.0 スモークテストフィクスチャ**: [`fixtures/webgl2-smoke/index.html`](./fixtures/webgl2-smoke/index.html)
- **作成者**: **Iamemily2050** (`Emily2040`) · [Webサイト](https://Iamemily2050.com) · [X](https://x.com/iamemily2050) · [Instagram](https://instagram.com/iamemily2050)

---

## このスキルが存在する理由

従来のグラフィックス系プロンプトは、巨大な教科書 1 冊分をそのままコンテキストウィンドウへ流し込むものが大半でした。それではトークンを浪費するだけでなく、インスタンシングを用いたラスターメッシュ描画に SDF レイマーチングの規則を混同させるなど、タスクにそぐわない指示を引き起こします。

本リポジトリは WebGL 2.0 システム設計をルーティング型ワークフローとして定義します：

1. **極小ルーターエントリポイント**: ルートの [`SKILL.md`](./SKILL.md) は 800 文字未満に抑えられ、[`references/00-orchestrator.md`](./references/00-orchestrator.md)（日本語セッションでは [`locales/ja/references/00-orchestrator.md`](./locales/ja/references/00-orchestrator.md)）へ直結します。
2. **トリアージ主導のモジュール選択**: [`skills/core/01-triage.md`](./locales/ja/skills/core/01-triage.md) が 6 つの意図（`architecture`, `implementation`, `debug`, `optimize`, `review`, `migration`）と 6 つのプロジェクト分類（`raster-mesh`, `sdf-raymarch`, `hybrid`, `postprocess`, `data-vis`, `ui`）を判定し、[`registry/module-map.json`](./registry/module-map.json) に定義されたモジュールのみをロードします。
3. **不変条件とヒューリスティクスの分離**: 不変条件（自由変数の禁止、前提条件の明示、導出コメント付き定数、VAO バインド必須、FBO 完全性検証）は常に適用されます。一方、ヒューリスティクス（`alpha: false`、Reversed-Z、Deferred/Forward 選択、DPR 上限、サンプル数）は実測フレームバジェットに応じて決定されます。
4. **誠実な WebGL 2.0 並行処理モデル**: Web Worker はアセット取得、glTF/Draco 展開、KTX2 トランスコード、カリングを並列化し、`KHR_parallel_shader_compile` と `gl.PIXEL_PACK_BUFFER` + `gl.fenceSync` はフレームをまたいで非同期ポーリングを行いますが、単一 `WebGL2RenderingContext` 上の描画コール送出は直列として扱います。
5. **実行可能な検証ゲート**: [`scripts/validate_repo.py`](./scripts/validate_repo.py) が JSON スキーマ、モジュール集合の完全一致、SVG の XML 整形式とテキスト収まり、4 言語パリティ、禁止表現チェック、およびネガティブセルフテストを自動実行します。

---

## アーキテクチャブループリント

![WebGL 2.0 Systems Architect ルーティングレーンと並行実行ブループリント](./docs/assets/architecture.svg)

---

## 4 言語ネイティブサポート (`en`, `zh-CN`, `ja`, `ko`)

| 言語 (Locale) | ルート README | ローカライズ SKILL | ローカライズ Orchestrator | コアモジュール (`01`..`07`) |
|---|---|---|---|---|
| **English (`en`)** | [`README.md`](./README.md) | [`SKILL.md`](./SKILL.md) | [`references/00-orchestrator.md`](./references/00-orchestrator.md) | [`skills/core/`](./skills/core) |
| **简体中文 (`zh-CN`)** | [`README.zh-CN.md`](./README.zh-CN.md) | [`locales/zh-CN/SKILL.md`](./locales/zh-CN/SKILL.md) | [`locales/zh-CN/references/00-orchestrator.md`](./locales/zh-CN/references/00-orchestrator.md) | [`locales/zh-CN/skills/core/`](./locales/zh-CN/skills/core) |
| **日本語 (`ja`)** | [`README.ja.md`](./README.ja.md) | [`locales/ja/SKILL.md`](./locales/ja/SKILL.md) | [`locales/ja/references/00-orchestrator.md`](./locales/ja/references/00-orchestrator.md) | [`locales/ja/skills/core/`](./locales/ja/skills/core) |
| **한국어 (`ko`)** | [`README.ko.md`](./README.ko.md) | [`locales/ko/SKILL.md`](./locales/ko/SKILL.md) | [`locales/ko/references/00-orchestrator.md`](./locales/ko/references/00-orchestrator.md) | [`locales/ko/skills/core/`](./locales/ko/skills/core) |

[`registry/forbidden-slop.json`](./registry/forbidden-slop.json) は 4 言語すべての曖昧な宣伝文句（「圧倒的なパフォーマンス」「映画のような質感」「シームレスな体験」など）を検出し、具体的なボトルネック名、レンダーパス、数値閾値への置き換えを強制します。

---

## コアモジュールと意図別ルーティング

[`registry/module-map.json`](./registry/module-map.json) に定義された意図別のロード対象モジュール：

| 意図 (`intent`) | ロードされるモジュール | 主な成果物 |
|---|---|---|
| `architecture` | `01-triage`, `02-hardware-budget`, `03-pipeline-and-concurrency`, `04-subject-audit`, `05-shader-rules`, `06-runtime-ops`, `07-validation-and-ci` | ティア別システム設計、パスグラフ、フレームバジェット計算式、P0/P1/P2 視覚階層 |
| `implementation` | `01-triage`, `03-pipeline-and-concurrency`, `05-shader-rules`, `06-runtime-ops` | 自己完結型 `#version 300 es` シェーダー、VAO/`std140` UBO バインド、パス実装 |
| `debug` | `01-triage`, `05-shader-rules`, `06-runtime-ops`, `07-validation-and-ci` | FBO 不完全エラー、`mediump` 精度破綻、2x2 クアッド微分境界、コンテキストロストの原因特定 |
| `optimize` | `01-triage`, `02-hardware-budget`, `03-pipeline-and-concurrency`, `05-shader-rules`, `06-runtime-ops`, `07-validation-and-ci` | パス別差分計測計画、動的 `targetDPR` クランプ式、`invalidateFramebuffer`、帯域削減 |
| `review` | `01-triage`, `04-subject-audit`, `05-shader-rules`, `06-runtime-ops`, `07-validation-and-ci` | コード品質、ステート分離、P0/P1/P2 視覚説得力、本番出荷判定 |
| `migration` | `01-triage`, `03-pipeline-and-concurrency`, `05-shader-rules`, `06-runtime-ops`, `07-validation-and-ci` | WebGL 1 -> WebGL 2.0 更新、または WebGL 2.0 -> WebGPU（`GPUBindGroup`, WGSL, クリップ空間 `Z in [0, 1]`）移行計画 |

---

## 構造化出力スキーマとサンプル

- [`schemas/authoring-base.json`](./schemas/authoring-base.json) — フル設計・移行スキーマ（`skill`, `task`, `inputs`, `modules`, `assumptions`, `decisions`, `derivations`, `parallel_plan`, `deliverables`, `risks`, `validation_gates`）。
  - サンプル (`architecture` / `sdf-raymarch`): [`examples/face-raymarch.output.json`](./examples/face-raymarch.output.json)
  - サンプル (`migration` / `hybrid`): [`examples/webgpu-migration-hybrid.output.json`](./examples/webgpu-migration-hybrid.output.json)
- [`schemas/runtime-compact.json`](./schemas/runtime-compact.json) — コンパクト応答スキーマ（`intent`, `project_class`, `subject`, `locale`, `modules`, `assumptions`, `derivations`, `key_decisions`, `parallel_tasks`, `risks`, `next_steps`, `validation_gates`）。
  - サンプル (`optimize` / `raster-mesh`): [`examples/terrain-midrange.output.json`](./examples/terrain-midrange.output.json)
  - サンプル (`debug` / `postprocess`): [`examples/postprocess-context-loss.output.json`](./examples/postprocess-context-loss.output.json)

---

## インストールと検証手順

```bash
git clone https://github.com/Emily2040/webgl2-systems-architect-skill.git
cd webgl2-systems-architect-skill
python scripts/validate_repo.py
```

ローカルサーバーを起動して 4 言語対応ワークベンチ (`docs/index.html?lang=ja`) またはスモークテスト (`fixtures/webgl2-smoke/index.html`) を開くことができます：

```bash
python -m http.server 8080
```

---

## リリース＆著者情報

- **パッケージ名**: `webgl2-systems-architect-skill`
- **バージョン**: `2.0.0`
- **ライセンス**: [MIT](./LICENSE)
- **作成者**: **Iamemily2050** (`Emily2040`)
- **Git コミットメール**: `191656017+Emily2040@users.noreply.github.com`
- **リンク**: [GitHub リポジトリ](https://github.com/Emily2040/webgl2-systems-architect-skill) · [Webサイト](https://Iamemily2050.com) · [X (@iamemily2050)](https://x.com/iamemily2050) · [Instagram (@iamemily2050)](https://instagram.com/iamemily2050)
