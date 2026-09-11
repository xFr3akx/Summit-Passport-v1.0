package com.summitpassport.app;
import org.json.*;
import java.time.*;
import java.util.*;
/** Portable validation for permanent award records, shared by the bridge and ZIP import. */
public final class AchievementRecords {
 public static void validate(JSONArray records)throws JSONException {
  if(records.length()>264)throw new IllegalArgumentException("Too many awards");
  Set<String> keys=new HashSet<>();List<String> families=Arrays.asList("peak","explorer","distance","vertical","time","castle","cave","waterfall","mustsee","regional","collections","country");
  for(int i=0;i<records.length();i++){JSONObject row=records.getJSONObject(i);String country=row.getString("country"),family=row.getString("family");int tier=row.getInt("tier");
   if(!Arrays.asList("PL","DE").contains(country)||!families.contains(family)||tier<0||tier>10||row.getDouble("tier")!=tier||!keys.add(country+"/"+family+"/"+tier))throw new IllegalArgumentException("Invalid award");
   LocalDate.parse(row.getString("earnedOn"));Instant.parse(row.getString("unlockedAt"));
  }
 }
}
