package com.summitpassport.app;
import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

public final class PassportDatabase extends SQLiteOpenHelper {
 public PassportDatabase(Context context) { super(context, "passport.db", null, 1); }
 @Override public void onConfigure(SQLiteDatabase db) { db.setForeignKeyConstraintsEnabled(true); }
 @Override public void onCreate(SQLiteDatabase db) {
  db.execSQL("CREATE TABLE places (stable_id TEXT PRIMARY KEY NOT NULL, country TEXT NOT NULL CHECK(country IN ('PL','DE')), name TEXT NOT NULL, admin_region_code TEXT NOT NULL, category TEXT NOT NULL, latitude REAL NOT NULL CHECK(latitude BETWEEN -90 AND 90), longitude REAL NOT NULL CHECK(longitude BETWEEN -180 AND 180), must_see INTEGER NOT NULL DEFAULT 0 CHECK(must_see IN (0,1)))");
  db.execSQL("CREATE TABLE visits (id TEXT PRIMARY KEY NOT NULL, place_id TEXT NOT NULL REFERENCES places(stable_id), visited_on TEXT NOT NULL, distance_m INTEGER NOT NULL DEFAULT 0 CHECK(distance_m >= 0), duration_minutes INTEGER NOT NULL DEFAULT 0 CHECK(duration_minutes >= 0), elevation_gain_m INTEGER NOT NULL DEFAULT 0 CHECK(elevation_gain_m >= 0), notes TEXT NOT NULL DEFAULT '')");
  db.execSQL("CREATE INDEX visits_place ON visits(place_id)");
  db.execSQL("CREATE TABLE achievement_unlocks (country TEXT NOT NULL CHECK(country IN ('PL','DE')), family TEXT NOT NULL, tier INTEGER NOT NULL CHECK(tier BETWEEN 0 AND 11), unlocked_at TEXT NOT NULL, PRIMARY KEY(country, family, tier))");
 }
 @Override public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) { throw new IllegalStateException("Explicit migration required"); }
}
