package com.generalsx.zerohour;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.provider.Settings;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import androidx.core.content.FileProvider;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Arrays;

// GeneralsX @feature Codex 16/10/2026 Owner-scoped full APK updates; no native hot swap.
final class ApkUpdates {
    static final String REPOSITORY = "realkot/GeneralsX";
    static final String API = "https://api.github.com/repos/" + REPOSITORY + "/releases?per_page=100";
    static final long MAX_APK = 300L * 1024 * 1024;
    private static final Object DOWNLOAD_LOCK=new Object();
    private final Activity activity;
    private boolean busy;
    private TextView status;
    private ProgressBar progress;

    ApkUpdates(Activity activity) { this.activity=activity; }
    static android.content.SharedPreferences prefs(Context c) { return c.getSharedPreferences("gx_apk_updates",0); }
    static boolean autoEnabled(Context c) { return prefs(c).getBoolean("auto",true); }
    private String t(String en,String ru) { return activity.getResources().getConfiguration().getLocales().get(0).getLanguage().equals("ru") ? ru : en; }
    private boolean alive() { return !activity.isFinishing() && !activity.isDestroyed(); }
    private void message(String value) { if(alive()) { if(status!=null)status.setText(value); else Toast.makeText(activity,value,Toast.LENGTH_LONG).show(); } }

    void build(LinearLayout root) {
        LinearLayout card=UiKit.card(root);
        UiKit.sectionHeader(card,R.drawable.ic_gzh_refresh,t("Application updates","Обновления приложения"),false);
        status=UiKit.body(card,t("Updates from realkot/GeneralsX. Installation requires Android confirmation.","Обновления из realkot/GeneralsX. Установка требует подтверждения Android."));
        progress=new ProgressBar(activity,null,android.R.attr.progressBarStyleHorizontal);
        progress.setMax(100);card.addView(progress);progress.setVisibility(android.view.View.GONE);
        UiKit.button(card,UiKit.BTN_TONAL,R.drawable.ic_gzh_download,t("Check for updates","Проверить обновления"),()->check(true));
        androidx.appcompat.widget.SwitchCompat auto=UiKit.switchRow(card,t("Check at launcher startup","Проверять при открытии лаунчера"),t("Checks only; APKs are downloaded after your confirmation.","Только проверка. APK загружается после вашего подтверждения."));
        auto.setChecked(autoEnabled(activity));auto.setOnCheckedChangeListener((b,on)->prefs(activity).edit().putBoolean("auto",on).apply());
        androidx.appcompat.widget.SwitchCompat tests=UiKit.switchRow(card,t("Include test prereleases","Включать тестовые prerelease"),t("Only updates matching the installed package are offered.","Предлагаются только обновления установленного пакета."));
        tests.setChecked(prefs(activity).getBoolean("tests",BuildConfig.INPUT_TEST));tests.setOnCheckedChangeListener((b,on)->prefs(activity).edit().putBoolean("tests",on).apply());
    }

    static boolean ownAsset(String value) {
        return value.startsWith("https://github.com/"+REPOSITORY+"/releases/download/") && !value.contains("/../") && !value.contains("\\");
    }
    static final class Candidate {
        String version,url,sha,notes;long code,size;
    }
    // Pure selection logic is shared with the regression tests.
    static Candidate parse(JSONObject release,JSONObject metadata,String packageName,long installed,boolean tests) throws Exception {
        if(release.optBoolean("draft") || release.optBoolean("prerelease")&&!tests) return null;
        if(!packageName.equals(metadata.getString("package")))return null;
        Candidate c=new Candidate();c.code=metadata.getLong("versionCode");
        if(c.code<=installed)return null;
        c.version=metadata.getString("versionName");c.size=metadata.getLong("bytes");c.sha=metadata.getString("sha256");c.url=metadata.getString("url");
        if(!ownAsset(c.url)||!c.sha.matches("[0-9a-f]{64}")||c.size<1||c.size>MAX_APK)throw new IOException("Invalid update metadata");
        JSONArray assets=release.getJSONArray("assets");boolean found=false;
        for(int i=0;i<assets.length();i++) {
            JSONObject a=assets.getJSONObject(i);
            if(c.url.equals(a.optString("browser_download_url"))&&a.optLong("size")==c.size&&("sha256:"+c.sha).equals(a.optString("digest")))found=true;
        }
        if(!found)throw new IOException("APK asset identity mismatch");
        c.notes=release.optString("body","");return c;
    }

