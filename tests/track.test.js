const assert = require('assert');
const { appendSubId, getVideoSlug, getTrackingSource, sanitizeSubId } = require('../track.js');

let pass = 0, fail = 0;
function t(name, fn) {
  try { fn(); console.log('ok   - ' + name); pass++; }
  catch (e) { console.log('FAIL - ' + name + ': ' + e.message); fail++; }
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

console.log(`\nPASS=${pass} FAIL=${fail}`);
process.exit(fail === 0 ? 0 : 1);
