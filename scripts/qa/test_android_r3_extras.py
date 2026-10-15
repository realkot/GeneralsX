#!/usr/bin/env python3
"""Exercise production Extras open/apply/cancel/escape ownership and preference guards."""
from pathlib import Path
import subprocess,re
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/input-tests';OUT.mkdir(parents=True,exist_ok=True)
s=(ROOT/'GeneralsMD/Code/GameEngine/Source/GameClient/GUI/GUICallbacks/Menus/ExtrasMenu.cpp').read_text()
def function(signature):
 start=s.index(signature);i=s.index('{',start);depth=1;j=i+1
 while depth:depth+=(s[j]=='{')-(s[j]=='}');j+=1
 return s[start:j]
code=r'''
#include <cassert>
#include <map>
#include <string>
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdarg>
#include <cmath>
using std::min;using std::max;using Bool=bool;using Int=int;using Real=float;using UnsignedInt=unsigned;using UnsignedByte=unsigned char;
using NameKeyType=int;using WindowMsgData=uintptr_t;using WindowMsgHandledType=int;
constexpr bool TRUE=true,FALSE=false;constexpr int NAMEKEY_INVALID=0,GWM_CREATE=1,GWM_DESTROY=2,GWM_INPUT_FOCUS=3,GBM_SELECTED=4,GWM_CHAR=5,KEY_ESC=27,KEY_STATE_UP=1,MSG_HANDLED=1,MSG_IGNORED=0;
#define BitIsSet(a,b) ((a)&(b))
#define DEG_TO_RADF(a) ((a)*3.14159265f/180.f)
struct AsciiString:std::string {using std::string::string;void format(const char*fmt,...){char b[100];va_list a;va_start(a,fmt);vsnprintf(b,sizeof(b),fmt,a);va_end(a);assign(b);}};
int writes=0,destroyed=0,shutdowns=0;
struct OptionPreferences:std::map<std::string,AsciiString>{void write(){++writes;}};
struct WindowLayout;struct WinInstanceData{};
struct GameWindow{int id=0,val=0;bool hasDraw=false;int winGetWindowId(){return id;}void winSetDrawFunc(void(*)(GameWindow*,WinInstanceData*)){hasDraw=true;}};
struct NameKeys{std::map<std::string,int>ids;int nameToKey(const char*s){if(!ids.count(s))ids[s]=ids.size()+1;return ids[s];}}keys,*TheNameKeyGenerator=&keys;
struct WM{
 bool missing=false,noRoot=false;GameWindow options;GameWindow*extra=nullptr,*focus=nullptr;std::vector<GameWindow*>modals;
 WindowLayout*winCreateLayout(const char*);
 GameWindow*winGetWindowFromId(void*,int id){if(id==keys.nameToKey("OptionsMenu.wnd:OptionsMenuParent"))return &options;if(id==keys.nameToKey("ExtrasMenu.wnd:ExtrasMenuParent"))return extra;return nullptr;}
 void winSetModal(GameWindow*w){modals.push_back(w);}void winUnsetModal(GameWindow*w){assert(!modals.empty()&&modals.back()==w);modals.pop_back();}
 void winSetFocus(GameWindow*w){focus=w;}
}wm,*TheWindowManager=&wm;
void gxExtrasBackdropDraw(GameWindow*,WinInstanceData*){}
struct WindowLayout{GameWindow root;bool shown=false;void runInit(void*);void runShutdown(void*);void hide(bool b){shown=!b;}void bringForward(){}void destroyWindows(){wm.extra=nullptr;++destroyed;}};
void deleteInstance(WindowLayout*p){delete p;}
int GadgetSliderGetPosition(GameWindow*w){return w->val;}void GadgetSliderSetPosition(GameWindow*w,int v){w->val=v;}
GameWindow maxSlider,minSlider,pitchSlider,scrollSlider,distanceSlider;
static GameWindow *sliderMaxCameraHeight=nullptr,*sliderMinCameraHeight=nullptr,*sliderCameraPitch=nullptr,*sliderScrollSpeed=nullptr,*sliderDrawDistance=nullptr;
static OptionPreferences *pref=nullptr;
static WindowLayout *s_extrasLayout=nullptr;static OptionPreferences *s_optionsPreferences=nullptr;
static const int GX_EXTRA_CAMERA_SCALE=4;
const int SLIDER_MAX_CAMERA_HEIGHT_MIN=400,SLIDER_MAX_CAMERA_HEIGHT_MAX=3600,SLIDER_MIN_CAMERA_HEIGHT_MIN=50,SLIDER_MIN_CAMERA_HEIGHT_MAX=300,SLIDER_CAMERA_PITCH_MIN=20,SLIDER_CAMERA_PITCH_MAX=60,SLIDER_SCROLL_SPEED_MIN=1,SLIDER_SCROLL_SPEED_MAX=200,SLIDER_DRAW_DISTANCE_MIN=100,SLIDER_DRAW_DISTANCE_MAX=200;
struct Global{float m_maxCameraHeight=500,m_minCameraHeight=80,m_cameraPitch=37,m_keyboardScrollFactor=1,m_terrainDrawDistanceScale=1.05;}global,*TheWritableGlobalData=&global;
struct Logic{bool interactive=true;bool isInInteractiveGame(){return interactive;}}logic,*TheGameLogic=&logic;
struct View{bool scripted=false;int limits=0,pitches=0;float pitch=0;void setCameraHeightAboveGroundLimitsToDefault(){++limits;}bool isDoingScriptedCamera(){return scripted;}void setPitch(float p){++pitches;pitch=p;}}view,*TheTacticalView=&view;
void CloseExtrasMenu();void ExtrasMenuShutdown(WindowLayout*,void*);WindowMsgHandledType ExtrasMenuSystem(GameWindow*,unsigned,uintptr_t,uintptr_t);
void WindowLayout::runInit(void*){
 pref=new OptionPreferences;(*pref)["UntouchedDiskSetting"]="original";
 sliderMaxCameraHeight=&maxSlider;sliderMinCameraHeight=&minSlider;sliderCameraPitch=&pitchSlider;sliderScrollSpeed=&scrollSlider;sliderDrawDistance=&distanceSlider;
 maxSlider.val=2000;minSlider.val=80;pitchSlider.val=37;scrollSlider.val=100;distanceSlider.val=105;
 ExtrasMenuSystem(&root,GWM_CREATE,0,0);
}
void WindowLayout::runShutdown(void*){++shutdowns;ExtrasMenuShutdown(this,nullptr);}
WindowLayout*WM::winCreateLayout(const char*name){assert(std::string(name)=="ExtrasMenu.wnd");if(missing)return nullptr;auto*l=new WindowLayout;extra=noRoot?nullptr:&l->root;return l;}
'''
code=code.replace('#include <map>', '#include <map>\n#include <vector>')
for signature in ['void CloseExtrasMenu()', 'void OpenExtrasMenu(', 'void ExtrasMenuShutdown(', 'static void saveExtras()', 'static void setDefaults()', 'WindowMsgHandledType ExtrasMenuSystem(', 'WindowMsgHandledType ExtrasMenuInput(']:code+='\n'+function(signature)+'\n'
code+=r'''
void click(const char*name){GameWindow control;control.id=keys.nameToKey(name);ExtrasMenuSystem(wm.extra,GBM_SELECTED,(uintptr_t)&control,0);}
int main(){
 OptionPreferences draft;draft["PendingMainSetting"]="keep draft";wm.modals.push_back(&wm.options);
 wm.missing=true;OpenExtrasMenu(&draft);assert(!s_extrasLayout&&wm.modals.size()==1&&writes==0);wm.missing=false;
 wm.noRoot=true;OpenExtrasMenu(&draft);assert(!s_extrasLayout&&wm.modals.size()==1);wm.noRoot=false;
 OpenExtrasMenu(&draft);assert(s_extrasLayout&&wm.modals.size()==2&&wm.focus==wm.extra&&wm.extra->hasDraw&&s_extrasLayout->shown);
 OpenExtrasMenu(&draft);assert(wm.modals.size()==2);click("ExtrasMenu.wnd:ButtonBack");assert(!s_extrasLayout&&wm.modals.size()==1&&wm.focus==&wm.options&&writes==0);
 OpenExtrasMenu(&draft);ExtrasMenuInput(wm.extra,GWM_CHAR,KEY_ESC,0);assert(s_extrasLayout);ExtrasMenuInput(wm.extra,GWM_CHAR,KEY_ESC,KEY_STATE_UP);assert(!s_extrasLayout&&wm.modals.size()==1&&writes==0);
 OpenExtrasMenu(&draft);maxSlider.val=2800;minSlider.val=120;pitchSlider.val=45;scrollSlider.val=150;distanceSlider.val=130;
 click("ExtrasMenu.wnd:ButtonAccept");assert(writes==1&&!s_extrasLayout&&global.m_maxCameraHeight==700&&global.m_minCameraHeight==120);assert(draft["MaxCameraHeight"]=="700"&&draft["PendingMainSetting"]=="keep draft");assert(view.limits==1&&view.pitches==1&&std::fabs(view.pitch-DEG_TO_RADF(45))<0.001);
 OpenExtrasMenu(&draft);view.scripted=true;maxSlider.val=99999;minSlider.val=-99;pitchSlider.val=90;scrollSlider.val=999;distanceSlider.val=999;
 click("ExtrasMenu.wnd:ButtonAccept");assert(global.m_maxCameraHeight==900&&global.m_minCameraHeight==50&&global.m_cameraPitch==60&&global.m_keyboardScrollFactor==2&&global.m_terrainDrawDistanceScale==2);assert(view.pitches==1);
 OpenExtrasMenu(&draft);maxSlider.val=400;minSlider.val=300;saveExtras();assert(global.m_maxCameraHeight>=global.m_minCameraHeight);click("ExtrasMenu.wnd:ButtonDefaults");assert(maxSlider.val==2000&&minSlider.val==80);CloseExtrasMenu();
 const int oldDestroyed=destroyed;CloseExtrasMenu();assert(destroyed==oldDestroyed&&wm.modals.size()==1);
 puts("PASS production Extras: missing layout, missing root, modal ownership, duplicate open, cancel, Escape, apply/draft persistence, bounds, defaults and scripted camera guard");
}
'''
p=OUT/'r3_extras.cpp';p.write_text(code)
subprocess.run(['g++','-std=c++17','-Werror=return-type',str(p),'-o',str(OUT/'r3_extras')],check=True)
subprocess.run([str(OUT/'r3_extras')],check=True)
asset=ROOT/'android/app/src/main/assets/gamedata/Window/ExtrasMenu.wnd';assert asset.read_bytes().startswith(b'FILE_VERSION = 2;')
assert 'TheShell->push' not in function('void OpenExtrasMenu(')
assert 'TheShell->pop' not in s
print('PASS Extras asset/header and no shell-stack transitions')

