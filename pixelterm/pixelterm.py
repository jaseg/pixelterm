#!/usr/bin/env python

from pixelterm.xtermcolors import closest_color

reset_sequence = '\033[39;49m'

def termify_pixels(img, fill=False):
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
		bgd[color] = '\033[48;5;'+str(closest_color(r,g,b))+'m'
		return bgd[color]

	def fgescape(color):
		nonlocal fg, fgd
		if fg == color:
			return ''
		fg=color
		r,g,b,_ = color
		fgd[color] = '\033[38;5;'+str(closest_color(r,g,b))+'m'
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
		out = (out.rstrip() if bg == (0,0,0,0) and not fill else out) + '\n'
	return out[:-1] + reset_sequence + '\n'

