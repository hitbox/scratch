# Makefile for Tile by Joe Wingbermuehle

CC=gcc
PREFIX=/usr/local/bin
EXENAME=tile

all:
	$(CC) -O2 tile.c -o $(EXENAME) `gtk-config --cflags --libs`

install: all
	cp $(EXENAME) $(PREFIX)/$(EXENAME)

uninstall:
	rm $(PREFIX)/$(EXENAME)

clean:
	rm $(EXENAME)
