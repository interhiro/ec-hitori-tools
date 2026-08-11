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
CONTACT_FORM_URL = "https://forms.gle/Uy3kPUrg5xcnqcSy6"


def render_footer(prefix: str = "") -> str:
    """サイト情報への共通フッターを返す。"""
    links = [
        ("operator.html", "運営者情報"),
        ("privacy.html", "プライバシーポリシー"),
        ("contact.html", "お問い合わせ"),
        ("disclaimer.html", "免責・広告掲載方針"),
    ]
    nav = "\n".join(
        f'      <a href="{prefix}{path}">{label}</a>' for path, label in links
    )
    return f'''  <footer>
    <nav class="footer-nav" aria-label="サイト情報">
{nav}
    </nav>
    <p class="footer-brand">ひとりネットショップ研究所</p>
    <p class="footer-operator">ひとりネットショップ研究所</p>
  </footer>'''


def render_video_cards(videos: list[dict]) -> str:
    """公開済みYouTube動画を新しい順のカードとして返す。"""
    cards = []
    for video in videos:
        video_id = html.escape(video.get("id", ""), quote=True)
        title = html.escape(video.get("title", ""))
        topic = html.escape(video.get("topic", "動画"))
        url = f"https://www.youtube.com/watch?v={video_id}"
        cards.append(
            f'''      <article class="video-card">
        <a class="video-thumb" href="{url}" target="_blank" rel="noopener" aria-label="{title}をYouTubeで見る">
          <img src="https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" alt="{title}" loading="lazy">
          <span class="play-mark" aria-hidden="true">▶</span>
        </a>
        <div class="video-copy">
          <span class="eyebrow">{topic}</span>
          <h3><a href="{url}" target="_blank" rel="noopener">{title}</a></h3>
        </div>
      </article>'''
        )
    return "\n".join(cards)


def render_info_page(title: str, description: str, body_html: str) -> str:
    """運営者情報・ポリシー等の固定ページを完全なHTMLとして返す。"""
    safe_title = html.escape(title)
    safe_description = html.escape(description, quote=True)
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title} | ひとりネットショップ研究所</title>
  <meta name="description" content="{safe_description}">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header class="hero hero-compact">
    <p class="kicker"><a href="index.html">← ひとりネットショップ研究所</a></p>
    <h1>{safe_title}</h1>
  </header>

  <main>
    <article class="legal-page">
{body_html}
    </article>
  </main>

