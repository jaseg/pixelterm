
PREFIX?=/usr/local

install:
	install -m 0755 pixelterm.py $(PREFIX)/bin/pixelterm

uninstall:
	rm $(PREFIX)/bin/pixelterm

reinstall: uninstall install

