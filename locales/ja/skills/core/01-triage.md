# 01 - 意図トリアージとスコープ定義 (ja)

## 目的 (Purpose)

シェーダーの数式導出、FBO パス設計、または最適化作業に入る前に、ユーザーの WebGL 2.0 タスクを単一の主要な意図（Intent）とプロジェクト分類（Project Class）へ切り分け、最小のモジュール集合を確定する。トリアージを省略して実装に入ってはならない。

## ロード時期 (When to load)

すべてのタスクで最初にロードする（`architecture`, `implementation`, `debug`, `optimize`, `review`, `migration`）。

## 入力 (Inputs)

- ユーザーの要件、対象プラットフォーム、目標フレームレート
- 提供されたコード、シェーダー、スクリーンショット、計測ログ、またはプロンプトのみ（`prompt-only`）

## 設計ルール (Rules)

### 1. 主要なエンジニアリング意図を 1 つ選ぶ

- **`architecture`**：新規のマルチパス WebGL 2.0 レンダラー、SDF レイマーチングパイプライン、FBO トポロジー、またはハイブリッド設計を構築する。
- **`implementation`**：`#version 300 es` シェーダー、VAO/UBO/Sampler バインド、FBO 構築、またはホスト側 JS/TS 描画コードを実装する。
- **`debug`**：ブラックアウト、`FRAMEBUFFER_INCOMPLETE_*`、非一様分岐での微分アーティファクト、NaN 伝播、`webglcontextlost` クラッシュ、同期リードバック停止を診断する。
- **`optimize`**：フレーム落ち、高 DPI モバイル端末でのフィルレート過負荷、タイルメモリ帯域圧迫、CPU/GPU 同期ストールを解消する。
- **`review`**：既存のシェーダーまたはレンダラーの数値安定性、マジックナンバー、ステート漏れ、テスト網羅性を監査する。
- **`migration`**：WebGL 1.0 から WebGL 2.0 へ移行する、または WebGL 2.0 フォールバック付きの WebGPU (`navigator.gpu` + WGSL) デュアルバックエンドを設計する。

### 2. プロジェクト分類を 1 つ選ぶ

```text
raster-mesh | sdf-raymarch | hybrid | postprocess | data-vis | ui
```

### 3. 入力証跡を整理しハードウェアデータ品質を明記する

`inputs.hardware_data_quality` を以下の 4 段階のいずれかに分類する：
- **`measured`**：`EXT_disjoint_timer_query_webgl2` の実測値、または制御されたパス切り替え差分計測がある場合。
- **`partial`**：`gl.getParameter` の上限値や断片的な FPS 記録はあるが、パス単位の計測がない場合。
- **`estimated`**：デバイス層（「ミドルレンジ Android」「モバイル Safari」など）のみが判明している場合（必ずヒューリスティック推定と明記）。
- **`unknown`**：ターゲットハードウェア情報が一切ない場合。

### 4. `registry/module-map.json` の最小モジュール集合に厳密一致させる

出力の `modules` 配列は `registry/module-map.json[intent]` と完全一致させる（不要なモジュールを追加せず、必須モジュールを省かない）。

## 典型的な失敗モード (Failure modes)

- 局所的な `debug` や `implementation` タスクで全 7 モジュールを読み込み、コンテキストを希釈させる
- デバイス層からの推測値を実測（`measured`）データとして扱う
- `registry/module-map.json` と異なるモジュール一覧を出力する

## 出力契約への寄与 (Output contribution)

`task`（またはトップレベルの `intent`, `project_class`, `subject`, `locale`）、`inputs`、`modules`、および初期 `assumptions` を出力する。
