# 03 - パイプライン構成と並行処理設計 (ja)

## 目的 (Purpose)

CPU スレッドと単一 GPU キューにおける WebGL 2.0 の実際の実行モデルに即したレンダーパスグラフ、起動シーケンス、非同期パイプラインを設計する。単一コンテキストの描画送出は常に直列である。

## ロード時期 (When to load)

`architecture`, `implementation`, `optimize`, `migration` タスクでパスグラフ、FBO チェーン、Web Worker、シェーダーコンパイル、リードバックを扱う際にロードする。

## 入力 (Inputs)

- プロジェクト分類（`raster-mesh`, `sdf-raymarch`, `hybrid`, `postprocess`, `data-vis`, `ui`）
- レンダーパス構成、アセットサイズ、初回フレーム表示までの許容レイテンシ
- `OffscreenCanvas`, Web Worker, `KHR_parallel_shader_compile` の対応状況

## 設計ルール (Rules)

### 1. コンテキスト属性を惰性ではなく要件で選ぶ

不透明キャンバスでは `alpha: false` を指定してページコンポジタの合成負荷を省く。オフスクリーン FBO や SDF レイマーチでは `antialias: false` とし、必要な場合のみ `renderbufferStorageMultisample` + `blitFramebuffer` を使う。

### 2. 真の並列処理、フレーム間パイプライン、単一コンテキスト直列処理を分離する

- **CPU / Web Worker で並列化可能**：`fetch`、glTF/Draco 展開、KTX2/Basis トランスコード、BVH 構築、フラスタムカリング、地形メッシュ生成、`createImageBitmap` デコード。
- **フレーム間でパイプライン化可能（非ブロッキング GPU/CPU オーバーラップ）**：
  - `KHR_parallel_shader_compile`：フレームをまたいで `ext.COMPLETION_STATUS_KHR` をポーリングし、`true` になってから `gl.LINK_STATUS` を取得する：

```js
function pollProgramLink(gl, ext, prog) {
  if (ext && !gl.getProgramParameter(prog, ext.COMPLETION_STATUS_KHR)) return null;
  return gl.getProgramParameter(prog, gl.LINK_STATUS);
}
```

  - `gl.PIXEL_PACK_BUFFER` (PBO) + `gl.fenceSync`：フレーム $N$ で非同期 `readPixels` とフェンスを発行し、後続フレームで `clientWaitSync(fence, 0, 0)` をポーリングしてシグナル完了後にのみ `getBufferSubData` を呼ぶ：

```js
// フレーム N：PBO への非同期パックを開始しフェンスを挿入
gl.bindBuffer(gl.PIXEL_PACK_BUFFER, pbo);
gl.readPixels(x, y, w, h, gl.RGBA, gl.UNSIGNED_BYTE, 0);
gl.bindBuffer(gl.PIXEL_PACK_BUFFER, null);
const fence = gl.fenceSync(gl.SYNC_GPU_COMMANDS_COMPLETE, 0);
gl.flush();
// フレーム N+k：timeout = 0 で非ブロッキング確認し、完了時のみ読み出す
const status = gl.clientWaitSync(fence, 0, 0);
if (status === gl.ALREADY_SIGNALED || status === gl.CONDITION_SATISFIED) {
  gl.bindBuffer(gl.PIXEL_PACK_BUFFER, pbo);
  gl.getBufferSubData(gl.PIXEL_PACK_BUFFER, 0, dstPixels);
  gl.bindBuffer(gl.PIXEL_PACK_BUFFER, null);
  gl.deleteSync(fence);
}
```

- **単一 `WebGL2RenderingContext` 上で直列**：状態変更、バッファ/テクスチャ転送、描画コール。

### 3. 初回フレーム起動の段階化とステートソート

フレーム 1 では最小限のシェーダーと 1×1 プレースホルダテクスチャ（`texStorage2D`）のみで即座に描画を開始し、高解像度アセットや補助シェーダーは後続フレームで非同期に準備する。パス内の描画は **FBO -> Program -> UBO/テクスチャ -> VAO -> Draw Call** の順にソートする。

## 典型的な失敗モード (Failure modes)

- 直列の `gl.*` 呼び出しを `async`/`await` で包んで並列 GPU 実行と主張する
- `COMPLETION_STATUS_KHR` が `false` のまま `LINK_STATUS` を照会してメインスレッドを停止させる
- `readPixels` と同一フレームで `TIMEOUT_EXPIRED` を無視して `getBufferSubData` を呼び、同期ストールを引き起こす

## 出力契約への寄与 (Output contribution)

`decisions`（コンテキスト属性、パスグラフ、起動フロー）、`parallel_plan`（または `parallel_tasks`）、並行処理の `risks` を出力する。
