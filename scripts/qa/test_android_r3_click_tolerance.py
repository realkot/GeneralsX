#!/usr/bin/env python3
"""Compile the production pointer-distance/viewport policy and command-click guards."""
from pathlib import Path
import argparse,subprocess
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/input-tests';OUT.mkdir(parents=True,exist_ok=True)
a=argparse.ArgumentParser();a.add_argument('--sdl-include',type=Path,required=True);args=a.parse_args()
def function(s,name):
 start=s.index(name);i=s.index('{',start);depth=1;j=i+1
 while depth:depth+=(s[j]=='{')-(s[j]=='}');j+=1
 return s[start:j]
base=(ROOT/'Core/GameEngine/Source/GameClient/Input/Mouse.cpp').read_text()
sdl=(ROOT/'GeneralsMD/Code/GameEngineDevice/Source/SDL3Device/GameClient/SDL3Mouse.cpp').read_text()
code=r'''
#include <SDL3/SDL.h>
#include <cassert>
#include <cmath>
#include <algorithm>
#include <cstdio>
using std::max;using Bool=bool;using Real=float;using UnsignedInt=unsigned;constexpr Bool TRUE=true,FALSE=false;
struct ICoord2D{int x=0,y=0;ICoord2D operator-(const ICoord2D&o)const{return {x-o.x,y-o.y};}};
struct Coord3D{float x=0,y=0,z=0;Coord3D operator-(const Coord3D&o)const{return {x-o.x,y-o.y,z-o.z};}float lengthSqr()const{return x*x+y*y+z*z;}};
template<class T>auto sqr(T v){return v*v;}
struct Display{
 int width=3048,height=2032,pw=600,ph=400;bool viewport=false;
 int getWidth(){return width;}int getHeight(){return height;}
 bool getViewportRect(int&x,int&y,int&w,int&h){x=50;y=40;w=pw;h=ph;return viewport;}
}display,*TheDisplay=&display;
int ww=1280,wh=853;
extern "C" bool SDL_GetWindowSize(SDL_Window*,int*w,int*h){*w=ww;*h=wh;return true;}
struct Mouse{
 int m_dragTolerance=2,m_dragToleranceMS=200,m_dragTolerance3D=2;
 void getClickToleranceScale(float&,float&)const;static void setClickToleranceScale(float,float);
 bool isClickDistance(const ICoord2D&)const;bool isClick(const ICoord2D&,const ICoord2D&,const Coord3D&,const Coord3D&,unsigned,unsigned);
};
struct SDL3Mouse:Mouse{
 bool active=true;SDL_Window*m_Window=reinterpret_cast<SDL_Window*>(1);
 bool hasContinuousPointer()const{return active;}
 void getPointerClickToleranceScale(float&,float&)const;
 void syncScale(){float x,y;getPointerClickToleranceScale(x,y);Mouse::setClickToleranceScale(x,y);}
};
'''+'static Real s_gxMouseClickScaleX=1,s_gxMouseClickScaleY=1;\n'+function(base,'void Mouse::getClickToleranceScale')+'\n'+function(base,'void Mouse::setClickToleranceScale')+'\n'+function(sdl,'void SDL3Mouse::getPointerClickToleranceScale')+'\n'+function(base,'Bool Mouse::isClickDistance')+'\n'+function(base,'Bool Mouse::isClick(')+r'''
int main(){
 SDL3Mouse m;float x,y;m.getPointerClickToleranceScale(x,y);m.syncScale();assert(std::fabs(x-3048.f/1280)<0.001);
 assert(m.isClickDistance({5,0}));assert(!m.isClickDistance({7,0})); // two window pixels plus integer endpoint quantization
 assert(m.isClick({0,0},{5,0},{0,0,0},{0,0,0},1000,1100));
 assert(!m.isClick({0,0},{5,0},{0,0,0},{0,0,0},1000,1300));
 assert(!m.isClick({0,0},{5,0},{0,0,0},{3,0,0},1000,1100));
 display.viewport=true;m.getPointerClickToleranceScale(x,y);m.syncScale();assert(std::fabs(x-5.08f)<0.001);assert(m.isClickDistance({10,0}));assert(!m.isClickDistance({14,0}));
 display.ph=600;m.getPointerClickToleranceScale(x,y);m.syncScale();assert(std::fabs(y-2032.f/600)<0.001);assert(m.isClickDistance({0,6}));assert(!m.isClickDistance({0,10}));
 m.active=false;m.getPointerClickToleranceScale(x,y);m.syncScale();assert(x==1&&y==1);assert(m.isClickDistance({2,0}));assert(!m.isClickDistance({3,0}));assert(!m.isClickDistance({2,1}));
 m.active=true;display.viewport=false;ww=wh=0;m.getPointerClickToleranceScale(x,y);m.syncScale();assert(x==1&&y==1);
 puts("PASS production click tolerance: 3048x2032, viewport/letterbox scale, quantization, real drag, touch fallback, duration and camera-movement guards");
}
'''
p=OUT/'r3_click_tolerance.cpp';p.write_text(code)
subprocess.run(['g++','-std=c++17','-I',str(args.sdl_include),str(p),'-o',str(OUT/'r3_click_tolerance')],check=True)
subprocess.run([str(OUT/'r3_click_tolerance')],check=True)
meta=(ROOT/'Core/GameEngine/Source/GameClient/MessageStream/MetaEvent.cpp').read_text()
selection=(ROOT/'Core/GameEngine/Source/GameClient/MessageStream/SelectionXlat.cpp').read_text()
assert 'TheMouse->isClickDistance(pixelRegion.hi - pixelRegion.lo)' in meta
assert '!TheMouse->isClickDistance(delta)' in selection
print('PASS both meta-click regions and drag selection use the same production predicate')

header=(ROOT/'Core/GameEngine/Include/GameClient/Mouse.h').read_text()
assert 'virtual void getClickToleranceScale' not in header
assert 'static void setClickToleranceScale' in header
print('PASS click scaling is device-fed without adding Mouse virtual slots or fields')
