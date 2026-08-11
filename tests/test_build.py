import json
import os
import re

from build import (
    build_html,
    render_footer,
    render_policy_pages,
    render_video_cards,
    resolve_link,
    render_cards,
)

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


def test_render_video_cards_links_public_youtube_video():
    out = render_video_cards([
        {"id": "abc123", "title": "テスト動画", "topic": "価格設計"},
    ])
    assert "https://www.youtube.com/watch?v=abc123" in out
    assert "https://i.ytimg.com/vi/abc123/hqdefault.jpg" in out
    assert "テスト動画" in out


def test_build_html_prioritizes_videos_before_tools():
    videos = {"videos": [{"id": "abc123", "title": "最新動画", "topic": "実務"}]}
    out = build_html(FIX_TOOLS, FIX_CFG, videos_data=videos)
    assert out.index("最新動画") < out.index("動画で触れた、運営に役立つツール")
    assert "ひとりネットショップ研究所" in out


def test_footer_links_to_all_review_readiness_pages():
    out = render_footer()
    for path in ("operator.html", "privacy.html", "contact.html", "disclaimer.html"):
        assert f'href="{path}"' in out
    assert "運営：" not in out


def test_footer_supports_article_relative_paths():
    out = render_footer("../")
    assert 'href="../operator.html"' in out
    assert 'href="../disclaimer.html"' in out


def test_policy_pages_omit_operator_identity_and_keep_contact_form():
    pages = render_policy_pages()
    assert set(pages) == {"operator.html", "privacy.html", "contact.html", "disclaimer.html"}
    assert "<dt>運営者</dt>" not in pages["operator.html"]
    assert "forms.gle/Uy3kPUrg5xcnqcSy6" in pages["contact.html"]
    assert "アフィリエイトプログラム" in pages["disclaimer.html"]


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


def test_render_article_links_orders_by_date_desc(tmp_path):
    """コラム一覧は date の新しい順に並ぶ(slug のアルファベット順ではない)。"""
    import build

    # ファイル名のアルファベット順(a-old → z-new)が日付順(z-new → a-old)と逆になるよう置く
    (tmp_path / "a-old.md").write_text(
        "---\ntitle: 古い記事\ndate: 2026-07-13\nslug: a-old\n---\n\n本文\n", encoding="utf-8"
    )
    (tmp_path / "z-new.md").write_text(
        "---\ntitle: 新しい記事\ndate: 2026-08-08\nslug: z-new\n---\n\n本文\n", encoding="utf-8"
    )

    out = build.render_article_links(str(tmp_path))
    assert out.index("新しい記事") < out.index("古い記事")


def test_render_article_links_handles_missing_date(tmp_path):
    """date 欠落の記事があっても例外を出さず、日付付きの記事より後ろに並ぶ。"""
    import build

    # ファイル名順では undated が先に来るが、日付ありが先に並ぶべき
    (tmp_path / "undated.md").write_text(
        "---\ntitle: 日付なし\nslug: undated\n---\n\n本文\n", encoding="utf-8"
    )
    (tmp_path / "zdated.md").write_text(
        "---\ntitle: 日付あり\ndate: 2026-01-01\nslug: zdated\n---\n\n本文\n", encoding="utf-8"
    )

    out = build.render_article_links(str(tmp_path))
    assert out.index("日付あり") < out.index("日付なし")


def test_generated_pages_expose_no_operator_identity_fields():
    """運営者を特定する項目を公開ページに一切置かない。

    2026-08-11の指示: 個人名・屋号・法人名は同格に扱い、公開しない。
    アフィリエイトのみのサイトに特定商取引法の表示義務はないため
    （義務を負うのは販売業者・役務提供事業者）、載せる法的理由がない。

    禁止語そのものをこのファイルに書くと、公開リポジトリに氏名を
    commit することになる。だから語ではなく「構造」を検査する。
    運営主体を名乗る項目が存在しないことを見る。
    """
    joined = "".join(render_policy_pages().values()) + render_footer()
    for label in ("<dt>運営者</dt>", "<dt>運営責任者</dt>", "運営：", "運営者名"):
        assert label not in joined, f"運営主体を名乗る項目が残っている: {label}"


def test_operator_page_rows_are_limited_to_the_approved_set():
    """運営者情報ページの項目を承認済みの3つに固定する。

    項目が増えるときは必ず本人確認を通すため、集合一致で固定する。
    """
    rows = set(re.findall(r"<dt>([^<]+)</dt>", render_policy_pages()["operator.html"]))
    assert rows == {"サイト名", "発信内容", "お問い合わせ"}
