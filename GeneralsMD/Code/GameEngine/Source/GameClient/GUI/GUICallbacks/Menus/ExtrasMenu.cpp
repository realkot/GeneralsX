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

////////////////////////////////////////////////////////////////////////////////
//																																						//
//  (c) 2001-2003 Electronic Arts Inc.																				//
//																																						//
//////////////////////////////////////////////////////////////////////////////// 

// FILE: ExtrasMenu.cpp ////////////////////////////////////////////////////////////////////////////
// Desc:   Extras/QoL settings menu for SagePatch (camera, scroll, terrain, graphics)
///////////////////////////////////////////////////////////////////////////////////////////////////

#include "PreRTS.h"

#include "GameClient/GameClient.h"
#include "Common/GlobalData.h"
#include "Common/OptionPreferences.h"
#include "Common/NameKeyGenerator.h"
#include "GameClient/Shell.h"
#include "GameClient/GUICallbacks.h"
#include "GameClient/GameWindow.h"
#include "GameClient/GameWindowManager.h"
#include "GameClient/Gadget.h"
#include "GameClient/GadgetSlider.h"
#include "GameClient/GadgetPushButton.h"
#include "GameClient/KeyDefs.h"
#include "GameClient/WindowLayout.h"
#include "GameClient/Display.h"
#include "GameClient/View.h"
#include "GameClient/Color.h"
#include "GameClient/GameFont.h"
#include "GameClient/GadgetStaticText.h"
#include "GameLogic/GameLogic.h"
#include <cstdlib>
#include <cstring>

// Widget IDs and pointers
static NameKeyType sliderMaxCameraHeightID = NAMEKEY_INVALID;
static NameKeyType sliderMinCameraHeightID = NAMEKEY_INVALID;
static NameKeyType sliderCameraPitchID = NAMEKEY_INVALID;
static NameKeyType sliderScrollSpeedID = NAMEKEY_INVALID;
static NameKeyType sliderDrawDistanceID = NAMEKEY_INVALID;

static GameWindow *sliderMaxCameraHeight = nullptr;
static GameWindow *sliderMinCameraHeight = nullptr;
static GameWindow *sliderCameraPitch = nullptr;
static GameWindow *sliderScrollSpeed = nullptr;
static GameWindow *sliderDrawDistance = nullptr;

static OptionPreferences *pref = nullptr;

// GeneralsX @extras Codex 14/10/2026 Keep the Options modal and paused game beneath this popup.
static WindowLayout *s_extrasLayout = nullptr;
static OptionPreferences *s_optionsPreferences = nullptr;
#if defined(__ANDROID__)
static const Int GX_EXTRA_CAMERA_SCALE = 4;
#else
static const Int GX_EXTRA_CAMERA_SCALE = 1;
#endif

static void gxExtrasBackdropDraw(GameWindow *window, WinInstanceData *data)
{
    // GeneralsX @feature Codex 15/10/2026 Opaque stock Options palette and section rules.
    if (!TheDisplay) return;
    const Int w = TheDisplay->getWidth(), h = TheDisplay->getHeight();
    TheDisplay->drawFillRect(0, 0, w, h, GameMakeColor(0, 0, 0, 255));
    const UnsignedInt blue = GameMakeColor(65, 65, 190, 255);
    TheDisplay->drawOpenRect(w/10, h/20, w*8/10, h*17/20, 1.0f, blue);
    TheDisplay->drawLine(w/10, h*95/600, w*9/10, h*95/600, 1.0f, blue);
    TheDisplay->drawLine(w/10, h*425/600, w*9/10, h*425/600, 1.0f, blue);
}

void CloseExtrasMenu()
{
    WindowLayout *layout = s_extrasLayout;
    s_extrasLayout = nullptr;
    s_optionsPreferences = nullptr;
    if (!layout) return;
    GameWindow *parent = TheWindowManager->winGetWindowFromId(nullptr,
        TheNameKeyGenerator->nameToKey("ExtrasMenu.wnd:ExtrasMenuParent"));
    if (parent) TheWindowManager->winUnsetModal(parent);
    layout->runShutdown(nullptr);
    layout->destroyWindows();
    deleteInstance(layout);
    GameWindow *options = TheWindowManager->winGetWindowFromId(nullptr,
        TheNameKeyGenerator->nameToKey("OptionsMenu.wnd:OptionsMenuParent"));
    if (options) TheWindowManager->winSetFocus(options);
}

