# 06 - ステート管理・リソース寿命・コンテキストロスト・WebGPU 移行 (ja)

## Purpose

WebGL 2.0 のステート漏れ、VRAM リーク、モバイルタイル GPU の不要な帯域消費、コンテキストロストからの復旧失敗を防ぎつつ、WebGPU へ移行しやすいリソース抽象を維持する。すべての GPU ハンドルを追跡する。

## When to load

すべての意図（`architecture`, `implementation`, `debug`, `optimize`, `review`, `migration`）でロードする。

## Inputs

- ホスト側 JS/TS レンダラーコード、パス設定、リサイズ処理、イベントリスナー
- テクスチャ、バッファ、VAO、Sampler、FBO、プログラムの生成と破棄経路

## Rules

### 1. パスごとのステート分離と WebGL 2.0 ネイティブオブジェクトの活用

- **VAO (`WebGLVertexArrayObject`)**：初期化時に `gl.createVertexArray()` で属性レイアウトを記録し、フレームループ内では `gl.bindVertexArray(vao)` のみを呼ぶ。`gl_VertexID` を用いるフルスクリーントライアングル描画でも VAO のバインドが必須。
- **UBO (`Uniform Buffer Object`)**：`gl.uniformBlockBinding` と `gl.bindBufferBase(gl.UNIFORM_BUFFER, binding, ubo)` で `std140` ブロックを共有する。`bindBufferRange` のオフセットは `UNIFORM_BUFFER_OFFSET_ALIGNMENT` の倍数に揃える。
- **Sampler オブジェクト**：`gl.createSampler()` と `gl.bindSampler(unit, sampler)` でフィルタ設定をテクスチャ本体から分離する。

### 2. 不変テクスチャ割り当てとタイル GPU の Framebuffer Invalidation

- ミップ検証オーバーヘッドを避けるため、可変の `texImage2D` ではなく `gl.texStorage2D` / `gl.texStorage3D` + `gl.texSubImage2D` を使用する。
- モバイルのタイルベース GPU では、パス終了後に不要な深度/ステンシルアタッチメントへ `gl.invalidateFramebuffer(gl.FRAMEBUFFER, [gl.DEPTH_ATTACHMENT, gl.STENCIL_ATTACHMENT])` を呼び、システム RAM への書き戻しを抑止する。

### 3. リソース破棄とコンテキストロスト復旧 (`webglcontextlost` / `webglcontextrestored`)

- `gl.linkProgram(prog)` 成功直後に `detachShader` と `deleteShader` を実行する。
- `webglcontextlost` で `event.preventDefault()` と `cancelAnimationFrame` を呼び、`webglcontextrestored` でシェーダー -> VAO/UBO/Sampler -> テクスチャ -> FBO の順に再構築する。

### 4. WebGL 2.0 から WebGPU への移行マッピング

- `VAO` -> `GPUVertexBufferLayout`
- `std140` UBO + テクスチャ + `WebGLSampler` -> `GPUBindGroupLayout` + `GPUBindGroup`
- `useProgram` + 可変ブレンド/深度ステート -> 不変の `GPURenderPipeline`
- `WebGLFramebuffer` + `invalidateFramebuffer` -> `GPURenderPassDescriptor` (`loadOp` / `storeOp`)
- クリップ空間 `Z in [-1, 1]`（左下 UV 原点） -> WebGPU `Z in [0, 1]`（左上フレームバッファ原点）

## Failure modes

- VAO をバインドせずに `gl.drawArrays` を呼ぶ
- `webglcontextlost` で `e.preventDefault()` を忘れ、ロスト前のハンドルを再利用する

## Output contribution

ランタイムの `decisions`、リソース/ステート面の `risks`、`deliverables`（ライフサイクル表または WebGPU 移行対応表）を出力する。
