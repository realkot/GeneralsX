#!/usr/bin/env python3
"""Compile production font sizing/loading callbacks against deterministic service mocks."""
from pathlib import Path
import re, subprocess
root=Path(__file__).resolve().parents[2]
out=root/'build/input-tests';out.mkdir(parents=True,exist_ok=True)
def function(text,signature):
 start=text.index(signature);i=text.index('{',start);depth=1;j=i+1
 while depth:
  depth+=(text[j]=='{')-(text[j]=='}');j+=1
 return text[start:j]
gx=(root/'Core/GameEngine/Source/GameClient/GUI/GXUiScale.cpp').read_text()
load=(root/'Core/GameEngine/Source/GameClient/GUI/LoadScreen.cpp').read_text()
code=r'''
#include <cassert>
#include <cmath>
#include <vector>
#include <cstdint>
using Int=int;using Real=float;using Bool=bool;using UnsignedInt=uint32_t;
constexpr bool TRUE=true,FALSE=false;
struct Transform{bool active=false;float fontK=1;};
struct Parsing{std::vector<int>scaled;int next=0;float resolutionFontK=1;Transform transform;};
std::vector<Parsing>s_parsing;
struct Engine{int calls=0;bool quitting=false;void serviceWindowsOS(){++calls;}bool getQuitting(){return quitting;}}engine,*TheGameEngine=&engine;
struct Logic{bool isQuitToDesktopRequested(){return false;}}logic,*TheGameLogic=&logic;
struct Audio{int calls=0;void UPDATE(){++calls;}}audio,*TheAudio=&audio;
struct WM{int calls=0;void update(){++calls;}}wm,*TheWindowManager=&wm;
struct Display{int updates=0,draws=0;void update(){++updates;}void draw(){++draws;}}display,*TheDisplay=&display;
uint32_t now=0;uint32_t timeGetTime(){return now;}void setFPMode(){}
static UnsignedInt s_gxLoadLastDraw=0;static Bool s_gxLoadHasDrawn=FALSE;
struct LoadScreen{void update(Int);};
#define GX_AUDIO_TRACE(...) ((void)0)
'''
code+=function(gx,'Int scaleFontSize( Int size )')+'\n'+function(load,'void LoadScreen::update( Int percent )')
code+=r'''
int main(){
 assert(scaleFontSize(12)==12);
 Parsing p;p.resolutionFontK=2032.f/600.f;s_parsing.push_back(p);
 assert(scaleFontSize(12)==41);assert(scaleFontSize(18)==61);
 // At 1280 output width, 3048 internal pixels: 41 becomes 17.2 visible pixels.
 assert(scaleFontSize(12)*1280.f/3048.f>17);
 s_parsing.back().resolutionFontK=1.8f;assert(scaleFontSize(12)==22);
 s_parsing.back().resolutionFontK=100;assert(scaleFontSize(18)==100);
 s_parsing.back().resolutionFontK=1;s_parsing.back().transform.active=true;
 s_parsing.back().transform.fontK=1.5f;s_parsing.back().scaled={1};s_parsing.back().next=1;
 assert(scaleFontSize(12)==18);
 LoadScreen screen;screen.update(0);assert(display.draws==1);
 for(int i=0;i<1000;++i)screen.update(50);
 assert(display.draws==1&&engine.calls==1001&&audio.calls==1001);
 now=33;screen.update(75);assert(display.draws==2);
 now=34;screen.update(100);assert(display.draws==3);
 // Unsigned subtraction remains safe across clock rollover.
 s_gxLoadLastDraw=UINT32_MAX-20;now=20;screen.update(50);assert(display.draws==4);
 engine.quitting=true;screen.update(100);assert(display.draws==4);
}
'''
cpp=out/'r4-ui-loading.cpp';exe=out/'r4-ui-loading';cpp.write_text(code)
subprocess.run(['g++','-std=c++17','-D__ANDROID__',str(cpp),'-o',str(exe)],check=True)
subprocess.run([str(exe)],check=True)
asset=root/'android/app/src/main/assets/gamedata/Window'
extra=(asset/'ExtrasMenu.wnd').read_text()
for block in re.findall(r'WINDOWTYPE = PUSHBUTTON;.*?\n\s*END',extra,re.S):
 assert 'SYSTEMCALLBACK = "[None]";' in block
 assert 'BORDERCOLOR: 70 70 210 255' in block
assert extra.count('STATUS = ENABLED+IMAGE+TABSTOP;')==5
assert extra.count('DISABLEDDRAWDATA = IMAGE: hilightedbox')>=5
assert 'Sleep(100)' not in load
panel=(root/'GeneralsMD/Code/GameEngine/Source/GameClient/GUI/GUICallbacks/GroupPanel.cpp').read_text()
assert 'digit.format(L"%d", group)' in panel
assert 'GadgetButtonSetText(button, digit)' in panel
text=(asset/'GroupPanel.wnd').read_text()
rects={}
for block in re.findall(r'WINDOWTYPE = \w+;.*?\n\s*END',text,re.S):
 m=re.search(r'UPPERLEFT: (\d+) (\d+), BOTTOMRIGHT: (\d+) (\d+)',block)
 n=re.search(r'NAME = "GroupPanel.wnd:([^"\n]+)"',block)
 if m and n:rects[n[1]]=tuple(map(int,m.groups()))
assert rects['GroupRow'][0]>rects['ArmyGround'][2]
print('PASS r4: production adaptive fonts, loading draw coalescing, audio/input service, final frame, clock wrap, literal digits, nonoverlapping groups, stock Extras image sliders')
