# short-20 実写画像で作り直して公開 — 2026-09-05

同一題材で2回差し戻された動画の3回目。**今回はCSS作図を使っていない。**

## 公開したもの

- 動画: https://www.youtube.com/watch?v=Pi9iWoXLjwM （public）
- プロジェクト: `videos/product-usage-photo/`
- MP4: `renders/product-usage-photo_2026-09-05_12-31-32.mp4`（45.03s / 1080x1920 / h264+aac / 4.9MB、ffprobeで実測）
- 画像3枚: `desk-product-only.png` / `worn-closeup.png` / `hand-holding.png`

## 画像生成の配線（今回の本体）

`image_pipeline.py` を新設し、**Codex優先・APIキー代替**を1本のコマンドにまとめた。

```sh
python3 image_pipeline.py --prompt "..." --out videos/<slug>/assets/<name>.png --size 1024x1536
```

- 既定はCodexの組み込み `image_gen`（APIキー不要・追加費用なし）
- **未ログイン / 利用上限のときだけ** `OPENAI_API_KEY` のCLIに落ちる
- `exit 0` を成功と見なさない。生成物のマジックバイトと更新時刻まで見る
- 出所は `ASSETS.md` に自動追記。両方失敗なら exit 1 で止まる

## 今日踏んだ障害（同じ場所で止まらないために）

| 症状 | 実際の原因 | 対処 |
|---|---|---|
| `codex exec` が401 | refresh token revoked（ログアウト） | 運用者が `codex login` |
| 次に exit 1 | 利用上限（復帰 9/7 13:38 と表示） | 上限解消 |
| 次に400 | アカウント既定が `gpt-6-astra`、CLI 0.151.0 が非対応 | `CODEX_MODEL=gpt-5.6-sol` に固定（CLIを上げたら空文字で既定に戻せる） |

**会話モデル（gpt-5.6-sol / gpt-6-astra）と画像モデルは別物。** 画像はCodex組み込み `image_gen`、
CLI代替の既定は `gpt-image-2`。組み込み側の実モデル名はskillのドキュメントに書かれていない。

## アップロード先の確認（毎回やること）

`youtube_token_ec_tips.json` を `--verify-only` で実測してから上げた。

```
チャンネル名 : ひとりネットショップ研究所
チャンネルID : UCYtX_BF_CHCaPpIpVhtMFfg
ハンドル     : @operatorfilesofficial   ← 旧 The Operator Files を改名したもの
```

**同名のチャンネルが2つある**（本物33本 / 空0本 `UCvbHaax_TOXAgECqk5CNfug`）。名前で判断しない。

## 検査

publish_check / cta_contract / `npm run check`（0 errors・contrast 23/23 AA）/ pytest 86件、すべて通過。
公開後は watchページの `playabilityStatus":"OK"` と、概要欄のLPリンク・広告表記の実在を実測した。

## 残っていること

- **公開翌日に再実測する**（公開直後のOKは翻ることがある）
- vidIQのクレジットが0で、動画ごとの残存率が取れない。冒頭の型（`20260827_batch3_cta_redesign.md`）の
  効果検証はクレジット復帰かStudio直接参照が要る
