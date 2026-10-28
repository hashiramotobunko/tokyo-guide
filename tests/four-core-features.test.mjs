import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const html=readFileSync(new URL('../tokyo-guide_2.html',import.meta.url),'utf8');
test('all four requested feature entry points exist',()=>{
 for(const id of ['browse','fieldnotes','visitor-info','mood']){
  assert.match(html,new RegExp('id="'+id+'"'));
  assert.ok(html.includes('href="#'+id+'"'),id+' link missing');
 }
});
test('region and area dropdowns are present',()=>{
 assert.ok(html.includes('id="ej-region-select"'));
 assert.ok(html.includes('id="ej-area-select"'));
 assert.ok(html.includes('id="ej-search"'));
});
test('walking route browser can filter ideas',()=>{
 assert.ok(html.includes('id="ej-route-options"'));
 assert.ok(html.includes('id="ej-route-area"'));
 assert.ok(html.includes('id="ej-field-list"'));
 assert.ok(html.includes('UNVERIFIED WALKING ROUTE'));
});
test('visitor essentials are data-grounded and sourced',()=>{
 assert.ok(html.includes('function ejPracticalField('));
 assert.ok(html.includes('function ejPracticalCitation('));
 assert.ok(html.includes('const EJ_PRACTICAL='));
 assert.ok(html.includes('id="visitor-info"'));
});
test('theme / mood selections use the actual category filter',()=>{
 assert.ok(html.includes('id="ej-mood-list"'));
 assert.ok(html.includes('function ejMoodMatches('));
 assert.ok(html.includes('if(ejMood)filtered=filtered.filter(ejMoodMatches)'));
});
test('the original approved 526 source entries are present',()=>{
 assert.equal((html.split('name:"').length-1),526);
});
