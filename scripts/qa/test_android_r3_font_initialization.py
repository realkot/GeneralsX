from pathlib import Path
import re
root=Path(__file__).resolve().parents[2]
prefix=root/'GeneralsMD/Code/GameEngine/Source/GameClient/GUI/GUICallbacks'
for name in ['GroupPanel.cpp','Menus/ExtrasMenu.cpp']:
 text=(prefix/name).read_text()
 assert 'winSetFont' not in text
 assert 'gx_army_font_baseline' not in text
options=(prefix/'Menus/OptionsMenu.cpp').read_text()
font=options.split('static void gxEnsureExtrasButton()',1)[1].split('void OptionsMenuInit',1)[0]
assert 'back->winGetInstanceData()->getFont()' in font
assert 'TheFontLibrary->getFont' not in font
for name in ['GroupPanel.wnd','ExtrasMenu.wnd']:
 text=(root/'android/app/src/main/assets/gamedata/Window'/name).read_text()
 sizes=[int(x) for x in re.findall(r'FONT = .*?SIZE: (\d+)',text)]
 assert sizes and all(1<=x<=18 for x in sizes),sizes
print('PASS native overlay fonts: no live font mutation, stock Options font reused, bounded original WND fonts, no temporary diagnostic switch')
