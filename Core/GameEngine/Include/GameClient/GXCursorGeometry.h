#pragma once
#include <algorithm>
#include <vector>

// GeneralsX @feature Codex 16/10/2026 Keep scaled cursor pixels and hotspot in one coordinate space.
namespace GXCursorGeometry {
inline int scale(int value,int percent) { return std::max(1,(value*percent+50)/100); }
inline int hotspot(int value,int percent,int extent) {
    return std::max(0,std::min(extent-1,(value*percent+50)/100));
}
inline void outline(unsigned char *rgba,int width,int height,int pitch) {
    if (!rgba || width<=0 || height<=0 || width>512 || height>512 || pitch<width*4) return;
    std::vector<unsigned char> alpha(width*height);
    for(int y=0;y<height;++y)for(int x=0;x<width;++x)alpha[y*width+x]=rgba[y*pitch+x*4+3];
    for(int y=0;y<height;++y)for(int x=0;x<width;++x) {
        if(alpha[y*width+x]>16)continue;
        bool edge=false;
        for(int dy=-1;dy<=1;++dy)for(int dx=-1;dx<=1;++dx) {
            int nx=x+dx,ny=y+dy;
            if(nx>=0&&ny>=0&&nx<width&&ny<height&&alpha[ny*width+nx]>16)edge=true;
        }
        if(edge) { unsigned char *p=rgba+y*pitch+x*4;p[0]=p[1]=p[2]=0;p[3]=255; }
    }
}
}