    private Candidate latest() throws Exception {
        JSONArray releases=new JSONArray(new String(fetch(API,4*1024*1024),StandardCharsets.UTF_8));
        PackageInfo installed=activity.getPackageManager().getPackageInfo(activity.getPackageName(),0);
        boolean tests=prefs(activity).getBoolean("tests",BuildConfig.INPUT_TEST);Candidate best=null;
        for(int i=0;i<releases.length();i++) {
            JSONObject release=releases.getJSONObject(i);
            if(release.optBoolean("draft")||release.optBoolean("prerelease")&&!tests)continue;
            JSONArray assets=release.getJSONArray("assets");
            for(int j=0;j<assets.length();j++) {
                JSONObject a=assets.getJSONObject(j);
                if(!"update.json".equals(a.optString("name")))continue;
                String url=a.getString("browser_download_url");if(!ownAsset(url))continue;
                Candidate c=parse(release,new JSONObject(new String(fetch(url,64*1024),StandardCharsets.UTF_8)),activity.getPackageName(),installed.getLongVersionCode(),tests);
                if(c!=null&&(best==null||c.code>best.code))best=c;
            }
        }
        return best;
    }
    void check(boolean manual) {
        if(busy)return;busy=true;
        if(manual)message(t("Checking…","Проверка…"));
        new Thread(()->{
            try {
                Candidate c=latest();activity.runOnUiThread(()->{
                    busy=false;if(!alive())return;
                    if(c==null){if(manual)message(t("No compatible newer version.","Новой совместимой версии нет."));return;}
                    String title=t("Update available: ","Доступно обновление: ")+c.version;
                    if(!manual){message(title);return;}
                    new AlertDialog.Builder(activity).setTitle(title).setMessage(c.notes).setNegativeButton(android.R.string.cancel,null)
                        .setPositiveButton(t("Download","Скачать"),(d,w)->download(c)).show();
                });
            } catch(Exception e) { android.util.Log.w("GXApkUpdate","Check failed",e);activity.runOnUiThread(()->{busy=false;if(manual)message(t("Could not check updates. Check your connection and retry.","Не удалось проверить обновления. Проверьте соединение и повторите."));}); }
        },"gx-apk-check").start();
    }