# Match the actual retail parser, which accepts named status/style tokens only.
parser=(ROOT/'GeneralsMD/Code/GameEngine/Source/GameClient/GUI/GameWindowManagerScript.cpp').read_text()
def allowed(name):
 body=parser.split('const char *const '+name+'[] =',1)[1].split('};',1)[0]
 return set(re.findall(r'"([^"\n]+)"',body))
text=asset.read_text()
for name,key in [('WindowStyleNames','STYLE'),('WindowStatusNames','STATUS')]:
 values=allowed(name)
 for expr in re.findall(r'\b'+key+r' = ([^;]+);',text):assert set(expr.split('+'))<=values,expr
assert text.count('STYLE = HORZSLIDER+MOUSETRACK;')==5
assert 'PassSelectedButtonsToParentSystem' not in text
assert text.count('STATICTEXTDATA = CENTERED: 1;')==6
group=(ROOT/'android/app/src/main/assets/gamedata/Window/GroupPanel.wnd').read_text()
for block in re.findall(r'WINDOWTYPE = PUSHBUTTON;.*?END',group,re.S):
 assert 'SYSTEMCALLBACK = "[None]";' in block # retain native GGM_SET_LABEL and owner delivery
print('PASS retail Extras styles/status, native slider/static/button callbacks and army label delivery')
