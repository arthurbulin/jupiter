import os
import lib_merc as lm
import numpy as np

absw = '/home/bulin/Mercury/'

def main(lookin):
	delf_dats = dict()
	for i in xrange(len(lookin)):
		delfs = dict()
		worlds = ['MERCURY','MARS']
		print 'For ' + lookin[i]
		folders = lm.lib_get_dir(lookin[i])
		folders.sort()
		for w in worlds:
			delF = list()
			for j in xrange(len(folders)):
				ifiles,ffiles = list(),list()
				dir_con = os.listdir(absw + lookin[i] +'/'+folders[j])
				for h in dir_con:
					if w+'1.fmft' in h: first = h
					if w+'2.fmft' in h: sec = h
#				print first,sec
				Fi,Ai,Pi = np.genfromtxt(absw + lookin[i] +'/'+ folders[j] +'/'+ first,unpack=True)
				Ff,Af,Pf = np.genfromtxt(absw + lookin[i] +'/'+ folders[j] +'/'+ sec,unpack=True)
				delF.append(Ff[0] - Fi[0])
			delfs[w] = delF
		delf_dats[lookin[i]] = delfs
	return delf_dats
