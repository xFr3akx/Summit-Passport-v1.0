'use strict';
const WEATHER_VALUES=['','Słonecznie','Częściowe zachmurzenie','Pochmurno','Deszcz','Śnieg','Mgła','Wiatr'];
const visitDialog=document.querySelector('#visitDialog');
document.querySelector('#openLegal').onclick=()=>document.querySelector('#legal').showModal();
document.querySelector('#closeLegal').onclick=()=>document.querySelector('#legal').close();
document.addEventListener('click',e=>{const b=e.target.closest('[data-visit-place]');if(b)openVisit(b.dataset.visitPlace);});
function photoUrl(id){return id.startsWith('data:image/')?id:'photos/'+id;}
function localDate(){const d=new Date();return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;}
function openVisit(placeId,existing){
 const p=catalog.places.find(x=>x.id===placeId);if(!p)return;
 const full=p.category==='peak',v=existing||{date:localDate()};photoDraft=[...(v.photos||[])];
 visitDialog.innerHTML=`<h2>${existing?t('Edytuj wizytę'):t('Twoja wizyta')}</h2><p>${escapeHtml(p.name)}</p><form class="visit-form" id="visitForm">
 <label>${t("Data wizyty")}<input name="date" type="date" required value="${escapeHtml(v.date)}"></label>
 <fieldset class="rating-field"><legend>${t("Twoja ocena")}</legend><input type="hidden" name="rating" value="${v.rating||0}"><div class="rating-choices">${[1,2,3,4,5].map(n=>`<button type="button" data-rating="${n}" aria-label="${t("Ocena {n} z 5",{n})}" aria-pressed="${v.rating===n}">${n<=(v.rating||0)?'★':'☆'}</button>`).join('')}</div><button type="button" id="clearRating">${t("Bez oceny")}</button></fieldset>
 <label>${t("Pogoda")}<select name="weather">${WEATHER_VALUES.map(w=>`<option value="${escapeHtml(w)}" ${v.weather===w?'selected':''}>${escapeHtml(t(w||'Nie podano'))}</option>`).join('')}</select></label>
 ${full?`<label>${t("Trasa / AllTrails")}<input name="trailUrl" type="text" maxlength="4000" value="${escapeHtml(v.trailUrl||'')}"></label>
 <label>${t("Dystans (km)")}<input name="distance" type="number" min="0" max="100000" step="0.01" value="${v.distance_m?v.distance_m/1000:''}"></label>
 <label>${t("Czas (minuty)")}<input name="duration" type="number" min="0" max="10000000" step="1" value="${v.duration_minutes||''}"></label>
 <label>${t("Suma podejść (m)")}<input name="elevation" type="number" min="0" max="10000000" step="1" value="${v.elevation_gain_m||''}"></label>`:''}
 <label>${t("Notatki")}<textarea name="notes" maxlength="20000" placeholder="${escapeHtml(t("Co chcesz zapamiętać?"))}">${escapeHtml(v.notes||'')}</textarea></label>

 <p class="muted">${t("Datę i szczegóły możesz później zmienić w Dzienniku.")}</p><p id="visitError" class="visit-error" role="alert"></p>
 <div class="visit-actions"><button type="button" id="cancelVisit">${t("Anuluj")}</button><button type="submit" class="primary">${t("Zapisz wizytę")}</button></div></form>`;
 document.querySelector('#cancelVisit').onclick=()=>visitDialog.close();
 const chooseRating=n=>{document.querySelector('[name=rating]').value=n;document.querySelectorAll('[data-rating]').forEach(b=>{b.textContent=Number(b.dataset.rating)<=n?'★':'☆';b.setAttribute('aria-pressed',String(Number(b.dataset.rating)===n));});};
 document.querySelectorAll('[data-rating]').forEach(b=>b.onclick=()=>chooseRating(Number(b.dataset.rating)));document.querySelector('#clearRating').onclick=()=>chooseRating(0);
 document.querySelector('#visitForm').onsubmit=e=>{
  e.preventDefault();const f=new FormData(e.target);
  const entry={id:existing?.id||'',placeId,date:f.get('date'),rating:Number(f.get('rating')),weather:f.get('weather'),trailUrl:full?String(f.get('trailUrl')||'').trim():(v.trailUrl||''),notes:f.get('notes'),distance_m:full?Math.round(Number(f.get('distance'))*1000):(v.distance_m||0),duration_minutes:full?Number(f.get('duration')):(v.duration_minutes||0),elevation_gain_m:full?Number(f.get('elevation')):(v.elevation_gain_m||0),photos:[...photoDraft]};
  try{
   if(window.Passport){const result=JSON.parse(window.Passport.saveVisit(JSON.stringify(entry)));if(!result.ok)throw Error(result.error);entry.id=result.visit.id;}
   else{if(!entry.id)entry.id=crypto.randomUUID();const next=visits.filter(x=>x.id!==entry.id).concat(entry);localStorage.setItem('visits',JSON.stringify(next));}
   visits=visits.filter(x=>x.id!==entry.id).concat(entry);visited.add(placeId);visitDialog.close();
   refreshVisitViews();
  }catch(err){document.querySelector('#visitError').textContent=t(err.message)||t('Nie udało się zapisać wizyty. Spróbuj ponownie.');}
 };
 visitDialog.showModal();
}
function paintPhotos(){if(!document.querySelector('#photoGrid'))return;document.querySelector('#photoGrid').innerHTML=photoDraft.map((p,i)=>`<div><img src="${escapeHtml(photoUrl(p))}" alt="${t("Zdjęcie z wizyty {n}",{n:i+1})}"><button type="button" data-remove-photo="${i}">${t("Usuń zdjęcie")}</button></div>`).join('');document.querySelectorAll('[data-remove-photo]').forEach(b=>b.onclick=()=>{photoDraft.splice(Number(b.dataset.removePhoto),1);paintPhotos();});document.querySelector('#addPhoto').disabled=photoDraft.length>=10;}
window.addVisitPhoto=id=>{if(!visitDialog.open||!document.querySelector('#photoGrid'))return;if(photoDraft.length<10)photoDraft.push(id);paintPhotos();document.querySelector('#photoStatus').textContent=t('Zdjęcie dodane.');};
window.photoFailed=()=>{if(!visitDialog.open||!document.querySelector('#photoGrid'))return;document.querySelector('#addPhoto').disabled=photoDraft.length>=10;document.querySelector('#photoStatus').textContent=t('Nie dodano zdjęcia. Możesz spróbować ponownie.');};
const journalFilters={date:'',rating:0,sort:'newest'};
const weatherSymbols=['','☀','⛅','☁','☂','❄','≋','༄'];
function journalIcon(symbol,label){
 const paths={
 'Słonecznie':'M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5 M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0',
 'Częściowe zachmurzenie':'M8 2v2M2 8h2m0-5 1 1m7-1-1 1M11 8a3 3 0 1 0-5 3 M6 20a4 4 0 0 1-1-8 6 6 0 0 1 11-1 4.5 4.5 0 1 1 2 9Z',
 'Pochmurno':'M6 19a4 4 0 0 1-1-8 6 6 0 0 1 11-1 4.5 4.5 0 1 1 2 9Z',
 'Deszcz':'M6 15a3 3 0 0 1-1-6 5 5 0 0 1 10-1 3.5 3.5 0 1 1 2 7H6m1 3-1 3m6-3-1 3m6-3-1 3',
 'Śnieg':'M12 2v20M3.3 7l17.4 10M3.3 17 20.7 7M9 4l3 3 3-3M9 20l3-3 3 3M4 10l4-1-1-4m10 14-1-4 4-1M4 14l4 1-1 4m10-14-1 4 4 1',
 'Mgła':'M4 6h16M2 10h16M6 14h16M3 18h16',
 'Wiatr':'M3 8h12a3 3 0 1 0-3-3M2 12h17a3 3 0 1 1-3 3M4 17h5a2 2 0 1 1-2 2',
 'Dystans':'M3 12h18M7 8l-4 4 4 4m10-8 4 4-4 4',
 'Suma podejść':'M12 21V3m-5 5 5-5 5 5',
 'Czas w terenie':'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0M12 6v6l4 2',
 'Notatki':'M6 3h14v18H6ZM3 6h5M3 10h5M3 14h5M3 18h5M11 8h5m-5 4h5m-5 4h3'};
 const art=paths[label]?`<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${paths[label]}" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>`:symbol;
 return `<span class="journal-weather" role="img" aria-label="${escapeHtml(t(label))}" title="${escapeHtml(t(label))}">${art}</span>`;
}

