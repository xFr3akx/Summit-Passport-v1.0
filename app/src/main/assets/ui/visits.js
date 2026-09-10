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
 <fieldset class="rating-field"><legend>Twoja ocena</legend><input type="hidden" name="rating" value="${v.rating||0}"><div class="rating-choices">${[1,2,3,4,5].map(n=>`<button type="button" data-rating="${n}" aria-label="Ocena ${n} z 5" aria-pressed="${v.rating===n}">${n<=(v.rating||0)?'★':'☆'}</button>`).join('')}</div><button type="button" id="clearRating">Bez oceny</button></fieldset>
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
 const chooseRating=n=>{document.querySelector('[name=rating]').value=n;document.querySelectorAll('[data-rating]').forEach(b=>{b.textContent=Number(b.dataset.rating)<=n?'★':'☆';b.setAttribute('aria-pressed',String(Number(b.dataset.rating)===n));});};
 document.querySelectorAll('[data-rating]').forEach(b=>b.onclick=()=>chooseRating(Number(b.dataset.rating)));document.querySelector('#clearRating').onclick=()=>chooseRating(0);
 document.querySelector('#addPhoto').onclick=()=>{if(photoDraft.length>=10)return;document.querySelector('#addPhoto').disabled=true;document.querySelector('#photoStatus').textContent='Wybierz zdjęcie…';if(window.Passport)window.Passport.pickPhoto();else document.querySelector('#photoInput').click();};
 document.querySelector('#photoInput').onchange=e=>{const file=e.target.files[0];if(!file){photoFailed();return;}const reader=new FileReader();reader.onload=()=>{const img=new Image();img.onload=()=>{const scale=Math.min(1,1600/Math.max(img.width,img.height)),canvas=document.createElement('canvas');canvas.width=Math.round(img.width*scale);canvas.height=Math.round(img.height*scale);canvas.getContext('2d').drawImage(img,0,0,canvas.width,canvas.height);addVisitPhoto(canvas.toDataURL('image/jpeg',.85));};img.onerror=photoFailed;img.src=reader.result;};reader.onerror=photoFailed;reader.readAsDataURL(file);};
 document.querySelector('#photoInput').oncancel=()=>photoFailed();
 document.querySelector('#visitForm').onsubmit=e=>{
  e.preventDefault();const f=new FormData(e.target),url=String(f.get('trailUrl')).trim();
  if(url){try{const u=new URL(url);if(u.protocol!=='https:'||!(u.hostname==='alltrails.com'||u.hostname.endsWith('.alltrails.com')))throw Error();}catch{document.querySelector('#visitError').textContent='Podaj link HTTPS do trasy w AllTrails.';return;}}
  const entry={id:existing?.id||'',placeId,date:f.get('date'),rating:Number(f.get('rating')),weather:f.get('weather')==='Nie podano'?'':f.get('weather'),trailUrl:url,notes:f.get('notes'),distance_m:Math.round(Number(f.get('distance'))*1000),duration_minutes:Number(f.get('duration')),elevation_gain_m:Number(f.get('elevation')),photos:[...photoDraft]};
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
 document.querySelector('#content').innerHTML=`<section class="journal"><h2>Dziennik podróży</h2>${items.length?items.map(v=>{const p=catalog.places.find(p=>p.id===v.placeId);return `<article><div class="journal-heading"><span class="journal-symbol" role="img" aria-label="${escapeHtml(labels[p.category])}">${iconSvg(p.category)}</span><div><h2>${escapeHtml(p.name)}</h2><p class="visit-date">${escapeHtml(v.date)}</p><div class="journal-rating" aria-label="${v.rating?'Ocena '+v.rating+' z 5':'Bez oceny'}">${v.rating?'★'.repeat(v.rating)+'☆'.repeat(5-v.rating):'<span class="muted">Bez oceny</span>'}</div></div></div><p>${v.weather?escapeHtml(v.weather):''}</p><p class="muted">${[v.distance_m?(v.distance_m/1000)+' km':'',v.duration_minutes?v.duration_minutes+' min':'',v.elevation_gain_m?'↑ '+v.elevation_gain_m+' m':''].filter(Boolean).join(' · ')}</p>${v.notes?`<p>${escapeHtml(v.notes)}</p>`:''}${v.trailUrl?`<p><a href="${escapeHtml(v.trailUrl)}">Otwórz trasę w AllTrails ↗</a></p>`:''}<div class="photo-grid">${(v.photos||[]).map(id=>`<img src="${escapeHtml(photoUrl(id))}" alt="Zdjęcie z wizyty" loading="lazy">`).join('')}</div><div class="journal-actions"><button data-edit-visit="${v.id}">Edytuj wizytę</button><button class="delete-visit" data-delete-visit="${v.id}" aria-label="Usuń wizytę: ${escapeHtml(p.name)}, ${escapeHtml(v.date)}" title="Usuń wizytę"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M9 7V4h6v3M6 7l1 14h10l1-14M10 10v7M14 10v7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button></div></article>`;}).join(''):'<p>Jeszcze nie masz zapisanych wizyt. Wybierz atrakcję na mapie i oznacz ją jako odwiedzoną.</p>'}</section>`;
 document.querySelectorAll('[data-delete-visit]').forEach(b=>b.onclick=()=>confirmDeleteVisit(b.dataset.deleteVisit));
 document.querySelectorAll('[data-edit-visit]').forEach(b=>b.onclick=()=>{const v=visits.find(v=>v.id===b.dataset.editVisit);openVisit(v.placeId,v);});
}

function confirmDeleteVisit(id){
 const v=visits.find(x=>x.id===id);if(!v)return;const p=catalog.places.find(x=>x.id===v.placeId);
 visitDialog.innerHTML=`<h2>Usunąć tę wizytę?</h2><p>${escapeHtml(p?.name)} · ${escapeHtml(v.date)}</p><p>Usunięty zostanie ten wpis z notatką, oceną i przypisanymi zdjęciami. Pozostałe wizyty zostaną zachowane.</p><p id="deleteVisitError" class="visit-error" role="alert"></p><div class="visit-actions"><button id="cancelDeleteVisit">Anuluj</button><button id="confirmDeleteVisit" class="delete-visit">Usuń wizytę</button></div>`;
 document.querySelector('#cancelDeleteVisit').onclick=()=>visitDialog.close();
 document.querySelector('#confirmDeleteVisit').onclick=()=>{
  try{const next=visits.filter(x=>x.id!==id);if(window.Passport){const result=JSON.parse(window.Passport.deleteVisit(id));if(!result.ok)throw Error();}else localStorage.setItem('visits',JSON.stringify(next));visits=next;visited=new Set(visits.map(x=>x.placeId));visitDialog.close();refreshVisitViews();}
  catch{document.querySelector('#deleteVisitError').textContent='Nie udało się usunąć wizyty. Spróbuj ponownie.';}
 };visitDialog.showModal();
}
