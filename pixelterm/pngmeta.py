#!/usr/bin/env python

import os, sys, argparse
from PIL import Image, PngImagePlugin

def main():
	parser = argparse.ArgumentParser(description='Print PNG metadata')
	parser.add_argument('image', type=str)
	args = parser.parse_args()
	img = Image.open(args.image)
	for k, v in img.info.items():
		print('{:15}: {}'.format(k, v))

if __name__ == '__main__':
	main()

