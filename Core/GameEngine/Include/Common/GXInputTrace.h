#pragma once
#include "Common/GXTabletControls.h"
#include <cstdarg>
#include <chrono>

// GeneralsX @feature Codex 16/10/2026 Local opt-in bounded input pipeline trace; never log text/motion.
namespace GXInputTrace {
inline bool enabled() {
    static const bool active=[] {
        if (GXTabletControls::get().diagnostics) return true;
        FILE *legacy=fopen("gx_input_trace.txt","r");
        if (!legacy) return false;
        fclose(legacy);return true;
    }();
    return active;
}
inline void record(const char *stage,const char *format,...) {
    if (!enabled()) return;
    FILE *file=fopen("gx_input_trace.log","a+");if (!file) return;
    if (fseek(file,0,SEEK_END)==0 && ftell(file)>512*1024) {
        fclose(file);file=fopen("gx_input_trace.log","w");if (!file)return;
        fputs("[trace wrapped at 512 KiB]\n",file);
    }
    const auto now=std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::steady_clock::now().time_since_epoch()).count();
    fprintf(file,"%lld %s ",(long long)now,stage);
    va_list args;va_start(args,format);vfprintf(file,format,args);va_end(args);
    fputc('\n',file);fclose(file);
}
}
