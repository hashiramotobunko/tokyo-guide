// Shared helpers for the visitor-essentials pipeline (read-only on tokyo-guide_2.html).
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
export const ROOT=new URL('../',import.meta.url);
export function extractData(){
 const src=readFileSync(new URL('tokyo-guide_2.html',ROOT),'utf8');
 const st=src.indexOf('const DATA = {');const b=src.indexOf('{',st);let d=0,q=null,e=false;
 for(let i=b;i<src.length;i++){const c=src[i];if(q){if(e){e=false;continue}if(c==='\\'){e=true;continue}if(c===q)q=null;continue}if(c==='"'||c==="'"){q=c;continue}if(c==='{')d++;else if(c==='}'&&--d===0)return vm.runInNewContext('('+src.slice(b,i+1)+')')}
 throw new Error('DATA block not closed');
}
export const placeKey=(city,p)=>{const m=p.url.match(/!1s(0x[0-9a-f]+:0x[0-9a-f]+)/);return city+'|'+(m?m[1]:'name:'+p.name)};
export function placeIndex(){const DATA=extractData();const byKey={},byCityName={};for(const [city,{places}] of Object.entries(DATA))for(const p of places){byKey[placeKey(city,p)]={city,p};byCityName[city+'|'+p.name]={city,p,key:placeKey(city,p)}}return {DATA,byKey,byCityName}}
export const FIELD_TYPES=['website','name','address','hours','closed','reservation','fee','payment','access','language','accessibility','notice','tip'];
export const STATS=['official','secondary','conflict','unverified','n-a'];
export const SOURCE_TYPES=['official','government','tourism-board','association','reservation-platform','media','aggregator','review-site','osm'];
export function validateRecord(r,idx){
 const hit=idx.byKey[r.key];if(!hit)throw new Error('unknown key '+r.key+' ('+r.name+')');
 if(hit.p.name!==r.name)throw new Error('name mismatch '+r.key+': '+r.name+' vs '+hit.p.name);
 if(!Array.isArray(r.fields)||!r.fields.length)throw new Error('no fields '+r.name);
 for(const f of r.fields){
  if(!FIELD_TYPES.includes(f.t))throw new Error(r.name+' bad type '+f.t);
  if(!STATS.includes(f.stat))throw new Error(r.name+' bad stat '+f.stat);
  if(!/^\d{4}-\d{2}-\d{2}$/.test(f.chk||''))throw new Error(r.name+' bad chk');
  if(!f.by)throw new Error(r.name+' missing by');
  if(['official','secondary','conflict'].includes(f.stat)){
   if(!f.v||f.v.length<3)throw new Error(r.name+' '+f.t+' needs value');
   if(!/^https?:\/\//.test(f.src||''))throw new Error(r.name+' '+f.t+' needs src');
   if(!SOURCE_TYPES.includes(f.st))throw new Error(r.name+' '+f.t+' bad st '+f.st);
   if(f.stat==='official'&&!['official','government','tourism-board','association'].includes(f.st))throw new Error(r.name+' '+f.t+' official stat needs official-grade st');
   if(f.stat==='secondary'&&f.st==='official')throw new Error(r.name+' '+f.t+' secondary value cannot cite an official source type');
   if(f.stat==='conflict'&&!(f.alt&&f.alt.length>2))throw new Error(r.name+' '+f.t+' conflict needs alt');
  }else if(f.v)throw new Error(r.name+' '+f.t+' unverified/n-a must not carry a value');
 }
}
