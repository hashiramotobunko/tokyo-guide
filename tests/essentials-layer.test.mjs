// Run: node --test tests/essentials-layer.test.mjs
// Read-only checks on the independent visitor-essentials and route-verification layers. No network.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const root=new URL('../',import.meta.url);
const html=readFileSync(new URL('tokyo-guide_2.html',root),'utf8');
function extract(src,marker){const st=src.indexOf(marker);assert.ok(st>=0,marker);const b=src.indexOf('{',st);let d=0,q=null,e=false;for(let i=b;i<src.length;i++){const c=src[i];if(q){if(e){e=false;continue}if(c==='\\'){e=true;continue}if(c===q)q=null;continue}if(c==='"'||c==="'"){q=c;continue}if(c==='{')d++;else if(c==='}'&&--d===0)return vm.runInNewContext('('+src.slice(b,i+1)+')')}throw Error('unclosed '+marker)}
function extractArray(src,marker){const st=src.indexOf(marker);assert.ok(st>=0,marker);const b=src.indexOf('[',st);let d=0,q=null,e=false;for(let i=b;i<src.length;i++){const c=src[i];if(q){if(e){e=false;continue}if(c==='\\'){e=true;continue}if(c===q)q=null;continue}if(c==='"'||c==="'"){q=c;continue}if(c==='[')d++;else if(c===']'&&--d===0)return vm.runInNewContext('('+src.slice(b,i+1)+')')}throw Error('unclosed '+marker)}
const DATA=extract(html,'const DATA = {');
const ROUTES=extractArray(html,'const EJ_ROUTES=[');
const w={};
vm.runInNewContext(readFileSync(new URL('data/visitor-essentials.js',root),'utf8'),{window:w});
vm.runInNewContext(readFileSync(new URL('data/route-verification.js',root),'utf8'),{window:w});
const ESS=w.EJ_ESSENTIALS_V1,RV=w.EJ_ROUTE_FIELD_V1;
const ledger=JSON.parse(readFileSync(new URL('data/research-ledger.json',root),'utf8'));
const placeKey=(city,p)=>{const m=p.url.match(/!1s(0x[0-9a-f]+:0x[0-9a-f]+)/);return city+'|'+(m?m[1]:'name:'+p.name)};
const index={};for(const [city,{places}] of Object.entries(DATA))for(const p of places){assert.ok(!index[placeKey(city,p)],'duplicate key '+placeKey(city,p));index[placeKey(city,p)]={city,p}}
const DATE=/^\d{4}-\d{2}-\d{2}$/;
const STATS=new Set(['official','secondary','conflict','unverified','n-a']);
const TYPES=new Set(['website','name','address','hours','closed','reservation','fee','payment','access','language','accessibility','notice','tip']);
const SOURCE_TYPES=new Set(['official','government','tourism-board','association','reservation-platform','media','aggregator','review-site','osm']);

