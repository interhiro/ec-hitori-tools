"""Shorts のCTA契約を機械的に検査する。

2026-08-27にCTA設計を決めたが(worklog/20260827_batch3_cta_redesign.md)、
8/31のHyperFramesパイプライン移行で設計がそのまま消えた。仕様がドキュメント
にしか無く、物理的に強制する仕組みが無かったことが原因である。

このモジュールは videos/<slug>/index.html を走査し、CTAが動画本体に
埋まっていることをテストで落とせる形にする。契約の中身は videos/CTA-SPEC.md。
"""
from __future__ import annotations

import pathlib
import re

# 動画本体に必ず含める2つのCTA。名前は data-cta-role 属性の値。
REQUIRED_ROLES = ("midpoint-lp", "end-subscribe")

# midpoint-lp を置いてよい位置(尺に対する比)。
# 39J3tjBtbH0 の実測残存率は 20%:57% / 33%:34% / 100%:11%。
# 末尾は11%にしか届かないため、最も到達の大きい前半3分の1に置く。
MIDPOINT_WINDOW = (0.20, 0.40)

# 公開済みで作り直さない動画。再レンダは既存の再生数を失うため
# (2026-08-27の決定「既存動画の作り直しは行わない」)。
# ここに足してよいのは「本契約より前に公開済み」のものだけ。
GRANDFATHERED = frozenset({"product-size-photo", "product-detail-photo"})

_TAG = re.compile(r"<[a-zA-Z][^>]*>")


def _attr(tag: str, name: str) -> str | None:
    m = re.search(rf'{re.escape(name)}\s*=\s*"([^"]*)"', tag)
    return m.group(1) if m else None


def _first_tag(html: str, predicate) -> str | None:
    return next((t for t in _TAG.findall(html) if predicate(t)), None)


def _as_float(value: str | None) -> float | None:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def check_composition(html: str) -> list[str]:
    """index.html の中身を検査し、違反を人が読める文字列で返す。

    空リストなら契約を満たしている。
    """
    violations: list[str] = []

    root = _first_tag(html, lambda t: _attr(t, "id") == "root")
    if root is None:
        return ['id="root" の要素が無い。HyperFramesの合成として読めない']

    total = _as_float(_attr(root, "data-duration"))
    if total is None or total <= 0:
        violations.append('root に data-duration が無い。CTAの位置を検証できない')

    tags = {
        role: _first_tag(html, lambda t, r=role: _attr(t, "data-cta-role") == r)
        for role in REQUIRED_ROLES
    }
    for role, tag in tags.items():
        if tag is None:
            violations.append(f'data-cta-role="{role}" の要素が無い')

    mid = tags["midpoint-lp"]
    if mid is not None and total:
        start = _as_float(_attr(mid, "data-start"))
        if start is None:
            violations.append('midpoint-lp に data-start が無い。位置を検証できない')
        else:
            lo, hi = MIDPOINT_WINDOW
            ratio = start / total
            if not lo <= ratio <= hi:
                violations.append(
                    f"midpoint-lp の位置が範囲外: {ratio:.0%}"
                    f"(許容 {lo:.0%}〜{hi:.0%}、data-start={start} / 尺={total})"
                )
    return violations


def scan_videos(videos_root: pathlib.Path) -> dict[str, list[str]]:
    """videos/ 配下を走査し、違反のある動画だけを返す。

    GRANDFATHERED と index.html を持たないディレクトリは対象外。
    """
    result: dict[str, list[str]] = {}
    for d in sorted(p for p in videos_root.iterdir() if p.is_dir()):
        if d.name in GRANDFATHERED:
            continue
        composition = d / "index.html"
        if not composition.is_file():
            continue
        violations = check_composition(composition.read_text(encoding="utf-8"))
        if violations:
            result[d.name] = violations
    return result


def main() -> int:
    root = pathlib.Path(__file__).resolve().parent / "videos"
    if not root.is_dir():
        print("videos/ が無い")
        return 0
    violations = scan_videos(root)
    if not violations:
        print("CTA契約: 違反なし")
        return 0
    for slug, items in violations.items():
        print(f"{slug}:")
        for v in items:
            print(f"  - {v}")
    print("\n契約の中身は videos/CTA-SPEC.md")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
