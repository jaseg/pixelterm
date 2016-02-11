#!/usr/bin/env python3

import ctypes

libpixelterm = ctypes.CDLL('./libpixelterm.so')
libpixelterm.termify_pixels.argtypes = ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint
libpixelterm.termify_pixels.restype  = ctypes.c_char_p
libpixelterm.free_str.argtypes = ctypes.c_char_p,

def termify_pixels(img):
    w, h = img.size
    res = libpixelterm.termify_pixels(img.tobytes(), w, h)
    if res:
        rv = res.decode()
#        libpixelterm.free_str(res)
        return rv
    return None

def main():
    import os, sys, argparse, os.path, json
    from PIL import Image, PngImagePlugin

    parser = argparse.ArgumentParser(description='Render pixel images on 256-color ANSI terminals')
    parser.add_argument('image', type=str, nargs='*')
    args = parser.parse_args()

    for f in args.image:
        img = Image.open(f).convert("RGBA")
        print(termify_pixels(img))

if __name__ == '__main__':
    main()

