// Generates data/visitor-essentials.js from the canonical data/visitor-essentials.json, validates every record,
// then rebuilds data/research-ledger.json. Usage: node scripts/build_essentials.mjs
import {readFileSync,writeFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {ROOT,placeIndex,validateRecord} from './essentials_lib.mjs';
const canon=JSON.parse(readFileSync(new URL('data/visitor-essentials.json',ROOT),'utf8'));
const idx=placeIndex();
const seen=new Set();
for(const r of canon.records){if(seen.has(r.key))throw new Error('duplicate '+r.key);seen.add(r.key);validateRecord(r,idx)}
// keep listing order for stable diffs
const order=Object.keys(idx.byKey);canon.records.sort((a,b)=>order.indexOf(a.key)-order.indexOf(b.key));
const header=`/* Encounter Japan — independent visitor-essentials data layer (generated from data/visitor-essentials.json by scripts/build_essentials.mjs; do not edit by hand).
   Loaded by tokyo-guide_2.html as a plain script so the page still works from file://.
   Nothing here alters the 526 approved listings; records attach by stable key = city + "|" + Google Maps place id taken from each listing's existing URL.
   Field shape: {t:type, v:value, src:source URL, st:source type, stat:verification status, chk:YYYY-MM-DD, by:method, alt?:conflicting value, note?:remark}
   stat: official | secondary | conflict | unverified | n-a      st: official | government | tourism-board | association | reservation-platform | media | aggregator | review-site | osm
   Values are what the cited source said on the checked date. They are not live data. Unverified fields carry no value and are never rendered as facts. */
`;
writeFileSync(new URL('data/visitor-essentials.json',ROOT),JSON.stringify(canon,null,1)+'\n');
writeFileSync(new URL('data/visitor-essentials.js',ROOT),header+'window.EJ_ESSENTIALS_V1 = '+JSON.stringify(canon,null,1)+';\n');
execFileSync(process.execPath,[fileURLToPath(new URL('build_research_ledger.mjs',import.meta.url))],{stdio:'inherit'});
console.log('records',canon.records.length,'fields',canon.records.reduce((a,r)=>a+r.fields.length,0));
