package com.generalsx.zerohour;

import android.content.Context;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.Robolectric;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.RuntimeEnvironment;
import org.robolectric.annotation.Config;
import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import static org.junit.Assert.*;

// GeneralsX @feature Codex 16/10/2026 Exercise persisted controls and real activity creation.
@RunWith(RobolectricTestRunner.class)
@Config(sdk=35)
public class TabletControlsTest {
    @Test public void preferencesSurviveRestartAndRejectMalformedValues() throws Exception {
        Context context=RuntimeEnvironment.getApplication();
        File path=new File(context.getFilesDir(),TabletControlPreferences.FILE);
        Files.write(path.toPath(),"cursorPercent=999\npanelScale=bad\nattackMove=0\npanelMask=-1\nunknown=55\n".getBytes(StandardCharsets.US_ASCII));
        TabletControlPreferences prefs=new TabletControlPreferences(context);
        assertEquals(250,prefs.get("cursorPercent"));assertEquals(100,prefs.get("panelScale"));
        assertEquals(0,prefs.get("panelMask"));assertEquals(0,prefs.get("attackMove"));
        prefs.set("diagnostics",1);prefs.set("cursorPercent",175);
        TabletControlPreferences reopened=new TabletControlPreferences(context);
        assertEquals(1,reopened.get("diagnostics"));assertEquals(175,reopened.get("cursorPercent"));
        reopened.reset();TabletControlPreferences defaults=new TabletControlPreferences(context);
        assertEquals(0,defaults.get("diagnostics"));assertEquals(1,defaults.get("attackMove"));
        assertEquals(200,defaults.get("cursorPercent"));assertEquals(31,defaults.get("panelMask"));
    }
    @Test public void activityRestoresWithoutStartingNativeEngine() {
        TabletControlsActivity activity=Robolectric.buildActivity(TabletControlsActivity.class).setup().get();
        assertNotNull(activity.findViewById(android.R.id.content));
        assertFalse(activity.isFinishing());
    }
}
