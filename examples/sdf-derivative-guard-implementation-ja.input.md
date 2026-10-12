# 入力ブリーフ：SDF レイマーチングにおける非一様分岐の微分保護と四面体法線の実装 (ja)

WebGL 2.0 の SDF レイマーチングシェーダー（`sdf-raymarch`）において、マテリアル ID ごとの動的分岐内で発生しているミップマップ境界ノイズを修正し、6 タップ中心差分法線を 4 タップ四面体法線（Tetrahedral Normal）へ置き換える実装計画（`implementation`）を `runtime-compact` 形式（`locale: "ja"`）で作成してください。