void OpenExtrasMenu(OptionPreferences *optionsPreferences)
{
    if (s_extrasLayout || !TheWindowManager) return;
    WindowLayout *layout = TheWindowManager->winCreateLayout("ExtrasMenu.wnd");
    if (!layout) {
        fprintf(stderr, "[GX-EXTRAS] missing layout; Options remains usable\n");
        return;
    }
    GameWindow *parent = TheWindowManager->winGetWindowFromId(nullptr,
        TheNameKeyGenerator->nameToKey("ExtrasMenu.wnd:ExtrasMenuParent"));
    if (!parent) { layout->destroyWindows(); deleteInstance(layout); return; }
    s_extrasLayout = layout;
    s_optionsPreferences = optionsPreferences;
    parent->winSetDrawFunc(gxExtrasBackdropDraw);
    layout->runInit(nullptr);
    layout->hide(FALSE);
    layout->bringForward();
    TheWindowManager->winSetModal(parent);
    TheWindowManager->winSetFocus(parent);
}

// Slider ranges (matching .wnd definitions)
static const Int SLIDER_MAX_CAMERA_HEIGHT_MIN = 100 * GX_EXTRA_CAMERA_SCALE;
// GeneralsX @tweak Codex 15/10/2026 900 stored units correspond to manual height 3600.
static const Int SLIDER_MAX_CAMERA_HEIGHT_MAX = 900 * GX_EXTRA_CAMERA_SCALE;
static const Int SLIDER_MIN_CAMERA_HEIGHT_MIN = 50;
static const Int SLIDER_MIN_CAMERA_HEIGHT_MAX = 300;
static const Int SLIDER_CAMERA_PITCH_MIN = 20;
static const Int SLIDER_CAMERA_PITCH_MAX = 60;
static const Int SLIDER_SCROLL_SPEED_MIN = 1;
static const Int SLIDER_SCROLL_SPEED_MAX = 200;
static const Int SLIDER_DRAW_DISTANCE_MIN = 100;
static const Int SLIDER_DRAW_DISTANCE_MAX = 200;

//-------------------------------------------------------------------------------------------------
void ExtrasMenuInit(WindowLayout *layout, void *userData)
{
	fprintf(stderr, "[GX-EXTRAS] initialize popup\n");
	sliderMaxCameraHeightID = TheNameKeyGenerator->nameToKey("ExtrasMenu.wnd:SliderMaxCameraHeight");
	sliderMinCameraHeightID = TheNameKeyGenerator->nameToKey("ExtrasMenu.wnd:SliderMinCameraHeight");
	sliderCameraPitchID = TheNameKeyGenerator->nameToKey("ExtrasMenu.wnd:SliderCameraPitch");
	sliderScrollSpeedID = TheNameKeyGenerator->nameToKey("ExtrasMenu.wnd:SliderScrollSpeed");
	sliderDrawDistanceID = TheNameKeyGenerator->nameToKey("ExtrasMenu.wnd:SliderDrawDistance");

	sliderMaxCameraHeight = TheWindowManager->winGetWindowFromId(nullptr, sliderMaxCameraHeightID);
	sliderMinCameraHeight = TheWindowManager->winGetWindowFromId(nullptr, sliderMinCameraHeightID);
	sliderCameraPitch = TheWindowManager->winGetWindowFromId(nullptr, sliderCameraPitchID);
	sliderScrollSpeed = TheWindowManager->winGetWindowFromId(nullptr, sliderScrollSpeedID);
	sliderDrawDistance = TheWindowManager->winGetWindowFromId(nullptr, sliderDrawDistanceID);

	pref = NEW OptionPreferences;

	// Populate sliders from current settings
	if (sliderMaxCameraHeight) {
		Int val = (Int)(pref->getMaxCameraHeight() * GX_EXTRA_CAMERA_SCALE);
		GadgetSliderSetPosition(sliderMaxCameraHeight, val);
	}
	if (sliderMinCameraHeight) {
		Int val = (Int)pref->getMinCameraHeight();
		GadgetSliderSetPosition(sliderMinCameraHeight, val);
	}
	if (sliderCameraPitch) {
		Int val = (Int)pref->getCameraPitch();
		GadgetSliderSetPosition(sliderCameraPitch, val);
	}
	if (sliderScrollSpeed) {
		Int val = (Int)(pref->getScrollFactor() * 100.0f);
		GadgetSliderSetPosition(sliderScrollSpeed, val);
	}
	if (sliderDrawDistance) {
		Int val = (Int)(pref->getTerrainDrawDistanceScale() * 100.0f);
		GadgetSliderSetPosition(sliderDrawDistance, val);
	}
    // GeneralsX @ui Codex 14/10/2026 Literal labels and fonts remain readable with high render resolution.
    const char *language = getenv("GENERALSX_TEXT_LANGUAGE");
    const Bool russian = language && strcmp(language, "russian") == 0;
    const char *names[] = {"LabelTitle", "LabelMaxCameraHeight", "LabelMinCameraHeight", "LabelCameraPitch", "LabelScrollSpeed", "LabelDrawDistance"};
    const wchar_t *english[] = {L"EXTRA OPTIONS", L"Maximum camera height", L"Minimum camera height", L"Camera pitch", L"Scroll speed", L"Terrain draw distance"};
    const wchar_t *ru[] = {L"ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ", L"Максимальная высота камеры", L"Минимальная высота камеры", L"Наклон камеры", L"Скорость прокрутки", L"Дальность отрисовки"};
    for (Int i=0; i<6; ++i) {
        AsciiString id; id.format("ExtrasMenu.wnd:%s", names[i]);
        GameWindow *label = TheWindowManager->winGetWindowFromId(nullptr, TheNameKeyGenerator->nameToKey(id));
        if (label) {
            GadgetStaticTextSetText(label, UnicodeString(russian ? ru[i] : english[i]));
        }
    }
    const char *buttons[] = {"ButtonBack", "ButtonDefaults", "ButtonAccept"};
    const wchar_t *enButtons[] = {L"Cancel", L"Defaults", L"Apply"};
    const wchar_t *ruButtons[] = {L"Отмена", L"По умолчанию", L"Применить"};
    for (Int i=0; i<3; ++i) {
        AsciiString id; id.format("ExtrasMenu.wnd:%s", buttons[i]);
        GameWindow *button = TheWindowManager->winGetWindowFromId(nullptr, TheNameKeyGenerator->nameToKey(id));
        if (button) {
            GadgetButtonSetText(button, UnicodeString(russian ? ruButtons[i] : enButtons[i]));
        }
    }

}

