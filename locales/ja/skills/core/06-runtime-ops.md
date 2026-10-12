# 06 - ステート管理・リソース寿命・コンテキストロスト・WebGPU 移行 (ja)

## 目的 (Purpose)

WebGL 2.0 のステート漏れ、VRAM リーク、モバイルタイル GPU の不要な帯域消費、コンテキストロストからの復旧失敗を防ぎつつ、WebGPU へ移行しやすいリソース抽象を維持する。すべての GPU ハンドルを追跡する。

## ロード時期 (When to load)

すべての意図（`architecture`, `implementation`, `debug`, `optimize`, `review`, `migration`）でロードする。

## 入力 (Inputs)

- ホスト側 JS/TS レンダラーコード、パス設定、リサイズ処理、イベントリスナー
- テクスチャ、バッファ、VAO、Sampler、FBO、プログラムの生成と破棄経路

## 設計ルール (Rules)

### 1. パスごとのステート分離と WebGL 2.0 ネイティブオブジェクトの活用

- **VAO (`WebGLVertexArrayObject`)**：初期化時に `gl.createVertexArray()` で属性レイアウトを記録し、フレームループ内では `gl.bindVertexArray(vao)` のみを呼ぶ。`gl_VertexID` を用いるフルスクリーントライアングル描画でも非 null VAO のバインドが必須。
- **UBO (`Uniform Buffer Object`)**：`gl.uniformBlockBinding` と `gl.bindBufferBase(gl.UNIFORM_BUFFER, binding, ubo)` で `std140` ブロックを共有する。`bindBufferRange` のオフセットは `UNIFORM_BUFFER_OFFSET_ALIGNMENT` の倍数に揃える。
- **Sampler オブジェクト**：`gl.createSampler()` と `gl.bindSampler(unit, sampler)` でフィルタ設定をテクスチャ本体から分離する。

### 2. 不変テクスチャ割り当てとタイル GPU の Framebuffer Invalidation

- ミップ検証オーバーヘッドを避けるため、可変の `texImage2D` ではなく `gl.texStorage2D` / `gl.texStorage3D` + `gl.texSubImage2D` を使用する。
- モバイルのタイルベース GPU では、パス終了後に不要な深度/ステンシルアタッチメントへ `gl.invalidateFramebuffer(gl.FRAMEBUFFER, [gl.DEPTH_ATTACHMENT, gl.STENCIL_ATTACHMENT])` を呼び、システム RAM への書き戻しを抑止する。

### 3. リソース破棄とコンテキストロスト復旧 (`webglcontextlost` / `webglcontextrestored`)

- `gl.linkProgram(prog)` 成功直後に `detachShader` と `deleteShader` を実行する。
- `webglcontextlost` と `webglcontextrestored` を登録し、ロスト済みの旧ハンドルに `delete*` を呼ばず依存順で再構築する：

```js
canvas.addEventListener('webglcontextlost', (e) => {
  e.preventDefault();
  cancelAnimationFrame(rafId);
}, false);

canvas.addEventListener('webglcontextrestored', () => {
  initCapabilitiesAndExtensions(gl);
  rebuildShadersVAOsUBOsSamplersTexturesAndFBOs(gl);
  rafId = requestAnimationFrame(renderFrame);
}, false);
```

### 4. WebGL 2.0 から WebGPU (WGSL) への 1:1 移行マッピング表

| WebGL 2.0 の概念 | WebGPU の対応概念 | 移行設計ルール |
| --- | --- | --- |
| `WebGLVertexArrayObject` (VAO) | `GPUVertexBufferLayout` | バッファストライドと属性オフセットを初期化時の記述子に集約する |
| `std140` UBO + テクスチャユニット + `WebGLSampler` | `GPUBindGroupLayout` + `GPUBindGroup` | 更新頻度別（`group(0)` フレーム、`group(1)` パス、`group(2)` マテリアル）に編成する |
| `useProgram` + 可変ブレンド/深度ステート | 不変の `GPURenderPipeline` | シェーダー・ブレンド・深度・アタッチメント形式をキーに事前生成する |
| `WebGLFramebuffer` + `invalidateFramebuffer` | `GPURenderPassDescriptor` (`loadOp`/`storeOp`) | 一時的な深度バッファには `storeOp: 'discard'` を明示する |
| クリップ空間 `Z in [-1, 1]`・左下 UV 原点 | クリップ空間 `Z in [0, 1]`・左上フレームバッファ原点 | 深度リマップと UV Y 軸反転を単一のカメラ/ポストプロセス関数に隔離する |

## 典型的な失敗モード (Failure modes)

- VAO をバインドせずに `gl.drawArrays` を呼ぶ
- `webglcontextlost` で `e.preventDefault()` を忘れ、ロスト前のハンドルを再利用する

## 出力契約への寄与 (Output contribution)

ランタイムの `decisions`、リソース/ステート面の `risks`、`deliverables`（ライフサイクル表または WebGPU 移行対応表）を出力する。