    private void download(Candidate c) {
        if(busy)return;busy=true;
        File dir=new File(activity.getCacheDir(),"apk-updates");
        new Thread(()->{
            synchronized(DOWNLOAD_LOCK) {
            String name="candidate-"+c.code+"-"+c.sha.substring(0,12);
            File part=new File(dir,name+".part.apk"),apk=new File(dir,name+".apk");
            try {
                if(!dir.isDirectory()&&!dir.mkdirs())throw new IOException("Update directory unavailable");
                if(apk.isFile()) {
                    try {
                        verify(activity,apk,c);
                        activity.runOnUiThread(()->{busy=false;if(alive())install(apk);});return;
                    } catch(Exception invalidCache) {
                        java.nio.file.Files.move(apk.toPath(),new File(dir,name+".rejected-"+System.currentTimeMillis()).toPath());
                    }
                }
                if(progress!=null)activity.runOnUiThread(()->{progress.setProgress(0);progress.setVisibility(android.view.View.VISIBLE);});
                HttpURLConnection conn=open(c.url);
                try(InputStream in=conn.getInputStream();OutputStream out=new FileOutputStream(part)) {
                    byte[] b=new byte[65536];long total=0;int n,last=-1;
                    while((n=in.read(b))!=-1) {
                        total+=n;if(total>c.size)throw new IOException("Oversize APK");out.write(b,0,n);
                        int percent=(int)(total*100/c.size);
                        if(percent!=last){last=percent;activity.runOnUiThread(()->{if(alive()&&progress!=null)progress.setProgress(percent);});}
                    }
                    if(total!=c.size)throw new IOException("Incomplete APK");
                } finally {conn.disconnect();}
                verify(activity,part,c);
                // Only replace this app-owned temporary download, never game data or saves.
                java.nio.file.Files.move(part.toPath(),apk.toPath(),java.nio.file.StandardCopyOption.REPLACE_EXISTING);
                activity.runOnUiThread(()->{busy=false;if(alive())install(apk);});
            } catch(Exception e) {android.util.Log.w("GXApkUpdate","Download/verification failed",e);activity.runOnUiThread(()->{busy=false;message(t("Download or verification failed. Retry the update.","Ошибка загрузки или проверки. Повторите обновление."));});}
            }
        },"gx-apk-download").start();
    }
    static void verify(Context context,File file,Candidate c) throws Exception {
        MessageDigest hash=MessageDigest.getInstance("SHA-256");
        try(InputStream in=new FileInputStream(file)){byte[] b=new byte[65536];int n;while((n=in.read(b))!=-1)hash.update(b,0,n);}
        StringBuilder hex=new StringBuilder();for(byte b:hash.digest())hex.append(String.format(java.util.Locale.ROOT,"%02x",b&255));
        if(file.length()!=c.size||!hex.toString().equals(c.sha))throw new IOException("Checksum mismatch");
        PackageManager pm=context.getPackageManager();
        PackageInfo update=pm.getPackageArchiveInfo(file.getPath(),PackageManager.GET_SIGNING_CERTIFICATES);
        PackageInfo installed=pm.getPackageInfo(context.getPackageName(),PackageManager.GET_SIGNING_CERTIFICATES);
        verifyPackage(installed,update,c);
    }
    static void verifyPackage(PackageInfo installed,PackageInfo update,Candidate c) throws IOException {
        if(update==null||!installed.packageName.equals(update.packageName)||update.getLongVersionCode()!=c.code||!c.version.equals(update.versionName)||c.code<=installed.getLongVersionCode())throw new IOException("Package/version mismatch");
        if(update.signingInfo==null||installed.signingInfo==null)throw new IOException("Signing identity mismatch");
        android.content.pm.Signature[] actual=update.signingInfo.getApkContentsSigners(),original=installed.signingInfo.getApkContentsSigners();
        if(actual==null||actual.length==0||original==null||!Arrays.equals(actual,original))throw new IOException("Signing identity mismatch");
    }
    private void install(File apk) {
        if(!activity.getPackageManager().canRequestPackageInstalls()) {
            new AlertDialog.Builder(activity).setMessage(t("Allow this launcher to install updates, then check and download again.","Разрешите лаунчеру установку обновлений, затем повторите проверку и загрузку."))
                .setPositiveButton(android.R.string.ok,(d,w)->activity.startActivity(new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,Uri.parse("package:"+activity.getPackageName())))).setNegativeButton(android.R.string.cancel,null).show();return;
        }
        Uri uri=FileProvider.getUriForFile(activity,activity.getPackageName()+".fileprovider",apk);
        activity.startActivity(new Intent(Intent.ACTION_VIEW).setDataAndType(uri,"application/vnd.android.package-archive").addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION));
    }
    static HttpURLConnection open(String url) throws IOException {
        for(int i=0;i<6;i++) {
            URL u=new URL(url);String host=u.getHost();
            if(!"https".equals(u.getProtocol())||u.getUserInfo()!=null||!(host.equals("api.github.com")||host.equals("github.com")||host.equals("release-assets.githubusercontent.com")||host.equals("objects.githubusercontent.com")))throw new IOException("Untrusted download host");
            HttpURLConnection c=(HttpURLConnection)u.openConnection();c.setConnectTimeout(15000);c.setReadTimeout(30000);c.setInstanceFollowRedirects(false);c.setRequestProperty("User-Agent","GeneralsX-realkot-launcher");
            int code=c.getResponseCode();
            if(code>=300&&code<400){String next=c.getHeaderField("Location");c.disconnect();if(next==null)throw new IOException("Missing redirect");url=new URL(u,next).toString();continue;}
            if(code!=200){c.disconnect();throw new IOException("HTTP "+code);}return c;
        }
        throw new IOException("Too many redirects");
    }
    static byte[] fetch(String url,int limit) throws IOException {
        HttpURLConnection c=open(url);
        try(InputStream in=c.getInputStream();ByteArrayOutputStream out=new ByteArrayOutputStream()) {
            byte[] b=new byte[16384];int n;while((n=in.read(b))!=-1){if(out.size()+n>limit)throw new IOException("Response too large");out.write(b,0,n);}return out.toByteArray();
        } finally {c.disconnect();}
    }
}
