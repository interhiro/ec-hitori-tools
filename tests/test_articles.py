import os

from articles_build import build_articles, parse_front_matter, md_to_html, render_article_page

CFG = {"subid_param": "utm_content", "site_base_url": "https://x.github.io/"}
TOOLS = {
    "tools": [
        {"id": "base", "name": "BASE", "category": "EC", "blurb": "b",
         "official_url": "https://thebase.com/", "affiliate_url": ""},
    ]
}


def test_parse_front_matter_splits_meta_and_body():
    raw = "---\ntitle: テスト記事\nslug: test\ntools: base, shopify\n---\n\n本文です。\n"
    meta, body = parse_front_matter(raw)
    assert meta["title"] == "テスト記事"
    assert meta["slug"] == "test"
    assert meta["tools"] == ["base", "shopify"]
    assert body.strip() == "本文です。"


def test_md_to_html_headings_and_paragraphs():
    out = md_to_html("## 見出し\n\n段落テキスト\n")
    assert "<h2>見出し</h2>" in out
    assert "<p>段落テキスト</p>" in out


def test_md_to_html_bullet_list():
    out = md_to_html("- 一つ目\n- 二つ目\n")
    assert "<ul>" in out and "<li>一つ目</li>" in out and "<li>二つ目</li>" in out


def test_md_to_html_bold_and_link():
    out = md_to_html("これは**太字**と[リンク](https://example.com)です\n")
    assert "<strong>太字</strong>" in out
    assert '<a href="https://example.com"' in out


def test_md_to_html_table():
    md = "| 名前 | 料金 |\n| --- | --- |\n| BASE | 無料 |\n"
    out = md_to_html(md)
    assert "<table>" in out
    assert "<th>名前</th>" in out
    assert "<td>BASE</td>" in out


def test_md_to_html_escapes_raw_html():
    out = md_to_html("危険 <script>alert(1)</script>\n")
    assert "<script>" not in out
    assert "&lt;script&gt;" in out


def test_render_article_page_is_full_doc_with_tool_cards():
    meta = {"title": "記事タイトル", "slug": "test", "description": "説明",
            "date": "2026-06-13", "tools": ["base"]}
    html_out = render_article_page(meta, "<p>本文</p>", TOOLS, CFG)
    assert html_out.strip().startswith("<!DOCTYPE html>")
    assert "記事タイトル" in html_out
    assert "track.js" in html_out          # トラッキング有効
    assert 'class="card"' in html_out       # 関連ツールカードが末尾に入る
    assert "BASE" in html_out
    assert "アフィリエイト" in html_out      # 開示文


def test_build_articles_writes_html_per_markdown_file(tmp_path):
    articles_dir = tmp_path / "articles"
    articles_dir.mkdir()
    (articles_dir / "sample.md").write_text(
        "---\ntitle: サンプル記事\nslug: sample\ndescription: 説明\ndate: 2026-07-13\ntools: base\n---\n\n本文。\n",
        encoding="utf-8",
    )

    written = build_articles(str(articles_dir), TOOLS, CFG)

    assert len(written) == 1
    out_path = articles_dir / "sample.html"
    assert out_path.exists()
    assert str(out_path) in written
    content = out_path.read_text(encoding="utf-8")
    assert "サンプル記事" in content
    assert 'class="card"' in content


def test_build_articles_skips_md_without_slug_gracefully(tmp_path):
    articles_dir = tmp_path / "articles"
    articles_dir.mkdir()
    (articles_dir / "noslug.md").write_text(
        "---\ntitle: スラッグなし\n---\n\n本文。\n", encoding="utf-8"
    )

    written = build_articles(str(articles_dir), TOOLS, CFG)

    # slug未指定時はファイル名(拡張子抜き)をslugとして使う
    out_path = articles_dir / "noslug.html"
    assert out_path.exists()
    assert str(out_path) in written
