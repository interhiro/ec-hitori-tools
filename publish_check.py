"""公開前の必須検査。動画に「見て分かる画像」と、その出所記録があるかを見る。

2026-09-05、同じ題材の動画を2本続けて基準未達で公開し、島山の差し戻しを受けた。
原因は3つ重なっている。

1. **参照した実装を間違えた。** 手本にすべきは 2026-08-31 の product-size-photo
   (実写主体・島山が良いと評価) だったが、直近という理由だけで 09-02 の
   product-detail-photo (CSS作図) を手本にした。8/31のBRIEFには
   「黒背景と文字だけの画面にはせず、商品写真を主役にする」と明記されていた。
2. **制約を読み違えた。** 「他人の商品画像を使わない=オリジナル画像を制作する」を
   「CSS作図で描く」に変換した。青い角丸長方形をピアスと見立てさせる図になった。
3. **再現できないと分かった時点で止まらなかった。** 画像生成手段がこちらに無いのに、
   代替に切り替えて押し通した。

さらに、8/31の画像の生成手段が worklog に「生成したオリジナル」としか書かれておらず、
**Codexのセッションログを掘るまで誰も再現できなかった。**

このモジュールは上の3つを機械的に落とす。ドキュメントに書くだけでは同じことが起きる。
"""
from __future__ import annotations

import pathlib
import re

# 本契約より前に公開済みで、作り直さない動画。
GRANDFATHERED = frozenset({"product-size-photo", "product-detail-photo"})

PROVENANCE = "ASSETS.md"
_IMG_EXT = (".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif", ".svg", ".mp4", ".webm")

_SRC = re.compile(r"""<img[^>]*\ssrc\s*=\s*["']([^"']+)["']""", re.I)
_BG = re.compile(r"""background(?:-image)?\s*:[^;}"']*url\(\s*['"]?([^'")]+)""", re.I)


def referenced_images(html: str) -> list[str]:
    """HTMLが参照している画像/動画のパスを、出現順・重複なしで返す。

    CSS作図(border-radius等)は画像ではないので当然ここに出てこない。
    """
    found: list[str] = []
    for pat in (_SRC, _BG):
        for m in pat.finditer(html or ""):
            p = m.group(1).strip()
            if p.lower().endswith(_IMG_EXT) and p not in found:
                found.append(p)
    return found


def _all_html(project_dir: pathlib.Path) -> list[pathlib.Path]:
    files = [project_dir / "index.html"]
    files += sorted((project_dir / "compositions").rglob("*.html"))
    return [f for f in files if f.is_file()]


def check_project(project_dir: pathlib.Path) -> list[str]:
    """公開してよいかを検査する。空リストなら合格。"""
    violations: list[str] = []

    refs: list[str] = []
    for f in _all_html(project_dir):
        for p in referenced_images(f.read_text(encoding="utf-8")):
            if p not in refs:
                refs.append(p)

    if not refs:
        violations.append(
            "画像が1枚も使われていない。CSS作図だけの画面は公開しない"
            "(2026-08-31 BRIEF「黒背景と文字だけの画面にはせず、商品写真を主役にする」)")
        return violations

    missing = [p for p in refs
               if not (project_dir / p).is_file()
               and not (project_dir / "public" / pathlib.Path(p).name).is_file()]
    for p in missing:
        violations.append(f"{p} を参照しているが実体が無い")

    prov_path = project_dir / PROVENANCE
    if not prov_path.is_file():
        violations.append(
            f"{PROVENANCE} が無い。画像をどう作ったかを残さないと次に誰も再現できない"
            "(8/31の画像はCodexのセッションログを掘るまで手段が分からなかった)")
        return violations

    prov = prov_path.read_text(encoding="utf-8")
    for p in refs:
        if pathlib.Path(p).name not in prov:
            violations.append(f"{PROVENANCE} に {pathlib.Path(p).name} の出所が書かれていない")
    return violations


def main() -> int:
    root = pathlib.Path(__file__).resolve().parent / "videos"
    if not root.is_dir():
        print("videos/ が無い")
        return 0
    bad = {}
    for d in sorted(p for p in root.iterdir() if p.is_dir()):
        if d.name in GRANDFATHERED or not (d / "index.html").is_file():
            continue
        v = check_project(d)
        if v:
            bad[d.name] = v
    if not bad:
        print("公開前検査: 違反なし")
        return 0
    for slug, items in bad.items():
        print(f"{slug}:")
        for i in items:
            print(f"  - {i}")
    print(f"\n基準は videos/CTA-SPEC.md。手本は videos/product-size-photo (2026-08-31)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
