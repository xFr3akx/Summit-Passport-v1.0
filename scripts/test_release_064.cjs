const {chromium}=require('playwright');
const assert=require('node:assert/strict'),fs=require('node:fs');
const path=require('node:path'),http=require('node:http');
const assets=path.resolve(__dirname,'../app/src/main/assets/ui'),out=path.resolve(__dirname,'../build/ui-qa');fs.mkdirSync(out,{recursive:true});
const server=http.createServer((req,res)=>{const file=path.resolve(assets,'.'+(new URL(req.url,'http://localhost').pathname==='/'?'/index.html':new URL(req.url,'http://localhost').pathname));if(!file.startsWith(assets+path.sep)){res.writeHead(403).end();return;}try{const mime={'.html':'text/html','.js':'text/javascript','.css':'text/css','.png':'image/png','.json':'application/json'};res.setHeader('Content-Type',mime[path.extname(file)]||'text/plain');res.end(fs.readFileSync(file));}catch{res.writeHead(404).end();}});
(async()=>{
 await new Promise(resolve=>server.listen(8765,'127.0.0.1',resolve));
 const browser=await chromium.launch({headless:true,channel:'msedge'}),page=await browser.newPage({viewport:{width:390,height:844}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));await page.goto('http://127.0.0.1:8765');
 assert.equal(await page.locator('[data-country=DE] [role=progressbar]').getAttribute('aria-valuemax'),'1333');
 await page.locator('[data-country=DE]').click();assert.equal(await page.evaluate(()=>selectedPlaces().length),1333);
 for(const name of ['Wiehler Tropfsteinhöhle','Schloss Wolfach','Schloss Charlottenburg','Kreuzberg']){
  await page.locator('#search').fill(name);assert(await page.locator('[data-place]').count()>0,name);
  assert(await page.evaluate(()=>selectedPlaces().every(p=>p.country==='DE'&&p.mapReady)));
 }
 await page.locator('[data-tab=collections]').click();await page.locator('[data-collection=DE-cave]').click();
 assert((await page.locator('#collectionMembers').innerText()).includes('Wiehler Tropfsteinhöhle'));
 await page.screenshot({path:path.join(out,'release064-germany-caves.png')});
 await page.locator('[data-tab=achievements]').click();assert.equal(await page.locator('[data-badge]').count(),12);
 await page.locator('#back').click();await page.locator('[data-country=PL]').click();assert.equal(await page.evaluate(()=>selectedPlaces().length),451);
 assert.deepEqual(errors,[]);await browser.close();server.close();console.log('PASS 0.6.4: country counts, newly completed places searchable, cave collection membership, badges and Poland isolation');
})().catch(e=>{console.error(e);process.exit(1)});
