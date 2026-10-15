# Pending Android changes after r6

- Skip the EA startup logo in the Android intro path; preserve subsequent state transitions and sizzle preferences.
- Double native physical mouse cursor frames and hotspots on Android. Original software touchpad cursor art remains unchanged. If enlargement fails, retain original frames.
- Refresh the press anchor for raw double-click events in MetaEventTranslator. Previously a nearby second press reused the previous press position, producing a non-point region on release and potentially suppressing positional orders. No click duration or drag thresholds are relaxed.

Validation: `scripts/qa/test_mouse_repeat_press.py` compiles the production press cases for all three buttons, repeated nearby clicks and drag anchors. This is a host regression check, not proof of physical tablet behavior. No APK was built; existing r6 APK remains unchanged.
