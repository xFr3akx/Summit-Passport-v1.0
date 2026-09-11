package com.summitpassport.app;
import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.content.ContentValues;
import android.database.Cursor;
import org.json.*;

public final class PassportDatabase extends SQLiteOpenHelper {
 public PassportDatabase(Context context) { super(context, "passport.db", null, 5); }
 @Override public void onConfigure(SQLiteDatabase db) { db.setForeignKeyConstraintsEnabled(true); }
 @Override public void onCreate(SQLiteDatabase db) {
  db.execSQL("CREATE TABLE app_state (key TEXT PRIMARY KEY NOT NULL, value TEXT NOT NULL)");
  db.execSQL("CREATE TABLE places (stable_id TEXT PRIMARY KEY NOT NULL, country TEXT NOT NULL CHECK(country IN ('PL','DE')), name TEXT NOT NULL, admin_region_code TEXT NOT NULL, category TEXT NOT NULL, latitude REAL NOT NULL CHECK(latitude BETWEEN -90 AND 90), longitude REAL NOT NULL CHECK(longitude BETWEEN -180 AND 180), must_see INTEGER NOT NULL DEFAULT 0 CHECK(must_see IN (0,1)))");
  db.execSQL("CREATE TABLE visits (id TEXT PRIMARY KEY NOT NULL, place_id TEXT NOT NULL REFERENCES places(stable_id), visited_on TEXT NOT NULL, distance_m INTEGER NOT NULL DEFAULT 0 CHECK(distance_m >= 0), duration_minutes INTEGER NOT NULL DEFAULT 0 CHECK(duration_minutes >= 0), elevation_gain_m INTEGER NOT NULL DEFAULT 0 CHECK(elevation_gain_m >= 0), notes TEXT NOT NULL DEFAULT '', weather TEXT NOT NULL DEFAULT '', trail_url TEXT NOT NULL DEFAULT '', photos TEXT NOT NULL DEFAULT '[]', rating INTEGER NOT NULL DEFAULT 0 CHECK(rating BETWEEN 0 AND 5))");
  db.execSQL("CREATE INDEX visits_place ON visits(place_id)");
  db.execSQL("CREATE TABLE achievement_unlocks (country TEXT NOT NULL CHECK(country IN ('PL','DE')), family TEXT NOT NULL, tier INTEGER NOT NULL CHECK(tier BETWEEN 0 AND 11), unlocked_at TEXT NOT NULL, earned_on TEXT NOT NULL, PRIMARY KEY(country, family, tier))");
 }
 @Override public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
  if(oldVersion<5){db.execSQL("ALTER TABLE achievement_unlocks ADD COLUMN earned_on TEXT NOT NULL DEFAULT ''");db.execSQL("UPDATE achievement_unlocks SET earned_on=substr(unlocked_at,1,10) WHERE earned_on=''");}
  if(oldVersion<2){db.execSQL("ALTER TABLE visits ADD COLUMN weather TEXT NOT NULL DEFAULT ''");db.execSQL("ALTER TABLE visits ADD COLUMN trail_url TEXT NOT NULL DEFAULT ''");db.execSQL("ALTER TABLE visits ADD COLUMN photos TEXT NOT NULL DEFAULT '[]'");}
  if(oldVersion<4)db.execSQL("CREATE TABLE app_state (key TEXT PRIMARY KEY NOT NULL, value TEXT NOT NULL)");
  if(oldVersion<3)db.execSQL("ALTER TABLE visits ADD COLUMN rating INTEGER NOT NULL DEFAULT 0 CHECK(rating BETWEEN 0 AND 5)");
 }
 public synchronized String state(String key,String fallback){try(Cursor c=getReadableDatabase().rawQuery("SELECT value FROM app_state WHERE key=?",new String[]{key})){return c.moveToFirst()?c.getString(0):fallback;}}
 public synchronized void setState(String key,String value){ContentValues v=new ContentValues();v.put("key",key);v.put("value",value);getWritableDatabase().execSQL("INSERT OR REPLACE INTO app_state (key,value) VALUES (?,?)",new Object[]{key,value});}
 public synchronized void initState(android.content.SharedPreferences legacy){for(String key:new String[]{"plans","country"}){String fallback=key.equals("plans")?"[]":"";if(state(key,null)==null)setState(key,legacy.getString(key,fallback));}}
 public synchronized JSONObject backupData()throws JSONException {return new JSONObject().put("format","summit-passport").put("version",2).put("achievements",awards()).put("createdAt",java.time.Instant.now().toString()).put("visits",visitList()).put("plans",new JSONArray(state("plans","[]"))).put("settings",new JSONObject().put("theme",state("theme","dark")).put("country",state("country","")).put("language",state("language","pl")));}
 public synchronized JSONObject previewBackup(JSONObject incoming)throws JSONException {
  java.util.HashSet<String> existing=new java.util.HashSet<>();JSONArray current=visitList();for(int i=0;i<current.length();i++)existing.add(current.getJSONObject(i).getString("id"));int newVisits=0;JSONArray ins=incoming.getJSONArray("visits");for(int i=0;i<ins.length();i++)if(!existing.contains(ins.getJSONObject(i).getString("id")))newVisits++;
  existing.clear();JSONArray plans=new JSONArray(state("plans","[]"));for(int i=0;i<plans.length();i++)existing.add(plans.getJSONObject(i).getString("id"));int newPlans=0;JSONArray ips=incoming.getJSONArray("plans");for(int i=0;i<ips.length();i++)if(!existing.contains(ips.getJSONObject(i).getString("id")))newPlans++;
  return new JSONObject().put("awards",incoming.optJSONArray("achievements")==null?0:incoming.getJSONArray("achievements").length()).put("newVisits",newVisits).put("skippedVisits",ins.length()-newVisits).put("newPlans",newPlans).put("skippedPlans",ips.length()-newPlans);
 }
 public synchronized void mergeBackup(BackupArchive.Loaded loaded,java.io.File photoDir)throws Exception {
  JSONObject data=loaded.data;SQLiteDatabase db=getWritableDatabase();java.util.ArrayList<java.io.File> created=new java.util.ArrayList<>();boolean committed=false;db.beginTransaction();
  try{java.util.HashSet<String> ids=new java.util.HashSet<>();JSONArray old=visitList();for(int i=0;i<old.length();i++)ids.add(old.getJSONObject(i).getString("id"));JSONArray incoming=BackupArchive.newEntries(old,data.getJSONArray("visits"));java.util.HashMap<String,String> remapped=new java.util.HashMap<>();photoDir.mkdirs();
   for(int i=0;i<incoming.length();i++){JSONObject v=new JSONObject(incoming.getJSONObject(i).toString());if(ids.contains(v.getString("id")))continue;JSONArray photos=v.getJSONArray("photos"),mapped=new JSONArray();for(int k=0;k<photos.length();k++){String original=photos.getString(k);String name=remapped.get(original);if(name==null){name=java.util.UUID.randomUUID()+".jpg";java.io.File dest=new java.io.File(photoDir,name);created.add(dest);java.nio.file.Files.copy(loaded.photos.get(original).toPath(),dest.toPath());remapped.put(original,name);}mapped.put(name);}v.put("photos",mapped);saveVisit(v);}
   JSONArray plans=new JSONArray(state("plans","[]"));ids.clear();for(int i=0;i<plans.length();i++)ids.add(plans.getJSONObject(i).getString("id"));JSONArray incomingPlans=BackupArchive.newEntries(plans,data.getJSONArray("plans"));for(int i=0;i<incomingPlans.length();i++){JSONObject p=incomingPlans.getJSONObject(i);if(!ids.contains(p.getString("id")))plans.put(p);}if(plans.length()>200)throw new IllegalArgumentException("Zbyt wiele list po połączeniu.");setState("plans",plans.toString());if(data.has("achievements"))mergeAwards(data.getJSONArray("achievements"));JSONObject settings=data.getJSONObject("settings");setState("country",settings.getString("country"));setState("theme",settings.getString("theme"));if(settings.has("language"))setState("language",settings.getString("language"));db.setTransactionSuccessful();committed=true;
  }finally{try{db.endTransaction();}catch(Exception e){committed=false;throw e;}finally{if(!committed)for(java.io.File file:created)file.delete();}}
 }
 public synchronized JSONArray awards()throws JSONException {JSONArray result=new JSONArray();try(Cursor c=getReadableDatabase().rawQuery("SELECT country,family,tier,unlocked_at,earned_on FROM achievement_unlocks ORDER BY country,family,tier",null)){while(c.moveToNext())result.put(new JSONObject().put("country",c.getString(0)).put("family",c.getString(1)).put("tier",c.getInt(2)).put("unlockedAt",c.getString(3)).put("earnedOn",c.getString(4)));}return result;}
 public synchronized JSONArray mergeAwards(JSONArray incoming)throws JSONException {AchievementRecords.validate(incoming);SQLiteDatabase db=getWritableDatabase();db.beginTransaction();try{for(int i=0;i<incoming.length();i++){JSONObject row=incoming.getJSONObject(i);ContentValues values=new ContentValues();values.put("country",row.getString("country"));values.put("family",row.getString("family"));values.put("tier",row.getInt("tier"));values.put("unlocked_at",row.getString("unlockedAt"));values.put("earned_on",row.getString("earnedOn"));db.insertWithOnConflict("achievement_unlocks",null,values,SQLiteDatabase.CONFLICT_IGNORE);}db.setTransactionSuccessful();}finally{db.endTransaction();}return awards();}
 public synchronized JSONObject saveVisit(JSONObject v)throws Exception {
  int rating=v.optInt("rating",0);if(rating<0||rating>5||v.optDouble("rating",0)!=rating)throw new IllegalArgumentException("Ocena musi być od 0 do 5.");
  String date=v.getString("date");java.time.LocalDate.parse(date);
  String link=v.optString("trailUrl");if(!link.isEmpty()){android.net.Uri u=android.net.Uri.parse(link);String host=u.getHost();if(!"https".equals(u.getScheme())||host==null||!(host.equals("alltrails.com")||host.endsWith(".alltrails.com")))throw new IllegalArgumentException("Podaj link HTTPS do AllTrails.");}
  String id=v.optString("id");if(id.isEmpty())id=java.util.UUID.randomUUID().toString();
  ContentValues values=new ContentValues();values.put("id",id);values.put("place_id",v.getString("placeId"));values.put("visited_on",date);values.put("weather",v.optString("weather"));values.put("trail_url",link);values.put("notes",v.optString("notes"));values.put("rating",rating);
  for(String key:new String[]{"distance_m","duration_minutes","elevation_gain_m"}){int n=v.optInt(key,0);if(n<0)throw new IllegalArgumentException("Wartości nie mogą być ujemne.");values.put(key,n);}
  JSONArray photos=v.optJSONArray("photos");if(photos==null)photos=new JSONArray();if(photos.length()>10)throw new IllegalArgumentException("Maksymalnie 10 zdjęć.");for(int i=0;i<photos.length();i++)if(!photos.getString(i).matches("[a-f0-9-]{36}\\.jpg"))throw new IllegalArgumentException("Nieprawidłowe zdjęcie.");values.put("photos",photos.toString());
  SQLiteDatabase db=getWritableDatabase();if(db.update("visits",values,"id=? AND place_id=?",new String[]{id,v.getString("placeId")})==0)db.insertOrThrow("visits",null,values);v.put("id",id);return v;
 }
 public synchronized JSONArray deleteVisit(String id)throws JSONException {
  SQLiteDatabase db=getWritableDatabase();JSONArray removedPhotos=new JSONArray();
  try(Cursor c=db.rawQuery("SELECT photos FROM visits WHERE id=?",new String[]{id})){if(c.moveToFirst())removedPhotos=new JSONArray(c.getString(0));}
  db.delete("visits","id=?",new String[]{id});
  java.util.HashSet<String> used=new java.util.HashSet<>();try(Cursor c=db.rawQuery("SELECT photos FROM visits",null)){while(c.moveToNext()){JSONArray photos=new JSONArray(c.getString(0));for(int i=0;i<photos.length();i++)used.add(photos.getString(i));}}
  JSONArray unused=new JSONArray();for(int i=0;i<removedPhotos.length();i++)if(!used.contains(removedPhotos.getString(i)))unused.put(removedPhotos.getString(i));return unused;
 }
 public synchronized JSONArray visitList()throws JSONException {
  JSONArray result=new JSONArray();try(Cursor c=getReadableDatabase().rawQuery("SELECT id,place_id,visited_on,weather,trail_url,notes,distance_m,duration_minutes,elevation_gain_m,photos,rating FROM visits ORDER BY visited_on DESC,id DESC",null)){
   while(c.moveToNext())result.put(new JSONObject().put("id",c.getString(0)).put("placeId",c.getString(1)).put("date",c.getString(2)).put("weather",c.getString(3)).put("trailUrl",c.getString(4)).put("notes",c.getString(5)).put("distance_m",c.getInt(6)).put("duration_minutes",c.getInt(7)).put("elevation_gain_m",c.getInt(8)).put("photos",new JSONArray(c.getString(9))).put("rating",c.getInt(10)));
  }return result;
 }
 public void importCatalog(JSONObject catalog)throws JSONException {
  SQLiteDatabase db=getWritableDatabase();db.beginTransaction();
  try {JSONArray places=catalog.getJSONArray("places");
   for(int i=0;i<places.length();i++){JSONObject p=places.getJSONObject(i);if(!p.getBoolean("mapReady"))continue;
    ContentValues v=new ContentValues();v.put("stable_id",p.getString("id"));v.put("country",p.getString("country"));v.put("name",p.getString("name"));v.put("category",p.getString("category"));v.put("latitude",p.getDouble("lat"));v.put("longitude",p.getDouble("lon"));v.put("admin_region_code",p.optString("regionCode",""));v.put("must_see",p.optBoolean("mustSee")?1:0);
    // Never REPLACE a catalog row: existing visit foreign keys must survive refresh.
    if(db.update("places",v,"stable_id=?",new String[]{p.getString("id")})==0)db.insertOrThrow("places",null,v);
   }db.setTransactionSuccessful();
  }finally{db.endTransaction();}
 }
 public synchronized JSONObject snapshot(JSONObject catalog)throws JSONException {
  JSONArray visited=new JSONArray();
  try(Cursor c=getReadableDatabase().rawQuery("SELECT DISTINCT place_id FROM visits",null)){while(c.moveToNext())visited.put(c.getString(0));}
  catalog.put("visits",visitList());catalog.put("visited",visited);return catalog;
 }
}
