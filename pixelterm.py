#!/usr/bin/env python

import os, sys, argparse
from pygments.formatters import terminal256
from PIL import Image, PngImagePlugin

def termify_pixels(img):
	sx, sy = img.size
	out = ''
	formatter = terminal256.Terminal256Formatter()
	def bgescape(color):
		r,g,b,a = color
		if color == (0,0,0,0):
			return terminal256.EscapeSequence(bg=formatter._closest_color(0,0,0)).reset_string()
		return terminal256.EscapeSequence(bg=formatter._closest_color(r,g,b)).color_string()
	def fgescape(color):
		r,g,b,_ = color
		return terminal256.EscapeSequence(fg=formatter._closest_color(r,g,b)).color_string()
	#NOTE: This ignores the last line if there is an odd number of lines.
	for y in range(0, sy-1, 2):
		lastfg, lastbg = None, None
		for x in range(sx):
			coltop = img.getpixel((x, y))
			colbot = img.getpixel((x, y+1))
			if coltop[3] != 255:
				coltop = (0,0,0,0)
			if colbot[3] != 255:
				colbot = (0,0,0,0)
			if coltop == colbot:
				if lastfg == coltop:
					out += '█'
				elif lastbg == coltop:
					out += ' '
				else:
					out += bgescape(coltop)
					lastfg = coltop
					out += ' '
			else:
				if coltop == (0,0,0,0):
					if lastfg != colbot:
						out += fgescape(colbot)
						lastfg = colbot
					if lastbg != coltop:
						out += bgescape(coltop)
						lastbg = coltop
					out += '▄'
				elif colbot == (0,0,0,0): 
					if lastfg != coltop:
						out += fgescape(coltop)
						lastfg = coltop
					if lastbg != colbot:
						out += bgescape(colbot)
						lastbg = colbot
					out += '▀'
				elif lastbg == coltop:
					if lastfg != colbot:
						out += fgescape(colbot)
						lastfg = colbot
					out += '▄'
				elif lastbg == colbot:
					if lastfg != coltop:
						out += fgescape(coltop)
						lastfg = coltop
					out += '▀'
				else:
					if lastfg == coltop:
						out += bgescape(coltop)
						lastbg = coltop
						out += '▀'
					elif lastfg == colbot:
						out += bgescape(colbot)
						lastbg = colbot
						out += '▄'
					else:
						out += fgescape(coltop)
						lastfg = coltop
						out += bgescape(colbot)
						lastbg = colbot
						out += '▀'
		out += '\n'
	return out

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Render pixel images on 256-color ANSI terminals')
	parser.add_argument('image', type=str)
	args = parser.parse_args()
	img = Image.open(args.image).convert("RGBA")
	print(termify_pixels(img))
