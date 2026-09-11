package com.summitpassport.app;

import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.security.MessageDigest;
import java.time.LocalDate;
import java.net.URI;
import java.util.*;
import java.util.zip.*;

/** Portable backup format; no Android or user-data mutation in this class. */
public final class BackupArchive {
 public static final long MAX_TOTAL=512L*1024*1024;
 public static final class Loaded {
  public final JSONObject data; public final Map<String,File> photos;
  Loaded(JSONObject data,Map<String,File> photos){this.data=data;this.photos=photos;}
 }
 private static void require(boolean ok)throws IOException {if(!ok)throw new IOException("Nieprawidłowa lub nieobsługiwana kopia danych.");}
 public static String hash(File file)throws Exception {MessageDigest md=MessageDigest.getInstance("SHA-256");try(InputStream in=new FileInputStream(file)){byte[] b=new byte[8192];int n;while((n=in.read(b))!=-1)md.update(b,0,n);}StringBuilder s=new StringBuilder();for(byte b:md.digest())s.append(String.format(java.util.Locale.ROOT,"%02x",b&255));return s.toString();}
 public static void write(OutputStream output,JSONObject input,File photoDir)throws Exception {
  JSONObject data=new JSONObject(input.toString()),hashes=new JSONObject();Set<String> photos=photoNames(data);
  long total=0;for(String name:photos){File file=new File(photoDir,name);require(file.isFile()&&file.length()<=8L*1024*1024);total+=file.length();require(total<=MAX_TOTAL);hashes.put(name,hash(file));}
  data.put("photoHashes",hashes);byte[] manifest=data.toString().getBytes(StandardCharsets.UTF_8);require(manifest.length<=16L*1024*1024&&total+manifest.length<=MAX_TOTAL);
  try(ZipOutputStream zip=new ZipOutputStream(output)){
   zip.putNextEntry(new ZipEntry("data.json"));zip.write(manifest);zip.closeEntry();
   for(String name:photos){zip.putNextEntry(new ZipEntry("photos/"+name));Files.copy(new File(photoDir,name).toPath(),zip);zip.closeEntry();}
  }
 }
 public static Loaded read(InputStream input,File staging)throws Exception {
  require(staging.isDirectory()||staging.mkdirs());Map<String,File> photos=new HashMap<>();Set<String> entries=new HashSet<>();byte[] manifest=null;long total=0;
  try(ZipInputStream zip=new ZipInputStream(input)) {ZipEntry entry;while((entry=zip.getNextEntry())!=null){
   String name=entry.getName();require(entries.add(name)&&entries.size()<=50001&&!entry.isDirectory());
   boolean json=name.equals("data.json");require(json||name.matches("photos/[a-f0-9-]{36}\\.jpg"));
   long limit=json?16L*1024*1024:8L*1024*1024,count=0;ByteArrayOutputStream bytes=json?new ByteArrayOutputStream():null;
   File destination=json?null:new File(staging,name.substring(7));
   try(OutputStream out=json?bytes:new FileOutputStream(destination)){byte[] b=new byte[8192];int n;while((n=zip.read(b))!=-1){count+=n;total+=n;require(count<=limit&&total<=MAX_TOTAL);out.write(b,0,n);}}
   if(json)manifest=bytes.toByteArray();else photos.put(name.substring(7),destination);zip.closeEntry();
  }}
  require(manifest!=null);JSONObject data=new JSONObject(new String(manifest,StandardCharsets.UTF_8));require(data.optString("format").equals("summit-passport")&&(data.optInt("version")==1||data.optInt("version")==2));
  Set<String> expected=photoNames(data);require(expected.equals(photos.keySet()));JSONObject hashes=data.getJSONObject("photoHashes");require(hashes.length()==expected.size());
  for(String name:expected)require(hash(photos.get(name)).equals(hashes.getString(name)));
  return new Loaded(data,photos);
 }
 public static Set<String> photoNames(JSONObject data)throws Exception {
  Set<String> names=new TreeSet<>();JSONArray visits=data.getJSONArray("visits");require(visits.length()<=10000);
  for(int i=0;i<visits.length();i++){JSONArray ps=visits.getJSONObject(i).getJSONArray("photos");require(ps.length()<=10);for(int j=0;j<ps.length();j++){String name=ps.getString(j);require(name.matches("[a-f0-9-]{36}\\.jpg"));names.add(name);}}
  return names;
 }
 public static JSONArray newEntries(JSONArray current,JSONArray incoming)throws JSONException {Set<String> ids=new HashSet<>();for(int i=0;i<current.length();i++)ids.add(current.getJSONObject(i).getString("id"));JSONArray result=new JSONArray();for(int i=0;i<incoming.length();i++){JSONObject row=incoming.getJSONObject(i);if(ids.add(row.getString("id")))result.put(new JSONObject(row.toString()));}return result;}
 public static void validate(JSONObject data,JSONObject catalog)throws Exception {
  require(data.optString("format").equals("summit-passport")&&(data.optInt("version")==1||data.optInt("version")==2));Map<String,String> places=new HashMap<>();JSONArray all=catalog.getJSONArray("places");for(int i=0;i<all.length();i++){JSONObject p=all.getJSONObject(i);if(p.optBoolean("mapReady"))places.put(p.getString("id"),p.getString("country"));}
  JSONArray visits=data.getJSONArray("visits"),plans=data.getJSONArray("plans");require(visits.length()<=10000&&plans.length()<=200);Set<String> ids=new HashSet<>();
  for(int i=0;i<visits.length();i++){JSONObject v=visits.getJSONObject(i);require(v.getString("id").matches("[a-f0-9-]{36}")&&ids.add(v.getString("id"))&&places.containsKey(v.getString("placeId")));LocalDate.parse(v.getString("date"));require(v.getString("notes").length()<=20000&&v.getString("weather").length()<=100);
   for(String key:new String[]{"rating","distance_m","duration_minutes","elevation_gain_m"}){double n=v.optDouble(key,0);require(Double.isFinite(n)&&n>=0&&n==Math.floor(n)&&n<=(key.equals("rating")?5:100000000));}
   String url=v.getString("trailUrl");require(url.length()<=4000);
  }
  if(data.optInt("version")==2)require(data.has("achievements"));if(data.has("achievements"))AchievementRecords.validate(data.getJSONArray("achievements"));
  photoNames(data);ids.clear();
  for(int i=0;i<plans.length();i++){JSONObject p=plans.getJSONObject(i);String id=p.getString("id"),country=p.getString("country");require(id.matches("user-[a-f0-9-]{36}")&&ids.add(id)&&(country.equals("PL")||country.equals("DE"))&&!p.getString("title").trim().isEmpty()&&p.getString("title").length()<=100);JSONArray ps=p.getJSONArray("placeIds");Set<String> unique=new HashSet<>();require(ps.length()>=2&&ps.length()<=100);for(int j=0;j<ps.length();j++){String place=ps.getString(j);require(country.equals(places.get(place))&&unique.add(place));}}
  JSONObject settings=data.getJSONObject("settings");require(!settings.has("language")||Arrays.asList("pl","de","en").contains(settings.getString("language")));require(Arrays.asList("light","dark").contains(settings.getString("theme"))&&Arrays.asList("","PL","DE").contains(settings.getString("country")));
 }
}
