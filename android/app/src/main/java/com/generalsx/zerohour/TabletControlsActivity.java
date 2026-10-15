package com.generalsx.zerohour;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.os.Bundle;
import android.widget.*;
import java.io.File;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.charset.StandardCharsets;

// GeneralsX @feature Codex 16/10/2026 Accessible persistent settings for physical tablet controls.
public final class TabletControlsActivity extends Activity {
    private TabletControlPreferences prefs;
    @Override protected void attachBaseContext(Context base) {
        super.attachBaseContext(ThemeHelper.wrap(LocaleHelper.wrap(base)));
    }
    @Override public void onCreate(Bundle saved) {
        ThemeHelper.apply(this);super.onCreate(saved);prefs=new TabletControlPreferences(this);build();
    }
    private void store(String key,int value) {
        try { prefs.set(key,value); }
        catch (IOException e) {
            Toast.makeText(this,R.string.tablet_save_error,Toast.LENGTH_LONG).show();
            android.util.Log.w("GXControls","Could not save controls",e);
        }
    }
    private LinearLayout section(LinearLayout root,int title) {
        LinearLayout card=UiKit.card(root);
        UiKit.sectionHeader(card,R.drawable.ic_gzh_sliders,getString(title),false);return card;
    }
    private void toggle(LinearLayout root,int title,int description,String key) {
        com.google.android.material.materialswitch.MaterialSwitch control=UiKit.switchRow(root,getString(title),getString(description));
        control.setChecked(prefs.get(key)!=0);
        control.setOnCheckedChangeListener((button,checked)->store(key,checked?1:0));
    }
    private void slider(LinearLayout root,int title,String key,int low,int high,int step,String unit) {
        TextView label=UiKit.body(root,"");
        SeekBar slider=new SeekBar(this);slider.setMax((high-low)/step);
        int initial=Math.max(0,Math.min(slider.getMax(),Math.round((prefs.get(key)-low)/(float)step)));
        slider.setProgress(initial);label.setText(getString(title)+": "+(low+initial*step)+unit);
        slider.setContentDescription(getString(title));
        slider.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            public void onProgressChanged(SeekBar bar,int value,boolean user) {
                label.setText(getString(title)+": "+(low+value*step)+unit);
                if (user) store(key,low+value*step);
            }
            public void onStartTrackingTouch(SeekBar bar) {}
            public void onStopTrackingTouch(SeekBar bar) {}
        });
        root.addView(slider,new LinearLayout.LayoutParams(-1,-2));
    }
    private void build() {
        ScrollView scroll=new ScrollView(this);
        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);
        int pad=(int)(16*getResources().getDisplayMetrics().density);root.setPadding(pad,pad,pad,pad);
        root.setBackgroundColor(LauncherUi.background(this));scroll.addView(root);setContentView(scroll);
        UiKit.body(root,getString(R.string.tablet_controls_title));
        UiKit.helpText(root,getString(R.string.tablet_restart_hint));
        LinearLayout orders=section(root,R.string.tablet_orders);
        toggle(orders,R.string.tablet_attack_move,R.string.tablet_attack_move_desc,"attackMove");
        toggle(orders,R.string.tablet_diagnostics,R.string.tablet_diagnostics_desc,"diagnostics");
        UiKit.button(orders,UiKit.BTN_TONAL,0,getString(R.string.tablet_open_log),this::showLog);
        LinearLayout panel=section(root,R.string.tablet_army_panel);
        slider(panel,R.string.tablet_scale,"panelScale",75,150,5,"%");
        slider(panel,R.string.tablet_width,"panelWidth",80,180,5,"%");
        slider(panel,R.string.tablet_opacity,"panelOpacity",25,100,5,"%");
        slider(panel,R.string.tablet_left,"panelLeft",0,100,5,"%");
        slider(panel,R.string.tablet_bottom,"panelBottom",0,100,5,"%");
        toggle(panel,R.string.tablet_collapsed,R.string.tablet_collapsed_desc,"panelCollapsed");
        toggle(panel,R.string.tablet_fit_labels,R.string.tablet_fit_labels_desc,"fitLabels");
        int[] names={R.string.tablet_army_screen,R.string.tablet_army_map,R.string.tablet_planes,R.string.tablet_helicopters,R.string.tablet_ground};
        for(int i=0;i<names.length;i++) {
            final int bit=1<<i;
            com.google.android.material.materialswitch.MaterialSwitch button=UiKit.switchRow(panel,getString(names[i]),null);
            button.setChecked((prefs.get("panelMask")&bit)!=0);
            button.setOnCheckedChangeListener((v,on)->store("panelMask",on?prefs.get("panelMask")|bit:prefs.get("panelMask")&~bit));
        }
        LinearLayout cursor=section(root,R.string.tablet_physical_cursor);
        slider(cursor,R.string.tablet_cursor_size,"cursorPercent",100,250,25,"%");
        toggle(cursor,R.string.tablet_cursor_outline,R.string.tablet_cursor_outline_desc,"cursorOutline");
        UiKit.button(root,UiKit.BTN_TONAL,0,getString(R.string.tablet_defaults),()->{
            try { prefs.reset();build(); }
            catch(IOException e) { Toast.makeText(this,R.string.tablet_save_error,Toast.LENGTH_LONG).show(); }
        });
        UiKit.button(root,UiKit.BTN_TONAL,0,getString(R.string.tablet_back),this::finish);
        ThemeHelper.applyBars(this);
    }
    private void showLog() {
        File dir=getFilesDir();
        File log=dir==null?null:new File(dir,"gx_input_trace.log");
        String text=getString(R.string.tablet_no_log);
        if(log!=null && log.isFile()) {
            try(RandomAccessFile file=new RandomAccessFile(log,"r")) {
                long start=Math.max(0,file.length()-64*1024);file.seek(start);
                if(start>0)file.readLine();
                byte[] tail=new byte[(int)(file.length()-file.getFilePointer())];file.readFully(tail);
                text=new String(tail,StandardCharsets.UTF_8);
            } catch(IOException e) { text=getString(R.string.tablet_log_error); }
        }
        TextView body=new TextView(this);body.setText(text);body.setTextIsSelectable(true);
        body.setTextSize(12);body.setPadding(16,16,16,16);
        ScrollView view=new ScrollView(this);view.addView(body);
        new AlertDialog.Builder(this).setTitle(R.string.tablet_open_log).setView(view).setPositiveButton(android.R.string.ok,null).show();
    }
}
