import { chromium } from 'playwright';
import { writeFileSync, mkdirSync } from 'node:fs';
import assert from 'node:assert/strict';

const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
const out='artifacts/screenshots';
mkdirSync(out,{recursive:true});
const report={};
try{
 for(const width of [320,390,768,1280]){
   const page=await browser.newPage({viewport:{width,height:860},deviceScaleFactor:1});
   const errors=[];
   page.on('pageerror',err=>errors.push(err.message));
   await page.goto('http://127.0.0.1:8765/tokyo-guide_2.html',{waitUntil:'domcontentloaded'});
   await page.waitForFunction(() => document.querySelectorAll('#ej-region-select option').length >= 15);
   const dims=await page.evaluate(()=>({windowWidth:innerWidth,docWidth:document.documentElement.scrollWidth}));
   assert.ok(dims.docWidth<=dims.windowWidth+1,'Horizontal overflow at '+width+': '+JSON.stringify(dims));
   assert.deepEqual(errors,[],'Script exceptions at '+width);
   await page.screenshot({path:`${out}/${width}-top.png`,fullPage:false});
   await page.locator('#browse').scrollIntoViewIfNeeded();
   await page.screenshot({path:`${out}/${width}-search.png`,fullPage:false});
   report[width]={overflow:false,errors:[],regionOptions:await page.locator('#ej-region-select option').count()};
   assert.ok(report[width].regionOptions>=15);
   if(width===390){
      await page.locator('#ej-search').fill('多賀野');
      const shown=await page.locator('.city-section.active .place-card').count();
      assert.match(await page.locator('#ej-discovery-count').textContent(),/1 matching place/);
      await page.locator('#ej-jump-results').click();
      assert.equal(await page.locator('.city-section.active .place-card').count(),1);
      assert.equal(shown,1,'Japanese search should find 多賀野');
      await page.locator('#ej-reset-all').click();
      await page.locator('#ej-mood-list button[data-mood="night"]').click();
      assert.equal(await page.locator('#ej-mood-list button[data-mood="night"]').getAttribute('aria-pressed'),'true');
      const night=await page.locator('.city-section.active .place-card').count();
      assert.ok(night>1&&night<376,'Night mood should narrow Tokyo results');
      await page.locator('#ej-reset-all').click();
      await page.locator('#ej-region-select').selectOption('Kyoto');
      await page.locator('#ej-area-select').selectOption('Higashiyama');
      assert.equal(await page.locator('.city-section.active .place-card').count(),11);
      assert.equal(new URL(page.url()).searchParams.get('area'),'Higashiyama');
      await page.locator('.city-section.active .ej-essentials summary').first().click();
      assert.ok(await page.locator('.city-section.active .ej-essentials[open]').count()>0);
      await page.locator('#ej-route-options button[data-route-choice="Kyoto"]').click();
      assert.equal(await page.locator('#ej-field-list .ej-route:not([hidden])').count(),1);
      // Sharing a route must not clear the active search via its parent article.
      await page.locator('#ej-search').fill('南座');
      await page.locator('#ej-field-list .ej-route:not([hidden]) .ej-route-share').click();
      assert.equal(await page.locator('#ej-search').inputValue(),'南座','Route controls must not hijack search');
      await page.locator('[data-find-venue="清水寺"]').click();
      await page.locator('.city-section.active .ej-essentials summary').first().click();
      assert.ok(await page.locator('.city-section.active .ej-field-provenance').count()>0,'Practical field must show individual source metadata');
      await page.locator('#visitor-info').scrollIntoViewIfNeeded();
      await page.screenshot({path:`${out}/390-visitor.png`,fullPage:false});
      report[width].interactions={japaneseSearch:shown,nightResult:night,kyotoHigashiyama:11,visitorEssentials:true,fieldProvenance:true,routeFilter:true,routeCardDoesNotHijackSearch:true};
      await page.locator('#fieldnotes').scrollIntoViewIfNeeded();
      await page.screenshot({path:`${out}/390-routes.png`,fullPage:false});
   }
   if(width===1280){
     await page.locator('#fieldnotes').scrollIntoViewIfNeeded();
     await page.locator('.ej-field-art img').evaluate(async img=>{await img.decode();});
     const overlap=await page.evaluate(()=>{const left=document.querySelector('.ej-field-intro')?.getBoundingClientRect(),right=document.querySelector('.ej-field-content')?.getBoundingClientRect();return {leftRight:left?.right,rightLeft:right?.left}});
     assert.ok(overlap.leftRight<=overlap.rightLeft+1,'Route column overlaps the editorial intro: '+JSON.stringify(overlap));
     await page.screenshot({path:`${out}/1280-routes.png`,fullPage:false});
     await page.locator('.ej-mixtape').scrollIntoViewIfNeeded();
     await page.locator('.ej-mixtape img').evaluate(async img=>{await img.decode();});
     await page.screenshot({path:`${out}/1280-editorial.png`,fullPage:false});
   }
   await page.close();
 }
 writeFileSync('artifacts/browser-report.json',JSON.stringify(report,null,2));
 console.log(JSON.stringify(report,null,2));
}finally{await browser.close()}
