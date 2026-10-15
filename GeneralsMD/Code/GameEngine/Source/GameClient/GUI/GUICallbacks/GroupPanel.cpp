/*
**	Command & Conquer Generals Zero Hour(tm)
**	Copyright 2025 Electronic Arts Inc.
**
**	This program is free software: you can redistribute it and/or modify
**	it under the terms of the GNU General Public License as published by
**	the Free Software Foundation, either version 3 of the License, or
**	(at your option) any later version.
**
**	This program is distributed in the hope that it will be useful,
**	but WITHOUT ANY WARRANTY; without even the implied warranty of
**	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
**	GNU General Public License for more details.
**
**	You should have received a copy of the GNU General Public License
**	along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

// FILE: GroupPanel.cpp ///////////////////////////////////////////////////////////////////////////
// GeneralsX @feature Android port 02/08/2026
//
// Native in-engine replacement for the Android-overlay unit-group touch
// panel: a small handle button that expands a row of 10 buttons (0-9) for
// control-group assignment/recall. GroupPanel.wnd is loaded from a loose
// file (Window\GroupPanel.wnd) rather than the game's own .big archives --
// see GameWindowManagerScript.cpp's Window\ path resolution, same trick
// already used for GeneralsOnline's own screens -- so this never touches
// the user's separately-owned game data.
//
// Quick tap (GBM_SELECTED): recall/select that group, same as a bare 0-9
// keypress -- unless the group is still empty, in which case tap assigns
// instead (an empty group has no useful "recall" meaning to begin with,
// and a first-time user has no reason to already know the
// long-press/right-click-to-assign convention -- this exact confusion was
// reported against the Android-overlay version of this feature).
// Two-finger-tap a group button (GBM_SELECTED_RIGHT -- GadgetPushButton's
// existing right-click handling, which the touch layer's two-finger-tap
// already produces at whatever screen position it lands on): always
// assign/replace, regardless of occupancy -- the deliberate, explicit
// version of the same action.
//
// GeneralsX @feature Android port 02/08/2026, simplified 03/08/2026 Hold
// gesture: press and hold a group button, a clock-wipe overlay
// (GadgetButtonDrawClock -- the same mechanism this engine already has for
// production-progress buttons, see W3DPushButton.cpp) fills clockwise in
// red over GROUP_HOLD_MS; release once it completes (the whole button
// reads solid red at percent=100) to CLEAR the group entirely. Releasing
// before the wipe completes is just the normal tap above -- unchanged.
// (A first version also had a shorter green "add to group" stage before
// the red one, dropped once real use showed it was redundant: a plain tap
// on a non-empty group already assigns/replaces it with the current
// selection, which covers the same "grow this group" need a two-finger-
// tap/force-assign already handles explicitly.)
//
// CLEAR is built from the existing, already network-replicated
// MSG_CREATE_TEAM<n> message (never a new message type), sent directly
// with zero object-ID arguments -- Player::processCreateTeamGameMessage()
// (Player.cpp) always clears the hotkey squad first regardless, so an
// argument-less message just clears it. This never touches the player's
// on-screen battlefield selection at all (an earlier version tried
// building the empty team via the SELECTION-driven MSG_META_CREATE_TEAM<n>
// instead -- deselect everything, fire it, restore afterward -- which hit
// a string of bugs: the restore raced the message translator, then broke
// move orders for the restored units by only touching the client-side
// selection list and not the player's real AIGroup, then still left the
// selection visibly flickering/disappearing for the reselect's deferred
// frame; sending the concrete message directly sidesteps all of it).
//
// None of the actual group logic (assignment, recall, double-press-to-
// recenter-camera) is reimplemented here -- SelectionXlat.cpp's
// onMetaCreateTeam()/onMetaSelectTeam() already do the tap/two-finger-tap
// paths; this only needs to feed the same MSG_META_CREATE_TEAM<n>/
// MSG_META_SELECT_TEAM<n>/MSG_CREATE_TEAM<n> a keyboard shortcut or a
// real click-based force-assign would have.
///////////////////////////////////////////////////////////////////////////////////////////////////

#include "PreRTS.h"

#include "Common/GXSafeArea.h"
#include "Common/MessageStream.h"
#include "Common/NameKeyGenerator.h"
#include "Common/Player.h"
#include "Common/PlayerList.h"
#include "GameClient/Color.h"
#include "GameClient/Display.h"
#include "GameClient/GXUiScale.h"
#include "GameClient/GXArmyPanelLayout.h"
#include "GameClient/GadgetPushButton.h"
#include "GameClient/GameWindow.h"
#include "GameClient/GameWindowManager.h"
#include "GameClient/GUICallbacks.h"
#include "GameClient/WindowLayout.h"
#include "GameClient/WinInstanceData.h"
#include "GameLogic/Squad.h"
#include "GameClient/Shell.h"
#include "GameClient/GameText.h"
#include "GameClient/GameFont.h"
#include <cstdlib>
#include <cstring>
#include <map>
#include "Common/GXTabletControls.h"
#include "GameClient/DisplayString.h"
#include "GameClient/DisplayStringManager.h"
#include "GameClient/InGameUI.h"
#include "GameLogic/GameLogic.h"

// GeneralsX @feature Codex 14/10/2026 Explicit screen/map selection, on the game thread.
static NameKeyType s_armyButtons[5] = { NAMEKEY_INVALID, NAMEKEY_INVALID, NAMEKEY_INVALID, NAMEKEY_INVALID, NAMEKEY_INVALID };
static Bool s_armyLabelsSet = FALSE;

// GeneralsX @feature Codex 16/10/2026 Keep customization outside the legacy window ABI.
static Bool s_armyCollapsed = FALSE;
static UnsignedInt s_handlePress = 0;
struct GXPanelFontState {
    GameFont *base=nullptr;
    Bool initialized=FALSE;Color colors[6]={};
    Int width=0,height=0;
    UnicodeString text;
};
static std::map<GameWindow*,GXPanelFontState> s_panelFonts;
static void gxStylePanelButton(GameWindow *button, Int width, Int height)
{
    if(!button)return;
    const auto &settings=GXTabletControls::get();
    auto &state=s_panelFonts[button];
    if(!state.initialized) {
        state.base=button->winGetFont();state.initialized=TRUE;
        state.colors[0]=button->winGetEnabledColor(0);state.colors[1]=button->winGetDisabledColor(0);
        state.colors[2]=button->winGetHiliteColor(0);state.colors[3]=button->winGetEnabledBorderColor(0);
        state.colors[4]=button->winGetDisabledBorderColor(0);state.colors[5]=button->winGetHiliteBorderColor(0);
    }
    UnicodeString text=button->winGetText();
    if(state.width==width && state.height==height && state.text==text)return;
    state.width=width;state.height=height;state.text=text;
    const auto fade=[&](Color color)->Color {
        UnsignedInt raw=(UnsignedInt)color;
        return (Color)((raw&0x00ffffffu)|(((raw>>24)*settings.panelOpacity/100)<<24));
    };
    button->winSetEnabledColor(0,fade(state.colors[0]));
    button->winSetDisabledColor(0,fade(state.colors[1]));
    button->winSetHiliteColor(0,fade(state.colors[2]));
    button->winSetEnabledBorderColor(0,fade(state.colors[3]));
    button->winSetDisabledBorderColor(0,fade(state.colors[4]));
    button->winSetHiliteBorderColor(0,fade(state.colors[5]));
    if(!state.base || !TheFontLibrary)return;
    Int target=max(1,state.base->pointSize*settings.panelScale/100);
    GameFont *font=TheFontLibrary->getFont(state.base->nameString,target,state.base->bold);
    if(settings.fitLabels && TheDisplayStringManager && TheDisplay) {
        DisplayString *measure=TheDisplayStringManager->newDisplayString();
        if(measure) {
            measure->setText(text);measure->setWordWrap(0);
            const Int smallest=max(8,(Int)(8*min(TheDisplay->getWidth()/800.0f,TheDisplay->getHeight()/600.0f)));
            while(font && target>smallest) {
                measure->setFont(font);Int w,h;measure->getSize(&w,&h);
                if(w<=width-8 && h<=height-4)break;
                --target;font=TheFontLibrary->getFont(state.base->nameString,target,state.base->bold);
            }
            TheDisplayStringManager->freeDisplayString(measure);
        }
    }
    if(font)button->winSetFont(font);
}

static Bool canSelectArmy()
{
    return TheMessageStream && TheInGameUI && TheInGameUI->getInputEnabled()
        && TheGameLogic && TheGameLogic->isInInteractiveGame() && TheGameLogic->getFrame() > 0
        && !TheGameLogic->isGamePaused() && !(TheShell && TheShell->isShellActive())
        && ThePlayerList && ThePlayerList->getLocalPlayer()
        && ThePlayerList->getLocalPlayer()->isPlayerActive();
}

static void selectArmy(Bool acrossMap)
{
    if (!canSelectArmy()) return;
    KindOfMaskType required, excluded;
    excluded.set(KINDOF_DOZER);
    excluded.set(KINDOF_HARVESTER);
    excluded.set(KINDOF_IGNORES_SELECT_ALL);
    excluded.set(KINDOF_STRUCTURE);
    // The destroy/create group messages preserve the authoritative command group,
    // including an empty result. Never use the screen-then-map toggle here.
    TheInGameUI->deselectAllDrawables();
    if (acrossMap) TheInGameUI->selectAllUnitsByTypeAcrossMap(required, excluded);
    else TheInGameUI->selectAllUnitsByTypeAcrossScreen(required, excluded);
}


// GeneralsX @feature Codex 14/10/2026 Select combat aircraft with the retail mass-selection predicate.
// Retail Comanche uses JetAIUpdate too; PRODUCED_AT_HELIPAD distinguishes helicopters.
// Do not exclude TRANSPORT: the armed Helix is a helicopter as well as a transport.
static void selectAirArmy(Bool helicopters)
{
    if (!canSelectArmy()) return;
    KindOfMaskType required, excluded;
    required.set(KINDOF_AIRCRAFT);
    required.set(KINDOF_CAN_ATTACK);
    if (helicopters) required.set(KINDOF_PRODUCED_AT_HELIPAD);
    else excluded.set(KINDOF_PRODUCED_AT_HELIPAD);
    excluded.set(KINDOF_DOZER);
    excluded.set(KINDOF_HARVESTER);
    excluded.set(KINDOF_IGNORES_SELECT_ALL);
    excluded.set(KINDOF_STRUCTURE);
    TheInGameUI->deselectAllDrawables();
    TheInGameUI->selectAllUnitsByTypeAcrossMap(required, excluded);
}

// GeneralsX @selection Codex 14/10/2026 Reset the repeat cycle after any other selection.
static Bool s_groundNextAcrossMap = FALSE;
static UnsignedInt s_groundSelectionRevision = 0;
static void selectGroundArmy()
{
    if (!canSelectArmy()) return;
    if (TheInGameUI->getSelectionRevision() != s_groundSelectionRevision) s_groundNextAcrossMap = FALSE;
    KindOfMaskType required, excluded;
    required.set(KINDOF_CAN_ATTACK);
    excluded.set(KINDOF_AIRCRAFT); excluded.set(KINDOF_DOZER); excluded.set(KINDOF_HARVESTER);
    excluded.set(KINDOF_IGNORES_SELECT_ALL); excluded.set(KINDOF_STRUCTURE);
    TheInGameUI->deselectAllDrawables();
    if (s_groundNextAcrossMap) TheInGameUI->selectAllUnitsByTypeAcrossMap(required, excluded);
    else TheInGameUI->selectAllUnitsByTypeAcrossScreen(required, excluded);
    s_groundNextAcrossMap = !s_groundNextAcrossMap;
    s_groundSelectionRevision = TheInGameUI->getSelectionRevision();
}

// Legacy language packs do not have the new compact labels. Honor the chosen text language.
static const wchar_t *gxArmyLabelFallback(Int index)
{
    struct Labels { const char *language; const wchar_t *text[5]; };
    static const Labels labels[] = {
        {"english", {L"Screen", L"Map", L"Planes", L"Helis", L"Ground"}},
        {"russian", {L"Экран", L"Карта", L"Самолёты", L"Вертол.", L"Наземные"}},
        {"ukrainian", {L"Екран", L"Карта", L"Літаки", L"Гелікоп.", L"Наземні"}},
        {"interslavic", {L"Ekran", L"Mapa", L"Aviony", L"Helikop.", L"Zemja"}},
        {"arabic", {L"الشاشة", L"الخريطة", L"طائرات", L"مروحيات", L"برية"}},
        {"brazilian", {L"Tela", L"Mapa", L"Aviões", L"Helicóp.", L"Terrest."}},
        {"chinese", {L"屏幕", L"全图", L"战机", L"直升机", L"地面"}},
        {"french", {L"Écran", L"Carte", L"Avions", L"Hélicos", L"Sol"}},
        {"german", {L"Bild", L"Karte", L"Flieger", L"Helis", L"Boden"}},
        {"korean", {L"화면", L"지도", L"전투기", L"헬기", L"지상군"}},
        {"persian", {L"صفحه", L"نقشه", L"هواپیما", L"بالگرد", L"زمینی"}},
        {"polish", {L"Ekran", L"Mapa", L"Samoloty", L"Śmigłow.", L"Lądowe"}},
        {"spanish", {L"Pantalla", L"Mapa", L"Aviones", L"Helicóp.", L"Tierra"}},
    };
    const char *language = getenv("GENERALSX_TEXT_LANGUAGE");
    for (const auto &entry : labels) if (language && strcmp(language, entry.language) == 0) return entry.text[index];
    return labels[0].text[index];
}

static NameKeyType s_parentID = NAMEKEY_INVALID;
static NameKeyType s_buttonHandleID = NAMEKEY_INVALID;
static NameKeyType s_groupRowID = NAMEKEY_INVALID;
static NameKeyType s_buttonGroupID[10];
static Bool s_groupRowExpanded = FALSE;

// GeneralsX @feature Android port 02/08/2026 Hold-gesture timing. 0 means
// "not currently pressed" for s_pressStartMs, so a genuine press start is
// never allowed to land exactly on timeGetTime()==0 in practice.
static const UnsignedInt GROUP_HOLD_MS = 600;
static UnsignedInt s_pressStartMs[10] = { 0 };

//-------------------------------------------------------------------------------------------------
static void cacheWidgetIDs()
{
	if (s_buttonHandleID != NAMEKEY_INVALID) {
		return; // already cached -- GWM_CREATE fires once per window in this layout
	}
	s_parentID = TheNameKeyGenerator->nameToKey("GroupPanel.wnd:GroupPanelParent");
	s_buttonHandleID = TheNameKeyGenerator->nameToKey("GroupPanel.wnd:ButtonHandle");
	s_groupRowID = TheNameKeyGenerator->nameToKey("GroupPanel.wnd:GroupRow");
    const char *armyNames[5] = {"ArmyScreen", "ArmyMap", "ArmyPlanes", "ArmyHelicopters", "ArmyGround"};
    for (Int i=0; i<5; ++i) {
        char armyID[64]; sprintf(armyID, "GroupPanel.wnd:%s", armyNames[i]);
        s_armyButtons[i] = TheNameKeyGenerator->nameToKey(armyID);
    }
	char buf[40];
	for (Int i = 0; i < 10; ++i) {
		sprintf(buf, "GroupPanel.wnd:ButtonGroup%d", i);
		s_buttonGroupID[i] = TheNameKeyGenerator->nameToKey(buf);
	}
}

//-------------------------------------------------------------------------------------------------
static Int findGroupButtonIndex(Int controlID)
{
	for (Int i = 0; i < 10; ++i) {
		if (controlID == s_buttonGroupID[i]) {
			return i;
		}
	}
	return -1;
}

//-------------------------------------------------------------------------------------------------
static Bool isGroupEmpty(Int group)
{
	if (!ThePlayerList) {
		return TRUE;
	}
	Player *player = ThePlayerList->getLocalPlayer();
	if (!player) {
		return TRUE;
	}
	Squad *squad = player->getHotkeySquad(group);
	return !squad || squad->getLiveObjects().empty();
}

//-------------------------------------------------------------------------------------------------
static void handleGroupCommand(Int group, Bool forceAssign)
{
	if (!TheMessageStream || group < 0 || group > 9) {
		return;
	}
	Bool assign = forceAssign || isGroupEmpty(group);
	GameMessage::Type type = assign
		? (GameMessage::Type)(GameMessage::MSG_META_CREATE_TEAM0 + group)
		: (GameMessage::Type)(GameMessage::MSG_META_SELECT_TEAM0 + group);
	TheMessageStream->appendMessage(type);
}

//-------------------------------------------------------------------------------------------------
// GeneralsX @bugfix Android port 04/08/2026 Two earlier versions of this
// built the empty team via MSG_META_CREATE_TEAM<n>, which has no
// arguments of its own -- SelectionTranslator::onMetaCreateTeam()
// (SelectionXlat.cpp) always builds it from whatever's CURRENTLY selected
// on the battlefield at translation time, so getting an EMPTY team out of
// it meant deselecting everything first, then restoring the player's
// actual selection afterward. That restore was a real source of bugs:
// doing it synchronously raced the translator (it hadn't run yet, so it
// saw the restored selection, not the empty one -- team never actually
// got cleared); deferring it a frame fixed that but reportedly used
// TheInGameUI->selectDrawable() to reselect, which never rebuilds the
// player's real (network-replicated) AIGroup, only the client-local
// selection list, so the "restored" units looked selected but weren't
// actually commandable; fixing THAT to send MSG_CREATE_SELECTED_GROUP
// instead fixed commandability, but the player's selection still
// visibly disappeared for a frame (and, per a later report, sometimes
// longer) between the deselect and the deferred restore.
//
// All of that complexity existed only to build an EMPTY team through a
// message that has no way to say "empty" directly. The underlying
// concrete message, MSG_CREATE_TEAM<n>, doesn't have that limitation --
// Player::processCreateTeamGameMessage() (Player.cpp) always clears the
// hotkey squad first, then adds whatever object-ID arguments the message
// carries; sent with ZERO of them, it just clears. Sending that directly
// means CLEAR never has to touch the player's on-screen selection at
// all -- nothing to snapshot, nothing to restore, nothing that can
// flicker or desync.
static void handleGroupClear(Int group)
{
	if (!TheMessageStream || group < 0 || group > 9) {
		return;
	}
	TheMessageStream->appendMessage((GameMessage::Type)(GameMessage::MSG_CREATE_TEAM0 + group));
}

//-------------------------------------------------------------------------------------------------
// Called every frame while the panel exists. Polls each group button's own
// WIN_STATE_SELECTED bit (set/cleared by GadgetPushButtonInput on
// GWM_LEFT_DOWN/GWM_LEFT_UP) rather than intercepting raw window messages,
// so the existing tap/click handling in GadgetPushButton.cpp is completely
// untouched -- this only observes it. Draws the red clock-wipe while held;
// GroupPanelSystem's GBM_SELECTED handler reads s_pressStartMs to decide
// what the release actually meant.
static void updateHoldVisuals()
{
	// GeneralsX @bugfix Android port 06/08/2026 This ran unconditionally
	// every frame of every match regardless of whether the group row was
	// even expanded -- 10 recursive TheWindowManager->winGetWindowFromId()
	// tree walks/frame for buttons that are hidden (and therefore
	// unpressable, so WIN_STATE_SELECTED could never be set on them) the
	// vast majority of the time, since s_groupRowExpanded defaults FALSE
	// and the row is only shown while the spoiler handle is held open.
	// Skip the whole thing when the row is collapsed, matching the same
	// s_groupRowExpanded gate the row's own winHide() already uses.
	if (!s_groupRowExpanded) {
		return;
	}
	if (!TheWindowManager) {
		return;
	}
	UnsignedInt now = timeGetTime();
	for (Int i = 0; i < 10; ++i) {
		GameWindow *button = TheWindowManager->winGetWindowFromId(nullptr, s_buttonGroupID[i]);
		if (!button) {
			continue;
		}

		Bool pressed = BitIsSet(button->winGetInstanceData()->getState(), WIN_STATE_SELECTED);
		if (!pressed) {
			s_pressStartMs[i] = 0;
			continue;
		}

		if (s_pressStartMs[i] == 0) {
			s_pressStartMs[i] = now;
		}

		UnsignedInt elapsed = now - s_pressStartMs[i];
		Int percent = 1 + (Int)((elapsed * 99u) / GROUP_HOLD_MS);
		if (percent > 100) percent = 100;
		GadgetButtonDrawClock(button, percent, GameMakeColor(220, 60, 50, 255));
	}
}

// GeneralsX @feature Android port 03/08/2026 See GUICallbacks.h's comment.
// The offset is captured exactly ONCE, at ControlBar::init() time, before
// the real bar has ever run a single show/hide slide animation -- at that
// moment both this panel's handle and the real ControlBarParent are still
// sitting at their plain authored .wnd resting positions, so the
// screen-space delta between them is the true, permanent spatial
// relationship, independent of any animation timing. Earlier attempts
// calibrated lazily at runtime (once "visible", or once "visible AND the
// bar's slide-in animation had settled") -- both were timing-dependent:
// the first could sample a transient mid-slide bar position (real device
// report: the panel flew off the top of the screen); the second was
// correct but only ever moved the panel AFTER the bar's animation
// finished, so the panel just sat static and "already in place" for the
// whole slide instead of sliding in together with the bar, which is the
// actual "become an inseparable part of the bar" behavior asked for.
// Since the offset never needs to change, tracking by it unconditionally
// every frame (see GroupPanelFollowControlBar below) makes the panel
// mirror the bar's live screen position on every single frame, including
// every frame of its slide-in/out animation.
// GeneralsX @bugfix Android port 04/10/2026 Issue #33: the panel's root window must cover exactly
// what is shown -- the handle, plus the row while it is open -- and nothing else.
//
// The window manager hit-tests by top-level window: the first one whose rectangle contains the
// point is searched for a child, and the search stops there (getWindowUnderCursor(),
// findWindowUnderMouse()). GroupPanelParent is authored as one rectangle around the handle and the
// whole row, and it is NOINPUT, so over its empty parts the answer was "no window" -- and the
// windows underneath it, the command bar's own buttons (the general's promotions among them), were
// never reached. Worse, the cutout margin (02/10/2026) moved the handle and the row right but not
// their parent, so the "9" button ended up outside the rectangle that is searched and could not be
// pressed at all. Fitting the root to its visible children after every move and every open/close
// fixes both: a point outside the buttons is outside the panel.
static void fitParentToVisibleContent()
{
	if (!TheWindowManager) {
		return;
	}
	GameWindow *parent = TheWindowManager->winGetWindowFromId(nullptr, s_parentID);
	GameWindow *handle = TheWindowManager->winGetWindowFromId(nullptr, s_buttonHandleID);
	GameWindow *row = TheWindowManager->winGetWindowFromId(nullptr, s_groupRowID);
	if (!parent || !handle || !row) {
		return;
	}
	Int hx, hy, hw, hh;
	handle->winGetScreenPosition(&hx, &hy);
	handle->winGetSize(&hw, &hh);
	Int loX = hx, loY = hy, hiX = hx + hw, hiY = hy + hh;
	if (!row->winIsHidden()) {
		Int rx, ry, rw, rh;
		row->winGetScreenPosition(&rx, &ry);
		row->winGetSize(&rw, &rh);
		loX = min(loX, rx);
		loY = min(loY, ry);
		hiX = max(hiX, rx + rw);
		hiY = max(hiY, ry + rh);
	}
    for (Int i=0; i<5; ++i) {
        GameWindow *button = TheWindowManager->winGetWindowFromId(nullptr, s_armyButtons[i]);
        if (!button || button->winIsHidden()) continue;
        Int bx,by,bw,bh; button->winGetScreenPosition(&bx,&by); button->winGetSize(&bw,&bh);
        loX=min(loX,bx); loY=min(loY,by); hiX=max(hiX,bx+bw); hiY=max(hiY,by+bh);
    }
	Int px, py, pw, ph;
	parent->winGetScreenPosition(&px, &py);
	parent->winGetSize(&pw, &ph);
	if (px == loX && py == loY && pw == hiX - loX && ph == hiY - loY) {
		return;
	}
	// The children are placed relative to the root: move them back by however far the root moves,
	// so nothing on screen shifts.
	const Int dx = loX - px;
	const Int dy = loY - py;
	Int cx, cy;
	handle->winGetPosition(&cx, &cy);
	handle->winSetPosition(cx - dx, cy - dy);
	row->winGetPosition(&cx, &cy);
	row->winSetPosition(cx - dx, cy - dy);
    for (Int i=0; i<5; ++i) {
        GameWindow *button = TheWindowManager->winGetWindowFromId(nullptr, s_armyButtons[i]);
        if (button) { button->winGetPosition(&cx,&cy); button->winSetPosition(cx-dx,cy-dy); }
    }
	Int ox, oy;
	parent->winGetPosition(&ox, &oy);
	parent->winSetPosition(ox + dx, oy + dy);
	parent->winSetSize(hiX - loX, hiY - loY);
}

static Bool s_followOffsetCalibrated = FALSE;
static Int s_followOffsetX = 0;
static Int s_followOffsetY = 0;

void GroupPanelCalibrateFollowOffset(Int barScreenX, Int barScreenY)
{
	if (!TheWindowManager) {
		return;
	}
	GameWindow *handle = TheWindowManager->winGetWindowFromId(nullptr, s_buttonHandleID);
	if (!handle) {
		return;
	}
	Int handleX, handleY;
	handle->winGetScreenPosition(&handleX, &handleY);
	s_followOffsetX = handleX - barScreenX;
	s_followOffsetY = handleY - barScreenY;
	s_followOffsetCalibrated = TRUE;
	// GeneralsX @feature Android port 02/10/2026 Where the row's handle and the control bar are when
	// the offset is taken, to check the interface scale moved both (GXUiScale.h).
	fprintf(stderr, "[GX-UISCALE] group panel handle at %d,%d, control bar at %d,%d\n",
		handleX, handleY, barScreenX, barScreenY);
}

// GeneralsX @feature Codex 15/10/2026 Place the army column in the HUD's left gap.
void GroupPanelFollowControlBar(Int barScreenX, Int barScreenY, Bool visible)
{
    if (!visible || !s_followOffsetCalibrated || !TheWindowManager || !TheDisplay) return;
    GameWindow *parent = TheWindowManager->winGetWindowFromId(nullptr, s_parentID);
    GameWindow *handle = TheWindowManager->winGetWindowFromId(nullptr, s_buttonHandleID);
    GameWindow *row = TheWindowManager->winGetWindowFromId(nullptr, s_groupRowID);
    if (!parent || !handle || !row) return;
    const auto &settings=GXTabletControls::get();
    Int visibleButtons=0;
    for(Int i=0;i<5;++i)if(!s_armyCollapsed && (settings.panelMask&(1<<i)))++visibleButtons;
    const GXUiScale::Transform &bar = GXUiScale::forLayout("ControlBar.wnd");
    const GXArmyPanelLayout::Layout box = GXArmyPanelLayout::calculate(
        TheDisplay->getWidth(), TheDisplay->getHeight(), barScreenX, barScreenY,
        GXSafeArea::leftPx(), GXSafeArea::bottomPx(), bar.fontK,
        settings.panelScale,settings.panelWidth,settings.panelLeft,settings.panelBottom,visibleButtons);
    Int px,py;
    parent->winGetScreenPosition(&px,&py);
    handle->winSetPosition(box.x-px,box.y-py);
    handle->winSetSize(box.width,box.height);
    gxStylePanelButton(handle,box.width,box.height);
    Int buttonRow=0;
    for (Int i=0;i<5;++i) {
        GameWindow *button = TheWindowManager->winGetWindowFromId(nullptr,s_armyButtons[i]);
        if (!button) continue;
        const Bool show=!s_armyCollapsed && (settings.panelMask&(1<<i));
        button->winHide(!show);
        if(!show)continue;
        ++buttonRow;
        button->winSetPosition(box.x-px,box.y+buttonRow*(box.height+box.gap)-py);
        button->winSetSize(box.width,box.height);
        gxStylePanelButton(button,box.width,box.height);
    }
    row->winSetPosition(box.rowX-px,box.rowY-py);
    row->winSetSize(box.columns*box.cellWidth+(box.columns-1)*box.gap,
        box.rows*box.cellHeight+(box.rows-1)*box.gap);
    for (Int i=0;i<10;++i) {
        GameWindow *button = TheWindowManager->winGetWindowFromId(nullptr,s_buttonGroupID[i]);
        if (!button) continue;
        button->winSetPosition((i%box.columns)*(box.cellWidth+box.gap),
            (i/box.columns)*(box.cellHeight+box.gap));
        button->winSetSize(box.cellWidth,box.cellHeight);
        gxStylePanelButton(button,box.cellWidth,box.cellHeight);
    }
    fitParentToVisibleContent();
}

//-------------------------------------------------------------------------------------------------
void GroupPanelInit(WindowLayout *layout, void *userData)
{
	(void)layout;
	(void)userData;
	s_armyCollapsed = GXTabletControls::get().panelCollapsed;
    s_handlePress=0;s_panelFonts.clear();
	s_groundNextAcrossMap = FALSE;
	s_groundSelectionRevision = TheInGameUI ? TheInGameUI->getSelectionRevision() : 0;
}

//-------------------------------------------------------------------------------------------------
void GroupPanelUpdate(WindowLayout *layout, void *userData)
{
	(void)layout;
	(void)userData;
	updateHoldVisuals();
    if(TheWindowManager) {
        GameWindow *handle=TheWindowManager->winGetWindowFromId(nullptr,s_buttonHandleID);
        if(handle && BitIsSet(handle->winGetInstanceData()->getState(),WIN_STATE_SELECTED)) {
            if(!s_handlePress)s_handlePress=timeGetTime();
        } else s_handlePress=0;
    }
    if (!TheWindowManager) return;
    const Bool enabled = canSelectArmy();
    for (Int i=0; i<5; ++i) {
        GameWindow *button = TheWindowManager->winGetWindowFromId(nullptr, s_armyButtons[i]);
        if (!button) continue;
        button->winEnable(enabled);
        // Existing installed language packs may predate these labels: use a readable fallback.
        if (TheGameText && !s_armyLabelsSet) {
            Bool exists = FALSE;
            const char *keys[5] = {"GUI:ArmyScreenShort", "GUI:ArmyMapShort", "GUI:ArmyPlanesShort", "GUI:ArmyHelicoptersShort", "GUI:ArmyGround"};
            UnicodeString label = TheGameText->fetch(keys[i], &exists);
            if (!exists) label = UnicodeString(gxArmyLabelFallback(i));
            if (button->winGetText() != label) GadgetButtonSetText(button, label);
        }
    }
    if (TheGameText && !s_armyLabelsSet) {
        GameWindow *handle = TheWindowManager->winGetWindowFromId(nullptr, s_buttonHandleID);
        if (handle) GadgetButtonSetText(handle, UnicodeString(L"+"));
        // GeneralsX @bugfix Codex 15/10/2026 Group digits are literal text, not localization keys.
        for (Int group=0; group<10; ++group) {
            GameWindow *button = TheWindowManager->winGetWindowFromId(nullptr, s_buttonGroupID[group]);
            UnicodeString digit; digit.format(L"%d", group);
            if (button) GadgetButtonSetText(button, digit);
        }
        s_armyLabelsSet = TRUE;
    }
}

//-------------------------------------------------------------------------------------------------
void GroupPanelShutdown(WindowLayout *layout, void *userData)
{
    s_panelFonts.clear();s_handlePress=0;
	(void)userData;
	if (layout) {
		layout->hide(TRUE);
	}
}

//-------------------------------------------------------------------------------------------------
WindowMsgHandledType GroupPanelSystem(GameWindow *window, UnsignedInt msg,
																			 WindowMsgData mData1, WindowMsgData mData2)
{
	(void)window;
	(void)mData2;

	switch (msg) {

		case GWM_CREATE:
		{
			// GeneralsX @bugfix Android port 03/08/2026 Used to also try to
			// hide GroupRow from here (matching window->winGetWindowId()
			// against s_groupRowID), but for a WINDOWTYPE=USER window
			// winSetWindowId() only runs AFTER winCreate() has already
			// dispatched this very GWM_CREATE (see createGadget()'s "USER"
			// branch in GameWindowManagerScript.cpp), so winGetWindowId()
			// read from in here was always still the pre-assignment
			// default and never matched -- moved the actual hide to
			// ControlBar::init(), right after winCreateLayout() returns,
			// where every window in the tree is guaranteed to already have
			// its real id. cacheWidgetIDs() is still safe and useful to run
			// this early since it only hashes names, independent of
			// whether the matching windows exist yet.
			cacheWidgetIDs();
			break;
		}

		case GWM_DESTROY:
			s_armyLabelsSet = FALSE;
			break;

		case GBM_SELECTED:
		{
			GameWindow *control = (GameWindow *)mData1;
			Int controlID = control->winGetWindowId();
            if(controlID==s_buttonHandleID && s_handlePress && timeGetTime()-s_handlePress>=GROUP_HOLD_MS) {
                s_armyCollapsed=!s_armyCollapsed;s_handlePress=0;return MSG_HANDLED;
            }

            if (controlID == s_armyButtons[4]) { selectGroundArmy(); return MSG_HANDLED; }
            if (controlID == s_armyButtons[2] || controlID == s_armyButtons[3]) {
                selectAirArmy(controlID == s_armyButtons[3]);
                return MSG_HANDLED;
            }
            if (controlID == s_armyButtons[0] || controlID == s_armyButtons[1]) {
                selectArmy(controlID == s_armyButtons[1]);
                return MSG_HANDLED;
            }
			if (controlID == s_buttonHandleID) {
				s_groupRowExpanded = !s_groupRowExpanded;
				GameWindow *groupRow = TheWindowManager->winGetWindowFromId(nullptr, s_groupRowID);
				if (groupRow) {
					groupRow->winHide(!s_groupRowExpanded);
				}
				fitParentToVisibleContent();
				return MSG_HANDLED;
			}

			Int group = findGroupButtonIndex(controlID);
			if (group >= 0) {
				UnsignedInt now = timeGetTime();
				UnsignedInt elapsed = (s_pressStartMs[group] != 0) ? (now - s_pressStartMs[group]) : 0;
				s_pressStartMs[group] = 0;

				if (elapsed >= GROUP_HOLD_MS) {
					handleGroupClear(group);
				} else {
					handleGroupCommand(group, FALSE);
				}
				return MSG_HANDLED;
			}
			break;
		}

		case GBM_SELECTED_RIGHT:
		{
			GameWindow *control = (GameWindow *)mData1;
			Int controlID = control->winGetWindowId();
            if(controlID==s_buttonHandleID) { s_armyCollapsed=!s_armyCollapsed;return MSG_HANDLED; }

			Int group = findGroupButtonIndex(controlID);
			if (group >= 0) {
				handleGroupCommand(group, TRUE);
				return MSG_HANDLED;
			}
			break;
		}

	}

	return MSG_IGNORED;
}
