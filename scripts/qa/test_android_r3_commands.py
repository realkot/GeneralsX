#!/usr/bin/env python3
"""Compile production r3 mouse queue, command policy and Extras lifecycle with host service fakes.
These tests do not claim Android hardware delivery or displayed rendering.
"""
from pathlib import Path
import argparse,re,subprocess
ROOT=Path(__file__).resolve().parents[2]
a=argparse.ArgumentParser();a.add_argument('--sdl-include',type=Path,required=True);args=a.parse_args()
OUT=ROOT/'build/input-tests';OUT.mkdir(parents=True,exist_ok=True)
def function(s,signature):
 start=s.index(signature);i=s.index('{',start);depth=1;j=i+1
 while depth:depth+=(s[j]=='{')-(s[j]=='}');j+=1
 return s[start:j]
def run(name,code):
 p=OUT/(name+'.cpp');p.write_text(code)
 subprocess.run(['g++','-std=c++17','-Werror=return-type','-I',str(args.sdl_include),str(p),'-o',str(OUT/name)],check=True)
 subprocess.run([str(OUT/name)],check=True)
mouse=(ROOT/'GeneralsMD/Code/GameEngineDevice/Source/SDL3Device/GameClient/SDL3Mouse.cpp').read_text()
base=(ROOT/'Core/GameEngine/Source/GameClient/Input/Mouse.cpp').read_text()
run('r3_mouse_queue',r'''
#include <SDL3/SDL.h>
#include <deque>
#include <vector>
#include <cassert>
#include <cstring>
#include <cstdio>
#define __ANDROID__ 1
using Bool=bool;using Int=int;using UnsignedInt=unsigned;using UnsignedByte=unsigned char;
constexpr bool TRUE=true,FALSE=false;
constexpr int MOUSE_OK=1,MOUSE_NONE=0,MOUSE_LOST=255;
struct MouseIO {SDL_Event event;};
struct Mouse {MouseIO m_mouseEvents[256]{};int m_eventsThisFrame=0;virtual UnsignedByte getMouseEvent(MouseIO*,Bool)=0;void updateMouseData();};
std::deque<SDL_Event>& gxMousePendingEvents(){static std::deque<SDL_Event> events;return events;}
struct SDL3Mouse:Mouse {
 static constexpr SDL_MouseID TOUCHPAD_MOUSE_ID=0xfffffffdu;
 bool m_touchpadPointer=false;std::deque<SDL_Event>&m_pendingEvents=gxMousePendingEvents();
 void addSDLEvent(SDL_Event*);UnsignedByte getMouseEvent(MouseIO*,Bool)override;
 void translateEvent(const SDL_Event&e,MouseIO*r){r->event=e;}
};
'''+function(mouse,'void SDL3Mouse::addSDLEvent')+'\n'+function(mouse,'UnsignedByte SDL3Mouse::getMouseEvent')+'\n'+function(base,'void Mouse::updateMouseData')+r'''
int main(){
 SDL3Mouse m;SDL_Event e{};e.type=SDL_EVENT_MOUSE_MOTION;e.motion.windowID=1;e.motion.which=7;e.motion.xrel=1;
 for(int i=0;i<10000;i++){e.motion.x=(float)i;e.motion.timestamp=i;m.addSDLEvent(&e);}
 assert(m.m_pendingEvents.size()==1);assert(m.m_pendingEvents.front().motion.x==9999);assert(m.m_pendingEvents.front().motion.xrel==10000);
 e={};e.type=SDL_EVENT_MOUSE_BUTTON_DOWN;e.button.which=7;e.button.button=SDL_BUTTON_RIGHT;e.button.down=true;m.addSDLEvent(&e);
 e.type=SDL_EVENT_MOUSE_BUTTON_UP;e.button.down=false;m.addSDLEvent(&e);
 m.updateMouseData();assert(m.m_eventsThisFrame==3);assert(m.m_mouseEvents[1].event.type==SDL_EVENT_MOUSE_BUTTON_DOWN);assert(m.m_mouseEvents[2].event.type==SDL_EVENT_MOUSE_BUTTON_UP);
 for(int i=0;i<1000;i++){e={};e.type=(i%2)?SDL_EVENT_MOUSE_BUTTON_UP:SDL_EVENT_MOUSE_BUTTON_DOWN;e.button.timestamp=i;m.addSDLEvent(&e);}
 unsigned next=0;
 while(!m.m_pendingEvents.empty()){
  m.updateMouseData();assert(m.m_eventsThisFrame>0);
  if(next==0)assert(m.m_eventsThisFrame==256); // old updateMouseData silently lost event 256
  for(int i=0;i<m.m_eventsThisFrame;i++)assert(m.m_mouseEvents[i].event.button.timestamp==next++);
 }
 assert(next==1000);m.updateMouseData();assert(m.m_eventsThisFrame==0);
 e={};e.type=SDL_EVENT_MOUSE_MOTION;e.motion.which=7;e.motion.windowID=1;e.motion.state=0;m.addSDLEvent(&e);
 e.motion.which=8;m.addSDLEvent(&e);e.motion.windowID=2;m.addSDLEvent(&e);e.motion.state=SDL_BUTTON_RMASK;m.addSDLEvent(&e);
 assert(m.m_pendingEvents.size()==4);e.type=SDL_EVENT_KEY_DOWN;m.addSDLEvent(&e);assert(m.m_pendingEvents.size()==4);
 puts("PASS production mouse: 10000-motion burst, ordered press/release, 1000 edges, exact 256-event frame, source/window/button boundaries");
}
''')
cmd=(ROOT/'Core/GameEngine/Source/GameClient/MessageStream/CommandXlat.cpp').read_text()
ai=(ROOT/'GeneralsMD/Code/GameEngine/Source/GameLogic/AI/AIGroup.cpp').read_text()
run('r3_default_commands',r'''
#include <cassert>
#include <vector>
#include <list>
#include <cstdio>
#define __ANDROID__ 1
using Bool=bool;using Int=int;constexpr bool TRUE=true,FALSE=false;
enum{KINDOF_CAN_ATTACK,KINDOF_STRUCTURE,KINDOF_DOZER,KINDOF_HARVESTER,KINDOF_FORCEATTACKABLE};
struct Coord3D{float x=0,y=0,z=0;};using CommandSourceType=int;
struct AIUpdateInterface{int attacks=0,moves=0;void aiAttackMoveToPosition(const Coord3D*,int,int){++attacks;}void aiMoveToPosition(const Coord3D*,int){++moves;}};
struct Object{
 unsigned kinds=0;bool local=true,dead=false,contained=false,armed=false;AIUpdateInterface ai;
 bool isKindOf(int b){return kinds&(1u<<b);}bool isLocallyControlled(){return local;}bool isEffectivelyDead(){return dead;}bool isContained(){return contained;}
 int getID(){return 42;}bool isAbleToAttack(){return armed;}AIUpdateInterface*getAIUpdateInterface(){return &ai;}
};
struct Drawable{Object*obj;Object*getObject(){return obj;}};using DrawableList=std::list<Drawable*>;using DrawableListCIt=DrawableList::const_iterator;
struct UI{
 bool controllable=true,waypoint=false,attack=false,force=false,forceAttack=false;DrawableList selected;
 bool areSelectedObjectsControllable(){return controllable;}int getSelectCount(){return selected.size();}const DrawableList*getAllSelectedDrawables(){return &selected;}
 bool isInWaypointMode(){return waypoint;}bool isInAttackMoveToMode(){return attack;}bool isInForceMoveToMode(){return force;}bool isInForceAttackMode(){return forceAttack;}
}ui,*TheInGameUI=&ui;
struct GameMessage{
 enum Type{MSG_INVALID,MSG_ADD_WAYPOINT,MSG_DO_ATTACKMOVETO,MSG_DO_FORCEMOVETO,MSG_DO_ATTACK_OBJECT,MSG_DO_MOVETO,MSG_CREATE_SELECTED_GROUP,MSG_CREATE_SELECTED_GROUP_NO_SOUND,MSG_SELECT_TEAM0,MSG_SELECT_TEAM1,MSG_SELECT_TEAM2,MSG_SELECT_TEAM3,MSG_SELECT_TEAM4,MSG_SELECT_TEAM5,MSG_SELECT_TEAM6,MSG_SELECT_TEAM7,MSG_SELECT_TEAM8,MSG_SELECT_TEAM9};Type type;int obj=0;Coord3D pos;
 void appendObjectIDArgument(int id){obj=id;}void appendLocationArgument(Coord3D p){pos=p;}
};
struct Stream{std::vector<GameMessage>messages;bool containsMessageOfType(GameMessage::Type t){for(auto&m:messages)if(m.type==t)return true;return false;}GameMessage*appendMessage(GameMessage::Type t){messages.push_back({t});return &messages.back();}}stream,*TheMessageStream=&stream;
struct Stats{void incrementMoveCount(){}}stats,*TheStatsCollector=&stats;
struct PickAndPlayInfo{Drawable*m_drawTarget;};void pickAndPlayUnitVoiceResponse(const DrawableList*,GameMessage::Type,PickAndPlayInfo*){}
enum CommandEvaluateType{DO_COMMAND,EVALUATE_ONLY};
struct CommandTranslator{bool m_teamExists=true;GameMessage::Type issueMoveToLocationCommand(const Coord3D*,Drawable*,CommandEvaluateType);};
struct AIGroup{std::list<Object*>m_memberList;void groupAttackMoveToPosition(const Coord3D*,int,CommandSourceType);};
'''+function(cmd,'static Bool gxPendingSelectedMoveGroup')+'\n'+function(cmd,'static Bool gxDefaultAttackMove')+'\n'+function(cmd,'GameMessage::Type CommandTranslator::issueMoveToLocationCommand')+'\n'+function(ai,'void AIGroup::groupAttackMoveToPosition')+r'''
int main(){
 Object soldier,worker,target; soldier.kinds=1u<<KINDOF_CAN_ATTACK;soldier.armed=true;worker.kinds=1u<<KINDOF_DOZER;
 Drawable a{&soldier},b{&worker},t{&target};Coord3D pos{10,20,30};CommandTranslator c;
 ui.selected={&a};assert(c.issueMoveToLocationCommand(&pos,nullptr,DO_COMMAND)==GameMessage::MSG_DO_ATTACKMOVETO);
 assert(stream.messages.back().pos.x==10);
 ui.selected={&b};assert(c.issueMoveToLocationCommand(&pos,nullptr,DO_COMMAND)==GameMessage::MSG_DO_MOVETO);
 ui.selected={&a,&b};assert(gxDefaultAttackMove());AIGroup group;group.m_memberList={&soldier,&worker};group.groupAttackMoveToPosition(&pos,-1,0);assert(soldier.ai.attacks==1&&worker.ai.moves==1);
 ui.force=true;assert(c.issueMoveToLocationCommand(&pos,nullptr,DO_COMMAND)==GameMessage::MSG_DO_FORCEMOVETO);ui.force=false;
 ui.waypoint=true;assert(c.issueMoveToLocationCommand(&pos,nullptr,DO_COMMAND)==GameMessage::MSG_ADD_WAYPOINT);ui.waypoint=false;
 ui.forceAttack=true;target.kinds=1u<<KINDOF_FORCEATTACKABLE;assert(c.issueMoveToLocationCommand(&pos,&t,DO_COMMAND)==GameMessage::MSG_DO_ATTACK_OBJECT);assert(stream.messages.back().obj==42);ui.forceAttack=false;
 for(auto flag:{&soldier.dead,&soldier.contained}){*flag=true;assert(!gxDefaultAttackMove());*flag=false;}
 soldier.local=false;assert(!gxDefaultAttackMove());soldier.local=true;
 for(int kind:{KINDOF_DOZER,KINDOF_HARVESTER,KINDOF_STRUCTURE}){soldier.kinds=(1u<<KINDOF_CAN_ATTACK)|(1u<<kind);assert(!gxDefaultAttackMove());}
 ui.controllable=false;assert(!gxDefaultAttackMove());ui.controllable=true;
 c.m_teamExists=false;const auto count=stream.messages.size();assert(c.issueMoveToLocationCommand(&pos,nullptr,DO_COMMAND)==GameMessage::MSG_INVALID);assert(stream.messages.size()==count);
 soldier.kinds=1u<<KINDOF_CAN_ATTACK;ui.selected={&a};stream.appendMessage(GameMessage::MSG_CREATE_SELECTED_GROUP);
 assert(c.issueMoveToLocationCommand(&pos,nullptr,DO_COMMAND)==GameMessage::MSG_DO_ATTACKMOVETO);
 assert(stream.messages[stream.messages.size()-2].type==GameMessage::MSG_CREATE_SELECTED_GROUP);
 puts("PASS production default commands: combat/mixed groups, passive worker fallback, force move, waypoint, forced target attack, ownership/dead/contained gates");
}
''')
print('PASS r3 mouse and command regression suites')
