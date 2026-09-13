const {chromium}=require('playwright');
const assert=require('node:assert/strict'),fs=require('node:fs');
const path=require('node:path'),http=require('node:http');
const assets=path.resolve(__dirname,'../app/src/main/assets/ui'),out=path.resolve(__dirname,'../build/ui-qa');fs.mkdirSync(out,{recursive:true});
const server=http.createServer((req,res)=>{const file=path.resolve(assets,'.'+(new URL(req.url,'http://localhost').pathname==='/'?'/index.html':new URL(req.url,'http://localhost').pathname));if(!file.startsWith(assets+path.sep)){res.writeHead(403).end();return;}try{const mime={'.html':'text/html','.js':'text/javascript','.css':'text/css','.png':'image/png','.json':'application/json'};res.setHeader('Content-Type',mime[path.extname(file)]||'text/plain');res.end(fs.readFileSync(file));}catch{res.writeHead(404).end();}});
(async()=>{
 await new Promise(resolve=>server.listen(8765,'127.0.0.1',resolve));
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try {
 const page=await browser.newPage({viewport:{width:390,height:844}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));await page.goto('http://127.0.0.1:8765');
 await page.locator('[data-country=DE]').click();
 const groups=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../data/germany_completion_12.json'),'utf8')).groups;
 const visible=await page.evaluate(()=>selectedPlaces().map(p=>p.id));
 for(const group of groups){assert(!visible.includes(group.id));for(const id of group.resolvedInto)assert(visible.includes(id));}
 for(const name of ['Oberburg Manderscheid','Niederburg Manderscheid','Unterer Gaisalpsee','Oberer Gaisalpsee','Wanderparkplatz Teiche','Parkplatz Kermeter','Greifensteine — Turnerfelsen','Heidezentrum Turmhof','Hochvogel']){
 await page.locator('#search').fill(name);assert(await page.locator('[data-place]').count()>0,name);
 }
 await page.locator('#search').fill('Oberburg Manderscheid');await page.locator('#listToggle').click();await page.locator('[data-place]').first().click();await page.locator('[data-visit-place]').click();
 assert.equal(await page.locator('[name=distance]').count(),0);await page.locator('[name=date]').fill('2026-09-13');await page.locator('[name=notes]').fill('Nowy zamek z rozdzielonej grupy');await page.getByRole('button',{name:'Zapisz wizytę',exact:true}).click();
 await page.locator('[data-tab=journal]').click();assert((await page.locator('.journal').innerText()).includes('Oberburg Manderscheid'));
 await page.reload();await page.locator('[data-tab=collections]').click();await page.locator('[data-collection=DE-castle]').click();assert((await page.locator('#collectionMembers').innerText()).includes('Oberburg Manderscheid'));
 await page.screenshot({path:path.join(out,'germany12-castles.png')});
 await page.locator('#back').click();await page.locator('[data-country=PL]').click();await page.locator('[data-tab=journal]').click();assert.equal(await page.locator('.journal article').count(),0);
 assert.deepEqual(errors,[]);console.log('PASS: split groups hidden, every child mapped, documented starts searchable, new castle visit persists, collections and Poland isolation');
 } finally {await browser.close();server.close();}
})().catch(e=>{console.error(e);process.exit(1)});
