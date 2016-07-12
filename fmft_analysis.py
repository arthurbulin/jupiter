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
names_default = ['mercury','venus','earth','mars','jupiter','saturn']


def main(lookin,worlds):
	delf_dats = dict()
	for i in xrange(len(lookin)):
		delfs = dict()
		print 'For ' + lookin[i]
		
		if do_hdf5 is 'true':
			folders = h5b.get_keys(sim=lookin[i])
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
			
def collect_fmft(sim,mode=0):
#	os.chdir(data_out+sim)
	dir = data_out+sim+'/'
	dir_list = os.listdir(dir)
	dir_list.sort()
	
	dirs = list() #For the good directories
	for i in dir_list:
		#Check for my runs in int named folders
		try: 
			int(i)
			num = True
		except:
			num = False
			
		if (os.path.isdir(dir+i)) and (num == True):
			dirs.append(i)
	dirs.sort()
	
	for i in dirs:
		data,fmft_l = list(),list()
		printlines,planets = list(),list()
		set_dir = os.listdir(dir+i)
		
		for j in set_dir:
			if str(mode)+'.fmft' in j:
				fmft_l.append(j)
		#Redo as a dictionary so that i can try to get it in order
		names = dict()
		for j in fmft_l:
			value,mag,phase = np.genfromtxt(dir+i+'/'+j,unpack=True)
			names[j.split(str(mode))[0]] = value

#		names.sort()
		
		#TOO MANY DAMN LOOPS, but i'm exhausted and i just want it in order right now. ill fix later
#		not_in,names_in = list(),list()
#		names_default = ['mercury','venus','earth','mars','jupiter','saturn']
#		for j in names_default:
#			if str.upper(j) in names:
#				names_in.append(j)
#		print 'names'
#		print names_in
#		for j in names:
#			if str.lower(j) not in names_default:
#				not_in.append(j)
	
	##	for j in not_in:		
	#		names_in.append(j)
		
#		if len(not_in) > 0:
#			for j in not_in:
#				names_in.append(j)
#		print names_in
#		for j in names_in:
##			try: value,mag,phase = np.genfromtxt(dir+i+'/'+j+str(mode)+'.fmft',unpack=True)
#			except IOError:
#				try: value,mag,phase = np.genfromtxt(dir+i+'/'+str.upper(j)+str(mode)+'.fmft',unpack=True)
#				except:
#					print "Something odd."
#					return 66
#			data.append(value)
#			
#COmmenting the following section out for Dict testing
#
#		dat = np.asarray(data)
#		dat = np.fliplr(np.flipud(np.rot90(dat)))
#		for j in dat:
#			tmp = ''
#			for k in j:
#				tmp = tmp+','+str(k)
#			printlines.append(tmp.split(',',1)[1])
		
#		tmp = ''
#		names.reverse()
#		for j in names:
#			tmp = tmp +','+str(j)
#		namesprint = tmp.split(',',1)[1]
#END COMMENT FOR DICT TESTING
#		names_default = ['mercury','venus','earth','mars','jupiter','saturn']
#		names_priority = dict()
		
		names_s = list()
		for j in names_default:
			if j in names:
				names_s.append(j)
			elif str.swapcase(j) in names:
				names_s.append(str.upper(j))
		for j in names:
			if (j not in names_s) and (str.swapcase(j) not in names_s):
				names_s.append(j)
				
		namesprint = ','.join(names_s)
		for k in xrange(len(names_s)):
			tmp = list()
			for j in names_s:
				tmp.append(str(names[j][k]))
			printlines.append(','.join(tmp))
				
		#This will create our csv file		
		f = open(dir+i+'/0_worlds_fmft.csv','w')
		f.write(namesprint+'\n')
		for j in printlines:
			f.write(j+'\n')
		f.close()

