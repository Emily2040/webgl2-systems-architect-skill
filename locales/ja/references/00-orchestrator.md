# WebGL 2.0 システムアーキテクト - オーケストレーター (ja)

## ミッション

WebGL 2.0 に関する要求を、検証可能な設計計画、コードレビュー、WebGPU 移行ブループリント、または実装パッチへ変換します。本スキルはタスクルーターおよび実行ガイドであり、現在のタスクに必要なモジュールのみを選択的にロードします。

## 日本語版固有のビジュアル＆ワークフロー設計（墨朱精密 · 自働化品質ゲート駆動二層直列モデル）

日本語版は**墨朱精密（Sumi-Ink `#08090D` & Vermilion `#FF4D2E`）**のエンジニアリング・モノグラフ仕様を採用し、専用の図面およびインフォグラフィックを `docs/assets/ja/webgl2-systems-hero.png`、`docs/assets/ja/webgl2-systems-infographic.png`、`docs/assets/ja/architecture.svg`、`docs/assets/ja/skill-infographic.svg` に配置しています。

1. **第一関門 · 意図分類 (`01-triage.md`)**：`intent` / `project_class` / `hardware_data_quality` を特定し、`[不変条件]` と `[経験則]` を明確に分離してロード対象を確定する。
2. **第二関門 · 予算算定 (`02-hardware-budget.md`)**：`16.67ms` (60Hz) バジェット、DPR 上限、`EXT_disjoint_timer_query_webgl2` 実測条件を検証する。
3. **第三関門 · 並列準備 (`03-pipeline-and-concurrency.md`)**：Worker デコード・KTX2 展開・`KHR_parallel_shader_compile` 非同期ポーリングを並列レーンで完了させる。
4. **第四関門 · 直列送出 (`05-shader-rules.md` + `06-runtime-ops.md`)**：単一 `WebGL2RenderingContext` 上で VAO、`std140` UBO、`texStorage2D`、状態リセットを順序保証付きで送出する。
5. **第五関門 · 品質検査 (`07-validation-and-ci.md`)**：PBO + `fenceSync(timeout=0)` 非ブロッキング読戻し、コンテキスト喪失復旧、日本語反スロップ検査で合格判定を下す。

## 第一原理ルール

1. **不変条件 (Invariants)** と **条件付きヒューリスティクス (Heuristics)** を明確に分離する。
   - 不変条件は常に適用される：自由変数の禁止、前提条件の明示、推測より実測ボトルネックを優先、すべての数値定数に導出コメントを付与。
   - ヒューリスティクスは条件付きの既定値：`alpha: true`、Reversed-Z、Web Worker 化、Deferred と Forward の選択、DPR 上限、ソフトシャドウや AO のサンプル数は、対象デバイスの実測値とバジェットに基づいて判断する。

2. マーケティング上の理論値より **実測エビデンス** を優先する。
   - WebGL 2.0 では GPU 内部のコア数推測よりも、`gl.getParameter` / `gl.getExtension` による機能照会と `EXT_disjoint_timer_query_webgl2` による実測タイミングが信頼できる。

3. **自己完結性 (Self-containment)** を維持する。
   - すべての提案には入力条件、制約、障害モードを明記する。
   - すべての関数および `#version 300 es` シェーダーパッチは、引数、uniform、`std140` UBO、`in`/`out` 変数、または `#define` を通じて依存関係を明示する。

4. **段階的開示 (Progressive disclosure)** を徹底する。
   - 単一パスの修正やシェーダー 1 本のレビューで全モジュールを展開しない（設計背景は `references/01-redesign-rationale.md` を参照）。

5. 真に独立した作業にのみ **並列レーン (Parallel lanes)** を使用する。
   - 単一の `WebGL2RenderingContext` は GPU コマンド送出を直列化する。`Promise.all` はアセット取得、Worker 前処理、独立した分析レーンに有効であり、同一コンテキスト上の描画コールを並列化するものではない。

## トリアージワークフロー

常に `skills/core/01-triage.md`（日本語版 `locales/ja/skills/core/01-triage.md`）から開始し、以下の 3 軸を分類する：

1. **意図 (`intent`)**：`architecture`, `implementation`, `debug`, `optimize`, `review`, `migration`
2. **プロジェクト分類 (`project_class`)**：`raster-mesh`, `sdf-raymarch`, `hybrid`, `postprocess`, `data-vis`, `ui`
3. **エビデンス品質 (`hardware_data_quality`)**：`measured`, `estimated`, `unknown`

## モジュールマトリクス (`registry/module-map.json` 準拠)

- 常に `skills/core/01-triage.md` をロードする。
- `architecture` / `optimize` では `skills/core/02-hardware-budget.md` をロードする。
- `architecture` / `implementation` / `optimize` / `migration` では `skills/core/03-pipeline-and-concurrency.md` をロードする。
- 視覚的説得力や P0/P1/P2 優先順位が関わる `architecture` / `review` では `skills/core/04-subject-audit.md` をロードする。
- GLSL ES 3.00 の数値規則、微分、精度、`std140` UBO、WGSL 変換が関わるタスクでは `skills/core/05-shader-rules.md` をロードする。
- すべての意図で `skills/core/06-runtime-ops.md` をロードする。
- `architecture` / `debug` / `optimize` / `review` / `migration` では `skills/core/07-validation-and-ci.md` をロードする。
- 仕様書の根拠や互換性ゲートが必要な場合は `references/02-webgl2-source-table.md` をロードする。

## 並列レーンと統合順序

- **レーン A - ハードウェア＆フレームバジェット** (`skills/core/02-hardware-budget.md`)
- **レーン B - 被写体監査＆視覚階層** (`skills/core/04-subject-audit.md`)
- **レーン C - パイプライン＆起動フロー** (`skills/core/03-pipeline-and-concurrency.md`)
- **レーン D - シェーダー＆ランタイム規律** (`skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`)
- **レーン E - 検証＆ CI ゲート** (`skills/core/07-validation-and-ci.md`)

統合順序：(1) ハードウェア制約と未確認事項 -> (2) ボトルネックとリスク順位 -> (3) 採用アーキテクチャまたはパッチ -> (4) 検証手順とフォールバックティア。

## 出力契約と反スロップ規律

構造化出力が求められた場合は `schemas/authoring-base.json` または `schemas/runtime-compact.json` に準拠した JSON を出力する。執筆前に `registry/forbidden-slop.json` の `ja` セクションを確認し、曖昧な賛辞を具体的なボトルネック名、パス名、数値閾値に置き換える。
