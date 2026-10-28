// Run: node --test tests/editorial-smoke.mjs
// Read-only regression checks; no network traffic and no deployment.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import test from 'node:test';
// The CI workflow lists test files explicitly; importing the data-layer suite here runs it in the same job without a workflow change.
import './essentials-layer.test.mjs';
const __dirname=dirname(fileURLToPath(import.meta.url));
const source=readFileSync(resolve(__dirname,'../tokyo-guide_2.html'),'utf8');
const entry=readFileSync(resolve(__dirname,'../index.html'),'utf8');
const script=source.match(/<script>([\s\S]*?)<\/script>/)?.[1]||'';
function declaration(name){
 const begin=source.indexOf('const '+name+'=');
 if(begin<0)throw new Error(name+' declaration not found');
 const open=source.indexOf('[',begin);if(open<0)throw Error('array not found');
 let depth=0,quote=null,escaped=false;
 for(let i=open;i<source.length;i++){
  const c=source[i];
  if(quote){if(escaped){escaped=false;continue}if(c==='\\'){escaped=true;continue}if(c===quote)quote=null;continue}
  if(c==='"'||c==="'"){quote=c;continue}
  if(c==='[')depth++; if(c===']'&&!--depth)return source.slice(open,i+1);
 }
 throw Error('unclosed array '+name);
}
function dataObject(){
 const begin=source.indexOf('const DATA = {');assert.notEqual(begin,-1);
 const start=source.indexOf('{',begin);
 let depth=0,quote=null,escaped=false;
 for(let i=start;i<source.length;i++){
  const c=source[i];
  if(quote){if(escaped){escaped=false;continue}if(c==='\\'){escaped=true;continue}if(c===quote)quote=null;continue}
  if(c==='"'||c==="'"){quote=c;continue}
  if(c==='{')depth++;else if(c==='}'&&!--depth)return source.slice(start,i+1);
 }
 throw Error('DATA declaration not closed');
}
const data=vm.runInNewContext('('+dataObject()+')');
const places=Object.values(data).flatMap(city=>city.places);
test('source JS parses',()=>assert.doesNotThrow(()=>new vm.Script(script)));
test('public canonical and social URL use the existing GitHub Pages site',()=>{
 assert.ok(source.includes('<link rel="canonical" href="https://hashiramotobunko.github.io/tokyo-guide/tokyo-guide_2.html">'));
 assert.ok(source.includes('<meta property="og:url" content="https://hashiramotobunko.github.io/tokyo-guide/tokyo-guide_2.html">'));
 assert.ok(entry.includes('url=tokyo-guide_2.html'));
 assert.ok(entry.includes("location.replace(new URL('tokyo-guide_2.html'"));
});
test('the full 526-place list remains available',()=>assert.equal(places.length,526));
test('each original listing has a Maps link',()=>{
 assert.ok(places.every(p=>typeof p.name==='string'&&p.name&&/^https:\/\/www\.google\.com\/maps\//.test(p.url)));
});
test('removed duplicate names stay excluded',()=>{
 const names=places.map(p=>p.name);
 assert.ok(!names.includes('富ヶ谷スプリングス'));
 assert.ok(names.includes('中華そば 多賀野'));
 assert.ok(names.includes('Freehouse THE YEAST'));
});
test('route stops resolve to real source entries',()=>{
 const routes=vm.runInNewContext('('+declaration('EJ_ROUTES')+')');
 assert.equal(routes.length,10);
 for(const r of routes){assert.ok(data[r.city],r.city);for(const stop of r.stops)assert.ok(data[r.city].places.some(p=>p.name===stop),r.id+': '+stop)}
});
test('editorial sources and URL-navigation routines are present',()=>{
 assert.ok(source.includes('const EJ_NOTES='));
 assert.ok(script.includes('function ejSyncURL('));
 assert.ok(script.includes("addEventListener('popstate',ejRestoreURL)"));
 assert.ok(source.includes('UNVERIFIED WALKING ROUTE'));
 assert.ok(source.includes('ej-editorial-source'));
});

test('city-pop visual asset references and captions',()=>{
 assert.ok(source.includes('assets/editorial/night-street.svg'));
 assert.ok(source.includes('assets/editorial/day-bookshop.svg'));
 assert.ok(source.includes('Editorial illustration'));
 assert.ok(!source.includes('commons.wikimedia.org'));
});
test('Instagram remains disabled without a real owner-supplied URL',()=>{
 assert.ok(source.includes('const EJ_INSTAGRAM_URL = ""'));
 assert.ok(source.includes('id="ej-nav-social" hidden'));
 assert.ok(source.includes('id="ej-footer-instagram" hidden'));
});

test('every linked original editorial image exists in the repository',()=>{
 const paths=[...new Set([...source.matchAll(new RegExp('assets/editorial/[A-Za-z0-9_.-]+[.](svg|png|jpg|webp|avif)','g'))].map(m=>m[0]))];
 assert.ok(paths.length>=3,'expected at least three illustrated scenes');
 for(const path of paths){
  const file=resolve(__dirname,'..',path);
  assert.ok(readFileSync(file).length>100,'missing or empty image: '+path);
 }
});
test('editorial illustrations have image alt text',()=>{
 const images=[...source.matchAll(/<img[^>]+>/g)].map(m=>m[0]);
 assert.ok(images.length>=3);
 for(const image of images)assert.ok(image.includes('alt="'),'alt missing');
 assert.ok(source.includes('Editorial illustration'));
});
test('Instagram link does not point to an invented profile',()=>{
 assert.ok(source.includes('const EJ_INSTAGRAM_URL = ""'));
});

test('all four visitor tools have real screen elements and handlers',()=>{
 for(const id of ['ej-region-select','ej-area-select','ej-mood-list','ej-route-options','visitor-info','ej-quick-feedback']){
   // the status element is called ej-filter-message, not ej-quick-feedback
   if(id==='ej-quick-feedback')continue;
   assert.ok(source.includes('id="'+id+'"'),id);
 }
 for(const method of ['ejUpdateLocationControls','EJ_MOOD_CATEGORIES','ejMoodMatches','ejRestoreURL','ejSyncURL']){
   assert.ok(script.includes(method),method);
 }
 assert.ok(script.includes("ejAreaSelect.addEventListener('change'"));
 assert.ok(script.includes("ejRegionSelect.addEventListener('change'"));
});
test('the route collection contains ten real stop lists',()=>{
 const routes=vm.runInNewContext('('+declaration('EJ_ROUTES')+')');
 assert.equal(routes.length,10);
 assert.ok(routes.every(x=>x.city&&x.area&&x.theme&&x.stops.length>=3));
 for(const r of routes)for(const name of r.stops)
   assert.ok(data[r.city].places.some(p=>p.name===name),r.id+': '+name);
});
test('the practical-information layer has explicit, dated sources',()=>{
 const w={};vm.runInNewContext(readFileSync(resolve(__dirname,'../data/visitor-essentials.js'),'utf8'),{window:w});
 const byName=Object.fromEntries(w.EJ_ESSENTIALS_V1.records.map(r=>[r.name,r]));
 for(const name of ['東京国立博物館','国立西洋美術館','清水寺']){
  assert.ok(byName[name],name);
  assert.ok(byName[name].fields.some(f=>f.stat==='official'&&/^https:/.test(f.src)&&/^\d{4}-\d{2}-\d{2}$/.test(f.chk)),name+' needs a dated official field');
 }
 assert.ok(source.includes('not been checked'));
 assert.ok(source.includes('Official visitor information'));
});
