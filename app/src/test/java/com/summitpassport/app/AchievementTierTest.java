package com.summitpassport.app;
import org.junit.Test;
import static org.junit.Assert.*;
public class AchievementTierTest {
 @Test public void elevenTiersEndWithThreeStars() { assertEquals(11,AchievementTier.values().length); assertEquals(0,AchievementTier.DIAMOND_II.stars()); assertEquals(1,AchievementTier.MASTER_ONE_STAR.stars()); assertEquals(2,AchievementTier.MASTER_TWO_STARS.stars()); assertEquals(3,AchievementTier.MASTER_THREE_STARS.stars()); }
}
