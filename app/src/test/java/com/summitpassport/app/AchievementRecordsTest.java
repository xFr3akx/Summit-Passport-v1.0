package com.summitpassport.app;
import org.json.*;
import org.junit.Test;
import static org.junit.Assert.*;
public class AchievementRecordsTest {
 private JSONObject row()throws Exception{return new JSONObject().put("country","PL").put("family","peak").put("tier",0).put("earnedOn","2026-09-01").put("unlockedAt","2026-09-11T12:00:00Z");}
 private void reject(JSONArray rows)throws Exception{try{AchievementRecords.validate(rows);fail("Invalid award accepted");}catch(IllegalArgumentException|JSONException|java.time.DateTimeException expected){}}
 @Test public void validatesDatesFamiliesCountriesAndElevenTiers()throws Exception{JSONObject r=row();for(int i=0;i<11;i++){r.put("tier",i);AchievementRecords.validate(new JSONArray().put(r));}r.put("tier",11);reject(new JSONArray().put(r));r.put("tier",0.5);reject(new JSONArray().put(r));r=row().put("country","FR");reject(new JSONArray().put(r));r=row().put("family","invented");reject(new JSONArray().put(r));r=row().put("earnedOn","2026-99-01");reject(new JSONArray().put(r));r=row().put("unlockedAt","bad");reject(new JSONArray().put(r));reject(new JSONArray().put(row()).put(row()));}
}
