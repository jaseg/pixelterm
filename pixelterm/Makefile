
all: libpixelterm


libpixelterm: pixelterm.c xtermcolors.c xtermcolors.h
	gcc -shared -fPIC -std=c11 -Wall -lm -o libpixelterm.so -g xtermcolors.c pixelterm.c

clean:
	rm libpixelterm.so
