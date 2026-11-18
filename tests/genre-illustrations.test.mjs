import test from 'node:test';
import assert from 'node:assert/strict';
import {readdirSync,readFileSync,statSync} from 'node:fs';
import {resolve} from 'node:path';
import vm from 'node:vm';

const root=resolve(new URL('..',import.meta.url).pathname);
const html=readFileSync(resolve(root,'tokyo-guide_2.html'),'utf8');
const files=readdirSync(resolve(root,'assets','genres')).filter(name=>name.endsWith('.webp')).sort();

function balancedAfter(startToken,open,close){
 const start=html.indexOf(startToken);assert.ok(start>=0,'missing '+startToken);
 const pos=html.indexOf(open,start+startToken.length-1);let quote=null,escape=false,depth=0;
 for(let i=pos;i<html.length;i++){
  const c=html[i];
  if(quote){if(escape){escape=false;continue}if(c==='\\'){escape=true;continue}if(c===quote)quote=null;continue}
  if(c==='"'||c==="'"){quote=c;continue}
  if(c===open)depth++;else if(c===close&&--depth===0)return html.slice(pos,i+1);
 }
 throw new Error('Unclosed '+startToken);
}

const data=vm.runInNewContext('('+balancedAfter('const DATA = {','{','}')+')');
const genreArt=vm.runInNewContext(balancedAfter('const EJ_GENRE_ART=[','[',']'));
const categories=new Set(Object.values(data).flatMap(region=>region.places.map(place=>place.cat)));

test('all 32 Box illustrations are present and non-empty WebP files',()=>{
 assert.equal(files.length,32);
 for(const file of files){
  assert.ok(statSync(resolve(root,'assets','genres',file)).size>200_000,file);
  assert.equal(readFileSync(resolve(root,'assets','genres',file)).subarray(0,4).toString(),'RIFF',file);
 }
});

test('every illustration maps once to a real genre and a real file',()=>{
 assert.equal(genreArt.length,32);
 assert.equal(new Set(genreArt.map(([category])=>category)).size,32);
 assert.equal(new Set(genreArt.map(([,slug])=>slug)).size,32);
 for(const [category,slug] of genreArt){
  assert.ok(categories.has(category),category+' is not present in source data');
  assert.ok(files.includes(slug+'.webp'),slug+'.webp is missing');
 }
});

test('illustrated genre controls are accessible and use the existing filter state',()=>{
 assert.match(html,/id="ej-genre-art-list" role="list" aria-label="Illustrated genre filters"/);
 assert.match(html,/class="ej-genre-art-card" type="button" role="listitem"/);
 assert.match(html,/aria-pressed=/);
 assert.match(html,/loading="lazy" decoding="async" alt="" aria-hidden="true"/);
 assert.match(html,/st\.cats=st\.cats\.length===1&&st\.cats\[0\]===category\?\[\]:\[category\]/);
});
