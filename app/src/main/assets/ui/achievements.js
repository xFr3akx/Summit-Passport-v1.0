'use strict';
let achievementData=null,achievementUnlocks=[],achievementSaveError=false;
function syncAchievements(){if(!achievementData||!catalog)return;const next=AchievementEngine.unlocks(achievementData,catalog.places,visits,collectionData.collections,achievementUnlocks);if(next.length===achievementUnlocks.length&&!achievementSaveError)return;try{if(window.Passport?.saveAchievements){const result=JSON.parse(window.Passport.saveAchievements(JSON.stringify(next)));if(!result.ok)throw Error();achievementUnlocks=result.awards;}else{localStorage.setItem('achievements',JSON.stringify(next));achievementUnlocks=next;}achievementSaveError=false;}catch{achievementSaveError=true;}}
function familyAwards(f){return achievementUnlocks.filter(a=>a.country===country&&a.family===f.id);}
function earnedTier(f){return familyAwards(f).reduce((tier,a)=>Math.max(tier,a.tier),-1);}
function earnedText(f,tier){const a=familyAwards(f).find(a=>a.tier===tier);return a?t('Zdobyto: {date}',{date:a.earnedOn}):t('Jeszcze niezdobyta');}

const badgePositions=[[35,135],[218,139],[394,139],[578,135],[33,379],[216,378],[393,380],[577,378],[34,613],[216,612],[393,611],[578,612]];
function badgeArt(family,tier){const [x,y]=badgePositions[family.art];const metals=['bronze','bronze','silver','silver','gold','gold','diamond','diamond','master','master','master'];return `<div class="badge-shell ${metals[Math.max(0,tier)]}"><div class="badge-art" style="--atlas-x:${-x*.75}px;--atlas-y:${-y*.75}px"></div><span class="badge-level">${tier<0?t('Jeszcze niezdobyta'):escapeHtml(t(achievementData.tiers[tier]))}</span></div>`;}
function badgeTitle(f){return f.countryTitles?.[country]||f.title;}
function badgeValue(f){return AchievementEngine.value(f,country,catalog.places,visits,collectionData.collections);}
function numberLabel(n){return Number.isInteger(n)?String(n):n.toLocaleString(language,{maximumFractionDigits:1});}
function badgeUnit(f,n){
 const forms={peak:['szczyt','szczyty','szczytów'],castle:['zamek','zamki','zamków'],cave:['jaskinia','jaskinie','jaskiń'],waterfall:['wodospad','wodospady','wodospadów']};
 if(!forms[f.id])return t(f.unit);
 const plural=n===1?0:n%10>=2&&n%10<=4&&!(n%100>=12&&n%100<=14)?1:2;
 return t(forms[f.id][plural]);
}
function badgeProgress(value,max,label){return `<div class="progress" role="progressbar" aria-label="${escapeHtml(label)}" aria-valuenow="${Math.min(max,value||0)}" aria-valuemin="0" aria-valuemax="${max}"><span style="width:${Math.min(100,Math.max(0,(value||0)/max*100))}%"></span></div>`;}
async function renderAchievements(){
 const target=document.querySelector('#content');target.innerHTML=`<p class="loading">${t("Przygotowanie odznak…")}</p>`;
 if(!achievementData)achievementData=await(await fetch('achievements.json')).json();if(activeTab!=='achievements'||!target.isConnected)return;syncAchievements();
 target.innerHTML=`<section class="achievements"><h2>${t("Twoje odznaki")}</h2><div class="achievement-countries">${['PL','DE'].map(c=>`<button data-achievement-country="${c}" aria-pressed="${country===c}">${c==='PL'?t('Polska'):t('Niemcy')}</button>`).join('')}</div><p class="badge-proposal">${t("Zdobyte odznaki i ich daty pozostają zapisane. Bieżący postęp wynika z Twoich wizyt.")}</p>${achievementSaveError?`<p class="visit-error" role="alert">${t("Nie udało się zapisać odznak. Otwórz tę zakładkę ponownie, aby spróbować jeszcze raz.")}</p>`:''}<div class="badge-grid">${achievementData.families.map(f=>{const tier=earnedTier(f),count=familyAwards(f).length;return `<button class="badge-card" data-badge="${f.id}"><span class="badge-mini" aria-hidden="true">${badgeArt(f,tier)}</span><span class="badge-summary"><strong>${escapeHtml(badgeTitle(f))}</strong>${badgeProgress(count,11,t('Zdobyte progi'))}<span class="badge-count">${count}/11 · ${t('Zdobyte progi')}</span></span></button>`;}).join('')}</div></section>`;
 document.querySelectorAll('[data-badge]').forEach(b=>b.onclick=()=>showBadge(b.dataset.badge));
 document.querySelectorAll('[data-achievement-country]').forEach(b=>b.onclick=()=>{country=b.dataset.achievementCountry;sessionStorage.setItem('country',country);if(window.Passport)window.Passport.setCountry(country);renderCountry();});
}
function showBadge(id){const f=achievementData.families.find(f=>f.id===id);let selected=Math.max(0,earnedTier(f));showDetail(()=>{
 const paint=()=>{const value=badgeValue(f),threshold=f.thresholds[selected];exploreDialog.innerHTML=detailHeader(badgeTitle(f))+`<p class="badge-description">${escapeHtml(t(f.description))}</p><div class="badge-detail-row"><div class="badge-hero">${badgeArt(f,selected)}</div><div class="badge-detail-progress"><p>${t('Próg {n}',{n:selected+1})} · <strong>${numberLabel(threshold)} ${badgeUnit(f,threshold)}</strong></p>${badgeProgress(value,threshold,t('Bieżący postęp'))}<p>${numberLabel(value||0)} / ${numberLabel(threshold)} ${badgeUnit(f,threshold)}</p><p class="badge-earned">${escapeHtml(earnedText(f,selected))}</p></div></div><p class="muted">${t('Zdobyte odznaki i ich daty pozostają zapisane. Bieżący postęp wynika z Twoich wizyt.')}</p><div class="badge-tiers">${achievementData.tiers.map((label,i)=>`<button data-tier="${i}" aria-pressed="${i===selected}"><span class="tier-dot tier-${Math.floor(i/2)}"></span>${escapeHtml(t(label))}${familyAwards(f).some(a=>a.tier===i)?' ✓':''}<small>${t('Próg {n}',{n:i+1})} · ${numberLabel(f.thresholds[i])} ${badgeUnit(f,f.thresholds[i])}${familyAwards(f).find(a=>a.tier===i)?' · '+familyAwards(f).find(a=>a.tier===i).earnedOn:''}</small></button>`).join('')}</div>`;document.querySelectorAll('[data-tier]').forEach(b=>b.onclick=()=>{selected=Number(b.dataset.tier);paint();});};paint();
 });}
