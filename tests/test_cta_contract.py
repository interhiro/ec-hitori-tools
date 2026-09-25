import pathlib

import pytest

from cta_contract import GRANDFATHERED, check_composition, scan_videos

BOTH_ROLES = """
<div id="root" data-composition-id="main" data-duration="30.0">
  <div class="scene" data-start="0" data-duration="10"></div>
  <div class="clip" data-cta-role="midpoint-lp" data-start="9.0" data-duration="2.0"></div>
  <div class="clip" data-cta-role="end-subscribe" data-start="25.0" data-duration="5.0"></div>
</div>
"""

NO_ROLES = """
<div id="root" data-composition-id="main" data-duration="30.0">
  <div class="scene" data-start="0" data-duration="30"></div>
</div>
"""


def test_composition_without_cta_roles_reports_both_as_missing():
    v = check_composition(NO_ROLES)
    assert any("midpoint-lp" in x for x in v)
    assert any("end-subscribe" in x for x in v)


def test_composition_with_both_roles_at_correct_position_passes():
    assert check_composition(BOTH_ROLES) == []


def test_midpoint_placed_too_early_is_rejected():
    html = BOTH_ROLES.replace('data-cta-role="midpoint-lp" data-start="9.0"',
                              'data-cta-role="midpoint-lp" data-start="1.5"')
    v = check_composition(html)
    assert any("位置" in x for x in v), v


def test_midpoint_placed_at_the_end_is_rejected():
    html = BOTH_ROLES.replace('data-cta-role="midpoint-lp" data-start="9.0"',
                              'data-cta-role="midpoint-lp" data-start="27.0"')
    assert any("位置" in x for x in check_composition(html))


def test_missing_root_duration_is_reported_not_silently_passed():
    html = '<div id="root" data-composition-id="main"></div>'
    v = check_composition(html)
    assert any("data-duration" in x for x in v), v


def test_scan_skips_published_videos_that_must_not_be_rebuilt(tmp_path):
    for slug in list(GRANDFATHERED)[:1] + ["new-short"]:
        d = tmp_path / slug
        d.mkdir()
        (d / "index.html").write_text(NO_ROLES, encoding="utf-8")
    result = scan_videos(tmp_path)
    assert "new-short" in result
    assert list(GRANDFATHERED)[0] not in result


def test_scan_ignores_directories_without_a_composition(tmp_path):
    (tmp_path / "assets-only").mkdir()
    assert scan_videos(tmp_path) == {}


def test_real_repo_videos_satisfy_the_contract():
    root = pathlib.Path(__file__).resolve().parent.parent / "videos"
    if not root.is_dir():
        pytest.skip("videos/ が無い")
    violations = scan_videos(root)
    assert violations == {}, f"CTA契約に違反する動画がある: {violations}"
