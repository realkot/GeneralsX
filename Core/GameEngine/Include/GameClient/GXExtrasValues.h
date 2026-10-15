#pragma once
#include <algorithm>

// GeneralsX @feature Codex 16/10/2026 Validate exact Extras input before touching preferences.
namespace GXExtrasValues {
template<class Char> inline bool digits(const Char *text,int length,int &value) {
    if(!text || length<=0 || length>6)return false;
    int result=0;
    for(int i=0;i<length;++i) {
        if(text[i]<'0'||text[i]>'9')return false;
        result=result*10+(text[i]-'0');
    }
    value=result;return true;
}
inline int normalize(int value,int low,int high,int quantum=1) {
    value=std::max(low,std::min(high,value));
    return std::max(low,std::min(high,value/quantum*quantum));
}
}
