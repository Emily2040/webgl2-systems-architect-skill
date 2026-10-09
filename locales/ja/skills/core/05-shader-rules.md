# 05 - GLSL ES 3.00 とシェーダー数値規律 (ja)

## Purpose

WebGL 2.0 シェーダーの移植性、自己完結性、数値安定性を保ち、マジックナンバーを排除する。すべてのシェーダーは `#version 300 es` で開始する。

## When to load

GLSL ES 3.00 の頂点・フラグメントシェーダーを作成、レビュー、デバッグ、最適化、または WGSL へ移行する際にロードする。

## Inputs

- シェーダーソースまたは対象のシェーディングアルゴリズム
- プロジェクト分類およびターゲット GPU の精度特性（モバイル `mediump` FP16 vs デスクトップ `highp` FP32）

## Rules

### 1. GLSL ES 3.00 (`#version 300 es`) ステージ契約を厳守する

- ファイル先頭バイトを `#version 300 es` とし、明示的な精度宣言（`precision highp float; precision highp int;`）を置く。
- 頂点入力は `layout(location = N) in`、ステージ間変数は `in` / `out`、フラグメント出力は `layout(location = 0) out vec4 outColor;` を使用する。WebGL 1.0 の `attribute`, `varying`, `texture2D`, `gl_FragColor` を混在させない。
- フレーム共通パラメータは `layout(std140) uniform FrameBlock { ... };` にまとめ、WebGPU の `GPUBindGroup` へ直接対応できるようにする。

### 2. 自由変数と根拠のないマジックナンバーを禁止する

すべてのヘルパー関数は引数、UBO、`in` 変数、または名前付き定数を通じて入力を受け取り、各定数には幾何学的・物理的導出コメントを添える（例：`SURF_HIT_EPS = 0.0042`, `NORMAL_GRAD_EPS = 0.0084`, `SKIN_F0 = 0.0255`）。

### 3. 精度・ゼロ除算・非一様制御フロー下の微分を保護する

- ワールド座標、カメラ位置、レイ原点・方向、経過時間 `uTime`、深度計算には必ず `highp` を用いる。
- 除算・平方根・べき乗をガードする：`inversesqrt(max(dot(v, v), 1e-12))`, `sqrt(max(x, 0.0))`, `pow(max(base, 0.0), expVal)`。
- 非一様な `if`, `for`, レイマーチ `break` ループに入る**前**に `vec2 dPdx = dFdx(uv); vec2 dPdy = dFdy(uv);` を計算し、分岐内では `textureGrad(uTex, uv, dPdx, dPdy)` または `textureLod` を使用する。
- SDF の法線計算には 4 タップの四面体差分法（Tetrahedral normal）を用いる。

## Failure modes

- `#version 300 es` シェーダー内で `varying` や `gl_FragColor` を使用してコンパイルエラーを起こす
- 動的ループや分岐内で暗黙 LOD の `texture(uTex, uv)` や `fwidth()` を呼び、2x2 クアッド境界アーティファクトを出す
- `std140` UBO 内で 16 バイト境界を考慮せず `vec3` 配列を並べる

## Output contribution

`derivations`（定数導出、精度選択、ループ上限）、シェーダーの `decisions`、数値面の `risks` を出力する。
