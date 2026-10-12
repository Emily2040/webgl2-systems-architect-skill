# 02 - WebGL 2.0 および GLSL ES 3.00 一次仕様リファレンス表 (ja)

本スキルパッケージで定義するすべての不変条件（Invariants）は、以下の一次仕様書およびハードウェアアーキテクチャ文書に基づいています。

| 領域 | 一次仕様書 / 技術標準 | 主要なエンジニアリング制約と対応モジュール |
| --- | --- | --- |
| **WebGL 2.0 レンダリングコンテキスト・ステートマシン** | Khronos WebGL 2.0 Specification (OpenGL ES 3.0.4 準拠) | 単一コンテキストの直列コマンド送出、VAO (`createVertexArray`) バインド必須、`texStorage2D` 不変テクスチャ割り当て、`invalidateFramebuffer` によるタイルメモリ書き戻し抑止、`MAX_CLIENT_WAIT_TIMEOUT_WEBGL == 0` (`03`, `06`) |
| **GLSL ES 3.00 シェーダー言語仕様** | The OpenGL ES Shading Language 3.00 Specification | 先頭バイト `#version 300 es`、`in`/`out` ステージ間変数、`layout(location = N)`、`layout(std140)` 16 バイト境界整列、非一様制御フロー内での暗黙的微分 (`texture`, `dFdx`, `dFdy`, `fwidth`) の未定義動作 (`05`) |
| **非同期コンパイル・GPU タイマー・FBO 拡張仕様** | Khronos WebGL Extension Registry (`KHR_parallel_shader_compile`, `EXT_disjoint_timer_query_webgl2`, `EXT_color_buffer_float`, `OES_texture_float_linear`, `WEBGL_lose_context`) | フレーム間での `COMPLETION_STATUS_KHR` ポーリング、`GPU_DISJOINT_EXT === false` 検証付き 3〜4 フレーム遅延タイマーリング、浮動小数点 FBO 完全性確認、コンテキスト復旧訓練 (`02`, `03`, `06`, `07`) |
| **SDF レイマーチング＆四面体法線数理** | Hart (1996) *Sphere Tracing: A Geometric Method for the Antialiased Ray Tracing of Implicit Surfaces*・四面体有限差分法 | Lipschitz 定数に基づくステップ減衰 (`stepScale = 0.65..0.85`)、6 タップ中心差分を置き換える 4 タップ四面体勾配法線 (`k = (±1,±1,±1)`) (`05`) |
| **WebGL 2.0 -> WebGPU 移行仕様** | W3C WebGPU & WGSL Specifications | `VAO -> GPUVertexBufferLayout`、`std140 UBO -> GPUBindGroup`、`WebGLFramebuffer -> GPURenderPassDescriptor`、クリップ空間深度 `Z in [-1, 1] -> [0, 1]` および UV Y 軸原点の単一ヘルパー隔離 (`06`) |
