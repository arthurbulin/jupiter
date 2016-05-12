import AMDmonitor as amd
import os
import numpy as np
import lib_merc as lme
import h5_bridge as h5b

#Set my absolute directory and end names. These are needed for certain things.
ind_names = lme.lib_ind_names()
#absw = lme.lib_get_absw()
absw = lme.lib_get_path('absw')
data_out = lme.lib_get_path('data_out')
do_hdf5 = lme.lib_get_path('hdf5')

def main(lookin,peaks=None):
	data = dict()
	peaks_to_check = peaks

	for i in xrange(len(lookin)):
#		print 'For ' + lookin[i]
		if do_hdf5 =='true':
			folders = h5b.get_keys(lookin[i]) #returns the 'folders' for the sim set within the hdf5
		else:
			folders = lme.lib_get_dir(lookin[i])
			folders.sort()
			noaei = lme.lib_need_aei(lookin[i],folders)
			if noaei:
				lme.lib_unpack(lookin[i],noaei)
		
		sets = dict()
		for j in xrange(len(folders)):
#		 	print 'Getting AMD for ' + lookin[i] + ':' + folders[j],
			t,am = amd.AMDmonitor(lookin[i],folders[j])
#			print 'Getting Max AMD',
			max = amd_max(t,am)
			if peaks_to_check is not None:
#				print 'Getting peaks'
				peaks = amd_first_times(t,am,peaks_to_check)
				sets[folders[j]] = {'max':max, 'peaks':peaks}
			else:
				sets[folders[j]] = {'max':max}
		data[lookin[i]] = sets
	return data

#########################################
#	AMD Stats that we want to get	#
#########################################

def amd_max(t,am):
	peak = 0
	for i in xrange(len(am)-1):
		if am[i+1] > am[i]:
			peak = am[i+1]
			time = t[i+1]
	return {'time':time, 'peak':peak}

#I was tired, so the variable names got worse and things got sloppy
def amd_first_times(t,am,peaks):
	d = dict()
	for each in peaks: #for each value in peaks
		for i in xrange(len(am)): #Now check all of the amd values for comparison
			if am[i] >= each:
				d[each] = {'time':t[i], 'amd':am[i]}
				break
	return d

#Not update for use with dictionaties
#def dat_out(data):
#	if data is dict(): print('Not updated'); return None
#	with open('amd.dat','w') as f:
#		for i in xrange(len(data)):
#			for j in xrange(len(data[i][1])):
#				init_str = str(data[i][0]) + ':'+ str(data[i][1][j][0]) + ',' + str(data[i][1][j][1][0]) +','+ str(data[i][1][j][1][1])
#				for k in xrange(len(data[i][1][j][2])):
#					init_str = init_str + ',' + str(data[i][1][j][2][k][1]) + ',' + str(data[i][1][j][2][k][2])
#				f.write(init_str+'\n')

def get_amd_data(lookin):
	time,amd = list(),list()
	for i in xrange(len(lookin)):
		a,b = ret_median(lookin[i])
		time.append(a)
		amd.append(b)
	return time,amd

#This will return median values across a single simulation
def ret_median(sim):
	#Get my directory structures
	if do_hdf5 =='true':
		folders = h5b.get_keys(sim)
		folders.sort()
	else:
		folders = lme.lib_get_dir(sim)
		folders.sort()
		#Need AEI? Unpack
		noaei = lme.lib_need_aei(sim,folders)
		if noaei:
			lme.lib_unpack(sim,noaei)
	
	#Get amd values and time
	med_sets,t_sets = list(),list()
	for i in xrange(len(folders)):
		t,am = amd.AMDmonitor(sim,folders[i])
		med_sets.append(am)
		t_sets.append(t)
	
	set_lens = list()
	for k in xrange(len(t_sets)):
		set_lens.append(len(t_sets[k]))
	time = t_sets[set_lens.index(max(set_lens))]
	new_amd = make_single_list(med_sets)
	return time,new_amd

def make_single_list(sets):
	temp = list()
	for i in xrange(len(sets)):
		temp.append(len(sets[i]))
	temp.sort(reverse=True)

	new_amd = list()
	for i in xrange(temp[0]):
		meds = list()
		for j in xrange(len(sets)):
			try: meds.append(sets[j][i])
			except: continue
		new_amd.append(np.median(meds))
	return new_amd
