const assert = require('assert');
const { appendSubId, getVideoSlug } = require('../track.js');

let pass = 0, fail = 0;
function t(name, fn) {
  try { fn(); console.log('ok   - ' + name); pass++; }
  catch (e) { console.log('FAIL - ' + name + ': ' + e.message); fail++; }
}

t('appendSubId adds param to a clean url', () => {
  assert.strictEqual(
    appendSubId('https://aff.example/canva', 'utm_content', 'ec-tips-01'),
    'https://aff.example/canva?utm_content=ec-tips-01'
  );
});

t('appendSubId merges with existing query', () => {
  const out = appendSubId('https://aff.example/x?id=9', 'utm_content', 'ec-tips-02');
  assert.ok(out.includes('id=9'));
  assert.ok(out.includes('utm_content=ec-tips-02'));
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

console.log(`\nPASS=${pass} FAIL=${fail}`);
process.exit(fail === 0 ? 0 : 1);
