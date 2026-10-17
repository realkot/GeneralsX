#!/usr/bin/env python3
"""Compile the real FramePacer and offline logic gate against small platform stubs."""
from pathlib import Path
import subprocess, re
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
#define GENERALS_ONLINE_HIGH_FPS_FRAME_MULTIPLIER (TEST_HZ/30)
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
struct FrameRateLimit { static inline float nextDelta=0; void reset(){nextDelta=0;} float wait(unsigned fps) {if(nextDelta>0){float d=nextDelta;nextDelta=0;return d;}return 1.0f/fps;} };
struct RenderFpsPreset { enum {UncappedFpsValue=1000000}; };
''',
'GameClient/View.h':r'''#pragma once
struct View {float multiplier=1;float getTimeMultiplier(){return multiplier;}};extern View* TheTacticalView;
''',
'GameLogic/GameLogic.h':r'''#pragma once
struct GameLogic { bool game=true,replay=false,skirmish=true,single=false,paused=false;
bool isInGame(){return game;} bool isInReplayGame(){return replay;}
bool isInSkirmishGame(){return skirmish;} bool isInSinglePlayerGame(){return single;}
bool isGamePaused(){return paused;} int updates=0; void preUpdate(){} void UPDATE(){updates++;}};extern GameLogic* TheGameLogic;
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
reset_start=engine.index('void GameEngine::resetFrameTiming()')
reset_end=engine.index('static void gxCatchUpSpedUpLogic()',reset_start)
reset=engine[reset_start:reset_end]
catch_start=reset_end;catch_end=engine.index('DECLARE_PERF_TIMER(GameEngine_update)',catch_start)
catchup=engine[catch_start:catch_end]
mobile=(ROOT/'GeneralsMD/Code/GameEngineDevice/Source/SDL3GameEngine.cpp').read_text()
watch_start=mobile.index('static bool SDLCALL mobileLifecycleWatcher(')
watch_end=mobile.index('\n\treturn true;\n}',watch_start)+len('\n\treturn true;\n}')
watch=mobile[watch_start:watch_end]
events=list(dict.fromkeys(re.findall(r'case (SDL_EVENT_\w+)',watch)))
consume=mobile.split('// GX_RESUME_TIMING_BEGIN',1)[1].split('// GX_RESUME_TIMING_END',1)[0]
lifecycle='enum { '+','.join(events)+' };\n'+r'''struct SDL_Event { int type; };
#define SDLCALL
static std::atomic<bool> s_appBackgrounded{false},s_appInactive{false},s_timingResetRequested{false};
static void logMobileLifecycleEvent(const char*){}
'''+watch+'\nstruct SDL3GameEngine : GameEngine { void consumeResumeTiming(){'+consume+'} };\n'
code=r'''
#include "PreRTS.h"
#include "Common/FramePacer.h"
#include "GameClient/View.h"
#include "GameLogic/GameLogic.h"
#include "GameLogic/ScriptEngine.h"
#include "GameNetwork/NetworkInterface.h"
#include <cstdio>
#include <atomic>
#include <chrono>
#include <thread>
#include <cmath>
GlobalData data;GlobalData* TheGlobalData=&data;
View view;View* TheTacticalView=&view;
GameLogic logic;GameLogic* TheGameLogic=&logic;
ScriptEngine script;ScriptEngine* TheScriptEngine=&script;
Network network;Network* TheNetwork=nullptr;
struct GameEngine { float m_logicTimeAccumulator=0;bool canUpdateRegularGameLogic(unsigned);void resetFrameTiming(); };
struct Recorder {bool isPlaybackMode(){return false;}} recorder;Recorder* TheRecorder=&recorder;
struct Shell {bool isShellActive(){return false;}} shell;Shell* TheShell=&shell;
struct MessageStream {void propagateMessages(){}} messages;MessageStream* TheMessageStream=&messages;
struct GameClient {void step(){}} client;GameClient* TheGameClient=&client;
static bool s_resetCatchupClock=false;static unsigned s_gxCatchUpSteps=0;
'''+gate+reset+catchup+lifecycle+r'''
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
 for(int flag=0;flag<2;flag++){
  pacer.enableFramesPerSecondLimit(flag==1);data.m_useFpsLimit=flag==0;
  assert(pacer.isRenderOnlyRateActive());assert(pacer.getActualLogicTimeScaleFps()==TEST_HZ);
  assert(pacer.getActualFramesPerSecondLimit()==120);
  GameEngine check;int ticks=0;
  for(int n=0;n<1200;n++){pacer.update();ticks+=check.canUpdateRegularGameLogic(FramePacer::IgnoreFrozenTime);}
  assert(ticks>=TEST_HZ*10-1&&ticks<=TEST_HZ*10);
 }
 pacer.enableFramesPerSecondLimit(true);data.m_useFpsLimit=true;
 SDL3GameEngine resumed;
 for(float gap:{0.05f,5.0f,120.0f}){
  SDL_Event event{SDL_EVENT_WILL_ENTER_BACKGROUND};mobileLifecycleWatcher(nullptr,&event);
  event.type=SDL_EVENT_WINDOW_FOCUS_LOST;mobileLifecycleWatcher(nullptr,&event);
  assert(s_appBackgrounded&&s_appInactive&&s_timingResetRequested);
  FrameRateLimit::nextDelta=gap;pacer.update();resumed.m_logicTimeAccumulator=0.01f;
  event.type=SDL_EVENT_DID_ENTER_FOREGROUND;mobileLifecycleWatcher(nullptr,&event);
  event.type=SDL_EVENT_WINDOW_FOCUS_GAINED;mobileLifecycleWatcher(nullptr,&event);
  assert(!s_appBackgrounded&&!s_appInactive);
  resumed.consumeResumeTiming();assert(!s_timingResetRequested);
  assert(resumed.m_logicTimeAccumulator==0&&std::abs(pacer.getUpdateTime()-1.0f/120)<0.00001f&&std::isfinite(pacer.getUpdateFps())&&s_resetCatchupClock);
  int updates=logic.updates;gxCatchUpSpedUpLogic();assert(!s_resetCatchupClock&&logic.updates==updates);
  int ticks=0;for(int n=0;n<1200;n++){pacer.update();ticks+=resumed.canUpdateRegularGameLogic(FramePacer::IgnoreFrozenTime);}
  assert(ticks>=TEST_HZ*10-1&&ticks<=TEST_HZ*10);
 }
 // Both lifecycle events can arrive within one poll; reset still must be consumed.
 for(int type:{SDL_EVENT_WINDOW_MINIMIZED,SDL_EVENT_WINDOW_RESTORED}){SDL_Event e{type};mobileLifecycleWatcher(nullptr,&e);}
 resumed.consumeResumeTiming();assert(resumed.m_logicTimeAccumulator==0&&s_resetCatchupClock);gxCatchUpSpedUpLogic();
 // Do not reset network or replay clocks.
 TheNetwork=&network;resumed.m_logicTimeAccumulator=0.01f;s_timingResetRequested=true;resumed.consumeResumeTiming();assert(resumed.m_logicTimeAccumulator==0.01f&&!s_resetCatchupClock);TheNetwork=nullptr;
 logic.replay=true;s_timingResetRequested=true;resumed.consumeResumeTiming();assert(resumed.m_logicTimeAccumulator==0.01f&&!s_resetCatchupClock);logic.replay=false;
 // A suspended custom-speed session must not receive catch-up work on resume.
 pacer.setFramesPerSecondLimit(TEST_HZ*2);gxCatchUpSpedUpLogic();std::this_thread::sleep_for(std::chrono::milliseconds(120));
 int previous=logic.updates;resumed.resetFrameTiming();gxCatchUpSpedUpLogic();assert(logic.updates==previous);pacer.setFramesPerSecondLimit(TEST_HZ);

 script.fast=true;assert(!pacer.isRenderOnlyRateActive());script.fast=false;
 pacer.setTimeFrozen(true);assert(pacer.getActualLogicTimeScaleFps()==0);assert(pacer.getActualLogicTimeScaleFps(FramePacer::IgnoreFrozenTime)==TEST_HZ);pacer.setTimeFrozen(false);
 pacer.enableLogicTimeScale(true);pacer.setLogicTimeScaleFps(TEST_HZ/2);assert(pacer.getActualLogicTimeScaleFps()==TEST_HZ/2);pacer.enableLogicTimeScale(false);
 FramePacer::setRequestedRenderFps(144);assert(!pacer.isRenderOnlyRateActive());
 printf("PASS actual FramePacer + regular logic gate: simulation %d Hz, render 30/60/90/120; replay/network/default/fast/pause, mutable FPS flags and suspend/resume guards\n",TEST_HZ);
}
'''
source=out/'test.cpp';source.write_text(code)
for hz in (30,60):
 binary=out/f'render-{hz}'
 subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror','-Wno-unused-parameter',f'-DTEST_HZ={hz}','-I'+str(out/'stubs'),'-I'+str(ROOT/'Core/GameEngine/Include'),str(source),str(ROOT/'Core/GameEngine/Source/Common/FramePacer.cpp'),'-o',str(binary)],check=True)
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
    without_includes='\n'.join(line for line in command.splitlines() if not line.lstrip().startswith('#include'))
    full=subprocess.check_output(['g++','-E','-P','-x','c++','-D__ANDROID__=1',*(['-DRTS_DEBUG=1'] if debug else []),'-'],input=without_includes,text=True)
    assert 'Int parseGXRenderFps(' in full, 'Render parser implementation missing from release engine'
