package com.generalsx.zerohour;

import android.content.Context;
import android.util.AtomicFile;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Properties;

// GeneralsX @feature Codex 16/10/2026 Atomic launcher/native contract, separate from game Options.
final class TabletControlPreferences {
    static final String FILE = "tablet_controls.ini";
    private final AtomicFile file;
    private final Map<String,Integer> values = new LinkedHashMap<>();
    TabletControlPreferences(Context context) {
        file = new AtomicFile(new File(context.getFilesDir(), FILE));
        Properties loaded = new Properties();
        if (file.getBaseFile().exists()) {
            try (InputStream input = file.openRead()) { loaded.load(input); }
            catch (IOException | IllegalArgumentException e) { android.util.Log.w("GXControls", "Unreadable preferences; using defaults", e); }
        }
        field(loaded,"diagnostics",0,0,1); field(loaded,"attackMove",1,0,1);
        field(loaded,"panelScale",100,75,150); field(loaded,"panelWidth",100,80,180);
        field(loaded,"panelOpacity",100,25,100); field(loaded,"panelLeft",0,0,100);
        field(loaded,"panelBottom",0,0,100); field(loaded,"panelMask",31,0,31);
        field(loaded,"panelCollapsed",0,0,1); field(loaded,"fitLabels",1,0,1);
        field(loaded,"cursorPercent",200,100,250); field(loaded,"cursorOutline",0,0,1);
    }
    private void field(Properties loaded,String key,int fallback,int min,int max) {
        int value=fallback;
        try { value=Integer.parseInt(loaded.getProperty(key,Integer.toString(fallback)).trim()); }
        catch (NumberFormatException ignored) { value=fallback; }
        values.put(key,Math.max(min,Math.min(max,value)));
    }
    int get(String key) { return values.get(key); }
    void set(String key,int value) throws IOException { values.put(key,value); save(); }
    void reset() throws IOException {
        values.put("diagnostics",0); values.put("attackMove",1);
        values.put("panelScale",100);values.put("panelWidth",100);values.put("panelOpacity",100);
        values.put("panelLeft",0);values.put("panelBottom",0);values.put("panelMask",31);
        values.put("panelCollapsed",0);values.put("fitLabels",1);
        values.put("cursorPercent",200);values.put("cursorOutline",0);save();
    }
    private void save() throws IOException {
        StringBuilder text=new StringBuilder();
        for (Map.Entry<String,Integer> item:values.entrySet()) text.append(item.getKey()).append('=').append(item.getValue()).append('\n');
        FileOutputStream output=null;
        try {
            output=file.startWrite();output.write(text.toString().getBytes(StandardCharsets.US_ASCII));file.finishWrite(output);
        } catch (IOException e) { if (output!=null) file.failWrite(output); throw e; }
    }
}
