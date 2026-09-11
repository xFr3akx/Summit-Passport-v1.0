'use strict';
const AchievementEngine={
 value(family,country,places,visits,collections){
  const local=new Map(places.filter(p=>p.country===country&&p.mapReady).map(p=>[p.id,p]));
  const entries=visits.filter(v=>local.has(v.placeId)),ids=new Set(entries.map(v=>v.placeId));
  switch(family.metric){
   case 'unique':return [...ids].filter(id=>family.key==='all'||local.get(id).category===family.key).length;
   case 'sum':return entries.reduce((sum,v)=>sum+(Number(v[family.key])||0),0)/(family.key==='distance_m'?1000:family.key==='duration_minutes'?60:1);
   case 'percent':return local.size?100*ids.size/local.size:0;
   case 'collections':return collections.filter(c=>c.country===country&&c.placeIds.length&&c.placeIds.every(id=>ids.has(id))).length;
   case 'mustsee':return [...ids].filter(id=>local.get(id).mustSee).length;
   case 'regions':return new Set([...ids].map(id=>local.get(id).regionCode).filter(Boolean)).size;
   default:return null;
  }
 },
 tier(value,thresholds){if(value===null)return -1;let tier=-1;thresholds.forEach((n,i)=>{if(value>=n)tier=i;});return tier;},
 unlocks(config,places,visits,collections,existing=[],now=new Date().toISOString()){
  const result=existing.map(row=>({...row})),known=new Set(result.map(row=>`${row.country}/${row.family}/${row.tier}`));
  for(const country of ['PL','DE']){
   const local=new Map(places.filter(p=>p.country===country&&p.mapReady).map(p=>[p.id,p]));
   const seen=new Set(),regions=new Set(),categories={},sums={},memberships=new Map(),remaining=new Map();let mustsee=0,completed=0;
   for(const c of collections.filter(c=>c.country===country&&c.placeIds.length)){remaining.set(c.id,c.placeIds.length);for(const id of c.placeIds){if(!memberships.has(id))memberships.set(id,[]);memberships.get(id).push(c.id);}}
   const timeline=visits.filter(v=>local.has(v.placeId)).slice().sort((a,b)=>a.date.localeCompare(b.date)||String(a.id).localeCompare(String(b.id)));
   for(const visit of timeline){
    const place=local.get(visit.placeId);for(const key of ['distance_m','duration_minutes','elevation_gain_m'])sums[key]=(sums[key]||0)+(Number(visit[key])||0);
    if(!seen.has(place.id)){seen.add(place.id);categories[place.category]=(categories[place.category]||0)+1;if(place.mustSee)mustsee++;if(place.regionCode)regions.add(place.regionCode);for(const id of memberships.get(place.id)||[]){const count=remaining.get(id)-1;remaining.set(id,count);if(count===0)completed++;}}
    for(const f of config.families){let value=0;switch(f.metric){case 'unique':value=f.key==='all'?seen.size:categories[f.key]||0;break;case 'sum':value=(sums[f.key]||0)/(f.key==='distance_m'?1000:f.key==='duration_minutes'?60:1);break;case 'collections':value=completed;break;case 'percent':value=local.size?100*seen.size/local.size:0;break;case 'mustsee':value=mustsee;break;case 'regions':value=regions.size;break;default:continue;}
     f.thresholds.forEach((threshold,tier)=>{const key=`${country}/${f.id}/${tier}`;if(value>=threshold&&!known.has(key)){known.add(key);result.push({country,family:f.id,tier,earnedOn:visit.date,unlockedAt:now});}});
    }
   }
  }
  return result;
 }
};
if(typeof module!=='undefined')module.exports=AchievementEngine;
