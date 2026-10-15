#!/usr/bin/env python3
"""Compile actual adaptive army geometry and camera ceiling/preferences, including old saves."""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[2]
def function(s,signature):
 start=s.index(signature);i=s.index('{',start);depth=1;j=i+1
 while depth:depth+=(s[j]=='{')-(s[j]=='}');j+=1
 return s[start:j]
view=(root/'Core/GameEngineDevice/Source/W3DDevice/GameClient/W3DView.cpp').read_text()
prefs=(root/'Core/GameEngine/Source/Common/OptionPreferences.cpp').read_text()
code=r'''
#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <map>
#include <string>
#define __ANDROID__ 1
#include "GameClient/GXArmyPanelLayout.h"
using Real=float;using Bool=bool;
struct Global{float m_maxCameraHeight=500;}global,*TheGlobalData=&global;
struct Text:std::string {using std::string::string;using std::string::operator=;const char*str()const{return c_str();}};
struct OptionPreferences:std::map<std::string,Text>{float getMaxCameraHeight()const;};
'''+function(view,'static Real gxUserCameraHeightLimit')+'\n'+function(prefs,'Real OptionPreferences::getMaxCameraHeight')+r'''
int main() {
 assert(gxUserCameraHeightLimit(500,true)==2000);
 assert(gxUserCameraHeightLimit(900,true)==3600);
 assert(gxUserCameraHeightLimit(1000,true)==3600);
 assert(gxUserCameraHeightLimit(2000,true)==3600);
 assert(gxUserCameraHeightLimit(2000,false)==2000);
 OptionPreferences p;assert(p.getMaxCameraHeight()==500);
 for (auto value: {"975","1000","4000"}) {p["MaxCameraHeight"]=value;assert(p.getMaxCameraHeight()==900);}
 p.clear();global.m_maxCameraHeight=1200;assert(p.getMaxCameraHeight()==900);
 p["MaxCameraHeight"]="0";assert(p.getMaxCameraHeight()==100);
 for(auto size: {std::pair<int,int>{3048,2032},{2560,1080},{1920,1080},{800,600},{600,800},{320,240}}) {
  for(float font : {1.f,1.25f,1.5f,2.f,3.f}) {
   const int w=size.first,h=size.second;
   const int barWidth=std::min(w,(int)(h*4.f/3*std::min(font,1.29f)));
   const int barLeft=w-barWidth,barTop=(int)(h*.69f);
   auto box=GXArmyPanelLayout::calculate(w,h,barLeft,barTop,0,0,font);
   assert(box.x>=0&&box.y>=0&&box.x+box.width<=w);
   assert(box.y+6*box.height+5*box.gap<=h);
   assert(box.rowX>=0&&box.rowY>=0);
   assert(box.rowX+box.columns*box.cellWidth+(box.columns-1)*box.gap<=w);
   assert(box.rowY+box.rows*box.cellHeight+(box.rows-1)*box.gap<=h);
   assert(box.columns*box.rows==10);
   if(box.x+box.width<=barLeft && box.y>=barTop) {
    assert(box.rowY+box.rows*box.cellHeight+(box.rows-1)*box.gap<=box.y);
   } else {
    assert(box.y+6*box.height+5*box.gap<=barTop);
    assert(box.rowX>=box.x+box.width);
   }
  }
 }
 puts("PASS production r8: 3600 manual ceiling, old preference clamp, script preservation; six screens/five scales, plus above army, bounded nonoverlapping groups");
}
'''
with tempfile.TemporaryDirectory(prefix='gx-r8-policy-') as directory:
 p=Path(directory);(p/'test.cpp').write_text(code)
 subprocess.run(['g++','-std=c++17','-I',str(root/'Core/GameEngine/Include'),str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
