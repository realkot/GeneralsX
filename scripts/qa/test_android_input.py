#!/usr/bin/env python3
"""Compile production keyboard code and exercise input boundaries using small engine fakes.

Requires g++ and the SDL 3.4.2 include directory. No renderer, game data, or device.
This does NOT test Android event delivery or the full engine translator chain.
"""
import argparse
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--sdl-include', type=Path, required=True)
parser.add_argument('--cxx', default='g++')
args = parser.parse_args()
out = ROOT / 'build/input-tests'
out.mkdir(parents=True, exist_ok=True)

def put(path, text):
    p = out / path
    p.parent.mkdir(parents=True, exist_ok=True)
    if path.endswith('_test.cpp'):
        text='namespace GXInputTrace { template<class... T> void record(T...) {} }\n'+(ROOT/'Core/GameEngine/Include/Common/GXPointerButtons.h').read_text()+'\n'+text
    p.write_text(text, encoding='utf-8')

def function(text, signature):
    start = text.index(signature)
    brace = text.index('{', start)
    depth = 1
    end = brace + 1
    # Functions below have no unmatched braces in comments or strings.
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]

put('Lib/BaseType.h', '''#pragma once
using Bool=bool; using Int=int; using UnsignedInt=unsigned;
using UnsignedByte=unsigned char; using UnsignedShort=unsigned short;
#define CPP_11(x) x
inline unsigned timeGetTime() { return 12345; }
''')
put('GameClient/Keyboard.h', '''#pragma once
#include <cstring>
#include "GameClient/KeyDefs.h"
struct KeyboardIO {
 enum {STATUS_UNUSED=0, STATUS_USED=1};
 unsigned char key=0, status=0; unsigned short state=0; unsigned keyDownTimeMsec=0;
};
class Keyboard {
protected:
 KeyboardIO m_keys[256]{}, m_keyStatus[KEY_COUNT]{};
 unsigned short m_modifiers=0;
public:
 virtual ~Keyboard()=default;
 virtual void init() {} virtual void reset() {} virtual void update() {}
 void resetKeys() { std::memset(m_keys,0,sizeof(m_keys)); std::memset(m_keyStatus,0,sizeof(m_keyStatus)); m_modifiers=0; }
 KeyboardIO* getFirstKey() { return m_keys; }
};
''')
put('Common/MessageStream.h', '''#pragma once
#include <vector>
struct GameMessage {
 enum {MSG_RAW_KEY_UP}; std::vector<int> args;
 void appendIntegerArgument(int i) { args.push_back(i); }
};
struct MessageStream {
 std::vector<GameMessage> messages;
 GameMessage* appendMessage(int) { messages.emplace_back(); return &messages.back(); }
};
extern MessageStream* TheMessageStream;
''')
keyboard = ROOT/'GeneralsMD/Code/GameEngineDevice/Source/SDL3Device/GameClient/SDL3Keyboard.cpp'
put('keyboard_test.cpp', f'''#include <cassert>
#include <set>
#include <iostream>
#include "{keyboard.as_posix()}"
MessageStream stream; MessageStream* TheMessageStream=&stream;
SDL_Keymod mods=0;
extern "C" SDL_Keymod SDL_GetModState() {{ return mods; }}
struct TestKeyboard : SDL3Keyboard {{
 using SDL3Keyboard::getKey;
 using SDL3Keyboard::translateScanCodeToKeyVal;
 void hold(int key) {{ m_keyStatus[key].state=KEY_STATE_DOWN; }}
 bool held(int key) {{ return m_keyStatus[key].state & KEY_STATE_DOWN; }}
}};
int main() {{
 TestKeyboard k;
 assert(k.translateScanCodeToKeyVal(SDL_SCANCODE_KP_0)==0x52);
 assert(k.translateScanCodeToKeyVal(SDL_SCANCODE_A)==0x1e);
 assert(k.translateScanCodeToKeyVal(SDL_SCANCODE_NONUSBACKSLASH)==0x56);
 assert(k.translateScanCodeToKeyVal(SDL_SCANCODE_AC_BACK)==KEY_ESC);
 std::set<int> mapped;
 for(int s=SDL_SCANCODE_A; s<=SDL_SCANCODE_NONUSBACKSLASH; ++s) {{
   int key=k.translateScanCodeToKeyVal(static_cast<SDL_Scancode>(s));
   if(key) assert(mapped.insert(key).second);
 }}
 SDL_Event e{{}}; e.type=SDL_EVENT_KEY_DOWN; e.key.down=true;
 e.key.scancode=SDL_SCANCODE_UNKNOWN; k.addSDLEvent(&e);
 e.key.scancode=SDL_SCANCODE_KP_0; k.addSDLEvent(&e);
 e.key.scancode=SDL_SCANCODE_A; e.key.repeat=true; k.addSDLEvent(&e);
 e.key.repeat=false; k.addSDLEvent(&e);
 KeyboardIO key;
 k.getKey(&key); assert(key.key==KEY_KP0 && key.state==KEY_STATE_DOWN);
 k.getKey(&key); assert(key.key==KEY_A && key.keyDownTimeMsec==12345);
 k.getKey(&key); assert(key.key==KEY_NONE);
 e.type=SDL_EVENT_KEY_UP; e.key.down=false; k.addSDLEvent(&e);
 k.getKey(&key); assert(key.key==KEY_A && key.state==KEY_STATE_UP);
 mods=SDL_KMOD_CAPS; assert(k.getCapsState()); mods=0; assert(!k.getCapsState());
 k.hold(KEY_LCTRL); k.hold(KEY_UP); k.reset();
 assert(!k.held(KEY_LCTRL) && !k.held(KEY_UP));
 assert(stream.messages.size()==2);
 for(auto &m:stream.messages) assert(m.args.size()==2 && m.args[1]==KEY_STATE_UP);
 assert(k.getKeyboard()!=nullptr);
 k.hold(KEY_UP);
 e.type=SDL_EVENT_KEY_DOWN;e.key.down=true;e.key.scancode=SDL_SCANCODE_A;
 for(int i=0;i<255;++i) k.addSDLEvent(&e);
 e.type=SDL_EVENT_KEY_UP;e.key.down=false;e.key.scancode=SDL_SCANCODE_UP;
 k.addSDL3KeyEvent(e.key);
 k.getKey(&key);assert(key.key==KEY_UP && key.state==KEY_STATE_UP && !k.held(KEY_UP));
 std::cout<<"PASS keyboard: DIK values, uniqueness, unknown events, keypad, repeats, release, caps, reset\\n";
}}
''')
mouse = (ROOT/'GeneralsMD/Code/GameEngineDevice/Source/SDL3Device/GameClient/SDL3Mouse.cpp').read_text()
wheel = function(mouse, 'void SDL3Mouse::translateWheelEvent')
heartbeat = function(mouse, 'void SDL3Mouse::createStreamMessages')
put('mouse_test.cpp', '''#include <SDL3/SDL.h>
#include <cassert>
#include <iostream>
using Int=int; using Real=float;
constexpr int MOUSE_WHEEL_DELTA=120, MBS_None=0;
struct Point { int x=0,y=0; };
struct MouseIO { Point pos,deltaPos; int time=0,wheelPos=0,leftState=0,rightState=0,middleState=0; };
extern "C" SDL_MouseButtonFlags SDL_GetMouseState(float*x,float*y) { *x=2; *y=3; return 0; }
bool virtualPointer=false; bool GXMouseModeEnabled(){return virtualPointer;}
struct Mouse { int streams=0; void createStreamMessages(){++streams;} };
struct SDL3Mouse: Mouse {
 bool m_physicalPointer=false,m_LostFocus=false,m_streamSuppressed=false;
 Real m_wheelRemainder=0;
 void translateWheelEvent(const SDL_MouseWheelEvent&,MouseIO*);
 void createStreamMessages();
};
''' + wheel + '\n' + heartbeat + '''
int main() {
 SDL3Mouse m; MouseIO result; SDL_MouseWheelEvent e{};
 e.y=1.0f/240; int total=0;
 for(int i=0;i<240;++i) { m.translateWheelEvent(e,&result); total+=result.wheelPos; }
 assert(total==120);
 e.y=1; e.direction=SDL_MOUSEWHEEL_FLIPPED; m.translateWheelEvent(e,&result); assert(result.wheelPos==-120);
 m.createStreamMessages(); assert(m.streams==0);
 virtualPointer=true; m.createStreamMessages(); assert(m.streams==1);
 virtualPointer=false; m.streams=0;
 m.m_physicalPointer=true; m.createStreamMessages(); assert(m.streams==1);
 m.m_streamSuppressed=true; m.createStreamMessages(); assert(m.streams==1);
 m.m_streamSuppressed=false; m.m_LostFocus=true; m.createStreamMessages(); assert(m.streams==1);
 std::cout<<"PASS mouse: fractional wheel, reversed wheel, touch/mouse/pan/focus heartbeat gates\\n";
}
''')
panel = (ROOT/'GeneralsMD/Code/GameEngine/Source/GameClient/GUI/GUICallbacks/GroupPanel.cpp').read_text()
put('selection_test.cpp', '''#include <cassert>
#include <iostream>
using Bool=bool;
enum { KINDOF_DOZER, KINDOF_HARVESTER, KINDOF_IGNORES_SELECT_ALL, KINDOF_STRUCTURE };
struct KindOfMaskType { unsigned bits=0; void set(int bit){bits|=1<<bit;} };
bool enabled=true; bool canSelectArmy(){return enabled;}
struct UI {
 int selected=9, clears=0, screens=0, maps=0; unsigned excluded=0;
 void deselectAllDrawables(){selected=0;++clears;}
 void selectAllUnitsByTypeAcrossScreen(KindOfMaskType,KindOfMaskType e){assert(!selected);++screens;excluded=e.bits;}
 void selectAllUnitsByTypeAcrossMap(KindOfMaskType,KindOfMaskType e){assert(!selected);++maps;excluded=e.bits;selected=9;}
} ui, *TheInGameUI=&ui;
''' + function(panel, 'static void selectArmy') + '''
int main(){
 selectArmy(true); assert(ui.maps==1 && ui.selected==9);
 selectArmy(false); assert(ui.maps==1 && ui.screens==1 && ui.selected==0);
 selectArmy(false); assert(ui.maps==1 && ui.screens==2 && ui.selected==0);
 assert(ui.excluded==15 && ui.clears==3);
 enabled=false; selectArmy(true); assert(ui.maps==1 && ui.clears==3);
 std::cout<<"PASS army: explicit scopes, map-to-empty-screen replacement, filters, disabled state\\n";
}
''')
includes = [out, args.sdl_include, ROOT/'GeneralsMD/Code/GameEngineDevice/Include',
            ROOT/'GeneralsMD/Code/GameEngine/Include', ROOT/'GeneralsMD/Code/CompatLib/Include']
