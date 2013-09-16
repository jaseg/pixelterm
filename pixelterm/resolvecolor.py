#!/usr/bin/env python

def main():
	import os, sys, argparse, os.path, json, re
	import xtermcolors

	# Resolve HTML-style hex RGB color codes to xterm-256color color numbers

	if len(sys.argv) != 2:
		print('Usage: resolvecolor.py #RRGGBB')
		exit()

	print(xtermcolors.closest_color(*[int(s, 16) for s in re.match('#?([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})', sys.argv[1]).groups()]))

if __name__ == '__main__':
	main()

