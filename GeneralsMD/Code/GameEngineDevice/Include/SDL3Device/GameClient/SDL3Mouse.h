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

/*
** SDL3Mouse.h
**
** SDL3-based mouse implementation for Linux builds.
**
** TheSuperHackers @feature CnC_Generals_Linux 10/02/2026 Bender
** Replaces Win32Mouse/Win32DIMouse with SDL3 mouse APIs for Linux.
*/

#pragma once

#ifndef _WIN32

// SYSTEM INCLUDES
#include <SDL3/SDL.h>
#include <SDL3_image/SDL_image.h>
#include <array>
#include <deque>
#if defined(__APPLE__)
#include <TargetConditionals.h>
#endif

// USER INCLUDES
#include "GameClient/Mouse.h"

// FORWARD REFERENCES
struct AnimatedCursor;

// SDL3Mouse ------------------------------------------------------------------
/** Mouse interface using SDL3 APIs for Linux */
//-----------------------------------------------------------------------------
class SDL3Mouse : public Mouse
{
public:
	SDL3Mouse(SDL_Window* window);
	virtual ~SDL3Mouse(void);

	// SubsystemInterface
	virtual void init(void);
	virtual void reset(void);
	virtual void update(void);
	virtual void initCursorResources(void);

	// Mouse interface
	virtual void setCursor(MouseCursor cursor);
	virtual void setVisibility(Bool visible);
	virtual void loseFocus();
	virtual void regainFocus();
	// GeneralsX @feature Codex 14/10/2026 Track the active input source, not just the OS.
	Bool hasContinuousPointer() const override;
	void getPointerClickToleranceScale(Real &x, Real &y) const;
	Bool hasPhysicalPointer() const { return m_physicalPointer; }
	void setPhysicalPointer(Bool active);
	void cancelInput();
	void suppressStream(Bool suppressed) { m_streamSuppressed = suppressed; }
	static void scaleMouseCoordinates(int rawX, int rawY, Uint32 windowID, int& scaledX, int& scaledY);

#if (defined(TARGET_OS_IPHONE) && TARGET_OS_IPHONE) || defined(__ANDROID__)
	// GeneralsX @bugfix Codex 14/10/2026 A physical mouse gets the retail stream;
	// touch owns its own gestures and must not leave a persistent pointer heartbeat.
	virtual void createStreamMessages() override;

	// GeneralsX @bugfix Android port 06/09/2026 Where the last finger touched.
	//
	// Writes ONLY m_currMouse.pos, the value getMouseStatus() returns. That field
	// is read by preview drawing -- InGameUI::handleRadiusCursor() for the ability
	// radius, InGameUI::handleBuildPlacements() for the placement icon, both called
	// once a frame from InGameUI::preDraw() -- and with nothing writing it on a
	// touch device they drew at (0,0), in the top-left corner.
	//
	// It deliberately does NOT emit MSG_RAW_MOUSE_POSITION. That message is the
	// event that drives GUI hilite, the selection box, and the engine's edge-scroll
	// anchor; two earlier attempts at this published one and had to be reverted,
	// because a position event arriving every frame gives the game a cursor that
	// outlives the finger -- menu buttons hilited with nothing on screen, and the
	// map scrolling by itself from a point left near an edge. The position and the
	// event are different things and only the first one is wanted here.
	void setTouchCursorPos(Int x, Int y);

	// GeneralsX @feature Android port 05/10/2026 Mouse and touchpad mode (GXMouseMode.h, issue #39).
	// The touchpad gestures (SDL3GameEngine.cpp) are mouse events with this id, added with
	// addSDLEvent() like a real mouse's. A real mouse is drawn by Android; a touchpad pointer is
	// not, so the game draws it while the last pointer input came from the touchpad.
	static const SDL_MouseID TOUCHPAD_MOUSE_ID = (SDL_MouseID)0xFFFFFFFDu;
	virtual void draw() override;
#endif

	// SDL3-specific methods
	// Fighter19 pattern: addSDLEvent() accepts raw SDL_Event directly
	// GeneralsX @refactor felipebraz 16/02/2026 Switch to fighter19 event model
	void addSDLEvent(SDL_Event *event);
	
	// Legacy methods (kept for compatibility, will be removed after validation)
	void addSDL3MouseMotionEvent(const SDL_MouseMotionEvent& event);
	void addSDL3MouseButtonEvent(const SDL_MouseButtonEvent& event);
	void addSDL3MouseWheelEvent(const SDL_MouseWheelEvent& event);

protected:
	virtual void capture(void);
	virtual void releaseCapture(void);
	virtual UnsignedByte getMouseEvent(MouseIO *result, Bool flush);

private:
	Bool m_physicalPointer = FALSE;
	Bool m_streamSuppressed = FALSE;
	Real m_wheelRemainder = 0;
	// Event translation from SDL_Event (raw format)
	// GeneralsX @refactor felipebraz 16/02/2026 Unified translation method
	void translateEvent(const SDL_Event &event, MouseIO *result);

	// Load cursor from ANI file (fighter19 pattern)
	// GeneralsX @bugfix BenderAI 22/02/2026 Port fighter19 cursor loading
	AnimatedCursor* loadCursorFromFile(const char* filepath);

	// Legacy translation methods (kept for compatibility)
	void translateMotionEvent(const SDL_MouseMotionEvent& event, MouseIO *result);
	void translateButtonEvent(const SDL_MouseButtonEvent& event, MouseIO *result);
	void translateWheelEvent(const SDL_MouseWheelEvent& event, MouseIO *result);

	// GeneralsX @input Codex 14/10/2026 Preserve button edges even during a motion burst.
	// Keep the previous device object layout; the non-lossy queue lives in the adapter implementation.
	static const UnsignedInt MAX_SDL3_MOUSE_EVENTS = 256;
	SDL_Event m_eventBuffer[MAX_SDL3_MOUSE_EVENTS];
	UnsignedInt m_nextFreeIndex;
	UnsignedInt m_nextGetIndex;

	SDL_Window* m_Window;
	Bool m_IsCaptured;
	Bool m_IsVisible;
	Bool m_LostFocus;             // GeneralsX @bugfix felipebraz 18/02/2026 Track window focus state
	
	// Track button states for click detection
	Uint32 m_LeftButtonDownTime;
	Uint32 m_RightButtonDownTime;
	Uint32 m_MiddleButtonDownTime;
	UnsignedInt m_LastFrameNumber;       // GeneralsX @bugfix felipebraz 18/02/2026 Frame tracking for determinism
	
	ICoord2D m_LeftButtonDownPos;
	ICoord2D m_RightButtonDownPos;
	ICoord2D m_MiddleButtonDownPos;
	
	// GeneralsX @bugfix BenderAI 22/02/2026 Add cursor animation tracking
	Int m_directionFrame;         ///< current frame of directional cursor (from 0 points up)

	// GeneralsX @feature Android port 05/10/2026 The pointer was last moved by the touchpad, not a
	// real mouse: draw() draws it. See TOUCHPAD_MOUSE_ID.
	Bool m_touchpadPointer;
};

#endif // !_WIN32
