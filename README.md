# ec-hitori-tools

YouTube連動サイト「ひとりネットショップ研究所」の**収益変換部**。視聴者を最新動画・補足ノート・おすすめツールに案内し、
アフィリエイトリンクへ送る。**どの動画が成約させたか**が ASP 管理画面で分かるよう、
動画別 sub-id を自動付与する。バックエンド不要・GitHub Pages で動く。

## 仕組み

```
YouTube動画 概要欄
  → https://interhiro.github.io/ec-hitori-tools/?v=<動画スラッグ>
      → LP(おすすめツール一覧)
          → 各アフィリンクに ?id1=<動画スラッグ> を自動付与(track.js)
              → ASP 管理画面の sub-id 別レポートで「成約した動画」が判明
```

- `tools.json` — 掲載ツール(名前・カテゴリ・紹介文・公式URL・アフィURL)
- `videos.json` — トップに掲載する公開確認済みYouTube動画（新しい順）
- `affiliate.config.json` — アフィ口座ID(**ここが唯一の要設定**)
- `measurement.config.json` — LPイベントをGA4へ送る公開用設定（ID未設定時は**未観測**）
- `build.py` — データからトップと運営者・ポリシー4ページを生成
- `track.js` — `?v=` を読みアフィリンクに sub-id を付与(完全クライアントサイド)
- `articles_build.py` — 動画の補足ノートをMarkdownから生成
- `style.css` / `*.html` — GitHub Pages公開物

`affiliate_url` が空のツールは公式URLにフォールバックし、`data-monetized="false"` が付く
(= まだ1円も生まない状態が一目で分かる)。

## ビルド

```sh
python3 build.py        # トップ + 運営者・ポリシー4ページ
python3 articles_build.py  # 補足ノートHTML
python3 -m pytest -q    # build ロジックのテスト
node tests/track.test.js  # トラッキングのテスト
```

## LPイベント計測

`track.js` は、流入URLの `source_id`（なければ従来の `v`）と安全なページパスだけを添えて、次のイベントを送ります。任意のURLクエリ文字列はGA4へ送信しません。

- `lp_view` — LPを表示した
- `affiliate_click` — アフィリエイトリンクを開いた
- `list_signup` — 先行案内リストのGoogleフォームを開いた（フォーム送信の完了自体は、GitHub Pagesからは観測できない）

既存の `?v=ec-tips-09` のようなURLは、引き続きA8の `id1=ectips09` に変換されます。Short経由など、より細かい流入元を分けるときは、`?v=ec-tips-09&source_id=yt_short_photo_aar5wmqvi0` のように両方を付けます。

GA4の `G-...` IDは推測・自動作成しません。`measurement.config.json` が空の現在はイベントが**未観測**であり、ゼロ件を意味しません。観測を有効にする一回限りの作業は、既存または新規のGA4プロパティで `https://interhiro.github.io/ec-hitori-tools/` 用Webデータストリームを選び、その公開Measurement IDを同設定ファイルに入れてデプロイすることです。流入別に集計するには、同じGA4プロパティで `source_id` をイベントスコープのカスタムディメンションとして登録します。

## 【運営者の要設定】これが済むまで収益はゼロ(2つだけ)

このLPは「配管」。**流すもの(口座)と流れ(チャンネル公開)が無いと1円も生まない。**
さっき止めた Pillar C の二の舞にしないため、収益化の鍵は以下の人間タスクに集約してある。

### 1. アフィリエイト口座を登録し、リンクを貼る(各15分)
- もしもアフィリエイト / Amazon Associates / A8.net 等に登録 → 審査通過
- 各ツールの提携リンクを取得し、`tools.json` の該当 `affiliate_url` に貼る
  - もしも/Amazon でトラッキングIDを使う場合は `affiliate.config.json` の `networks` にIDを入れる
- `python3 build.py` を再実行 → `data-monetized="true"` になる

### 2. YouTube動画を公開し、概要欄に下記リンクを貼る
動画ごとにスラッグを変える(これが A8 の id1 / sub-id になる):
```
▼ 動画で紹介したツールはこちら
https://interhiro.github.io/ec-hitori-tools/?v=ec-tips-01
```
2本目は `?v=ec-tips-02`、テーマ別なら `?v=base-hikaku` のように。
→ ASP管理画面の sub-id 別成果で「どの動画が稼いだか」が分かり、当たり動画に寄せられる。

## デプロイ(GitHub Pages)

`main` の `index.html` / `style.css` / `track.js` をルートから配信。
Settings → Pages → Source: `main` / root。