function renderJournal(){
 const all=visits.filter(v=>catalog.places.some(p=>p.id===v.placeId&&p.country===country));
 const items=all.filter(v=>(!journalFilters.date||v.date===journalFilters.date)&&(v.rating||0)>=journalFilters.rating).sort((a,b)=>journalFilters.sort==='oldest'?a.date.localeCompare(b.date):journalFilters.sort==='rating'?(b.rating||0)-(a.rating||0)||b.date.localeCompare(a.date):b.date.localeCompare(a.date));
 document.querySelector('#content').innerHTML=`<section class="journal"><h2>${t("Dziennik podróży")}</h2><div class="journal-filters"><label>${t('Dzień odwiedzin')}<input id="journalDate" type="date" value="${journalFilters.date}"></label><label>${t('Ocena minimalna')}<select id="journalRating">${[0,1,2,3,4,5].map(n=>`<option value="${n}" ${journalFilters.rating===n?'selected':''}>${n?'★'.repeat(n)+'+':t('Wszystkie oceny')}</option>`).join('')}</select></label><label>${t('Sortowanie')}<select id="journalSort">${[['newest','Najnowsze'],['oldest','Najstarsze'],['rating','Najwyżej ocenione']].map(([key,label])=>`<option value="${key}" ${journalFilters.sort===key?'selected':''}>${t(label)}</option>`).join('')}</select></label><button id="resetJournalFilters">${t('Wyczyść filtry')}</button></div>${items.length?items.map(v=>{const p=catalog.places.find(p=>p.id===v.placeId);return `<article><div class="journal-heading"><span class="journal-symbol" role="img" aria-label="${escapeHtml(labels[p.category])}">${iconSvg(p.category)}</span><div><h2>${escapeHtml(p.name)}</h2><p class="visit-date">${escapeHtml(v.date)}</p><div class="journal-rating" aria-label="${v.rating?t("Ocena {n} z 5",{n:v.rating}):t('Bez oceny')}">${v.rating?'★'.repeat(v.rating)+'☆'.repeat(5-v.rating):`<span class="muted">${t("Bez oceny")}</span>`}</div></div></div><div class="journal-metrics">${v.weather?journalIcon(weatherSymbols[WEATHER_VALUES.indexOf(v.weather)]||'☁',v.weather):''}${p.category==='peak'?[v.distance_m?`<span>${journalIcon('↔','Dystans')} ${numberLabel(v.distance_m/1000)} km</span>`:'',v.duration_minutes?`<span>${journalIcon('◷','Czas w terenie')} ${v.duration_minutes} min</span>`:'',v.elevation_gain_m?`<span>${journalIcon('↑','Suma podejść')} ${v.elevation_gain_m} m</span>`:''].join(''):''}</div>${v.notes?`<p class="journal-note">${journalIcon('▤','Notatki')} ${escapeHtml(v.notes)}</p>`:''}${p.category==='peak'&&v.trailUrl?`<p class="journal-route">${t('Trasa / AllTrails')}: ${escapeHtml(v.trailUrl)}</p>`:''}<div class="journal-actions"><button data-edit-visit="${v.id}">${t("Edytuj wizytę")}</button><button class="delete-visit" data-delete-visit="${v.id}" aria-label="${escapeHtml(t("Usuń wizytę: {name}, {date}",{name:p.name,date:v.date}))}" title="${escapeHtml(t("Usuń wizytę"))}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M9 7V4h6v3M6 7l1 14h10l1-14M10 10v7M14 10v7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button></div></article>`;}).join(''):`<p>${t(all.length?'Brak wizyt spełniających filtry.':'Jeszcze nie masz zapisanych wizyt. Wybierz atrakcję na mapie i oznacz ją jako odwiedzoną.')}</p>`}</section>`;
 document.querySelector('#journalDate').onchange=e=>{journalFilters.date=e.target.value;renderJournal();};
 document.querySelector('#journalRating').onchange=e=>{journalFilters.rating=Number(e.target.value);renderJournal();};
 document.querySelector('#journalSort').onchange=e=>{journalFilters.sort=e.target.value;renderJournal();};
 document.querySelector('#resetJournalFilters').onclick=()=>{Object.assign(journalFilters,{date:'',rating:0,sort:'newest'});renderJournal();};
 document.querySelectorAll('[data-delete-visit]').forEach(b=>b.onclick=()=>confirmDeleteVisit(b.dataset.deleteVisit));
 document.querySelectorAll('[data-edit-visit]').forEach(b=>b.onclick=()=>{const v=visits.find(v=>v.id===b.dataset.editVisit);openVisit(v.placeId,v);});
}

