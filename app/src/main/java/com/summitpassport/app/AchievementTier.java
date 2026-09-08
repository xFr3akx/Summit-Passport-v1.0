package com.summitpassport.app;
public enum AchievementTier {
 BRONZE_I, BRONZE_II, SILVER_I, SILVER_II, GOLD_I, GOLD_II, DIAMOND_I, DIAMOND_II, MASTER, MASTER_ONE_STAR, MASTER_TWO_STARS, MASTER_THREE_STARS;
 public int stars() { return Math.max(0, ordinal() - MASTER.ordinal()); }
}
