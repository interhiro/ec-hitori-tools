#!/usr/bin/env python3
"""tools.json + affiliate.config.json から静的LP(index.html)を生成する。

設計:
- アフィリンク(affiliate_url)が空のツールは official_url にフォールバックし、
  data-monetized="false" を付ける(運用者が未収益化を一目で把握できる)。
- 各リンクには data-subid-param を埋め、ブラウザ側の track.js が
  ?v=<動画ID> を読んで sub-id として付与する(どの動画が成約させたかを ASP 管理画面で追える)。
- バックエンド不要。GitHub Pages にそのまま乗る。
"""

from __future__ import annotations

import glob
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def render_article_links(articles_dir: str) -> str:
    """articles_dir 配下の *.md からタイトル/スラッグを読み、コラムへのリンク一覧を返す(0件なら空文字列)。"""
    from articles_build import parse_front_matter

    items = []
    for md_path in sorted(glob.glob(os.path.join(articles_dir, "*.md"))):
        with open(md_path, encoding="utf-8") as f:
            raw = f.read()
        meta, _ = parse_front_matter(raw)
        slug = meta.get("slug") or os.path.splitext(os.path.basename(md_path))[0]
        title = meta.get("title", slug)
        items.append((slug, title))

    if not items:
        return ""

    lis = "".join(
        f'<li><a href="articles/{html.escape(slug, quote=True)}.html">{html.escape(title)}</a></li>'
        for slug, title in items
    )
    return f'''    <section class="columns">
      <h2>コラム</h2>
      <ul>
{lis}
      </ul>
    </section>
'''


def resolve_link(tool: dict, cfg: dict) -> tuple[str, bool]:
    """ツールの遷移先URLと、収益化済みかどうかを返す。"""
    aff = (tool.get("affiliate_url") or "").strip()
    if aff:
        return aff, True
    return tool.get("official_url", "").strip(), False


def render_cards(tools: list[dict], cfg: dict) -> str:
    subid_param = cfg.get("subid_param", "utm_content")
    cards = []
    for t in tools:
        url, monetized = resolve_link(t, cfg)
        name = html.escape(t.get("name", ""))
        category = html.escape(t.get("category", ""))
        blurb = html.escape(t.get("blurb", ""))
        href = html.escape(url, quote=True)
        cards.append(
            f'''      <article class="card" data-monetized="{str(monetized).lower()}">
        <span class="cat">{category}</span>
        <h3>{name}</h3>
        <p>{blurb}</p>
        <a class="cta" href="{href}" target="_blank" rel="nofollow sponsored noopener"
           data-base-href="{href}" data-subid-param="{html.escape(subid_param, quote=True)}">
          {name} を見る →
        </a>
      </article>'''
        )
    return "\n".join(cards)


def build_html(tools_data: dict, cfg: dict, articles_dir: str | None = None) -> str:
    tools = tools_data.get("tools", [])
    cards_html = render_cards(tools, cfg)
    site = html.escape(cfg.get("site_base_url", ""), quote=True)
    columns_html = render_article_links(articles_dir) if articles_dir else ""
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EC一人社長のおすすめツール</title>
  <meta name="description" content="一人でECを回す社長が、時間を増やさず売上を伸ばすために使っているツールだけを厳選。">
  <meta property="og:title" content="EC一人社長のおすすめツール">
  <meta property="og:url" content="{site}">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header class="hero">
    <h1>EC一人社長のおすすめツール</h1>
    <p>一人で店を回す社長が、<strong>時間を増やさず</strong>売上を伸ばすために使っている道具だけを厳選しました。</p>
  </header>

  <main>
    <section class="grid">
{cards_html}
    </section>
{columns_html}    <p class="disclosure">※ 当ページのリンクには広告(アフィリエイト)を含みます。</p>
  </main>

  <footer>
    <p>EC一人社長 Tips</p>
  </footer>

  <script src="track.js"></script>
</body>
</html>
'''


def main() -> None:
    with open(os.path.join(HERE, "tools.json"), encoding="utf-8") as f:
        tools_data = json.load(f)
    with open(os.path.join(HERE, "affiliate.config.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    out = build_html(tools_data, cfg, articles_dir=os.path.join(HERE, "articles"))
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
        f.write(out)
    monetized = sum(1 for t in tools_data.get("tools", []) if (t.get("affiliate_url") or "").strip())
    total = len(tools_data.get("tools", []))
    print(f"built index.html: {total} tools ({monetized} monetized, {total - monetized} pending affiliate_url)")


if __name__ == "__main__":
    main()
