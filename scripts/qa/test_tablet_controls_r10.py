#!/usr/bin/env python3
"""Compile actual control policies; reject malformed prefs, layout overflow and orphan releases."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/input-tests';OUT.mkdir(parents=True,exist_ok=True)
code=r'''
#include "Common/GXTabletControls.h"
#include "Common/GXPointerButtons.h"
#include "GameClient/GXCursorGeometry.h"
#include "GameClient/GXExtrasValues.h"
#include "GameClient/GXArmyPanelLayout.h"
#include <cassert>
#include <string>
int main(){
 GXTabletControls::Settings s;
 FILE *f=tmpfile();assert(f);
 std::string input="attackMove=0\ncursorPercent=999\npanelScale=bad\npanelMask=-5\npanelWidth=999999999999999999999999\n";
 input+=std::string(300,'x')+"=1\npanelOpacity=50\nfitLabels=0garbage\n";
 fwrite(input.data(),1,input.size(),f);rewind(f);GXTabletControls::parse(f,s);fclose(f);
 assert(s.attackMove==0&&s.cursorPercent==250&&s.panelScale==100&&s.panelMask==0&&s.panelWidth==100&&s.panelOpacity==50&&s.fitLabels==1);
 unsigned held=0;
 assert(!GXPointerButtons::accept(held,1,false));
 assert(GXPointerButtons::accept(held,1,true));held=0;
 assert(!GXPointerButtons::accept(held,1,false));
 assert(GXPointerButtons::accept(held,2,true));assert(GXPointerButtons::accept(held,2,false));assert(held==0);
 for(int percent=100;percent<=250;percent+=25)for(int size:{1,16,32,64}){
   int width=GXCursorGeometry::scale(size,percent);
   for(int hot:{0,size-1}){int h=GXCursorGeometry::hotspot(hot,percent,width);assert(h>=0&&h<width);}
 }
 unsigned char pixels[5*24]={};pixels[2*24+2*4]=255;pixels[2*24+2*4+3]=255;
 GXCursorGeometry::outline(pixels,5,5,24);
 assert(pixels[2*24+2*4]==255&&pixels[2*24+2*4+3]==255);
 assert(pixels[1*24+1*4+3]==255&&pixels[1*24+1*4]==0&&pixels[3]==0);
 int value=0;assert(GXExtrasValues::digits(L"3600",4,value)&&value==3600);
 assert(!GXExtrasValues::digits(L"-1",2,value));assert(!GXExtrasValues::digits(L"2x",2,value));assert(!GXExtrasValues::digits(L"",0,value));
 assert(GXExtrasValues::normalize(99999,400,3600,4)==3600);
 assert(GXExtrasValues::normalize(601,400,3600,4)==600);
 assert(GXExtrasValues::normalize(1,400,3600,4)==400);
 for(auto size:{std::pair<int,int>(1280,853),{2560,1080},{3048,2032},{800,600}})
 for(int scale:{75,100,150})for(int width:{80,100,180})for(int offset:{0,50,100})for(int count:{0,1,5}){
   int w=size.first,h=size.second;
   auto box=GXArmyPanelLayout::calculate(w,h,w*5/12,h*7/10,0,0,1.0f,scale,width,offset,offset,count);
   assert(box.x>=0&&box.y>=0&&box.width>0&&box.height>0);
   assert(box.x+box.width<=w);
   assert(box.y+(count+1)*box.height+count*box.gap<=h);
   assert(box.rowX>=0&&box.rowY>=0);
   assert(box.rowX+box.columns*box.cellWidth+(box.columns-1)*box.gap<=w);
 }
 puts("PASS production tablet prefs, cancelled releases, cursor geometry/outline, exact Extras values and layout combinations");
}
'''
source=OUT/'tablet-controls-r10.cpp';source.write_text(code)
subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror','-I',str(ROOT/'Core/GameEngine/Include'),str(source),'-o',str(OUT/'tablet-controls-r10')],check=True)
subprocess.run([str(OUT/'tablet-controls-r10')],check=True)