engine = (ROOT/'GeneralsMD/Code/GameEngineDevice/Source/SDL3GameEngine.cpp').read_text()
put('router_test.cpp', '''#include <SDL3/SDL.h>
#include <cassert>
#include <iostream>
#define __ANDROID__ 1
using Bool=bool; using Int=int;
constexpr bool TRUE=true,FALSE=false;
struct Mouse { virtual ~Mouse()=default; };
struct SDL3Mouse:Mouse {
 bool active=false,suppressed=false; int x=0,y=0;
 bool hasPhysicalPointer(){return active;} void setPhysicalPointer(bool b){active=b;}
 void suppressStream(bool b){suppressed=b;} void setPosition(int a,int b){x=a;y=b;}
 static void scaleMouseCoordinates(int,int,Uint32,int&,int&);
} mouse;
Mouse* TheMouse=&mouse;
struct TouchState{enum{IDLE,MOMENTUM,SELECTING};int phase=IDLE;} s_touch;
struct Pad {int fingers=0;} s_pad;
bool s_middlePan=false; float s_middleX=0,s_middleY=0;
SDL_MouseButtonFlags s_physicalButtons=0;
struct Display {
 int getWidth(){return 800;} int getHeight(){return 600;}
 bool getViewportRect(int&x,int&y,int&w,int&h)const{x=100;y=50;w=1600;h=1200;return true;}
} display,*TheDisplay=&display;
struct Logic { bool paused=false; bool isInInteractiveGame(){return true;} bool isGamePaused(){return paused;} } logic,*TheGameLogic=&logic;
struct Look {void cancelScrolling(){}} look,*TheLookAtTranslator=&look;
bool ui=false,script=false,captured=false; int pans=0,cancels=0;
float fromX=0,toX=0;
bool touchPointBelongsToUi(float,float){return ui;} bool gxScriptOwnsCamera(){return script;}
void cancelPointerGesture(){++cancels;s_middlePan=false;s_touch.phase=TouchState::IDLE;mouse.suppressed=false;}
void applyCameraPan(float x,float,float xx,float){++pans;fromX=x;toX=xx;}
extern "C" bool SDL_GetWindowSize(SDL_Window*,int*w,int*h){*w=1800;*h=1300;return true;}
extern "C" SDL_WindowID SDL_GetWindowID(SDL_Window*){return 1;}
extern "C" SDL_Window* SDL_GetWindowFromID(SDL_WindowID){return reinterpret_cast<SDL_Window*>(1);}
extern "C" bool SDL_CaptureMouse(bool b){captured=b;return true;}
''' + function(mouse, 'void SDL3Mouse::scaleMouseCoordinates') + '\n' +
function(engine, 'Bool handlePhysicalMouse') + '''
int main(){
 SDL_Event e{}; SDL_Window*w=reinterpret_cast<SDL_Window*>(1);
 e.type=SDL_EVENT_MOUSE_MOTION; e.motion.which=SDL_TOUCH_MOUSEID;
 assert(handlePhysicalMouse(e,w) && !mouse.active);
 e.motion.which=7; s_touch.phase=TouchState::SELECTING;
 assert(handlePhysicalMouse(e,w) && !mouse.active);
 s_touch.phase=TouchState::IDLE;
 assert(!handlePhysicalMouse(e,w) && mouse.active);
 e={};e.type=SDL_EVENT_MOUSE_BUTTON_DOWN;e.button.button=SDL_BUTTON_MIDDLE;e.button.down=true;
 e.button.which=7;e.button.x=900;e.button.y=650;
 assert(handlePhysicalMouse(e,w) && s_middlePan && mouse.suppressed && captured);
 assert(s_middleX==400 && s_middleY==300);
 e={};e.type=SDL_EVENT_MOUSE_MOTION;e.motion.which=7;e.motion.x=1100;e.motion.y=650;
 assert(handlePhysicalMouse(e,w));assert(pans==1 && fromX==400 && toX==500);
 logic.paused=true;assert(handlePhysicalMouse(e,w));assert(pans==1);logic.paused=false;
 e={};e.type=SDL_EVENT_MOUSE_BUTTON_UP;e.button.button=SDL_BUTTON_MIDDLE;
 e.button.which=7;e.button.x=1100;e.button.y=650;
 assert(!handlePhysicalMouse(e,w) && !s_middlePan && !mouse.suppressed && !captured);
 assert(e.type==SDL_EVENT_MOUSE_MOTION && mouse.x==500 && mouse.y==300);
 assert(s_physicalButtons==0);
 ui=true;e={};e.type=SDL_EVENT_MOUSE_BUTTON_DOWN;e.button.button=SDL_BUTTON_MIDDLE;e.button.down=true;e.button.which=7;
 assert(handlePhysicalMouse(e,w) && !s_middlePan);
 std::cout<<"PASS router: synthetic events, held touch ownership, MMB pan/release, pause/UI gates, viewport offsets\\n";
}
''')
ingame = (ROOT/'GeneralsMD/Code/GameEngine/Source/GameClient/InGameUI.cpp').read_text()
put('filter_test.cpp', '''#include <cassert>
#include <vector>
#include <iostream>
using Bool=bool;constexpr bool TRUE=true,FALSE=false;
struct Mask{unsigned bits=0;};
struct Drawable;
struct Object {
 unsigned kinds=0;bool local=true,contained=false,dead=false,mass=true,offmap=false;
 Drawable*draw=nullptr;
 bool isKindOfMulti(Mask required,Mask excluded)const{return (kinds&required.bits)==required.bits && !(kinds&excluded.bits);}
 bool isLocallyControlled()const{return local;} bool isContained()const{return contained;}
 Drawable*getDrawable()const{return draw;} bool isEffectivelyDead()const{return dead;}
 bool isMassSelectable()const{return mass;} bool isOffMap()const{return offmap;}
};
struct Drawable {Object*object=nullptr;bool selected=false;Object*getObject(){return object;}bool isSelected(){return selected;}};
struct KindOfSelectionData{Mask m_mustbeSet,m_mustbeClear;std::vector<Drawable*>newlySelectedDrawables;};
struct UnicodeString {void format(const char*,int){}const char*str(){return "";}};
struct Text{UnicodeString fetch(const char*){return {};}} text,*TheGameText=&text;
struct UI {
 int count=0,cap=0;bool warning=false;
 int getMaxSelectCount(){return cap;}int getSelectCount(){return count;}
 bool getDisplayedMaxWarning(){return warning;}void setDisplayedMaxWarning(bool w){warning=w;}
 void message(UnicodeString){}void selectDrawable(Drawable*d){d->selected=true;++count;}
} ui,*TheInGameUI=&ui;
''' + function(ingame, 'static Bool kindOfUnitSelection') + '''
int main(){
 KindOfSelectionData data;data.m_mustbeClear.bits=15;
 Object obj;Drawable draw;obj.draw=&draw;draw.object=&obj;
 for(unsigned kind:{1u,2u,4u,8u}){obj.kinds=kind;assert(!kindOfUnitSelection(&draw,&data));}
 obj.kinds=0;
 for(bool*flag:{&obj.contained,&obj.dead,&obj.offmap}){*flag=true;assert(!kindOfUnitSelection(&draw,&data));*flag=false;}
 obj.local=false;assert(!kindOfUnitSelection(&draw,&data));obj.local=true;
 obj.mass=false;assert(!kindOfUnitSelection(&draw,&data));obj.mass=true;
 ui.cap=1;ui.count=1;assert(!kindOfUnitSelection(&draw,&data));assert(ui.warning);
 ui.count=0;assert(kindOfUnitSelection(&draw,&data));assert(ui.count==1 && data.newlySelectedDrawables.size()==1);
 assert(!kindOfUnitSelection(&draw,&data));assert(!kindOfUnitSelection(nullptr,&data));
 std::cout<<"PASS retail selection predicate: excluded kinds, ownership, contained/dead/offmap, mass selection, cap, duplicates\\n";
}
''')
for name in ['keyboard', 'mouse', 'selection', 'router', 'filter']:
    cmd = [args.cxx, '-std=c++17', '-Werror=return-type']
    for inc in includes:
        cmd += ['-I', str(inc)]
    binary = out/(name+'_test')
    subprocess.run(cmd+[str(out/(name+'_test.cpp')), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)

# Catch malformed WND edits, duplicated IDs and overlaps in the authored button row.
wnd = (ROOT/'android/app/src/main/assets/gamedata/Window/GroupPanel.wnd').read_text()
names = re.findall(r'NAME = "(GroupPanel.wnd:[^"]+)";', wnd)
assert len(names) == len(set(names))
assert len(re.findall(r'^\s*WINDOW\s*$',wnd,re.M)) == len(re.findall(r'^\s*END\s*$',wnd,re.M))
rects=[]
for name in ['ButtonHandle','ArmyScreen','ArmyMap','ArmyPlanes','ArmyHelicopters','ArmyGround']:
    block=wnd[:wnd.index(f'NAME = "GroupPanel.wnd:{name}"')].rsplit('SCREENRECT = ',1)[1]
    x1,y1,x2,y2=map(int,re.search(r'UPPERLEFT: (\d+) (\d+), BOTTOMRIGHT: (\d+) (\d+)',block).groups())
    assert 0<=x1<x2<=448 and 214<=y1<y2<=446
    rects.append((x1,y1,x2,y2))
for i,a in enumerate(rects):
 for b in rects[i+1:]:assert a[2]<=b[0] or b[2]<=a[0] or a[3]<=b[1] or b[3]<=a[1]
# r6: retain readable Russian labels with the approved 80-pixel creation width.
assert all(rect[2]-rect[0]==80 for rect in rects[1:])
assert wnd.startswith('FILE_VERSION = 2;')
for lang in (ROOT/'languages').glob('*/generals.str'):
    text=lang.read_text(encoding='utf-8')
    assert all(text.count('\nGUI:'+key+'\n')==1 for key in ['ArmyScreen','ArmyMap','ArmyPlanes','ArmyHelicopters','ArmyScreenShort','ArmyMapShort','ArmyPlanesShort','ArmyHelicoptersShort','ArmyGround']),lang
print('PASS layout structure, unique IDs, button bounds/non-overlap, 12 language labels')
# Lifecycle watcher is deliberately atomic-only; never access engine objects from its thread.
watcher = engine[:engine.index('namespace {')]
assert 'cancelMobileInput();' not in watcher
assert 'cancelMobileInput();' in engine[engine.index('void SDL3GameEngine::pollSDL3Events'):]
poll_prefix = engine[engine.index('void SDL3GameEngine::pollSDL3Events'):engine.index('while (SDL_PollEvent')]
assert 'SDL_StartTextInput' not in poll_prefix and 'SDL_HasKeyboard' not in poll_prefix
print('PASS lifecycle cancellation is on the game thread, not the event watcher')
