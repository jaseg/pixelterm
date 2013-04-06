
PREFIX?=/usr/local

install:
	install -m 0755 pixelterm.py $(PREFIX)/bin/pixelterm
	install -m 0755 unpixelterm.py $(PREFIX)/bin/unpixelterm
	install -m 0755 pngmeta.py $(PREFIX)/bin/pngmeta

uninstall:
	rm $(PREFIX)/bin/pixelterm
	rm $(PREFIX)/bin/unpixelterm
	rm $(PREFIX)/bin/pngmeta

reinstall: uninstall install

