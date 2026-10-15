#pragma once
#include <algorithm>

// GeneralsX @feature Codex 15/10/2026 Pure screen-space policy shared by runtime and QA.
// A wide screen puts the army column below the HUD's top, in its left gap. When that
// gap is too narrow, keep readable buttons above the HUD rather than cover its controls.
namespace GXArmyPanelLayout {
struct Layout {
    int x, y, width, height, gap;
    int rowX, rowY, cellWidth, cellHeight, columns, rows;
};
inline Layout calculate(int width, int height, int barLeft, int barTop,
                        int safeLeft, int safeBottom, float fontScale,
                        int scalePercent=100, int widthPercent=100,
                        int leftPercent=0, int bottomPercent=0, int buttons=5) {
    buttons=std::max(0,std::min(5,buttons));
    const int slots=buttons+1;
    const float resolution = std::max(0.25f, std::min(width/800.0f, height/600.0f));
    const float unit = resolution * std::max(1.0f, fontScale) * std::max(75,std::min(150,scalePercent))/100.0f;
    const int margin = std::max(4, (int)(6*resolution));
    const int gap = std::max(2, (int)(4*resolution));
    const int available = barLeft - safeLeft - 2*margin;
    const int bottom = std::max(1, height - safeBottom - margin);
    const int gapHeight = bottom - barTop;
    const bool beside = available >= (int)(64*unit) && gapHeight >= (int)(120*unit) + 5*gap;
    Layout p{};
    p.x = safeLeft + margin;
    p.gap = gap;
    p.width = std::max(1, std::min((int)(80*unit*std::max(80,std::min(180,widthPercent))/100.0f), beside ? available : width-p.x-margin));
    const int space = beside ? gapHeight : std::max(1, barTop-margin);
    p.height = std::max(1, std::min((int)(34*unit), (space-(slots-1)*gap)/slots));
    p.y = std::max(margin, (beside ? bottom : barTop-margin) - slots*p.height-(slots-1)*gap);
    p.columns = beside ? 2 : 5;
    p.rows = 10 / p.columns;
    p.cellWidth = beside ? std::max(1,(p.width-gap)/2) : std::max(1,std::min((int)(36*unit),(width-p.x-margin-4*gap)/5));
    p.cellHeight = beside ? std::max(1,std::min(p.height,(p.y-margin-(p.rows-1)*gap)/p.rows)) : p.height;
    p.rowX = beside ? p.x : p.x+p.width+gap;
    if (!beside) p.cellWidth=std::max(1,std::min((int)(36*unit),(width-p.rowX-margin-4*gap)/5));
    p.rowY = beside ? std::max(0,p.y-gap-p.rows*p.cellHeight-(p.rows-1)*gap) : p.y;
    // GeneralsX @feature Codex 16/10/2026 User offsets stay inside the available panel region.
    const int right=beside ? barLeft-margin : width-margin;
    const int contentRight=std::max(p.x+p.width,p.rowX+p.columns*p.cellWidth+(p.columns-1)*gap);
    const int shiftX=std::max(0,right-contentRight)*std::max(0,std::min(100,leftPercent))/100;
    p.x+=shiftX;p.rowX+=shiftX;
    const int shiftY=std::max(0,std::min(p.y,p.rowY)-margin)*std::max(0,std::min(100,bottomPercent))/100;
    p.y-=shiftY;p.rowY-=shiftY;
    return p;
}
}
