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

#HACK this adds two missing entries to pygment's color table
formatter.xterm_colors.append((0xe4, 0xe4, 0xe4))
formatter.xterm_colors.append((0xee, 0xee, 0xee))

pallette = formatter.xterm_colors
basecolors = formatter.xterm_colors[:16]
colorcube = formatter.xterm_colors[16:233]
color_inc = 255/5
greyscale = formatter.xterm_colors[233:]
diag = (3*255*255)**0.5
greyscale_inc = 10
ogrey = (3*18*18)**(1/2)
r3 = 3**0.5

def closest_color(c):
	r, g, b, _ = c
	cdist = lambda c1, c2: (c1[0]-c2[0])*(c1[0]-c2[0]) + (c1[1]-c2[1])*(c1[1]-c2[1]) + (c1[2]-c2[2])*(c1[2]-c2[2])

	#distance to next color on the 24-value greyscale slide
	agrey = round(((r+g+b)/r3-ogrey)/greyscale_inc)
	grey = basecolors[0]
	if agrey < 0:
		agrey = 0
	elif agrey >= len(greyscale):
		agrey = 15
	else:
		agrey = 233+agrey
	grey = pallette[agrey]
	dgrey = cdist(grey, c)

	#distance to the next color on the 6*6*6 color cube
	nr, ng, nb = round(r/color_inc), round(g/color_inc), round(b/color_inc)
	nrgb = nr*36 + ng*6 + nb
	rgb = colorcube[nrgb]
	nrgb += 16
	drgb = cdist(rgb, c)

	best, bestc, dbest = (nrgb, rgb, drgb) if drgb < dgrey else (agrey, grey, dgrey)
	for i, c in enumerate(basecolors):
		d = cdist(bestc, c)
		if d < dbest:
			dbest, bestc, best = d, c, i

	return best

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
		bgd[color] = '\033[48;5;'+str(formatter._closest_color(color))+'m'
		return bgd[color]

	def fgescape(color):
		nonlocal fg, fgd
		if fg == color:
			return ''
		fg=color
		fgd[color] = '\033[38;5;'+str(formatter._closest_color(color))+'m'
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
