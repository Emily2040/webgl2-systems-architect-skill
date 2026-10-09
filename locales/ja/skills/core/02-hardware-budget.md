# 02 - ハードウェアプローブとフレームバジェット (ja)

## Purpose

アーキテクチャ設計と最適化判断を、WebGL 2.0 の実機能上限、メモリ帯域計算、実測フレーム時間に基づかせる。視覚機能を削る前に計測する。

## When to load

`architecture` および `optimize` タスク、または FPS 低下、DPR スケーリング、帯域圧迫、サーマルスロットリングが関わる場合にロードする。

## Inputs

- 対象プラットフォーム、ビューポート解像度、目標 FPS（`30`, `60`, `90`, `120`）
- `gl.getParameter` および `gl.getExtension` の実行時クエリ結果
- 既存のパス計測値または差分トグル計測データ

## Rules

### 1. WebGL 2.0 の機能上限を直接クエリする

User-Agent 文字列からの推測ではなく、`gl.getParameter` と `gl.getExtension` で実機上限を取得する：

- テクスチャ上限：`MAX_TEXTURE_SIZE`, `MAX_CUBE_MAP_TEXTURE_SIZE`, `MAX_3D_TEXTURE_SIZE`, `MAX_ARRAY_TEXTURE_LAYERS`, `MAX_TEXTURE_IMAGE_UNITS`, `MAX_VERTEX_TEXTURE_IMAGE_UNITS`
- MRT・MSAA 上限：`MAX_COLOR_ATTACHMENTS`, `MAX_DRAW_BUFFERS`, `MAX_SAMPLES`, `MAX_RENDERBUFFER_SIZE`
- Uniform・UBO 上限：`MAX_VERTEX_UNIFORM_VECTORS`, `MAX_FRAGMENT_UNIFORM_VECTORS`, `MAX_UNIFORM_BUFFER_BINDINGS`, `MAX_UNIFORM_BLOCK_SIZE`, `UNIFORM_BUFFER_OFFSET_ALIGNMENT`
- 拡張機能：`EXT_disjoint_timer_query_webgl2`, `KHR_parallel_shader_compile`, `EXT_color_buffer_float`, `OES_texture_float_linear`, `WEBGL_lose_context`

### 2. エビデンスの優先順位を厳守する

1. **リングバッファ方式の GPU タイマークエリ (`EXT_disjoint_timer_query_webgl2`)**：2〜3 フレーム後に `QUERY_RESULT_AVAILABLE` を確認し、`GPU_DISJOINT_EXT === false` の場合のみ `QUERY_RESULT` を採用する。
2. **制御された差分計測**：カメラとシーンを固定し、パス単位の ON/OFF や DPR 変更でフレーム時間差を測る。
3. **`gl.getParameter` による明示的な上限値**。
4. **デバイス層からのヒューリスティック推定**（最低ランク：`estimated` または `unknown` と明記）。

### 3. フレームバジェット・フィルレート・帯域を式で導出する

```text
frameBudgetMs = 1000 / targetFPS
gpuBudgetMs   = frameBudgetMs - cpuMainThreadReserveMs - browserCompositorReserveMs
activePixels  = (cssWidth * targetDPR) * (cssHeight * targetDPR)
bandwidthBps  = activePixels * bytesPerPixelReadWriteAcrossPasses * targetFPS
targetDPR     = min(devicePixelRatio, maxDPRCap, sqrt(gpuBudgetMs / (cssWidth * cssHeight * 1e-6 * msPerMegapixel)))
```

### 4. 3 段階の品質ティア (`low` / `mid` / `high`) を定義する

ティアごとに内部解像度スケール、`targetDPR` 上限、FBO フォーマット（`RGBA8` vs `RGBA16F`）、MSAA サンプル数、レイマーチ・フィルタのタップ数を明記する。

## Failure modes

- カタログ上の TFLOPS 値を実ブラウザ性能として扱う
- タイマークエリを同一フレームで同期取得する、または `GPU_DISJOINT_EXT` を無視する
- `bindBufferRange` のオフセットが `UNIFORM_BUFFER_OFFSET_ALIGNMENT` の倍数になっていない

## Output contribution

`inputs.hardware_data_quality`, `derivations`（バジェット・DPR・帯域）, ティア別の `decisions`, ハードウェアの `risks` を出力する。
