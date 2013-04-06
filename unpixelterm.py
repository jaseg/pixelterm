#!/usr/bin/env python

import os, sys, argparse
#NOTE: This script uses pygments for X256->RGB conversion since pygments is
#readily available. If you do not like pygments (e.g. because it is large),
#you could patch in something like https://github.com/magarcia/python-x256
#(but don't forget to send me a pull request ;)
from pygments.formatters import terminal256
from PIL import Image, PngImagePlugin
try:
	import re2 as re
except:
	import re

formatter = terminal256.Terminal256Formatter()

def parse_escape_sequence(seq):
	codes = list(map(int, seq.lstrip('\x1b[').rstrip('m').split(';')))
	fg, bg = None, None
	i = 0
	while i<len(codes):
		if codes[i] in [38, 48]:
			if codes[i+1] == 5:
				c = formatter.xterm_colors[codes[i+2]]
				fg, bg = (c, bg) if codes[i] == 38 else (fg, c)
				i += 2
		elif codes[i] == 39:
			fg = (0,0,0,0)
		elif codes[i] == 49:
			bg = (0,0,0,0)
		i += 1
	return fg, bg

def unpixelterm(text):
	lines = text.split('\n')
	metadata = {}
	try:
		first = lines.index('$$$')
		second = lines[first+1:].index('$$$')
		foo = [ line.split(': ') for line in lines[first+1:second] if line != '' ]
		d = {}
		for k,v in foo:
			if k not in ['WIDTH', 'HEIGHT']:
				d[k.lower()] = d.get(k.lower(), []) + [v]
		metadata.update(d)
		lines[first:] = lines[first+1+second+1:]
	except:
		pass

	h = len(lines)*2
	w = max([ len(re.sub(r'\x1b\[[0-9;]+m|\$.*\$', '', line)) for line in lines ])
	img = Image.new('RGBA', (w, h))
	fg, bg = (0,0,0,0), (0,0,0,0)
	x, y = 0, 0
	for line in lines:
		for escapeseq, specialstr, char in re.findall(r'(\x1b\[[0-9;]+m)|(\$[^$]+\$)|(.)', line, re.DOTALL):
			if escapeseq:
				nfg, nbg = parse_escape_sequence(escapeseq)
				fg, bg = nfg or fg, nbg or bg
			elif specialstr:
				if specialstr == '$\\$':
					img.putpixel((x, y), (255, 0, 0, 127))
					img.putpixel((x, y+1), (255, 0, 0, 127))
					x += 1
				elif specialstr == '$/$':
					img.putpixel((x, y), (0, 0, 255, 127))
					img.putpixel((x, y+1), (0, 0, 255, 127))
					x += 1
				else: #(should be a) balloon
					bw = int(re.match(r'\$balloon([0-9]*)\$', specialstr).group(1))
					for i in range(x, x+bw):
						img.putpixel((i, y), (0, 255, 0, 127))
						img.putpixel((i, y+1), (0, 255, 0, 127))
					x += bw
			elif char:
				#Da magicks: ▀█▄
				c = {' ': (bg, bg),
					 '█': (fg, fg),
					 '▀': (fg, bg),
					 '▄': (bg, fg)}[char]
				img.putpixel((x, y), c[0])
				img.putpixel((x, y+1), c[1])
				x += 1
		x, y = 0, y+2
	return img, metadata

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Convert images rendered by pixelterm-like utilities back to PNG')
	parser.add_argument('input', type=argparse.FileType('r'))
	parser.add_argument('output', type=str)
	args = parser.parse_args()
	img, metadata = unpixelterm(args.input.read())
	print('Metadata:')
	pnginfo = PngImagePlugin.PngInfo()
	for k, v in metadata.items():
		print('{:15}: {}'.format(k, '/'.join(v)))
		pnginfo.add_text(k, '/'.join(v))
	img.save(args.output, 'PNG', pnginfo=pnginfo)
