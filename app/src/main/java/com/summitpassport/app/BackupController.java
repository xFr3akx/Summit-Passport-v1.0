package com.summitpassport.app;
import android.app.Activity;
import android.content.Intent;
import org.json.*;
import java.io.*;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.function.Consumer;

final class BackupController {
 private final Activity activity;private final PassportDatabase db;private final ExecutorService worker;private final String catalog;private final Consumer<JSONObject> notify;
 private BackupArchive.Loaded pending;private File staging;private String token;private volatile boolean busy;
 BackupController(Activity a,PassportDatabase d,ExecutorService w,String c,Consumer<JSONObject> n){activity=a;db=d;worker=w;catalog=c;notify=n;}
 private void event(String type,String message){try{notify.accept(new JSONObject().put("type",type).put("message",message));}catch(Exception ignored){}}
 void exportFile(){if(busy)return;busy=true;Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/zip");i.putExtra(Intent.EXTRA_TITLE,"Summit_Passport_"+java.time.LocalDate.now()+".zip");try{activity.startActivityForResult(i,92);}catch(Exception e){busy=false;event("error","Nie można otworzyć wyboru pliku.");}}
 void chooseFile(){if(busy)return;busy=true;Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("*/*");try{activity.startActivityForResult(i,93);}catch(Exception e){busy=false;event("error","Nie można otworzyć wyboru pliku.");}}
 void result(int request,int result,Intent data){if(result!=Activity.RESULT_OK||data==null||data.getData()==null){busy=false;event("cancelled","Anulowano wybór pliku.");return;}
  worker.execute(()->{try{
   if(request==92){JSONObject backup=db.backupData();BackupArchive.validate(backup,new JSONObject(catalog));try(OutputStream out=activity.getContentResolver().openOutputStream(data.getData(),"wt")){if(out==null)throw new IOException();BackupArchive.write(out,backup,new File(activity.getFilesDir(),"photos"));}event("exported","Kopia danych została zapisana.");}
   else {clearPending();staging=new File(activity.getCacheDir(),"import-"+UUID.randomUUID());try(InputStream in=activity.getContentResolver().openInputStream(data.getData())){if(in==null)throw new IOException();pending=BackupArchive.read(in,staging);}BackupArchive.validate(pending.data,new JSONObject(catalog));token=UUID.randomUUID().toString();JSONObject preview=db.previewBackup(pending.data).put("type","preview").put("token",token).put("theme",pending.data.getJSONObject("settings").getString("theme")).put("country",pending.data.getJSONObject("settings").getString("country")).put("photos",pending.photos.size());notify.accept(preview);}
  }catch(Exception e){if(request==93)clearPending();event("error",request==92?"Nie udało się zapisać pełnej kopii. Sprawdź wolne miejsce i spróbuj ponownie.":"Plik jest uszkodzony, niezgodny lub przekracza limit kopii. Twoje dane nie zostały zmienione.");}finally{busy=false;}});
 }
 synchronized void confirm(String value){if(busy||pending==null||token==null||!token.equals(value)){event("error","Wybierz ponownie plik kopii.");return;}busy=true;worker.execute(()->{try{db.mergeBackup(pending,new File(activity.getFilesDir(),"photos"));notify.accept(new JSONObject().put("type","imported").put("message","Dane zostały połączone.").put("theme",db.state("theme","dark")));}catch(Exception e){event("error","Nie udało się połączyć danych. Poprzednie dane zostały zachowane.");}finally{clearPending();busy=false;}});}
 private void clearPending(){pending=null;token=null;if(staging!=null){File[] files=staging.listFiles();if(files!=null)for(File f:files)if(f.isFile())f.delete();staging.delete();staging=null;}}
}
