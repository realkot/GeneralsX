package com.generalsx.zerohour;

import static org.junit.Assert.*;
import java.io.File;
import java.nio.file.Files;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;
import org.junit.runner.RunWith;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.annotation.Config;

@RunWith(RobolectricTestRunner.class)
@Config(sdk = 28)
public class HudTextureDeliveryTest {
    @Rule public TemporaryFolder temp = new TemporaryFolder();

    // GeneralsX @bugfix Codex 15/10/2026 Large UI packs are copied once per fingerprint.
    @Test public void fingerprintSkipsCopiesButRepairsMissingAndUpdatesSameSize() throws Exception {
        File bundle = temp.newFolder("versionedBundle");
        File game = temp.newFolder("versionedGame");
        File source = new File(bundle, "Art/Textures");
        assertTrue(source.mkdirs());
        File input = new File(source, "gx_hd_sncontrolbar512_001.tga");
        File marker = new File(source, "gx_hd_manifest.txt");
        Files.write(input.toPath(), new byte[]{1,2,3});
        Files.write(marker.toPath(), new byte[]{1});
        SetupActivity.syncEngineHudTextures(bundle, game.getAbsolutePath());
        File output = new File(game, "Art/Textures/gx_hd_sncontrolbar512_001.tga");
        assertTrue(output.setLastModified(1000000L));
        SetupActivity.syncEngineHudTextures(bundle, game.getAbsolutePath());
        assertEquals(1000000L, output.lastModified());
        Files.write(input.toPath(), new byte[]{4,5,6});
        Files.write(marker.toPath(), new byte[]{2});
        SetupActivity.syncEngineHudTextures(bundle, game.getAbsolutePath());
        assertArrayEquals(new byte[]{4,5,6}, Files.readAllBytes(output.toPath()));
        assertTrue(output.delete());
        SetupActivity.syncEngineHudTextures(bundle, game.getAbsolutePath());
        assertArrayEquals(new byte[]{4,5,6}, Files.readAllBytes(output.toPath()));
    }

    @Test public void failedAtlasCopyDoesNotCommitFingerprint() throws Exception {
        File bundle = temp.newFolder("failedBundle");
        File game = temp.newFolder("failedGame");
        File source = new File(bundle, "Art/Textures");
        assertTrue(source.mkdirs());
        Files.write(new File(source, "gx_hd_sncontrolbar512_001.tga").toPath(), new byte[]{1});
        Files.write(new File(source, "gx_hd_manifest.txt").toPath(), new byte[]{2});
        File target = new File(game, "Art/Textures");
        assertTrue(target.mkdirs());
        assertTrue(new File(target, "gx_hd_sncontrolbar512_001.tga").mkdir());
        File marker = new File(target, "gx_hd_manifest.txt");
        Files.write(marker.toPath(), new byte[]{1});
        SetupActivity.syncEngineHudTextures(bundle, game.getAbsolutePath());
        assertArrayEquals(new byte[]{1}, Files.readAllBytes(marker.toPath()));
    }

    @Test public void installsAndUpdatesOnlyOwnedAtlasesAndHandlesSharedRoot() throws Exception {
        File bundle = temp.newFolder("bundle");
        File game = temp.newFolder("game");
        File source = new File(bundle, "Art/Textures");
        assertTrue(source.mkdirs());
        File target = new File(game, "Art/Textures");
        assertTrue(target.mkdirs());
        File original = new File(target, "sncommandbar.tga");
        Files.write(original.toPath(), new byte[]{9});
        File input = new File(source, "gx_hd_sncommandbar.tga");
        Files.write(input.toPath(), new byte[]{1,2,3});
        Files.write(new File(source, "unrelated.tga").toPath(), new byte[]{7});
        Files.write(new File(source, "gx_hd_scshelluserinterface512_001.tga").toPath(), new byte[]{8});
        SetupActivity.syncEngineHudTextures(bundle, game.getAbsolutePath());
        File output = new File(target, input.getName());
        assertArrayEquals(new byte[]{1,2,3}, Files.readAllBytes(output.toPath()));
        assertArrayEquals(new byte[]{9}, Files.readAllBytes(original.toPath()));
        assertFalse(new File(target, "unrelated.tga").exists());
        assertFalse(new File(target, "gx_hd_scshelluserinterface512_001.tga").exists());
        Files.write(input.toPath(), new byte[]{4,5});
        SetupActivity.syncEngineHudTextures(bundle, game.getAbsolutePath());
        assertArrayEquals(new byte[]{4,5}, Files.readAllBytes(output.toPath()));
        SetupActivity.syncEngineHudTextures(bundle, bundle.getAbsolutePath());
        assertArrayEquals(new byte[]{4,5}, Files.readAllBytes(input.toPath()));
    }
}
