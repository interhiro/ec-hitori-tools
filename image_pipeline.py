"""画像生成の経路を1本にまとめる。Codexを既定にし、止まっているときだけAPIキーに落ちる。

2026-09-05まで、画像生成の手段はCodexのセッション側にしか無く、Claude Code側からは
再現できなかった。その結果、手段が無いことに気づいた時点で止まらずCSS作図で代替し、
基準未達の動画を2本公開する事故になった(publish_check.py の冒頭に経緯)。

経路は2つだけ。**Codexが既定**、APIは代替。

1. `codex-builtin` — Codexの組み込み `image_gen`。APIキー不要。追加費用なし
2. `openai-cli`   — `~/.codex/skills/.system/imagegen/scripts/image_gen.py`。
                    `OPENAI_API_KEY` が要る。Codexが利用上限などで止まったときだけ使う

どちらも失敗したら **例外で止まる**。CSS作図に落ちない。exit 0 は成功の証明にならないので、
生成物の実体(PNG/JPEG/WebPのマジックバイト)と、実行前後で変化したことまで見る。

使い方:

    python3 image_pipeline.py --prompt "ピアスの実写..." \
        --out videos/product-usage-photo/assets/hero.png --size 1024x1536
"""
from __future__ import annotations

import argparse
import datetime as _dt
import os
import pathlib
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Callable, Mapping, Optional

IMAGEGEN_CLI = pathlib.Path.home() / ".codex/skills/.system/imagegen/scripts/image_gen.py"
KEYCHAIN_SERVICE = "openai"
KEY_HINT = 'security add-generic-password -s openai -a "$USER" -w'
CODEX_TIMEOUT_SEC = 900

# Codexの会話モデル。**画像そのものを作るモデルではない**（画像は組み込み image_gen 側）。
# 2026-09-05、アカウント既定の `gpt-6-astra` が
# 「requires a newer version of Codex」で400を返したため、動くモデルに固定した。
# CLIを上げたら CODEX_MODEL="" で既定に戻せる。
CODEX_MODEL = os.environ.get("CODEX_MODEL", "gpt-5.6-sol")