//-------------------------------------------------------------------------------------------------
void ExtrasMenuUpdate(WindowLayout *layout, void *userData)
{
}

//-------------------------------------------------------------------------------------------------
void ExtrasMenuShutdown(WindowLayout *layout, void *userData)
{
	sliderMaxCameraHeight = nullptr;
	sliderMinCameraHeight = nullptr;
	sliderCameraPitch = nullptr;
	sliderScrollSpeed = nullptr;
	sliderDrawDistance = nullptr;

	if (pref) {
		delete pref;
		pref = nullptr;
	}
}

//-------------------------------------------------------------------------------------------------
static void saveExtras()
{
	if (!pref || !TheWritableGlobalData || !sliderMaxCameraHeight || !sliderMinCameraHeight
        || !sliderCameraPitch || !sliderScrollSpeed || !sliderDrawDistance) return;

	Int val;

	val = max(SLIDER_MAX_CAMERA_HEIGHT_MIN, min(SLIDER_MAX_CAMERA_HEIGHT_MAX, GadgetSliderGetPosition(sliderMaxCameraHeight))) / GX_EXTRA_CAMERA_SCALE;
    val = max(val, max(SLIDER_MIN_CAMERA_HEIGHT_MIN, min(SLIDER_MIN_CAMERA_HEIGHT_MAX, GadgetSliderGetPosition(sliderMinCameraHeight))));
	if (val > 0) {
		TheWritableGlobalData->m_maxCameraHeight = (Real)val;
		AsciiString prefString;
		prefString.format("%d", val);
		(*pref)["MaxCameraHeight"] = prefString;
	}

	val = max(SLIDER_MIN_CAMERA_HEIGHT_MIN, min(SLIDER_MIN_CAMERA_HEIGHT_MAX, GadgetSliderGetPosition(sliderMinCameraHeight)));
	if (val > 0) {
		TheWritableGlobalData->m_minCameraHeight = (Real)val;
		AsciiString prefString;
		prefString.format("%d", val);
		(*pref)["MinCameraHeight"] = prefString;
	}

	val = max(SLIDER_CAMERA_PITCH_MIN, min(SLIDER_CAMERA_PITCH_MAX, GadgetSliderGetPosition(sliderCameraPitch)));
	if (val > 0) {
		TheWritableGlobalData->m_cameraPitch = (Real)val;
		AsciiString prefString;
		prefString.format("%d", val);
		(*pref)["CameraPitch"] = prefString;
	}

	val = max(SLIDER_SCROLL_SPEED_MIN, min(SLIDER_SCROLL_SPEED_MAX, GadgetSliderGetPosition(sliderScrollSpeed)));
	if (val > 0) {
		TheWritableGlobalData->m_keyboardScrollFactor = val / 100.0f;
		AsciiString prefString;
		prefString.format("%d", val);
		(*pref)["ScrollFactor"] = prefString;
	}

	val = max(SLIDER_DRAW_DISTANCE_MIN, min(SLIDER_DRAW_DISTANCE_MAX, GadgetSliderGetPosition(sliderDrawDistance)));
	if (val > 0) {
		TheWritableGlobalData->m_terrainDrawDistanceScale = val / 100.0f;
		AsciiString prefString;
		prefString.format("%d", val);
		(*pref)["TerrainDrawDistanceScale"] = prefString;
	}
    if (s_optionsPreferences) {
        const char *keys[] = {"MaxCameraHeight", "MinCameraHeight", "CameraPitch", "ScrollFactor", "TerrainDrawDistanceScale"};
        for (const char *key : keys) (*s_optionsPreferences)[key] = (*pref)[key];
    }
    if (TheTacticalView) {
        TheTacticalView->setCameraHeightAboveGroundLimitsToDefault();
        if (TheGameLogic && TheGameLogic->isInInteractiveGame() && !TheTacticalView->isDoingScriptedCamera()) {
            TheTacticalView->setPitch(DEG_TO_RADF(TheWritableGlobalData->m_cameraPitch));
        }
    }

}

