'use strict';
let achievementData=null,achievementUnlocks=[],achievementSaveError=false;
function syncAchievements(){if(!achievementData||!catalog)return;const next=AchievementEngine.unlocks(achievementData,catalog.places,visits,collectionData.collections,achievementUnlocks);if(next.length===achievementUnlocks.length&&!achievementSaveError)return;try{if(window.Passport?.saveAchievements){const result=JSON.parse(window.Passport.saveAchievements(JSON.stringify(next)));if(!result.ok)throw Error();achievementUnlocks=result.awards;}else{localStorage.setItem('achievements',JSON.stringify(next));achievementUnlocks=next;}achievementSaveError=false;}catch{achievementSaveError=true;}}
function familyAwards(f){return achievementUnlocks.filter(a=>a.country===country&&a.family===f.id);}
function earnedTier(f){return familyAwards(f).reduce((tier,a)=>Math.max(tier,a.tier),-1);}
function earnedText(f,tier){const a=familyAwards(f).find(a=>a.tier===tier);return a?t('Zdobyto: {date}',{date:a.earnedOn}):t('Jeszcze niezdobyta');}

const badgePositions=[[35,135],[218,139],[394,139],[578,135],[33,379],[216,378],[393,380],[577,378],[34,613],[216,612],[393,611],[578,612]];
function rankName(tier){return tier<0?t('Jeszcze niezdobyta'):tier>=8?'Master '+(tier-7):t(achievementData.tiers[tier]);}
function rankStars(count){return `<svg class="rank-stars" viewBox="0 0 ${count*24} 24" aria-hidden="true">${Array.from({length:count},(_,i)=>`<path data-rank-star transform="translate(${i*24},0)" d="M12 2l3 6.2 6.9 1-5 4.8 1.2 6.8L12 17.6l-6.1 3.2L7 14l-5-4.8 6.9-1Z" fill="#efca68" stroke="#866027" stroke-width="1.1"/>`).join('')}</svg>`;}
function badgeArt(family,tier){
 const [x,y]=badgePositions[family.art],metals=['bronze','bronze','silver','silver','gold','gold','diamond','diamond','master','master','master'],metal=tier<0?'locked':metals[tier];
 // Peak ranks reuse the approved A1 illustrations. Master stars are drawn separately
 // to ensure that two stars are distinct, aligned, and independent of font glyphs.
 const rankX=[27,126,225,225,323,323,421,421,518,518,518][Math.max(0,tier)],rankWidth=[83,84,85,85,85,85,86,86,88,88,88][Math.max(0,tier)];
 const art=family.id==='peak'?`<svg class="rank-picture" viewBox="0 0 100 132" aria-hidden="true"><svg width="100" height="132" viewBox="${rankX} 1072 ${rankWidth} 113" preserveAspectRatio="none" style="clip-path:polygon(50% 0,98% 24%,98% 77%,50% 100%,2% 77%,2% 24%)"><image href="badge-ranks-source.png" width="1024" height="1536"/></svg></svg>`:`<div class="family-art badge-art ${[1,2,4,6,8,10].includes(family.art)?'round-art':'shield-art'}" style="--atlas-x:${-x*.75}px;--atlas-y:${-y*.75}px"></div>`;
 return `<div class="badge-shell ${metal}" data-art-tier="${tier}"><div class="rank-art ${family.id==='peak'?'peak-art':''}">${art}${tier>=8?`<span class="master-insignia">${rankStars(tier-7)}</span>`:tier>=0?`<span class="rank-insignia">${tier%2===0?'I':'II'}</span>`:'<span class="rank-insignia">—</span>'}</div><span class="badge-level">${escapeHtml(rankName(tier))}</span></div>`;
}

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
 target.innerHTML=`<section class="achievements"><h2>${t("Twoje odznaki")}</h2><div class="achievement-countries">${['PL','DE'].map(c=>`<button data-achievement-country="${c}" aria-pressed="${country===c}">${c==='PL'?t('Polska'):t('Niemcy')}</button>`).join('')}</div><p class="badge-proposal">${t("Zdobyte odznaki i ich daty pozostają zapisane. Bieżący postęp wynika z Twoich wizyt.")}</p>${achievementSaveError?`<p class="visit-error" role="alert">${t("Nie udało się zapisać odznak. Otwórz tę zakładkę ponownie, aby spróbować jeszcze raz.")}</p>`:''}<div class="badge-grid">${achievementData.families.map(f=>{const tier=earnedTier(f),count=familyAwards(f).length;return `<button class="badge-card" data-badge="${f.id}"><span class="badge-mini" aria-hidden="true">${badgeArt(f,tier)}</span><span class="badge-summary"><strong>${escapeHtml(badgeTitle(f))}</strong><span class="badge-current-rank">${escapeHtml(rankName(tier))}</span>${badgeProgress(count,11,t('Zdobyte progi'))}<span class="badge-count">${count}/11 · ${t('Zdobyte progi')}</span></span></button>`;}).join('')}</div></section>`;
 document.querySelectorAll('[data-badge]').forEach(b=>b.onclick=()=>showBadge(b.dataset.badge));
 document.querySelectorAll('[data-achievement-country]').forEach(b=>b.onclick=()=>{country=b.dataset.achievementCountry;sessionStorage.setItem('country',country);if(window.Passport)window.Passport.setCountry(country);renderCountry();});
}
function showBadge(id){const f=achievementData.families.find(f=>f.id===id);let selected=Math.max(0,earnedTier(f));showDetail(()=>{
 const paint=()=>{const value=badgeValue(f),threshold=f.thresholds[selected];exploreDialog.innerHTML=detailHeader(badgeTitle(f))+`<div class="badge-focus"><div class="badge-hero">${badgeArt(f,selected)}</div><div class="badge-detail-progress"><p class="badge-target">${t('Próg {n} - cel:',{n:selected+1})} <strong>${numberLabel(threshold)} ${badgeUnit(f,threshold)}</strong></p>${badgeProgress(value,threshold,t('Bieżący postęp'))}<p>${numberLabel(value||0)} / ${numberLabel(threshold)} ${badgeUnit(f,threshold)}</p><p class="badge-earned">${escapeHtml(earnedText(f,selected))}</p></div>${selected<10?`<button id="nextBadgeTier">${t('Następny:')} ${escapeHtml(rankName(selected+1))} · ${numberLabel(f.thresholds[selected+1])} ${badgeUnit(f,f.thresholds[selected+1])}</button>`:''}</div><p class="badge-description">${escapeHtml(t(f.description))}</p><details class="badge-all-tiers"><summary>${t('Wszystkie progi')}</summary><div class="badge-tiers">${achievementData.tiers.map((label,i)=>`<button data-tier="${i}" aria-pressed="${i===selected}"><span class="tier-dot tier-${Math.floor(i/2)}"></span>${escapeHtml(rankName(i))}${i>=8?rankStars(i-7):''}${familyAwards(f).some(a=>a.tier===i)?' ✓':''}<small>${t('Próg {n}',{n:i+1})} · ${numberLabel(f.thresholds[i])} ${badgeUnit(f,f.thresholds[i])}${familyAwards(f).find(a=>a.tier===i)?' · '+familyAwards(f).find(a=>a.tier===i).earnedOn:''}</small></button>`).join('')}</div></details><p class="muted">${t('Zdobyte odznaki i ich daty pozostają zapisane. Bieżący postęp wynika z Twoich wizyt.')}</p>`;
 document.querySelectorAll('[data-tier]').forEach(b=>b.onclick=()=>{selected=Number(b.dataset.tier);paint();document.querySelector('#exploreDialog').scrollTop=0;});const next=document.querySelector('#nextBadgeTier');if(next)next.onclick=()=>{selected++;paint();document.querySelector('#exploreDialog').scrollTop=0;};};paint();
 });}
