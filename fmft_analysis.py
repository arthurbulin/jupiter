#This subroutine will run an anaylsis of the fmft values returning the delta(freq) between start and stop times of the 
#of the planets. There is also a method that calls plot_base to either save or view the plots.
#Arthur Bulin April 6, 2016
#Version 1.0

import os
import lib_merc as lme
import numpy as np
import plot_base as pb
import h5_bridge as h5b

absw = lme.lib_get_path('absw')
ind_names = lme.lib_ind_names()
do_hdf5 = lme.lib_get_path('hdf5')
data_out = lme.lib_get_path('data_out')

def main(lookin,worlds):
	delf_dats = dict()
	for i in xrange(len(lookin)):
		delfs = dict()
		print 'For ' + lookin[i]
		
		if do_hdf5 is 'true':
			folders = h5b.get_keys(lookin[i])
		else:
			folders = lme.lib_get_dir(lookin[i])
		
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

def plot_hist(dat,worlds,look,save=False):
	#names = list()
	for w in worlds:
		for i in xrange(len(look)):
			to_plot = np.absolute(dat[look[i]][w])
	#		names.append(look[i])
			if save == True:
				pb.plot_base(None,[to_plot],savename=absw+data_out+'/image_output/'+'hist_'+w+'_sim_'+look[i],type=2,title=r'Histogram of |$\Delta f$| for '+w+' for Sim '+look[i],xaxis_title=r'|$\Delta f$|',yaxis_title='Number of occurances')
			else:
				pb.plot_base(None,[to_plot],type=2,title=r'Histogram of |$\Delta f$| for '+w+' for Sim '+look[i],xaxis_title=r'|$\Delta f$|',yaxis_title='Number of occurances')
			
