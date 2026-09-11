package com.summitpassport.app;
import org.junit.Test;
import static org.junit.Assert.*;
import org.json.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.zip.*;

public class BackupArchiveTest {
 private JSONObject fixture()throws Exception {return new JSONObject().put("format","summit-passport").put("version",1).put("settings",new JSONObject().put("theme","dark").put("country","PL")).put("plans",new JSONArray()).put("visits",new JSONArray().put(new JSONObject().put("id",UUID.randomUUID().toString()).put("placeId","p1").put("date","2026-09-11").put("weather","Śnieg").put("notes","Zażółć gęślą jaźń").put("trailUrl","https://www.alltrails.com/trail/test").put("rating",5).put("photos",new JSONArray())));}
 private JSONObject catalog()throws Exception{return new JSONObject().put("places",new JSONArray().put(new JSONObject().put("id","p1").put("country","PL").put("mapReady",true)));}
 private interface Run{void run()throws Exception;}
 private void rejects(Run run)throws Exception{try{run.run();fail("Invalid backup accepted");}catch(IOException|JSONException|IllegalArgumentException expected){}}
 @Test public void zipRoundTripIncludesPhotoAndUnicode()throws Exception{
  File dir=Files.createTempDirectory("backup-test").toFile();String photo=UUID.randomUUID()+".jpg";Files.write(new File(dir,photo).toPath(),new byte[]{1,2,3});JSONObject data=fixture();data.getJSONArray("visits").getJSONObject(0).getJSONArray("photos").put(photo);BackupArchive.validate(data,catalog());ByteArrayOutputStream bytes=new ByteArrayOutputStream();BackupArchive.write(bytes,data,dir);BackupArchive.Loaded loaded=BackupArchive.read(new ByteArrayInputStream(bytes.toByteArray()),Files.createTempDirectory("restore-test").toFile());BackupArchive.validate(loaded.data,catalog());assertEquals("Zażółć gęślą jaźń",loaded.data.getJSONArray("visits").getJSONObject(0).getString("notes"));assertEquals(5,loaded.data.getJSONArray("visits").getJSONObject(0).getInt("rating"));assertArrayEquals(new byte[]{1,2,3},Files.readAllBytes(loaded.photos.get(photo).toPath()));
 }
 @Test public void rejectsBadVersionUnknownPlaceAndRating()throws Exception{
  JSONObject d=fixture();d.put("version",99);rejects(()->BackupArchive.validate(d,catalog()));d.put("version",1);JSONObject v=d.getJSONArray("visits").getJSONObject(0);v.put("placeId","unknown");rejects(()->BackupArchive.validate(d,catalog()));v.put("placeId","p1").put("rating",6);rejects(()->BackupArchive.validate(d,catalog()));v.put("rating",2.5);rejects(()->BackupArchive.validate(d,catalog()));
 }
 @Test public void rejectsTraversalAndOversizedEntry()throws Exception{
  ByteArrayOutputStream b=new ByteArrayOutputStream();try(ZipOutputStream z=new ZipOutputStream(b)){z.putNextEntry(new ZipEntry("../escape"));z.write(1);}rejects(()->BackupArchive.read(new ByteArrayInputStream(b.toByteArray()),Files.createTempDirectory("bad").toFile()));
  b.reset();try(ZipOutputStream z=new ZipOutputStream(b)){z.putNextEntry(new ZipEntry("photos/"+UUID.randomUUID()+".jpg"));z.write(new byte[9*1024*1024]);}rejects(()->BackupArchive.read(new ByteArrayInputStream(b.toByteArray()),Files.createTempDirectory("big").toFile()));
 }
 @Test public void rejectsMissingOrCorruptPhoto()throws Exception{
  JSONObject d=fixture();String name=UUID.randomUUID()+".jpg";d.getJSONArray("visits").getJSONObject(0).getJSONArray("photos").put(name);d.put("photoHashes",new JSONObject().put(name,"wrong"));
  ByteArrayOutputStream b=new ByteArrayOutputStream();try(ZipOutputStream z=new ZipOutputStream(b)){z.putNextEntry(new ZipEntry("data.json"));z.write(d.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));z.closeEntry();z.putNextEntry(new ZipEntry("photos/"+name));z.write(1);}rejects(()->BackupArchive.read(new ByteArrayInputStream(b.toByteArray()),Files.createTempDirectory("bad-hash").toFile()));
 }
 @Test public void mergeKeepsExistingIdsAndDoesNotMutateInput()throws Exception {
  JSONArray current=new JSONArray().put(new JSONObject().put("id","same").put("notes","local"));JSONArray incoming=new JSONArray().put(new JSONObject().put("id","same").put("notes","backup")).put(new JSONObject().put("id","new").put("notes","new note"));JSONArray added=BackupArchive.newEntries(current,incoming);assertEquals(1,added.length());assertEquals("new",added.getJSONObject(0).getString("id"));assertEquals("local",current.getJSONObject(0).getString("notes"));added.getJSONObject(0).put("notes","changed");assertEquals("new note",incoming.getJSONObject(1).getString("notes"));assertEquals(0,BackupArchive.newEntries(incoming,incoming).length());
 }
}
