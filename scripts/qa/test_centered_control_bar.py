#!/usr/bin/env python3
"""Compile the complete production right-anchored HUD transform with fake services."""
from pathlib import Path
import re,subprocess,tempfile
root=Path(__file__).resolve().parents[2]
cpp=(root/'Core/GameEngine/Source/GameClient/GUI/GXUiScale.cpp').read_text()
header=(root/'Core/GameEngine/Include/GameClient/GXUiScale.h').read_text()
cpp=re.sub(r'^#include .*$', '', cpp, flags=re.M)
header=header[header.index('namespace GXUiScale'):]
preamble=r'''
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <strings.h>
#include <map>
#include <string>
#include <vector>
#include <cassert>
#include <fstream>
#include <sstream>
using Int=int; using Real=float; using Bool=bool;
constexpr Bool TRUE=true,FALSE=false;
struct Display { int w=1920,h=1080; int getWidth(){return w;} int getHeight(){return h;} } display,*TheDisplay=&display;
struct File { enum {READ}; int size(){return 0;} int read(char*,int){return 0;} void close(){} };
struct FS { File* openFile(const char*,int){return nullptr;} } *TheFileSystem=nullptr;
'''
main=r'''
int main(int argc,char**argv) {
 std::ifstream stream(argv[1]);std::stringstream buffer;buffer<<stream.rdbuf();std::string wnd=buffer.str();
 assert(!wnd.empty());
 for (auto size : std::vector<std::pair<int,int>>{{800,600},{1920,1080},{2560,1080},{3048,2032},{600,800}}) {
  display.w=size.first;display.h=size.second;
  GXUiScale::beginLayout("ControlBar.wnd",wnd.data(),wnd.size());
  auto t=GXUiScale::forLayout("ControlBar.wnd");
  float sx=t.kx*display.w/800.f,sy=t.ky*display.h/600.f;
  assert(std::fabs(sx-sy)<0.002f);
  float left=t.mapX(0),right=t.mapX(display.w);
  assert(left>=-0.1f && right<=display.w+0.1f);
  assert(std::fabs(right-display.w)<0.01f);
  int x=0,y=416*display.h/600,x1=799*display.w/800,y1=599*display.h/600;
  int beforeX=x,beforeY=y,beforeX1=x1,beforeY1=y1;
  GXUiScale::mapNextWindowRect(&x,&y,&x1,&y1);
  assert(std::abs(x-(int)std::floor(t.mapX(beforeX)+0.5f))<=1);
  assert(std::abs(x1-(int)std::floor(t.mapX(beforeX1)+0.5f))<=1);
  assert(std::abs(y-(int)std::floor(t.mapY(beforeY)+0.5f))<=1);
  assert(y1<=display.h);
  GXUiScale::endLayout();
  GXUiScale::beginLayout("GroupPanel.wnd",wnd.data(),wnd.size());
  auto group=GXUiScale::forLayout("GroupPanel.wnd");
  assert(group.kx==1.f&&group.addX==0.f);
  assert(group.ky==t.ky&&group.addY==t.addY);
  GXUiScale::endLayout();
 }
 puts("PASS production right HUD: 4:3, 16:9, ultrawide, tablet, portrait; matching art/hit rectangles and left army shortcuts");
}
'''
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--layout',type=Path,required=True);args=parser.parse_args()
with tempfile.TemporaryDirectory(prefix='gx-centered-hud-') as directory:
 p=Path(directory);(p/'test.cpp').write_text(preamble+header+cpp+main)
 subprocess.run(['g++','-std=c++17',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 for scale in ['100','125','150','200','300']:
  import os
  subprocess.run([str(p/'test'),str(args.layout)],env=dict(os.environ,GX_UI_SCALE=scale),check=True)
