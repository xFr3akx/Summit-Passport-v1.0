'use strict';
let collectionData={collections:[],proposals:[]},plans=[],collectionMode='theme',collectionId=null,collectionQuery='',detailRender=null,detailHistory=[],planDraft=null;
const exploreDialog=document.querySelector('#exploreDialog');
function allPlans(){return [...collectionData.proposals,...plans].filter(p=>p.country===country);}
function members(ids){return ids.map(id=>catalog.places.find(p=>p.id===id&&p.country===country&&p.mapReady)).filter(Boolean);}
function progress(ids){const ps=members(ids);return {total:ps.length,done:ps.filter(p=>visited.has(p.id)).length};}
function progressHtml(ids){const n=progress(ids);return `<p class="collection-meta">${n.done} / ${n.total} odwiedzonych</p><div class="progress" role="progressbar" aria-label="Postęp kolekcji" aria-valuemin="0" aria-valuemax="${n.total}" aria-valuenow="${n.done}"><span style="width:${n.total?100*n.done/n.total:0}%"></span></div>`;}
function collectionMembers(c){return members(c.placeIds).filter(p=>normal(p.name).includes(normal(collectionQuery))).sort((a,b)=>Number(visited.has(b.id))-Number(visited.has(a.id))||a.name.localeCompare(b.name,'pl'));}
function renderCollections(){
 const content=document.querySelector('#content');
 if(collectionId){const c=collectionData.collections.find(c=>c.id===collectionId&&c.country===country);if(!c){collectionId=null;renderCollections();return;}
  content.innerHTML=`<section class="collections"><button id="backCollections">‹ Wszystkie kolekcje</button><h2>${escapeHtml(c.title)}</h2>${progressHtml(c.placeIds)}<p class="muted">Odwiedzone miejsca na górze</p><input id="collectionSearch" class="wide-search" type="search" aria-label="Szukaj w kolekcji" placeholder="Szukaj w kolekcji" value="${escapeHtml(collectionQuery)}"><div id="collectionMembers"></div></section>`;
  document.querySelector('#backCollections').onclick=()=>{collectionId=null;collectionQuery='';renderCollections();};document.querySelector('#collectionSearch').oninput=e=>{collectionQuery=e.target.value;paintMembers(c);};paintMembers(c);return;
 }
 content.innerHTML=`<section class="collections"><div class="eyebrow">Twój paszport odkryć</div><h2>Kolekcje</h2><div class="collection-tabs">${[['theme','Tematyczne'],['peaks','Pasma i regiony'],['plans','Kolejność odwiedzin']].map(([id,label])=>`<button data-collection-mode="${id}" aria-pressed="${collectionMode===id}">${label}</button>`).join('')}</div><p class="muted">${collectionMode==='plans'?'Zapisz miejsca w takiej kolejności, w jakiej chcesz je odwiedzić.':'Postęp obejmuje miejsca dostępne w obecnej bazie.'}</p><div id="collectionGrid" class="collection-grid"></div></section>`;
 document.querySelectorAll('[data-collection-mode]').forEach(b=>b.onclick=()=>{collectionMode=b.dataset.collectionMode;renderCollections();});
 if(collectionMode==='plans'){
  document.querySelector('#collectionGrid').innerHTML=`<button id="newPlan" class="primary">+ Ułóż własną kolejność</button>${allPlans().map(p=>`<button class="collection-card" data-plan="${p.id}"><span class="eyebrow">${p.editable?'Twoja lista':'Propozycja'}</span><h3>${escapeHtml(p.title)}</h3>${progressHtml(p.placeIds)}</button>`).join('')}`;
  document.querySelector('#newPlan').onclick=()=>editPlan();document.querySelectorAll('[data-plan]').forEach(b=>b.onclick=()=>showPlan(b.dataset.plan));return;
 }
 const groups=collectionData.collections.filter(c=>c.country===country&&c.kind===collectionMode);
 document.querySelector('#collectionGrid').innerHTML=groups.map(c=>`<button class="collection-card" data-collection="${c.id}">${iconSvg(c.icon)}<h3>${escapeHtml(c.title)}</h3>${progressHtml(c.placeIds)}</button>`).join('');
 document.querySelectorAll('[data-collection]').forEach(b=>b.onclick=()=>{collectionId=b.dataset.collection;collectionQuery='';renderCollections();});
}
function paintMembers(c){const ps=collectionMembers(c);document.querySelector('#collectionMembers').innerHTML=ps.length?ps.map(p=>`<button class="place-row" data-detail-place="${p.id}">${iconSvg(p.category)}<span>${escapeHtml(p.name)}<small>${visited.has(p.id)?'✓ Odwiedzone':'Nieodwiedzone'}</small></span></button>`).join(''):'<p class="empty">Brak pasujących miejsc.</p>';}
function showDetail(render,push=true){if(push&&exploreDialog.open&&detailRender)detailHistory.push(detailRender);if(!exploreDialog.open)detailHistory=[];detailRender=render;render();if(!exploreDialog.open)exploreDialog.showModal();}
function detailHeader(title){return `<div class="detail-head"><h2>${escapeHtml(title)}</h2><button data-detail-close aria-label="Zamknij szczegóły">×</button></div>${detailHistory.length?'<button data-detail-back>‹ Wróć</button>':''}`;}
function detailBack(){if(detailHistory.length){detailRender=detailHistory.pop();detailRender();}else exploreDialog.close();}
function showPlace(id){const p=catalog.places.find(p=>p.id===id&&p.country===country);if(!p)return;showDetail(()=>{exploreDialog.innerHTML=detailHeader(p.name)+`<div class="detail-place">${iconSvg(p.category)}<p>${escapeHtml(labels[p.category])} · ${visited.has(id)?'✓ Odwiedzone':'Nieodwiedzone'}</p><p class="muted">${escapeHtml(p.area)}</p><button data-visit-place="${id}">${visited.has(id)?'Dodaj kolejną wizytę':'Oznacz jako odwiedzone'}</button><button data-show-map="${id}">Pokaż na mapie</button><button data-propose="${id}">Propozycja wycieczki</button></div>`;});}
function showProposals(id){const p=catalog.places.find(p=>p.id===id&&p.country===country);if(!p)return;showDetail(()=>{const matches=allPlans().filter(g=>g.placeIds.includes(id));exploreDialog.innerHTML=detailHeader('Propozycja wycieczki')+`<p>${escapeHtml(p.name)}</p><p class="muted">Kolejność odwiedzin możesz dopasować do swojego wyjazdu.</p>${matches.length?matches.map(g=>`<button class="collection-card" data-plan="${g.id}"><h3>${escapeHtml(g.title)}</h3>${progressHtml(g.placeIds)}</button>`).join(''):'<p>Nie ma jeszcze zapisanej propozycji dla tego miejsca.</p>'}<button data-new-plan="${id}" class="primary">Ułóż własną kolejność</button>`;});}
function showPlan(id){const p=allPlans().find(p=>p.id===id);if(!p)return;showDetail(()=>{exploreDialog.innerHTML=detailHeader(p.title)+`<p class="muted">Kolejność odwiedzin · bez wyznaczania przebiegu trasy</p>${p.description?`<p>${escapeHtml(p.description)}</p>`:''}${progressHtml(p.placeIds)}<ol class="visit-order">${members(p.placeIds).map(x=>`<li><button data-detail-place="${x.id}"><strong>${escapeHtml(x.name)}</strong><small>${visited.has(x.id)?'✓ Odwiedzone':'Nieodwiedzone'}</small></button></li>`).join('')}</ol><button data-edit-plan="${p.id}">${p.editable?'Edytuj kolejność':'Zapisz własną wersję'}</button>${p.editable?`<button data-delete-plan="${p.id}">Usuń listę</button>`:''}`;});}
function editPlan(source,anchor){
 planDraft=source?{id:source.editable?source.id:'',title:source.title,country,placeIds:[...source.placeIds]}:{id:'',title:'',country,placeIds:anchor?[anchor]:[]};
 showDetail(()=>paintPlanEditor(),true);
}
function paintPlanEditor(){
 exploreDialog.innerHTML=detailHeader('Twoja kolejność odwiedzin')+`<label class="plan-label">Nazwa listy<input id="planTitle" maxlength="100" value="${escapeHtml(planDraft.title)}" placeholder="Np. Weekend w górach"></label><ol id="draftOrder" class="visit-order"></ol><label class="plan-label">Dodaj miejsce<input id="planSearch" type="search" placeholder="Wpisz nazwę miejsca" autocomplete="off"></label><div id="planMatches"></div><p id="planError" class="visit-error" role="alert"></p><button id="savePlan" class="primary">Zapisz kolejność</button>`;
 document.querySelector('#planTitle').oninput=e=>planDraft.title=e.target.value;
 document.querySelector('#planSearch').oninput=e=>paintPlanMatches(e.target.value);
 document.querySelector('#savePlan').onclick=()=>{
  if(!planDraft.title.trim()||planDraft.placeIds.length<2){document.querySelector('#planError').textContent='Wpisz nazwę i dodaj co najmniej dwa różne miejsca.';return;}
  const p={...planDraft,id:planDraft.id||'user-'+crypto.randomUUID(),title:planDraft.title.trim(),editable:true};
  try{const next=plans.filter(x=>x.id!==p.id).concat(p);persistPlans(next);plans=next;exploreDialog.close();collectionMode='plans';collectionId=null;activeTab='collections';renderCountry();showPlan(p.id);}catch(e){document.querySelector('#planError').textContent=e.message;}
 };
 paintDraftOrder();
}
function paintDraftOrder(){document.querySelector('#draftOrder').innerHTML=members(planDraft.placeIds).map((p,i)=>`<li><strong>${escapeHtml(p.name)}</strong><div class="order-actions"><button data-move-index="${i}" data-delta="-1" ${i===0?'disabled':''} aria-label="Przesuń ${escapeHtml(p.name)} w górę">↑</button><button data-move-index="${i}" data-delta="1" ${i===planDraft.placeIds.length-1?'disabled':''} aria-label="Przesuń ${escapeHtml(p.name)} w dół">↓</button><button data-remove-index="${i}" aria-label="Usuń ${escapeHtml(p.name)} z listy">Usuń</button></div></li>`).join('');}
function paintPlanMatches(q){const matches=q.trim()?catalog.places.filter(p=>p.country===country&&p.mapReady&&!planDraft.placeIds.includes(p.id)&&normal(p.name).includes(normal(q.trim()))).slice(0,12):[];document.querySelector('#planMatches').innerHTML=matches.map(p=>`<button class="place-row" data-add-plan="${p.id}"><span>${escapeHtml(p.name)}<small>${escapeHtml(p.area)}</small></span><span>+</span></button>`).join('')||(q.trim()?'<p class="muted">Brak nowych pasujących miejsc.</p>':'');}
function persistPlans(next){if(window.Passport){const r=JSON.parse(window.Passport.savePlans(JSON.stringify(next)));if(!r.ok)throw Error('Nie udało się zapisać listy. Spróbuj ponownie.');}else localStorage.setItem('plans',JSON.stringify(next));}
function refreshVisitViews(){if(activeTab==='collections')renderCollections();else if(activeTab==='journal')renderJournal();else if(map){map.closePopup();updateResults();}if(exploreDialog.open&&detailRender)detailRender();}
document.addEventListener('click',e=>{
 const b=e.target.closest('button');if(!b)return;
 if(b.hasAttribute('data-detail-close')){exploreDialog.close();return;}
 if(b.hasAttribute('data-detail-back')){detailBack();return;}
 if(b.dataset.detailPlace){showPlace(b.dataset.detailPlace);return;}
 if(b.dataset.propose){showProposals(b.dataset.propose);return;}
 if(b.dataset.plan&&exploreDialog.contains(b)){showPlan(b.dataset.plan);return;}
 if(b.hasAttribute('data-new-plan')){editPlan(null,b.dataset.newPlan);return;}
 if(b.dataset.editPlan){editPlan(allPlans().find(p=>p.id===b.dataset.editPlan));return;}
 if(b.dataset.deletePlan){const id=b.dataset.deletePlan;showDetail(()=>{exploreDialog.innerHTML=detailHeader('Usunąć listę?')+'<p>Wizyty i ich postęp pozostaną zapisane.</p><button id="confirmDeletePlan">Usuń listę</button><button data-detail-back>Anuluj</button>';document.querySelector('#confirmDeletePlan').onclick=()=>{try{const next=plans.filter(p=>p.id!==id);persistPlans(next);plans=next;exploreDialog.close();if(activeTab==='collections')renderCollections();}catch{document.querySelector('#confirmDeletePlan').textContent='Błąd zapisu — spróbuj ponownie';}};});return;}
 if(b.dataset.showMap){const p=catalog.places.find(p=>p.id===b.dataset.showMap);exploreDialog.close();activeTab='map';listMode=false;filters={q:'',category:'all',unvisited:false};mapFocus=p;renderCountry();return;}
 if(b.dataset.addPlan){if(planDraft.placeIds.length>=100){document.querySelector('#planError').textContent='Lista może zawierać maksymalnie 100 miejsc.';return;}if(!planDraft.placeIds.includes(b.dataset.addPlan))planDraft.placeIds.push(b.dataset.addPlan);paintDraftOrder();paintPlanMatches(document.querySelector('#planSearch').value);return;}
 if(b.hasAttribute('data-move-index')){const i=Number(b.dataset.moveIndex),j=i+Number(b.dataset.delta);if(j>=0&&j<planDraft.placeIds.length){[planDraft.placeIds[i],planDraft.placeIds[j]]=[planDraft.placeIds[j],planDraft.placeIds[i]];paintDraftOrder();}return;}
 if(b.hasAttribute('data-remove-index')){planDraft.placeIds.splice(Number(b.dataset.removeIndex),1);paintDraftOrder();paintPlanMatches(document.querySelector('#planSearch').value);}
});
