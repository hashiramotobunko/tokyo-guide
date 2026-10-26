// Manual, network-using check: every source URL in the data layer answers (HEAD/GET) without a 4xx. Not part of CI.
// Usage: node scripts/check_source_links.mjs
import {readFileSync} from 'node:fs';import vm from 'node:vm';
const w={};for(const f of ['visitor-essentials.js','route-verification.js'])vm.runInNewContext(readFileSync(new URL('../data/'+f,import.meta.url),'utf8'),{window:w});
const urls=new Set();
for(const r of w.EJ_ESSENTIALS_V1.records){if(r.website)urls.add(r.website);for(const f of r.fields)if(f.src)urls.add(f.src)}
for(const v of Object.values(w.EJ_ROUTE_FIELD_V1.routes))for(const c of v.culture)urls.add(c.src);
const out=[];
for(const u of urls){
 let status='ERR';
 try{const r=await fetch(u,{method:'GET',redirect:'follow',headers:{'User-Agent':'Mozilla/5.0 (EncounterJapan link check)'},signal:AbortSignal.timeout(20000)});status=r.status}catch(e){status='ERR '+(e.cause?.code||e.name)}
 out.push([status,u]);console.log(status,u);
}
const bad=out.filter(([s])=>!(typeof s==='number'&&s<400));
console.log('\nchecked',out.length,'bad',bad.length);
