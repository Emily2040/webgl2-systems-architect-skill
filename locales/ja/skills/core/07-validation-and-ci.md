# 07 - 検証ラダー・プロファイリング・CI ゲート (ja)

## 目的 (Purpose)

WebGL 2.0 レンダラーおよびスキルパッケージが正しくコンパイルされ、期待通りのピクセルを描画し、コンテキストロストから復帰し、不変条件違反時に確実に失敗することを検証する。コンパイル通過だけで完了としない。

## ロード時期 (When to load)

`architecture`, `debug`, `optimize`, `review`, `migration` タスクでロードする。

## 入力 (Inputs)

- 検証対象のシェーダー、JS/TS ランタイムコード、または設計計画
- テスト環境（ローカルブラウザ、ヘッドレス Chromium/Playwright、CI ランナー）

## 設計ルール (Rules)

### 1. WebGL 2.0 の 5 段階検証ラダーを実行する

1. **シェーダーコンパイル＆リンクゲート**：先頭バイトの `#version 300 es` と `COMPILE_STATUS` / `LINK_STATUS` を検証する。
2. **フレームバッファ完全性＆ステートゲート**：すべてのカスタム FBO で `gl.checkFramebufferStatus(gl.FRAMEBUFFER) === gl.FRAMEBUFFER_COMPLETE` を検証し、`EXT_color_buffer_float` 未有効時の `FRAMEBUFFER_INCOMPLETE_ATTACHMENT` やサンプル数不一致による `FRAMEBUFFER_INCOMPLETE_MULTISAMPLE` を捕捉する。
3. **ピクセル＆複数フレーム PBO + Fence 非同期リードバックゲート**：既知座標のピクセル値を検証し（`fixtures/webgl2-smoke/index.html` 参照）、`gl.PIXEL_PACK_BUFFER` + `gl.fenceSync` をフレーム間でポーリングして完了後に `getBufferSubData` で読み出す。
4. **コンテキストロスト復旧ドリル**：`WEBGL_lose_context.loseContext()` と `restoreContext()` を実行し、`gl.getError() === gl.NO_ERROR` で描画が復帰することを確認する。
5. **差分パフォーマンス＆視覚回帰ゲート**：固定環境でのスクリーンショット比較と、パス個別トグルおよび `EXT_disjoint_timer_query_webgl2` によるフレーム時間差分を計測する。

### 2. 診断用シェーダー出力モード (`uDebugMode`)

不具合切り分けのため、シェーダー内に 4 つの診断出力モードを用意する：

```glsl
if (uDebugMode == 1) { outColor = vec4(N * 0.5 + 0.5, 1.0); return; }           // 四面体法線の可視化
if (uDebugMode == 2) { outColor = vec4(vec3(float(steps) / float(MAX_STEPS)), 1.0); return; } // ステップ数ヒートマップ
if (uDebugMode == 3) { outColor = vec4(dPdx * 16.0, length(dPdy) * 16.0, 1.0); return; }      // UV 微分不連続チェック
if (isnan(col.r) || isnan(col.g) || isnan(col.b) || isinf(col.r)) {
  outColor = vec4(1.0, 0.0, 1.0, 1.0); return; // NaN / Inf マゼンタ警告出力
}
```

### 3. リポジトリ検証とネガティブセルフテスト

`python scripts/validate_repo.py` および `python scripts/verify_browser.py` を実行し、JSON スキーマ、モジュール集合の完全一致、全 8 枚の SVG の XML 整形式とテキスト収まり、4 言語（`en`, `zh-CN`, `ja`, `ko`）パリティ、`registry/forbidden-slop.json` の 4 言語禁止表現検査、および不正入力を確実に拒否するネガティブセルフテストを通過させる。

## 典型的な失敗モード (Failure modes)

- `gl.checkFramebufferStatus` を確認せずにマルチパス FBO を出荷する
- 本番の毎フレーム描画ループ内で `gl.getError()` や同期 `gl.readPixels` を呼び出して GPU/CPU 同期ストールを招く

## 出力契約への寄与 (Output contribution)

`deliverables`（検証マトリクス）、`risks`、`validation_gates`、および最終的な確信度評価を出力する。
