// Merges a batch of research results into data/visitor-essentials.json, then rebuilds the JS layer and ledger.
// Usage: node scripts/add_essentials_records.mjs batch.json
// Batch format: [{city, name, nameEn?, website?, flags?, fields:[{t,v,src,st,stat,chk,by,alt?,note?}]}]
// The key is derived from the listing's own Google Maps URL (city + place id); a record for an existing key replaces it.
import {readFileSync,writeFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {ROOT,placeIndex,validateRecord} from './essentials_lib.mjs';
const batch=JSON.parse(readFileSync(process.argv[2],'utf8'));
const idx=placeIndex();
const canonPath=new URL('data/visitor-essentials.json',ROOT);
const canon=JSON.parse(readFileSync(canonPath,'utf8'));
let added=0,replaced=0;
for(const b of batch){
 const hit=idx.byCityName[b.city+'|'+b.name];if(!hit)throw new Error('listing not found: '+b.city+' / '+b.name);
 const rec={key:hit.key,name:b.name,city:b.city,nameEn:b.nameEn||'',website:b.website||'',fields:b.fields};
 if(b.flags&&b.flags.length)rec.flags=b.flags;
 validateRecord(rec,idx);
 const i=canon.records.findIndex(r=>r.key===rec.key);
 if(i>=0){canon.records[i]=rec;replaced++}else{canon.records.push(rec);added++}
}
canon.version=new Date().toLocaleDateString('sv-SE',{timeZone:'Asia/Tokyo'});
writeFileSync(canonPath,JSON.stringify(canon,null,1)+'\n');
execFileSync(process.execPath,[fileURLToPath(new URL('build_essentials.mjs',import.meta.url))],{stdio:'inherit'});
console.log('added',added,'replaced',replaced);
