# アフィリンク投入シート（島山 → Claude）

審査済み・afb/A8/もしも アカウントあり・担当付きが前提。
**やること: 管理画面で各ツールの広告主と提携 → 発行されたアフィリンクURLを下の「貼る欄」にペーストするだけ。**
1つでも埋めてくれれば Claude が tools.json に反映 → `build.py` 再実行 → LP に即反映（`data-monetized="true"` になる）。

> リンクは「素のアフィURL」でOK。動画別トラッキング（?v=）は LP 側の track.js が自動付与するので、ここでは付けなくて良い。
> どのASPで提携したかは任意メモ（成果照合の参考）。

| tools.json の id | ツール | 想定ASP（候補） | 貼る欄（アフィURL） | 提携したASP |
|---|---|---|---|---|
| base | BASE | A8 / もしも | | |
| shopify | Shopify | もしも / アクセストレード等 | | |
| canva | Canva Pro | **Impact（Canvassador）※別系統** | | |
| colormeshop | カラーミーショップ | A8 / afb / バリューコマース | | |
| freee | freee会計 | A8 / もしも | | |
| lstep | Lステップ | A8 / 各ASP | | |

## 補足
- **Canva** は A8/afb/もしも に無い。Canva公式 Canvassador（Impact 経由）で発行 → そのリンクをcanva欄に貼る。面倒なら canva 行は空のままでOK（公式URLにフォールバックし続ける）。
- 上の6つは叩き台。**あなたのアカウントで実際に提携できて、EC一人社長に刺さる広告主が他にあれば差し替え・追加可**。その場合は「ツール名 / 紹介文1行 / 公式URL / アフィURL」をくれれば Claude が tools.json に新カードを足す。
- 担当に「EC開業・一人社長向けに出せる広告主リスト」を聞けるなら、それが一番早い（取扱いが一覧で分かる）。

## 渡し方（どちらでも）
1. このファイルの「貼る欄」に直接ペーストして保存 → Claude に「投入した」と言う
2. or チャットに「base: https://... / freee: https://...」と貼る → Claude が反映
