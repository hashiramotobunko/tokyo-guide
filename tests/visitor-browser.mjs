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
   // TAKE THE DETOUR: the headline is meant to run over the photograph; the reading copy is not, and must stay on paper and inside the viewport.
   const hero=await page.evaluate(()=>{const r=s=>document.querySelector(s)?.getBoundingClientRect();
    const photo=r('.td-hero-media'),title=r('.td-hero-title'),intro=r('.td-hero-intro'),jp=r('.td-jp');
    const hit=(a,b)=>!!(a&&b&&a.left<b.right-2&&a.right>b.left+2&&a.top<b.bottom-2&&a.bottom>b.top+2);
    const img=document.querySelector('.td-hero-media img');
    return {titleOverPhoto:hit(title,photo),introInside:!!intro&&intro.right<=innerWidth+1&&intro.left>=-1,jpInside:!!jp&&jp.right<=innerWidth+1&&jp.left>=-1,photoLoaded:!!img&&img.naturalWidth>0,photoIsLocal:!!img&&!/^https?:/.test(img.getAttribute('src'))}});
   assert.deepEqual(hero,{titleOverPhoto:true,introInside:true,jpInside:true,photoLoaded:true,photoIsLocal:true},'Hero composition at '+width+': '+JSON.stringify(hero));
   // Every photograph on the page must really load — a fallback-only page is not a pass.
   const photos=await page.evaluate(async()=>{const out=[];for(const img of document.querySelectorAll('img')){img.loading='eager';try{await img.decode()}catch(e){}out.push({src:img.getAttribute('src'),w:img.naturalWidth})}return out});
   const broken=photos.filter(p=>!p.w);
   assert.deepEqual(broken,[],'Images failed to load at '+width+': '+JSON.stringify(broken));
   assert.ok(photos.filter(p=>/assets\/photos\//.test(p.src)).length>=4,'expected the four street photographs at '+width);
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
      // Deep-link state survives a reload; back/forward returns to the selected neighborhood.
      const kyotoLink=page.url();
      await page.reload({waitUntil:'domcontentloaded'});
      assert.equal(await page.locator('#ej-region-select').inputValue(),'Kyoto');
      assert.equal(await page.locator('#ej-area-select').inputValue(),'Higashiyama');
      assert.equal(page.url(),kyotoLink);
      await page.locator('#ej-area-select').selectOption('');
      assert.equal(new URL(page.url()).searchParams.get('area'),null);
      await page.goBack({waitUntil:'domcontentloaded'});
      assert.equal(await page.locator('#ej-area-select').inputValue(),'Higashiyama');
      await page.goForward({waitUntil:'domcontentloaded'});
      assert.equal(await page.locator('#ej-area-select').inputValue(),'');
      await page.goBack({waitUntil:'domcontentloaded'});
      assert.equal(await page.locator('#ej-area-select').inputValue(),'Higashiyama');
      await page.locator('.city-section.active .ej-essentials summary').first().click();
      assert.ok(await page.locator('.city-section.active .ej-essentials[open]').count()>0);
      await page.locator('#ej-route-options button[data-route-choice="Kyoto"]').click();
      assert.equal(await page.locator('#ej-field-list .ej-route:not([hidden])').count(),1);
      // Sharing a route must not clear the active search via its parent article.
      await page.locator('#ej-search').fill('南座');
      await page.locator('#ej-field-list .ej-route:not([hidden]) .ej-route-share').click();
      assert.equal(await page.locator('#ej-search').inputValue(),'南座','Route controls must not hijack search');
      await page.locator('.ej-visitor-index').evaluate(d=>{d.open=true});
      await page.locator('[data-find-venue="清水寺"]').evaluate(b=>b.scrollIntoView({block:'center',behavior:'instant'}));
      await page.locator('[data-find-venue="清水寺"]').click();
      await page.locator('.city-section.active .ej-essentials summary').first().click();
      assert.ok(await page.locator('.city-section.active .ej-field-provenance').count()>0,'Practical field must show individual source metadata');
      await page.locator('#visitor-info').scrollIntoViewIfNeeded();
      await page.screenshot({path:`${out}/390-visitor.png`,fullPage:false});
      report[width].interactions={japaneseSearch:shown,nightResult:night,kyotoHigashiyama:11,visitorEssentials:true,fieldProvenance:true,routeFilter:true,routeCardDoesNotHijackSearch:true};
      await page.locator('#fieldnotes').scrollIntoViewIfNeeded();
      await page.screenshot({path:`${out}/390-routes.png`,fullPage:false});
      // Route cards must show map-estimated legs, per-stop status chips and sourced details from the data layer.
      await page.locator('#ej-route-options button[data-route-choice="all"]').click().catch(()=>{});
      const ueno=page.locator('#route-ueno');
      await ueno.evaluate(el=>el.scrollIntoView({block:'start',behavior:'instant'}));
      assert.equal(await ueno.locator('.ej-route-leg').count(),3,'Ueno route needs three walking legs');
      assert.ok((await ueno.locator('.ej-route-check').textContent()).includes('not yet'),'Route summary must say it was not walked');
      assert.ok(await ueno.locator('.ej-chip-official').count()>=3,'Ueno stops should show official hour chips');
      assert.ok(await ueno.locator('.ej-route-notes a[href^="https://"]').count()>=3,'Background facts must link sources');
      await ueno.locator('.ej-stop-details summary').first().click();
      assert.ok(await ueno.locator('.ej-stop-details[open] .ej-field-provenance a[href^="https://"]').count()>0,'Stop details must cite a source');
      assert.ok((await page.locator('#fieldnotes').textContent()).includes('NOT FIELD-WALKED'));
      const order=await ueno.evaluate(el=>{const s=el.querySelector('.ej-route-stop'),v=el.querySelector('.ej-route-verification');return {stopsFirst:!!(s&&v)&&!!(s.compareDocumentPosition(v)&Node.DOCUMENT_POSITION_FOLLOWING),verificationClosed:v&&!v.open,legHasDirections:!!el.querySelector('.ej-route-leg a[href*="maps/dir"]')}});
      assert.deepEqual(order,{stopsFirst:true,verificationClosed:true,legHasDirections:true},'Route card must lead with stops and keep verification collapsed');
      await page.screenshot({path:`${out}/390-route-detail.png`,fullPage:false});
      // Visitor essentials shortcuts are generated from the data layer and reach a researched listing.
      await page.locator('.ej-visitor-index').evaluate(d=>{d.open=true});
      const shortcuts=await page.locator('#ej-visitor-shortcuts button').count();
      assert.ok(shortcuts>=30,'Expected generated shortcuts for researched places, got '+shortcuts);
      await page.locator('#ej-visitor-shortcuts button[data-find-venue="自由軒 難波本店"]').evaluate(b=>b.scrollIntoView({block:'center',behavior:'instant'}));
      await page.locator('#ej-visitor-shortcuts button[data-find-venue="自由軒 難波本店"]').click();
      await page.locator('.city-section.active .ej-essentials summary').first().click();
      const ess=page.locator('.city-section.active .ej-essentials[open]').first();
      assert.ok(await ess.locator('.ej-ess-row[data-stat="official"]').count()>=2,'Jiyuken should show official rows');
      assert.ok((await ess.textContent()).includes('as checked'),'Time-sensitive rows must say when they were checked');
      assert.equal(await ess.locator('.ej-ess-row[data-stat="unverified"]').count(),0,'Unverified fields must not render as rows');
      await ess.evaluate(el=>el.scrollIntoView({block:'start',behavior:'instant'}));
      await page.screenshot({path:`${out}/390-essentials.png`,fullPage:false});
      report[width].dataLayer={legs:3,shortcuts,officialRows:true};
   }
   if(width===1280){
     await page.locator('#fieldnotes').scrollIntoViewIfNeeded();
     // The approved city-pop artwork now lives in its own spread; make sure both plates decode.
     await page.locator('#imagined').scrollIntoViewIfNeeded();
     const plates=await page.locator('#imagined img').evaluateAll(async imgs=>{for(const img of imgs){img.loading='eager';await img.decode();}return imgs.filter(i=>i.naturalWidth>0).length;});
     assert.equal(plates,2,'both plates of the illustrated spread must load');
     await page.locator('#fieldnotes').scrollIntoViewIfNeeded();
     const overlap=await page.evaluate(()=>{const left=document.querySelector('.ej-field-intro')?.getBoundingClientRect(),right=document.querySelector('.ej-field-content')?.getBoundingClientRect();return {leftRight:left?.right,rightLeft:right?.left}});
     assert.ok(overlap.leftRight<=overlap.rightLeft+1,'Route column overlaps the editorial intro: '+JSON.stringify(overlap));
     // Capture the start of the section, not whichever middle route Playwright scrolled to.
     await page.locator('#fieldnotes').evaluate(el=>el.scrollIntoView({block:'start',behavior:'instant'}));
     await page.screenshot({path:`${out}/1280-routes.png`,fullPage:false});
     const namba=page.locator('#route-namba');
     await namba.evaluate(el=>el.scrollIntoView({block:'start',behavior:'instant'}));
     assert.equal(await namba.locator('.ej-route-stop').count(),3);
     assert.equal(await namba.locator('.ej-route-leg').count(),2);
     await page.screenshot({path:`${out}/1280-route-detail.png`,fullPage:false});
     await page.locator('#visitor-info').evaluate(el=>el.scrollIntoView({block:'start',behavior:'instant'}));
     await page.screenshot({path:`${out}/1280-visitor.png`,fullPage:false});
     // Keyboard: the first generated shortcut is reachable and operable by keyboard.
     await page.locator('.ej-visitor-index').evaluate(d=>{d.open=true});
     await page.locator('#ej-visitor-shortcuts button').first().focus();
     await page.keyboard.press('Enter');
     assert.ok(await page.locator('.city-section.active .place-card').count()>=1);
     await page.locator('.td-spread').scrollIntoViewIfNeeded();
     await page.locator('.td-spread img').first().evaluate(async img=>{img.loading='eager';await img.decode();});
     await page.screenshot({path:`${out}/1280-editorial.png`,fullPage:false});
   }
   await page.close();
 }
 writeFileSync('artifacts/browser-report.json',JSON.stringify(report,null,2));
 console.log(JSON.stringify(report,null,2));
}finally{await browser.close()}
