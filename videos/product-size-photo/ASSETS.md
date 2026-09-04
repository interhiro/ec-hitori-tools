# 素材の出所

この動画で使った画像を、**どう作ったか再現できる形**で残す。
2026-09-05、ここが空白だったために別のセッションが画像を再現できず、
CSS作図で代替した基準未達の動画を2本公開する事故になった。

## 画像

| ファイル | 生成手段 | 生成日 | 用途 |
|---|---|---|---|
| `assets/earring-scale-comparison.png` | **Codex の組み込み `image_gen` ツール**（gpt-image系） | 2026-08-31 | 全フレームの背景写真。ピアス単体と着用比較 |
| `assets/earring-scale-comparison-bottom.png` | 同上（同一画像のクロップ違い） | 2026-08-31 | 下部クロップ用 |
| `public/earring-scale-comparison.png` | 同上 | 2026-08-31 | HyperFrames の user-supplied image パス |

941x1672 / PNG / RGB。

## 生成手段の所在（重要）

**画像生成は Codex 側の機能で、Claude Code にはありません。**

- Codex の「Image Generation Skill」= 組み込み `image_gen` ツール。既定パス。`OPENAI_API_KEY` 不要
- CLI フォールバック `scripts/image_gen.py`（`generate` / `edit` / `generate-batch`）。`OPENAI_API_KEY` が要る。**ユーザーが明示的に求めたときだけ使う**
- Claude Code 側の `/media-use` は heygen または mflux が要るが、2026-09-05 時点でどちらも未導入（`resolve.mjs --doctor` で確認）

したがって **Claude Code だけで画像入りショートは作れない。** 作るなら次のどれか。

1. 画像生成の工程を Codex に投げ、生成物をこのディレクトリに置いてから合成する
2. `mflux` をローカル導入する（FLUX・オフライン・無料。モデルDLが数GB）
3. HeyGen CLI を入れて OAuth サインインする（無料枠）

**手段が無いと分かった時点で止まること。CSS作図で代替してはいけない。**

## 復元の経緯

2026-08-31 の worklog には「画像: 生成したオリジナルのピアス単体＋着用比較写真」としか
書かれておらず、ツール名もプロンプトも残っていなかった。
2026-09-05 に `~/.codex/sessions/2026/09/01/rollout-*.jsonl` を検索して
`image_gen` の利用を特定した。**この掘り起こしが必要だった時点で記録として失格。**
以後は `publish_check.py` がこのファイルの存在と、参照画像名の記載を必須にする。
