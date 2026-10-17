package com.generalsx.zerohour;

import android.content.Context;
import java.util.ArrayList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.RuntimeEnvironment;
import org.robolectric.annotation.Config;
import static org.junit.Assert.*;

// GeneralsX @test Codex 17/10/2026 Rendering preferences never choose a simulation library.
@RunWith(RobolectricTestRunner.class) @Config(sdk = 35)
public class RenderRateTest {
    @Test public void defaultAndInvalidValuesRestoreLegacyAndDoNotChangeSimulation() {
        Context c = RuntimeEnvironment.getApplication(); RenderRate.set(c, 0); SetupActivity.setSimHz(c, 30);
        assertEquals(0, RenderRate.get(c));
        for (int fps : new int[]{30, 60, 90, 120}) {
            RenderRate.set(c, fps); assertEquals(fps, RenderRate.get(c)); assertEquals(30, SetupActivity.getSimHz(c));
        }
        RenderRate.set(c, 144); assertEquals(0, RenderRate.get(c));
        SetupActivity.setSimHz(c, 60); RenderRate.set(c, 30); assertEquals(60, RenderRate.target(c));
        RenderRate.set(c, 0);
    }
    @Test public void launchArgumentIsOptInAndReplayUsesLegacyTiming() {
        Context c = RuntimeEnvironment.getApplication(); ArrayList<String> args = new ArrayList<>();
        RenderRate.set(c, 0); RenderRate.appendArguments(c, args, false); assertEquals(java.util.Arrays.asList("-gxRenderFps", "0"), args); args.clear();
        RenderRate.set(c, 120); RenderRate.appendArguments(c, args, true); assertEquals(java.util.Arrays.asList("-gxRenderFps", "0"), args); args.clear();
        RenderRate.appendArguments(c, args, false); assertEquals(java.util.Arrays.asList("-gxRenderFps", "120"), args);
        RenderRate.set(c, 0);
    }
    @Test public void displayRequestHandlesUnsupportedRatesWithoutInventingModes() {
        assertEquals(120f, RenderRate.chooseRate(new float[]{60, 144, 120, 90}, 120), 0.01f);
        assertEquals(60f, RenderRate.chooseRate(new float[]{60}, 120), 0.01f);
        assertEquals(90f, RenderRate.chooseRate(new float[]{60, 90}, 90), 0.01f);
        assertEquals(144f, RenderRate.chooseRate(new float[]{60, 144}, 120), 0.01f);
        assertEquals(0f, RenderRate.chooseRate(new float[]{Float.NaN, 0}, 120), 0.01f);
    }
}
