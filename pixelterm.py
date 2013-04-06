#!/usr/bin/env python

import os, sys, argparse, os.path
#NOTE: This script uses pygments for RGB->X256 conversion since pygments is
#readily available. If you do not like pygments (e.g. because it is large),
#you could patch in something like https://github.com/magarcia/python-x256
#(but don't forget to send me a pull request ;)
from pygments.formatters import terminal256
from PIL import Image, PngImagePlugin

formatter = terminal256.Terminal256Formatter()
reset_sequence = terminal256.EscapeSequence(fg=formatter._closest_color(0,0,0), bg=formatter._closest_color(0,0,0)).reset_string()

def termify_pixels(img):
	sx, sy = img.size
	out = ''

	fg,bg = None,None
	fgd,bgd = {},{}
	def bgescape(color):
		nonlocal bg
		if bg == color:
			return ''
		bg=color
		r,g,b,a = color
		if color in bgd:
			return bgd[color]
		bgd[color] = terminal256.EscapeSequence(bg=formatter._closest_color(r,g,b)).color_string()
		if color == (0,0,0,0):
			bgd[color] = terminal256.EscapeSequence(bg=formatter._closest_color(0,0,0)).reset_string()
		return bgd[color]

	def fgescape(color):
		nonlocal fg
		if fg == color:
			return ''
		fg=color
		r,g,b,_ = color
		fgd[color]= terminal256.EscapeSequence(fg=formatter._closest_color(r,g,b)).color_string()
		return fgd[color]

	def balloon(x,y):
		if x+1 == img.size[0] or img.getpixel((x+1, y)) != (0,255,0,127):
			w = 1
			while x-w >= 0 and img.getpixel((x-w, y)) == (0,255,0,127):
				w += 1
			return '$balloon{}$'.format(w)
		return ''

	for y in range(0, sy, 2):
		for x in range(sx):
			coltop = img.getpixel((x, y))
			colbot = img.getpixel((x, y+1)) if y+1 < img.size[1] else (0,0,0,0)

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
	parser.add_argument('image', type=str, nargs='*')
	parser.add_argument('-d', '--output-dir', type=str, help='Output directory (if not given, output to stdout)')
	args = parser.parse_args()
	for f in args.image:
		img = Image.open(f).convert("RGBA")
		if args.output_dir:
			print(f)
			foo, _, _ = f.rpartition('.png')
			output = os.path.join(args.output_dir, os.path.basename(foo)+'.pony')
			metadata = '$$$\n' +\
				'\n'.join([ k.upper()+': '+img.info[k] for k in sorted(img.info.keys()) if k != 'comment' ]) +\
				'\n' + img.info.get('comment', '') +\
				'\n$$$\n'
			with open(output, 'w') as of:
				of.write(metadata)
				of.write(termify_pixels(img))
		else:
			print(termify_pixels(img))
