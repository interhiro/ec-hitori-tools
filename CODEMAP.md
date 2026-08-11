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
