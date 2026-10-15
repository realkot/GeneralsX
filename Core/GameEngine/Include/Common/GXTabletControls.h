#pragma once
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cerrno>
#if defined(__ANDROID__)
#include <unistd.h>
#include "GXAndroidIdentity.h"
#endif

// GeneralsX @feature Codex 16/10/2026 Startup-only tablet preferences, independent of legacy ABI.
namespace GXTabletControls {
struct Settings {
    int diagnostics = 0, attackMove = 1;
    int panelScale = 100, panelWidth = 100, panelOpacity = 100;
    int panelLeft = 0, panelBottom = 0, panelMask = 31, panelCollapsed = 0;
    int fitLabels = 1, cursorPercent = 200, cursorOutline = 0;
};
inline int clamp(long value, int low, int high) {
    return value < low ? low : value > high ? high : (int)value;
}
inline void parse(FILE *file, Settings &s) {
    if (!file) return;
    char line[192];
    while (fgets(line, sizeof(line), file)) {
        if (!strchr(line, '\n') && !feof(file)) {
            int c; while ((c=fgetc(file))!=EOF && c!='\n') {}
            continue;
        }
        char *eq=strchr(line,'='); if (!eq) continue;
        *eq++=0;
        errno=0; char *end=nullptr; long value=strtol(eq,&end,10);
        if (errno || end==eq) continue;
        while (*end==' ' || *end=='\r' || *end=='\n' || *end=='\t') ++end;
        if (*end) continue;
        struct Field { const char *name; int *value; int low,high; };
        Field fields[] = {
            {"diagnostics",&s.diagnostics,0,1},{"attackMove",&s.attackMove,0,1},
            {"panelScale",&s.panelScale,75,150},{"panelWidth",&s.panelWidth,80,180},
            {"panelOpacity",&s.panelOpacity,25,100},{"panelLeft",&s.panelLeft,0,100},
            {"panelBottom",&s.panelBottom,0,100},{"panelMask",&s.panelMask,0,31},
            {"panelCollapsed",&s.panelCollapsed,0,1},{"fitLabels",&s.fitLabels,0,1},
            {"cursorPercent",&s.cursorPercent,100,250},{"cursorOutline",&s.cursorOutline,0,1}
        };
        for (auto &f:fields) if (!strcmp(line,f.name)) { *f.value=clamp(value,f.low,f.high); break; }
    }
}
inline const Settings &get() {
    static const Settings value=[] {
        Settings s;
#if defined(__ANDROID__)
        char path[256];
        const int userId=(int)(getuid()/100000);
        snprintf(path,sizeof(path),"/data/user/%d/" GX_ANDROID_APP_ID "/files/tablet_controls.ini",userId);
        FILE *file=fopen(path,"r"); if (file) { parse(file,s); fclose(file); }
#endif
        return s;
    }();
    return value;
}
}
