# 03 - パイプライン構成と並行処理設計 (ja)

## Purpose

CPU スレッドと単一 GPU キューにおける WebGL 2.0 の実際の実行モデルに即したレンダーパスグラフ、起動シーケンス、非同期パイプラインを設計する。単一コンテキストの描画送出は直列である。

## When to load

`architecture`, `implementation`, `optimize`, `migration` タスクでパスグラフ、FBO チェーン、Web Worker、シェーダーコンパイル、リードバックを扱う際にロードする。

## Inputs

- プロジェクト分類（`raster-mesh`, `sdf-raymarch`, `hybrid`, `postprocess`, `data-vis`, `ui`）
- レンダーパス構成、アセットサイズ、初回フレーム表示までの許容レイテンシ
- `OffscreenCanvas`, Web Worker, `KHR_parallel_shader_compile` の対応状況

## Rules

### 1. コンテキスト属性を惰性ではなく要件で選ぶ

不透明キャンバスでは `alpha: false` を指定してページコンポジタの合成負荷を省く。オフスクリーン FBO や SDF レイマーチでは `antialias: false` とし、必要な場合のみ `renderbufferStorageMultisample` + `blitFramebuffer` を使う。

### 2. 真の並列処理と単一コンテキスト直列処理を分離する

- **CPU / Web Worker で並列化可能**：`fetch`、glTF/Draco 展開、KTX2/Basis トランスコード、BVH 構築、フラスタムカリング、地形メッシュ生成、`createImageBitmap` デコード。
- **フレーム間でパイプライン化可能（非ブロッキング）**：
  - `KHR_parallel_shader_compile`：毎フレーム `ext.COMPLETION_STATUS_KHR` をポーリングし、`true` になってから `gl.LINK_STATUS` を取得する。
  - `gl.PIXEL_PACK_BUFFER` (PBO) + `gl.fenceSync(gl.SYNC_GPU_COMMANDS_COMPLETE, 0)` + `gl.clientWaitSync` + `gl.getBufferSubData` による非同期リードバック。
- **単一 `WebGL2RenderingContext` 上で直列**：状態変更、バッファ/テクスチャ転送、描画コール。

### 3. 初回フレーム起動の段階化とステートソート

フレーム 1 では最小限のシェーダーと 1x1 プレースホルダテクスチャ（`texStorage2D`）のみで即座に描画を開始し、高解像度アセットや補助シェーダーは後続フレームで非同期に準備する。パス内の描画は **FBO -> Program -> UBO/テクスチャ -> VAO -> Draw Call** の順にソートする。

## Failure modes

- 直列の `gl.*` 呼び出しを `async`/`await` で包んで並列 GPU 実行と主張する
- `COMPLETION_STATUS_KHR` が `false` のまま `LINK_STATUS` を照会してメインスレッドを停止させる
- 毎フレーム PBO なしで CPU 配列へ同期 `gl.readPixels` を呼ぶ

## Output contribution

`decisions`（コンテキスト属性、パスグラフ、起動フロー）、`parallel_plan`、並行処理の `risks` を出力する。
