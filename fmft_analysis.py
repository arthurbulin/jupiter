import os
import lib_merc as lm

absw = '/home/bulin/Mercury/'

def fmft_analysis(lookin):
	for i in xrange(len(lookin)):
		print 'For ' + lookin[i]
		folders = lm.get_dir(lookin[i])
		folders.sort()
		for j in xrange(len(folders)):
			ifiles,ffiles = list(),list()
			
			dir_con = os.listdir(absw + lookin[i] +'/'+folders[j])
			
			for h in dir_con:
				if '1.fmft' in h: ifiles.append(h)
				if '2.fmft' in h: ffiles.append(h)
			for k in xrange(len(ifiles)):
				F,A,P = np.genfromtxt(ifiles[k],unpack=True)
