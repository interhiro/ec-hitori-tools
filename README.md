# ec-hitori-tools

YouTube「EC一人社長 Tips」の**収益変換部**。視聴者を1枚のおすすめツールLPに集め、
アフィリエイトリンクへ送る。**どの動画が成約させたか**が ASP 管理画面で分かるよう、
動画別 sub-id を自動付与する。バックエンド不要・GitHub Pages で動く。

## 仕組み

```
YouTube動画 概要欄
  → https://interhiro.github.io/ec-hitori-tools/?v=<動画スラッグ>
      → LP(おすすめツール一覧)
          → 各アフィリンクに ?utm_content=<動画スラッグ> を自動付与(track.js)
              → ASP 管理画面の sub-id 別レポートで「成約した動画」が判明
```

- `tools.json` — 掲載ツール(名前・カテゴリ・紹介文・公式URL・アフィURL)
- `affiliate.config.json` — アフィ口座ID(**ここが唯一の要設定**)
- `build.py` — 上記2つから `index.html` を生成
- `track.js` — `?v=` を読みアフィリンクに sub-id を付与(完全クライアントサイド)
- `style.css` / `index.html` — 公開物

`affiliate_url` が空のツールは公式URLにフォールバックし、`data-monetized="false"` が付く
(= まだ1円も生まない状態が一目で分かる)。

## ビルド

```sh
python3 build.py        # tools.json + affiliate.config.json → index.html
python3 -m pytest -q    # build ロジックのテスト
node tests/track.test.js  # トラッキングのテスト
```

## 【島山の要設定】これが済むまで収益はゼロ(2つだけ)

このLPは「配管」。**流すもの(口座)と流れ(チャンネル公開)が無いと1円も生まない。**
さっき止めた Pillar C の二の舞にしないため、収益化の鍵は以下の人間タスクに集約してある。

### 1. アフィリエイト口座を登録し、リンクを貼る(各15分)
- もしもアフィリエイト / Amazon Associates / A8.net 等に登録 → 審査通過
- 各ツールの提携リンクを取得し、`tools.json` の該当 `affiliate_url` に貼る
  - もしも/Amazon でトラッキングIDを使う場合は `affiliate.config.json` の `networks` にIDを入れる
- `python3 build.py` を再実行 → `data-monetized="true"` になる

### 2. 「EC一人社長 Tips」チャンネルで動画を公開し、概要欄に下記リンクを貼る
動画ごとにスラッグを変える(これが sub-id になる):
```
▼ 動画で紹介したツールはこちら
https://interhiro.github.io/ec-hitori-tools/?v=ec-tips-01
```
2本目は `?v=ec-tips-02`、テーマ別なら `?v=base-hikaku` のように。
→ ASP管理画面の sub-id 別成果で「どの動画が稼いだか」が分かり、当たり動画に寄せられる。

## デプロイ(GitHub Pages)

`main` の `index.html` / `style.css` / `track.js` をルートから配信。
Settings → Pages → Source: `main` / root。
