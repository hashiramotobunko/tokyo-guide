// Immutable editorial source check: compares approved place identifiers to main in CI.
// This test neither fetches external pages nor modifies the repository.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import vm from 'node:vm';
function extract(source){
 const start=source.indexOf('const DATA = {');
 assert.ok(start>=0,'source DATA block missing');
 const brace=source.indexOf('{',start);let depth=0,quote=null,esc=false;
 for(let i=brace;i<source.length;i++){
  const c=source[i];
  if(quote){if(esc){esc=false;continue}if(c==='\\'){esc=true;continue}if(c===quote)quote=null;continue}
  if(c==='"'||c==="'"){quote=c;continue}
  if(c==='{')depth++;
  else if(c==='}'&&--depth===0)return vm.runInNewContext('('+source.slice(brace,i+1)+')');
 }
 throw Error('Unclosed DATA block');
}
const current=extract(readFileSync(new URL('../tokyo-guide_2.html',import.meta.url),'utf8'));
test('526 original place names and Google Maps URLs remain identical to main and in order',()=>{
 const mainHtml=execFileSync('git',['show','origin/main:tokyo-guide_2.html'],{encoding:'utf8'});
 const original=extract(mainHtml);
 const pairs=obj=>Object.entries(obj).flatMap(([city,{places}])=>places.map(({name,url})=>[city,name,url]));
 const now=pairs(current),base=pairs(original);
 assert.equal(base.length,526,'unexpected main baseline');
 assert.equal(now.length,526,'listing count changed');
 assert.deepEqual(now,base,'approved listing names, Maps links or ordering changed');
});
test('known deleted duplicates stay removed and known exceptions remain',()=>{
 const names=Object.values(current).flatMap(group=>group.places.map(p=>p.name));
 for(const n of ['桃花林（The Okura Tokyo）','中華そば 多賀野','Freehouse THE YEAST'])assert.ok(names.some(name=>name.includes(n)),'missing '+n);
 assert.ok(!names.includes('富ヶ谷スプリングス'));
});