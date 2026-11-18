import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const html = readFileSync(new URL('../tokyo-guide_2.html', import.meta.url), 'utf8');

test('quick genre and sort controls are discoverable and accessible', () => {
  assert.match(html, /id="ej-genre-select" aria-label="Choose a specific genre"/);
  assert.match(html, /id="ej-sort-select" aria-label="Group and sort places"/);
  assert.match(html, /Name Z–A/);
  assert.match(html, /Neighborhood A–Z/);
});
test('quick controls reuse the existing category and sorting state', () => {
  assert.match(html, /STATE\[city\]\.cats=ejGenreSelect\.value/);
  assert.match(html, /st\.sort=sort;st\.dir=dir;/);
  assert.match(html, /ejSyncQuickFind\(\)/);
  assert.match(html, /ejRefreshAll\(\);ejUpdateLocationControls\(\);ejSyncURL\(true\)/);
});
test('existing 526 addresses are unchanged', () => {
  assert.equal(html.split('name:"').length-1, 526);
});
