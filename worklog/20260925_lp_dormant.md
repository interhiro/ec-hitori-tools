# LP休止（下書き保持）— 2026-09-25

YouTube「ひとりネットショップ研究所」の停止にともない、収益変換部のLPを休止する。
**削除ではなく休止。** ソースは全て残し、コマンド1回で復旧できる状態を保つ。

## 何をしたか

`build.py` / `articles_build.py` の**生成物だけ**をリポジトリから外した。

| 外したもの | 種別 |
|---|---|
| `index.html` | build.py 生成 |
| `sitemap.xml` | build.py 生成 |
| `robots.txt` | build.py 生成 |
| `operator.html` `privacy.html` `contact.html` `disclaimer.html` `checklist.html` | build.py 生成 |
| `articles/*.html`（6本） | articles_build.py 生成 |

**この8ファイル＋記事6本は、すべて生成物であることを実測で確認した。**
退避 → `build.py` 実行 → 復活、`git status` 差分ゼロ（バイト単位で一致）。

## 残したもの（＝下書き。これがあれば完全に戻る）

- `build.py` `articles_build.py` — ジェネレーター
- `articles/*.md`（6本） — 記事の原稿
- `tools.json` — 掲載ツールとアフィリリンク（**A8提携3件のURLを含む**）
- `videos.json` `affiliate.config.json` `measurement.config.json`
- `style.css` `track.js` — スタイルと計測
- `tests/` — 全テスト
- `videos/` — HyperFrames合成一式（LPとは別系統。無関係につき手を触れていない）
- `google3c5717818d1af74a.html` — **Search Console 認証ファイル。意図的に残した。**
  削除すると再開時に所有権の再認証が必要になる。1ファイル配信されるだけで実害はない。

## 再開の手順

```sh
cd ec-hitori-tools
python3 build.py
python3 articles_build.py
git add -A && git commit -m "feat: LPを再開する" && git push
```

これだけで、休止前とバイト単位で同一のサイトが戻る。**内容の劣化は無い。**

## 休止時点の状態（再開判断の材料）

| 項目 | 状態 |
|---|---|
| A8提携 | **3件成立**（BASE / カラーミーショップ / minne）。2026-09-09にEPC・確定率まで確定 |
| 未設定 | freee会計 / ラクスル / Canva Pro（freeeは着地先が誤りのため9/9に撤去済み） |
| GA4 | `G-M8MXQJLYFS` 設定済み。`measurement.config.json` に保持 |
| Search Console | 2026-09-09 認証ファイル設置済み |
| 記事 | 6本。うち2本は競合5.3/8.7の低競合キーワード狙い |

## 休止によって止まること

1. **A8提携3件の収益機会** — ページが無いのでクリックが発生しない
2. **記事6本のSEO蓄積** — 検索流入はYouTubeと独立に効くため、動画停止とは別に失われる
3. **GA4のLPイベント** — 配信ページが無いため発火しない

再開すれば1と3は即座に戻る。2はインデックスの再獲得に時間がかかる。

## 運用者の作業（このリポジトリの外）

- **GitHub Pages の停止** — Settings → Pages → Source を None に。
  （リポジトリ側の生成物を外しただけでは、Pages自体は有効のまま404を返す状態になる）
- **市場接触台帳への記帳** — `~/projects/shimayama-ops/state/market_contact_ledger.csv`。
  `CLAUDE.md` に「記帳していない公開は市場接触として存在しない扱いになる」とあり、
  LP変更も記帳対象。state/ はgit管理外のためこのセッションからは書き込めない。
- **A8への申告** — 提携先によっては掲載サイトの停止申告が要る場合がある。要確認。
