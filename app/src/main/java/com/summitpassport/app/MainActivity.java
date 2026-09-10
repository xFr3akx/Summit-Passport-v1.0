package com.summitpassport.app;
import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.*;
import android.widget.TextView;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public final class MainActivity extends Activity {
 private static final String ORIGIN="https://appassets.androidplatform.net";
 private WebView web;
 private PassportDatabase database;
 private final ExecutorService worker=Executors.newSingleThreadExecutor();
 private volatile String snapshot="{}";
 @Override public void onCreate(Bundle state) {
  super.onCreate(state); database=new PassportDatabase(this);
  TextView loading=new TextView(this);loading.setText("Summit Passport · przygotowanie mapy…");loading.setPadding(24,64,24,24);setContentView(loading);
  worker.execute(()->{try {
   JSONObject catalog=new JSONObject(readAsset("ui/catalog.json"));database.importCatalog(catalog);snapshot=database.snapshot(catalog).toString();
   runOnUiThread(()->{if(!isFinishing()&&!isDestroyed())showApp();});
  }catch(Exception e){runOnUiThread(()->loading.setText("Nie udało się otworzyć katalogu. Uruchom aplikację ponownie."));}});
 }
 private String readAsset(String path)throws IOException {try(InputStream in=getAssets().open(path);ByteArrayOutputStream out=new ByteArrayOutputStream()){byte[] b=new byte[8192];int n;while((n=in.read(b))!=-1)out.write(b,0,n);return out.toString(StandardCharsets.UTF_8.name());}}
 @android.annotation.SuppressLint("SetJavaScriptEnabled")
 private void showApp(){
  web=new WebView(this);setContentView(web);
  web.setOnApplyWindowInsetsListener((v,i)->{v.setPadding(i.getSystemWindowInsetLeft(),i.getSystemWindowInsetTop(),i.getSystemWindowInsetRight(),i.getSystemWindowInsetBottom());return i;});web.requestApplyInsets();
  WebSettings s=web.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);s.setAllowFileAccess(false);s.setAllowContentAccess(false);s.setGeolocationEnabled(false);s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
  s.setUserAgentString(s.getUserAgentString()+" SummitPassport/0.3 (https://github.com/xFr3akx/Summit-Passport-v1.0)");
  web.addJavascriptInterface(new Bridge(),"Passport");
  web.setWebViewClient(new WebViewClient(){
   @Override public WebResourceResponse shouldInterceptRequest(WebView view,WebResourceRequest request){
    Uri u=request.getUrl();if(!"appassets.androidplatform.net".equals(u.getHost()))return null;String p=u.getPath();
    if(p==null||!p.startsWith("/ui/")||p.contains(".."))return new WebResourceResponse("text/plain","UTF-8",new ByteArrayInputStream(new byte[0]));
    try{String mime=p.endsWith(".js")?"text/javascript":p.endsWith(".css")?"text/css":p.endsWith(".json")?"application/json":p.endsWith(".png")?"image/png":p.endsWith(".svg")?"image/svg+xml":"text/html";return new WebResourceResponse(mime,"UTF-8",getAssets().open(p.substring(1)));}
    catch(IOException e){return new WebResourceResponse("text/plain","UTF-8",404,"Not Found",null,new ByteArrayInputStream(new byte[0]));}
   }
   @Override public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest request){
    Uri u=request.getUrl();if(ORIGIN.equals(u.getScheme()+"://"+u.getHost())&&"/ui/index.html".equals(u.getPath()))return false;
    if(request.isForMainFrame()&&"https".equals(u.getScheme())){try{startActivity(new Intent(Intent.ACTION_VIEW,u));}catch(android.content.ActivityNotFoundException ignored){}}return true;
   }
  });web.loadUrl(ORIGIN+"/ui/index.html");
 }
 public final class Bridge {
  @JavascriptInterface public String getSnapshot(){return snapshot;}
  @JavascriptInterface public String getCountry(){return getPreferences(MODE_PRIVATE).getString("country","");}
  @JavascriptInterface public void setCountry(String value){if("PL".equals(value)||"DE".equals(value)||"".equals(value))getPreferences(MODE_PRIVATE).edit().putString("country",value).apply();}
  @JavascriptInterface public void setTheme(String value){if(!"light".equals(value)&&!"dark".equals(value))return;runOnUiThread(()->{
   boolean dark="dark".equals(value);int color=android.graphics.Color.parseColor(dark?"#0c1c21":"#f6f4ed");
   getWindow().setStatusBarColor(color);getWindow().setNavigationBarColor(color);if(web!=null)web.setBackgroundColor(color);
   getWindow().getDecorView().setSystemUiVisibility(dark?0:android.view.View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR|android.view.View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
  });}
 }
 @Override public void onBackPressed(){if(web!=null)web.evaluateJavascript("window.handleBack && window.handleBack()",value->{if(!"true".equals(value))finish();});else super.onBackPressed();}
 @Override protected void onDestroy(){if(web!=null){web.removeJavascriptInterface("Passport");web.destroy();}worker.execute(()->database.close());worker.shutdown();super.onDestroy();}
}
