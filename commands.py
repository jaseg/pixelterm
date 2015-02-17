#!/usr/bin/env python

import os, sys, argparse, os.path, json, time, signal, atexit
from collections import defaultdict
from pixelterm.pixelterm import termify_pixels, reset_sequence
from pixelterm.unpixelterm import unpixelterm
from PIL import Image, PngImagePlugin, GifImagePlugin, ImageSequence
import re


def pixelterm():
	import os, sys, argparse, os.path, json
	from multiprocessing.dummy import Pool
	from PIL import Image, PngImagePlugin

	parser = argparse.ArgumentParser(description='Render pixel images on 256-color ANSI terminals')
	parser.add_argument('image', type=str, nargs='*')
	parser.add_argument('-d', '--output-dir', type=str, help='Output directory (if not given, output to stdout)')
	args = parser.parse_args()

	def convert(f):
		img = Image.open(f).convert("RGBA")
		if args.output_dir:
			print(f)
			foo, _, _ = f.rpartition('.png')
			output = os.path.join(args.output_dir, os.path.basename(foo)+'.pony')
			metadata = json.loads(img.info.get('pixelterm-metadata'))
			comment = metadata.get('_comment')
			if comment is not None:
				del metadata['_comment']
				comment = '\n'+comment
			else:
				comment = ''
			metadataarea = '$$$\n' +\
				'\n'.join([ '\n'.join([ k.upper() + ': ' + v for v in metadata[k] ]) for k in sorted(metadata.keys()) ]) +\
				comment + '\n$$$\n'
			with open(output, 'w') as of:
				of.write(metadataarea)
				of.write(termify_pixels(img))
		else:
			print(termify_pixels(img))

	p = Pool()
	p.map(convert, args.image)


def unpixelterm():
	import argparse, json

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
		pnginfo = PngImagePlugin.PngInfo()
		pnginfo.add_text('pixelterm-metadata', json.dumps(metadata))
		foo, _, _ = f.name.rpartition('.pony')
		output = args.output or foo+'.png'
		if args.output_dir:
			output = os.path.join(args.output_dir, os.path.basename(output))
		img.save(output, 'PNG', pnginfo=pnginfo)


clear_screen = '\033[H\033[2J'
home_cursor = '\033[H'
cursor_invisible = '\033[?25l'
cursor_visible = '\033[?25h'

def gifterm():
	parser = argparse.ArgumentParser(description='Render pixel images on 256-color ANSI terminals')
	parser.add_argument('image', type=str)
	parser.add_argument('-s', '--size', type=str, help='Terminal size, [W]x[H]')
	parser.add_argument('--serve', type=int, help='Serve via TCP on given port')
	args = parser.parse_args()

	tw, th = None, None
	if args.size:
		tw, th = map(int, args.size.split('x'))
	else:
		try:
			tw, th = os.get_terminal_size()
		except: # If this is not a regular terminal
			pass
	th = th*2

	img = Image.open(args.image)
	palette = img.getpalette()
	last_frame = Image.new("RGBA", img.size)
	frames = []

	for frame in ImageSequence.Iterator(img):
		#This works around a known bug in Pillow
		#See also: http://stackoverflow.com/questions/4904940/python-converting-gif-frames-to-png
		frame.putpalette(palette)
		c = frame.convert("RGBA")

		if img.info['background'] != img.info.get('transparency'):
			last_frame.paste(c, c)
		else:
			last_frame = c

		im = last_frame.copy()
		if (tw, th) != (None, None):
			im.thumbnail((tw, th), Image.NEAREST)
		frames.append(termify_pixels(im, True))

	if args.serve:
		from socketserver import ThreadingMixIn, TCPServer, BaseRequestHandler

		# Quote-Of-The-Day protocol implementation
		# See RFC865 ( https://tools.ietf.org/html/rfc865 ) for details.

		class ThreadingTCPServer(ThreadingMixIn, TCPServer): pass

		class QOTDHandler(BaseRequestHandler):
			def handle(self):
				try:
					self.request.sendall(bytes(cursor_invisible, "UTF-8"))
					while True:
						for frame in frames:
							self.request.sendall(bytes(home_cursor + reset_sequence, "UTF-8"))
							self.request.sendall(bytes(frame, "UTF-8"))
							time.sleep(min(1/10, img.info['duration']/1000.0))
				except:
					pass

		server = ThreadingTCPServer(('', args.serve), QOTDHandler)
		server.serve_forever()
	else:
		print(cursor_invisible)
		atexit.register(lambda:print(cursor_visible))
		signal.signal(signal.SIGTERM, lambda signum, stack_frame: exit(1))

		try:
			while True:
				for frame in frames:
					print(home_cursor)
					print(reset_sequence)
					print(frame)
					time.sleep(min(1/10, img.info['duration']/1000.0))
		except KeyboardInterrupt:
			pass


# Display an xterm-256color color palette on the terminal, including color ids

reset_sequence = '\033[39;49m'

def _esc(i):
	return '\033[48;5;'+str(i)+'m'

def colorcube():
	print(''.join([str(i).ljust(4) for i in range(16)]))
	print('    '.join([_esc(i) for i in range(16)])+'    ' + reset_sequence)

	for j in range(6):
		for k in range(6):
			c = 16+j*6+k*6*6
			print(''.join([str(c+i).ljust(4) for i in range(6)]))
			print('    '.join([_esc(c+i) for i in range(6)])+'    ' + reset_sequence)

	print(''.join([str(i).ljust(4) for i in range(16+6*6*6, 16+6*6*6+24)]))
	print('    '.join([_esc(i) for i in range(16+6*6*6, 16+6*6*6+24)])+'    ' + reset_sequence)


def pngmeta():
	parser = argparse.ArgumentParser(description='Print PNG metadata')
	parser.add_argument('image', type=str)
	args = parser.parse_args()
	img = Image.open(args.image)
	for k, v in img.info.items():
		print('{:15}: {}'.format(k, v))


def resolvecolor():
	import os, sys, argparse, os.path, json, re
	from pixelterm.xtermcolors import closest_color

	# Resolve HTML-style hex RGB color codes to xterm-256color color numbers

	if len(sys.argv) != 2:
		print('Usage: resolvecolor.py #RRGGBB')
		exit()

	print(closest_color(*[int(s, 16) for s in re.match('#?([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})', sys.argv[1]).groups()]))

