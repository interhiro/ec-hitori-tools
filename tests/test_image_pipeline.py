import pathlib

import pytest

from image_pipeline import (
    ImageGenerationError,
    Result,
    append_assets_row,
    assets_row,
    generate,
    is_rate_limited,
    is_valid_image,
    resolve_api_key,
)

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 4096


class _Run:
    """subprocess.CompletedProcess の最小代用。"""

    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _writer(payload=PNG, returncode=0, stdout="", stderr=""):
    """呼ばれたら out に payload を書くランナー。呼び出し回数を数える。"""
    calls = []

    def run(prompt, out, **kw):
        calls.append({"prompt": prompt, "out": out, **kw})
        if payload is not None:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(payload)
        return _Run(returncode, stdout, stderr)

    run.calls = calls
    return run


# --- 限界の検出 ---

@pytest.mark.parametrize("text", [
    "You've hit your usage limit. Try again in 4 hours.",
    "Error: rate limit exceeded",
    "stream error: 429 Too Many Requests",
    "You have reached your weekly limit for gpt-5.6-sol",
    "quota exceeded for this organization",
])
def test_rate_limit_phrases_are_detected(text):
    assert is_rate_limited(text) is True


@pytest.mark.parametrize("text", [
    "Saved image to /Users/shima/.codex/generated_images/x.png",
    "done",
    "",
])
def test_normal_output_is_not_rate_limit(text):
    assert is_rate_limited(text) is False


# --- 生成物の検証 ---

def test_valid_png_is_accepted(tmp_path):
    p = tmp_path / "a.png"
    p.write_bytes(PNG)
    assert is_valid_image(p) is True


def test_missing_file_is_rejected(tmp_path):
    assert is_valid_image(tmp_path / "nope.png") is False


def test_truncated_or_text_file_is_rejected(tmp_path):
    p = tmp_path / "a.png"
    p.write_text("Error: could not generate", encoding="utf-8")
    assert is_valid_image(p) is False


# --- APIキーの解決 ---

def test_env_key_wins_over_keychain():
    assert resolve_api_key({"OPENAI_API_KEY": "sk-env"}, lambda: "sk-chain") == "sk-env"


def test_keychain_is_used_when_env_is_empty():
    assert resolve_api_key({}, lambda: "sk-chain") == "sk-chain"


def test_no_key_anywhere_returns_none():
    assert resolve_api_key({"OPENAI_API_KEY": ""}, lambda: None) is None


# --- 経路の選択（本題）---

def test_codex_is_used_first_and_cli_is_not_called(tmp_path):
    codex, cli = _writer(), _writer()
    r = generate("ピアスの実写", tmp_path / "out.png",
                 codex_runner=codex, cli_runner=cli, api_key="sk-x")
    assert isinstance(r, Result)
    assert r.backend == "codex-builtin"
    assert len(codex.calls) == 1
    assert cli.calls == []


def test_falls_back_to_cli_when_codex_is_rate_limited(tmp_path):
    codex = _writer(payload=None, returncode=1,
                    stderr="You've hit your usage limit. Try again in 4 hours.")
    cli = _writer()
    r = generate("ピアスの実写", tmp_path / "out.png",
                 codex_runner=codex, cli_runner=cli, api_key="sk-x")
    assert r.backend == "openai-cli"
    assert len(cli.calls) == 1
    assert cli.calls[0]["api_key"] == "sk-x"


def test_falls_back_when_codex_exits_zero_but_writes_nothing(tmp_path):
    """exit 0 は成功の証明にならない。実体を見る。"""
    codex = _writer(payload=None, returncode=0, stdout="done")
    cli = _writer()
    r = generate("x", tmp_path / "out.png",
                 codex_runner=codex, cli_runner=cli, api_key="sk-x")
    assert r.backend == "openai-cli"


def test_no_key_and_codex_limited_raises_instead_of_pretending(tmp_path):
    codex = _writer(payload=None, returncode=1, stderr="rate limit exceeded")
    cli = _writer()
    with pytest.raises(ImageGenerationError) as e:
        generate("x", tmp_path / "out.png",
                 codex_runner=codex, cli_runner=cli, api_key=None)
    assert "security add-generic-password" in str(e.value)
    assert cli.calls == []


def test_both_paths_fail_raises(tmp_path):
    codex = _writer(payload=None, returncode=1, stderr="rate limit exceeded")
    cli = _writer(payload=None, returncode=1, stderr="Error: invalid_api_key")
    with pytest.raises(ImageGenerationError):
        generate("x", tmp_path / "out.png",
                 codex_runner=codex, cli_runner=cli, api_key="sk-bad")


