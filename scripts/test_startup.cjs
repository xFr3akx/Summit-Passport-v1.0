const {chromium}=require('playwright');
const assert=require('node:assert/strict'),fs=require('node:fs');
const path=require('node:path'),http=require('node:http');
const assets=path.resolve(__dirname,'../app/src/main/assets/ui'),out=path.resolve(__dirname,'../build/ui-qa');fs.mkdirSync(out,{recursive:true});
const server=http.createServer((req,res)=>{const file=path.resolve(assets,'.'+(new URL(req.url,'http://localhost').pathname==='/'?'/index.html':new URL(req.url,'http://localhost').pathname));if(!file.startsWith(assets+path.sep)){res.writeHead(403).end();return;}try{const mime={'.html':'text/html','.js':'text/javascript','.css':'text/css','.png':'image/png','.json':'application/json'};res.setHeader('Content-Type',mime[path.extname(file)]||'text/plain');res.end(fs.readFileSync(file));}catch{res.writeHead(404).end();}});
(async()=>{
 await new Promise(resolve=>server.listen(8765,'127.0.0.1',resolve));const browser=await chromium.launch({headless:true,channel:process.env.BROWSER_CHANNEL||'msedge'});
 const snapshot=JSON.parse(fs.readFileSync(path.join(assets,'catalog.json'),'utf8'));snapshot.visited=[snapshot.places[0].id];snapshot.visits=[{id:'existing',placeId:snapshot.places[0].id,date:'2026-09-01',notes:'Zachowane',photos:[]}];
 for(const country of ['','PL','DE']){
  const page=await browser.newPage({viewport:{width:390,height:844}});const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error'&&!m.text().includes('net::'))errors.push(m.text());});
  await page.addInitScript(({snapshot,country})=>{window.Passport={getSnapshot:()=>JSON.stringify(snapshot),getCountry:()=>country,getPlans:()=>JSON.stringify([{id:'user-existing',country:'PL',title:'Zachowana lista',placeIds:snapshot.places.slice(0,2).map(p=>p.id),editable:true}]),setTheme:()=>{},setCountry:()=>{}};},{snapshot,country});
  // Native assets can return before the parser has executed later feature scripts.
  await page.route('**/collections.js',async route=>{await new Promise(r=>setTimeout(r,1200));await route.continue();});
  await page.goto('http://127.0.0.1:8765');
  const failure=await page.locator('#app').innerText();console.log(JSON.stringify({country,errors,failed:failure.includes('Nie udało się wczytać')}));
  assert(!failure.includes('Nie udało się wczytać'),'startup failed with slow feature script');
  await page.locator('[data-country=PL]').waitFor();if(await page.locator('#search').count())throw Error('Cold start restored country');
  assert.equal(await page.evaluate(()=>visits[0].notes),'Zachowane');assert.equal(await page.evaluate(()=>plans[0].title),'Zachowana lista');assert.equal(await page.evaluate(()=>visited.size),1);assert.equal(await page.evaluate(()=>collectionData.collections.length),JSON.parse(fs.readFileSync(path.join(assets,'collections.json'),'utf8')).collections.length);assert.deepEqual(errors,[]);await page.close();
 }
 console.log('PASS: native-bridge startup with delayed feature script, home/PL/DE, preserved visits and lists');await browser.close();server.close();
})().catch(e=>{console.error(e);process.exit(1)});