print('PASS render option registered in both release/debug engine-init parsers')

# Exercise the real monotonic FrameRateLimit implementation across a wall-time pause.
timer_stubs=out/'timer-stubs';(timer_stubs/'Common').mkdir(parents=True,exist_ok=True)
(timer_stubs/'PreRTS.h').write_text(headers['PreRTS.h']+'\nusing Int64=long long;\n#define PROFILER_SECTION ((void)0)\n#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))\n#include <climits>\n')
(timer_stubs/'Common/GameCommon.h').write_text('#pragma once\n')
timer_source=out/'timer.cpp';timer_source.write_text(r'''
#include "PreRTS.h"
#include "Common/FrameRateLimit.h"
#include <chrono>
#include <thread>
#include <cmath>
#include <cstdio>
int main(){
 FrameRateLimit limiter;limiter.wait(120);
 std::this_thread::sleep_for(std::chrono::milliseconds(150));
 auto start=std::chrono::steady_clock::now();limiter.reset();float delta=limiter.wait(120);
 double spent=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
 assert(std::isfinite(delta)&&delta>0&&delta<=spent+0.01);
 printf("PASS actual monotonic timer discards suspended wall time (delta %.6f, wait %.6f)\n",delta,spent);
}
''')
timer=out/'monotonic-reset'
subprocess.run(['g++','-std=c++17','-DTEST_HZ=60','-I'+str(timer_stubs),'-I'+str(ROOT/'Core/GameEngine/Include'),str(timer_source),str(ROOT/'Core/GameEngine/Source/Common/FrameRateLimit.cpp'),'-o',str(timer)],check=True)
subprocess.run([str(timer)],check=True)