{render_footer()}
</body>
</html>
'''


def render_policy_pages() -> dict[str, str]:
    """ASP審査と利用者保護に必要な固定4ページを返す。"""
    operator = render_info_page(
        "運営者情報",
        "ひとりネットショップ研究所の運営者情報です。",
        '''      <p>「ひとりネットショップ研究所」は、個人・小規模でネットショップやハンドメイド販売を行う方に向けて、実務動画と補足情報を発信するサイトです。</p>
      <dl class="legal-list">
        <div><dt>サイト名</dt><dd>ひとりネットショップ研究所</dd></div>
        <div><dt>発信内容</dt><dd>ネットショップ運営、ハンドメイド販売、業務ツールに関する動画・補足情報</dd></div>
        <div><dt>お問い合わせ</dt><dd><a href="contact.html">お問い合わせページ</a>をご利用ください。</dd></div>
      </dl>
      <h2>広告掲載について</h2>
      <p>当サイトはアフィリエイトプログラムを利用しています。対象リンクを経由して申込みや購入が行われた場合、運営者が報酬を受け取ることがあります。詳しくは<a href="disclaimer.html">免責・広告掲載方針</a>をご確認ください。</p>''',
    )

    privacy = render_info_page(
        "プライバシーポリシー",
        "ひとりネットショップ研究所における個人情報等の取扱方針です。",
        '''      <p class="updated">制定・最終更新：2026年8月11日</p>
      <p>本サイトの運営者（以下「運営者」）は、本サイトにおける利用者の情報を、以下の方針に基づいて取り扱います。</p>
      <h2>1. 取得する情報と利用目的</h2>
      <p>お問い合わせ時に、氏名、メールアドレス、お問い合わせ内容等をご提供いただく場合があります。これらは、お問い合わせへの回答、本人確認、必要なご連絡およびサイト運営の改善に利用します。</p>
      <h2>2. Cookie等について</h2>
      <p>本サイトから移動した広告配信事業者、アフィリエイト事業者その他の外部サービスでは、成果計測や利便性向上のためCookie等が利用される場合があります。取得される情報や停止方法は、各事業者のプライバシーポリシーをご確認ください。</p>
      <h2>3. 外部サービス</h2>
      <p>お問い合わせにはGoogleフォームを利用しています。フォームに入力した情報はGoogleのサービスを経由して運営者に送信されます。YouTubeその他の外部サービス上での情報の取扱いについては、各提供者の規約・プライバシーポリシーもご確認ください。</p>
      <h2>4. 第三者提供</h2>
      <p>運営者は、法令に基づく場合または本人の同意がある場合などを除き、取得した個人情報を第三者に提供しません。</p>
      <h2>5. 安全管理</h2>
      <p>運営者は、取得した情報の漏えい、滅失または毀損を防ぐため、必要かつ適切な安全管理措置を講じます。</p>
      <h2>6. 開示・訂正・削除等</h2>
      <p>保有する個人情報の開示、訂正、利用停止、削除等をご希望の場合は、<a href="contact.html">お問い合わせページ</a>からご連絡ください。本人確認のうえ、法令に従って対応します。</p>
      <h2>7. 方針の変更</h2>
      <p>本方針は、法令やサービス内容の変更等に応じて改定することがあります。重要な変更がある場合は、本ページ上でお知らせします。</p>''',
    )

    contact = render_info_page(
        "お問い合わせ",
        "ひとりネットショップ研究所へのお問い合わせ窓口です。",
        f'''      <p>記事・動画の補足内容、掲載情報、広告掲載その他のご連絡は、下記のフォームからお送りください。</p>
      <p class="contact-action"><a class="cta" href="{CONTACT_FORM_URL}" target="_blank" rel="noopener">お問い合わせフォームを開く →</a></p>
      <div class="notice-box">
        <h2>お問い合わせ前にご確認ください</h2>
        <ul>
          <li>内容により回答までお時間をいただく場合、または回答できない場合があります。</li>
          <li>商品・サービスの契約、解約、返金、操作方法は、各提供元の公式窓口へ直接お問い合わせください。</li>
          <li>入力情報は<a href="privacy.html">プライバシーポリシー</a>に基づいて取り扱います。</li>
        </ul>
      </div>''',
    )

    disclaimer = render_info_page(
        "免責・広告掲載方針",
        "ひとりネットショップ研究所の免責事項とアフィリエイト広告の掲載方針です。",
        '''      <p class="updated">制定・最終更新：2026年8月11日</p>
      <h2>広告・アフィリエイトについて</h2>
      <p>当サイトには、アフィリエイトプログラムによる広告リンクが含まれます。リンクを経由して申込みや購入が行われた場合、運営者が報酬を受け取ることがあります。利用者の購入価格に追加料金が生じるものではありません。</p>
      <p>広告であることが分かるよう、対象ページには広告を含む旨を表示します。掲載報酬の有無だけを理由に評価を決めず、読者にとっての有用性、機能、利用条件等を踏まえて情報を掲載します。</p>
      <h2>情報の正確性</h2>
      <p>掲載情報の正確性と最新性の確保に努めますが、その完全性、正確性、安全性または特定目的への適合性を保証するものではありません。料金、仕様、在庫、キャンペーン、利用条件等は変更される場合があるため、申込みや購入の前に必ず各提供元の公式サイトで最新情報をご確認ください。</p>
      <h2>免責事項</h2>
      <p>当サイトの情報または外部サイトを利用したことにより生じた損害について、運営者は法令上認められる範囲で責任を負いません。商品・サービスに関する契約は、利用者と各提供事業者との間で成立します。最終的な判断は利用者ご自身の責任で行ってください。</p>
      <h2>成果に関する注意</h2>
      <p>紹介する事例、方法、ツール等は、特定の売上、利益、業務改善その他の成果を保証するものではありません。結果は事業環境、利用方法その他の条件によって異なります。</p>
      <h2>著作権と外部リンク</h2>
      <p>掲載する文章、画像その他のコンテンツの著作権は、運営者または正当な権利者に帰属します。法令で認められる範囲を超えた無断転載等を禁止します。外部サイトの内容や提供サービスは各運営者の責任で管理されます。</p>''',
    )

    return {
        "operator.html": operator,
        "privacy.html": privacy,
        "contact.html": contact,
        "disclaimer.html": disclaimer,
    }


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
        items.append((meta.get("date", ""), slug, title))

    if not items:
        return ""

    # 新着が上に来るよう date 降順。date 欠落("")は最後尾へ回し、同順位はファイル名順を保つ
    items.sort(key=lambda it: (it[0] == "", [-ord(c) for c in it[0]]))

    lis = "".join(
        f'<li><a href="articles/{html.escape(slug, quote=True)}.html">{html.escape(title)}</a></li>'
        for _, slug, title in items
    )
    return f'''    <section class="columns">
      <div class="section-heading">
        <span class="eyebrow">VIDEO NOTES</span>
        <h2>動画の補足ノート</h2>
        <p>動画で扱ったテーマを、あとから読み返せる形に整理しています。</p>
      </div>
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


