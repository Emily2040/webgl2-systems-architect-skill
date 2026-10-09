# 07 - 検証ラダー・プロファイリング・CI ゲート (ja)

## Purpose

WebGL 2.0 レンダラーおよびスキルパッケージが正しくコンパイルされ、期待通りのピクセルを描画し、コンテキストロストから復帰し、不変条件違反時に確実に失敗することを検証する。コンパイル通過だけで完了としない。

## When to load

`architecture`, `debug`, `optimize`, `review`, `migration` タスクでロードする。

## Inputs

- 検証対象のシェーダー、JS/TS ランタイムコード、または設計計画
- テスト環境（ローカルブラウザ、ヘッドレス Chrome/Playwright、CI ランナー）

## Rules

### 1. WebGL 2.0 の 5 段階検証ラダーを実行する

1. **シェーダーコンパイル＆リンクゲート**：先頭バイトの `#version 300 es` と `COMPILE_STATUS` / `LINK_STATUS` を検証する。
2. **フレームバッファ完全性＆ステートゲート**：すべてのカスタム FBO で `gl.checkFramebufferStatus(gl.FRAMEBUFFER) === gl.FRAMEBUFFER_COMPLETE` を検証し、`EXT_color_buffer_float` 未有効時の `FRAMEBUFFER_INCOMPLETE_ATTACHMENT` やサンプル数不一致による `FRAMEBUFFER_INCOMPLETE_MULTISAMPLE` を捕捉する。
3. **ピクセル＆ PBO + Fence スモークリードバックゲート**：既知座標のピクセル値を検証し（`fixtures/webgl2-smoke/index.html` 参照）、`gl.PIXEL_PACK_BUFFER` + `gl.fenceSync` による非同期リードバックも確認する。
4. **コンテキストロスト復旧ドリル**：`WEBGL_lose_context.loseContext()` と `restoreContext()` を実行し、`gl.getError() === gl.NO_ERROR` で描画が復帰することを確認する。
5. **差分パフォーマンス＆視覚回帰ゲート**：固定環境でのスクリーンショット比較と、パス個別トグルによるフレーム時間差分を計測する。

### 2. 診断用シェーダー出力モード

不具合切り分けのため、法線可視化 (`N * 0.5 + 0.5`)、レイマーチステップ数ヒートマップ、UV 微分不連続表示 (`fwidth(uv)`)、`isnan`/`isinf` マゼンタ検出 (`vec4(1.0, 0.0, 1.0, 1.0)`) を用意する。

### 3. リポジトリ検証とネガティブセルフテスト

`python scripts/validate_repo.py` を実行し、JSON スキーマ、モジュール集合の完全一致、SVG の XML 整形式とテキスト収まり、4 言語（`en`, `zh-CN`, `ja`, `ko`）パリティ、`registry/forbidden-slop.json` の禁止語検査、および不正入力を確実に拒否するネガティブセルフテストを通過させる。

## Failure modes

- `gl.checkFramebufferStatus` を確認せずにマルチパス FBO を出荷する
- 本番の毎フレーム描画ループ内で `gl.getError()` を呼び出して GPU/CPU 同期ストールを招く

## Output contribution

`deliverables`（検証マトリクス）、`risks`、`validation_gates`、および最終的な確信度評価を出力する。
