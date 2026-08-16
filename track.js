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

// ?v= が無い流入（検索から補足ノートへ来た場合など）は、ページ側で渡した
// 既定値を使う。YouTube 経由の値が常に優先される。
function getTrackingSource(search, fallback) {
  return getVideoSlug(search) || fallback || '';
}

// source_id は LP 上の行動イベントを流入元ごとに分けるための値。既存の
// ?v= は A8 の id1 用としてそのまま優先順位を保ち、source_id があるときだけ
// イベント計測の帰属をより細かくする。
function sanitizeSourceId(value) {
  return String(value || '').replace(/[^0-9A-Za-z_-]/g, '').slice(0, 80);
}

function getSourceId(search, fallback) {
  var params = new URLSearchParams(search || '');
  return sanitizeSourceId(
    params.get('source_id') || getTrackingSource(search, fallback)
  );
}

function getSafePagePath(pageLocation) {
  try {
    return new URL(pageLocation || '', 'https://measurement.invalid').pathname;
  } catch (e) {
    return String(pageLocation || '/').split(/[?#]/, 1)[0] || '/';
  }
}

function buildMeasurementPayload(eventName, search, fallback, pageLocation) {
  return {
    event_name: eventName,
    source_id: getSourceId(search, fallback) || 'unattributed',
    // URLクエリには想定外の個人情報が入り得るため、計測にはパスだけを渡す。
    page_path: getSafePagePath(pageLocation),
  };
}

function emitMeasurementEvent(reporter, eventName, search, fallback, pageLocation) {
  var payload = buildMeasurementPayload(eventName, search, fallback, pageLocation);
  if (typeof reporter === 'function') reporter(payload);
  return payload;
}

function isGa4MeasurementId(value) {
  return /^G-[A-Z0-9]{4,}$/.test(String(value || ''));
}

function measurementStatus(config) {
  return isGa4MeasurementId(config && config.measurement_id) ? 'active' : 'unobserved';
}

function getMeasurementConfigUrl() {
  var scripts = document.querySelectorAll('script[src]');
  for (var i = 0; i < scripts.length; i += 1) {
    var src = scripts[i].src || '';
    if (/\/track\.js(?:\?|$)/.test(src)) {
      return new URL('measurement.config.json', src).toString();
    }
  }
  return 'measurement.config.json';
}

function dispatchBrowserMeasurementEvent(payload) {
  document.dispatchEvent(new CustomEvent('lp_measurement', { detail: payload }));
}

function createGa4Reporter(measurementId) {
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  gtag('js', new Date());
  // 自動 page_view は任意のクエリ文字列を送るため止め、下の lp_view のみを送る。
  gtag('config', measurementId, { send_page_view: false });

  var script = document.createElement('script');
  script.async = true;
  script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(measurementId);
  document.head.appendChild(script);

  return function (payload) {
    gtag('event', payload.event_name, {
      source_id: payload.source_id,
      page_path: payload.page_path,
    });
  };
}

function loadMeasurementConfig() {
  if (typeof window.fetch !== 'function') return Promise.resolve(null);
  return window.fetch(getMeasurementConfigUrl(), { cache: 'no-store' })
    .then(function (response) { return response.ok ? response.json() : null; })
    .catch(function () { return null; });
}

// ブラウザ実行: 全 .cta リンクを書き換える
if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', function () {
    var queuedEvents = [];
    var report = function (payload) {
      dispatchBrowserMeasurementEvent(payload);
      queuedEvents.push(payload);
    };
    var pageLocation = window.location.href;

    emitMeasurementEvent(report, 'lp_view', window.location.search, '', pageLocation);

    var links = document.querySelectorAll('a.cta[data-base-href]');
    links.forEach(function (a) {
      var defaultSubid = a.getAttribute('data-default-subid') || '';
      a.addEventListener('click', function () {
        emitMeasurementEvent(
          report,
          'affiliate_click',
          window.location.search,
          defaultSubid,
          pageLocation
        );
      });

      var slug = getTrackingSource(
        window.location.search,
        defaultSubid
      );
      if (!slug) return;
      var base = a.getAttribute('data-base-href');
      var param = a.getAttribute('data-subid-param') || 'utm_content';
      a.setAttribute('href', appendSubId(base, param, slug));
    });

    var listLinks = document.querySelectorAll('a[data-list-signup="true"]');
    listLinks.forEach(function (a) {
      a.addEventListener('click', function () {
        // GitHub Pages からは Google Form の完了送信を読めないため、ここでは
        // リスト登録フォームを開いた時点を list_signup として記録する。
        emitMeasurementEvent(report, 'list_signup', window.location.search, '', pageLocation);
      });
    });

    loadMeasurementConfig().then(function (config) {
      if (measurementStatus(config) !== 'active') return;
      var sendToGa4 = createGa4Reporter(config.measurement_id);
      queuedEvents.forEach(sendToGa4);
      queuedEvents = [];
      report = function (payload) {
        dispatchBrowserMeasurementEvent(payload);
        sendToGa4(payload);
      };
    });
  });
}

// node テスト用エクスポート
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    appendSubId: appendSubId,
    getVideoSlug: getVideoSlug,
    getTrackingSource: getTrackingSource,
    sanitizeSubId: sanitizeSubId,
    sanitizeSourceId: sanitizeSourceId,
    getSourceId: getSourceId,
    getSafePagePath: getSafePagePath,
    buildMeasurementPayload: buildMeasurementPayload,
    emitMeasurementEvent: emitMeasurementEvent,
    isGa4MeasurementId: isGa4MeasurementId,
    measurementStatus: measurementStatus,
  };
}
