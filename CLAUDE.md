# ec-hitori-tools

Pillar B(YouTube「ひとりネットショップ研究所」×アフィリエイト)の**収益変換部**。
サイトの仕組み・ビルド手順は`README.md`を読む。

## Shortsを作るとき(必ず最初に読む)

**`videos/CTA-SPEC.md`を読んでから合成を書く。** 動画本体に入れるCTAの位置・文言・
`data-cta-role`属性が決まっている。ドキュメントを読み飛ばせないよう`cta_contract.py`が検査する。

公開前に必ず通す:

```sh
python3 publish_check.py         # 画像が主役か + 出所記録があるか(違反で exit 1)
python3 cta_contract.py          # 動画本体のCTA契約(違反で exit 1)
python3 -m pytest -q             # 全テスト
```

**手本は `videos/product-size-photo`（2026-08-31）だけ。** `product-detail-photo` を手本にしない。
CSS作図で代替してはいけない（2026-09-05に2本続けて差し戻された)。

画像は `image_pipeline.py` から作る。**Codexが既定、APIキーは代替**（2026-09-05に配線）。

```sh
python3 image_pipeline.py --prompt "..." --out videos/<slug>/assets/<name>.png --size 1024x1536
```

Codexの組み込み `image_gen` を先に試し、**未ログイン・利用上限のときだけ** `OPENAI_API_KEY`
（環境変数 → keychain `openai` の順で解決）で `~/.codex/skills/.system/imagegen` のCLIに落ちる。
出所は `ASSETS.md` に自動で追記される。**両方駄目なら exit 1 で止まる。CSS作図に落ちない。**
Codexが `未ログイン` と出たら `codex login` を運用者に依頼する（本人認証なので代行できない）。

公開したあとは、概要欄側も必ず検査する。**動画本体のCTAと概要欄のLPリンクは別の穴で、
前者だけ通しても収益導線は欠けうる**（2026-08-27に実際に起きた）。

```sh
python3 ~/projects/shimayama-ops/scripts/check_lp_link.py --recent 6
```

HyperFramesの合成そのものを書くときは、各動画ディレクトリの`CLAUDE.md`の指示どおり
`/hyperframes`をinvokeしてから着手する。

**公開済み動画は作り直さない。** Shortsは公開後3〜4日で配信が終わるため、
再レンダしても新規視聴者は来ず、既存の再生数だけを失う(2026-08-23にn=9で確認)。

## 市場接触の記帳

公開・LP変更・測定は`~/projects/shimayama-ops/state/market_contact_ledger.csv`に記帳する。
**記帳していない公開は、市場接触として存在しない扱いになる。**
2026-08-25から9/4まで記帳が10日間止まり、その間のShorts 12本が台帳から抜けた。

## 未計測を0と書かない

GA4・A8の数値が取れなかったときは`未取得`と書く。`0`と書かない。
90日計画の計上条件であり、取れなかったことと0だったことは別の情報である。
