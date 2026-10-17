#!/usr/bin/env python3
"""Compile the real FramePacer and offline logic gate against small platform stubs."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'build/input-tests/render-rate';out.mkdir(parents=True,exist_ok=True)
headers={
'PreRTS.h':r'''#pragma once
#include <algorithm>
#include <cassert>
using Int=int;using Real=float;using UnsignedInt=unsigned;using Bool=bool;
using std::min;
#define CPP_11(...) __VA_ARGS__
#define TRUE true
#define FALSE false
#define DEBUG_LOG(x) ((void)0)
constexpr int BaseFps=30;
constexpr int LOGICFRAMES_PER_SECOND=TEST_HZ;
constexpr int GENERALS_ONLINE_HIGH_FPS_LIMIT=TEST_HZ;
constexpr float LOGICFRAMES_PER_SECONDS_REAL=TEST_HZ;
constexpr float SECONDS_PER_LOGICFRAME_REAL=1.0f/TEST_HZ;
constexpr float MSEC_PER_LOGICFRAME_REAL=1000.0f/TEST_HZ;
struct GlobalData { bool m_useFpsLimit=true;bool m_TiVOFastMode=false; };
extern GlobalData* TheGlobalData;
''',
'Common/FrameRateLimit.h':r'''#pragma once
struct FrameRateLimit { float wait(unsigned fps) {return 1.0f/fps;} };
struct RenderFpsPreset { enum {UncappedFpsValue=1000000}; };
''',
'GameClient/View.h':r'''#pragma once
struct View {float multiplier=1;float getTimeMultiplier(){return multiplier;}};extern View* TheTacticalView;
''',
'GameLogic/GameLogic.h':r'''#pragma once
struct GameLogic { bool game=true,replay=false,skirmish=true,single=false,paused=false;
bool isInGame(){return game;} bool isInReplayGame(){return replay;}
bool isInSkirmishGame(){return skirmish;} bool isInSinglePlayerGame(){return single;}
bool isGamePaused(){return paused;}};extern GameLogic* TheGameLogic;
''',
'GameLogic/ScriptEngine.h':r'''#pragma once
struct ScriptEngine {bool fast=false;bool isTimeFast(){return fast;}};extern ScriptEngine* TheScriptEngine;
''',
'GameNetwork/NetworkDefs.h':'#pragma once\n',
'GameNetwork/NetworkInterface.h':r'''#pragma once
struct Network {int getFrameRate(){return TEST_HZ;}};extern Network* TheNetwork;
'''}
for n,s in headers.items():
 p=out/'stubs'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
engine=(ROOT/'GeneralsMD/Code/GameEngine/Source/Common/GameEngine.cpp').read_text()
a=engine.index('Bool GameEngine::canUpdateRegularGameLogic(');b=engine.index('\n#if defined(GENERALS_ONLINE_HIGH_FPS_RENDER)',a);gate=engine[a:b]
code=r'''
#include "PreRTS.h"
#include "Common/FramePacer.h"
#include "GameClient/View.h"
#include "GameLogic/GameLogic.h"
#include "GameLogic/ScriptEngine.h"
#include "GameNetwork/NetworkInterface.h"
#include <cstdio>
GlobalData data;GlobalData* TheGlobalData=&data;
View view;View* TheTacticalView=&view;
GameLogic logic;GameLogic* TheGameLogic=&logic;
ScriptEngine script;ScriptEngine* TheScriptEngine=&script;
Network network;Network* TheNetwork=nullptr;
struct GameEngine { float m_logicTimeAccumulator=0;bool canUpdateRegularGameLogic(unsigned); };
'''+gate+r'''
int main(){
 FramePacer pacer;TheFramePacer=&pacer;pacer.enableFramesPerSecondLimit(true);pacer.setFramesPerSecondLimit(TEST_HZ);
 FramePacer::setRequestedRenderFps(0);assert(!pacer.isRenderOnlyRateActive());assert(pacer.getActualLogicTimeScaleFps()==1000000);
 for(int fps:{30,60,90,120}){
  FramePacer::setRequestedRenderFps(fps);assert(pacer.isRenderOnlyRateActive());
  int render=std::max(fps,TEST_HZ);assert(pacer.getActualFramesPerSecondLimit()==render);
  assert(pacer.getActualLogicTimeScaleFps()==TEST_HZ);
  GameEngine engine;int ticks=0;
  for(int i=0;i<render*10;i++){pacer.update();ticks+=engine.canUpdateRegularGameLogic(FramePacer::IgnoreFrozenTime);}
  assert(ticks>=TEST_HZ*10-1&&ticks<=TEST_HZ*10); // exact production accumulator, 10 seconds
 }
 FramePacer::setRequestedRenderFps(120);
 logic.replay=true;assert(!pacer.isRenderOnlyRateActive());assert(pacer.getActualLogicTimeScaleFps()==1000000);logic.replay=false;
 TheNetwork=&network;assert(!pacer.isRenderOnlyRateActive());assert(pacer.getActualLogicTimeScaleFps()==TEST_HZ);TheNetwork=nullptr;
 logic.game=false;assert(!pacer.isRenderOnlyRateActive());logic.game=true;
 pacer.setFramesPerSecondLimit(TEST_HZ*2);assert(!pacer.isRenderOnlyRateActive());assert(pacer.getActualFramesPerSecondLimit()==TEST_HZ*2);pacer.setFramesPerSecondLimit(TEST_HZ);
 pacer.enableFramesPerSecondLimit(false);assert(!pacer.isRenderOnlyRateActive());pacer.enableFramesPerSecondLimit(true);
 script.fast=true;assert(!pacer.isRenderOnlyRateActive());script.fast=false;
 pacer.setTimeFrozen(true);assert(pacer.getActualLogicTimeScaleFps()==0);assert(pacer.getActualLogicTimeScaleFps(FramePacer::IgnoreFrozenTime)==TEST_HZ);pacer.setTimeFrozen(false);
 pacer.enableLogicTimeScale(true);pacer.setLogicTimeScaleFps(TEST_HZ/2);assert(pacer.getActualLogicTimeScaleFps()==TEST_HZ/2);pacer.enableLogicTimeScale(false);
 FramePacer::setRequestedRenderFps(144);assert(!pacer.isRenderOnlyRateActive());
 printf("PASS actual FramePacer + regular logic gate: simulation %d Hz, render 30/60/90/120; replay/network/default/fast/pause guards\n",TEST_HZ);
}
'''
source=out/'test.cpp';source.write_text(code)
for hz in (30,60):
 binary=out/f'render-{hz}'
 subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror',f'-DTEST_HZ={hz}','-I'+str(out/'stubs'),'-I'+str(ROOT/'Core/GameEngine/Include'),str(source),str(ROOT/'Core/GameEngine/Source/Common/FramePacer.cpp'),'-o',str(binary)],check=True)
 subprocess.run([str(binary)],check=True)
assert '!TheFramePacer->isRenderOnlyRateActive()' in engine

# Preprocess the actual registration table with release/debug flags: a parsed option
# must survive the same conditional compilation as the production release engine.
command=(ROOT/'GeneralsMD/Code/GameEngine/Source/Common/CommandLine.cpp').read_text()
start=command.index('static CommandLineParam paramsForEngineInit[]')
end=command.index('\n};',start)+3
table=command[start:end]
for debug in (0,1):
    processed=subprocess.check_output(['g++','-E','-P','-x','c++','-D__ANDROID__=1',*(['-DRTS_DEBUG=1'] if debug else []),'-'],input=table,text=True)
    assert processed.count('"-gxRenderFps"')==1, 'Render option missing from release parser'
print('PASS render option registered in both release/debug engine-init parsers')
