package com.summitpassport.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.os.Bundle;
import android.content.res.Configuration;
import android.graphics.Color;
import android.view.View;
import android.widget.*;

public final class MainActivity extends Activity {
 private String country;
 private int tab = 0;
 private boolean dark;
 private LinearLayout root;
 private PassportDatabase database;
 @Override public void onCreate(Bundle state) {
  super.onCreate(state);
  database = new PassportDatabase(this);
  database.getWritableDatabase();
  if(state != null) { country=state.getString("country"); tab=state.getInt("tab"); }
  render();
 }
 @Override protected void onSaveInstanceState(Bundle out) { super.onSaveInstanceState(out); out.putString("country",country); out.putInt("tab",tab); }
 @Override protected void onDestroy() { database.close(); super.onDestroy(); }
 private int dp(int n) { return (int)(n*getResources().getDisplayMetrics().density); }
 private TextView text(String value,int size) {
  TextView view=new TextView(this); view.setText(value); view.setTextSize(size); view.setTextColor(Color.parseColor(dark?"#F5F4EA":"#183D32")); view.setPadding(0,dp(12),0,dp(12)); root.addView(view); return view;
 }
 private void button(String value,Runnable action) { Button b=new Button(this); b.setText(value); b.setAllCaps(false); root.addView(b,new LinearLayout.LayoutParams(-1,dp(60))); b.setOnClickListener(v->action.run()); }
 private void render() {
  int mode=getPreferences(MODE_PRIVATE).getInt("theme",0);
  dark=mode==2 || (mode==0 && (getResources().getConfiguration().uiMode & Configuration.UI_MODE_NIGHT_MASK)==Configuration.UI_MODE_NIGHT_YES);
  ScrollView scroll=new ScrollView(this); scroll.setFillViewport(true);
  root=new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL); root.setPadding(dp(24),dp(24),dp(24),dp(24)); root.setBackgroundColor(Color.parseColor(dark?"#102923":"#F7F5ED")); scroll.addView(root); setContentView(scroll);
  scroll.setOnApplyWindowInsetsListener((v,insets)-> { v.setPadding(insets.getSystemWindowInsetLeft(),insets.getSystemWindowInsetTop(),insets.getSystemWindowInsetRight(),insets.getSystemWindowInsetBottom()); return insets; }); scroll.requestApplyInsets();
  text("SUMMIT\nPASSPORT",32);
  if(country==null) {
   text("Wybierz kraj",20);
   countryCard("PL","🇵🇱  Polska"); countryCard("DE","🇩🇪  Niemcy");
   text("Kolejne kraje w przyszłości",14);
  } else {
   button("‹ Wybór kraju",()->{country=null;render();});
   text(country.equals("PL")?"Polska":"Niemcy",24);
   String[] tabs={"Mapa","Kolekcje","Dziennik","Osiągnięcia"};
   for(int i=0;i<tabs.length;i++){ final int next=i; button((tab==i?"●  ":"")+tabs[i],()->{tab=next;render();}); }
   text(tabs[tab],22);
   text(tab==0?"Katalog miejsc oczekuje na import. Mapa pojawi się w kolejnym etapie.":tab==1?"Kolekcje pojawią się po imporcie katalogu.":tab==2?"Nie zapisano jeszcze żadnej wizyty.":"Każda rodzina: 12 poziomów, od Brązu I do Master ★★★.",16);
  }
  button("Ustawienia · motyw",this::settings);
 }
 private void countryCard(String code,String label) {
  button(label,()->{country=code;tab=0;render();});
  text("Brak zaimportowanego katalogu",14);
  ProgressBar bar=new ProgressBar(this,null,android.R.attr.progressBarStyleHorizontal); bar.setMax(100); bar.setProgress(0); bar.setContentDescription("Postęp niedostępny do czasu importu katalogu"); root.addView(bar);
 }
 private void settings() {
  new AlertDialog.Builder(this).setTitle("Motyw").setSingleChoiceItems(new String[]{"System","Light","Dark"},getPreferences(MODE_PRIVATE).getInt("theme",0),(dialog,which)->{getPreferences(MODE_PRIVATE).edit().putInt("theme",which).apply();dialog.dismiss();render();}).setNegativeButton("Zamknij",null).show();
 }
}
