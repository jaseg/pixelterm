#!/usr/bin/env python

import os, sys, argparse, os.path, json, time, signal, atexit
#NOTE: This script uses pygments for RGB->X256 conversion since pygments is
#readily available. If you do not like pygments (e.g. because it is large),
#you could patch in something like https://github.com/magarcia/python-x256
#(but don't forget to send me a pull request ;)
from pygments.formatters import terminal256
from PIL import Image, GifImagePlugin, ImageSequence
import pixelterm

clear_screen = '\033[H\033[2J'
cursor_invisible = '\033[?25l'
cursor_visible = '\033[?25h'

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Render pixel images on 256-color ANSI terminals')
	parser.add_argument('image', type=str)
	parser.add_argument('-s', '--size', type=str, help='Terminal size, [W]x[H]')
	args = parser.parse_args()

	tw, th = os.get_terminal_size()
	th = th*2
	if args.size:
		tw, th = map(int, args.size.split('x'))

	img = Image.open(args.image)
	palette = img.getpalette()
	last_frame = Image.new("RGBA", img.size)
	frames = []

	for frame in ImageSequence.Iterator(img):
		#This works around a known bug in Pillow
		#See also: http://stackoverflow.com/questions/4904940/python-converting-gif-frames-to-png
		frame.putpalette(palette)
		c = frame.convert("RGBA")

		if img.info['background'] != img.info['transparency']:
			last_frame.paste(c, c)
		else:
			last_frame = c

		im = last_frame.copy()
		im.thumbnail((tw, th), Image.NEAREST)
		frames.append(pixelterm.termify_pixels(im))

	print(cursor_invisible)
	atexit.register(lambda:print(cursor_visible))
	signal.signal(signal.SIGTERM, lambda signum, stack_frame: exit(1))

	while True:
		for frame in frames:
			print(clear_screen, pixelterm.reset_sequence)
			print(frame)
			time.sleep(img.info['duration']/1000.0)

