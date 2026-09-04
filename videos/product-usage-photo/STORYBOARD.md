---
format: 1080x1920
duration: 45s
message: "商品写真に、使っているところが分かる1枚を足す"
arc: diagnosis-then-fix
audience: "商品写真を自分で撮る一人EC・ハンドメイド販売者"
mode: autonomous
music: none
---

## Frame 1 — 物だけで終わっている

- scene: 商品カードが3枚並び、どれも机の上の物だけ。買い手のシルエットが手前で止まる
- duration: 9.23s
- poster: 4s
- transition_in: cut
- status: outline
- voiceover: "商品写真が、机の上で撮ったものだけになっていませんか。買う人は、それを自分が持ったところまで想像できていません。"
- src: compositions/frames/01-hook.html
- type: hook
- persuasion: Rhetorical question
- beat: Curiosity
- blueprint: kinetic-type

narrativeRole: 欠落だけを名指しし、直し方は伏せる。
keyMessage: 物だけの写真は、買い手の想像を助けていない。

### 時間割り
- 0.0-1.4 見出し「机の上の物だけ」が下から入る
- 1.4-4.2 商品カード3枚が左から順に立ち上がる(0.28s stagger)
- 4.2-6.4 3枚とも同じ構図であることを示すラベルが出る
- 6.4-9.23 買い手のシルエットが手前に入り、止まる

## Frame 2 — 最後に迷う二つ

- scene: 濃い青の面。中央に空の答え欄が二つ、「大きさ」「似合うか」。物だけの写真はどちらも埋められない
- duration: 14.90s
- poster: 7s
- transition_in: crossfade
- status: outline
- voiceover: "一覧を見た人が最後に迷うのは、大きさと、自分に似合うかどうかの二つです。物だけの写真は、そのどちらにも答えていません。だから、よさそうだけど分からない、のところで止まります。"
- src: compositions/frames/02-gap.html
- type: pain_point
- persuasion: Progressive disclosure
- beat: Recognition
- blueprint: zoom-reveal

narrativeRole: 止まる理由を二つに絞って言語化する。
keyMessage: 迷いは大きさと似合うかの二点。物だけの写真はどちらにも答えない。

### 時間割り
- 0.0-2.2 見出し「最後に迷うのは二つ」
- 2.2-5.0 答え欄01「大きさ」が左から
- 5.0-7.8 答え欄02「似合うか」が右から
- 7.8-11.0 二つの欄に斜線が入り、未回答であることを示す
- 11.0-14.90 下段に「よさそう、だけど分からない」が残る

## Frame 3 — 1枚足す

- scene: クリーム地。写真枠の中に商品と手が入り、大きさが伝わる。右上に黄色の「＋1」
- duration: 14.04s
- poster: 7s
- transition_in: cut
- status: outline
- voiceover: "使っているところを一枚足します。身につけるものなら着けた状態、置くものなら置いた部屋。手が写り込むだけでも大きさは伝わります。モデルは要りません。自分の手で足ります。"
- src: compositions/frames/03-fix.html
- type: solution
- persuasion: Concrete instruction
- beat: Relief
- blueprint: build-up

narrativeRole: 手順を一つに絞り、実行の障壁を下げる。
keyMessage: 使用シーンを1枚。手が写るだけで足り、モデルは要らない。

### 時間割り
- 0.0-2.0 見出し「使っているところを1枚」
- 2.0-4.6 写真枠が立ち上がり、商品が入る
- 4.6-7.4 手のシルエットが下から入り、商品の隣に並ぶ
- 7.4-10.2 「＋1」が黄色で弾んで出る
- 10.2-14.04 下段に「モデルは要らない。自分の手で足りる」

## Frame 4 — 一本に一つずつ

- scene: 濃い青の面。チャンネルの約束を一行で置く
- duration: 6.85s
- poster: 3s
- transition_in: crossfade
- status: outline
- voiceover: "一人でネットショップを回す人が、決めるだけで終わることを、一本に一つずつ出しています。"
- src: compositions/frames/04-cta.html
- type: cta
- persuasion: Series promise
- beat: Commitment

narrativeRole: 単発の答えではなく続きがあることを示す。
keyMessage: 決めるだけで終わることを、一本に一つずつ。

## Video direction

- 色は frame.md の canvas/ink/accent のみ。クリーム #f6f1e8 と青 #1534c5 を面で交互に使い、フレームの切り替わりを色で分からせる
- 図版はすべてCSS作図。実在ブランド・実在の商品画像・顔は使わない
- 文字は Noto Sans JP のウェイト800を主、支えの一文は400
- 各フレームは音声の尺いっぱいまで展開を続ける。冒頭で全部出して固まらせない
- ルート直下に2つのCTAクリップを置く。13.5秒に midpoint-lp、38.163秒から end-subscribe
