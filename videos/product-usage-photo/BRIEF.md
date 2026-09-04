---
workflow: faceless-explainer
flow: automation
storyboard: no
message: "商品写真に、使っているところが分かる1枚を足す"
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

物だけを撮った商品写真では、買う人が大きさと似合うかを判断できない。使っているところが分かる1枚を足すと、その2つに答えられる。モデルは要らず自分の手で足りる、というところまでを短く伝える。ひとりネットショップ研究所へ公開する。

## Customizations

- **既存ナレーション音声を再利用する**（新規生成しない）。`~/ai-agent-workspace/outputs/video-short-20/audio/voice/sections/*.wav` と `scene-timings.json`。AivisSpeech まお・おちつきで生成済み、4セクション計45.01秒。
  - 01_hook 0.00-9.23 / 02_bunkai 9.23-24.13 / 03_naze 24.13-38.16 / 04_cta 38.16-45.01
- **視覚は product-detail-photo / product-size-photo と同じ水準に揃える。** 黒背景に文字だけのレイアウトは不可（2026-09-05に旧ジェネレータで作って差し戻しになった）。色面（#1534c5 / #f6f1e8）、フレームごとに異なる構図、CSS作図または実画像による図版を必ず入れる。
- **CTA契約 `../CTA-SPEC.md` を満たす。**
  - 尺の20〜40%に `data-cta-role="midpoint-lp"`。無音テロップ2秒「使うツールと手順は／概要欄にまとめてあります」
  - 最終フレームに `data-cta-role="end-subscribe"`。「一本に一つずつ／決めるだけで終わること」
  - どちらもルート直下のクリップに置く。フレーム内に埋めない
  - `python3 ../../cta_contract.py` で検査が通ること
- 関連動画（概要欄の本編リンク）は `fiS_R3IkQg4`。

## Notes

- 実在ブランド、既存出品者の商品画像、顔写真は使わない。図版はCSS作図で作る。
- 公開設定は public。仮タイトルは「商品写真、使っているところが1枚もありませんか #Shorts」。
- 概要欄にはLPリンク `?v=short-20` と広告表記（アップローダーのガードが要求する）。