function confirmDeleteVisit(id){
 const v=visits.find(x=>x.id===id);if(!v)return;const p=catalog.places.find(x=>x.id===v.placeId);
 visitDialog.innerHTML=`<h2>${t("Usunąć tę wizytę?")}</h2><p>${escapeHtml(p?.name)} · ${escapeHtml(v.date)}</p><p>${t("Usunięty zostanie ten wpis z notatką i oceną. Pozostałe wizyty zostaną zachowane.")}</p><p id="deleteVisitError" class="visit-error" role="alert"></p><div class="visit-actions"><button id="cancelDeleteVisit">${t("Anuluj")}</button><button id="confirmDeleteVisit" class="delete-visit">${t("Usuń wizytę")}</button></div>`;
 document.querySelector('#cancelDeleteVisit').onclick=()=>visitDialog.close();
 document.querySelector('#confirmDeleteVisit').onclick=()=>{
  try{const next=visits.filter(x=>x.id!==id);if(window.Passport){const result=JSON.parse(window.Passport.deleteVisit(id));if(!result.ok)throw Error();}else localStorage.setItem('visits',JSON.stringify(next));visits=next;visited=new Set(visits.map(x=>x.placeId));visitDialog.close();refreshVisitViews();}
  catch{document.querySelector('#deleteVisitError').textContent=t('Nie udało się usunąć wizyty. Spróbuj ponownie.');}
 };visitDialog.showModal();
}
