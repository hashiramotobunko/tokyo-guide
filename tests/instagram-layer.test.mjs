// Run: node --test tests/instagram-layer.test.mjs
// The Instagram layer must never invent an account, never show one it could not
// confirm, and never touch the 526 original listings.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import test from 'node:test';

const __dirname = dirname(fileURLToPath(import.meta.url));
const read = p => readFileSync(resolve(__dirname, '..', p), 'utf8');
const page = read('tokyo-guide_2.html');
const ledger = JSON.parse(read('data/instagram-research-ledger.json'));
const site = vm.runInNewContext(read('data/instagram-links.js') + ';EJ_INSTAGRAM');
const HANDLE = /^[A-Za-z0-9._]{1,30}$/;

test('every one of the 526 listings has a research result or a recorded reason', () => {
  assert.equal(ledger.length, 526);
  const seen = new Set();
  for (const r of ledger) {
    assert.ok(['VERIFIED', 'AMBIGUOUS', 'NOT_FOUND'].includes(r.status), r.name + ': ' + r.status);
    assert.ok(r.evidence && r.evidence.length > 20, 'no reason recorded for ' + r.name);
    assert.ok(r.checked_at && /^\d{4}-\d{2}-\d{2}$/.test(r.checked_at), r.name);
    assert.ok(r.maps_url.startsWith('https://www.google.com/maps/'), r.name);
    assert.ok(!seen.has(r.id), 'duplicate id ' + r.id);
    seen.add(r.id);
  }
});

test('an Instagram URL is recorded only where the account was confirmed', () => {
  for (const r of ledger) {
    if (r.status === 'VERIFIED') {
      assert.ok(HANDLE.test(r.instagram_username), r.name + ': bad handle');
      assert.equal(r.instagram_url, `https://www.instagram.com/${r.instagram_username}/`, r.name);
      assert.ok(['store', 'brand'].includes(r.account_type), r.name + ': ' + r.account_type);
      assert.ok(r.evidence_url.startsWith('http'), r.name + ': no evidence URL');
    } else {
      assert.equal(r.instagram_url, '', r.name + ' is ' + r.status + ' but carries a URL');
      assert.equal(r.instagram_username, '', r.name);
    }
  }
});

test('the page data layer holds exactly the confirmed accounts, and no others', () => {
  const verified = ledger.filter(r => r.status === 'VERIFIED');
  assert.equal(Object.keys(site).length, verified.length);
  for (const r of verified) {
    const entry = site[`${r.region}|${r.place_key}`];
    assert.ok(entry, 'missing from data/instagram-links.js: ' + r.name);
    assert.equal(entry.u, r.instagram_username, r.name);
    assert.equal(entry.t, r.account_type, r.name);
  }
  for (const [key, v] of Object.entries(site)) {
    assert.ok(HANDLE.test(v.u), key);
    assert.ok(['store', 'brand'].includes(v.t), key);
  }
});

test('a handle used by more than one listing is filed as a brand account', () => {
  const byHandle = new Map();
  for (const [key, v] of Object.entries(site)) {
    byHandle.set(v.u, [...(byHandle.get(v.u) || []), key]);
  }
  for (const [handle, keys] of byHandle) {
    if (keys.length > 1) {
      for (const k of keys) assert.equal(site[k].t, 'brand', handle + ' is shared by ' + keys.length + ' listings');
    }
  }
});

test('the button is rendered only from the data layer, and opens safely', () => {
  assert.ok(page.includes('<script src="data/instagram-links.js"></script>'));
  assert.ok(page.includes('function ejInstagram(p)'));
  // the link is built from the handle only, and carries both protections
  assert.ok(page.includes(`href="https://www.instagram.com/'+ejHTML(ig.u)+'/"`),
    'the Instagram href must be built from the recorded handle');
  assert.ok(page.includes(`target="_blank" rel="noopener noreferrer"`), 'target and rel must be set');
  // nothing is rendered when there is no record
  assert.ok(page.includes("if(!ig)return '';"), 'no record must render no button');
  // the Google Maps link stays
  assert.ok(page.includes('class="place-map" href="${p.url}"'));
});

test('the Instagram layer does not touch the original listing data', () => {
  assert.ok(!page.includes('instagram') || !/places:\s*\[[^\]]*instagram/i.test(page),
    'instagram data must live in its own file, not inside DATA');
});