_MAGIC = (b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff", b"RIFF")
_AUTH = re.compile(
    r"(token_revoked|refresh_token_invalidated|revoked|401 Unauthorized"
    r"|log ?in again|sign in again|session has ended)", re.I)
_LIMIT = re.compile(
    r"(usage limit|rate.?limit|too many requests|\b429\b|quota"
    r"|(daily|weekly|monthly) limit|insufficient_quota)", re.I)

_SECTION = "## 自動生成の記録（image_pipeline.py）"
_HEADER = "| ファイル | 生成手段 | 生成日 | プロンプト |"
_SEP = "|---|---|---|---|"


class ImageGenerationError(RuntimeError):
    """生成できなかった。代替表現に落ちずにここで止める。"""


@dataclass(frozen=True)
class Result:
    path: pathlib.Path
    backend: str
    model: Optional[str]
    prompt: str


def is_rate_limited(text: str) -> bool:
    """Codexが利用上限・レート制限で止まったかを出力から判定する。"""
    return bool(_LIMIT.search(text or ""))


def codex_failure_reason(text: str) -> str:
    """Codexが使えなかった理由。上限なのか未ログインなのかで、次にやることが変わる。"""
    if is_rate_limited(text):
        return "利用上限"
    if _AUTH.search(text or ""):
        return "未ログイン"
    return "不明"


def is_valid_image(path: pathlib.Path) -> bool:
    """実体がある画像か。エラーメッセージが書かれたファイルを通さない。"""
    p = pathlib.Path(path)
    if not p.is_file() or p.stat().st_size < 100:
        return False
    head = p.open("rb").read(12)
    return any(head.startswith(m) for m in _MAGIC)


def resolve_api_key(env: Mapping[str, str], keychain: Callable[[], Optional[str]]) -> Optional[str]:
    """環境変数 > keychain の順。値はログに出さない。"""
    return (env.get("OPENAI_API_KEY") or "").strip() or (keychain() or None)


def keychain_key() -> Optional[str]:
    try:
        r = subprocess.run(
            ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE,
             "-a", os.environ.get("USER", ""), "-w"],
            capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() or None if r.returncode == 0 else None


def assets_row(filename: str, backend: str, date: str, prompt: str) -> str:
    p = " ".join((prompt or "").split()).replace("|", "/")
    if len(p) > 120:
        p = p[:117] + "..."
    return f"| `{filename}` | {backend} | {date} | {p} |"


def append_assets_row(assets_md: pathlib.Path, row: str) -> None:
    """publish_check.py が要求する出所記録を残す。同じファイル名は二重に書かない。"""
    md = pathlib.Path(assets_md)
    text = md.read_text(encoding="utf-8") if md.is_file() else ""
    name = row.split("|")[1].strip().strip("`")
    if name and name in text:
        return
    add = ""
    if _HEADER not in text:
        add += ("\n" if text and not text.endswith("\n") else "") + f"\n{_SECTION}\n\n{_HEADER}\n{_SEP}\n"
    md.parent.mkdir(parents=True, exist_ok=True)
    md.write_text(text + add + row + "\n", encoding="utf-8")


def _stamp(p: pathlib.Path):
    return (p.stat().st_mtime_ns, p.stat().st_size) if p.is_file() else None


def _produced(out: pathlib.Path, before) -> bool:
    return is_valid_image(out) and _stamp(out) != before


def generate(prompt: str, out_path, *, codex_runner, cli_runner, api_key: Optional[str],
             prefer: str = "codex", assets_md=None, size: Optional[str] = None,
             model: Optional[str] = None, today: Optional[str] = None) -> Result:
    """Codexを試し、止まっていたらAPIに落ちる。どちらも駄目なら例外。"""
    out = pathlib.Path(out_path)
    reasons: list[str] = []

    if prefer != "cli":
        before = _stamp(out)
        r = codex_runner(prompt, out, size=size)
        if r.returncode == 0 and _produced(out, before):
            return _record(out, "codex-builtin", None, prompt, assets_md, today)
        blob = f"{getattr(r, 'stdout', '')}\n{getattr(r, 'stderr', '')}".strip()
        why = codex_failure_reason(blob)
        hint = {"未ログイン": " → `codex login` で入り直す",
                "利用上限": " → 上限が戻るまでAPIに落ちる"}.get(why, "")
        reasons.append(f"codex: {why}(exit={r.returncode}){hint}\n  {blob[-300:]}")

    if not api_key:
        raise ImageGenerationError(
            "Codexが使えず、OPENAI_API_KEY も無いので画像を生成できない。\n"
            + "\n".join(reasons)
            + f"\nキーを入れる: {KEY_HINT}\n"
            "CSS作図で代替しないこと(2026-09-05に2本差し戻し)。")

    before = _stamp(out)
    r = cli_runner(prompt, out, api_key=api_key, size=size, model=model)
    if r.returncode == 0 and _produced(out, before):
        return _record(out, "openai-cli", model or "gpt-image-2", prompt, assets_md, today)
    blob = f"{getattr(r, 'stdout', '')}\n{getattr(r, 'stderr', '')}".strip()
    reasons.append(f"openai-cli: exit={r.returncode} {blob[-300:]}")
    raise ImageGenerationError("画像を生成できなかった。\n" + "\n".join(reasons))


def _record(out: pathlib.Path, backend: str, model, prompt: str, assets_md, today) -> Result:
    if assets_md:
        date = today or _dt.date.today().isoformat()
        label = backend if not model else f"{backend} ({model})"
        append_assets_row(pathlib.Path(assets_md), assets_row(out.name, label, date, prompt))
    return Result(out, backend, model, prompt)


# --- 実行系（テストでは差し替える） ---

def codex_cmd(out: pathlib.Path, order: str, model: Optional[str]) -> list[str]:
    cmd = ["codex", "exec", "--sandbox", "workspace-write", "--skip-git-repo-check",
           "-C", str(pathlib.Path(out).parent.resolve())]
    if model:
        cmd += ["-m", model]
    return cmd + [order]


def codex_runner(prompt: str, out: pathlib.Path, *, size=None):
    out.parent.mkdir(parents=True, exist_ok=True)
    order = (
        "imagegen スキルの組み込み image_gen ツールで画像を1枚だけ生成し、"
        f"生成物を {out.resolve()} に保存せよ。"
        "CLIフォールバック(scripts/image_gen.py)は使わない。"
        + (f"サイズは {size}。" if size else "")
        + f"\n\nプロンプト:\n{prompt}\n\n"
        "完了したら保存先の絶対パスだけを出力せよ。"
    )
    cmd = codex_cmd(out, order, CODEX_MODEL or None)
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=CODEX_TIMEOUT_SEC)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(cmd, 124, "", f"timeout after {CODEX_TIMEOUT_SEC}s")
    except OSError as e:
        return subprocess.CompletedProcess(cmd, 127, "", f"codex を起動できない: {e}")


def cli_runner(prompt: str, out: pathlib.Path, *, api_key: str, size=None, model=None):
    if not IMAGEGEN_CLI.is_file():
        return subprocess.CompletedProcess([], 127, "", f"{IMAGEGEN_CLI} が無い")
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(IMAGEGEN_CLI), "generate", "--prompt", prompt,
           "--out", str(out.resolve()), "--force"]
    if size:
        cmd += ["--size", size]
    if model:
        cmd += ["--model", model]
    env = {**os.environ, "OPENAI_API_KEY": api_key}
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=600, env=env)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(cmd, 124, "", "timeout after 600s")


def default_assets_md(out: pathlib.Path) -> pathlib.Path:
    d = out.parent
    return (d.parent if d.name in ("assets", "public") else d) / "ASSETS.md"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Codex優先・APIキー代替で画像を生成する")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--size", default=None, help="例 1024x1536")
    ap.add_argument("--model", default=None, help="APIに落ちたときのモデル(既定 gpt-image-2)")
    ap.add_argument("--prefer", choices=("codex", "cli"), default="codex")
    ap.add_argument("--assets", default=None, help="出所を書くASSETS.md(既定は動画ディレクトリ)")
    a = ap.parse_args(argv)

    out = pathlib.Path(a.out).resolve()
    try:
        r = generate(a.prompt, out, codex_runner=codex_runner, cli_runner=cli_runner,
                     api_key=resolve_api_key(os.environ, keychain_key), prefer=a.prefer,
                     assets_md=pathlib.Path(a.assets) if a.assets else default_assets_md(out),
                     size=a.size, model=a.model)
    except ImageGenerationError as e:
        print(str(e), file=sys.stderr)
        return 1
    print(f"{r.backend}: {r.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
