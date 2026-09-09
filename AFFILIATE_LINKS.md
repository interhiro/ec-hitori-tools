# アフィリンク投入シート（運営者 → Claude）

**ASPはA8.net一本。** 6ツールの取り扱いを1件ずつ実地調査した結果、
BASE・カラーミー・freee・minne・ラクスルが全てA8にあり、afbは該当ゼロ、
もしもはfreeeのみでA8と重複だったため。詳細は提携申請時の調査記録を参照。
**やること: 管理画面で各ツールの広告主と提携 → 発行されたアフィリンクURLを下の「貼る欄」にペーストするだけ。**
1つでも埋めてくれれば Claude が tools.json に反映 → `build.py` 再実行 → LP に即反映（`data-monetized="true"` になる）。

> リンクは「素のアフィURL」でOK。動画別トラッキング（?v=）は LP 側の track.js が自動付与するので、ここでは付けなくて良い。
> どのASPで提携したかは任意メモ（成果照合の参考）。

| tools.json の id | ツール | 申請先ASP | 状態 | 貼る欄（アフィURL） |
|---|---|---|---|---|
| base | BASE | A8.net | 申請済み(2026-08-12) | <a href="https://px.a8.net/svt/ejp?a8mat=4BA419+E22MDM+2QQG+68EPE" rel="nofollow">自由ワード</a>
<img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4BA419+E22MDM+2QQG+68EPE" alt="">|
| colormeshop | カラーミーショップ | A8.net | 申請済み(2026-08-12) | 個人事業主・中小企業にぴったり！理想のオリジナルネットショップが作れます。<br>
【 <A href="https://px.a8.net/svt/ejp?a8mat=4BA419+E1H6RU+348+I2I7M" rel="nofollow">カラーミーショップ</A> 】
<img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4BA419+E1H6RU+348+I2I7M" alt="">|
| freee | freee会計 | A8.net | **広告掲載URL提出待ち**(申請2026-08-12) | |
| minne | minne | A8.net | 申請済み(2026-08-12) |<a href="https://px.a8.net/svt/ejp?a8mat=4BA419+EOP3D6+348+2BCWEQ" rel="nofollow">minne</a>
<img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4BA419+EOP3D6+348+2BCWEQ" alt=""> |
| rakusul | ラクスル | A8.net | **承認待ち**(申請2026-08-12) | |

### 提携ステータスの実態（2026-09-09 A8管理画面で確認）

表の「申請済み(2026-08-12)」は**申請日**であって提携成立ではない。混同しないこと。

| ツール | 状態 | 成果報酬 |
|---|---|---|
| ラクスル | **承認待ち**（申込中プログラム s00000013809001） | 注文(税抜)の5%。EPC 13.92 / 確定率 92.44% |
| freee | **広告掲載URLの提出が必要**（承認前） | 未確認 |
| BASE / カラーミー / minne | リンク発行済み・稼働中 | 未確認 |

ラクスルは注文単価¥5,000で報酬¥250、¥10,000でも¥500。**単価の実態を把握してから主役の案件を決める。**

freee の広告掲載URLとして提出するのは、freee リンクが実在する本番3ページ（2026-09-09 実測・各1本・HTTP200）:

- `https://interhiro.github.io/ec-hitori-tools/`
- `https://interhiro.github.io/ec-hitori-tools/checklist.html`
- `https://interhiro.github.io/ec-hitori-tools/articles/tools-before-automation.html`

## 実測済みの着地先（2026-09-09、デスクトップUAでクリック確認）

| id | 着地先 | 判定 |
|---|---|---|
| base | `thebase.com/?...&a8=<token>` | OK |
| colormeshop | `shop-pro.jp/lp/202305/?...&a8=<token>` | OK |
| minne | `minne.com/?a8` | OK |
| freee | `px.a8.net/qr_code/qr_code.html?rawquerystring=...` | **NG** |

**freee のリンクはスマートデバイス専用。** PCからクリックすると「このページはスマートデバイス専用URLです。」の
QRコードページで行き止まりになる。URLの形式は他と同じ `px.a8.net/svt/ejp?a8mat=...` で、
`grep` でも目視でも区別がつかない。**クリックして着地先を読むまで分からない。**

YouTube Shorts 流入は大半がモバイルのため実害は限定的だが、PC訪問者は購入導線を失う。

**やること（運営者）: A8管理画面で freee のPC用リンクを取得する。** ログイン後の画面操作と転記は Claude が代行できる。

確認コマンド（リンクを差し替えたら必ず実行する）:

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
curl -s -A "$UA" -L -o /dev/null -w "%{url_effective}\n" "<A8のURL>&id1=verify"
```

着地先に `qr_code` が含まれていたらスマートデバイス専用リンク。取り直す。

### チェックリストページの収益導線（2026-09-09 追加）

`checklist.html` は章の直後に1枚だけCTAを置く。対応は `build.py` の `CHECKLIST_TOOL_SLOTS`:

- 「開業前」章 → **freee**（開業届・青色申告・売上用口座）
- 「ショップを作る」章 → **BASE**（決済・URL・特商法表記）

subid は `checklist` 固定（動画経由の `?v=`、記事経由の `article-<slug>` と成果を切り分けるため）。

### 申請していないもの（記録）

| ツール | 理由 |
|---|---|
| プリントパック | A8.netに取り扱いが無いことを管理画面で確認(2026-08-12) |
| Shopify | ASP外(公式Shopify Partners)。開業直後の視聴者には月額固定費が壁で、対応する動画も薄い |
| Canva Pro | ASP外(Canvassador / Impact経由)。必要になれば別途取得する |
| Lステップ | ASP外。正規代理店制度が本線で、一人作家の段階には早い |

## 補足
- **Canva** は A8/afb/もしも に無い。Canva公式 Canvassador（Impact 経由）で発行 → そのリンクをcanva欄に貼る。面倒なら canva 行は空のままでOK（公式URLにフォールバックし続ける）。
- 上の6つは叩き台。**あなたのアカウントで実際に提携できて、EC一人社長に刺さる広告主が他にあれば差し替え・追加可**。その場合は「ツール名 / 紹介文1行 / 公式URL / アフィURL」をくれれば Claude が tools.json に新カードを足す。
- 担当に「EC開業・一人社長向けに出せる広告主リスト」を聞けるなら、それが一番早い（取扱いが一覧で分かる）。

## 渡し方（どちらでも）
1. このファイルの「貼る欄」に直接ペーストして保存 → Claude に「投入した」と言う
2. or チャットに「base: https://... / freee: https://...」と貼る → Claude が反映
