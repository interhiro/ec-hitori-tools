const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const {
  appendSubId,
  getVideoSlug,
  getTrackingSource,
  sanitizeSubId,
  getSourceId,
  buildMeasurementPayload,
  emitMeasurementEvent,
  isGa4MeasurementId,
  measurementStatus,
} = require('../track.js');

let pass = 0, fail = 0;
function t(name, fn) {
  try { fn(); console.log('ok   - ' + name); pass++; }
  catch (e) { console.log('FAIL - ' + name + ': ' + e.message); fail++; }
}

function bootBrowserTracking(search) {
  let domReady;
  const delivered = [];
  const cta = {
    attrs: {
      'data-base-href': 'https://aff.example/tool',
      'data-subid-param': 'id1',
    },
    listeners: {},
    getAttribute(name) { return this.attrs[name] || null; },
    setAttribute(name, value) { this.attrs[name] = value; },
    addEventListener(name, handler) { this.listeners[name] = handler; },
    click() { if (this.listeners.click) this.listeners.click(); },
  };
  const document = {
    addEventListener(name, handler) {
      if (name === 'DOMContentLoaded') domReady = handler;
    },
    querySelectorAll(selector) {
      if (selector === 'a.cta[data-base-href]') return [cta];
      if (selector === 'a[data-list-signup="true"]') return [];
      if (selector === 'script[src]') return [{ src: 'https://example.test/track.js' }];
      return [];
    },
    dispatchEvent(event) { delivered.push(event.detail); },
    createElement() { return {}; },
    head: { appendChild() {} },
  };
  class CustomEvent {
    constructor(name, init) {
      this.name = name;
      this.detail = init.detail;
    }
  }
  const context = {
    document,
    window: {
      location: { search, href: `https://example.test/${search}` },
      fetch: undefined,
    },
    CustomEvent,
    URL,
    URLSearchParams,
    Promise,
    module: { exports: {} },
  };
  vm.runInNewContext(
    fs.readFileSync(path.join(__dirname, '..', 'track.js'), 'utf8'),
    context,
  );
  domReady();
  return { cta, delivered };
}

t('appendSubId adds param to a clean url', () => {
  assert.strictEqual(
    appendSubId('https://aff.example/canva', 'utm_content', 'ec-tips-01'),
    'https://aff.example/canva?utm_content=ectips01'
  );
});

t('appendSubId merges with existing query', () => {
  const out = appendSubId('https://aff.example/x?id=9', 'utm_content', 'ec-tips-02');
  assert.ok(out.includes('id=9'));
  assert.ok(out.includes('utm_content=ectips02'));
});

t('appendSubId returns base unchanged when no slug', () => {
  assert.strictEqual(
    appendSubId('https://aff.example/x', 'utm_content', ''),
    'https://aff.example/x'
  );
});

t('appendSubId overwrites an existing subid param', () => {
  const out = appendSubId('https://aff.example/x?utm_content=old', 'utm_content', 'new');
  assert.ok(out.includes('utm_content=new'));
  assert.ok(!out.includes('utm_content=old'));
});

t('getVideoSlug reads v param', () => {
  assert.strictEqual(getVideoSlug('?v=ec-tips-07&foo=1'), 'ec-tips-07');
});

t('getVideoSlug empty when absent', () => {
  assert.strictEqual(getVideoSlug('?foo=1'), '');
});

t('getTrackingSource uses a page default when v is absent', () => {
  assert.strictEqual(getTrackingSource('?foo=1', 'article-opening'), 'article-opening');
});

t('getTrackingSource gives a YouTube v value priority over the page default', () => {
  assert.strictEqual(getTrackingSource('?v=ec-tips-12', 'article-opening'), 'ec-tips-12');
});

t('sanitizeSubId strips characters A8 rejects', () => {
  // A8のパラメータ計測は「半角英数字のみ」。ハイフンを含む slug をそのまま
  // 渡すと計測が落ちる可能性がある(公式: 最大50byte・記号不可)。
  assert.strictEqual(sanitizeSubId('ec-tips-06'), 'ectips06');
  assert.strictEqual(sanitizeSubId('short_01'), 'short01');
  assert.strictEqual(sanitizeSubId('動画01'), '01');
});

