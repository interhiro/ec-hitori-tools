import pathlib

import pytest

from publish_check import (
    GRANDFATHERED,
    check_project,
    referenced_images,
)

INDEX_WITH_IMG = """
<div id="root" data-composition-id="main" data-duration="30.0">
  <div class="scene" data-composition-src="compositions/frames/01-hook.html"></div>
  <div class="clip" data-cta-role="midpoint-lp" data-start="9.0" data-duration="2.0"></div>
  <div class="clip" data-cta-role="end-subscribe" data-start="25.0" data-duration="5.0"></div>
</div>
"""

FRAME_WITH_IMG = '<img id="hero" src="assets/product-hero.png" alt="" />'
FRAME_WITH_BG = '<div style="background-image:url(\'assets/product-hero.png\')"></div>'
FRAME_CSS_ONLY = '<div class="charm" style="border-radius:60px;border:15px solid #1534c5"></div>'


def _project(tmp_path, frame_body, assets=(), provenance=None):
    d = tmp_path / "sample-video"
    (d / "compositions" / "frames").mkdir(parents=True)
    (d / "assets").mkdir()
    (d / "index.html").write_text(INDEX_WITH_IMG, encoding="utf-8")
    (d / "compositions" / "frames" / "01-hook.html").write_text(frame_body, encoding="utf-8")
    for a in assets:
        (d / "assets" / a).write_bytes(b"\x89PNG\r\n\x1a\n")
    if provenance is not None:
        (d / "ASSETS.md").write_text(provenance, encoding="utf-8")
    return d


def test_img_tag_is_detected():
    assert referenced_images(FRAME_WITH_IMG) == ["assets/product-hero.png"]


def test_css_background_image_is_detected():
    assert referenced_images(FRAME_WITH_BG) == ["assets/product-hero.png"]


def test_css_drawing_counts_as_no_image():
    assert referenced_images(FRAME_CSS_ONLY) == []


def test_project_without_any_image_is_rejected(tmp_path):
    """2026-09-05の差し戻し。CSS作図だけの動画を公開させない。

    8/31のBRIEFは「黒背景と文字だけの画面にはせず、商品写真を主役にする」と
    書いていたが、指示は守られず2本続けて基準未達の動画が公開された。
    """
    d = _project(tmp_path, FRAME_CSS_ONLY)
    v = check_project(d)
    assert any("画像" in x for x in v), v


def test_project_with_image_but_no_provenance_is_rejected(tmp_path):
    """生成手段が記録されないと、次に誰も再現できない。"""
    d = _project(tmp_path, FRAME_WITH_IMG, assets=["product-hero.png"])
    v = check_project(d)
    assert any("ASSETS.md" in x for x in v), v


def test_provenance_must_name_the_actual_file(tmp_path):
    d = _project(tmp_path, FRAME_WITH_IMG, assets=["product-hero.png"],
                 provenance="# 素材の出所\n\n- other-file.png / Codex image_gen\n")
    v = check_project(d)
    assert any("product-hero.png" in x for x in v), v


def test_project_with_image_and_provenance_passes(tmp_path):
    d = _project(tmp_path, FRAME_WITH_IMG, assets=["product-hero.png"],
                 provenance="# 素材の出所\n\n- product-hero.png — Codex 組み込み image_gen / 2026-09-05\n")
    assert check_project(d) == []


def test_missing_image_file_on_disk_is_reported(tmp_path):
    d = _project(tmp_path, FRAME_WITH_IMG, assets=[],
                 provenance="- product-hero.png — Codex image_gen\n")
    v = check_project(d)
    assert any("実体が無い" in x for x in v), v


def test_real_repo_projects_pass_or_are_grandfathered():
    root = pathlib.Path(__file__).resolve().parent.parent / "videos"
    if not root.is_dir():
        pytest.skip("videos/ が無い")
    for d in sorted(p for p in root.iterdir() if p.is_dir()):
        if d.name in GRANDFATHERED or not (d / "index.html").is_file():
            continue
        assert check_project(d) == [], f"{d.name}: {check_project(d)}"
