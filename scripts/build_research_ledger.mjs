// Builds/merges data/research-ledger.json: one row per approved listing (526), keyed by city + Google Maps place id.
// Usage: node scripts/build_research_ledger.mjs   (read-only on tokyo-guide_2.html; never edits the listings)
// Statuses: not-started | official | secondary | conflict | unverified   (derived from data/visitor-essentials.js when a record exists)
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import vm from 'node:vm';
const html=readFileSync(new URL('../tokyo-guide_2.html',import.meta.url),'utf8');
function extract(src,marker){const st=src.indexOf(marker);const b=src.indexOf('{',st);let d=0,q=null,e=false;for(let i=b;i<src.length;i++){const c=src[i];if(q){if(e){e=false;continue}if(c==='\\'){e=true;continue}if(c===q)q=null;continue}if(c==='"'||c==="'"){q=c;continue}if(c==='{')d++;else if(c==='}'&&--d===0)return vm.runInNewContext('('+src.slice(b,i+1)+')')}}
const DATA=extract(html,'const DATA = {');
const w={};vm.runInNewContext(readFileSync(new URL('../data/visitor-essentials.js',import.meta.url),'utf8'),{window:w});
vm.runInNewContext(readFileSync(new URL('../data/route-verification.js',import.meta.url),'utf8'),{window:w});
const byKey=Object.fromEntries(w.EJ_ESSENTIALS_V1.records.map(r=>[r.key,r]));
const routeStops=new Set(Object.values(w.EJ_ROUTE_FIELD_V1.routes).flatMap(r=>r.stops.map(s=>s.name)));
export const placeKey=(city,p)=>{const m=p.url.match(/!1s(0x[0-9a-f]+:0x[0-9a-f]+)/);return city+'|'+(m?m[1]:'name:'+p.name)};
const PRIORITY_CATS=new Set(['Museum','Temple','Shrine','Landmark','Monument','Park & Garden','Sightseeing','Shopping Street','Event Venue','Live House','Sento','Onsen','Activity']);
const ledgerPath=new URL('../data/research-ledger.json',import.meta.url);
const previous=existsSync(ledgerPath)?JSON.parse(readFileSync(ledgerPath,'utf8')).rows:[];
const prevByKey=Object.fromEntries(previous.map(r=>[r.key,r]));
const rows=[];let order=0;
for(const [city,{places}] of Object.entries(DATA))for(const p of places){
 const key=placeKey(city,p);const rec=byKey[key];order++;
 let status='not-started',checked='',fieldsOfficial=0,fieldsSecondary=0,fieldsConflict=0,fieldsUnverified=0,flags=[];
 if(rec){for(const f of rec.fields){if(f.stat==='official')fieldsOfficial++;else if(f.stat==='secondary')fieldsSecondary++;else if(f.stat==='conflict')fieldsConflict++;else if(f.stat==='unverified')fieldsUnverified++;}
  status=fieldsOfficial?'official':fieldsSecondary?'secondary':fieldsConflict?'conflict':'unverified';
  checked=rec.fields.map(f=>f.chk).sort().pop()||'';flags=rec.flags||[];}
 const batch=routeStops.has(p.name)||rec?1:PRIORITY_CATS.has(p.cat)?2:3;
 rows.push({key,order,city,area:p.area,name:p.name,cat:p.cat,url:p.url,batch,status,checked,fieldsOfficial,fieldsSecondary,fieldsConflict,fieldsUnverified,officialSiteFound:!!(rec&&rec.website),flags,notes:prevByKey[key]?.notes||''});
}
const summary={total:rows.length,byStatus:Object.fromEntries(['official','secondary','conflict','unverified','not-started'].map(s=>[s,rows.filter(r=>r.status===s).length])),byBatch:Object.fromEntries([1,2,3].map(b=>[b,rows.filter(r=>r.batch===b).length])),processed:rows.filter(r=>r.status!=='not-started').length,withOfficialField:rows.filter(r=>r.fieldsOfficial>0).length,officialSiteFound:rows.filter(r=>r.officialSiteFound).length,generated:new Date().toLocaleDateString('sv-SE',{timeZone:'Asia/Tokyo'})};
writeFileSync(ledgerPath,JSON.stringify({about:'Encounter Japan practical-information research ledger. One row per approved listing; status derives from data/visitor-essentials.js. Resume by taking the lowest batch with not-started rows.',summary,rows},null,1));
console.log(JSON.stringify(summary));
