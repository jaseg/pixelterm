#ifndef __XTERMCOLORS_H__
#define __XTERMCOLORS_H__

#include <stdint.h>

union rgba_color {
    struct __attribute__((__packed__)) {
        unsigned char r;
        unsigned char g;
        unsigned char b;
        unsigned char a;
    } c;
    uint32_t i;
};

struct yuv_color {
    float y;
    float u;
    float v;
};

int xterm_closest_color(uint32_t rgba_col);
extern struct yuv_color xtermcolors_yuv[240];

#endif//__XTERMCOLORS_H__
