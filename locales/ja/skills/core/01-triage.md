# 01 - トリアージとタスク分類 (ja)

## Purpose

WebGL 2.0 の要求を正確に分類し、必要なモジュールのみをロードして無関係なルールの混入を防ぐ。すべてのタスクはここから開始する。

## When to load

すべてのリクエストにおいて最初にロードする。

## Inputs

- ユーザープロンプトおよび対象言語（`en`, `zh-CN`, `ja`, `ko`）
- 既存のシェーダー、JS/TS コード、パスグラフ、リポジトリファイル（存在する場合）
- スクリーンショット、動画、GPU プロファイル、エラーログ（存在する場合）
- 対象デバイス、ブラウザ、目標 FPS（既知の場合）

## Rules

### 1. 要求を 4 つの軸で分類する

1. **意図 (`intent`)**
   - `architecture`：全体設計、パスグラフ、機能ティア分け、起動シーケンス
   - `implementation`：新規 `#version 300 es` シェーダー、FBO パス、VAO/UBO 実装
   - `debug`：描画不具合、`NaN`/精度バグ、不完全な FBO、状態リーク、コンテキストロスト
   - `optimize`：フレームレート低下、フィルレート圧迫、帯域ボトルネック、同期リードバック停止
   - `review`：コード監査、視覚的説得力評価、移植性チェック、本番出荷判定
   - `migration`：WebGL 1 から WebGL 2.0 への更新、または WebGL 2.0 から WebGPU/WGSL への移行計画

2. **プロジェクト分類 (`project_class`)**
   - `raster-mesh`, `sdf-raymarch`, `hybrid`, `postprocess`, `data-vis`, `ui`

3. **対象 (`subject`)**
   - `human face bust`、`terrain flyover`、`HDR bloom chain`、`WebGPU bind-group migration` など具体的な対象を明記する。

4. **エビデンス品質 (`hardware_data_quality`)**
   - `measured`（実測値あり）、`estimated`（デバイス層から推定）、`unknown`（プロンプトのみ、前提条件の明示が必須）。

### 2. 変更提案の前に既存の成果物を検査する

- シェーダーやコードがある場合は、`#version 300 es` 宣言、VAO/UBO バインド、FBO 構成、描画ループを先に確認する。

### 3. 意図別のモジュール選択 (`registry/module-map.json` と完全一致)

- `architecture`: `skills/core/01-triage.md`, `skills/core/02-hardware-budget.md`, `skills/core/03-pipeline-and-concurrency.md`, `skills/core/04-subject-audit.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`, `skills/core/07-validation-and-ci.md`
- `implementation`: `skills/core/01-triage.md`, `skills/core/03-pipeline-and-concurrency.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`
- `debug`: `skills/core/01-triage.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`, `skills/core/07-validation-and-ci.md`
- `optimize`: `skills/core/01-triage.md`, `skills/core/02-hardware-budget.md`, `skills/core/03-pipeline-and-concurrency.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`, `skills/core/07-validation-and-ci.md`
- `review`: `skills/core/01-triage.md`, `skills/core/04-subject-audit.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`, `skills/core/07-validation-and-ci.md`
- `migration`: `skills/core/01-triage.md`, `skills/core/03-pipeline-and-concurrency.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`, `skills/core/07-validation-and-ci.md`

## Failure modes

- 1 行のシェーダー修正に対して全モジュールをロードする
- ラスターメッシュパイプラインに SDF レイマーチング規則を強制する
- ボトルネックの切り分け前に視覚機能を削除する

## Output contribution

`task.intent`, `task.project_class`, `task.subject`, `inputs.hardware_data_quality`, `modules`, 初期 `assumptions` を確定する。
