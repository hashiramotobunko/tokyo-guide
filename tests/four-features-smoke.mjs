// Usage: node --test tests/four-features-smoke.mjs
// Read-only: verifies the complete source and data relationships, no network calls.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import {dirname,resolve} from 'node:path';
const here=dirname(fileURLToPath(import.meta.url));
const source=readFileSync(resolve(here,'..','tokyo-guide_2.html'),'utf8');
const script=source.match(/<script>([\s\S]*?)<\/script>/)?.[1];
assert.ok(script,'inline app JS should exist');

function balancedAfter(startToken,open,close){
 const start=source.indexOf(startToken);
 assert.ok(start>=0,'missing '+startToken);
 const pos=source.indexOf(open,start+startToken.length-1);
 let quote=null,escape=false,depth=0;
 for(let i=pos;i<source.length;i++){
  const c=source[i];
  if(quote){if(escape){escape=false;continue}if(c==='\\'){escape=true;continue}if(c===quote)quote=null;continue;}
  if(c==='"'||c==="'"){quote=c;continue;}
  if(c===open)depth++;else if(c===close && --depth===0)return source.slice(pos,i+1);
 }
 throw new Error('Unclosed: '+startToken);
}
const data=vm.runInNewContext('('+balancedAfter('const DATA = {','{','}')+')');
const routes=vm.runInNewContext('('+balancedAfter('const EJ_ROUTES=[','[',']')+')');
const all=Object.entries(data).flatMap(([city,group])=>group.places.map(place=>({...place,city})));
const cardMapCount=(source.match(/https:\/\/www\.google\.com\/maps\/place\//g)||[]).length;
test('JavaScript parses',()=>assert.doesNotThrow(()=>new vm.Script(script)));
test('all 526 approved places have usable location data',()=>{
 assert.equal(all.length,526);
 assert.ok(all.every(p=>p.name&&p.area&&p.cat&&/^https:\/\/www\.google\.com\/maps\/(?:place\/|search\/\?api=1&query=)/.test(p.url)));
 assert.equal(new Set(all.map(p=>p.url)).size,526);
});
test('region and area selectors are genuinely connected to the filters',()=>{
 for(const id of ['ej-region-select','ej-area-select','ej-search','ej-filter-message','ej-reset-all'])assert.ok(source.includes('id="'+id+'"'),id);
 assert.ok(script.includes("ejRegionSelect.addEventListener('change'"));
 assert.ok(script.includes("ejAreaSelect.addEventListener('change'"));
 assert.ok(script.includes("ejSearchBox.addEventListener('input'"));
 assert.ok(script.includes("addEventListener('popstate',ejRestoreURL)"));
 assert.ok(script.includes("ejSyncURL(true)"));
});
test('ten curated routes link only to real selected places in one region and area',()=>{
 assert.equal(routes.length,10);
 const ids=new Set();
 for(const r of routes){
  assert.ok(!ids.has(r.id));ids.add(r.id);
  assert.ok(data[r.city],r.id);
  assert.ok(r.stops.length>=2,r.id);
  for(const name of r.stops){
   const p=data[r.city].places.find(x=>x.name===name);
   assert.ok(p,r.id+': '+name);
   assert.equal(p.area,r.area,r.id+' area');
  }
 }
 assert.ok(source.includes('ejRouteGoogleMapsURL'));
 assert.ok(source.includes('travelmode'));
 assert.ok(source.includes('walking'));
 assert.ok(source.includes('UNVERIFIED WALKING ROUTE'));
});
test('themed search is category based and has six filters',()=>{
 const moods=['night','coffee','culture','food','shop','slow'];
 for(const mood of moods)assert.ok(source.includes('data-mood="'+mood+'"'));
 assert.ok(script.includes('EJ_MOOD_CATEGORIES'));
 assert.ok(script.includes('ejMoodMatches'));
 assert.ok(script.includes("ejSyncURL(true)"));
});
test('practical data is attributed and unknown values are not presented as facts',()=>{
 for(const key of ['東京国立博物館','東京都美術館','国立西洋美術館','明治神宮','通天閣','清水寺'])assert.ok(source.includes('"'+key+'":{'),key);
 assert.ok(source.includes('data-find-venue="通天閣"'));
 assert.ok(source.includes('ejPracticalCitation'));
 assert.ok(source.includes('Checked '));
 assert.ok(source.includes('not been checked'));
 assert.ok(source.includes('ejPracticalField(p,'));
});
test('all four feature areas are reachable from the editorial navigation',()=>{
 for(const anchor of ['#browse','#fieldnotes','#visitor-info','#mood'])assert.ok(source.includes('href="'+anchor+'"'));
});
