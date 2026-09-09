import json
import os
import re

from build import (
    build_html,
    render_checklist_page,
    build_html,
    render_footer,
    render_policy_pages,
    render_video_cards,
    render_sitemap,
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


def test_render_cards_can_embed_a_default_source_for_article_tracking():
    html = render_cards(FIX_TOOLS["tools"], FIX_CFG, default_subid="article-opening")
    assert 'data-default-subid="article-opening"' in html


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


def test_sitemap_lists_the_homepage_and_dated_articles(tmp_path):
    (tmp_path / "opening.md").write_text(
        "---\ntitle: 開店\ndate: 2026-08-14\nslug: opening\n---\n\n本文\n",
        encoding="utf-8",
    )
    sitemap = render_sitemap("https://x.github.io/site/", str(tmp_path))
    assert "https://x.github.io/site/</loc>" in sitemap
    assert "https://x.github.io/site/articles/opening.html</loc><lastmod>2026-08-14</lastmod>" in sitemap


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


def test_checklist_page_is_generated_with_all_sections():
    """リスト登録の理由になる公開資産。動画10本の内容を1枚に畳んだもの。"""
    page = render_checklist_page(FIX_TOOLS_SLOTTED, FIX_CFG)
    for heading in ("開業前", "商品を決める", "ショップを作る", "商品ページ", "公開前", "公開後"):
        assert heading in page, heading
    assert page.count('class="check"') >= 20


def test_index_has_a_list_signup_with_a_working_form():
    """再生が増えてもリスト導線が無ければ Day60 の合格条件を満たせない。"""
    out = build_html(FIX_TOOLS, {"subid_param": "id1"})
    assert "先行案内" in out
    assert "docs.google.com/forms" in out
    assert 'data-list-signup="true"' in out
    # 2026-08-26: メール1項目の専用フォームに差し替え済み（旧: 問い合わせフォームのプリフィル転用）
    assert "1FAIpQLSePJWjEKIZovbTMl254cH8Kp4UWc2VQrwCt5cOpjcBQ6uGTqg" in out


def test_checklist_page_exposes_no_operator_identity():
    page = render_checklist_page(FIX_TOOLS_SLOTTED, FIX_CFG)
    for label in ("<dt>運営者</dt>", "<dt>運営責任者</dt>", "運営："):
        assert label not in page


def test_checklist_page_marks_the_list_form_for_measurement():
    assert 'data-list-signup="true"' in render_checklist_page(FIX_TOOLS_SLOTTED, FIX_CFG)


# --- 2026-09-09: checklist.html に収益導線と計測が無かった件の回帰テスト ---
# 発覚時の実測: grep -c "px.a8.net" checklist.html → 0 / track.js の読み込み → 無し。
# サイト内で最も購買意欲が高いページ（開業届・決済方法・特商法表記の章を持つ）に
# クリックできる場所が1つも無く、置いても計測されない状態だった。

FIX_TOOLS_SLOTTED = {
    "tools": [
        {"id": "base", "name": "BASE", "category": "ネットショップ開設", "blurb": "b",
         "official_url": "https://thebase.com/", "affiliate_url": "https://aff.example/base?x=1"},
        {"id": "freee", "name": "freee会計", "category": "会計", "blurb": "f",
         "official_url": "https://www.freee.co.jp/", "affiliate_url": "https://aff.example/freee?x=2"},
    ]
}


def test_checklist_page_loads_the_tracking_script():
    """track.js が無ければ affiliate_click も list_signup も発火しない。

    data-list-signup は以前から付いていたが、スクリプト自体が読まれていなかったため
    チェックリスト経由のリスト登録も計測されていなかった。
    """
    assert '<script src="track.js"></script>' in render_checklist_page(FIX_TOOLS_SLOTTED, FIX_CFG)


def test_checklist_page_places_monetized_links_in_section_context():
    """章の文脈に、その章で必要になる道具を置く。

    index.html のツールセクションは6枚並列で affiliate_click 0 だった。
    チェックリストは章ごとに「いま何をするか」が確定しているため章の直後に置く。
    """
    page = render_checklist_page(FIX_TOOLS_SLOTTED, FIX_CFG)
    links = re.findall(r'<a class="cta" href="([^"]+)"', page)
    assert len(links) == 2, f"収益導線が {len(links)} 本: {links}"
    # track.js は a.cta[data-base-href] だけを拾う
    assert page.count("data-base-href=") == len(links)
    # 章の見出しより後ろに置く（見出しの前に出すと文脈が壊れる）
    assert page.index("開業前") < page.index("aff.example/freee")
    assert page.index("ショップを作る") < page.index("aff.example/base")


def test_checklist_page_skips_tools_without_an_affiliate_url():
    """affiliate_url が空の道具を章に置くと、公式サイトへの無償送客になる。

    FIX_TOOLS の base は affiliate_url が空。リンクを出してはいけない。
    """
    page = render_checklist_page(FIX_TOOLS, FIX_CFG)
    hrefs = re.findall(r'<a class="cta" href="([^"]+)"', page)
    assert "https://thebase.com/" not in hrefs, f"未収益化の公式URLを置いている: {hrefs}"


def test_checklist_page_links_carry_the_sponsored_rel():
    """index.html のツールカードと同じ rel に揃える。"""
    page = render_checklist_page(FIX_TOOLS_SLOTTED, FIX_CFG)
    assert page.count('rel="nofollow sponsored noopener"') == page.count("data-base-href=")


def test_checklist_page_uses_its_own_subid_so_conversions_are_separable():
    """動画経由と検索経由の成果を ASP 側で切り分ける。

    articles_build.py が article-<slug> を使うのと同じ意図。
    """
    page = render_checklist_page(FIX_TOOLS_SLOTTED, FIX_CFG)
    assert 'data-default-subid="checklist"' in page
    # subid_param は cfg 由来。実運用は affiliate.config.json の "id1"(A8のパラメータ計測)
    assert 'data-subid-param="utm_content"' in page
    assert 'data-subid-param="id1"' in render_checklist_page(
        FIX_TOOLS_SLOTTED, {"subid_param": "id1"}
    )


def test_checklist_page_discloses_advertising():
    """リンクを置くなら広告表記を同じページに出す。"""
    page = render_checklist_page(FIX_TOOLS_SLOTTED, FIX_CFG)
    assert "広告" in page


def test_checklist_page_requires_tools_so_monetization_cannot_be_dropped_silently():
    """引数を省略できると、収益導線の無いページが黙って生成されうる。

    フォールバックで空のページを返す実装にはしない（失敗を隠さない）。
    """
    try:
        render_checklist_page()
    except TypeError:
        return
    raise AssertionError("引数なしで呼べてしまう。収益導線の欠落が黙って通る")


def test_index_hero_cta_leads_into_the_site_not_back_to_youtube():
    """YouTube の概要欄から来た人に、最初の選択肢として YouTube を出さない。

    発覚時: hero-cta が #latest-videos（動画グリッド＝各カードが youtube.com へ外部遷移）。
    """
    out = build_html(FIX_TOOLS, FIX_CFG)
    hero = re.search(r'<a class="hero-cta" href="([^"]+)"', out)
    assert hero, "hero-cta が見つからない"
    assert hero.group(1) == "checklist.html", f"hero-cta が {hero.group(1)} を指している"


# --- Search Console 認証ファイルのガード（2026-09-09） ---
# このファイルが消えるとプロパティの認証が外れ、検索パフォーマンスのデータが
# 取れなくなる。しかもサイト側は何のエラーも出さないため気づけない。

def test_search_console_verification_file_is_present():
    """GSC認証ファイルを消さない。

    プロパティは URLプレフィックス https://interhiro.github.io/ec-hitori-tools/ で、
    認証ファイルはリポジトリ直下（= プロパティ直下）に置く必要がある。
    """
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    name = "google3c5717818d1af74a.html"
    path = os.path.join(here, name)
    assert os.path.exists(path), f"{name} が無い。GSCの認証が外れる"
    with open(path, encoding="utf-8") as f:
        body = f.read().strip()
    # Google はファイル名と一致する1行を要求する
    assert body == f"google-site-verification: {name}", f"中身が想定と違う: {body!r}"
