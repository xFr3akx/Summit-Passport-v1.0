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
   default:return null;
  }
 },
 tier(value,thresholds){if(value===null)return -1;let tier=-1;thresholds.forEach((n,i)=>{if(value>=n)tier=i;});return tier;}
};
if(typeof module!=='undefined')module.exports=AchievementEngine;
