# CODEMAP

## Structure

```text
ec-hitori-tools/
├── articles/             # Markdown原稿と生成済み補足ノートHTML
├── tests/                # Python/JavaScriptテスト
├── build.py              # トップ・固定4ページの生成
├── articles_build.py     # 補足ノートのHTML生成
├── tools.json            # 掲載ツールと遷移先
├── videos.json           # トップ掲載YouTube動画
├── affiliate.config.json # 公開URL・sub-id設定
├── style.css             # 全ページ共通スタイル
├── track.js              # 動画slugを広告リンクへ付与
└── *.html                # GitHub Pages公開物
```

## Key files

- `build.py`: `index.html`、`operator.html`、`privacy.html`、`contact.html`、`disclaimer.html` を生成する。
- `articles_build.py`: `articles/*.md` を変換し、関連ツールと共通フッターを付ける。
- `videos.json`: 公開確認済み動画を新しい順で管理する。
- `style.css`: 白基調のトップ、動画カード、記事、固定ページを定義する。
- `tests/test_build.py`: トップ、動画、リンク、固定ページを検証する。
- `tests/test_articles.py`: Markdown変換と記事ページを検証する。

## Dependencies

```text
tools.json + videos.json + affiliate.config.json -> build.py -> index + fixed pages
articles/*.md + tools.json                       -> articles_build.py -> articles/*.html
articles_build.py                                -> build.render_cards/render_footer
all HTML                                         -> style.css
index/articles                                   -> track.js
```

## Entry points

- `python3 build.py`: トップと固定4ページを再生成。
- `python3 articles_build.py`: 補足ノートを再生成。
- `pytest`: Pythonテスト。
- `node tests/track.test.js`: JavaScriptテスト。

## Environment variables

- なし。公開URLとsub-id名は `affiliate.config.json` で管理する。

## 保留中の変更

### BudouX(日本語改行整形)のビルド時適用 — 2026-08-23保留

`build.py` を次に編集するときに同梱する。単独タスクとしては着手しない(LP流入がまだ積まれていないため、単体で時間を取る価値がない)。

- 方式: `pip install budoux` してビルド時にZWSP(U+200B)を埋め込む。CDNもクライアントJSも使わない
- 対象: 日本語見出し(`<h1>`/`<h2>`)。スマホ幅で不自然な位置に折れるのを防ぐ
- 合格基準: `python3 -c "import budoux; print(budoux.load_default_japanese_parser().parse('開業から最初の1件が売れるまで、24項目'))"` が意味の切れ目で分割する、かつiPhone実機幅で見出しの折れ位置が改善する
- 停止条件: ビルド時間が体感で伸びる、またはBudouXの既知issue(iOSで数字が`tel:`リンク化する)が自サイトで再現する
- 未確認: ZWSP混入時のブラウザ内検索・コピペ・SEOの扱い。見出しに入れる場合はテストページで実測する
