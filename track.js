// 動画別トラッキング: LP の URL に付いた ?v=<動画スラッグ> を読み、
// 各アフィリンクの sub-id パラメータとして付与する。
// これで「どの動画がクリック/成約させたか」が ASP 管理画面の sub-id 別レポートで分かる。
// バックエンド不要・完全クライアントサイド。

// テスト可能な純粋関数: base URL に subid パラメータを付与して返す。
function appendSubId(baseHref, subidParam, videoSlug) {
  if (!videoSlug) return baseHref;
  try {
    var u = new URL(baseHref);
    u.searchParams.set(subidParam, videoSlug);
    return u.toString();
  } catch (e) {
    // 相対URL等で URL() が失敗した場合は素朴に連結
    var sep = baseHref.indexOf('?') === -1 ? '?' : '&';
    return baseHref + sep + encodeURIComponent(subidParam) + '=' + encodeURIComponent(videoSlug);
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
  module.exports = { appendSubId: appendSubId, getVideoSlug: getVideoSlug };
}
