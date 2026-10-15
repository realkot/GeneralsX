#pragma once
// GeneralsX @bugfix Codex 16/10/2026 A release after cancellation cannot complete an old click.
namespace GXPointerButtons {
inline bool accept(unsigned &held,unsigned mask,bool down) {
    if(!mask)return false;
    if(down) {held|=mask;return true;}
    if(!(held&mask))return false;
    held&=~mask;return true;
}
}
