#!/usr/bin/env python

import os, sys, argparse
from pygments.formatters import terminal256
from PIL import Image, PngImagePlugin

def termify_pixels(img):
	sx, sy = img.size
	out = ''
	formatter = terminal256.Terminal256Formatter()
	fg,bg = None,None
	def bgescape(color):
		nonlocal bg
		if bg == color:
			return ''
		bg=color
		r,g,b,a = color
		if color == (0,0,0,0):
			return terminal256.EscapeSequence(bg=formatter._closest_color(0,0,0)).reset_string()
		return terminal256.EscapeSequence(bg=formatter._closest_color(r,g,b)).color_string()
	def fgescape(color):
		nonlocal fg
		if fg == color:
			return ''
		fg=color
		r,g,b,_ = color
		return terminal256.EscapeSequence(fg=formatter._closest_color(r,g,b)).color_string()
	#NOTE: This ignores the last line if there is an odd number of lines.
	for y in range(0, sy-1, 2):
		for x in range(sx):
			coltop = img.getpixel((x, y))
			colbot = img.getpixel((x, y+1))
			if coltop[3] != 255:
				coltop = (0,0,0,0)
			if colbot[3] != 255:
				colbot = (0,0,0,0)
			c  = '▀'
			te = fgescape
			be = bgescape
			#Da magicks: ▀█▄
			if coltop == (0,0,0,0):
				c,te,be = '▄',be,te
			if colbot == coltop:
				c = ' '
			out += te(coltop)
			out += be(colbot)
			out += c
		out += '\n'
	return out

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Render pixel images on 256-color ANSI terminals')
	parser.add_argument('image', type=str)
	args = parser.parse_args()
	img = Image.open(args.image).convert("RGBA")
	print(termify_pixels(img))