def build_html(
    tools_data: dict,
    cfg: dict,
    articles_dir: str | None = None,
    videos_data: dict | None = None,
) -> str:
    tools = tools_data.get("tools", [])
    cards_html = render_cards(tools, cfg)
    videos_html = render_video_cards((videos_data or {}).get("videos", []))
    video_section = f'''    <section class="videos-section">
      <div class="section-heading">
        <span class="eyebrow">LATEST VIDEOS</span>
        <h2>まずは動画で、今日やることを決める</h2>
        <p>直近の実務動画です。気になるテーマからご覧ください。</p>
      </div>
      <div class="video-grid">
{videos_html}
      </div>
    </section>
''' if videos_html else ""
    site = html.escape(cfg.get("site_base_url", ""), quote=True)
    columns_html = render_article_links(articles_dir) if articles_dir else ""
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ひとりネットショップ研究所｜動画の補足とおすすめツール</title>
  <meta name="description" content="個人・小規模のネットショップ運営に役立つ実務動画、補足ノート、おすすめツールをまとめています。">
  <meta property="og:title" content="ひとりネットショップ研究所">
  <meta property="og:url" content="{site}">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header class="hero">
    <span class="eyebrow">ひとり運営の実務チャンネル</span>
    <h1>動画で学び、<br>使う道具をここで選ぶ。</h1>
    <p>ネットショップとハンドメイド販売を、ひとりで回す人へ。<br>動画の要点、公式情報、紹介ツールを一か所にまとめました。</p>
    <a class="hero-cta" href="#latest-videos">最新動画を見る ↓</a>
  </header>

  <main>
    <div id="latest-videos"></div>
{video_section}    <section class="tools-section">
      <div class="section-heading">
        <span class="eyebrow">TOOLS</span>
        <h2>動画で触れた、運営に役立つツール</h2>
        <p>申込み前に、料金・仕様・条件を必ず公式サイトでご確認ください。</p>
      </div>
      <div class="grid">
{cards_html}
      </div>
    </section>
{columns_html}    <p class="disclosure">※ 当サイトのリンクには広告（アフィリエイト）を含みます。リンク経由の申込み等で運営者が報酬を受け取る場合があります。</p>
  </main>

{render_footer()}

  <script src="track.js"></script>
</body>
</html>
'''


def main() -> None:
    with open(os.path.join(HERE, "tools.json"), encoding="utf-8") as f:
        tools_data = json.load(f)
    with open(os.path.join(HERE, "affiliate.config.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    with open(os.path.join(HERE, "videos.json"), encoding="utf-8") as f:
        videos_data = json.load(f)
    out = build_html(
        tools_data,
        cfg,
        articles_dir=os.path.join(HERE, "articles"),
        videos_data=videos_data,
    )
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
        f.write(out)
    for filename, page in render_policy_pages().items():
        with open(os.path.join(HERE, filename), "w", encoding="utf-8") as f:
            f.write(page)
    monetized = sum(1 for t in tools_data.get("tools", []) if (t.get("affiliate_url") or "").strip())
    total = len(tools_data.get("tools", []))
    print(
        f"built index.html + 4 info pages: {len(videos_data.get('videos', []))} videos, "
        f"{total} tools ({monetized} monetized, {total - monetized} pending affiliate_url)"
    )


if __name__ == "__main__":
    main()
