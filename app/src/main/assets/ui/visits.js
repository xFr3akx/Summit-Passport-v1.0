'use strict';
const visitDialog=document.querySelector('#visitDialog');
document.querySelector('#openLegal').onclick=()=>document.querySelector('#legal').showModal();
document.querySelector('#closeLegal').onclick=()=>document.querySelector('#legal').close();
document.addEventListener('click',e=>{const b=e.target.closest('[data-visit-place]');if(b)openVisit(b.dataset.visitPlace);});
function photoUrl(id){return id.startsWith('data:image/')?id:'photos/'+id;}
function localDate(){const d=new Date();return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;}
function openVisit(placeId,existing){
 const p=catalog.places.find(x=>x.id===placeId);if(!p)return;
 const v=existing||{date:localDate()};photoDraft=[...(v.photos||[])];
 visitDialog.innerHTML=`<h2>${existing?'Edytuj wizytę':'Twoja wizyta'}</h2><p>${escapeHtml(p.name)}</p><form class="visit-form" id="visitForm">
 <label>Data wizyty<input name="date" type="date" required value="${escapeHtml(v.date)}"></label>
 <label>Pogoda<select name="weather">${['','Słonecznie','Częściowe zachmurzenie','Pochmurno','Deszcz','Śnieg','Mgła','Wiatr'].map(w=>`<option ${v.weather===w?'selected':''}>${w||'Nie podano'}</option>`).join('')}</select></label>
 <label>Trasa w AllTrails<input name="trailUrl" type="url" placeholder="https://www.alltrails.com/…" value="${escapeHtml(v.trailUrl||'')}"></label>
 <label>Dystans (km)<input name="distance" type="number" min="0" max="100000" step="0.01" value="${v.distance_m?v.distance_m/1000:''}"></label>
 <label>Czas (minuty)<input name="duration" type="number" min="0" max="10000000" step="1" value="${v.duration_minutes||''}"></label>
 <label>Suma podejść (m)<input name="elevation" type="number" min="0" max="10000000" step="1" value="${v.elevation_gain_m||''}"></label>
 <label>Notatki<textarea name="notes" maxlength="20000" placeholder="Co chcesz zapamiętać?">${escapeHtml(v.notes||'')}</textarea></label>
 <div><p>Zdjęcia <span class="muted">(do 10)</span></p><div id="photoGrid" class="photo-grid"></div><button id="addPhoto" type="button">Dodaj zdjęcie</button><input id="photoInput" type="file" accept="image/*" hidden><p id="photoStatus" role="status"></p></div>
 <p class="muted">Datę i szczegóły możesz później zmienić w Dzienniku.</p><p id="visitError" class="visit-error" role="alert"></p>
 <div class="visit-actions"><button type="button" id="cancelVisit">Anuluj</button><button type="submit" class="primary">Zapisz wizytę</button></div></form>`;
 document.querySelector('#cancelVisit').onclick=()=>visitDialog.close();
 document.querySelector('#addPhoto').onclick=()=>{if(photoDraft.length>=10)return;document.querySelector('#addPhoto').disabled=true;document.querySelector('#photoStatus').textContent='Wybierz zdjęcie…';if(window.Passport)window.Passport.pickPhoto();else document.querySelector('#photoInput').click();};
 document.querySelector('#photoInput').onchange=e=>{const file=e.target.files[0];if(!file){photoFailed();return;}const reader=new FileReader();reader.onload=()=>{const img=new Image();img.onload=()=>{const scale=Math.min(1,1600/Math.max(img.width,img.height)),canvas=document.createElement('canvas');canvas.width=Math.round(img.width*scale);canvas.height=Math.round(img.height*scale);canvas.getContext('2d').drawImage(img,0,0,canvas.width,canvas.height);addVisitPhoto(canvas.toDataURL('image/jpeg',.85));};img.onerror=photoFailed;img.src=reader.result;};reader.onerror=photoFailed;reader.readAsDataURL(file);};
 document.querySelector('#photoInput').oncancel=()=>photoFailed();
 document.querySelector('#visitForm').onsubmit=e=>{
  e.preventDefault();const f=new FormData(e.target),url=String(f.get('trailUrl')).trim();
  if(url){try{const u=new URL(url);if(u.protocol!=='https:'||!(u.hostname==='alltrails.com'||u.hostname.endsWith('.alltrails.com')))throw Error();}catch{document.querySelector('#visitError').textContent='Podaj link HTTPS do trasy w AllTrails.';return;}}
  const entry={id:existing?.id||'',placeId,date:f.get('date'),weather:f.get('weather')==='Nie podano'?'':f.get('weather'),trailUrl:url,notes:f.get('notes'),distance_m:Math.round(Number(f.get('distance'))*1000),duration_minutes:Number(f.get('duration')),elevation_gain_m:Number(f.get('elevation')),photos:[...photoDraft]};
  try{
   if(window.Passport){const result=JSON.parse(window.Passport.saveVisit(JSON.stringify(entry)));if(!result.ok)throw Error(result.error);entry.id=result.visit.id;}
   else{if(!entry.id)entry.id=crypto.randomUUID();const next=visits.filter(x=>x.id!==entry.id).concat(entry);localStorage.setItem('visits',JSON.stringify(next));}
   visits=visits.filter(x=>x.id!==entry.id).concat(entry);visited.add(placeId);visitDialog.close();
   refreshVisitViews();
  }catch(err){document.querySelector('#visitError').textContent=err.message||'Nie udało się zapisać wizyty. Spróbuj ponownie.';}
 };
 paintPhotos();visitDialog.showModal();
}
function paintPhotos(){document.querySelector('#photoGrid').innerHTML=photoDraft.map((p,i)=>`<div><img src="${escapeHtml(photoUrl(p))}" alt="Zdjęcie z wizyty ${i+1}"><button type="button" data-remove-photo="${i}">Usuń zdjęcie</button></div>`).join('');document.querySelectorAll('[data-remove-photo]').forEach(b=>b.onclick=()=>{photoDraft.splice(Number(b.dataset.removePhoto),1);paintPhotos();});document.querySelector('#addPhoto').disabled=photoDraft.length>=10;}
window.addVisitPhoto=id=>{if(!visitDialog.open)return;if(photoDraft.length<10)photoDraft.push(id);paintPhotos();document.querySelector('#photoStatus').textContent='Zdjęcie dodane.';};
window.photoFailed=()=>{if(!visitDialog.open)return;document.querySelector('#addPhoto').disabled=photoDraft.length>=10;document.querySelector('#photoStatus').textContent='Nie dodano zdjęcia. Możesz spróbować ponownie.';};
function renderJournal(){
 const items=visits.filter(v=>catalog.places.some(p=>p.id===v.placeId&&p.country===country)).sort((a,b)=>b.date.localeCompare(a.date));
 document.querySelector('#content').innerHTML=`<section class="journal"><h2>Dziennik podróży</h2>${items.length?items.map(v=>{const p=catalog.places.find(p=>p.id===v.placeId);return `<article><h2>${escapeHtml(p.name)}</h2><p>${escapeHtml(v.date)}${v.weather?' · '+escapeHtml(v.weather):''}</p><p class="muted">${[v.distance_m?(v.distance_m/1000)+' km':'',v.duration_minutes?v.duration_minutes+' min':'',v.elevation_gain_m?'↑ '+v.elevation_gain_m+' m':''].filter(Boolean).join(' · ')}</p>${v.notes?`<p>${escapeHtml(v.notes)}</p>`:''}${v.trailUrl?`<p><a href="${escapeHtml(v.trailUrl)}">Otwórz trasę w AllTrails ↗</a></p>`:''}<div class="photo-grid">${(v.photos||[]).map(id=>`<img src="${escapeHtml(photoUrl(id))}" alt="Zdjęcie z wizyty" loading="lazy">`).join('')}</div><button data-edit-visit="${v.id}">Edytuj wizytę</button></article>`;}).join(''):'<p>Jeszcze nie masz zapisanych wizyt. Wybierz atrakcję na mapie i oznacz ją jako odwiedzoną.</p>'}</section>`;
 document.querySelectorAll('[data-edit-visit]').forEach(b=>b.onclick=()=>{const v=visits.find(v=>v.id===b.dataset.editVisit);openVisit(v.placeId,v);});
}
