import json
import os

from build import resolve_link, render_cards, build_html

FIX_TOOLS = {
    "tools": [
        {"id": "base", "name": "BASE", "category": "EC", "blurb": "b",
         "official_url": "https://thebase.com/", "affiliate_url": ""},
        {"id": "canva", "name": "Canva", "category": "Design", "blurb": "c",
         "official_url": "https://canva.com/", "affiliate_url": "https://aff.example/canva?id=X"},
    ]
}
FIX_CFG = {"subid_param": "utm_content", "site_base_url": "https://x.github.io/"}


def test_resolve_link_falls_back_to_official_when_no_affiliate():
    t = FIX_TOOLS["tools"][0]
    url, monetized = resolve_link(t, FIX_CFG)
    assert url == "https://thebase.com/"
    assert monetized is False


def test_resolve_link_uses_affiliate_when_present():
    t = FIX_TOOLS["tools"][1]
    url, monetized = resolve_link(t, FIX_CFG)
    assert url == "https://aff.example/canva?id=X"
    assert monetized is True


def test_render_cards_marks_unmonetized_tools():
    html = render_cards(FIX_TOOLS["tools"], FIX_CFG)
    # 収益化されていないツールには data-monetized="false" が付く(運用者が一目で分かる)
    assert 'data-monetized="false"' in html
    assert 'data-monetized="true"' in html
    assert "BASE" in html and "Canva" in html


def test_render_cards_embeds_subid_param_for_tracking():
    html = render_cards(FIX_TOOLS["tools"], FIX_CFG)
    # track.js が ?v= を読んで付与する先のパラメータ名がカードに埋まっている
    assert 'data-subid-param="utm_content"' in html


def test_build_html_is_complete_document():
    html = build_html(FIX_TOOLS, FIX_CFG)
    assert html.strip().startswith("<!DOCTYPE html>")
    assert "track.js" in html
    assert "EC" in html  # category appears


def test_build_html_includes_article_links_when_articles_dir_given(tmp_path):
    articles_dir = tmp_path / "articles"
    articles_dir.mkdir()
    (articles_dir / "sample.md").write_text(
        "---\ntitle: サンプルコラム\nslug: sample\n---\n\n本文\n", encoding="utf-8"
    )

    out = build_html(FIX_TOOLS, FIX_CFG, articles_dir=str(articles_dir))

    assert "サンプルコラム" in out
    assert "articles/sample.html" in out


def test_build_html_omits_article_section_when_no_articles(tmp_path):
    articles_dir = tmp_path / "articles"
    articles_dir.mkdir()

    out = build_html(FIX_TOOLS, FIX_CFG, articles_dir=str(articles_dir))

    assert "コラム" not in out


def test_build_html_backward_compatible_without_articles_dir():
    out = build_html(FIX_TOOLS, FIX_CFG)
    assert "コラム" not in out
