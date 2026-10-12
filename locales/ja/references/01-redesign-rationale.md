# 01 - 再設計の根拠とアーキテクチャ上のトレードオフ (ja)

## 1. モノリシックなプロンプトをモジュラー型スキルへ分割した理由

従来の単一ファイル型 WebGL 2.0 プロンプトでは、顔面解剖学の比率、SDF レイマーチングのステップ制御、FBO アタッチメント管理、モバイル帯域計算、CI テストが 1 つの長大な文書に混在していました。この構造には 3 つの重大な欠陥がありました。

1. **コンテキストの希釈（Context Dilution）**：`webglcontextlost` によるブラックアウトや `EXT_color_buffer_float` 未対応 FBO のデバッグを行いたいだけでも、無関係な解剖学ルールや地形生成ルールまで読み込まれてしまいます。
2. **擬似的な精度とマジックナンバー（Pseudo-Precision）**：定数の導出根拠を記述する契約がないため、シェーダー内に物理的・幾何学的根拠のないリテラル（`0.003` や `1.42` など）が混入します。
3. **検証なき完了報告（Unverified Claims）**：「コンパイルが通った」ことや主観的な宣伝形容詞だけで完了とみなされ、FBO 完全性検査、非ブロッキング PBO リードバック、コンテキストロスト復旧訓練が欠落していました。

## 2. 主要なエンジニアリング改善点

- **意図ベースの最小モジュールルーティング（`registry/module-map.json`）**：`01-triage.md` によりタスクを 6 つの意図（`architecture`, `implementation`, `debug`, `optimize`, `review`, `migration`）と 6 つのプロジェクト分類へ切り分け、必要なモジュールのみをロードします。
- **実機計測とヒューリスティック推定の厳格な分離（`02-hardware-budget.md`）**：`EXT_disjoint_timer_query_webgl2` のリングバッファ計測と `gl.getParameter` の実機上限取得を最優先とし、カタログ上の TFLOPS 推測値を排除します。
- **単一コンテキスト直列提出と非同期パイプラインの分離（`03-pipeline-and-concurrency.md`）**：Web Worker による CPU 並列処理、フレーム間パイプライン処理（`KHR_parallel_shader_compile` ポーリング、複数フレームにわたる `PIXEL_PACK_BUFFER` + `gl.fenceSync` 非同期リードバック）、および単一 `WebGL2RenderingContext` 上の直列コマンド送出を明確に区別します。
- **観察可能な 5 層構造とバジェット削減順序（`04-subject-audit.md`）**：被写体を 5 つの観察レイヤーと P0/P1/P2 優先度に分解し、`gpuBudgetMs` 超過時は P2 演出 -> 0.5x 補助パス -> DPR クランプ -> P1 サンプル数の順に削減して P0 のシルエットを死守します。
- **GLSL ES 3.00 数値・微分規律（`05-shader-rules.md`）**：先頭バイトの `#version 300 es`、`std140` 16 バイト境界整列 UBO、Lipschitz 有界 SDF ステップ、4 タップ四面体法線、および非一様分岐前の `dFdx`/`dFdy` 事前計算＋`textureGrad` を徹底します。
- **2 種類の JSON 出力契約と禁止表現ゲート（`schemas/` + `registry/forbidden-slop.json`）**：`authoring-base.json` と `runtime-compact.json` の厳密なスキーマ検証に加え、日・英・中・韓 4 言語の誇大宣伝表現を `scripts/validate_repo.py` で自動遮断します。