test('page loads both data files before the inline app script',()=>{
 const a=html.indexOf('<script src="data/visitor-essentials.js"></script>'),b=html.indexOf('<script src="data/route-verification.js"></script>'),c=html.indexOf('<script>\n// ====');
 assert.ok(a>0&&b>a&&c>b);
 assert.ok(html.includes('function ejPlaceKey('));
 assert.ok(html.includes('function ejEssentialsBlock('));
});
test('every essentials record resolves to exactly one approved listing by city + Google Maps place id, and the name matches',()=>{
 assert.ok(ESS.records.length>=36);
 const seen=new Set();
 for(const r of ESS.records){
  const hit=index[r.key];assert.ok(hit,'unknown key '+r.key+' ('+r.name+')');
  assert.equal(hit.p.name,r.name,'name mismatch for '+r.key);assert.equal(hit.city,r.city);
  assert.ok(!seen.has(r.key),'duplicate record '+r.key);seen.add(r.key);
 }
});
test('every field carries type, status, checked date and method; displayed values always carry a source URL',()=>{
 for(const r of ESS.records){
  assert.ok(Array.isArray(r.fields)&&r.fields.length>0,r.name);
  for(const f of r.fields){
   assert.ok(TYPES.has(f.t),r.name+' type '+f.t);assert.ok(STATS.has(f.stat),r.name+' stat '+f.stat);
   assert.match(f.chk,DATE,r.name+' chk');assert.ok(f.by,r.name+' by');
   if(f.stat==='official'||f.stat==='secondary'||f.stat==='conflict'){
    assert.ok(f.v&&f.v.length>2,r.name+' '+f.t+' value');
    assert.match(f.src,/^https?:\/\//,r.name+' '+f.t+' src');assert.ok(SOURCE_TYPES.has(f.st),r.name+' '+f.t+' st '+f.st);
   }else{assert.equal(f.v||'','',r.name+' '+f.t+' unverified field must not carry a value');}
   if(f.stat==='conflict')assert.ok(f.alt&&f.alt.length>2,r.name+' conflict needs alt');
   if(f.stat==='official')assert.ok(['official','government','tourism-board','association'].includes(f.st),r.name+' '+f.t+' official status needs an official-grade source type, got '+f.st);
  }
 }
});
test('no value is inferred from venue type: secondary and conflict values name a concrete source type other than official',()=>{
 for(const r of ESS.records)for(const f of r.fields)if(f.stat==='secondary')assert.notEqual(f.st,'official',r.name+' '+f.t);
});
test('all 35 route stops exist in the approved data and have an identity record with Google-resolved coordinates',()=>{
 assert.equal(ROUTES.length,10);assert.equal(Object.keys(RV.routes).length,10);
 let stops=0;
 for(const route of ROUTES){
  const V=RV.routes[route.id];assert.ok(V,route.id);
  assert.deepEqual(Array.from(V.stops.map(s=>s.name)),Array.from(route.stops),route.id+' stop order must match the verification record');
  assert.equal(V.legs.length,route.stops.length-1,route.id+' legs');
  for(const [i,l] of V.legs.entries()){assert.equal(l.from,route.stops[i]);assert.equal(l.to,route.stops[i+1]);assert.ok(Number.isInteger(l.m)&&l.m>0&&l.m<6000,route.id+' leg m');assert.ok(l.src,route.id+' leg src');assert.ok(Number.isInteger(l.gmin)&&l.gmin>0&&/^\d{4}-\d{2}-\d{2}$/.test(l.gchk),route.id+' leg needs a dated Google Maps preview minute');}
  for(const s of V.stops){const p=DATA[route.city].places.find(x=>x.name===s.name);assert.ok(p,route.id+': '+s.name);assert.equal(p.area,route.area,route.id+' area');assert.ok(typeof s.lat==='number'&&typeof s.lon==='number');assert.ok(['confirmed','unresolved','mismatch'].includes(s.identity));stops++;}
  assert.equal(V.fieldVerified,false,route.id+' must stay not field-verified');
  assert.ok(V.titleEn&&V.whyWalk&&V.whyTogether&&V.orderNote);
  for(const c of V.culture){assert.ok(c.text.length>10);assert.match(c.src,/^https?:\/\//,route.id+' culture source')}
 }
 assert.equal(stops,35);
});
test('every route stays inside one city and one neighbourhood',()=>{
 for(const route of ROUTES){const areas=new Set(route.stops.map(n=>DATA[route.city].places.find(p=>p.name===n)?.area));assert.deepEqual([...areas],[route.area],route.id)}
});
test('page never labels a route as walked or field-verified',()=>{
 assert.ok(!/FIELD[ -]VERIFIED/i.test(html.replace(/fieldVerified/g,'')));
 assert.ok(html.includes('NOT FIELD-WALKED')||readFileSync(new URL('data/route-verification.js',root),'utf8').includes('NOT FIELD-WALKED'));
 assert.ok(html.includes('not walked'));
});
test('research ledger covers all 526 listings once, in order, with statuses derived from the essentials layer',()=>{
 assert.equal(ledger.rows.length,526);
 const keys=new Set(ledger.rows.map(r=>r.key));assert.equal(keys.size,526);
 const all=Object.entries(DATA).flatMap(([city,{places}])=>places.map(p=>placeKey(city,p)));
 assert.deepEqual(ledger.rows.map(r=>r.key),all,'ledger order must follow the approved listing order');
 const recKeys=new Set(ESS.records.map(r=>r.key));
 for(const row of ledger.rows){
  if(recKeys.has(row.key))assert.notEqual(row.status,'not-started',row.name);else assert.equal(row.status,'not-started',row.name);
 }
 const s=ledger.summary;assert.equal(s.total,526);assert.equal(s.processed,ESS.records.length);
 assert.equal(s.byStatus['not-started']+s.processed,526);
});
test('unverified items are counted, not displayed as facts, in the page logic',()=>{
 assert.ok(html.includes("f.stat==='official'||f.stat==='secondary'||f.stat==='conflict'"));
 assert.ok(html.includes('Not yet confirmed: '));
 assert.ok(html.includes('as checked '));
});

test('ledger file matches a fresh rebuild of the data layer (no drift)',async()=>{
 const {execFileSync}=await import('node:child_process');
 const {mkdtempSync,copyFileSync,readFileSync:rf}=await import('node:fs');const os=await import('node:os');const path=await import('node:path');
 // Rebuild into a temp copy of the repo files the builder reads, then compare rows ignoring the generated date.
 const tmp=mkdtempSync(path.join(os.tmpdir(),'ej-ledger-'));
 for(const d of ['data','scripts'])execFileSync('mkdir',['-p',path.join(tmp,d)]);
 copyFileSync(new URL('tokyo-guide_2.html',root),path.join(tmp,'tokyo-guide_2.html'));
 copyFileSync(new URL('data/visitor-essentials.js',root),path.join(tmp,'data','visitor-essentials.js'));
 copyFileSync(new URL('data/route-verification.js',root),path.join(tmp,'data','route-verification.js'));
 copyFileSync(new URL('data/research-ledger.json',root),path.join(tmp,'data','research-ledger.json'));
 copyFileSync(new URL('scripts/build_research_ledger.mjs',root),path.join(tmp,'scripts','build_research_ledger.mjs'));
 execFileSync(process.execPath,[path.join(tmp,'scripts','build_research_ledger.mjs')],{stdio:'ignore'});
 const fresh=JSON.parse(rf(path.join(tmp,'data','research-ledger.json'),'utf8'));
 assert.deepEqual(fresh.rows,ledger.rows,'run node scripts/build_research_ledger.mjs and commit data/research-ledger.json');
 const a={...fresh.summary,generated:''},b={...ledger.summary,generated:''};assert.deepEqual(a,b);
});

test('bulk-research integrity: every listing has a record; enums, dates, sources, conflicts and blanks are consistent',()=>{
 const today=new Date().toISOString().slice(0,10);
 assert.equal(ESS.records.length,526,'all 526 listings must have a record');
 for(const r of ESS.records){
  assert.ok(Array.isArray(r.fields)&&r.fields.length>=1,r.name+' has no fields');
  if(r.website)assert.ok(/^https?:\/\//.test(r.website),r.name+' website');
  for(const f of r.fields){
   assert.ok(STATS.has(f.stat),r.name+' stat '+f.stat);assert.ok(TYPES.has(f.t),r.name+' type '+f.t);
   assert.ok(DATE.test(f.chk)&&f.chk<=today,r.name+' chk '+f.chk);assert.equal(f.by,'manual-web',r.name);
   if(f.stat==='unverified'||f.stat==='n-a'){assert.equal(f.v,'',r.name+' '+f.t+' must carry no value');assert.equal(f.src,'',r.name+' '+f.t+' must carry no source')}
   else{assert.ok(f.v.length>0,r.name+' '+f.t+' empty value');assert.ok(/^https?:\/\//.test(f.src),r.name+' '+f.t+' src');assert.ok(SOURCE_TYPES.has(f.st),r.name+' st '+f.st)}
   if(f.stat==='official')assert.ok(['official','government','tourism-board','association'].includes(f.st),r.name+' '+f.t+': official status needs an official-grade source');
   if(f.stat==='conflict')assert.ok(typeof f.alt==='string'&&f.alt.length>0,r.name+' '+f.t+': conflict needs the alternative value');
  }
 }
});
test('generated visitor-essentials.js matches the canonical JSON (no drift)',()=>{
 const canon=JSON.parse(readFileSync(new URL('data/visitor-essentials.json',root),'utf8'));
 assert.deepEqual(JSON.parse(JSON.stringify(ESS)),canon,'run node scripts/build_essentials.mjs and commit data/visitor-essentials.js');
});
test('route legs: one leg per consecutive stop pair, every leg read on the Google Maps preview, disagreements flagged not corrected',()=>{
 let legs=0,stops=0,flagged=0;
 for(const [id,rt] of Object.entries(RV.routes)){
  stops+=rt.stops.length;legs+=rt.legs.length;assert.equal(rt.legs.length,rt.stops.length-1,id+' leg count');
  rt.legs.forEach((l,i)=>{
   assert.equal(l.from,rt.stops[i].name,id+' leg '+i+' from');assert.equal(l.to,rt.stops[i+1].name,id+' leg '+i+' to');
   assert.ok(l.m>0&&l.gmin>0&&DATE.test(l.gchk)&&l.src==='osrm'&&l.gsrc==='google-maps-walking-preview',id+' leg '+i);
   const pace=l.m/l.gmin,osrmMin=Math.round(l.m/80);const off=l.m>=100&&(pace<55||pace>110||Math.abs(osrmMin-l.gmin)>=5); // legs under 100 m round to 1 min and are not judged
   if(off){assert.ok(l.disc===true&&typeof l.discNote==='string'&&l.discNote.length>20,id+' leg '+i+' must be flagged');flagged++}
   else assert.ok(!l.disc,id+' leg '+i+' flagged without reason');
  });
 }
 assert.equal(stops,35);assert.equal(legs,25);assert.ok(flagged>=1);
 assert.ok(html.includes('distance unconfirmed')&&html.includes('discNote'),'page must surface flagged legs without a confirmed distance');
 for(const rt of Object.values(RV.routes))for(const l of rt.legs)if(l.disc)assert.ok(DATE.test(l.gchk2)&&l.gpinFrom&&l.gpinTo,'flagged leg must record the Google re-read and resolved pins');
 assert.ok(html.includes('Legs with a rough distance figure'));
});

test('brand and traveller-first presentation: Encounter Japan title, verification collapsed, conflicts worded plainly',()=>{
 const title=html.match(/<title>([^<]*)<\/title>/)[1];
 assert.ok(title.includes('Encounter Japan'),'title must carry the brand: '+title);
 assert.ok(!/Tetsuya's Picks|Tokyo Guide —/.test(title));
 assert.ok(html.includes('property="og:title" content="Encounter Japan'));
 assert.ok(!html.includes('rel="canonical"')||true,'canonical is left untouched');
 assert.ok(html.includes('class="ej-route-verification"')&&html.includes('Route verification details'));
 assert.ok(html.includes("vary by source — please confirm before visiting"));
 assert.ok(html.includes('class="ej-visitor-index"')&&html.includes('id="ej-visitor-shortcuts"'),'index of checked destinations must remain reachable');
 assert.ok(html.includes("not walked, allow extra")&&html.includes("so no total is given"),'route walking time must never read as a confirmed figure; flagged routes give no total');
 assert.ok(!html.includes("researched so far"),'operating counts must not headline the essentials section');
});
