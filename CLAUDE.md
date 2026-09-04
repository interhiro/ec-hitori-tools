# ec-hitori-tools

Pillar B(YouTube「ひとりネットショップ研究所」×アフィリエイト)の**収益変換部**。
サイトの仕組み・ビルド手順は`README.md`を読む。

## Shortsを作るとき(必ず最初に読む)

**`videos/CTA-SPEC.md`を読んでから合成を書く。** 動画本体に入れるCTAの位置・文言・
`data-cta-role`属性が決まっている。ドキュメントを読み飛ばせないよう`cta_contract.py`が検査する。

公開前に必ず通す:

```sh
python3 cta_contract.py          # CTA契約の検査(違反があると exit 1)
python3 -m pytest -q             # 全テスト
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
