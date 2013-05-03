#!/usr/bin/env python

import os, sys, argparse, os.path, json, time, signal, atexit
#NOTE: This script uses pygments for RGB->X256 conversion since pygments is
#readily available. If you do not like pygments (e.g. because it is large),
#you could patch in something like https://github.com/magarcia/python-x256
#(but don't forget to send me a pull request ;)
from pygments.formatters import terminal256
from PIL import Image, GifImagePlugin, ImageSequence

formatter = terminal256.Terminal256Formatter()
reset_sequence = terminal256.EscapeSequence(fg=formatter._closest_color(0,0,0), bg=formatter._closest_color(0,0,0)).reset_string()
clear_screen = '\033[H\033[2J'
cursor_invisible = '\033[?25l'
cursor_visible = '\033[?25h'

def termify_pixels(img):
	sx, sy = img.size
	out = ''

	fg,bg = None,None
	fgd,bgd = {},{}
	def bgescape(color):
		nonlocal bg, bgd
		if bg == color:
			return ''
		bg=color
		if color == (0,0,0,0):
			return '\033[49m'
		if color in bgd:
			return bgd[color]
		r,g,b,_ = color
		bgd[color] = '\033[48;5;'+str(formatter._closest_color(r,g,b))+'m'
		return bgd[color]

	def fgescape(color):
		nonlocal fg, fgd
		if fg == color:
			return ''
		fg=color
		r,g,b,_ = color
		fgd[color] = '\033[38;5;'+str(formatter._closest_color(r,g,b))+'m'
		return fgd[color]

	def balloon(x,y):
		if x+1 == img.size[0] or img.im.getpixel((x+1, y)) != (0,255,0,127):
			w = 1
			while x-w >= 0 and img.im.getpixel((x-w, y)) == (0,255,0,127):
				w += 1
			return '$balloon{}$'.format(w)
		return ''

	for y in range(0, sy, 2):
		for x in range(sx):
			coltop = img.im.getpixel((x, y))
			colbot = img.im.getpixel((x, y+1)) if y+1 < img.size[1] else (0,0,0,0)

			if coltop[3] == 127: #Control colors
				out += reset_sequence
				out += {(255, 0, 0, 127): lambda x,y:'$\\$',
						(0, 0, 255, 127): lambda x,y:'$/$',
						(0, 255, 0, 127): balloon
					   }.get(coltop, lambda x,y:' ')(x,y)
				continue

			if coltop[3] != 255:
				coltop = (0,0,0,0)
			if colbot[3] != 255:
				colbot = (0,0,0,0)

			#Da magicks: ▀█▄
			c,cf = '▀','█'
			te,be = fgescape,bgescape
			if coltop == (0,0,0,0) or ((coltop == bg or colbot == fg) and not colbot == (0,0,0,0)):
				c,cf,te,be = '▄',' ',be,te
			if colbot == coltop:
				c,te,be = cf,te,te
			out += te(coltop) + be(colbot) + c
		out = out.rstrip() + '\n'
	return out[:-1] + reset_sequence + '\n'

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Render pixel images on 256-color ANSI terminals')
	parser.add_argument('image', type=str)
	args = parser.parse_args()
	img = Image.open(args.image)
	frames = []
	palette = img.getpalette()
	for frame in ImageSequence.Iterator(img):
		f = frame.copy()
		#This works around a known bug in Pillow
		#See also: http://stackoverflow.com/questions/4904940/python-converting-gif-frames-to-png
		f.putpalette(palette)
		f = f.convert("RGBA")
		frames.append(termify_pixels(f))

	print(cursor_invisible)
	atexit.register(lambda:print(cursor_visible))
	signal.signal(signal.SIGTERM, lambda signum, stack_frame: exit(1))

	while True:
		for frame in frames:
			print(clear_screen, reset_sequence)
			print(frame)
			time.sleep(img.info['duration']/1000.0)

