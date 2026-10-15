# Android input test r5 — invisible Extras slider thumbs

Resource-only follow-up to r4, 15 October 2026. Package `com.generalsx.zerohour.inputtest`, version code 10305, version `1.4.0-inputtest.20261015-r5`.

Removed the images, fill and border colors from all nine draw slots in each of the five Extras sliders' enabled, disabled and highlighted thumb states. The extra small square was the independent native slider-thumb image, drawn over the stock segmented scale. Slider ranges, geometry, native drag handlers, keyboard handling and preference application are unchanged. The thumb remains interactive; only its decoration is absent.

Repackaged the verified r4 dual-Hz engines with the existing local packager and original staging directory. All 16 packaged native libraries, including both engines, match r4 byte-for-byte. Existing WSL/toolchains/caches and r4/r3 APKs remain. APK manifest, version, signing, alignment, ZIP CRC, dependencies, JNI and exact WND-resource checks passed; existing production Extras lifecycle/parser checks passed. No native recompilation or new implementation-mirroring tests were needed for this visual asset adjustment.

Visual validation in MuMu with the final r5 APK confirmed that all five square thumb markers are absent. A touch drag changed the scroll-speed fill while leaving the thumb invisible; Cancel returned to Options without applying the trial value. Screenshots are stored in validation-r5 in the enclosing workspace.
