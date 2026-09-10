const {chromium}=require('playwright');
const assert=require('node:assert/strict'),fs=require('node:fs');
const path=require('node:path'),http=require('node:http');
const assets=path.resolve(__dirname,'../app/src/main/assets/ui'),out=path.resolve(__dirname,'../build/ui-qa');fs.mkdirSync(out,{recursive:true});
const server=http.createServer((req,res)=>{const file=path.resolve(assets,'.'+(new URL(req.url,'http://localhost').pathname==='/'?'/index.html':new URL(req.url,'http://localhost').pathname));if(!file.startsWith(assets+path.sep)){res.writeHead(403).end();return;}try{const mime={'.html':'text/html','.js':'text/javascript','.css':'text/css','.png':'image/png','.json':'application/json'};res.setHeader('Content-Type',mime[path.extname(file)]||'text/plain');res.end(fs.readFileSync(file));}catch{res.writeHead(404).end();}});
(async()=>{
 await new Promise(resolve=>server.listen(8765,'127.0.0.1',resolve));
 const browser=await chromium.launch({headless:true,channel:process.env.BROWSER_CHANNEL||'msedge'});const page=await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:1});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8765');await page.locator('[data-country=PL]').waitFor();
 const counts=await page.evaluate(()=>({pl:catalog.places.filter(p=>p.country==='PL'&&p.mapReady).length,de:catalog.places.filter(p=>p.country==='DE'&&p.mapReady).length}));
 await page.screenshot({path:path.join(out,'stage3-home-light.png')});
 await page.getByRole('button',{name:'Ustawienia'}).click();await page.getByRole('button',{name:'Dark',exact:true}).click();await page.getByRole('button',{name:'Gotowe'}).click();await page.waitForTimeout(300);await page.screenshot({path:path.join(out,'stage3-home-dark.png')});
 await page.reload();await page.locator('[data-country=PL]').waitFor();assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');
 await page.locator('[data-country=PL]').click();await page.waitForTimeout(1200);assert.equal(await page.evaluate(()=>layer.getLayers().length),counts.pl);await page.screenshot({path:path.join(out,'stage3-map-dark.png')});
 await page.selectOption('#category','castle');assert(await page.evaluate(()=>selectedPlaces().every(p=>p.category==='castle')));
 await page.fill('#search','wawel');await page.fill('#search','no-such-place-xyz');assert.equal(await page.evaluate(()=>layer.getLayers().length),0);await page.getByRole('button',{name:'Lista',exact:true}).click();assert(await page.locator('#list').innerText().then(t=>t.includes('Brak miejsc')));
 await page.fill('#search','');await page.selectOption('#category','all');
 // Inject only test visit state in this browser session; production DB remains untouched.
 await page.evaluate(()=>{visited=new Set([selectedPlaces()[0].id]);updateResults();});await page.check('#unvisited');assert.equal(await page.evaluate(()=>selectedPlaces().length),counts.pl-1);await page.uncheck('#unvisited');
 await page.locator('[data-place]').first().click();assert(await page.locator('.leaflet-popup-content').isVisible());
 await page.getByRole('button',{name:'Ustawienia',exact:true}).click();await page.getByRole('button',{name:'Light',exact:true}).click();await page.getByRole('button',{name:'Gotowe'}).click();await page.screenshot({path:path.join(out,'stage3-map-light.png')});
 await page.getByRole('button',{name:'Wybór kraju',exact:true}).click();await page.locator('[data-country=DE]').click();await page.waitForTimeout(500);assert.equal(await page.evaluate(()=>layer.getLayers().length),counts.de);
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
 assert(!await page.locator('body').innerText().then(t=>/Near Me/i.test(t)));
 await page.context().setOffline(true);await page.fill('#search','burg');assert(await page.evaluate(()=>selectedPlaces().length)>0);
 assert.deepEqual(errors,[]);console.log(JSON.stringify({passed:true,counts,checks:'themes persistence, countries, category and name filters, empty state, visited filtering, list-to-map, offline filtering, mobile overflow, no Near Me, JS errors'}));
 await browser.close();server.close();
})().catch(e=>{console.error(e);process.exit(1)});
