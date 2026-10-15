#!/usr/bin/env python3
"""Compile production press cases: repeated clicks must not reuse old drag anchors."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
source = (root / 'Core/GameEngine/Source/GameClient/MessageStream/MetaEvent.cpp').read_text()
start = source.index('case GameMessage::MSG_RAW_MOUSE_LEFT_BUTTON_DOWN:', source.index('void MetaEventTranslator::onMouseEvent'))
end = source.index('case GameMessage::MSG_RAW_MOUSE_LEFT_BUTTON_UP:', start)
cases = source[start:end]
names = ['LEFT_BUTTON_DOWN', 'MIDDLE_BUTTON_DOWN', 'RIGHT_BUTTON_DOWN',
         'LEFT_DOUBLE_CLICK', 'MIDDLE_DOUBLE_CLICK', 'RIGHT_DOUBLE_CLICK']
code = r'''
#include <cassert>
#include <cstdio>
#define FALLTHROUGH [[fallthrough]]
constexpr bool TRUE = true, FALSE = false;
struct Point { int x, y; };
struct Argument { Point pixel; };
struct GameMessage {
 enum Type { ENUMS };
 Type type; Argument arg;
 Type getType() const { return type; }
 const Argument* getArgument(int) const { return &arg; }
};
Point m_mouseDownPosition[3]{};
bool m_nextUpShouldCreateDoubleClick[3]{};
void press(const GameMessage* msg) {
 int index = 3;
 switch (msg->getType()) { CASES }
}
int main() {
 for (int button = 0; button < 3; ++button) {
  GameMessage msg{static_cast<GameMessage::Type>(button), {{100,100}}};
  press(&msg);
  assert(!m_nextUpShouldCreateDoubleClick[button]);
  // SDL can classify nearby presses as double clicks even when the game's
  // much smaller drag threshold would reject the distance from the old press.
  for (int x : {112,124,136}) {
   msg.type = static_cast<GameMessage::Type>(button + 3);
   msg.arg.pixel = {x,105};
   press(&msg);
   assert(m_nextUpShouldCreateDoubleClick[button]);
   assert(m_mouseDownPosition[button].x == x);
   assert(m_mouseDownPosition[button].y == 105);
   // A stationary release has zero region; a genuine drag still has distance.
   assert(x - m_mouseDownPosition[button].x == 0);
   assert(x + 20 - m_mouseDownPosition[button].x == 20);
  }
 }
 puts("PASS production press cases: all buttons, repeated nearby clicks, drag anchors");
}
'''.replace('ENUMS', ','.join('MSG_RAW_MOUSE_' + n for n in names)).replace('CASES', cases)
code = '#include <initializer_list>\n' + code
with tempfile.TemporaryDirectory(prefix='gx-repeat-press-') as directory:
    path = Path(directory)
    (path / 'test.cpp').write_text(code)
    subprocess.run(['g++', '-std=c++17', str(path / 'test.cpp'), '-o', str(path / 'test')], check=True)
    subprocess.run([str(path / 'test')], check=True)
