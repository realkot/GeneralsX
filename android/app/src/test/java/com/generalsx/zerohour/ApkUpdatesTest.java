package com.generalsx.zerohour;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.RuntimeEnvironment;
import org.robolectric.annotation.Config;
import org.json.JSONArray;
import org.json.JSONObject;
import static org.junit.Assert.*;

// GeneralsX @test Codex 16/10/2026 Release identity, channels and corrupt metadata.
@RunWith(RobolectricTestRunner.class) @Config(sdk=35)
public class ApkUpdatesTest {
    private final String sha="a".repeat(64);
    private final String url="https://github.com/realkot/GeneralsX/releases/download/test/game.apk";
    private JSONObject meta() throws Exception {return new JSONObject().put("package","com.generalsx.zerohour.inputtest").put("versionCode",10311).put("versionName","r11").put("bytes",1200).put("sha256",sha).put("url",url);}
    private JSONObject release() throws Exception {return new JSONObject().put("prerelease",true).put("assets",new JSONArray().put(new JSONObject().put("browser_download_url",url).put("size",1200).put("digest","sha256:"+sha)));}
    @Test public void channelsPackagesAndDowngrades() throws Exception {
        assertNotNull(ApkUpdates.parse(release(),meta(),"com.generalsx.zerohour.inputtest",10310,true));
        assertNull(ApkUpdates.parse(release(),meta(),"com.generalsx.zerohour.inputtest",10311,true));
        assertNull(ApkUpdates.parse(release(),meta(),"com.generalsx.zerohour",10310,true));
        assertNull(ApkUpdates.parse(release(),meta(),"com.generalsx.zerohour.inputtest",10310,false));
        assertNull(ApkUpdates.parse(release().put("draft",true),meta(),"com.generalsx.zerohour.inputtest",10310,true));
    }
    @Test public void rejectForeignAssetsAndDigestSubstitution() throws Exception {
        for(JSONObject bad:new JSONObject[]{meta().put("url","https://github.com/other/repo/releases/download/x/a.apk"),meta().put("sha256","b".repeat(64)),meta().put("bytes",ApkUpdates.MAX_APK+1),meta().put("bytes",0)}) {
            try{ApkUpdates.parse(release(),bad,"com.generalsx.zerohour.inputtest",10310,true);fail();}catch(java.io.IOException expected){}
        }
        assertFalse(ApkUpdates.ownAsset("http://github.com/realkot/GeneralsX/releases/download/x/a.apk"));
        assertFalse(ApkUpdates.ownAsset("https://github.com/realkot/GeneralsX/releases/download/../a.apk"));
    }
    @Test public void autoCheckCanBeDisabledAndSurvivesRecreation() {
        android.content.Context c=RuntimeEnvironment.getApplication();ApkUpdates.prefs(c).edit().clear().commit();
        assertTrue(ApkUpdates.autoEnabled(c));ApkUpdates.prefs(c).edit().putBoolean("auto",false).commit();assertFalse(ApkUpdates.autoEnabled(c));
    }
    @Test public void rejectNonHttpsBeforeNetwork() throws Exception {
        try{ApkUpdates.open("http://github.com/realkot/GeneralsX");fail();}catch(java.io.IOException expected){}
        try{ApkUpdates.open("https://example.com/update.apk");fail();}catch(java.io.IOException expected){}
    }
    private android.content.pm.PackageInfo info(int code,String signer) {
        android.content.pm.PackageInfo p=new android.content.pm.PackageInfo();p.packageName="com.generalsx.zerohour.inputtest";p.setLongVersionCode(code);p.versionName="r11";
        p.signingInfo=new android.content.pm.SigningInfo();
        org.robolectric.Shadows.shadowOf(p.signingInfo).setSignatures(new android.content.pm.Signature[]{new android.content.pm.Signature(signer)});
        return p;
    }
    @Test public void installedPackageAndSigningIdentityAreRequired() throws Exception {
        ApkUpdates.Candidate c=ApkUpdates.parse(release(),meta(),"com.generalsx.zerohour.inputtest",10310,true);
        android.content.pm.PackageInfo installed=info(10310,"aabb"),update=info(10311,"aabb");
        ApkUpdates.verifyPackage(installed,update,c);
        for(int n=0;n<5;n++) {
            update=info(10311,"aabb");
            if(n==0)update.packageName="other";
            if(n==1)update.setLongVersionCode(10310);
            if(n==2)update.versionName="different";
            if(n==3)update=info(10311,"ccdd");
            if(n==4)update.signingInfo=null;
            try{ApkUpdates.verifyPackage(installed,update,c);fail();}catch(java.io.IOException expected){}
        }
    }
    @Test public void interruptedOrCorruptDownloadCannotReachInstaller() throws Exception {
        ApkUpdates.Candidate c=ApkUpdates.parse(release(),meta(),"com.generalsx.zerohour.inputtest",10310,true);
        java.io.File f=new java.io.File(RuntimeEnvironment.getApplication().getCacheDir(),"corrupt.apk");
        java.nio.file.Files.write(f.toPath(),new byte[]{1,2,3});
        try{ApkUpdates.verify(RuntimeEnvironment.getApplication(),f,c);fail();}catch(java.io.IOException expected){assertEquals("Checksum mismatch",expected.getMessage());}
    }

}
