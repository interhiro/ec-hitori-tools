// 動画別トラッキング: LP の URL に付いた ?v=<動画スラッグ> を読み、
// 各アフィリンクの sub-id パラメータとして付与する。
// これで「どの動画がクリック/成約させたか」が ASP 管理画面の sub-id 別レポートで分かる。
// バックエンド不要・完全クライアントサイド。

// A8.netのパラメータ計測は「半角英数字のみ・最大50byte」。記号を含む値を
// そのまま渡すと計測が落ちる。動画スラッグ(ec-tips-06)を安全な形に均す。
function sanitizeSubId(value) {
  return String(value || '').replace(/[^0-9A-Za-z]/g, '').slice(0, 50);
}

// テスト可能な純粋関数: base URL に subid パラメータを付与して返す。
function appendSubId(baseHref, subidParam, videoSlug) {
  var subid = sanitizeSubId(videoSlug);
  if (!subid) return baseHref;
  try {
    var u = new URL(baseHref);
    u.searchParams.set(subidParam, subid);
    return u.toString();
  } catch (e) {
    // 相対URL等で URL() が失敗した場合は素朴に連結
    var sep = baseHref.indexOf('?') === -1 ? '?' : '&';
    return baseHref + sep + encodeURIComponent(subidParam) + '=' + encodeURIComponent(subid);
  }
}

function getVideoSlug(search) {
  var params = new URLSearchParams(search || '');
  return params.get('v') || '';
}

// ブラウザ実行: 全 .cta リンクを書き換える
if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', function () {
    var slug = getVideoSlug(window.location.search);
    if (!slug) return;
    var links = document.querySelectorAll('a.cta[data-base-href]');
    links.forEach(function (a) {
      var base = a.getAttribute('data-base-href');
      var param = a.getAttribute('data-subid-param') || 'utm_content';
      a.setAttribute('href', appendSubId(base, param, slug));
    });
  });
}

// node テスト用エクスポート
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { appendSubId: appendSubId, getVideoSlug: getVideoSlug, sanitizeSubId: sanitizeSubId };
}
