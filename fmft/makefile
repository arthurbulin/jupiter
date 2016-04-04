#FMFT.c Makefile, 2015 by Arthur A. Bulin
#last modified 11-20-15
all: nrutil fmft link

nrutil:
	gcc -c nrutil.c

fmft:
	gcc -c fmft.c

link:
	gcc -o main_fmft main_fmft.c fmft.o nrutil.o -lm

clean:
	rm main_fmft main_fmft.c fmft.o nrutil.o