//-------------------------------------------------------------------------------------------------
static void setDefaults()
{
	if (sliderMaxCameraHeight)
		GadgetSliderSetPosition(sliderMaxCameraHeight, 500 * GX_EXTRA_CAMERA_SCALE);
	if (sliderMinCameraHeight)
		GadgetSliderSetPosition(sliderMinCameraHeight, 80);
	if (sliderCameraPitch)
		GadgetSliderSetPosition(sliderCameraPitch, 37);
	if (sliderScrollSpeed)
		GadgetSliderSetPosition(sliderScrollSpeed, 100);
	if (sliderDrawDistance)
		GadgetSliderSetPosition(sliderDrawDistance, 105);
}

//-------------------------------------------------------------------------------------------------
WindowMsgHandledType ExtrasMenuSystem(GameWindow *window, UnsignedInt msg,
																				WindowMsgData mData1, WindowMsgData mData2)
{
	static NameKeyType buttonBack = NAMEKEY_INVALID;
	static NameKeyType buttonDefaults = NAMEKEY_INVALID;
	static NameKeyType buttonAccept = NAMEKEY_INVALID;

	switch (msg) {

		case GWM_CREATE:
		{
			buttonBack = TheNameKeyGenerator->nameToKey("ExtrasMenu.wnd:ButtonBack");
			buttonDefaults = TheNameKeyGenerator->nameToKey("ExtrasMenu.wnd:ButtonDefaults");
			buttonAccept = TheNameKeyGenerator->nameToKey("ExtrasMenu.wnd:ButtonAccept");
			break;
		}

		case GWM_DESTROY:
			break;

		case GWM_INPUT_FOCUS:
		{
			if (mData1 == TRUE)
				*(Bool *)mData2 = TRUE;
			return MSG_HANDLED;
		}

		case GBM_SELECTED:
		{
			GameWindow *control = (GameWindow *)mData1;
			Int controlID = control->winGetWindowId();

			if (controlID == buttonBack) {
				CloseExtrasMenu();
			}
			else if (controlID == buttonAccept) {
				saveExtras();
				if (pref) {
					pref->write();
				}
				CloseExtrasMenu();
			}
			else if (controlID == buttonDefaults) {
				setDefaults();
			}
			break;
		}

		default:
			break;
	}

	return MSG_IGNORED;
}

//-------------------------------------------------------------------------------------------------
WindowMsgHandledType ExtrasMenuInput(GameWindow *window, UnsignedInt msg,
																				WindowMsgData mData1, WindowMsgData mData2)
{
	switch (msg) {

		case GWM_CHAR:
		{
			UnsignedByte key = mData1;
			UnsignedByte state = mData2;

			switch (key) {

				case KEY_ESC:
				{
					if (BitIsSet(state, KEY_STATE_UP)) {
						CloseExtrasMenu();
					}
					return MSG_HANDLED;
				}

			}
		}

	}

	return MSG_IGNORED;
}
