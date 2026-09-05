---
workflow: faceless-explainer
flow: automation
storyboard: no
message: "商品写真の1枚目が暗いと、一覧で飛ばされる"
destination: youtube-shorts
aspect: 1080x1920
language: ja
audience: "商品写真を自分で撮る一人EC・ハンドメイド販売者"
length: 45s
angle: how-to
narration: yes
voice: "AivisSpeech まお・おちつき"
style_preset: cobalt-grid
---

## Intent

一覧に並んだとき、1枚目が暗い商品は見比べられる前に流れていく。原因は腕ではなく光。
窓際に移して白い紙を1枚立てるだけで解決する、というところまでを短く伝える。

## テーマ選定の根拠

`worklog/20260821_shorts_batch2_scripts.md` で凍結したタイトル型の実測に従った。

- 採用する型: **具体物を名指し + いま損している状態**（実測1,851 / 1,487 / 982再生）
- 避ける型: 「〜していますか？」のYes/No質問、抽象語

## 冒頭の型

`worklog/20260827_batch3_cta_redesign.md` の実測（平均視聴率 43.96% / 35.95% / 15.75%）に従い、
**01-hook では損だけを名指しし、直し方は 03-fix まで伏せる。** 合格ライン35%、目標50%。

## Customizations

- 画像は `image_pipeline.py` で生成（Codex優先）。`ASSETS.md` に出所を自動記録
- **暗い版と明るい版は同じ商品・同じ角度で光だけが違う。** 比較は合成側で並べる（生成画像に焼き込まない）
- CTA契約 `../CTA-SPEC.md` を満たす（尺の20〜40%に midpoint-lp、最終フレームに end-subscribe）

## Notes

- 実在ブランド、既存出品者の商品画像、顔写真は使わない。**オリジナル画像を生成して使う。CSS作図で代替しない**
- 公開設定は public。仮タイトルは「1枚目が暗いだけで、一覧で飛ばされています #Shorts」
- 概要欄にはLPリンク `?v=short-21` と広告表記
- 関連動画（概要欄の本編リンク）は `fiS_R3IkQg4`
