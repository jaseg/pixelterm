#!/usr/bin/env python

import os, sys, argparse, os.path, json, time, signal, atexit
import pixelterm
from PIL import Image, GifImagePlugin, ImageSequence

clear_screen = '\033[H\033[2J'
cursor_invisible = '\033[?25l'
cursor_visible = '\033[?25h'

def main():
	parser = argparse.ArgumentParser(description='Render pixel images on 256-color ANSI terminals')
	parser.add_argument('image', type=str)
	parser.add_argument('-s', '--size', type=str, help='Terminal size, [W]x[H]')
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

		if img.info['background'] != img.info['transparency']:
			last_frame.paste(c, c)
		else:
			last_frame = c

		im = last_frame.copy()
		if (tw, th) != (None, None):
			im.thumbnail((tw, th), Image.NEAREST)
		frames.append(pixelterm.termify_pixels(im))

	print(cursor_invisible)
	atexit.register(lambda:print(cursor_visible))
	signal.signal(signal.SIGTERM, lambda signum, stack_frame: exit(1))

	try:
		while True:
			for frame in frames:
				print(clear_screen, pixelterm.reset_sequence)
				print(frame)
				time.sleep(img.info['duration']/1000.0)
	except KeyboardInterrupt:
		pass

if __name__ == '__main__':
	main()

