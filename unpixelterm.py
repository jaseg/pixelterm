#!/usr/bin/env python

import os, sys, argparse, os.path
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
#HACK this adds two missing entries to pygment's color table
formatter.xterm_colors.append((0xe4, 0xe4, 0xe4))
formatter.xterm_colors.append((0xee, 0xee, 0xee))

def parse_escape_sequence(seq):
	codes = list(map(int, seq[2:-1].split(';')))
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
		elif codes[i] == 0:
			fg, bg = (0,0,0,0), (0,0,0,0)
		i += 1
	return fg, bg

def unpixelterm(text):
	lines = text.split('\n')
	metadata = {}
	try:
		first = lines.index('$$$')
		second = lines[first+1:].index('$$$')
		comment = []
		d = {}
		for l in lines[first+1:second+1]:
			parts = l.split(': ')
			if len(parts) == 2:
				k,v = parts
				if k not in ['WIDTH', 'HEIGHT']:
					d[k.lower()] = d.get(k.lower(), []) + [v]
			elif l != '':
				comment.append(l)
		if comment:
			d['comment'] = d.get('comment', []) + comment
		metadata.update(d)
		lines[first:] = lines[first+1+second+1:]
	except:
		pass

	if lines[-1] == '\x1b[0m':
		lines = lines[:-1]

	h = len(lines)*2
	w = max([ len(re.sub(r'\x1b\[[0-9;]+m|\$balloon.*\$|\$', '', line)) for line in lines ])
	bw = int(re.search(r'\$balloon([0-9]*)\$', text).group(1) or '1')
	if bw > w: #Fuck special cases.
		w = bw
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
	parser.add_argument('-v', '--verbose', action='store_true')
	output_group = parser.add_mutually_exclusive_group()
	output_group.add_argument('-o', '--output', type=str, help='Output file name, defaults to ${input%.pony}.png')
	output_group.add_argument('-d', '--output-dir', type=str, help='Place output files here')
	parser.add_argument('input', type=argparse.FileType('r'), nargs='+')
	args = parser.parse_args()
	if len(args.input) > 1 and args.output:
		parser.print_help()
		print('You probably do not want to overwrite the given output file {} times.'.format(len(args.input)))
		sys.exit(1)

	for f in args.input:
		if len(args.input) > 1:
			print(f.name)
		img, metadata = unpixelterm(f.read())
		if args.verbose:
			print('Metadata:')
		pnginfo = PngImagePlugin.PngInfo()
		for k, v in metadata.items():
			if args.verbose:
				print('{:15}: {}'.format(k, '/'.join(v)))
			pnginfo.add_text(k, '/'.join(v))
		foo, _, _ = f.name.rpartition('.pony')
		output = args.output or foo+'.png'
		if args.output_dir:
			output = os.path.join(args.output_dir, os.path.basename(output))
		img.save(output, 'PNG', pnginfo=pnginfo)
