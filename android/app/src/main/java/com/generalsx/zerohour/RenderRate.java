package com.generalsx.zerohour;

import android.app.Activity;
import android.content.Context;
import android.os.Build;
import android.util.Log;
import android.view.Display;
import android.view.Surface;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import java.util.ArrayList;
import java.util.List;

// GeneralsX @feature Codex 17/10/2026 Opt-in render cap and same-resolution display request.
final class RenderRate {
    static final int[] VALUES = {0, 30, 60, 90, 120};
    private static final String KEY = "render_fps_experiment";
    static int normalize(int fps) {
        for (int value : VALUES) if (fps == value) return fps;
        return 0;
    }
    static int get(Context context) {
        return normalize(context.getSharedPreferences(SetupActivity.PREFS_NAME, Context.MODE_PRIVATE).getInt(KEY, 0));
    }
    static void set(Context context, int fps) {
        context.getSharedPreferences(SetupActivity.PREFS_NAME, Context.MODE_PRIVATE).edit().putInt(KEY, normalize(fps)).apply();
    }
    static int target(Context context) { return Math.max(get(context), SetupActivity.getSimHz(context)); }
    static void appendArguments(Context context, List<String> args, boolean replay) {
        // Explicit zero also clears an earlier opt-in if SDL restarts in the same process.
        int fps = replay ? 0 : get(context);
        args.add("-gxRenderFps"); args.add(Integer.toString(fps));
    }
    // Pick the lowest available rate satisfying the target, otherwise the highest supported one.
    static float chooseRate(float[] rates, int target) {
        float above = Float.MAX_VALUE, highest = 0;
        for (float rate : rates) {
            if (!Float.isFinite(rate) || rate <= 0) continue;
            highest = Math.max(highest, rate);
            if (rate + 0.5f >= target) above = Math.min(above, rate);
        }
        return above < Float.MAX_VALUE ? above : highest;
    }
    static void applyWindowRequest(Activity activity) {
        if (get(activity) == 0) return;
        try {
            Display display = activity.getWindowManager().getDefaultDisplay();
            Display.Mode current = display.getMode();
            ArrayList<Display.Mode> compatible = new ArrayList<>();
            for (Display.Mode mode : display.getSupportedModes()) {
                if (mode.getPhysicalWidth() == current.getPhysicalWidth()
                    && mode.getPhysicalHeight() == current.getPhysicalHeight()) compatible.add(mode);
            }
            float[] rates = new float[compatible.size()];
            for (int i = 0; i < rates.length; i++) rates[i] = compatible.get(i).getRefreshRate();
            float picked = chooseRate(rates, target(activity));
            WindowManager.LayoutParams attributes = activity.getWindow().getAttributes();
            for (Display.Mode mode : compatible) {
                if (Math.abs(mode.getRefreshRate() - picked) < 0.01f) {
                    attributes.preferredDisplayModeId = mode.getModeId();
                    attributes.preferredRefreshRate = picked;
                    activity.getWindow().setAttributes(attributes);
                    Log.i("GXRenderRate", "Requested FPS=" + get(activity) + " simulation=" + SetupActivity.getSimHz(activity)
                        + " display mode=" + picked + "Hz; actual/OEM policy may differ");
                    break;
                }
            }
        } catch (RuntimeException error) { Log.w("GXRenderRate", "Display request unavailable", error); }
    }
    private static SurfaceView findSurface(View view) {
        if (view instanceof SurfaceView) return (SurfaceView)view;
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup)view;
            for (int i = 0; i < group.getChildCount(); i++) {
                SurfaceView result = findSurface(group.getChildAt(i));
                if (result != null) return result;
            }
        }
        return null;
    }
    private static void applySurfaceRequest(Activity activity, SurfaceHolder holder) {
        if (get(activity) == 0 || Build.VERSION.SDK_INT < 30) return;
        Surface surface = holder.getSurface();
        if (surface == null || !surface.isValid()) return;
        try { surface.setFrameRate(target(activity), Surface.FRAME_RATE_COMPATIBILITY_DEFAULT); }
        catch (RuntimeException error) { Log.w("GXRenderRate", "Surface frame-rate hint unavailable", error); }
    }
    static void installDisplayRequest(Activity activity) {
        if (get(activity) == 0) return;
        applyWindowRequest(activity);
        SurfaceView view = findSurface(activity.getWindow().getDecorView());
        if (view == null) { Log.w("GXRenderRate", "SDL surface not available for frame-rate hint"); return; }
        SurfaceHolder holder = view.getHolder();
        holder.addCallback(new SurfaceHolder.Callback() {
            @Override public void surfaceCreated(SurfaceHolder h) { applySurfaceRequest(activity, h); }
            @Override public void surfaceChanged(SurfaceHolder h, int format, int width, int height) { applySurfaceRequest(activity, h); }
            @Override public void surfaceDestroyed(SurfaceHolder h) {}
        });
        applySurfaceRequest(activity, holder);
    }
    private RenderRate() {}
}
