#!/usr/bin/env python3
"""記事(articles/*.md)を静的HTMLへ変換する。

依存ゼロ方針を守るため Markdown は自前のミニパーサで処理する。
対応記法: 見出し(##/###)、段落、箇条書き(-)、番号リスト(1.)、太字(**)、
リンク([]())、表(| |)、水平線(---)。生のHTMLはエスケープする(XSS/事故防止)。
記事末尾には関連ツールカード(build.render_cards 再利用)を差し込み、収益導線にする。
"""

from __future__ import annotations

import glob
import html
import json
import os
import re

from build import render_cards

HERE = os.path.dirname(os.path.abspath(__file__))


def parse_front_matter(raw: str) -> tuple[dict, str]:
    """先頭の `---` frontmatter を dict に、残りを本文文字列にして返す。"""
    meta: dict = {}
    body = raw
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end != -1:
            header = raw[3:end].strip("\n")
            body = raw[end + 4:]
            for line in header.splitlines():
                if ":" not in line:
                    continue
                key, _, val = line.partition(":")
                key = key.strip()
                val = val.strip()
                if key == "tools":
                    meta[key] = [t.strip() for t in val.split(",") if t.strip()]
                else:
                    meta[key] = val
    return meta, body


def _inline(text: str) -> str:
    """インライン記法(エスケープ → 太字 → リンク)を適用する。"""
    out = html.escape(text)
    # リンク [label](url) — url は href 用にクォートエスケープ済みの素材を使う
    def link_sub(m: re.Match) -> str:
        label, url = m.group(1), m.group(2)
        safe_url = html.escape(url, quote=True)
        return f'<a href="{safe_url}" target="_blank" rel="nofollow sponsored noopener">{label}</a>'
    out = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_sub, out)
    # 太字 **text**
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    return out


def md_to_html(md: str) -> str:
    """ミニ Markdown を HTML へ変換する。"""
    lines = md.split("\n")
    html_parts: list[str] = []
    i = 0
    n = len(lines)
    para: list[str] = []

    def flush_para() -> None:
        if para:
            html_parts.append(f"<p>{_inline(' '.join(para))}</p>")
            para.clear()

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            flush_para()
            i += 1
            continue

        # 水平線
        if re.fullmatch(r"-{3,}", stripped):
            flush_para()
            html_parts.append("<hr>")
            i += 1
            continue

        # 見出し
        m = re.match(r"(#{2,4})\s+(.*)", stripped)
        if m:
            flush_para()
            level = len(m.group(1))
            html_parts.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # 表(| ... | で始まり、次行が区切り | --- |)
        if stripped.startswith("|") and i + 1 < n and re.match(r"\s*\|[\s:|-]+\|", lines[i + 1]):
            flush_para()
            header_cells = [c.strip() for c in stripped.strip("|").split("|")]
            rows = []
            i += 2  # ヘッダ行 + 区切り行
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            thead = "".join(f"<th>{_inline(c)}</th>" for c in header_cells)
            tbody = "".join(
                "<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>" for r in rows
            )
            html_parts.append(f"<table><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table>")
            continue

        # 箇条書き
        if re.match(r"-\s+", stripped):
            flush_para()
            items = []
            while i < n and re.match(r"-\s+", lines[i].strip()):
                items.append(re.sub(r"-\s+", "", lines[i].strip(), count=1))
                i += 1
            lis = "".join(f"<li>{_inline(it)}</li>" for it in items)
            html_parts.append(f"<ul>{lis}</ul>")
            continue

        # 番号リスト
        if re.match(r"\d+\.\s+", stripped):
            flush_para()
            items = []
            while i < n and re.match(r"\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"\d+\.\s+", "", lines[i].strip(), count=1))
                i += 1
            lis = "".join(f"<li>{_inline(it)}</li>" for it in items)
            html_parts.append(f"<ol>{lis}</ol>")
            continue

        # 通常段落
        para.append(stripped)
        i += 1

    flush_para()
    return "\n".join(html_parts)


def build_articles(articles_dir: str, tools_data: dict, cfg: dict) -> list[str]:
    """articles_dir 配下の *.md を読み、同ディレクトリに *.html を書き出す。書き出したパス一覧を返す。"""
    written: list[str] = []
    for md_path in sorted(glob.glob(os.path.join(articles_dir, "*.md"))):
        with open(md_path, encoding="utf-8") as f:
            raw = f.read()
        meta, body = parse_front_matter(raw)
        body_html = md_to_html(body)
        page = render_article_page(meta, body_html, tools_data, cfg)

        slug = meta.get("slug") or os.path.splitext(os.path.basename(md_path))[0]
        out_path = os.path.join(articles_dir, f"{slug}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(page)
        written.append(out_path)
    return written


def render_article_page(meta: dict, body_html: str, tools_data: dict, cfg: dict) -> str:
    """記事1本の完全な HTML ページを返す(末尾に関連ツールカード)。"""
    title = html.escape(meta.get("title", ""))
    desc = html.escape(meta.get("description", ""), quote=True)
    site = html.escape(cfg.get("site_base_url", ""), quote=True)
    date = html.escape(meta.get("date", ""))

    # 関連ツールカード(meta.tools の id に一致するものだけ)
    want = set(meta.get("tools", []))
    related = [t for t in tools_data.get("tools", []) if t.get("id") in want]
    cards_html = render_cards(related, cfg) if related else ""
    related_section = (
        f'''    <section class="related">
      <h2>この記事で紹介したツール</h2>
      <div class="grid">
{cards_html}
      </div>
      <p class="disclosure">※ 当ページのリンクには広告(アフィリエイト)を含みます。</p>
    </section>''' if related else ""
    )

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} | EC一人社長 Tips</title>
  <meta name="description" content="{desc}">
  <meta property="og:title" content="{title}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{site}articles/{html.escape(meta.get('slug',''), quote=True)}.html">
  <link rel="stylesheet" href="../style.css">
</head>
<body>
  <header class="hero">
    <p class="kicker"><a href="../index.html">← EC一人社長 Tips</a></p>
    <h1>{title}</h1>
    <p class="date">{date}</p>
  </header>

  <main>
    <article class="post">
{body_html}
    </article>
{related_section}
  </main>

  <footer>
    <p>EC一人社長 Tips</p>
  </footer>

  <script src="../track.js"></script>
</body>
</html>
'''


def main() -> None:
    with open(os.path.join(HERE, "tools.json"), encoding="utf-8") as f:
        tools_data = json.load(f)
    with open(os.path.join(HERE, "affiliate.config.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    written = build_articles(os.path.join(HERE, "articles"), tools_data, cfg)
    for path in written:
        print(f"built {path}")
    print(f"built {len(written)} article(s)")


if __name__ == "__main__":
    main()