t('sanitizeSubId caps length at 50 bytes', () => {
  assert.strictEqual(sanitizeSubId('a'.repeat(80)).length, 50);
});

t('appendSubId sanitizes the value before attaching', () => {
  const out = appendSubId('https://aff.example/x', 'id1', 'ec-tips-06');
  assert.ok(out.includes('id1=ectips06'), out);
  assert.ok(!out.includes('ec-tips-06'), out);
});

t('appendSubId preserves plus signs in an A8 link', () => {
  // a8mat の「+」が壊れるとリンクごと無効になる。
  const a8 = 'https://px.a8.net/svt/ejp?a8mat=4BA419+E22MDM+2QQG+68EPE';
  const out = appendSubId(a8, 'id1', 'ec-tips-06');
  assert.ok(out.includes('a8mat=4BA419+E22MDM+2QQG+68EPE'), out);
  assert.ok(out.includes('id1=ectips08'.replace('08', '06')), out);
});

t('getSourceId gives explicit source_id priority over v', () => {
  assert.strictEqual(
    getSourceId('?v=ec-tips-09&source_id=yt_short_photo_aar5wmqvi0'),
    'yt_short_photo_aar5wmqvi0'
  );
});

t('getSourceId keeps historical v attribution when source_id is absent', () => {
  assert.strictEqual(getSourceId('?v=ec-tips-09'), 'ec-tips-09');
});

t('buildMeasurementPayload records lp_view with its source_id', () => {
  assert.deepStrictEqual(
    buildMeasurementPayload(
      'lp_view',
      '?source_id=yt_channel_profile',
      '',
      'https://interhiro.github.io/ec-hitori-tools/?source_id=yt_channel_profile&email=not-for-analytics@example.test'
    ),
    {
      event_name: 'lp_view',
      source_id: 'yt_channel_profile',
      page_path: '/ec-hitori-tools/',
    }
  );
});

t('source_id-only visits still record affiliate_click', () => {
  const browser = bootBrowserTracking('?source_id=yt_channel_profile');
  browser.cta.click();
  assert.deepStrictEqual(
    browser.delivered.map((payload) => payload.event_name),
    ['lp_view', 'affiliate_click']
  );
  assert.strictEqual(browser.delivered[1].source_id, 'yt_channel_profile');
});

t('emitMeasurementEvent sends affiliate_click with source_id to its reporter', () => {
  const received = [];
  emitMeasurementEvent(
    (payload) => received.push(payload),
    'affiliate_click',
    '?v=ec-tips-09&source_id=yt_short_photo_aar5wmqvi0',
    '',
    'https://interhiro.github.io/ec-hitori-tools/?v=ec-tips-09&source_id=yt_short_photo_aar5wmqvi0'
  );
  assert.strictEqual(received.length, 1);
  assert.strictEqual(received[0].event_name, 'affiliate_click');
  assert.strictEqual(received[0].source_id, 'yt_short_photo_aar5wmqvi0');
});

t('emitMeasurementEvent sends list_signup with source_id to its reporter', () => {
  const received = [];
  emitMeasurementEvent(
    (payload) => received.push(payload),
    'list_signup',
    '?source_id=yt_channel_profile',
    '',
    'https://interhiro.github.io/ec-hitori-tools/?source_id=yt_channel_profile'
  );
  assert.strictEqual(received.length, 1);
  assert.strictEqual(received[0].event_name, 'list_signup');
  assert.strictEqual(received[0].source_id, 'yt_channel_profile');
});

t('measurementStatus distinguishes a configured observer from unobserved', () => {
  assert.strictEqual(isGa4MeasurementId('G-AB12CD34'), true);
  assert.strictEqual(measurementStatus({ measurement_id: 'G-AB12CD34' }), 'active');
  assert.strictEqual(measurementStatus({ measurement_id: '' }), 'unobserved');
});

console.log(`\nPASS=${pass} FAIL=${fail}`);
process.exit(fail === 0 ? 0 : 1);