def test_force_fallback_skips_codex(tmp_path):
    codex, cli = _writer(), _writer()
    r = generate("x", tmp_path / "out.png", codex_runner=codex, cli_runner=cli,
                 api_key="sk-x", prefer="cli")
    assert r.backend == "openai-cli"
    assert codex.calls == []


# --- 出所記録（publish_check.py が要求する）---

def test_assets_row_contains_filename_backend_and_date():
    row = assets_row("hero.png", "codex-builtin", "2026-09-05", "ピアスの実写")
    assert "hero.png" in row and "codex-builtin" in row and "2026-09-05" in row
    assert row.startswith("|") and row.endswith("|")


def test_append_creates_file_with_header_when_missing(tmp_path):
    md = tmp_path / "ASSETS.md"
    append_assets_row(md, assets_row("hero.png", "codex-builtin", "2026-09-05", "p"))
    text = md.read_text(encoding="utf-8")
    assert "hero.png" in text
    assert "| ファイル |" in text


def test_append_is_idempotent_for_the_same_file(tmp_path):
    md = tmp_path / "ASSETS.md"
    row = assets_row("hero.png", "codex-builtin", "2026-09-05", "p")
    append_assets_row(md, row)
    append_assets_row(md, row)
    assert md.read_text(encoding="utf-8").count("hero.png") == 1


def test_generated_image_is_recorded_in_assets_md(tmp_path):
    project = tmp_path / "video"
    (project / "assets").mkdir(parents=True)
    generate("ピアスの実写", project / "assets" / "hero.png",
             codex_runner=_writer(), cli_runner=_writer(), api_key="sk-x",
             assets_md=project / "ASSETS.md")
    text = (project / "ASSETS.md").read_text(encoding="utf-8")
    assert "hero.png" in text
    assert "codex-builtin" in text


# --- Codexが使えない理由の切り分け（2026-09-05にrevokedを実際に踏んだ）---

from image_pipeline import codex_failure_reason  # noqa: E402

REVOKED = ("ERROR: Your access token could not be refreshed because your refresh token "
           "was revoked. Please log out and sign in again.")


def test_revoked_token_is_reported_as_logged_out_not_rate_limit():
    assert codex_failure_reason(REVOKED) == "未ログイン"
    assert is_rate_limited(REVOKED) is False


@pytest.mark.parametrize("text", [
    'HTTP 401: {"code": "token_revoked"}',
    "failed to connect to websocket: HTTP error: 401 Unauthorized",
    "Your session has ended. Please log in again.",
])
def test_auth_failures_are_logged_out(text):
    assert codex_failure_reason(text) == "未ログイン"


def test_usage_limit_is_reported_as_limit():
    assert codex_failure_reason("You've hit your usage limit.") == "利用上限"


def test_unknown_failure_is_labelled_unknown():
    assert codex_failure_reason("Segmentation fault") == "不明"


def test_failure_message_carries_the_reason_and_stderr(tmp_path):
    codex = _writer(payload=None, returncode=1, stderr=REVOKED)
    with pytest.raises(ImageGenerationError) as e:
        generate("x", tmp_path / "out.png", codex_runner=codex,
                 cli_runner=_writer(), api_key=None)
    msg = str(e.value)
    assert "未ログイン" in msg
    assert "codex login" in msg
    assert "revoked" in msg


def test_empty_keychain_entry_counts_as_no_key():
    """空のkeychainエントリは「入っている」ではない(2026-09-05に実際に作られた)。"""
    assert resolve_api_key({}, lambda: "") is None
    assert resolve_api_key({"OPENAI_API_KEY": "   "}, lambda: "") is None


# --- Codexに渡すコマンド（2026-09-05: 既定モデルが新CLIを要求して400になった）---

from image_pipeline import codex_cmd  # noqa: E402


def test_codex_cmd_pins_the_model(tmp_path):
    cmd = codex_cmd(tmp_path / "a.png", "指示", model="gpt-5.6-sol")
    assert cmd[:2] == ["codex", "exec"]
    assert "-m" in cmd and cmd[cmd.index("-m") + 1] == "gpt-5.6-sol"


def test_codex_cmd_omits_model_when_not_pinned(tmp_path):
    assert "-m" not in codex_cmd(tmp_path / "a.png", "指示", model=None)


def test_codex_cmd_makes_the_output_dir_writable(tmp_path):
    out = tmp_path / "videos" / "x" / "assets" / "a.png"
    cmd = codex_cmd(out, "指示", model=None)
    assert cmd[cmd.index("-C") + 1] == str(out.parent.resolve())
